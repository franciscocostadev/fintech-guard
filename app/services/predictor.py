"""Classificador simples de intenção.

A próxima etapa pode trocar o miolo do predict() por um modelo treinado no
PolyAI/banking77. A interface fica igual, então as rotas não mudam.
"""

import hashlib

from app.schemas.predict import PredictResponse, RiskLevel

MODEL_VERSION = "regras-v1"


def _has_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _risk_level(text: str) -> RiskLevel:
    high_terms = ("senha", "token", "codigo", "código", "pix", "transferencia")
    pressure_terms = ("urgente", "agora", "imediato", "bloquear sua conta")

    if _has_any(text, high_terms) and _has_any(text, pressure_terms):
        return RiskLevel.HIGH
    if _has_any(text, ("pix", "transferencia", "transferência", "senha", "token")):
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def hash_message(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()


class IntentPredictor:
    version = MODEL_VERSION

    def predict(self, message: str, channel: str = "chat") -> PredictResponse:
        text = message.lower()
        risk_level = _risk_level(text)

        if _has_any(text, ("cartao", "cartão")) and _has_any(
            text, ("bloqueado", "bloqueio", "desbloquear", "desbloqueio")
        ):
            intent = "cartao_bloqueado"
            confidence = 0.82
            detail = "Mensagem sobre bloqueio ou desbloqueio de cartão."
        elif _has_any(text, ("pix", "transferencia", "transferência")):
            intent = "transferencia_pix"
            confidence = 0.74
            detail = "Mensagem relacionada a transferência ou PIX."
        elif _has_any(text, ("senha", "login", "acesso", "token")):
            intent = "acesso_conta"
            confidence = 0.71
            detail = "Mensagem relacionada a acesso da conta."
        else:
            intent = "atendimento_geral"
            confidence = 0.55
            detail = "Mensagem enviada para triagem geral."

        return PredictResponse(
            intent=intent,
            confidence=confidence,
            risk_level=risk_level,
            model_version=self.version,
            detail=detail,
        )


_predictor = IntentPredictor()


async def get_predictor() -> IntentPredictor:
    return _predictor
