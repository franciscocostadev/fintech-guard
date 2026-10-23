from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="`ok` ou `degraded` quando o banco não responde.")
    app: str
    version: str
    environment: str
    database: str = Field(description="`up` ou `down`.")


class ErrorResponse(BaseModel):
    detail: str


class FieldError(BaseModel):
    campo: str = Field(description="Local do erro, por exemplo `body.message`.")
    erro: str


class ValidationErrorResponse(BaseModel):
    """Formato do handler de 422: indica o campo, nunca o valor recebido."""

    detail: str = "Requisição inválida."
    erros: list[FieldError]
