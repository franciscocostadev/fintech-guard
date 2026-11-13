"""Auditoria estrutural dos dados disponíveis para o TP4, sem treinamento."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata


FILES = {
    "security": "data/processed/security/phishing_nlp_dataset.csv",
    "banking_train": "data/processed/banking77/train.csv",
    "banking_test": "data/processed/banking77/test.csv",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip().casefold()


def inspect_csv(path: Path) -> tuple[dict, set[str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        if not {"text", "category"}.issubset(columns):
            raise ValueError(f"Colunas text/category ausentes em {path.name}.")
        rows = list(reader)
    classes = Counter(row["category"] for row in rows)
    texts = [row["text"] or "" for row in rows]
    normalized = [normalize(text) for text in texts]
    groups = defaultdict(set)
    for row, key in zip(rows, normalized):
        groups[key].add(row["category"])
    frequencies = Counter(normalized)
    conflicts = {key for key, labels in groups.items() if len(labels) > 1}
    result = {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": len(rows),
        "columns": columns,
        "classes": len(classes),
        "class_counts": dict(sorted(classes.items())),
        "empty_texts": sum(not text.strip() for text in texts),
        "empty_labels": sum(not (row["category"] or "").strip() for row in rows),
        "exact_duplicate_text_excess": len(texts) - len(set(texts)),
        "normalized_duplicate_text_excess": len(normalized) - len(set(normalized)),
        "normalized_duplicate_groups": sum(count > 1 for count in frequencies.values()),
        "normalized_conflicting_groups": len(conflicts),
        "rows_in_conflicting_groups": sum(key in conflicts for key in normalized),
        "min_characters": min(map(len, texts), default=0),
        "max_characters": max(map(len, texts), default=0),
        "texts_above_current_predict_limit_1000": sum(len(text) > 1000 for text in texts),
    }
    return result, set(normalized)


def audit(project_root: Path) -> dict:
    datasets = {}
    text_sets = {}
    for name, relative in FILES.items():
        summary, text_set = inspect_csv(project_root / relative)
        datasets[name] = {"path": relative, **summary}
        text_sets[name] = text_set
    return {
        "purpose": "Inspeção estrutural prévia; não treina, escolhe modelo nem altera os dados.",
        "normalization_for_audit_only": "Unicode NFKC, espaços consecutivos reduzidos, strip e casefold.",
        "datasets": datasets,
        "banking_normalized_train_test_overlap": len(text_sets["banking_train"] & text_sets["banking_test"]),
        "caveats": [
            "Duplicatas similares por template não são detectadas por normalização exata.",
            "Contagens incluem o teste bancário já explorado no TP1; não há seleção de modelo pelo teste.",
            "Nenhuma exclusão ou relabeling é feita por este script.",
            "Segurança do conteúdo e intenção bancária são tarefas diferentes.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    output = args.output or root / "reports/TP4/auditoria_dados.json"
    result = audit(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "rows": {name: item["rows"] for name, item in result["datasets"].items()},
        "classes": {name: item["classes"] for name, item in result["datasets"].items()},
        "duplicate_groups": {name: item["normalized_duplicate_groups"] for name, item in result["datasets"].items()},
        "conflicting_groups": {name: item["normalized_conflicting_groups"] for name, item in result["datasets"].items()},
        "banking_overlap": result["banking_normalized_train_test_overlap"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
