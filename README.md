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

Use Python 3.12 ou mais novo.

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

## Dataset e EDA por entrega

Os notebooks estão organizados primeiro por TP e depois por dataset. `01` indica a ordem dentro daquela entrega. Dados e scripts são compartilhados; cada notebook pode ser executado independentemente, a partir da raiz do projeto ou da sua própria pasta.

| Entrega | Notebook | Conteúdo |
|---|---|---|
| TP1 | [BANKING77](notebooks/TP1/banking77/01_eda_banking77.ipynb) | EDA inicial com as correções do professor: describe completo, três gráficos e outputs. |
| TP1 | [Segurança](notebooks/TP1/security/01_dataset_understanding.ipynb) | Entendimento, reconstrução e limpeza inicial do dataset de ameaças. |
| TP2 | [Validação e EDA estatística](notebooks/TP2/security/01_validacao_e_eda_estatistica.ipynb) | EDA concluída: auditoria, sete atributos, heatmaps, scatter, boxplots e teste de hipótese interpretado. |

No TP2, o dataset de segurança é o principal para o desafio de identificação de ameaças. BANKING77 permanece complementar para intenções de atendimento; suas classes não são rótulos de fraude.

- [Relatório de EDA do TP2 (Markdown)](reports/TP2/relatorio_eda.md)
- [Relatório de EDA do TP2 (PDF)](reports/TP2/relatorio_eda.pdf)
- [Auditoria de dados do TP2](reports/TP2/security_validation/README.md)
- [Documentação BANKING77](docs/dataset_banking77.md)
- [Documentação do dataset de segurança](docs/dataset_security.md)
- Figuras da EDA inicial: `reports/TP1/figures/`.

Com as dependências de desenvolvimento instaladas, execute na raiz:

```bash
python -m scripts.execute_eda_notebook
python -m scripts.execute_security_notebook --tp TP1
python -m scripts.execute_security_notebook
```

O primeiro comando executa o BANKING77 do TP1; o segundo, segurança do TP1; o terceiro, segurança do TP2. A execução padrão de segurança é o TP2. Para somente revalidar os dados e gerar a auditoria: `python -m scripts.validate_security_dataset`.

Os notebooks do TP1 preservam as análises daquela entrega. A evolução acontece no diretório do TP correspondente; correções posteriores de uma entrega devem ser identificadas no histórico Git. Não misture novas etapas do TP2 nos notebooks do TP1.

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
  TP1/
    banking77/
    security/
  TP2/
    security/
reports/
  TP1/figures/
  TP2/
    relatorio_eda.md
    relatorio_eda.pdf
    security_validation/
    security_features/
    hypothesis_test/
    figures/
scripts/
tests/
```

### TP2 — atributos exploratórios

O notebook do TP2 calcula sete medidas textuais, com definições e evidências em [reports/TP2/security_features](reports/TP2/security_features/README.md). A implementação reutilizável está em `scripts/security_features.py`. As medidas não são indicadores comprovados de fraude.

A análise foi validada com Python 3.13. Para o TP2, basta executar `python -m scripts.execute_security_notebook`; não é necessário reexecutar o TP1. Os arquivos históricos usados no protocolo são preservados byte a byte por `.gitattributes`. Uma alteração intencional do dataset ou da evidência histórica requer um novo protocolo, sem sobrescrever silenciosamente o original.


A branch de EDA do TP2 parte da correção `fix/tp1-eda` (PR #1), ainda pendente de integração na data da preparação. Integrar o TP1 antes de revisar o diff final do TP2 contra `main`. Esta branch não inclui mudanças na API ou auditoria ZAP.
