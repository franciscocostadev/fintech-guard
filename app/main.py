import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.routes import api_router
from app.core.config import get_settings
from app.db.session import Base, engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # em produção isso vira migração (Alembic)
    Base.metadata.create_all(bind=engine)
    logger.info("Fintech Guard API iniciada (env=%s)", settings.environment)
    yield
    logger.info("Fintech Guard API encerrada")


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "API de apoio ao atendimento bancário: classifica a intenção do cliente "
        "e sinaliza risco de fraude/engenharia social."
    ),
    lifespan=lifespan,
    # sem Swagger em produção pra não publicar o mapa da API
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # o handler padrão devolve o input recebido dentro do erro; se o cliente
    # digitou o CPF no campo errado, o dado voltaria na resposta
    campos = [
        {"campo": ".".join(str(p) for p in e.get("loc", [])), "erro": e.get("msg", "")}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Requisição inválida.", "erros": campos},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Erro não tratado em %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erro interno do servidor."},
    )


app.include_router(api_router)
