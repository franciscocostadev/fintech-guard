"""Carregamento de artefato local confiável e contrato para POST /classify."""
from __future__ import annotations

import hashlib
from importlib.metadata import version
import json
from pathlib import Path

import joblib
import numpy as np

DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[1] / "models/TP4/security"


class SecurityClassifier:
    def __init__(self, model_dir: Path = DEFAULT_MODEL_DIR):
        model_dir = Path(model_dir)
        self.metadata = json.loads((model_dir / "metadata.json").read_text(encoding="utf-8"))
        artifact = model_dir / "classifier.joblib"
        if self.metadata.get("task") != "security_binary" or self.metadata.get("classes") != ["benign", "threat"]:
            raise ValueError("Metadados de tarefa/classes incompatíveis.")
        if hashlib.sha256(artifact.read_bytes()).hexdigest() != self.metadata.get("artifact_sha256"):
            raise ValueError("Integridade do artefato divergente dos metadados.")
        for dependency in ["scikit-learn", "numpy", "scipy", "joblib"]:
            if version(dependency) != self.metadata["dependencies"][dependency]:
                raise RuntimeError(f"Versão incompatível de {dependency}; use requirements-tp4-dados.txt.")
        # joblib executa desserialização: aceitar somente o artefato revisado do projeto.
        # O hash detecta corrupção, mas não autentica um arquivo de origem desconhecida.
        self.pipeline = joblib.load(artifact)
        if list(self.pipeline.classes_) != self.metadata["classes"]:
            raise ValueError("Classes do pipeline incompatíveis com os metadados.")
        if self.metadata.get("decision_threshold") != 0.5 or self.metadata.get("max_text_characters") != 4000:
            raise ValueError("Contrato de inferência divergente.")

    def classify(self, text: str) -> dict:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text deve ser uma string não vazia.")
        if len(text) > self.metadata["max_text_characters"]:
            raise ValueError("text excede 4000 caracteres; não há truncamento silencioso.")
        scores = self.pipeline.predict_proba([text])[0]
        if not np.isfinite(scores).all() or not np.isclose(scores.sum(), 1.0) or (scores < 0).any():
            raise RuntimeError("Probabilidades inválidas retornadas pelo pipeline.")
        probabilities = {label: float(score) for label, score in zip(self.pipeline.classes_, scores)}
        label = "threat" if probabilities["threat"] > 0.5 else "benign"
        return {"task": "security_binary", "label": label, "probability": probabilities[label],
                "probabilities": probabilities, "model_version": self.metadata["model_version"]}
