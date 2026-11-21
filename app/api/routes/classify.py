"""POST /classify — intenção bancária (BANKING77) + análise de segurança (TP4).

Rota autenticada por JWT que consome o `ClassificationService` carregado no
startup. Definida como `def` (síncrona) para que o FastAPI execute a inferência
de CPU no threadpool, sem bloquear o event loop. Não persiste texto bruto nem
recarrega modelos por requisição.
"""
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status  # noqa: F401

from app.api.deps import CurrentUser, enforce_classify_rate_limit
from app.api.docs import AUTH_ERRORS, RATE_LIMITED_USER, SERVICE_UNAVAILABLE, VALIDATION_ERROR
from app.schemas.classify import ClassifyRequest, ClassifyResponse
from app.services.classifier import get_classification_service
from ml.classification_service import ClassificationService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["classify"])


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Classificar intenção bancária e segurança",
    description=(
        "Recebe `{\"text\": \"...\"}` (string de 1 a 4000 caracteres), autentica "
        "via JWT e retorna a intenção BANKING77 com sua probabilidade, mais a "
        "análise de segurança do conteúdo.\n\n"
        "O body aceita **apenas** `text`; qualquer outro campo, tipo incorreto, "
        "vazio ou acima de 4000 caracteres gera **422**. Os dois scores têm "
        "significados distintos e não devem ser somados: `threat` descreve o "
        "conteúdo e não acusa o remetente."
    ),
    response_description="Intenção prevista, probabilidade e análise de segurança.",
    responses={**AUTH_ERRORS, **VALIDATION_ERROR, **RATE_LIMITED_USER, **SERVICE_UNAVAILABLE},
    dependencies=[Depends(enforce_classify_rate_limit)],
)
def classify(
    payload: ClassifyRequest,
    current_user: CurrentUser,
    service: Annotated[ClassificationService, Depends(get_classification_service)],
) -> ClassifyResponse:
    try:
        result = service.classify(payload.text)
    except (ValueError, RuntimeError):
        # O schema já garantiu a entrada; erro aqui é do modelo em execução.
        # 503 sem traceback, caminho local ou classe inventada.
        logger.exception("Falha de inferência em /classify (usuario=%s)", current_user.username)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de classificação indisponível.",
        ) from None
    return ClassifyResponse(**result)
