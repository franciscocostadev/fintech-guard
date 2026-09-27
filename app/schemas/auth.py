from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.base import InputModel


class LoginRequest(InputModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=72, repr=False)
    # Campos OAuth2 usados pelo Swagger. Permissões vêm somente do banco.
    grant_type: Literal["password"] = "password"
    scope: str = Field(default="", max_length=256)
    client_id: str | None = Field(default=None, max_length=128)
    client_secret: str | None = Field(default=None, max_length=256, repr=False)

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Senha maior que 72 bytes.")
        return value



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Validade do token em segundos.")


class TokenPayload(BaseModel):
    sub: str
    scopes: list[str] = []
    jti: str | None = None


class UserPublic(BaseModel):
    username: str
    full_name: str | None = None
    role: str
