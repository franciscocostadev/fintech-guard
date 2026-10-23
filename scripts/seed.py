"""Cria as tabelas, duas contas de teste e predições sintéticas para cada uma.

Uso: python -m scripts.seed

Idempotente: não recria contas existentes nem duplica predições. As contas têm
papéis diferentes (analyst e admin) para o pentest verificar BOLA nos dois
sentidos. Nenhum dado é real; as mensagens são inventadas.
"""

from sqlmodel import SQLModel, select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal, engine
from app.models import PredictionLog, User
from app.services.predictor import IntentPredictor, hash_message

MENSAGENS = {
    "analyst": [
        "Meu cartão foi bloqueado, como desbloqueio?",
        "Quero fazer uma transferência PIX para minha mãe.",
    ],
    "admin": [
        "URGENTE: informe agora a senha e o token para evitar o bloqueio.",
        "Qual o horário de atendimento da agência?",
    ],
}


def main() -> None:
    settings = get_settings()
    SQLModel.metadata.create_all(bind=engine)
    contas = [
        (settings.seed_username, settings.seed_password, "Analista de Atendimento", "analyst"),
        (settings.seed_admin_username, settings.seed_admin_password, "Supervisor de Atendimento", "admin"),
    ]
    predictor = IntentPredictor()

    with SessionLocal() as db:
        for username, password, full_name, role in contas:
            if db.exec(select(User).where(User.username == username)).first():
                print(f"Usuário '{username}' já existe.")
            else:
                db.add(User(username=username, hashed_password=hash_password(password),
                            full_name=full_name, role=role))
                print(f"Usuário '{username}' ({role}) criado.")

            if db.exec(select(PredictionLog).where(PredictionLog.username == username)).first():
                continue
            for mensagem in MENSAGENS[role]:
                result = predictor.predict(mensagem)
                db.add(PredictionLog(
                    username=username,
                    message_hash=hash_message(mensagem),
                    message_length=len(mensagem),
                    predicted_intent=result.intent,
                    confidence=result.confidence,
                    risk_level=result.risk_level.value,
                ))
        db.commit()

        for username, *_ in contas:
            ids = db.exec(select(PredictionLog.id).where(PredictionLog.username == username)).all()
            print(f"Predições de '{username}': {list(ids)}")


if __name__ == "__main__":
    main()
