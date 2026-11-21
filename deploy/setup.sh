#!/usr/bin/env bash
# Prepara o ambiente da API no VPS (CloudPanel). Idempotente.
# Rode como o USUÁRIO DO SITE, dentro da raiz do projeto:
#   cd /home/<usuario-do-site>/htdocs/<seu-dominio> && bash deploy/setup.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# 1. uv (gerenciador de ambiente/Python) — instala se faltar
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi
export PATH="$HOME/.local/bin:$PATH"

# 2. venv com Python 3.13 (o stack fixado não compila em 3.14)
uv venv --python 3.13 .venv/dados

# 3. dependências de PRODUÇÃO da API (enxutas: inclui scikit-learn, scipy, numpy,
#    pandas, joblib — sem jupyter/seaborn/matplotlib/pytest)
uv pip install --python .venv/dados/bin/python -r requirements-prod.txt

# 4. .env
if [ ! -f .env ]; then
  cp deploy/.env.production.example .env
  echo ">> Criei .env a partir do exemplo. EDITE-O (SECRET_KEY, senhas, domínio) antes de seguir."
  echo ">> Gere o SECRET_KEY:  .venv/dados/bin/python -c \"import secrets; print(secrets.token_urlsafe(64))\""
  exit 1
fi

# 5. verifica que os modelos carregam (hash/versões) e semeia o banco
.venv/dados/bin/python -c "from ml.classification_service import ClassificationService; ClassificationService(); print('modelos OK')"
.venv/dados/bin/python -m scripts.seed

echo ">> Pronto. Agora instale o serviço systemd (ver deploy/README-cloudpanel.md)."
