from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import InputModel


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PredictRequest(InputModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
        description="Mensagem do cliente a ser classificada.",
        examples=["Meu cartão foi bloqueado, como desbloqueio?"],
    )
    channel: str = Field(
        default="chat",
        max_length=32,
        description="Canal de origem: chat, whatsapp, email, telefone.",
    )

    @field_validator("message")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("A mensagem não pode ser vazia.")
        return v


class PredictResponse(BaseModel):
    id: int | None = Field(default=None, description="ID da predição persistida.")
    intent: str = Field(description="Intenção prevista (taxonomia BANKING77).")
    confidence: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel = Field(description="Risco de fraude/engenharia social.")
    model_version: str
    detail: str


class PredictionPublic(BaseModel):
    id: int
    intent: str
    confidence: float
    risk_level: RiskLevel
    created_at: datetime
