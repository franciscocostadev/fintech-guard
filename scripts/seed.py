"""Cria as tabelas e um usuário pra testar a API. Uso: python -m scripts.seed"""

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models import User


def main() -> None:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        ja_existe = (
            db.query(User).filter(User.username == settings.seed_username).first()
        )
        if ja_existe:
            print(f"Usuário '{settings.seed_username}' já existe.")
            return

        db.add(
            User(
                username=settings.seed_username,
                hashed_password=hash_password(settings.seed_password),
                full_name="Analista de Atendimento",
                role="analyst",
            )
        )
        db.commit()
        print(f"Usuário '{settings.seed_username}' criado.")


if __name__ == "__main__":
    main()
