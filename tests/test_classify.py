"""Testes HTTP do endpoint POST /classify (TP4).

Cobre os critérios de aceite do contrato (reports/TP4/contrato_classify.md):
JWT, schema estrito de entrada, resposta composta, limites de tamanho,
equivalência com o serviço Python e documentação OpenAPI.
"""
import json
from pathlib import Path

import pytest

from ml.classification_service import ClassificationService

VALID_TEXT = "I lost my bank card. How can I report it through the official support channel?"
BANKING77_LABELS = set(
    json.loads(Path("ml/banking77_labels.json").read_text(encoding="utf-8"))
)


@pytest.fixture(scope="module")
def service() -> ClassificationService:
    return ClassificationService()


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# --- Autenticação -----------------------------------------------------------

def test_classify_sem_token_retorna_401(client):
    r = client.post("/classify", json={"text": VALID_TEXT})
    assert r.status_code == 401


def test_classify_token_invalido_retorna_401(client):
    r = client.post("/classify", json={"text": VALID_TEXT}, headers=_auth("nao.e.um.jwt"))
    assert r.status_code == 401


# --- Caminho feliz ----------------------------------------------------------

def test_classify_valido_retorna_200_e_schema_composto(client, token):
    r = client.post("/classify", json={"text": VALID_TEXT}, headers=_auth(token))
    assert r.status_code == 200, r.text
    body = r.json()

    # Exatamente cinco campos no topo.
    assert set(body) == {"task", "intent", "probability", "model_version", "security"}
    assert body["task"] == "banking_intent_with_security"
    assert body["intent"] in BANKING77_LABELS
    assert 0.0 <= body["probability"] <= 1.0
    assert body["model_version"] == "tp4-banking77-v1"

    sec = body["security"]
    assert set(sec) == {"task", "label", "probability", "probabilities", "model_version"}
    assert sec["task"] == "security_binary"
    assert sec["label"] in {"benign", "threat"}
    assert set(sec["probabilities"]) == {"benign", "threat"}
    # security.probability é o score do próprio label.
    assert sec["probabilities"][sec["label"]] == pytest.approx(sec["probability"])
    assert sec["probabilities"]["benign"] + sec["probabilities"]["threat"] == pytest.approx(1.0)
    # label coerente com as probabilidades (threat só se P(threat) > 0.5).
    esperado = "threat" if sec["probabilities"]["threat"] > 0.5 else "benign"
    assert sec["label"] == esperado


def test_classify_equivale_ao_servico_python(client, token, service):
    r = client.post("/classify", json={"text": VALID_TEXT}, headers=_auth(token))
    assert r.status_code == 200
    assert r.json() == service.classify(VALID_TEXT)


def test_classify_preserva_espacos_e_pontuacao(client, token, service):
    texto = "  Hello!!  I need   help, please... ATM #42?  "
    r = client.post("/classify", json={"text": texto}, headers=_auth(token))
    assert r.status_code == 200
    # Mesma saída do serviço recebendo o texto original integral (sem strip/trunc).
    assert r.json() == service.classify(texto)


# --- Schema estrito de entrada (422) ---------------------------------------

@pytest.mark.parametrize("payload", [
    {},                                   # text ausente
    {"text": ""},                         # vazio
    {"text": "   "},                      # só espaços
    {"text": 123},                        # número
    {"text": None},                       # null
    {"text": ["a", "b"]},                 # lista
    {"text": True},                       # bool
    {"text": VALID_TEXT, "extra": "x"},   # campo extra (extra='forbid')
])
def test_classify_entradas_invalidas_retornam_422(client, token, payload):
    r = client.post("/classify", json=payload, headers=_auth(token))
    assert r.status_code == 422, (payload, r.text)
    # O handler não devolve o valor enviado.
    assert "erros" in r.json()


def test_classify_limite_4000_aceito(client, token):
    r = client.post("/classify", json={"text": "a" * 4000}, headers=_auth(token))
    assert r.status_code == 200, r.text


def test_classify_4001_rejeitado_sem_truncar(client, token):
    r = client.post("/classify", json={"text": "a" * 4001}, headers=_auth(token))
    assert r.status_code == 422


# --- Rate limiting por usuário ----------------------------------------------

def test_classify_rate_limit_retorna_429(client, token):
    from app.main import app
    from app.services.rate_limit import LoginRateLimiter

    # Janela com apenas 2 classificações para exercitar o limite.
    app.state.classify_limiter = LoginRateLimiter(2, 60)
    ok1 = client.post("/classify", json={"text": VALID_TEXT}, headers=_auth(token))
    ok2 = client.post("/classify", json={"text": VALID_TEXT}, headers=_auth(token))
    blocked = client.post("/classify", json={"text": VALID_TEXT}, headers=_auth(token))
    assert ok1.status_code == 200 and ok2.status_code == 200
    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) >= 1


def test_classify_rate_limit_nao_afeta_sem_token(client):
    from app.main import app
    from app.services.rate_limit import LoginRateLimiter

    # Mesmo com limite saturado, falta de token resolve antes: 401, não 429.
    app.state.classify_limiter = LoginRateLimiter(1, 60)
    client_resp = client.post("/classify", json={"text": VALID_TEXT})
    assert client_resp.status_code == 401


# --- OpenAPI ----------------------------------------------------------------

def test_openapi_documenta_classify_com_seguranca_e_jwt(client):
    spec = client.get("/openapi.json").json()
    op = spec["paths"]["/classify"]["post"]
    # Autenticação declarada.
    assert op.get("security"), "rota /classify deve exigir JWT no OpenAPI"
    # Schema de saída com o objeto security aninhado.
    ref = op["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]
    schema_name = ref.split("/")[-1]
    props = spec["components"]["schemas"][schema_name]["properties"]
    assert set(props) == {"task", "intent", "probability", "model_version", "security"}
    # Erros documentados (inclui 429 do limite por usuário).
    assert {"401", "422", "429", "503"} <= set(op["responses"])
