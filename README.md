# Fintech Guard

O Fintech Guard é uma API para classificar mensagens de atendimento bancário e
sinalizar possíveis fraudes ou tentativas de engenharia social. A API usa JWT,
guarda as predições com SQLModel e verifica se o usuário pode consultar cada
registro. Por enquanto, o classificador usa regras simples; ainda não foi
integrado um modelo treinado.

O repositório reúne a API com os controles OWASP auditados pelo OWASP ZAP e a
análise exploratória dos dados, organizada por entrega (TP1 e TP2). Veja
[Dados e EDA](#dados-e-eda).

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

A suíte tem 43 testes: API, controles de segurança (acesso sem token, recurso
de outro usuário, campo extra no body, headers, CORS e rate limiting) e os
atributos usados na EDA. Na última execução registrada, todos passaram. A saída
arquivada em [reports/security/pytest.txt](reports/security/pytest.txt) é da
execução que acompanhou o scan, com os 37 testes de API existentes na época. O scan passivo final do
OWASP ZAP não encontrou alertas High, Medium ou Low; registrou cinco alertas
informativos. Os relatórios e a análise dos findings estão aqui:

- [Relatório ZAP em HTML](reports/security/zap-final/report.html)
- [Relatório ZAP em JSON](reports/security/zap-final/report.json)
- [Análise dos findings](docs/zap-findings.md)
- [Resumo da execução e cobertura](reports/security/zap-final/execution.json)

## Dados e EDA

O projeto usa dois conjuntos de dados, sem misturar suas classes:

| Dataset | Papel | Documentação |
| --- | --- | --- |
| Multiclass NLP Dataset for Phishing and Social Engineering Threat Detection (Zenodo) | Principal para o desafio de identificar fraude e engenharia social. 603 mensagens em inglês e seis classes após a limpeza. | [docs/dataset_security.md](docs/dataset_security.md) |
| BANKING77 | Complementar: intenções de atendimento bancário, em inglês, com 77 categorias. As categorias não são rótulos de fraude. | [docs/dataset_banking77.md](docs/dataset_banking77.md) |

Os notebooks ficam separados por entrega e são versionados com as saídas da
execução:

| Entrega | Notebook | Conteúdo |
| --- | --- | --- |
| TP1 | [BANKING77](notebooks/TP1/banking77/01_eda_banking77.ipynb) | Shape, tipos, ausentes, `describe(include="all")`, limpeza e três visualizações. |
| TP1 | [Segurança](notebooks/TP1/security/01_dataset_understanding.ipynb) | Reconstrução do arquivo original, qualidade e limpeza inicial. |
| TP2 | [Validação e EDA estatística](notebooks/TP2/security/01_validacao_e_eda_estatistica.ipynb) | Auditoria dos dados, sete atributos textuais, heatmaps de correlação (Pearson e Spearman), scatter plots, boxplots e teste de Mann-Whitney com p-valor interpretado. |

O relatório de EDA do TP2 (problema, dados, análise, insights principais,
limitações e próximos passos) está em
[Markdown](reports/TP2/relatorio_eda.md) e [PDF](reports/TP2/relatorio_eda.pdf).
As figuras e evidências ficam em `reports/TP1/` e `reports/TP2/`.

Principais resultados do TP2:

- A classe benigna tem 171 mensagens e Pretexting, a menor, 65. A avaliação do
  futuro modelo deve ser feita por classe.
- Phishing e mensagens benignas têm medianas de comprimento próximas (111 e 108
  caracteres). O Mann-Whitney deu p = 0,19, portanto não rejeitamos H₀. Phishing
  tem dispersão maior e concentra as mensagens mais longas (até 3.693 caracteres).
- Caracteres e palavras são quase redundantes (Spearman 0,96).
- Phishing e Pretexting tinham rótulos conflitantes para textos iguais; esses
  casos foram removidos e indicam classes difíceis de separar no TP3.

Para executar os notebooks novamente, com as dependências de desenvolvimento
instaladas:

```bash
python -m scripts.execute_eda_notebook                 # TP1 — BANKING77
python -m scripts.execute_security_notebook --tp TP1   # TP1 — segurança
python -m scripts.execute_security_notebook            # TP2 — segurança
```

O DFD e a análise CIA estão em [docs/dfd.md](docs/dfd.md) e
[docs/cia.md](docs/cia.md).
