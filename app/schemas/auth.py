from pydantic import BaseModel, Field


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
