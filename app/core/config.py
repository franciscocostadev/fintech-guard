from functools import lru_cache
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Fintech Guard API"
    environment: str = "development"

    secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15

    database_url: str = "sqlite:///./fintech_guard.db"
    cors_origins: str = "http://localhost:3000"

    login_max_attempts: int = Field(default=5, ge=1, le=100)
    login_window_seconds: int = Field(default=300, ge=1, le=3600)

    seed_username: str = "analista"
    seed_password: str = "Troque@Esta#Senha123"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @field_validator("cors_origins")
    @classmethod
    def _explicit_origins(cls, value: str) -> str:
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        for origin in origins:
            parsed = urlsplit(origin)
            # Uma origem é apenas esquema, host e porta; não URL com caminho.
            if (
                "*" in origin or parsed.scheme not in {"http", "https"}
                or not parsed.hostname or parsed.username or parsed.password
                or parsed.path or parsed.query or parsed.fragment
                or any(char.isspace() for char in origin)
            ):
                raise ValueError("CORS exige origens HTTP(S) explícitas, sem curingas ou caminhos.")
            _ = parsed.port  # valida portas malformadas
        return ",".join(dict.fromkeys(origins))

    @field_validator("secret_key")
    @classmethod
    def _reject_default_secret(cls, v: str) -> str:
        if "troque" in v.lower():
            raise ValueError(
                "SECRET_KEY ainda está com o valor de exemplo. Gere outra com: "
                'python -c "import secrets; print(secrets.token_urlsafe(64))"'
            )
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
