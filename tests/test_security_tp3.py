"""Testes de segurança do TP3: autenticação, BOLA, validação e rate limiting.

Os cinco casos obrigatórios do enunciado estão marcados com [obrigatório N];
os demais cobrem variações que um pentest exploraria a seguir.
"""

import base64
import json
from datetime import timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.user import User
from tests.conftest import OTHER_USERNAME, PASSWORD, USERNAME


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def b64url(data: dict) -> str:
    raw = json.dumps(data, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def predict(client, token, message="Cartão bloqueado"):
    response = client.post("/predict", json={"message": message}, headers=bearer(token))
    assert response.status_code == 200, response.text
    return response


def from_ip(ip: str):
    # TestClient sempre usa o mesmo IP; isto simula clientes distintos.
    async def asgi(scope, receive, send):
        if scope["type"] == "http":
            scope["client"] = (ip, 50000)
        await app(scope, receive, send)
    return asgi


# --- Autenticação ---------------------------------------------------------

@pytest.mark.parametrize("method,path", [
    ("GET", "/auth/me"), ("POST", "/predict"), ("GET", "/predictions/1"),
])
def test_obrigatorio_1_rotas_protegidas_sem_token_retornam_401(client, method, path):
    response = client.request(method, path, json={"message": "Olá"})
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {"detail": "Credenciais inválidas ou expiradas."}


def test_obrigatorio_2_token_adulterado_ou_expirado_retorna_401(client, token):
    # Troca o "sub" mantendo a assinatura original: tentativa de se passar por outro.
    header, _, signature = token.split(".")
    claims = jwt.decode(token, options={"verify_signature": False})
    forged = f"{header}.{b64url({**claims, 'sub': OTHER_USERNAME})}.{signature}"
    expired, _ = create_access_token(USERNAME, expires_delta=timedelta(seconds=-1))

    for bad in (forged, expired):
        response = client.get("/auth/me", headers=bearer(bad))
        assert response.status_code == 401
        # mesma mensagem para todos os casos: não revela o motivo da recusa
        assert response.json() == {"detail": "Credenciais inválidas ou expiradas."}
    assert client.get("/auth/me", headers=bearer(token)).status_code == 200


def test_token_alg_none_chave_errada_e_sem_issuer_sao_recusados(client):
    settings = get_settings()
    claims = {"sub": USERNAME, "scopes": ["admin"], "iat": 1, "exp": 4_102_444_800,
              "iss": settings.app_name}
    alg_none = f"{b64url({'alg': 'none', 'typ': 'JWT'})}.{b64url(claims)}."
    wrong_key = jwt.encode(claims, "chave-do-atacante-com-mais-de-32-caracteres", algorithm="HS256")
    no_issuer = jwt.encode({k: v for k, v in claims.items() if k != "iss"},
                           settings.secret_key, algorithm="HS256")
    for bad in (alg_none, wrong_key, no_issuer, "nao.e.jwt", ""):
        assert client.get("/auth/me", headers=bearer(bad)).status_code == 401


def test_token_valido_de_usuario_inativo_ou_removido_retorna_401(client):
    with SessionLocal() as db:
        db.add(User(username="ex_funcionario", hashed_password=hash_password(PASSWORD),
                    is_active=False))
        db.commit()
    for username in ("ex_funcionario", "nunca_existiu"):
        token, _ = create_access_token(username)
        assert client.get("/auth/me", headers=bearer(token)).status_code == 401
    # o login também recusa o inativo, com a mesma resposta de senha errada
    response = client.post("/auth/token", data={"username": "ex_funcionario", "password": PASSWORD})
    assert response.status_code == 401
    assert response.json() == {"detail": "Usuário ou senha inválidos."}


def test_login_nao_diferencia_usuario_inexistente_de_senha_errada(client):
    unknown = client.post("/auth/token", data={"username": "fantasma", "password": PASSWORD})
    wrong = client.post("/auth/token", data={"username": USERNAME, "password": "errada"})
    assert unknown.status_code == wrong.status_code == 401
    assert unknown.json() == wrong.json()


# --- Autorização (BOLA) ---------------------------------------------------

def test_obrigatorio_3_bola_isolamento_nos_dois_sentidos(client, token, other_token):
    mine = predict(client, token).json()["id"]
    theirs = predict(client, other_token).json()["id"]

    assert client.get(f"/predictions/{mine}", headers=bearer(token)).status_code == 200
    assert client.get(f"/predictions/{theirs}", headers=bearer(other_token)).status_code == 200
    # A não lê B e B (admin) não lê A; resposta igual à de um ID inexistente
    for owner_id, intruder in ((theirs, token), (mine, other_token)):
        response = client.get(f"/predictions/{owner_id}", headers=bearer(intruder))
        assert response.status_code == 404
        assert response.json() == {"detail": "Predição não encontrada."}


def test_bola_enumeracao_sequencial_nao_vaza_predicoes_alheias(client, token, other_token):
    foreign = {predict(client, other_token).json()["id"] for _ in range(3)}
    own = predict(client, token).json()["id"]
    found = {
        i for i in range(1, own + 5)
        if client.get(f"/predictions/{i}", headers=bearer(token)).status_code == 200
    }
    assert own in found
    assert not found & foreign


def test_bola_identidade_vem_do_token_e_nao_do_cliente(client, token):
    # parâmetros e headers forjados não mudam o dono nem o usuário de /auth/me
    me = client.get(f"/auth/me?username={OTHER_USERNAME}", headers={
        **bearer(token), "X-User": OTHER_USERNAME, "X-Forwarded-User": OTHER_USERNAME,
    })
    assert me.json()["username"] == USERNAME


# --- Validação de entradas ------------------------------------------------

def test_obrigatorio_4_campo_extra_no_body_retorna_422(client, token):
    response = client.post("/predict", headers=bearer(token), json={
        "message": "Quero cancelar meu pedido", "admin": True,
    })
    assert response.status_code == 422
    assert response.json()["erros"][0]["campo"] == "body.admin"


@pytest.mark.parametrize("body", [
    {"message": "x" * 1001},                    # acima do limite
    {"message": "   \n\t "},                    # só espaços
    {"message": 123},                           # tipo errado
    {"message": ["lista"]},
    {"message": None},
    {},                                         # campo obrigatório ausente
    {"message": "Olá", "channel": "sms"},       # fora da allowlist
    {"message": "Olá", "channel": "x" * 5000},
])
def test_predict_rejeita_entradas_invalidas(client, token, body):
    response = client.post("/predict", json=body, headers=bearer(token))
    assert response.status_code == 422
    assert response.json()["detail"] == "Requisição inválida."


def test_predict_aceita_limite_exato_e_todos_os_canais(client, token):
    assert predict(client, token, "x" * 1000).json()["id"]
    for channel in ("chat", "whatsapp", "email", "telefone"):
        response = client.post("/predict", headers=bearer(token),
                               json={"message": "Olá", "channel": channel})
        assert response.status_code == 200


def test_predict_rejeita_json_malformado_e_content_type_errado(client, token):
    malformed = client.post("/predict", content=b'{"message": ', headers={
        **bearer(token), "Content-Type": "application/json"})
    plain = client.post("/predict", content=b"message=Ola", headers={
        **bearer(token), "Content-Type": "text/plain"})
    assert malformed.status_code == plain.status_code == 422


@pytest.mark.parametrize("payload", [
    "<script>alert(1)</script>", "' OR 1=1 --", "{{7*7}}", "../../etc/passwd",
])
def test_payloads_de_injecao_sao_tratados_como_texto_e_nao_refletidos(client, token, payload):
    response = predict(client, token, f"Meu cartão {payload}")
    assert payload not in response.text
    assert client.get(response.headers["location"], headers=bearer(token)).status_code == 200


@pytest.mark.parametrize("prediction_id", [
    "0", "-1", "abc", "1.5", "1e3", "1;DROP TABLE users", str(2**63), str(2**70),
])
def test_id_invalido_ou_fora_do_intervalo_retorna_422_e_nao_500(token, prediction_id):
    # 2**63 estourava o INTEGER do SQLite e devolvia 500 antes do limite no Path.
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(f"/predictions/{prediction_id}", headers=bearer(token))
    assert response.status_code == 422


def test_login_valida_tamanho_de_usuario(client):
    response = client.post("/auth/token", data={"username": "a" * 65, "password": PASSWORD})
    assert response.status_code == 422
    assert "a" * 65 not in response.text


# --- Rate limiting --------------------------------------------------------

def test_obrigatorio_5_rate_limit_bloqueia_forca_bruta_no_login(client):
    attempts = [
        client.post("/auth/token", data={"username": USERNAME, "password": f"chute-{i}"})
        for i in range(6)
    ]
    assert [r.status_code for r in attempts] == [401] * 5 + [429]
    assert 1 <= int(attempts[-1].headers["retry-after"]) <= 300
    # bloqueado mesmo acertando a senha: o atacante não ganha a 6ª tentativa
    correct = client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD})
    assert correct.status_code == 429


def test_rate_limit_vale_por_ip_e_nao_afeta_outros_clientes(token):
    with TestClient(from_ip("198.51.100.1")) as attacker, \
            TestClient(from_ip("198.51.100.2")) as legit:
        for _ in range(5):
            attacker.post("/auth/token", data={"username": USERNAME, "password": "x"})
        assert attacker.post("/auth/token", data={"username": USERNAME, "password": PASSWORD}).status_code == 429
        assert legit.post("/auth/token", data={"username": USERNAME, "password": PASSWORD}).status_code == 200
        # token já emitido continua válido nas rotas protegidas
        assert attacker.get("/auth/me", headers=bearer(token)).status_code == 200


def test_rate_limit_nao_e_contornado_por_barra_final_ou_alternancia_de_usuario(client):
    for i in range(5):
        path = "/auth/token/" if i % 2 else "/auth/token"
        # sem seguir o redirect 307, para cada chamada valer exatamente uma tentativa
        client.post(path, data={"username": f"usuario{i}", "password": "x"}, follow_redirects=False)
    response = client.post("/auth/token", data={"username": OTHER_USERNAME, "password": PASSWORD})
    assert response.status_code == 429
