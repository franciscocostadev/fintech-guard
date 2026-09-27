from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class PredictionLog(SQLModel, table=True):
    """Classificação e proprietário; mantém compatibilidade com o banco existente.

    Guarda o hash da mensagem, nunca seu texto. O proprietário vem da sessão
    autenticada, nunca do body ou de parâmetros enviados pelo cliente.
    """

    __tablename__ = "prediction_logs"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=64, index=True)
    message_hash: str = Field(max_length=64)
    message_length: int
    predicted_intent: str = Field(max_length=64)
    confidence: float
    risk_level: str = Field(max_length=16)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        index=True,
    )
