import re
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlmodel import select

from app.core.config import Settings
from app.db.session import SessionLocal
from app.main import app
from app.models.audit import PredictionLog
from app.services.predictor import get_predictor
from app.services.rate_limit import LoginRateLimiter
from tests.conftest import PASSWORD, USERNAME


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_recurso_por_id_exige_token(client):
    response = client.get("/predictions/1")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_ownership_bloqueia_outro_usuario_inclusive_admin(client, token, other_token):
    created = client.post("/predict", json={"message": "Cartão bloqueado"}, headers=bearer(token))
    assert created.status_code == 200
    resource = created.headers["location"]
    own = client.get(resource, headers=bearer(token))
    assert own.status_code == 200
    assert own.json()["id"] == created.json()["id"]
    assert "message_hash" not in own.json()
    foreign = client.get(resource, headers=bearer(other_token))
    missing = client.get("/predictions/99999999", headers=bearer(other_token))
    assert foreign.status_code == missing.status_code == 404
    assert foreign.json() == missing.json()
    # Também não pode transferir ownership por query string.
    assert client.get(resource + f"?username={USERNAME}", headers=bearer(other_token)).status_code == 404


def test_predict_rejeita_extra_sem_persistir(client, token):
    with SessionLocal() as db:
        before = len(db.exec(select(PredictionLog)).all())
    response = client.post(
        "/predict", headers=bearer(token),
        json={"message": "Olá", "username": "outro_analista", "role": "admin"},
    )
    assert response.status_code == 422
    assert "outro_analista" not in response.text
    with SessionLocal() as db:
        assert len(db.exec(select(PredictionLog)).all()) == before


def test_login_rejeita_campo_extra_no_form(client):
    response = client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD, "role": "admin"})
    assert response.status_code == 422
    assert PASSWORD not in response.text
    assert "access_token" not in response.json()


def test_login_suporta_form_oauth2_sem_escalar_permissoes(client):
    response = client.post("/auth/token", data={
        "username": USERNAME, "password": PASSWORD, "grant_type": "password", "scope": "admin",
    })
    assert response.status_code == 200
    assert client.get("/auth/me", headers=bearer(response.json()["access_token"])).json()["role"] == "analyst"


def test_sql_injection_no_username_nao_autentica(client):
    response = client.post("/auth/token", data={"username": "' OR 1=1 --", "password": PASSWORD})
    assert response.status_code == 401
    assert client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD}).status_code == 200


def test_login_rejeita_senha_bcrypt_truncada_em_bytes(client):
    response = client.post("/auth/token", data={"username": USERNAME, "password": "é" * 37})
    assert response.status_code == 422


def test_rate_limit_sexta_tentativa_e_ip_forjado(client):
    for _ in range(5):
        assert client.post("/auth/token", data={"username": USERNAME, "password": "incorreta"}).status_code == 401
    response = client.post(
        "/auth/token", data={"username": USERNAME, "password": PASSWORD},
        headers={"X-Forwarded-For": "203.0.113.7", "X-Real-IP": "203.0.113.8"},
    )
    assert response.status_code == 429
    assert 1 <= int(response.headers["retry-after"]) <= 300
    assert response.headers["x-frame-options"] == "DENY"
    assert client.get("/health").status_code == 200


def test_rate_limit_conta_sucessos_e_bodies_invalidos(client):
    assert client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD}).status_code == 200
    for _ in range(4):
        assert client.post("/auth/token", data={"unexpected": "value"}).status_code == 422
    assert client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD}).status_code == 429


def test_rate_limit_janela_ip_e_concorrencia():
    now = [1000.0]
    limiter = LoginRateLimiter(5, 300, clock=lambda: now[0])
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(lambda _: limiter.consume("same-ip"), range(50)))
    assert results.count(0) == 5
    assert results.count(300) == 45
    assert limiter.consume("other-ip") == 0
    now[0] = 1299.2
    assert limiter.consume("same-ip") == 1
    now[0] = 1300
    assert limiter.consume("same-ip") == 0


def test_rate_limit_memoria_limitada_nao_descarta_buckets_ativos():
    now = [0.0]
    limiter = LoginRateLimiter(1, 300, clock=lambda: now[0], max_keys=2)
    assert limiter.consume("a") == limiter.consume("b") == 0
    assert limiter.consume("c") == 300
    assert limiter.consume("a") == 300
    now[0] = 300
    assert limiter.consume("c") == 0


@pytest.mark.parametrize("path,expected", [("/health", 200), ("/missing", 404), ("/auth/me", 401)])
def test_headers_em_sucesso_e_erros(client, path, expected):
    response = client.get(path)
    assert response.status_code == expected
    assert response.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    csp = response.headers["content-security-policy"]
    assert "default-src 'none'" in csp and "frame-ancestors 'none'" in csp
    assert "unsafe-inline" not in csp and "unsafe-eval" not in csp


def test_headers_em_erro_interno(token):
    def crash():
        raise RuntimeError("internal-sensitive-detail")
    app.dependency_overrides[get_predictor] = crash
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.post("/predict", headers=bearer(token), json={"message": "Olá"})
        assert response.status_code == 500
        assert "internal-sensitive-detail" not in response.text
        for header in ("content-security-policy", "strict-transport-security", "x-frame-options", "x-content-type-options"):
            assert header in response.headers
    finally:
        app.dependency_overrides.pop(get_predictor)


@pytest.mark.parametrize("path", ["/", "/docs"])
def test_html_tem_nonce_compativel_com_csp(client, path):
    first = client.get(path)
    second = client.get(path)
    nonce = re.search(r"'nonce-([^']+)'", first.headers["content-security-policy"])[1]
    assert f'nonce="{nonce}"' in first.text
    assert nonce not in second.headers["content-security-policy"]
    assert "unsafe-inline" not in first.headers["content-security-policy"]
    assert PASSWORD not in first.text and "Troque@Esta#Senha123" not in first.text


def test_cors_allowlist_e_preflight(client):
    allowed = {"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "Authorization,Content-Type"}
    response = client.options("/predict", headers=allowed)
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed["Origin"]
    assert response.headers["x-frame-options"] == "DENY"
    blocked = client.options("/predict", headers={**allowed, "Origin": "https://evil.example"})
    assert blocked.status_code == 400
    assert "access-control-allow-origin" not in blocked.headers
    blocked_get = client.get("/health", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in blocked_get.headers
    assert client.options("/predict", headers={**allowed, "Access-Control-Request-Method": "DELETE"}).status_code == 400


@pytest.mark.parametrize("origin", ["*", "https://*.example.com", "null", "https://example.com/path", "https://user:pass@example.com"])
def test_config_recusa_cors_sem_origem_explicita(origin):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins=origin)


def test_openapi_todos_os_bodies_rejeitam_extras(client):
    spec = client.get("/openapi.json").json()
    for path in spec["paths"].values():
        for operation in path.values():
            for content in operation.get("requestBody", {}).get("content", {}).values():
                model = content["schema"]["$ref"].rsplit("/", 1)[1]
                assert spec["components"]["schemas"][model]["additionalProperties"] is False


def test_swagger_assets_fixados_com_integridade(client):
    html = client.get("/docs").text
    assert html.count('integrity="sha384-') == 2
    assert html.count('crossorigin="anonymous"') == 2
    assert "swagger-ui-dist@5.17.14" in html
