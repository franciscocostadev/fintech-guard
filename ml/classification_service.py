"""Composição das duas tarefas, pronta para ser chamada pela rota autenticada de B."""
from pathlib import Path

from .banking_classifier import BankingClassifier, DEFAULT_MODEL_DIR as BANKING_DIR
from .security_classifier import SecurityClassifier, DEFAULT_MODEL_DIR as SECURITY_DIR


class ClassificationService:
    def __init__(self, banking_dir: Path = BANKING_DIR, security_dir: Path = SECURITY_DIR):
        # Falha antes de expor um serviço parcialmente pronto se qualquer artefato for inválido.
        self.banking = BankingClassifier(banking_dir)
        self.security = SecurityClassifier(security_dir)

    def classify(self, text: str) -> dict:
        banking = self.banking.classify(text)
        security = self.security.classify(text)
        return {'task':'banking_intent_with_security', **banking, 'security':security}
