"""Respostas de erro reaproveitadas na documentação OpenAPI das rotas."""

from app.schemas.common import ErrorResponse, ValidationErrorResponse

AUTH_ERRORS = {
    401: {
        "model": ErrorResponse,
        "description": "Token ausente, adulterado, expirado ou de usuário inativo.",
        "content": {"application/json": {"example": {"detail": "Credenciais inválidas ou expiradas."}}},
    },
}

VALIDATION_ERROR = {
    422: {
        "model": ValidationErrorResponse,
        "description": "Entrada inválida ou com campos não previstos. O valor recebido não é devolvido.",
        "content": {"application/json": {"example": {
            "detail": "Requisição inválida.",
            "erros": [{"campo": "body.message", "erro": "String should have at most 1000 characters"}],
        }}},
    },
}

RATE_LIMITED = {
    429: {
        "model": ErrorResponse,
        "description": "Limite de tentativas de login por IP excedido.",
        "headers": {"Retry-After": {"description": "Segundos até a próxima tentativa.",
                                    "schema": {"type": "integer"}}},
        "content": {"application/json": {"example": {
            "detail": "Muitas tentativas de login. Tente novamente mais tarde."}}},
    },
}
