# Fintech Guard

O Fintech Guard é uma API para classificar mensagens de atendimento bancário e
sinalizar possíveis fraudes ou tentativas de engenharia social. A API usa JWT,
guarda as predições com SQLModel e verifica se o usuário pode consultar cada
registro. Por enquanto, o classificador usa regras simples; ainda não foi
integrado um modelo treinado.

O repositório reúne a API com os controles OWASP auditados pelo OWASP ZAP e a
análise exploratória dos dados, organizada por entrega (TP1, TP2, TP3 e TP4). Veja
[Dados e EDA](#dados-e-eda).

## TP4: Dados e IA

O TP4 retoma as duas funções da proposta original: **identificar a intenção de
atendimento bancário com BANKING77** e **sinalizar conteúdo de ameaça com o dataset
de segurança**. Os modelos têm classes, probabilidades, versões e avaliações
separadas; um cliente legítimo pode estar relatando um golpe.

O [índice TP4](reports/TP4/README.md) reúne o
[notebook BANKING77 executado](notebooks/TP4/banking77/01_classificacao_intencoes.ipynb),
o [relatório das 77 intenções](reports/TP4/classificacao_banking77.md), os
[metadados do modelo bancário](models/TP4/banking77/metadata.json) e a
[conferência das 12 rubricas](reports/TP4/rubricas_TP4.md). O componente de segurança
permanece ativo, com [notebook próprio](notebooks/TP4/security/01_classificacao.ipynb),
[modelo próprio](models/TP4/security/metadata.json) e
[resultados separados](reports/TP4/classificacao.md).

O [serviço de classificação](ml/classification_service.py) carrega os dois modelos
e compõe seus resultados para o agente. **A integração de `/classify` com JWT e
carregamento na inicialização da API permanece pendente**, assim como a conversa
real do agente com três turnos, que exige chave e modelo OpenAI configurados.
O [contrato para integração](reports/TP4/contrato_classify.md), o
[guia do agente](reports/TP4/agente.md) e o
[alinhamento para Francisco](reports/TP4/alinhamento_francisco.md) especificam os
próximos passos. Testes offline com provedor/API simulados não são evidência de
conversa real. O pentest é do Integrante B. Ambos os datasets estão em inglês;
o desempenho em português ainda precisa de validação própria.

## TP3: evidências para avaliação

Revisão disponível no [PR #6](https://github.com/franciscocostadev/fintech-guard/pull/6). A [execução do PR](https://github.com/franciscocostadev/fintech-guard/actions/runs/43149334149)
aprovou 95 testes no commit `8bdec52`. Confira o estado de integração e os checks da revisão mais recente na página do PR.

O [índice específico do TP3](reports/TP3/README.md) organiza os requisitos e seus arquivos.
A [conferência das 12 rubricas](reports/TP3/rubricas_TP3.md) identifica os oito itens apontados na avaliação e suas evidências.
A [revisão do feedback de 11/11/2026](reports/TP3/revisao_feedback.md) diferencia a entrega
já integrada, as melhorias desta revisão e as pendências antes do TP4.

- [Notebook executado: regressão simples e múltipla, métricas e diagnósticos](notebooks/TP3/security/01_regressao_e_transicao.ipynb).
- Pergunta de classificação: [Markdown](reports/TP3/pergunta_classificacao.md) e [PDF](reports/TP3/pergunta_classificacao.pdf).
- [Planejamento T2: TF-IDF, regressão logística e comparação com SVM](reports/TP3/planejamento_T2.md).
- [95 testes aprovados na revisão local](reports/TP3/revisao_20261111/pytest.txt) e [JUnit](reports/TP3/revisao_20261111/pytest.xml).
- [OpenAPI obtido por HTTP](reports/TP3/revisao_20261111/openapi.json) e [verificação dos cinco contratos](reports/TP3/revisao_20261111/openapi-validacao.json).
- [Auditoria de segurança do integrante B](docs/auditoria-final-tp3.md).

**Pendente:** colega adversário, URL/IP autorizada e formalização do escopo/janela do pentest.
O endereço do repositório e o localhost de validação não substituem a URL da API adversária.

## Como executar

Requer Python 3.12 ou mais recente.

```bash
git clone https://github.com/franciscocostadev/fintech-guard.git
cd fintech-guard
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
```

Gere uma chave para `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Edite `.env`, troque a chave de exemplo e confira as origens em `CORS_ORIGINS`.
Depois, crie as tabelas, as duas contas de teste e as predições sintéticas:

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

O seed cria duas contas sintéticas com papéis diferentes, cada uma com duas
predições, para testar o isolamento entre usuários (BOLA):

| Usuário | Papel | Predições |
| --- | --- | --- |
| `analista` | analyst | 1 e 2 |
| `supervisor` | admin | 3 e 4 |

Com os valores padrão de `.env.example`, faça login em um banco recém-criado:

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  --data-urlencode 'username=analista' \
  --data-urlencode 'password=Troque@Esta#Senha123'
```

Se alterou `SEED_USERNAME`, `SEED_PASSWORD`, `SEED_ADMIN_USERNAME` ou
`SEED_ADMIN_PASSWORD` no `.env`, use esses valores.
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

## Testes, CI e auditoria

Para executar os testes:

```bash
python -m pytest tests/ -v
```

A suíte cobre API e controles de segurança, atributos da EDA e o experimento de
regressão do TP3. Os testes de segurança verificam autenticação (sem token, JWT
adulterado, expirado ou `alg: none`, usuário inativo), autorização BOLA nos dois
sentidos, validação de entradas, rate limiting, headers e CORS. A execução da
auditoria final está em
[reports/security/tp3/pytest.txt](reports/security/tp3/pytest.txt).
As dependências de desenvolvimento incluem scikit-learn e os recursos para
executar os notebooks. `requirements-tp3-dados.txt` é um alias desse mesmo conjunto.
Os resultados e o ambiente de cada validação de Dados estão em
[reports/TP3/resultado_validacao.md](reports/TP3/resultado_validacao.md).

O GitHub Actions executa a suíte a cada push e pull request
([security-tests.yml](.github/workflows/security-tests.yml)). A branch `main`
é protegida: só recebe mudanças por pull request, e o merge exige o check
`security-tests` aprovado. A regra está descrita na seção 5 da auditoria.

A [auditoria final do TP3](docs/auditoria-final-tp3.md) reúne o checklist de
segurança, o re-scan do OWASP ZAP (nenhum alerta High, Medium ou Low; cinco
informativos), a correção do finding manual AUD-01, a verificação de prontidão
e o escopo do pentest. Os relatórios ZAP do TP2 e o
[pytest do TP2](reports/security/pytest.txt) continuam como registro histórico
em [docs/zap-findings.md](docs/zap-findings.md).

- [Relatório ZAP final em HTML](reports/security/zap-tp3/report.html)
- [Relatório ZAP final em JSON](reports/security/zap-tp3/report.json)
- [Resumo da execução e cobertura](reports/security/zap-tp3/execution.json)

## Dados e EDA

O projeto usa dois conjuntos de dados, sem misturar suas classes:

| Dataset | Papel | Documentação |
| --- | --- | --- |
| BANKING77 | Classificador principal de intenções de atendimento no TP4, em inglês, com 77 categorias. As categorias não são rótulos de fraude. | [docs/dataset_banking77.md](docs/dataset_banking77.md) |
| Multiclass NLP Dataset for Phishing and Social Engineering Threat Detection (Zenodo) | Componente ativo de segurança. 603 mensagens em inglês e seis classes após a limpeza, agrupadas em benigno/ameaça no classificador TP4. Não determina a intenção pessoal do remetente. | [docs/dataset_security.md](docs/dataset_security.md) |

Os notebooks ficam separados por entrega e são versionados com as saídas da
execução:

| Entrega | Notebook | Conteúdo |
| --- | --- | --- |
| TP1 | [BANKING77](notebooks/TP1/banking77/01_eda_banking77.ipynb) | Shape, tipos, ausentes, `describe(include="all")`, limpeza e três visualizações. |
| TP1 | [Segurança](notebooks/TP1/security/01_dataset_understanding.ipynb) | Reconstrução do arquivo original, qualidade e limpeza inicial. |
| TP2 | [Validação e EDA estatística](notebooks/TP2/security/01_validacao_e_eda_estatistica.ipynb) | Auditoria dos dados, sete atributos textuais, heatmaps de correlação (Pearson e Spearman), scatter plots, boxplots e teste de Mann-Whitney com p-valor interpretado. |
| TP3 | [Regressão e transição](notebooks/TP3/security/01_regressao_e_transicao.ipynb) | Pré-processamento, regressão simples e múltipla, baseline, R²/RMSE, resíduos, Q-Q plot e limitações. |
| TP4 | [Intenções bancárias](notebooks/TP4/banking77/01_classificacao_intencoes.ipynb) | TF-IDF + regressão logística multiclasse, GridSearchCV, baseline, matriz de confusão, métricas por classe, ROC-AUC e serialização. |
| TP4 | [Conteúdo de segurança](notebooks/TP4/security/01_classificacao.ipynb) | Pipeline binário independente, GridSearchCV, baseline, métricas e limitações de detecção de ameaças. |

O relatório de EDA do TP2 (problema, dados, análise, insights principais,
limitações e próximos passos) está em
[Markdown](reports/TP2/relatorio_eda.md) e [PDF](reports/TP2/relatorio_eda.pdf).
As figuras e evidências ficam em `reports/TP1/`, `reports/TP2/`, `reports/TP3/` e `reports/TP4/`.

A [entrega de Dados do TP3](reports/TP3/README.md) reúne também a pergunta de
classificação em [Markdown](reports/TP3/pergunta_classificacao.md) e
[PDF](reports/TP3/pergunta_classificacao.pdf), o
[planejamento T2](reports/TP3/planejamento_T2.md) e os registros de validação.
No registro histórico do TP3, o alvo planejado foi o conteúdo de ameaça das
mensagens. O [adendo de arquitetura do TP4](reports/TP4/arquitetura_dupla.md)
explica a retomada das intenções bancárias como tarefa principal de atendimento,
mantendo a análise de segurança separada. Os dois classificadores supervisionados
estão treinados no TP4; a API ainda depende da integração descrita acima.

Principais resultados do TP2:

- A classe benigna tem 171 mensagens e Pretexting, a menor, 65. A avaliação do
  futuro modelo deve ser feita por classe.
- Phishing e mensagens benignas têm medianas de comprimento próximas (111 e 108
  caracteres). O Mann-Whitney deu p = 0,19, portanto não rejeitamos H₀. Phishing
  tem dispersão maior e concentra as mensagens mais longas (até 3.693 caracteres).
- Caracteres e palavras são quase redundantes (Spearman 0,96).
- Phishing e Pretexting tinham rótulos conflitantes para textos iguais; esses
  casos foram removidos e indicam classes difíceis de separar no futuro classificador.

Para executar os notebooks novamente, com as dependências de desenvolvimento
instaladas:

```bash
python -m scripts.execute_eda_notebook                 # TP1 — BANKING77
python -m scripts.execute_security_notebook --tp TP1   # TP1 — segurança
python -m scripts.execute_security_notebook            # TP2 — segurança
python -m scripts.execute_tp3_notebook                 # TP3 — regressão
python -m scripts.execute_tp4_notebook                 # TP4 — segurança
python -m scripts.execute_tp4_banking_notebook          # TP4 — intenções bancárias
```

Para reproduzir o TP4, instale `requirements-tp4-dados.txt`. O agente utiliza
um ambiente separado, conforme [guia do agente](reports/TP4/agente.md).

O DFD e a análise CIA estão em [docs/dfd.md](docs/dfd.md) e
[docs/cia.md](docs/cia.md).
