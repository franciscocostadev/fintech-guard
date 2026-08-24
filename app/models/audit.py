from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PredictionLog(Base):
    """Trilha das classificações feitas no /predict.

    Guarda o hash da mensagem e não o texto, pra manter a rastreabilidade sem
    criar mais um lugar com CPF e saldo dentro.
    """

    __tablename__ = "prediction_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    message_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    message_length: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_intent: Mapped[str] = mapped_column(String(64), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True, nullable=False
    )
