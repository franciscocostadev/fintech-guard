import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, DbSession
from app.models.audit import PredictionLog
from app.schemas.predict import PredictRequest, PredictResponse
from app.services.predictor import IntentPredictor, get_predictor, hash_message

logger = logging.getLogger(__name__)
router = APIRouter(tags=["predict"])


@router.post(
    "/predict",
    response_model=PredictResponse,
    status_code=status.HTTP_200_OK,
    summary="Classificar mensagem",
    responses={401: {"description": "Token ausente, inválido ou expirado."}},
)
async def predict(
    payload: PredictRequest,
    current_user: CurrentUser,
    db: DbSession,
    predictor: Annotated[IntentPredictor, Depends(get_predictor)],
) -> PredictResponse:
    result = predictor.predict(payload.message, payload.channel)

    # a mensagem em si não é gravada nem logada, só o hash
    db.add(
        PredictionLog(
            username=current_user.username,
            message_hash=hash_message(payload.message),
            message_length=len(payload.message),
            predicted_intent=result.intent,
            confidence=result.confidence,
            risk_level=result.risk_level.value,
        )
    )
    db.commit()

    logger.info(
        "Predição registrada: usuario=%s intent=%s risco=%s",
        current_user.username,
        result.intent,
        result.risk_level.value,
    )
    return result
