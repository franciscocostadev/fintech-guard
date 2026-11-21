# Validação do OpenAPI — Fintech Guard API

Validação do contrato OpenAPI em ambiente de desenvolvimento
(`ENVIRONMENT=development`), conferindo os schemas de entrada e saída de todos os
endpoints. Em produção o `/openapi.json` e o `/docs` ficam desligados por
segurança (não publicam o mapa da API).

Gerado a partir do app com `app.openapi()` (equivale a `GET /openapi.json` com a
API em dev). Spec completa em [`openapi.json`](openapi.json). Versão: **OpenAPI 3.1.0**.

## Endpoints (6)

| Método | Rota | Auth | Entrada | Respostas |
| --- | --- | --- | --- | --- |
| GET | `/health` | público | — | 200 (`HealthResponse`) |
| POST | `/auth/token` | público (rate limit) | `LoginRequest` (form) | 200 (`Token`), 401, 422, 429 |
| GET | `/auth/me` | JWT | — | 200 (`UserPublic`), 401 |
| POST | `/predict` | JWT | `PredictRequest` | 200 (`PredictResponse`), 401, 422 |
| GET | `/predictions/{prediction_id}` | JWT | — | 200 (`PredictionPublic`), 401, 404 |
| POST | `/classify` | JWT | `ClassifyRequest` | 200 (`ClassifyResponse`), 401, 422, 429, 503 |

## Contrato do `/classify` (foco do TP4)

**Entrada — `ClassifyRequest`:**
- `text`: string de 1 a 4000 caracteres (`StrictStr`, não vazio; campos extras rejeitados com 422).

**Saída — `ClassifyResponse`** (exatamente 5 campos de topo):
- `task`: `"banking_intent_with_security"`
- `intent`: uma das 77 intenções BANKING77
- `probability`: float em [0,1]
- `model_version`: string (versão do artefato BANKING77)
- `security` → `SecurityResult`: `task`, `label` (`benign`|`threat`), `probability`, `probabilities` (`benign`,`threat`), `model_version`

**Respostas:** 200 (sucesso), 401 (sem token / JWT inválido), 422 (entrada inválida),
429 (rate limit por usuário, com `Retry-After`), 503 (modelo de classificação indisponível).

## Schemas publicados (16)

`Channel`, `ClassifyRequest`, `ClassifyResponse`, `ErrorResponse`, `FieldError`,
`HealthResponse`, `LoginRequest`, `PredictRequest`, `PredictResponse`,
`PredictionPublic`, `RiskLevel`, `SecurityProbabilities`, `SecurityResult`,
`Token`, `UserPublic`, `ValidationErrorResponse`.

Validação realizada em 21/11/2026.
