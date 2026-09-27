import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlmodel import select

from app.api.deps import CurrentUser, DbSession
from app.models.audit import PredictionLog
from app.schemas.predict import PredictionPublic, PredictRequest, PredictResponse
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
    response: Response,
    current_user: CurrentUser,
    db: DbSession,
    predictor: Annotated[IntentPredictor, Depends(get_predictor)],
) -> PredictResponse:
    result = predictor.predict(payload.message, payload.channel)
    record = PredictionLog(
        username=current_user.username,
        message_hash=hash_message(payload.message),
        message_length=len(payload.message),
        predicted_intent=result.intent,
        confidence=result.confidence,
        risk_level=result.risk_level.value,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    result.id = record.id
    response.headers["Location"] = f"/predictions/{record.id}"
    logger.info("Predição registrada: id=%s usuario=%s", record.id, current_user.username)
    return result


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionPublic,
    summary="Consultar uma predição própria",
    responses={401: {"description": "Token obrigatório."},
               404: {"description": "Predição inexistente ou de outro usuário."}},
)
async def read_prediction(
    prediction_id: Annotated[int, Path(gt=0)],
    current_user: CurrentUser,
    db: DbSession,
) -> PredictionPublic:
    # BOLA: ID e proprietário na MESMA consulta parametrizada. Não existe
    # exceção para administradores, nem confiança em username vindo do cliente.
    record = db.exec(
        select(PredictionLog).where(
            PredictionLog.id == prediction_id,
            PredictionLog.username == current_user.username,
        )
    ).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Predição não encontrada.")
    return PredictionPublic(
        id=record.id,
        intent=record.predicted_intent,
        confidence=record.confidence,
        risk_level=record.risk_level,
        created_at=record.created_at,
    )
