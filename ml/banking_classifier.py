"""Inferência BANKING77: artefato confiável, taxonomia original e scores separados."""
from importlib.metadata import version
from pathlib import Path
import hashlib
import json

import joblib
import numpy as np

DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[1] / 'models/TP4/banking77'


class BankingClassifier:
    def __init__(self, model_dir: Path = DEFAULT_MODEL_DIR):
        model_dir = Path(model_dir)
        self.metadata = json.loads((model_dir/'metadata.json').read_text(encoding='utf-8'))
        self.labels = json.loads((Path(__file__).parent/'banking77_labels.json').read_text(encoding='utf-8'))
        if (self.metadata.get('task') != 'banking77_intent' or self.metadata.get('classes') != self.labels
                or len(self.labels) != 77 or self.metadata.get('max_text_characters') != 4000):
            raise ValueError('Contrato/taxonomia BANKING77 incompatível.')
        artifact = model_dir/'classifier.joblib'
        if hashlib.sha256(artifact.read_bytes()).hexdigest() != self.metadata.get('artifact_sha256'):
            raise ValueError('Integridade do modelo BANKING77 divergente.')
        for package in ('scikit-learn','numpy','scipy','joblib'):
            if version(package) != self.metadata['dependencies'][package]:
                raise RuntimeError(f'Versão incompatível de {package}; use requirements-tp4-dados.txt.')
        # Desserializar somente o artefato revisado; um hash não autentica origem desconhecida.
        self.pipeline = joblib.load(artifact)
        if list(self.pipeline.classes_) != self.labels:
            raise ValueError('Classes do pipeline não correspondem à taxonomia.')

    def classify(self, text: str) -> dict:
        if not isinstance(text,str) or not text.strip() or len(text)>4000:
            raise ValueError('text deve ser uma string não vazia com até 4000 caracteres.')
        scores = self.pipeline.predict_proba([text])[0]
        if scores.shape != (77,) or not np.isfinite(scores).all() or (scores<0).any() or not np.isclose(scores.sum(),1.0):
            raise RuntimeError('Probabilidades inválidas do modelo bancário.')
        selected = int(np.argmax(scores))
        return {'intent':self.labels[selected],'probability':float(scores[selected]),
                'model_version':self.metadata['model_version']}
