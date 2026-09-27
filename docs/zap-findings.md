# Evidências OWASP ZAP — Fintech Guard

## Resultado

Scans executados em **26/09/2026**, com **OWASP ZAP 2.17.0**, Java 21 e
61 regras passivas habilitadas. Alvo exclusivo: `http://127.0.0.1:18000`.

| Severidade | Versão original (ocorrências) | Versão corrigida (ocorrências) |
| --- | ---: | ---: |
| High | 0 | 0 |
| Medium | 7 | 0 |
| Low | 2 | 0 |
| Informational | 6 | 5 |

Contagens da API ZAP em `alerts.json`; os relatórios HTML/JSON tradicionais
agrupam ocorrências equivalentes. `Medium (High)` no relatório significa risco
**Medium** e confiança **High**, não severidade High. Não houve finding de risco
High, nem risco Medium aceito na versão final.

- **Antes**, fontes do commit `60c69d8`: [HTML](../reports/security/zap-before/report.html), [JSON](../reports/security/zap-before/report.json), [alertas individuais](../reports/security/zap-before/alerts.json), [execução](../reports/security/zap-before/execution.json).
- **Depois**, código atualizado: [HTML](../reports/security/zap-final/report.html), [JSON](../reports/security/zap-final/report.json), [alertas individuais](../reports/security/zap-final/alerts.json), [execução](../reports/security/zap-final/execution.json).
- **pytest**: [saída completa, 37 passed](../reports/security/pytest.txt), [JUnit XML](../reports/security/pytest.xml).

## Findings Medium/High: detecção, problema e tratamento

### 10038 — Content Security Policy (CSP) Header Not Set

**Severidade:** Medium; confiança High. **Status: corrigido.**

**Detecção:** três respostas HTML sem `Content-Security-Policy`: `/`, `/docs` e
`/redoc`. Evidências e URLs estão no relatório anterior, `pluginid=10038`.

**Por que é um problema:** sem CSP, o navegador não restringe a execução de
scripts, o carregamento de recursos nem o enquadramento da página por uma
política explícita. Isso elimina uma defesa importante para reduzir o impacto
de injeções e XSS. CSP complementa a renderização segura dos dados.

**Correção:** `app/core/middleware.py` aplica uma política com
`default-src 'none'`, scripts/estilos locais e nonce aleatório por resposta,
`object-src 'none'`, `base-uri 'none'`, `frame-ancestors 'none'` e
`form-action 'self'`. A página inicial e o Swagger recebem o nonce correspondente.
Não há `unsafe-inline` nem `unsafe-eval`. Dados da interface são inseridos com
`textContent`. O handler 500 preserva os headers; `/redoc` agora redireciona para
`/docs`. Documentação interativa é desabilitada em produção.

**Validação:** a regra 10038 permaneceu habilitada; zero ocorrências no scan
final. Testes verificam CSP em respostas normais, erros, preflight e nonces
variáveis compatíveis com o HTML. [Referência da regra ZAP](https://www.zaproxy.org/docs/alerts/10038/).

### 90003 — Sub Resource Integrity Attribute Missing

**Severidade:** Medium; confiança High. **Status: corrigido.**

**Detecção:** quatro recursos externos sem atributo `integrity`, presentes em
`/docs` e `/redoc` (scripts e stylesheets). Evidências de tags e URLs constam no
relatório anterior, `pluginid=90003`.

**Por que é um problema:** se um CDN entregar bytes modificados, o navegador
pode executar código diferente daquele validado pela aplicação. Uma versão
flutuante também pode mudar sem revisão do repositório. SRI permite ao navegador
recusar conteúdo cujo hash não corresponde ao esperado.

**Correção:** Swagger usa `swagger-ui-dist@5.17.14`, com hashes **SHA-384**
calculados sobre os bytes de `swagger-ui-bundle.js` e `swagger-ui.css`.
`app/main.py` adiciona `integrity` e `crossorigin="anonymous"` às duas tags,
além do nonce para scripts. O antigo ReDoc/CDN foi substituído por um redirect
para a mesma documentação protegida. Ao atualizar Swagger, recalcular e revisar
os hashes junto com a versão. Os recursos só são utilizados em desenvolvimento.

**Validação:** regra 90003 habilitada, zero ocorrências no scan final, teste de
versão fixa e atributos SRI aprovado. [Referência da regra ZAP](https://www.zaproxy.org/docs/alerts/90003/).

## Demais findings

| ID | Severidade | Descrição | Status e justificativa |
| --- | --- | --- | --- |
| 10017 | Low | Inclusão de JavaScript de outro domínio em `/docs` e `/redoc` (duas ocorrências anteriores). | Mitigado: dependência externa restrita ao Swagger de desenvolvimento, com versão fixa, SRI e nonce. O scan final não emitiu esse alerta; o CDN continua sendo uma dependência explícita da documentação. |
| 10109 | Informational | Identificação de aplicação web moderna com JavaScript. | Aceito: comportamento esperado da interface de documentação, sem vulnerabilidade demonstrada. |
| 10111 | Informational | Identificação de requisições de autenticação em `/auth/token`. | Aceito: função esperada do endpoint. Credenciais sintéticas; limite de 5 tentativas/300s validado. |
| 10112 | Informational | Identificação de resposta que contém token de sessão. | Aceito: emissão intencional de JWT, com expiração e `Cache-Control: no-store`. |

## Método e cobertura

O script [scripts/zap_passive.py](../scripts/zap_passive.py) cria banco SQLite,
chave JWT aleatória, dois usuários sintéticos e uma senha aleatória em diretório temporário. Inicia a
API em loopback com um worker, sem confiança em proxy headers recebidos do
cliente, e o ZAP também em loopback com chave de API. Define e verifica modo
**safe**, habilita as regras passivas e envia tráfego funcional pelo proxy.

Foram observadas 23 requisições na versão original e 27 na versão corrigida,
incluindo:

- Página inicial, health, Swagger, redirect ReDoc, OpenAPI, favicon e 404.
- Login válido/inválido, campos extras no formulário, resposta 429.
- `/auth/me` e `/predict` com e sem token; JSON inválido e com campo extra.
- Predição própria (200), de outro usuário (404) e inexistente (404).
- Preflight CORS de origem permitida (200) e não permitida (400).

Nenhum active scan, spider ou fuzzing foi executado. O script confirma que não
há scans ativos, espera **fila passiva e tarefas em execução zerarem**, e então
exporta relatórios nativos pela API do ZAP. Os arquivos `execution.json` incluem
versão, horários UTC, cobertura/status HTTP, regras habilitadas e SHA-256 de cada
fonte da API analisado. Os arquivos `sha256.json` permitem verificar integridade
dos artefatos. Senhas, JWTs e a chave temporária do ZAP são substituídos por
`[REDACTED_EPHEMERAL_CREDENTIAL]` quando presentes; findings e severidades são
preservados. Processos e banco de scan são encerrados/removidos ao final.

## Reprodução

Requisitos: Java 17+ e dependências de `requirements-dev.txt`. Foi utilizada a
[distribuição oficial ZAP 2.17.0](https://github.com/zaproxy/zaproxy/releases/tag/v2.17.0),
extraída em `/tmp/ZAP_2.17.0`. SHA-256 verificado do arquivo
`ZAP_2.17.0_Linux.tar.gz`:

```text
efe799aaa3627db683b43f00c9c210aea0b75c00cc8f0a0f0434d12bb3ddde5a
```

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m scripts.zap_passive \
  --zap /tmp/ZAP_2.17.0/zap.sh \
  --output reports/security/zap-final
pytest tests/
```

Para reproduzir a comparação histórica, extrair `git archive 60c69d8` em um
diretório temporário e executar o mesmo script com
`--app-dir /caminho/da/copia --baseline --output reports/security/zap-before`.
O banco de trabalho e o `.env` do desenvolvedor não são alterados.

## Limites da evidência

O scan cobre o tráfego exercitado, em ambiente de desenvolvimento por HTTP
local. Não avalia certificado TLS, configuração do proxy público, caminhos não
exercitados, dependências em profundidade nem demonstra ausência de falhas de
lógica. HSTS foi verificado como header, mas seu efeito depende de **HTTPS**.
BOLA, campos extras e rate limiting são exercitados por pytest, além do tráfego
observado pelo ZAP. O contador de login em memória exige um worker; limitações,
justificativa e migração para contador compartilhado estão em
[security-controls.md](security-controls.md).

O ZAP pode registrar um erro de criação do perfil Firefox no startup. Não foi
usado navegador/AJAX spider; esse componente não participa desta análise
passiva, que concluiu com fila e tarefas zeradas.
