from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Atendente/analista. Username é único e não pode ser alterado pela API."""

    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=64, unique=True, index=True)
    hashed_password: str = Field(max_length=128)
    full_name: str | None = Field(default=None, max_length=120)
    role: str = Field(default="analyst", max_length=32)
    is_active: bool = True
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )
