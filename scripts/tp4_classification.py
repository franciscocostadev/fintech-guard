"""Experimento TP4: seleção no treino e avaliação interna de conteúdo de segurança."""
from __future__ import annotations

from collections import Counter
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import re
import unicodedata

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                             classification_report, confusion_matrix, f1_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, cross_val_score
from sklearn.pipeline import Pipeline

SEED = 42
LABELS = ["benign", "threat"]
MAPPING = {"NOT-Malicious General Class": "benign", "Baiting": "threat", "Malware": "threat",
           "Phishing": "threat", "Pretexting": "threat", "Scareware": "threat"}
PARAM_GRID = {"classifier__C": [0.1, 1.0, 10.0], "tfidf__min_df": [1, 2, 3],
              "classifier__class_weight": [None, "balanced"]}
DATA_FILE = "data/processed/security/phishing_nlp_dataset.csv"
DATA_SHA = "b416c4362ef0447340770b7c73a57d5705ecc8bbeaf2efc1c2a0de632707d5c1"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def template(text: str) -> str:
    """Somente para auditoria/grupos; não transforma a entrada do classificador."""
    text = unicodedata.normalize("NFKC", text).casefold()
    text = re.sub(r"https?://\S+|www\.\S+", " URL ", text)
    text = re.sub(r"\b[\w.+-]+@[\w.-]+\.[a-z]{2,}\b", " EMAIL ", text)
    text = re.sub(r"\d+", " NUM ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity_groups(texts: list[str], threshold: float = 0.85) -> tuple[list[str], pd.DataFrame]:
    """Componentes conexos de templates iguais ou Jaccard >= .85 de char-5-gramas.

    A comparação aproximada requer >=80 caracteres em ambos os textos para não
    agrupar frases curtas por trechos comuns. Não utiliza rótulos nem resultados.
    """
    normalized = [template(t) for t in texts]
    grams = [set(t[i:i + 5] for i in range(max(0, len(t) - 4))) for t in normalized]
    parents = list(range(len(texts)))

    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i

    pairs = []
    for i, left in enumerate(normalized):
        for j in range(i):
            if left == normalized[j]:
                similarity, reason = 1.0, "template_equal"
            else:
                if min(len(left), len(normalized[j])) < 80:
                    continue
                a, b = grams[i], grams[j]
                if min(len(a), len(b)) / max(len(a), len(b)) < threshold:
                    continue
                similarity = len(a & b) / len(a | b)
                if similarity < threshold:
                    continue
                reason = "char5_jaccard"
            parents[find(i)] = find(j)
            pairs.append({"row_a": j, "row_b": i, "similarity": similarity, "reason": reason})
    members = {}
    for i in range(len(texts)):
        members.setdefault(find(i), []).append(i)
    group_min = {i: min(values) for values in members.values() for i in values}
    groups = [f"g{group_min[i]:04d}" for i in range(len(texts))]
    return groups, pd.DataFrame(pairs, columns=["row_a", "row_b", "similarity", "reason"])


def prepare(root: Path):
    output = root / "reports/TP4/classification"
    output.mkdir(parents=True, exist_ok=True)
    data_path = root / DATA_FILE
    if digest(data_path) != DATA_SHA:
        raise ValueError("Dataset alterado: revisar protocolo antes de executar outro experimento.")
    df = pd.read_csv(data_path, keep_default_na=False)
    if len(df) != 603 or set(df.category) != set(MAPPING) or df.text.str.strip().eq("").any():
        raise ValueError("Dados não correspondem à base validada do TP3.")
    df["label"] = df.category.map(MAPPING)
    df["row_id"] = np.arange(len(df))
    df["text_sha256"] = df.text.map(lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest())
    df["group_id"], pairs = similarity_groups(df.text.tolist())
    splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED)
    # Estratificação por categoria original preserva representação dos seis subtipos.
    train_idx, test_idx = next(splitter.split(df.text, df.category, df.group_id))
    manifest = df[["row_id", "text_sha256", "category", "label", "group_id"]].copy()
    manifest["split"] = "train"
    manifest.loc[test_idx, "split"] = "test"
    manifest["validation_fold"] = -1
    train = df.iloc[train_idx].copy()
    cv_splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=SEED + 1)
    cv = list(cv_splitter.split(train.text, train.label, train.group_id))
    for fold, (fit_idx, val_idx) in enumerate(cv):
        assert set(train.iloc[fit_idx].group_id).isdisjoint(train.iloc[val_idx].group_id)
        assert set(train.iloc[fit_idx].label) == set(train.iloc[val_idx].label) == set(LABELS)
        manifest.loc[train.iloc[val_idx].index, "validation_fold"] = fold
    assert set(df.iloc[train_idx].group_id).isdisjoint(df.iloc[test_idx].group_id)
    assert set(df.iloc[test_idx].label) == set(LABELS)
    protocol = {
        "experiment": "tp4-security-binary-v1", "recorded_before_model_evaluation": True,
        "seed": SEED, "dataset_sha256": DATA_SHA, "mapping": MAPPING,
        "positive_class": "threat", "threshold": 0.5,
        "split": "first StratifiedGroupKFold(5, shuffle=True, seed=42); stratify original category",
        "cv": "5-fold StratifiedGroupKFold on training only; binary labels; seed=43",
        "groups": "NFKC/casefold/space + URL/email/digit templates; equal or char5 Jaccard>=0.85, min80 chars; connected components",
        "tfidf": {"ngram_range": [1, 2], "sublinear_tf": True, "max_features": 20000,
                  "lowercase": True, "stop_words": None},
        "initial_classifier": {"C": 1.0, "class_weight": None, "solver": "liblinear", "max_iter": 2000},
        "grid": PARAM_GRID, "selection_metric": "f1_macro", "candidates": 18,
        "test_policy": "No choice of features, hyperparameters or threshold from test results; identical reruns are reproduction, not new validation.",
        "limitations": "Internal test from a small dataset already explored in EDA; no claim of external independence or Portuguese banking validity.",
    }
    protocol_path = output / "protocol.json"
    if protocol_path.exists() and json.loads(protocol_path.read_text(encoding="utf-8")) != protocol:
        raise ValueError("Protocolo diferente do registrado; criar experimento separado, não sobrescrever o teste.")
    manifest_path = output / "split_manifest.csv"
    csv_text = manifest.to_csv(index=False, lineterminator="\n")
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") != csv_text:
        raise ValueError("Partição divergente da congelada.")
    write_json(protocol_path, protocol)
    manifest_path.write_text(csv_text, encoding="utf-8")
    pairs.to_csv(output / "similar_pairs.csv", index=False)
    counts = Counter(df.group_id)
    write_json(output / "group_audit.json", {
        "groups": len(counts), "groups_with_multiple_rows": sum(n > 1 for n in counts.values()),
        "largest_group": max(counts.values()), "similar_pairs": len(pairs),
        "mixed_binary_label_groups": int((df.groupby("group_id").label.nunique() > 1).sum()),
        "train_rows": len(train_idx), "test_rows": len(test_idx),
        "cross_split_groups": 0, "cross_cv_fold_groups": 0,
    })
    return df, manifest, train, df.iloc[test_idx].copy(), cv


def build_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True,
                                  max_features=20000, lowercase=True, stop_words=None, min_df=1)),
        ("classifier", LogisticRegression(C=1.0, class_weight=None, solver="liblinear",
                                          max_iter=2000, random_state=SEED)),
    ])


def train_baselines(train, cv, pipeline):
    models = {"majority": DummyClassifier(strategy="prior"), "initial": clone(pipeline)}
    cv_scores = {}
    for name, model in models.items():
        cv_scores[name] = cross_val_score(model, train.text, train.label, cv=cv, scoring="f1_macro", n_jobs=1)
        model.fit(train.text, train.label)
    return models, cv_scores


def export_evaluation(root, train, test, search, baselines, cv_scores):
    """Avalia modelos já fixados; não ajusta modelo ou limiar usando o teste."""
    output = root / "reports/TP4/classification"
    model_dir = root / "models/TP4/security"
    model_dir.mkdir(parents=True, exist_ok=True)
    write_json(output / "selection.json", {
        "best_params": search.best_params_, "best_cv_macro_f1": float(search.best_score_),
        "selection_uses_test": False, "threshold": 0.5,
    })
    cv_results = pd.DataFrame(search.cv_results_)
    cols = [c for c in cv_results if c.startswith("param_") or c.endswith("test_score") or c == "params"]
    cv_results[cols].to_csv(output / "cv_results.csv", index=False)
    cv_scores["tuned"] = np.array([search.cv_results_[f"split{i}_test_score"][search.best_index_] for i in range(5)])
    models = {**baselines, "tuned": search.best_estimator_}
    rows, details, predictions = [], {}, []
    for name, model in models.items():
        proba = model.predict_proba(test.text)
        p_threat = proba[:, list(model.classes_).index("threat")]
        # Fixar o mesmo limiar para todos; nenhuma otimização com o teste.
        predicted = np.where(p_threat > 0.5, "threat", "benign")
        truth = (test.label == "threat").astype(int)
        report = classification_report(test.label, predicted, labels=LABELS, output_dict=True, zero_division=0)
        rows.append({"model": name, "cv_macro_f1_mean": float(cv_scores[name].mean()),
                     "cv_macro_f1_std": float(cv_scores[name].std()),
                     "test_macro_f1": f1_score(test.label, predicted, average="macro"),
                     "test_accuracy": accuracy_score(test.label, predicted),
                     "test_balanced_accuracy": balanced_accuracy_score(test.label, predicted),
                     "test_roc_auc": roc_auc_score(truth, p_threat),
                     "test_average_precision": average_precision_score(truth, p_threat)})
        details[name] = {"classification_report": report,
                         "confusion_matrix": confusion_matrix(test.label, predicted, labels=LABELS).tolist(),
                         "labels_order": LABELS, "cv_fold_macro_f1": cv_scores[name].tolist()}
        for (_, row), pred, score in zip(test.iterrows(), predicted, p_threat):
            predictions.append({"model": name, "row_id": int(row.row_id), "text_sha256": row.text_sha256,
                                "original_category": row.category, "label": row.label,
                                "predicted": pred, "p_threat": float(score), "error": bool(pred != row.label)})
    metrics = pd.DataFrame(rows)
    metrics.to_csv(output / "metrics.csv", index=False)
    write_json(output / "metrics_per_class.json", details)
    prediction_frame = pd.DataFrame(predictions)
    prediction_frame.to_csv(output / "predictions.csv", index=False)
    tuned_predictions = prediction_frame[prediction_frame.model == "tuned"]
    subtype = tuned_predictions.groupby("original_category").agg(support=("label", "size"), errors=("error", "sum"))
    subtype["error_rate"] = subtype.errors / subtype.support
    subtype.to_csv(output / "subtype_errors.csv")
    artifact = model_dir / "classifier.joblib"
    joblib.dump(search.best_estimator_, artifact, compress=3)
    deps = {pkg: version(pkg) for pkg in ["scikit-learn", "numpy", "scipy", "joblib", "pandas"]}
    write_json(model_dir / "metadata.json", {
        "model_version": "tp4-security-binary-v1", "task": "security_binary",
        "classes": LABELS, "positive_class": "threat", "decision_threshold": 0.5,
        "max_text_characters": 4000, "probability_calibrated": False,
        "dataset_sha256": DATA_SHA, "artifact_sha256": digest(artifact),
        "split_manifest_sha256": digest(output / "split_manifest.csv"),
        "protocol_sha256": digest(output / "protocol.json"),
        "training_script_sha256": digest(Path(__file__)),
        "training_rows": len(train), "test_rows": len(test), "fitted_on_test": False,
        "mapping": MAPPING, "best_params": search.best_params_, "dependencies": deps,
        "language": "English dataset; Portuguese banking performance not validated",
    })
    write_json(output / "environment.json", {**deps, "matplotlib": version("matplotlib"),
                                             "seaborn": version("seaborn")})
    return metrics, details, prediction_frame, subtype


def main():
    root = Path(__file__).resolve().parents[1]
    _, _, train, test, cv = prepare(root)
    pipeline = build_pipeline()
    baselines, cv_scores = train_baselines(train, cv, pipeline)
    search = GridSearchCV(pipeline, PARAM_GRID, cv=cv, scoring="f1_macro", n_jobs=1, refit=True, error_score="raise")
    search.fit(train.text, train.label)
    metrics, _, _, _ = export_evaluation(root, train, test, search, baselines, cv_scores)
    print(metrics.to_string(index=False))


if __name__ == "__main__":
    main()
