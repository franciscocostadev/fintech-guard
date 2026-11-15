"""Integridade da entrega de dados e inferência; não substitui avaliação externa."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from ml.security_classifier import SecurityClassifier
from scripts.tp4_classification import DATA_FILE, DATA_SHA, PARAM_GRID, similarity_groups

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "reports/TP4/classification"


@pytest.fixture(scope="module")
def classifier():
    return SecurityClassifier(ROOT / "models/TP4/security")


def test_tp4_manifest_matches_original_rows_and_excludes_group_overlap():
    data = pd.read_csv(ROOT / DATA_FILE)
    manifest = pd.read_csv(OUTPUT / "split_manifest.csv")
    assert hashlib.sha256((ROOT / DATA_FILE).read_bytes()).hexdigest() == DATA_SHA
    assert manifest.row_id.tolist() == list(range(len(data)))
    expected = data.text.map(lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest())
    assert manifest.text_sha256.tolist() == expected.tolist()
    assert manifest.groupby("group_id").split.nunique().max() == 1
    train = manifest[manifest.split == "train"]
    test = manifest[manifest.split == "test"]
    assert train.groupby("group_id").validation_fold.nunique().max() == 1
    assert test.validation_fold.eq(-1).all()
    assert set(train.validation_fold) == set(range(5))
    assert set(test.label) == {"benign", "threat"}
    for fold in range(5):
        assert set(train[train.validation_fold == fold].label) == {"benign", "threat"}


def test_tp4_grouping_keeps_template_variants_together():
    texts = ["Reference 100: contact hello@example.com", "Reference 200: contact bye@example.com", "An unrelated short sentence."]
    groups, pairs = similarity_groups(texts)
    assert groups[0] == groups[1] != groups[2]
    assert len(pairs) == 1


def test_tp4_grid_has_two_parameters_with_three_values_and_train_selection():
    protocol = json.loads((OUTPUT / "protocol.json").read_text(encoding="utf-8"))
    selection = json.loads((OUTPUT / "selection.json").read_text(encoding="utf-8"))
    cv_results = pd.read_csv(OUTPUT / "cv_results.csv")
    assert sum(len(values) >= 3 for values in PARAM_GRID.values()) >= 2
    assert len(cv_results) == protocol["candidates"] == 18
    assert not selection["selection_uses_test"]
    assert selection["best_cv_macro_f1"] == pytest.approx(cv_results.mean_test_score.max())


def test_tp4_vocabulary_has_no_terms_exclusive_to_test(classifier):
    data = pd.read_csv(ROOT / DATA_FILE)
    manifest = pd.read_csv(OUTPUT / "split_manifest.csv")
    vectorizer = classifier.pipeline.named_steps["tfidf"]
    analyze = vectorizer.build_analyzer()
    def terms(split):
        return {term for text in data.loc[manifest.split.eq(split), "text"] for term in analyze(text)}
    train_terms, test_terms = terms("train"), terms("test")
    assert set(vectorizer.vocabulary_).issubset(train_terms)
    assert set(vectorizer.vocabulary_).isdisjoint(test_terms - train_terms)


@pytest.mark.parametrize("text", [None, 42, "", "  \n", "x" * 4001])
def test_tp4_inference_rejects_invalid_text_without_truncation(classifier, text):
    with pytest.raises(ValueError):
        classifier.classify(text)


def test_tp4_serialized_model_matches_recorded_scores_and_contract(classifier):
    data = pd.read_csv(ROOT / DATA_FILE)
    predictions = pd.read_csv(OUTPUT / "predictions.csv")
    for row in predictions[predictions.model == "tuned"].itertuples():
        result = classifier.classify(data.loc[row.row_id, "text"])
        assert result["label"] == row.predicted
        assert result["probabilities"]["threat"] == pytest.approx(row.p_threat)
        assert result["probability"] == result["probabilities"][result["label"]]
        assert sum(result["probabilities"].values()) == pytest.approx(1)
        assert result["task"] == "security_binary"
    assert classifier.metadata["fitted_on_test"] is False


def test_tp4_corrupt_artifact_rejected_before_deserialization(tmp_path, monkeypatch):
    metadata = json.loads((ROOT / "models/TP4/security/metadata.json").read_text(encoding="utf-8"))
    (tmp_path / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (tmp_path / "classifier.joblib").write_bytes(b"corrupt artifact")
    def must_not_load(*args, **kwargs):
        pytest.fail("Artefato corrompido não pode ser desserializado.")
    monkeypatch.setattr("ml.security_classifier.joblib.load", must_not_load)
    with pytest.raises(ValueError, match="Integridade"):
        SecurityClassifier(tmp_path)


def test_tp4_incompatible_environment_rejected_before_deserialization(monkeypatch):
    monkeypatch.setattr("ml.security_classifier.version", lambda name: "0.invalid")
    def must_not_load(*args, **kwargs):
        pytest.fail("Ambiente incompatível não pode carregar o artefato.")
    monkeypatch.setattr("ml.security_classifier.joblib.load", must_not_load)
    with pytest.raises(RuntimeError, match="Versão incompatível"):
        SecurityClassifier(ROOT / "models/TP4/security")


def test_tp4_metrics_recomputed_from_predictions():
    from sklearn.metrics import f1_score, roc_auc_score
    metrics = pd.read_csv(OUTPUT / "metrics.csv").set_index("model")
    predictions = pd.read_csv(OUTPUT / "predictions.csv")
    for name, rows in predictions.groupby("model"):
        assert metrics.loc[name, "test_macro_f1"] == pytest.approx(f1_score(rows.label, rows.predicted, average="macro"))
        assert metrics.loc[name, "test_roc_auc"] == pytest.approx(roc_auc_score(rows.label.eq("threat"), rows.p_threat))


def test_tp4_notebook_has_executed_cells_without_errors_and_figures():
    notebook = json.loads((ROOT / "notebooks/TP4/security/01_classificacao.ipynb").read_text(encoding="utf-8"))
    code = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
    assert all(isinstance(cell["execution_count"], int) for cell in code)
    assert not any(out["output_type"] == "error" for cell in code for out in cell["outputs"])
    assert sum("image/png" in out.get("data", {}) for cell in code for out in cell["outputs"]) >= 5
