# Fintech Guard

Projeto do bloco para uma API de apoio ao atendimento bancario.

Nesta primeira entrega eu deixei a base pronta: dataset analisado, API FastAPI
rodando, login com JWT e documentacao de seguranca.

O classificador ainda nao usa modelo treinado. Por enquanto o `/predict` usa
regras simples, so para a rota ja funcionar.

## O que tem no projeto

- API em FastAPI
- rotas separadas em `app/api/routes/`
- modelos SQLAlchemy em `app/models/`
- banco SQLite local
- autenticacao JWT com `OAuth2PasswordBearer`
- EDA do BANKING77
- DFD e analise CIA

Rotas principais:

- `GET /health`
- `POST /auth/token`
- `POST /predict`
- `GET /auth/me`

## Rodando localmente

Use Python 3.11 ou mais novo.

```bash
git clone https://github.com/franciscocostadev/fintech-guard.git
cd fintech-guard

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Abra o `.env` e troque a `SECRET_KEY`. Para gerar uma chave:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Depois crie o banco e o usuario local:

```bash
python -m scripts.seed
```

Suba a API:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Links locais:

- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health

Usuario criado pelo seed:

```text
usuario: analista
senha: Troque@Esta#Senha123
```

## Testando por curl

Health:

```bash
curl http://127.0.0.1:8000/health
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -d "username=analista&password=Troque@Esta#Senha123"
```

Use o `access_token` retornado no `/predict`:

```bash
TOKEN="cole_o_token_aqui"

curl -X POST http://127.0.0.1:8000/predict \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Meu cartão foi bloqueado, como desbloqueio?","channel":"chat"}'
```

Exemplo de retorno:

```json
{
  "intent": "cartao_bloqueado",
  "confidence": 0.82,
  "risk_level": "low",
  "model_version": "regras-v1",
  "detail": "Mensagem sobre bloqueio ou desbloqueio de cartão."
}
```

Sem token, o `/predict` retorna `401`.

## Dataset e EDA

O dataset principal e o BANKING77. Ele tem mensagens de atendimento bancario e
77 categorias de intencao.

Arquivos:

- `data/raw/banking77/`
- `data/processed/banking77/`
- `notebooks/banking77/01_eda_banking77.ipynb`
- `scripts/eda_banking77.py`
- `docs/dataset_banking77.md`
- `reports/figures/`

Para refazer a limpeza e os graficos:

```bash
python -m scripts.eda_banking77
```

Tambem deixei no repositorio um notebook de seguranca para apoiar as proximas
etapas:

- `notebooks/security/01_dataset_understanding.ipynb`
- `docs/dataset_security.md`

## Seguranca

O DFD fica em:

- `docs/dfd.md`
- `docs/dfd.png`

A analise CIA fica em:

- `docs/cia.md`

Alguns cuidados que ja estao no codigo:

- senha salva com bcrypt
- token JWT com validade curta
- `.env` fora do git
- `/predict` exige `Authorization: Bearer`
- texto completo da mensagem nao e salvo no banco, so o hash
- erro de validacao nao devolve a mensagem enviada

## Testes

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Estrutura

```text
app/
  api/
  core/
  db/
  models/
  schemas/
  services/
data/
  raw/
  processed/
docs/
notebooks/
reports/
scripts/
tests/
```
