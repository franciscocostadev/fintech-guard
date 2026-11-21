# Deploy da Fintech Guard API no CloudPanel

A API é FastAPI/uvicorn com modelos de ML carregados no startup. No CloudPanel ela
roda como **serviço systemd** em `127.0.0.1:8000`, e o **Nginx do CloudPanel** faz
o reverse proxy + HTTPS (Let's Encrypt) para o seu domínio.

> **Segurança — código fora da pasta pública:** como o site é um *reverse proxy*, o
> Nginx encaminha tudo para `127.0.0.1:8000` e **não** serve arquivos do disco. Por
> isso o código **não fica no `htdocs`**, e sim numa pasta privada
> `/home/<usuario-do-site>/fintech-api`. Assim `.env`, o banco e os modelos nunca
> ficam sob a raiz web.

## Pré-requisitos

- Um **VPS** (Ubuntu 22.04/24.04 ou Debian 12) com **CloudPanel** instalado.
- Um **domínio** (ex.: `api.seudominio.com`) apontando (registro A) para o IP do VPS.
- Acesso SSH ao VPS e `sudo` para instalar o serviço systemd.

## Passo a passo

### 1. Criar o site no CloudPanel

No painel: **Sites → Add Site → Create a Reverse Proxy**
- **Domain Name:** `api.seudominio.com`
- **Reverse Proxy URL:** `http://127.0.0.1:8000`
Isso cria o usuário do site (ex.: `api-seudominio`). O reverse proxy aponta para
`http://127.0.0.1:8000`, então **o código não precisa ficar no `htdocs`**.

> Alternativa: tipo **Python Site** (se sua versão do CloudPanel tiver). O reverse
> proxy funciona igual e é o caminho mais simples para ASGI.

### 2. Enviar o código (pasta privada, fora do htdocs)

Por `git clone` ou `scp`, coloque o projeto em
`/home/<usuario-do-site>/fintech-api` (os arquivos `app/`, `ml/`, `models/`,
`scripts/`, `deploy/`, `requirements-tp4-dados.txt`). Faça isso como o usuário do
site e garanta o dono: `chown -R <usuario-do-site>:<usuario-do-site> /home/<usuario-do-site>/fintech-api`.

### 3. Ambiente e banco

```bash
cd /home/<usuario-do-site>/fintech-api
bash deploy/setup.sh      # instala uv, cria .venv/dados, instala deps
# na 1ª vez ele cria o .env e para: EDITE o .env (SECRET_KEY, senhas, domínio, DATABASE_URL)
.venv/dados/bin/python -c "import secrets; print(secrets.token_urlsafe(64))"   # gere o SECRET_KEY
bash deploy/setup.sh      # rode de novo: valida modelos e semeia o banco
```

No `.env`, ajuste `DATABASE_URL` para um caminho absoluto dentro da pasta do site e
`CORS_ORIGINS=https://api.seudominio.com`. Mantenha `ENVIRONMENT=production`.

### 4. Serviço systemd (mantém o uvicorn no ar)

Edite `deploy/fintech-guard.service` trocando `<USUARIO-DO-SITE>` (a unit já aponta
para a pasta privada `/home/<USUARIO-DO-SITE>/fintech-api`), e:

```bash
sudo cp deploy/fintech-guard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fintech-guard
systemctl status fintech-guard        # deve estar "active (running)"
curl -s http://127.0.0.1:8000/health  # {"status":"ok",...}
```

### 5. SSL

No CloudPanel: **site → SSL/TLS → Let's Encrypt → Create**. Depois teste:
`https://api.seudominio.com/health`.

## Verificação final

```bash
# login + /classify pela URL pública
TOKEN=$(curl -s -X POST https://api.seudominio.com/auth/token \
  -d "username=analista&password=<SEED_PASSWORD>" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s https://api.seudominio.com/classify -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" -d '{"text":"I lost my card"}'
```

## Observações

- **Em produção `/docs` e `/openapi.json` ficam desligados** (`ENVIRONMENT=production`).
  Para o agente/desenvolvimento, use a instância local, não a pública.
- **1 worker** porque os rate limiters são em memória por processo. Para escalar com
  vários workers, migrar os limitadores para um store compartilhado (ex.: Redis).
- **Atualizar o deploy:** `git pull` → `bash deploy/setup.sh` →
  `sudo systemctl restart fintech-guard`.
- **Logs:** `journalctl -u fintech-guard -f`.
- Esta é a URL que pode ser registrada como **alvo do pentest adversário** para o colega.
