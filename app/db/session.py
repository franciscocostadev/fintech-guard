from collections.abc import AsyncGenerator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, create_engine

from app.core.config import get_settings

settings = get_settings()

connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False,  # SQL no log acabaria expondo dado de cliente
)

SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False)


async def get_db() -> AsyncGenerator[Session, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
