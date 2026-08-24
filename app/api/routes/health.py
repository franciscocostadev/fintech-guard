from fastapi import APIRouter
from sqlalchemy import text

from app import __version__
from app.core.config import get_settings
from app.db.session import engine
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Status da API",
)
async def health() -> HealthResponse:
    settings = get_settings()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "up"
    except Exception:
        # rota pública, então o motivo da falha não entra na resposta
        db_status = "down"

    return HealthResponse(
        status="ok" if db_status == "up" else "degraded",
        app=settings.app_name,
        version=__version__,
        environment=settings.environment,
        database=db_status,
    )
