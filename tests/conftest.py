import os
import tempfile

# Isola os testes do .env e do banco de trabalho do desenvolvedor.
os.environ["SECRET_KEY"] = "chave-de-teste-com-mais-de-32-caracteres-aqui-ok"
os.environ["ENVIRONMENT"] = "test"
os.environ["CORS_ORIGINS"] = "http://localhost:3000,http://127.0.0.1:3000"
os.environ["LOGIN_MAX_ATTEMPTS"] = "5"
os.environ["LOGIN_WINDOW_SECONDS"] = "300"
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_db_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from app.core.security import create_access_token, hash_password
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.user import User
from app.services.rate_limit import LoginRateLimiter

USERNAME = "analista"
PASSWORD = "Senha#Teste123"
OTHER_USERNAME = "outro_analista"


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    SQLModel.metadata.create_all(bind=engine)
    hashed = hash_password(PASSWORD)
    with SessionLocal() as db:
        db.add_all([
            User(username=USERNAME, hashed_password=hashed, role="analyst"),
            User(username=OTHER_USERNAME, hashed_password=hashed, role="admin"),
        ])
        db.commit()
    yield
    engine.dispose()
    os.unlink(_db_path)


@pytest.fixture(autouse=True)
def _reset_limiter():
    app.state.login_limiter = LoginRateLimiter(5, 300)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def token(client):
    r = client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture
def other_token():
    return create_access_token(OTHER_USERNAME, scopes=["admin"])[0]
