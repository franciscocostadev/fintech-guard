# Controles de segurança da API

## Validação, persistência e autorização

Todos os bodies recebidos pela API herdam `InputModel`, com
`ConfigDict(extra="forbid")`: `PredictRequest` (JSON) e `LoginRequest`
(formulário OAuth2). Campos desconhecidos geram **422**, sem refletir seus valores
na resposta. O formulário declara os campos OAuth2 utilizados pelo Swagger;
`scope` enviado pelo cliente não concede permissões. Senhas acima de 72 bytes
são recusadas para evitar truncamento do bcrypt. `Settings` descreve o ambiente,
não requests HTTP; seus campos extras do `.env` continuam ignorados.

`User` e `PredictionLog` são tabelas SQLModel. Leitura usa
`Session.exec(select(...).where(...))` e escrita usa `add`/`commit`, com valores
vinculados pelo ORM. O health check usa `select(1)`. Não há SQL raw na aplicação
ou no seed. Os nomes, tipos e índices existentes foram mantidos, preservando o
banco SQLite anterior.

`POST /predict` retorna o ID persistido e o header `Location`.
`GET /predictions/{prediction_id}` exige JWT válido e consulta **ID e proprietário
na mesma expressão SQLModel**. O proprietário é o `username` único obtido da
sessão autenticada; a API não permite alterar, excluir ou reutilizar usernames.
Operações administrativas externas também devem preservar essa identidade.
Recursos inexistentes e recursos alheios retornam o mesmo **404**. Nem o papel
`admin` contorna a regra. A resposta não expõe hash da mensagem nem credenciais.
`GET /auth/me` sempre usa a identidade do token, sem ID fornecido pelo cliente.

## Headers e CORS

`SecurityHeadersMiddleware` adiciona a todas as respostas HTTP:

| Header | Política |
| --- | --- |
| Strict-Transport-Security | `max-age=31536000; includeSubDomains` |
| X-Frame-Options | `DENY` |
| X-Content-Type-Options | `nosniff` |
| Content-Security-Policy | `default-src 'none'`; scripts/styles locais com nonce por resposta; `object-src 'none'`, `base-uri 'none'`, `frame-ancestors 'none'`, `form-action 'self'` |
| Cache-Control | `no-store` |
| Referrer-Policy | `no-referrer` |

O handler de erros inesperados também aplica os headers, pois o middleware de
exceções 500 do Starlette é externo aos middlewares registrados. Os testes cobrem
200, 401, 404, 429, preflight e 500. HSTS **só é obedecido em HTTPS**; o HTTP local
serve para desenvolvimento. Em produção, publicar por TLS e redirecionar HTTP
no proxy, incluindo os subdomínios abrangidos pela política.

A página inicial usa nonce em scripts e estilos, sem `unsafe-inline` ou
`unsafe-eval`. Renderização de dados usa `textContent`. O token fica em memória
da página, sem persistência no navegador e sem senha preenchida no HTML.
Swagger utiliza assets com versão fixa e SRI, com autorização de script por
nonce e stylesheet de `https://cdn.jsdelivr.net`. `/redoc` redireciona para
`/docs`. As duas interfaces e `/openapi.json` ficam indisponíveis em produção.

CORS usa `CORS_ORIGINS` como allowlist explícita, por exemplo:

```dotenv
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

A configuração recusa `*`, `null`, curingas em hosts e URLs com caminhos ou
credenciais. Métodos permitidos: GET/POST; headers: Authorization/Content-Type.
`Location` e `Retry-After` são expostos para as origens permitidas. CORS é uma
restrição de leitura imposta pelo navegador; autorização continua no servidor.

## Rate limiting de /auth/token

**Limite padrão: 5 tentativas por IP em uma janela deslizante de 300 segundos.**
A sexta tentativa retorna **429** e `Retry-After` com os segundos restantes até
haver capacidade. O middleware reserva uma tentativa antes da validação e do
bcrypt; conta sucessos, falhas e bodies inválidos. Um login válido não reinicia
o contador. A verificação e a reserva usam o mesmo lock, impedindo que chamadas
simultâneas excedam o limite. IPs inativos expiram; a memória é limitada a 10.000
IPs e, quando cheia, novos IPs são bloqueados sem descartar contadores ativos.

A escolha permite algumas correções de digitação, limita a aproximadamente uma
tentativa por minuto em ataques sustentados e protege o custo de CPU do bcrypt
(rounds=12). A janela deslizante evita o dobro de tentativas na fronteira entre
janelas fixas. O limite por IP reduz ataques que alternam usernames e não cria
bloqueio permanente de uma conta vítima. Redes com NAT compartilham a cota;
ataques distribuídos exigem proteção adicional no gateway. Valores podem ser
ajustados com `LOGIN_MAX_ATTEMPTS` e `LOGIN_WINDOW_SECONDS`, validados no startup.

O contador em memória vale para **um processo**. Reiniciar o processo limpa a
janela. O modo suportado aqui é um worker; antes de múltiplos workers/réplicas,
substituir por contador compartilhado (por exemplo, operação atômica em Redis)
ou aplicar a mesma política no gateway. Não confiar em `X-Forwarded-For`
enviado diretamente pelo cliente. Para execução local/direta:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --no-proxy-headers --no-server-header
```

Atrás de proxy, habilitar proxy headers somente para os IPs efetivamente
confiáveis e impedir acesso direto ao backend. Usuários inexistentes também
passam pelo bcrypt com hash fictício, reduzindo diferenças de tempo observáveis.

## Testes e scan

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest tests/
```

A suíte cobre acesso sem token, acesso a recurso alheio, campo extra sem escrita
no banco, formulário estrito, injeção SQL no username, headers/CSP, CORS,
concorrência, expiração e esgotamento de capacidade do rate limiter.

A execução do ZAP, evidências e avaliação de findings estão em
[zap-findings.md](zap-findings.md). Scan passivo não demonstra ausência de BOLA,
injeção ou vulnerabilidades de lógica: os testes de integração complementam a
análise de tráfego.

## Referências

- [Modelos de formulário com campos extras proibidos — FastAPI](https://fastapi.tiangolo.com/tutorial/request-form-models/)
- [Consultas com Session.exec e select — SQLModel](https://sqlmodel.tiangolo.com/tutorial/select/)
- [Allowlist de CORS — FastAPI](https://fastapi.tiangolo.com/tutorial/cors/)
- [Modo safe — ZAP](https://www.zaproxy.org/docs/desktop/start/features/modes/)
