import os
import asyncio
import tempfile

os.environ.setdefault("SECRET_KEY", "chave-de-teste-com-mais-de-32-caracteres-aqui-ok")
os.environ.setdefault("ENVIRONMENT", "test")
_db_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"

import pytest
import httpx

from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.main import app
from app.models.user import User

USERNAME = "analista"
PASSWORD = "Senha#Teste123"


class LocalClient:
    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        async def send() -> httpx.Response:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return await client.request(method, url, **kwargs)

        return asyncio.run(send())

    def get(self, url: str, **kwargs) -> httpx.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        return self.request("POST", url, **kwargs)


@pytest.fixture(scope="session", autouse=True)
def _setup_db():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add(
            User(
                username=USERNAME,
                hashed_password=hash_password(PASSWORD),
                role="analyst",
            )
        )
        db.commit()
    yield
    Base.metadata.drop_all(bind=engine)
    os.close(_db_fd)
    os.unlink(_db_path)


@pytest.fixture
def client():
    return LocalClient()


@pytest.fixture
def token(client):
    r = client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]
