import logging
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, Request, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import Token, UserPublic
from app.services import rate_limit

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


def _client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


@router.post("/token", response_model=Token, summary="Gerar token")
async def login_for_access_token(
    request: Request,
    db: DbSession,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
) -> Token:
    settings = get_settings()
    key = _client_key(request)

    if rate_limit.is_blocked(
        key, settings.login_max_attempts, settings.login_window_seconds
    ):
        logger.warning("Login bloqueado por rate limit: origem=%s", key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas tentativas de login. Tente novamente mais tarde.",
        )

    user = db.query(User).filter(User.username == username).first()

    # usuário inexistente, senha errada e conta inativa dão a mesma resposta,
    # senão dá pra descobrir quem existe testando login
    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.hashed_password)
    ):
        rate_limit.register_failure(key, settings.login_window_seconds)
        logger.warning(
            "Falha de autenticação: usuario=%s origem=%s", username, key
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    rate_limit.reset(key)
    token, expires_in = create_access_token(subject=user.username, scopes=[user.role])
    logger.info("Login autorizado: usuario=%s origem=%s", user.username, key)
    return Token(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=UserPublic, summary="Usuário logado")
async def read_current_user(current_user: CurrentUser) -> UserPublic:
    return UserPublic(
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
    )
