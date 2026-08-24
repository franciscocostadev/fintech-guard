from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import (
    ExpiredSignatureError,
    InvalidTokenError,
    decode_access_token,
)
from app.db.session import get_db
from app.models.user import User

# tokenUrl alimenta o botão "Authorize" do Swagger.
# auto_error=False pra devolver a nossa mensagem no lugar do "Not authenticated"
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token", scheme_name="OAuth2Password", auto_error=False
)

# mensagem genérica de propósito: não dizemos se o token expirou, foi adulterado
# ou se o usuário existe
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas ou expiradas.",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    if not token:
        raise CREDENTIALS_EXCEPTION

    try:
        payload = decode_access_token(token)
    except (ExpiredSignatureError, InvalidTokenError):
        raise CREDENTIALS_EXCEPTION from None

    username = payload.get("sub")
    if not username:
        raise CREDENTIALS_EXCEPTION

    # consultar o banco a cada request permite desativar um usuário sem
    # esperar o token expirar
    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise CREDENTIALS_EXCEPTION
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]


def require_role(*roles: str):
    async def _checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para este recurso.",
            )
        return user

    return _checker
