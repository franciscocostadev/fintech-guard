import logging
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUser, DbSession
from app.api.docs import AUTH_ERRORS, RATE_LIMITED, VALIDATION_ERROR
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, Token, UserPublic

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
# Executa bcrypt também para usuários inexistentes, reduzindo enumeração por tempo.
_DUMMY_HASH = hash_password("dummy-password-never-used-for-login")


@router.post(
    "/token",
    response_model=Token,
    summary="Gerar token",
    description=(
        "Troca usuário e senha (formulário OAuth2 password, "
        "`application/x-www-form-urlencoded`) por um JWT HS256 com validade "
        "de 15 minutos por padrão.\n\n"
        "**Rate limiting:** 5 tentativas por IP em janela deslizante de 300 s. "
        "Toda chamada conta, inclusive logins válidos e bodies inválidos; a "
        "sexta responde **429** com `Retry-After`. O campo `scope` é aceito "
        "pelo Swagger, mas não concede permissões: o papel vem do banco."
    ),
    response_description="JWT para o header `Authorization: Bearer <token>`.",
    responses={
        401: {**AUTH_ERRORS[401], "description": "Usuário inexistente, inativo ou senha incorreta.",
              "content": {"application/json": {"example": {"detail": "Usuário ou senha inválidos."}}}},
        **VALIDATION_ERROR,
        **RATE_LIMITED,
    },
)
def login_for_access_token(
    db: DbSession,
    credentials: Annotated[LoginRequest, Form()],
) -> Token:
    # O middleware reserva a tentativa atomicamente antes de validar/processar
    # o body. Sucesso não zera o contador e toda chamada consome o limite.
    user = db.exec(select(User).where(User.username == credentials.username)).first()
    password_ok = verify_password(
        credentials.password, user.hashed_password if user else _DUMMY_HASH
    )
    if user is None or not user.is_active or not password_ok:
        logger.warning("Falha de autenticação")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token, expires_in = create_access_token(subject=user.username, scopes=[user.role])
    logger.info("Login autorizado: usuario=%s", user.username)
    return Token(access_token=token, expires_in=expires_in)


@router.get(
    "/me",
    response_model=UserPublic,
    summary="Usuário logado",
    description="Retorna a identidade do token. Não recebe ID: sempre o próprio usuário.",
    responses=AUTH_ERRORS,
)
async def read_current_user(current_user: CurrentUser) -> UserPublic:
    return UserPublic(
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
    )
