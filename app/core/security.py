import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import get_settings

MAX_PASSWORD_BYTES = 72  # limite do bcrypt


def hash_password(plain_password: str) -> str:
    pwd = plain_password.encode("utf-8")
    if len(pwd) > MAX_PASSWORD_BYTES:
        # o bcrypt trunca em silêncio, então é melhor recusar
        raise ValueError("Senha maior que 72 bytes.")
    return bcrypt.hashpw(pwd, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )
    except ValueError:
        # hash malformado no banco
        return False


def create_access_token(
    subject: str,
    scopes: list[str] | None = None,
    expires_delta: timedelta | None = None,
) -> tuple[str, int]:
    """Retorna (token, validade em segundos)."""
    settings = get_settings()
    expires_delta = expires_delta or timedelta(
        minutes=settings.access_token_expire_minutes
    )
    now = datetime.now(timezone.utc)

    # JWT é assinado, não criptografado: só identificador e permissões aqui,
    # nada de CPF ou saldo.
    payload = {
        "sub": subject,
        "scopes": scopes or [],
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": str(uuid.uuid4()),
        "iss": settings.app_name,
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, int(expires_delta.total_seconds())


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    # algorithms fixo fecha a porta pro "alg: none" e pra confusão de algoritmo
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.app_name,
        options={"require": ["exp", "sub", "iat"]},
    )


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "ExpiredSignatureError",
    "InvalidTokenError",
]
