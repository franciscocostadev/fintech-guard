import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html
from sqlmodel import SQLModel

from app import __version__
from app.api.routes import api_router
from app.core.config import get_settings
from app.db.session import engine
from app.core.middleware import (
    LoginRateLimitMiddleware, SecurityHeadersMiddleware, security_headers,
)
from app.services.rate_limit import LoginRateLimiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # em produção isso vira migração (Alembic)
    SQLModel.metadata.create_all(bind=engine)
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
    docs_url=None,
    redoc_url=None,
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.state.login_limiter = LoginRateLimiter(
    settings.login_max_attempts, settings.login_window_seconds
)
app.add_middleware(LoginRateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    expose_headers=["Retry-After", "Location"],
)


app.add_middleware(SecurityHeadersMiddleware)


SWAGGER_INTEGRITY = {
    "swagger-ui-bundle.js": (
        "sha384-wmyclcVGX/WhUkdkATwhaK1X1JtiNrr2EoYJ+diV3vj4v6OC5yCeSu+yW13SYJep"
    ),
    "swagger-ui.css": (
        "sha384-wxLW6kwyHktdDGr6Pv1zgm/VGJh99lfUbzSn6HNHBENZlCN7W602k9VkGdxuFvPn"
    ),
}


if not settings.is_production:
    @app.get("/docs", include_in_schema=False)
    async def swagger_docs(request: Request):
        html = get_swagger_ui_html(
            openapi_url="/openapi.json", title=f"{settings.app_name} - Swagger UI",
            swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui-bundle.js",
            swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.17.14/swagger-ui.css",
            swagger_favicon_url="/favicon.ico",
            swagger_ui_parameters={"validatorUrl": None},
        ).body.decode()
        # SRI calculado sobre os bytes dos assets da versão fixa acima.
        for asset, integrity in SWAGGER_INTEGRITY.items():
            html = html.replace(
                f'{asset}"', f'{asset}" integrity="{integrity}" crossorigin="anonymous"'
            )
        html = html.replace("<script", f'<script nonce="{request.state.csp_nonce}"')
        return HTMLResponse(html)

    @app.get("/redoc", include_in_schema=False)
    async def redoc_redirect():
        return RedirectResponse("/docs")


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
        # ServerErrorMiddleware está fora dos middlewares registrados no FastAPI.
        headers=security_headers(getattr(request.state, "csp_nonce", "")),
    )


app.include_router(api_router)
