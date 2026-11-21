#!/usr/bin/env bash
# Executa a conversa REAL de 3 turnos do agente contra a API viva (/classify).
#
# Pré-requisitos:
#   1. API rodando localmente:  .venv/dados/bin/python -m uvicorn app.main:app --port 8000
#   2. Banco semeado:           .venv/dados/bin/python -m scripts.seed
#   3. Venv do agente:          .venv/agent  (uv pip install -r requirements-tp4-agent.txt)
#   4. Variáveis de ambiente OpenAI exportadas ANTES de chamar este script:
#        export OPENAI_API_KEY="sk-..."      # sua chave (NÃO vai para o repo)
#        export OPENAI_MODEL="gpt-4o-mini"   # ou outro modelo com acesso
#
# O script emite um JWT fresco da conta sintética, exporta FINTECH_API_TOKEN e
# grava a transcrição em reports/TP4/agente_transcricao.json após os 3 turnos.
set -euo pipefail
cd "$(dirname "$0")/.."

API="${FINTECH_API_BASE_URL:-http://127.0.0.1:8000}"
USER_NAME="${SEED_USERNAME:-analista}"
# senha: do ambiente, senão lê do .env local
PASS="${SEED_PASSWORD:-$(grep -E '^SEED_PASSWORD=' .env 2>/dev/null | cut -d= -f2-)}"

: "${OPENAI_API_KEY:?Defina OPENAI_API_KEY antes de rodar}"
: "${OPENAI_MODEL:?Defina OPENAI_MODEL antes de rodar}"

echo "Emitindo JWT da conta '$USER_NAME' em $API ..."
TOKEN=$(curl -s -X POST "$API/auth/token" -d "username=$USER_NAME&password=$PASS" \
  | .venv/dados/bin/python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
[ -n "$TOKEN" ] || { echo "Falha ao obter token (API no ar? senha correta?)"; exit 1; }

export FINTECH_API_TOKEN="$TOKEN"
export FINTECH_API_BASE_URL="$API"

echo "Rodando os 3 turnos reais (OpenAI + /classify) ..."
.venv/agent/bin/python -m fintech_agent.demo --output reports/TP4/agente_transcricao.json
echo "Transcrição em reports/TP4/agente_transcricao.json"
