# Auditoria final de segurança — Fintech Guard — TP3

**Responsável:** Integrante B — API e segurança.
**Entrega:** auditoria final da API do TP3, executada em 23/10/2026. Cobre os
testes automatizados de segurança, o pipeline de CI, o re-scan do OWASP ZAP e a
preparação da API como alvo do pentest do TP4/TP5. A regressão linear, a
pergunta de classificação e o planejamento do T2 pertencem às demais entregas
do TP3.

**Leitura:** sete seções — findings do ZAP, finding da auditoria manual,
checklist de segurança, testes, CI/CD, prontidão para o pentest e escopo. As
evidências citadas ficam em `reports/security/tp3/` e
`reports/security/zap-tp3/`.

## 1. Findings do OWASP ZAP

O re-scan foi executado sobre o código final com **OWASP ZAP 2.17.0**, modo
**safe** e 61 regras passivas, usando o mesmo script do TP2
([scripts/zap_passive.py](../scripts/zap_passive.py)). Foram observadas 29
requisições, duas a mais que no TP2: canal fora da allowlist e ID acima do
limite do SQLite, ambos com **422**. Não houve active scan nem spider.

| Severidade | TP2, versão original | TP2, versão corrigida | TP3, versão final |
| --- | ---: | ---: | ---: |
| High | 0 | 0 | **0** |
| Medium | 7 | 0 | **0** |
| Low | 2 | 0 | **0** |
| Informational | 6 | 5 | 5 |

**Não há finding Medium ou High pendente.** Os dois findings Medium do TP2,
10038 (CSP ausente) e 90003 (SRI ausente), foram corrigidos naquela entrega e
não voltaram a aparecer. A análise completa de cada um, com detecção, risco e
correção, está em [zap-findings.md](zap-findings.md). No TP3, a verificação foi
repetida de duas formas: pelos testes que conferem CSP com nonce em respostas
200, 401, 404, 429 e 500 e os atributos SRI do Swagger, e pela ausência das
regras 10038, 90003 e 10017 no re-scan.

Os cinco alertas informativos são os mesmos do TP2 e continuam aceitos: 10111
e 10112 identificam o login e a emissão do JWT, funções esperadas da rota
`/auth/token`; 10109 identifica a interface Swagger como aplicação moderna.
Nenhum deles aponta vulnerabilidade.

Relatórios: [HTML](../reports/security/zap-tp3/report.html),
[JSON](../reports/security/zap-tp3/report.json),
[alertas individuais](../reports/security/zap-tp3/alerts.json),
[execução](../reports/security/zap-tp3/execution.json) e
[SHA-256](../reports/security/zap-tp3/sha256.json).

## 2. Finding da auditoria manual

Um scan passivo só analisa o tráfego que recebe; ele não procura limites de
entrada. Por isso, a auditoria também enviou valores de borda às rotas
autenticadas. Um desses testes encontrou uma falha que o ZAP não acusou.

### AUD-01 — Erro 500 com ID acima do limite do SQLite

**Severidade:** Medium, por avaliação própria. **Status: corrigido.**

**Detecção:** `GET /predictions/9223372036854775808` com um token válido
respondia **500**. O log registrava `OverflowError: Python int too large to
convert to SQLite INTEGER`, com o stack trace completo. A validação exigia
apenas `prediction_id > 0`, e o maior inteiro do SQLite é 2⁶³−1.

**Por que é um problema:** qualquer usuário autenticado consegue gerar erros
500 quando quiser. Cada chamada grava um traceback no log, o que facilita
encher o disco e esconder outras ocorrências. A resposta em si é genérica, mas
um 500 reproduzível indica a quem faz fuzzing que a entrada chega ao banco sem
validação de intervalo. É exatamente o tipo de comportamento que a equipe
adversária vai procurar.

**Correção:** o parâmetro passou a ser `Path(gt=0, le=2**63 - 1)` em
[app/api/routes/predict.py](../app/api/routes/predict.py). O valor é recusado
na validação, com **422**, antes de chegar ao SQLite.

**Validação:** `test_id_invalido_ou_fora_do_intervalo_retorna_422_e_nao_500`
cobre oito casos (0, −1, texto, decimal, notação científica, SQL na URL, 2⁶³ e
2⁷⁰). Removendo o limite, os casos 2⁶³ e 2⁷⁰ voltam a falhar. No re-scan, a
mesma requisição respondeu 422 e o log da API terminou sem erros.

Na mesma revisão, o campo `channel` de `POST /predict` deixou de ser texto livre
de até 32 caracteres. Agora aceita apenas `chat`, `whatsapp`, `email` e
`telefone`, os mesmos valores da interface. O campo não era usado pelo
classificador; aceitar qualquer texto só ampliava a superfície de entrada.

## 3. Checklist de segurança

O status **resolvido** indica controle implementado e verificado por teste,
scan ou configuração do repositório. **Aceito** indica um limite conhecido, com
justificativa.

| # | Controle | Status | Verificação |
| --- | --- | --- | --- |
| 1 | JWT com algoritmo fixo e claims `exp`, `iat`, `sub` e `iss` obrigatórias | Resolvido | Tokens adulterados, expirados, com `alg: none`, chave errada ou sem `iss` recebem 401. |
| 2 | Usuário inativo ou removido perde o acesso antes de o token expirar | Resolvido | O usuário é consultado no banco a cada requisição; teste com conta desativada. |
| 3 | Login não revela se o usuário existe | Resolvido | Mesma mensagem para usuário inexistente e senha errada; bcrypt com hash fictício. |
| 4 | BOLA: ID e proprietário na mesma consulta, inclusive para `admin` | Resolvido | Testes nos dois sentidos e varredura sequencial de IDs. |
| 5 | Identidade obtida só do token | Resolvido | Query string e headers forjados não mudam o usuário. |
| 6 | Bodies rejeitam campos não previstos | Resolvido | `extra="forbid"` no login e no predict; o OpenAPI publica `additionalProperties: false`. |
| 7 | Limites de entrada em todos os campos | Resolvido | Mensagem de 1 a 1000 caracteres, canal em allowlist, ID até 2⁶³−1, usuário até 64 caracteres, senha até 72 bytes. |
| 8 | Erros sem dados do cliente nem detalhes internos | Resolvido | O 422 indica o campo, não o valor; o 500 é genérico e mantém os headers. |
| 9 | Injeção | Resolvido | Consultas pelo ORM; a mensagem é guardada como hash e nunca volta na resposta. |
| 10 | Rate limiting do login | Resolvido | 5 tentativas por IP em 300 s; a sexta recebe 429 com `Retry-After`; barra final e troca de usuário não contornam o limite. |
| 11 | Headers de segurança | Resolvido | CSP com nonce, HSTS, X-Frame-Options, nosniff, Referrer-Policy e `no-store` em todas as respostas. |
| 12 | CORS por allowlist explícita | Resolvido | Origem não listada não recebe `Access-Control-Allow-Origin`; `*` é recusado no startup. |
| 13 | Swagger com versão fixa e SRI; documentação desligada em produção | Resolvido | Re-scan sem 90003 e 10017. |
| 14 | Segredos fora do código | Resolvido | Configuração via ambiente; a `SECRET_KEY` de exemplo impede o startup. |
| 15 | Testes de segurança no CI | Resolvido | `security-tests.yml` a cada push e pull request. |
| 16 | Merge bloqueado quando o CI falha | Resolvido | Ruleset `proteger-main` exige pull request e o check `security-tests` (seção 5). |
| 17 | HSTS efetivo | Aceito | O header é enviado, mas só tem efeito sob HTTPS, que cabe ao proxy da implantação. |
| 18 | Contador de rate limiting em memória | Aceito | Vale para um worker; várias réplicas exigiriam um contador compartilhado. |
| 19 | Rate limiting apenas no login | Aceito | As demais rotas exigem JWT; proteção contra volume fica no gateway. |
| 20 | Swagger carregado de CDN | Aceito | Só em desenvolvimento, com versão fixa, SRI e nonce. |

## 4. Testes de segurança

A suíte integrada tem **95 testes**, todos aprovados
([saída](../reports/security/tp3/pytest.txt),
[JUnit XML](../reports/security/tp3/pytest.xml)). Inclui os 15 testes da
entrega de Dados do TP3 (regressão e verificação de evidências). Desses, 62 são de segurança:
25 em [test_security.py](../tests/test_security.py), do TP2, e 37 em
[test_security_tp3.py](../tests/test_security_tp3.py), escritos nesta
entrega. Os cinco casos exigidos pelo enunciado estão marcados no nome do teste:

| Caso | Requisição | Esperado | Teste |
| --- | --- | --- | --- |
| 1. Sem token | `/auth/me`, `/predict` e `/predictions/1` sem `Authorization` | 401 | `test_obrigatorio_1_rotas_protegidas_sem_token_retornam_401` |
| 2. Token inválido | JWT com `sub` trocado mantendo a assinatura; JWT expirado | 401 | `test_obrigatorio_2_token_adulterado_ou_expirado_retorna_401` |
| 3. BOLA | Analista lê predição do supervisor e vice-versa | 404 | `test_obrigatorio_3_bola_isolamento_nos_dois_sentidos` |
| 4. Campo extra | `POST /predict` com `"admin": true` | 422 | `test_obrigatorio_4_campo_extra_no_body_retorna_422` |
| 5. Rate limiting | Seis logins seguidos do mesmo IP | 429 | `test_obrigatorio_5_rate_limit_bloqueia_forca_bruta_no_login` |

Os demais testes exploram variações que um pentest tentaria em seguida: JWT
com `alg: none`, com chave errada ou sem emissor; varredura sequencial de IDs;
tipos errados, JSON malformado e payloads de SQL injection, XSS, SSTI e path
traversal; rate limiting por IP, sem efeito sobre outros clientes e sem
contorno pela barra final.

Um teste que passa não prova, sozinho, que detecta a falha. Por isso cada
controle foi removido temporariamente do código e a suíte foi executada de
novo. Em todos os casos, pelo menos um teste falhou:

| Controle removido | Testes que falharam |
| --- | ---: |
| Limite superior do ID | 2 |
| Filtro de proprietário (BOLA) | 2 |
| `extra="forbid"` | 1 |
| Rate limiting | 3 |
| Normalização da barra final no rate limiting | 1 |
| Verificação de usuário ativo | 1 |

## 5. CI/CD

O workflow [security-tests.yml](../.github/workflows/security-tests.yml)
executa `pytest tests/ -v` com Python 3.12 a cada push e pull request, e também
sob demanda. O relatório JUnit fica disponível como artefato da execução. Se
algum teste falhar, o job `security-tests` termina com falha. O workflow tem
apenas permissão de leitura do repositório e não usa segredos: o `conftest.py`
cria a chave e o banco temporário dos testes.

Um workflow com falha, sozinho, **não impede o merge**. Por isso a branch `main`
é protegida pelo ruleset `proteger-main`, ativo desde 23/10/2026, com a lista de
bypass vazia: a regra vale também para o dono do repositório. Ele aplica quatro
regras à branch padrão:

| Regra | Efeito |
| --- | --- |
| Require a pull request before merging | Nenhum commit entra na `main` sem pull request. Zero aprovações, porque a dupla tem dois integrantes e cada um precisa conseguir integrar a própria parte. |
| Require status checks to pass | O merge só é liberado com o check `security-tests` (GitHub Actions) aprovado. |
| Block force pushes | O histórico da `main` não pode ser reescrito. |
| Restrict deletions | A `main` não pode ser apagada. |

A configuração lida pela API pública do GitHub está em
[ruleset-main.json](../reports/security/tp3/ruleset-main.json). O primeiro uso
foi o próprio PR desta entrega (#4): o merge só foi liberado depois que os dois
runs do `security-tests`, de push e de pull request, terminaram com sucesso.
O run na `main` após o merge, no commit `653e851`, também passou. Até o pentest
do TP4/TP5, qualquer mudança na API passa pelo mesmo caminho.

Exigir zero aprovações tem um limite: o check impede regressões dos controles
testados, mas não substitui a revisão humana. Se a dupla quiser essa garantia,
basta subir *Required approvals* para 1.

## 6. Prontidão para o pentest

A API foi iniciada como será servida no TP4/TP5: uvicorn com um worker e banco
novo criado pelo seed. Executar o seed duas vezes não duplica contas nem
predições. As contas são sintéticas e têm papéis diferentes, para que o BOLA
possa ser testado nos dois sentidos:

| Usuário | Papel | Predições |
| --- | --- | --- |
| `analista` | analyst | 1 e 2 |
| `supervisor` | admin | 3 e 4 |

| Critério | Resultado |
| --- | --- |
| A API inicia e responde às rotas | `/health` respondeu `status: ok` e `database: up`; nenhum erro no log. |
| `/docs` acessível e documentado | 200. As cinco operações têm descrição, exemplos, respostas de erro e botão *Authorize* ([captura](../reports/security/tp3/docs-swagger.png)). |
| `/openapi.json` disponível | 200, OpenAPI 3.1. |
| Autenticação | As duas contas obtêm JWT; `/auth/me` devolve o papel correto. |
| Autorização | `analista` lê 1 e 2 e recebe 404 em 3 e 4; `supervisor`, o inverso. |
| Contas e dados de teste | Criados por `python -m scripts.seed`. |
| Testes automatizados | 95 de 95 aprovados, 62 deles de segurança. |
| CI | `security-tests` roda a cada push e pull request e é obrigatório para o merge na `main`. |
| Findings Medium/High | Nenhum no re-scan; AUD-01 corrigido. |
| Escopo, equipe adversária e URL | Pendente (seção 7). |

A captura do Swagger também confirma um ponto levantado em aula: a CSP
restritiva não impediu a documentação de funcionar. O Chromium renderizou as
operações sem bloqueios de política.

Para subir o alvo:

```bash
pip install -r requirements.txt
cp .env.example .env    # trocar SECRET_KEY e as duas senhas
python -m scripts.seed
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1 --no-proxy-headers --no-server-header
```

`ENVIRONMENT` deve continuar como `development` para expor `/docs` e
`/openapi.json`. O worker único é necessário porque o contador do rate limiting
fica em memória. Atrás de proxy, `--no-proxy-headers` deve ser trocado por
`--forwarded-allow-ips` com o IP do proxy; `X-Forwarded-For` enviado pelo
cliente não pode ser aceito.

## 7. Escopo do pentest

| Dimensão | Definição |
| --- | --- |
| Alvo | **A preencher:** URL ou IP e porta do ambiente de teste, nunca de produção. |
| Responsáveis | Equipe proprietária: **a preencher**. Equipe adversária: **a preencher**. |
| Autorização | Confirmação por escrito da equipe proprietária, com data e janela de teste: **a preencher**. |
| Endpoints liberados | `GET /`, `/health`, `/docs`, `/openapi.json`, `POST /auth/token`, `GET /auth/me`, `POST /predict` e `GET /predictions/{id}`. |
| Fora do escopo | Sistema operacional, rede, outros serviços da máquina, o repositório GitHub e engenharia social. |
| Credenciais | `analista` e `supervisor`, com as senhas do `.env` do alvo entregues por canal privado. |
| Dados | Somente os dados sintéticos do seed. |
| Técnicas permitidas | Autenticação e JWT, BOLA/IDOR, validação de entrada, injeção, headers e CORS, rate limiting do login e scan ativo do ZAP restrito ao alvo. |
| Não permitido | Negação de serviço, carga volumétrica, força bruta além do necessário para demonstrar o 429 e qualquer ação fora do alvo. |
| Segurança operacional | Até 10 requisições por segundo. A equipe proprietária pode interromper o teste a qualquer momento e recriar o banco com o seed. |
| Evidências | Requisição e resposta HTTP de cada finding, horário, severidade e passos para reproduzir; logs do uvicorn do lado proprietário. |

## Limites da evidência

O re-scan é passivo e cobre o tráfego exercitado pelo script. Ele não
demonstra ausência de falhas de lógica, nem avalia TLS, o proxy da implantação
ou as dependências em profundidade. Os testes automatizados cobrem os
controles listados, mas não substituem o pentest: a equipe adversária pode
explorar caminhos que esta auditoria não previu. A auditoria foi executada em
HTTP local; HSTS e TLS só podem ser verificados no ambiente publicado.
