from tests.conftest import PASSWORD, USERNAME


def test_health_e_publico(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["database"] == "up"


def test_home_exibe_interface_simples(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "Fintech Guard" in r.text
    assert "Not Found" not in r.text


def test_health_traz_cabecalhos_de_seguranca(client):
    r = client.get("/health")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"


def test_token_com_credenciais_validas(client):
    r = client.post("/auth/token", data={"username": USERNAME, "password": PASSWORD})
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"] and body["expires_in"] > 0


def test_token_com_senha_errada(client):
    r = client.post("/auth/token", data={"username": USERNAME, "password": "errada"})
    assert r.status_code == 401


def test_predict_sem_token(client):
    r = client.post("/predict", json={"message": "meu cartão foi bloqueado"})
    assert r.status_code == 401


def test_predict_com_token_invalido(client):
    r = client.post(
        "/predict",
        json={"message": "meu cartão foi bloqueado"},
        headers={"Authorization": "Bearer token.falso.aqui"},
    )
    assert r.status_code == 401


def test_predict_autenticado_retorna_intencao_por_regras(client, token):
    r = client.post(
        "/predict",
        json={"message": "Meu cartão foi bloqueado, como desbloqueio?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["intent"] == "cartao_bloqueado"
    assert body["model_version"] == "regras-v1"
    assert body["risk_level"] == "low"


def test_predict_rejeita_mensagem_vazia(client, token):
    r = client.post(
        "/predict",
        json={"message": "   "},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422


def test_erro_de_validacao_nao_devolve_o_input(client, token):
    cpf = "123.456.789-00"
    r = client.post(
        "/predict",
        json={"message": cpf * 200},  # estoura o max_length
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 422
    assert cpf not in r.text


def test_auth_me(client, token):
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == USERNAME
    assert "hashed_password" not in body


def test_predict_sem_token_responde_em_portugues(client):
    r = client.post("/predict", json={"message": "oi"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Credenciais inválidas ou expiradas."
