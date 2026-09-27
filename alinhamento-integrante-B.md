# Fintech Guard

API FastAPI para classificar mensagens de atendimento bancário e sinalizar
possíveis situações de fraude ou engenharia social. A API usa JWT, persiste
resultados com SQLModel e verifica o proprietário em consultas por ID. O
classificador atual usa regras simples; ainda não há um modelo de machine
learning treinado.

## Estado da entrega

Os controles de segurança da API, os testes e o scan passivo do OWASP ZAP estão
implementados. O notebook do BANKING77 registra uma EDA inicial; a etapa
avançada descrita abaixo continua pendente.

## Executar localmente

Requer Python 3.12 ou mais recente.

```bash
git clone https://github.com/franciscocostadev/fintech-guard.git
cd fintech-guard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Gere uma `SECRET_KEY` exclusiva antes de iniciar a API:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Edite `.env`, substitua a chave de exemplo e confira `CORS_ORIGINS`. Crie as
tabelas e o usuário local definidos nessa configuração:

```bash
python -m scripts.seed
```

Inicie um worker local:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --no-proxy-headers --no-server-header
```

Em `ENVIRONMENT=development`, a documentação interativa fica em
<http://127.0.0.1:8000/docs>. Em produção, a documentação e o OpenAPI ficam
desabilitados. O exemplo de usuário e senha em `.env.example` serve apenas para
desenvolvimento; altere-os antes de criar o usuário.

## Rotas

| Método e rota | Acesso | Descrição |
| --- | --- | --- |
| `GET /health` | Público | Estado da API e do banco. |
| `POST /auth/token` | Formulário de usuário e senha | Emite um JWT. |
| `GET /auth/me` | JWT obrigatório | Retorna o usuário do token atual. |
| `POST /predict` | JWT obrigatório | Classifica e registra uma mensagem. Retorna o ID e o header `Location`. |
| `GET /predictions/{id}` | JWT obrigatório | Retorna uma predição somente ao seu proprietário. |

Exemplo de login local:

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -d 'username=analista&password=troque-esta-senha'
```

Use o `access_token` da resposta para classificar uma mensagem:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Meu cartão foi bloqueado, como desbloqueio?","channel":"chat"}'
```

O retorno inclui `id`. Para consultar a predição salva, chame
`GET /predictions/<id>` com o mesmo token; outro usuário recebe `404`.

## Controles de segurança

- Todos os modelos de entrada da API rejeitam campos extras (`extra="forbid"`).
- Persistência e consultas usam SQLModel; a rota por ID aplica o filtro de
  proprietário na própria consulta.
- Middleware define HSTS, X-Frame-Options, X-Content-Type-Options e CSP. HSTS
  só é efetivo sob HTTPS; configure TLS e o redirecionamento no proxy de
  produção.
- CORS usa a allowlist exata definida em `CORS_ORIGINS`; não use `*`.
- `/auth/token` limita por padrão **5 tentativas por IP em 300 segundos** e
  devolve `429` com `Retry-After` ao esgotar o limite.
- O limitador em memória suporta um worker. Para várias réplicas, substitua-o
  por um contador compartilhado; os detalhes e a justificativa estão em
  [docs/security-controls.md](docs/security-controls.md).
- O texto das mensagens não é salvo no log de predições; é armazenado somente
  seu hash e o resultado da classificação.

## Testes e relatório ZAP

Execute a suite com:

```bash
pytest tests/
```

Evidências e análise do scan passivo do ZAP:

- [Relatório HTML final](reports/security/zap-final/report.html)
- [Relatório JSON final](reports/security/zap-final/report.json)
- [Findings, severidades e correções](docs/zap-findings.md)
- [Execução e cobertura do scan](reports/security/zap-final/execution.json)

O scan final registrou zero findings High, Medium ou Low; restaram alertas
informativos. O relatório documenta o escopo e as limitações da análise.

## Dados e EDA

O dataset principal da classificação bancária é o [BANKING77](docs/dataset_banking77.md),
com as mensagens em inglês distribuídas entre 77 categorias de intenção. Os
arquivos originais e processados ficam em `data/raw/banking77/` e
`data/processed/banking77/`.

Reproduza a limpeza e a EDA inicial com:

```bash
python -m scripts.eda_banking77
```

O notebook correspondente é
[notebooks/banking77/01_eda_banking77.ipynb](notebooks/banking77/01_eda_banking77.ipynb).
Ele inclui checagens de qualidade, distribuição de categorias, comprimentos de
mensagens e hipóteses qualitativas. **Ainda faltam para a EDA avançada desta
entrega:** heatmap de correlação, scatter plots, teste de hipótese com p-valor
interpretado, outputs salvos nas células do notebook e relatório de EDA do
BANKING77 com problema, dados, análise, insights, limitações e próximos passos.
Os gráficos atuais ficam em `reports/figures/`.

O repositório também contém uma análise exploratória separada de um dataset de
phishing e engenharia social em
[notebooks/security/01_dataset_understanding.ipynb](notebooks/security/01_dataset_understanding.ipynb),
documentada em [docs/dataset_security.md](docs/dataset_security.md). Ela não
substitui as análises pendentes do BANKING77.

Diagramas e contexto adicional: [DFD](docs/dfd.md) e [análise CIA](docs/cia.md).

## Uso de ferramentas de IA

O OpenAI ChatGPT foi utilizado em 26 e 27 de setembro de 2026 como apoio à
revisão do repositório, implementação e documentação dos controles de segurança
da API e dos testes. A análise e as conclusões devem ser verificadas pelos
autores antes da entrega. Referência: OpenAI. (2026). *ChatGPT*. <https://chatgpt.com/>.
