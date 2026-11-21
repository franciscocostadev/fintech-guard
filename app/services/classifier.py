"""Carregamento e acesso ao serviço de classificação composto (TP4).

O `ClassificationService` carrega os dois artefatos (BANKING77 + segurança) com
verificação de hash e de versões de dependências. É construído uma vez por
processo no lifespan da aplicação (ver `app/main.py`) e exposto via
`request.app.state.classification_service`. Falha de artefato impede a
inicialização; indisponibilidade em execução vira 503 sem vazar detalhes.
"""
import logging

from fastapi import HTTPException, Request, status

from ml.classification_service import ClassificationService

logger = logging.getLogger(__name__)

STATE_ATTR = "classification_service"


def build_classification_service() -> ClassificationService:
    """Constrói o serviço; propaga erro de artefato para falhar o startup."""
    service = ClassificationService()
    logger.info(
        "ClassificationService carregado: banking=%s security=%s",
        service.banking.metadata["model_version"],
        service.security.metadata["model_version"],
    )
    return service


def get_classification_service(request: Request) -> ClassificationService:
    """Dependência: devolve o serviço do estado da app ou 503 se ausente."""
    service = getattr(request.app.state, STATE_ATTR, None)
    if service is None:
        # Startup deveria ter carregado; ausência indica indisponibilidade real.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de classificação indisponível.",
        )
    return service
