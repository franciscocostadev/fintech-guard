# Fintech Guard

O Fintech Guard é uma API para classificar mensagens de atendimento bancário e
sinalizar possíveis fraudes ou tentativas de engenharia social. A API usa JWT,
guarda as predições com SQLModel e verifica se o usuário pode consultar cada
registro. Por enquanto, o classificador usa regras simples; ainda não foi
integrado um modelo treinado.

A API e os controles de segurança já estão implementados. A EDA do BANKING77
continua inicial; os itens pendentes estão descritos na seção [Dados e EDA](#dados-e-eda).

## Como executar

Requer Python 3.12 ou mais recente.

```bash
git clone https://github.com/franciscocostadev/fintech-guard.git
cd fintech-guard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
```

Gere uma chave para `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Edite `.env`, troque a chave de exemplo e confira as origens em `CORS_ORIGINS`.
Depois, crie as tabelas e o usuário local:

```bash
python -m scripts.seed
```

Inicie a API com um worker:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --no-proxy-headers --no-server-header
```

Em desenvolvimento, a documentação interativa fica em
<http://127.0.0.1:8000/docs>. Em produção, a documentação e o OpenAPI ficam
desativados. As credenciais de `.env.example` são apenas para desenvolvimento;
troque-as antes de criar o usuário.

## Rotas

| Rota | Acesso | Uso |
| --- | --- | --- |
| `GET /health` | Público | Verificar a API e o banco. |
| `POST /auth/token` | Usuário e senha | Obter um JWT. |
| `GET /auth/me` | JWT | Consultar o usuário autenticado. |
| `POST /predict` | JWT | Classificar e registrar uma mensagem. A resposta traz o ID e o header `Location`. |
| `GET /predictions/{id}` | JWT | Consultar uma predição própria. |

Com os valores padrão de `.env.example`, faça login em um banco recém-criado:

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  --data-urlencode 'username=analista' \
  --data-urlencode 'password=Troque@Esta#Senha123'
```

Se alterou `SEED_USERNAME` ou `SEED_PASSWORD` no `.env`, use esses valores.
Passe o token recebido no header `Authorization` das outras rotas. Por exemplo:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H 'Authorization: Bearer <access_token>' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Meu cartão foi bloqueado, como desbloqueio?","channel":"chat"}'
```

A resposta de `/predict` inclui o ID da predição. Consulte-o com
`GET /predictions/<id>` usando o mesmo token; outro usuário recebe `404`.

## Segurança

Os bodies de entrada rejeitam campos que não fazem parte do modelo. As consultas
e os modelos persistidos usam SQLModel; a consulta por ID também verifica o
proprietário no banco. A API envia HSTS, X-Frame-Options,
X-Content-Type-Options e Content-Security-Policy. HSTS só funciona sobre HTTPS,
portanto a implantação deve configurar TLS e redirecionamento no proxy.

CORS permite somente as origens configuradas em `CORS_ORIGINS`. O login aceita,
por padrão, cinco tentativas por endereço IP em 300 segundos; depois responde
`429` com `Retry-After`. O contador fica em memória e requer um worker. Para usar
vários processos ou réplicas, é preciso migrá-lo para um contador compartilhado.
Os detalhes e a justificativa estão em
[docs/security-controls.md](docs/security-controls.md).

As predições guardam o hash da mensagem, não o texto enviado.

## Testes e ZAP

Para executar os testes:

```bash
pytest tests/
```

Na última execução registrada, os 37 testes passaram. O scan passivo final do
OWASP ZAP não encontrou alertas High, Medium ou Low; registrou cinco alertas
informativos. Os relatórios e a análise dos findings estão aqui:

- [Relatório ZAP em HTML](reports/security/zap-final/report.html)
- [Relatório ZAP em JSON](reports/security/zap-final/report.json)
- [Análise dos findings](docs/zap-findings.md)
- [Resumo da execução e cobertura](reports/security/zap-final/execution.json)

## Dados e EDA

O BANKING77 é o conjunto principal para as mensagens de atendimento bancário: as
mensagens são em inglês e estão divididas em 77 categorias de intenção. A fonte,
os arquivos e a limpeza estão descritos em [docs/dataset_banking77.md](docs/dataset_banking77.md).

Para repetir a limpeza e a EDA inicial:

```bash
python -m scripts.eda_banking77
```

O notebook fica em
[notebooks/banking77/01_eda_banking77.ipynb](notebooks/banking77/01_eda_banking77.ipynb).
Ele já verifica a qualidade dos dados e mostra a distribuição das categorias e
o tamanho das mensagens. Para completar a EDA desta entrega, ainda faltam o
heatmap de correlação, scatter plots e um teste de hipótese com p-valor
interpretado. Também é preciso salvar as saídas do notebook e entregar um
relatório com problema, dados, análise, insights, limitações e próximos passos.

Há ainda uma EDA de outro conjunto, voltada a phishing e engenharia social, em
[notebooks/security/01_dataset_understanding.ipynb](notebooks/security/01_dataset_understanding.ipynb),
com notas em [docs/dataset_security.md](docs/dataset_security.md). Ela não
substitui o trabalho que falta no BANKING77. O DFD e a análise CIA estão em
[docs/dfd.md](docs/dfd.md) e [docs/cia.md](docs/cia.md).

## Uso de IA

O ChatGPT, da OpenAI, foi usado como apoio ao trabalho nos controles de segurança
da API, nos testes e na documentação do scan e do README. A revisão não substitui
a conferência dos resultados pelos integrantes. Referência: OpenAI. (2026).
*ChatGPT*. <https://chatgpt.com/>.
