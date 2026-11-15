# Contrato de integração de intenção bancária e segurança — TP4

Atualizado em 13/11/2026. O Integrante A entrega dois pipelines independentes e
o serviço de inferência composto. O Integrante B implementa a rota, os schemas,
o carregamento na API e seus testes HTTP. **Situação: implementação de
`POST /classify` e validação HTTP integradas pendentes.**

## Entrada e autenticação

`POST /classify`, `Authorization: Bearer <JWT>`, `Content-Type: application/json`.

```json
{"text": "I lost my bank card. How can I report it through the official support channel?"}
```

- `text` é uma string estrita, de 1 a 4000 caracteres Unicode; vazio ou apenas
  espaços é inválido. Preservar espaços, pontuação e conteúdo original na inferência.
- Configurar Pydantic com `extra='forbid'` e tipo estrito. Rejeitar números, listas,
  `null`, campos extras, texto vazio e comprimento superior a 4000 com HTTP 422.
- Usar `strip()` somente para testar se o texto é vazio; não alterar a mensagem
  recebida nem truncá-la silenciosamente. O limite cobre o máximo de 3693
  caracteres observado na base de segurança; é independente do `/predict` antigo.
- Validar JWT pelas dependências existentes. Ausência ou token inválido retorna
  401. A rota não recebe chaves OpenAI ou nomes de modelo no corpo da requisição.
- A inferência não precisa persistir texto bruto. Se for criado um recurso
  persistido, aplicar ownership nas rotas de consulta correspondentes.

## Resposta HTTP 200

O schema de primeiro nível contém exatamente cinco campos. Os valores abaixo
são **ilustrativos do contrato**, não são uma previsão executada da entrada acima.

```json
{
  "task": "banking_intent_with_security",
  "intent": "lost_or_stolen_card",
  "probability": 0.82,
  "model_version": "tp4-banking77-v1",
  "security": {
    "task": "security_binary",
    "label": "benign",
    "probability": 0.75,
    "probabilities": {"benign": 0.75, "threat": 0.25},
    "model_version": "tp4-security-binary-v1"
  }
}
```

| Campo | Significado e validação |
| --- | --- |
| `task` | Literal `banking_intent_with_security`. |
| `intent` | Uma das 77 classes originais de [`banking77_labels.json`](../../ml/banking77_labels.json), incluindo maiúsculas e pontuação existentes. |
| `probability` | `predict_proba` da intenção escolhida pelo maior score; número finito em [0,1]. |
| `model_version` | Versão do artefato BANKING77, atualmente `tp4-banking77-v1`. |
| `security.task` | Literal `security_binary`. |
| `security.label` | `threat` quando `P(threat) > 0.5`; caso contrário `benign`, inclusive no empate. |
| `security.probabilities` | Exatamente `benign` e `threat`, valores finitos em [0,1], soma igual a 1 dentro da tolerância numérica. |
| `security.probability` | O score correspondente a `security.label`, não o score BANKING77. |
| `security.model_version` | Versão do artefato de segurança, atualmente `tp4-security-binary-v1`. |

Usar schema de saída explícito no FastAPI/OpenAPI, inclusive para o objeto
`security`. O agente rejeita campos extras, tarefas desconhecidas, intenção fora
da taxonomia, scores inválidos e inconsistência entre label e probabilidades.
Não renomear rótulos BANKING77 no retorno; traduções para apresentação podem
existir em outra camada, mantendo o identificador original.

Os scores dos dois modelos não podem ser somados ou comparados como uma única
confiança. Não há calibração validada para atendimento real. `threat` descreve
o conteúdo: um cliente legítimo pode citar uma tentativa de golpe. Não autoriza
bloquear uma conta ou acusar o remetente.

## Carregamento e execução

Instalar [`requirements-tp4-dados.txt`](../../requirements-tp4-dados.txt) no ambiente
de dados/API, conferir compatibilidade com as dependências da API e executar sua
suíte completa. O agente usa ambiente próprio com `requirements-tp4-agent.txt`.

```python
from ml.classification_service import ClassificationService

service = ClassificationService()  # uma vez por processo, no lifespan/startup
result = service.classify(text)    # dentro da rota autenticada
```

O serviço usa `BankingClassifier` e `SecurityClassifier`, cada um com seu próprio
pipeline e metadados. Devem estar presentes os dois diretórios:

```text
models/TP4/banking77/{classifier.joblib,metadata.json}
models/TP4/security/{classifier.joblib,metadata.json}
ml/banking77_labels.json
```

1. Criar o serviço uma vez na inicialização e disponibilizá-lo via estado ou
   dependência da aplicação. Cada worker carrega sua própria instância.
2. Falhar a inicialização/prontidão se algum artefato estiver ausente, corrompido
   ou incompatível. Não publicar sucesso de prontidão com apenas um modelo ativo.
3. Executar a inferência síncrona em uma rota `def` ou por threadpool apropriado
   se a rota for `async def`, evitando bloquear diretamente o loop assíncrono.
4. Não executar `fit`, `GridSearchCV`, download ou carregamento joblib por request.
5. Caso haja indisponibilidade em execução, responder 503 sem traceback, caminho
   local ou classe inventada. Entrada inválida deve ser capturada pelo schema e
   retornar 422; não mapear indiscriminadamente todo erro de modelo para 422.
6. Preservar JWT, headers, CORS e controles existentes; revisar o custo de CPU,
   concorrência e limites da nova rota. Logs não devem expor texto bruto ou JWT.

O hash verifica integridade, mas não torna confiável um joblib de origem desconhecida.
Carregar somente os artefatos revisados deste projeto; desserialização pode executar
código. As versões das dependências devem coincidir com os metadados. Não reajustar
os modelos em todas as linhas mantendo as métricas de teste como se descrevessem
um artefato novo; os artefatos desta avaliação devem permanecer ajustados no treino.

## Critérios de aceite da integração de B

| Verificação | Resultado esperado |
| --- | --- |
| Inicialização normal | Ambos os modelos carregados uma vez por processo. |
| Modelo ausente, hash/versão incompatível | Falha de inicialização/prontidão; sem previsão fictícia. |
| JWT válido e texto válido | HTTP 200 com intenção, score, versão e objeto de segurança. |
| Sem JWT ou JWT inválido | HTTP 401. |
| Campo extra, tipo incorreto, vazio/apenas espaços | HTTP 422. |
| 4000/4001 caracteres | 4000 aceitos; 4001 rejeitados sem truncamento. |
| Mensagem com espaços e pontuação | O serviço recebe o texto original integral. |
| Resposta HTTP versus serviço Python | Mesmo resultado para os mesmos artefatos e texto. |
| OpenAPI em execução | `/classify` com autenticação e schemas de entrada, saída e erros. |
| Suíte da API | Testes anteriores e novos aprovados; evidência da execução atual. |

Depois da integração, configurar chave/modelo OpenAI e JWT de conta sintética
para executar o [roteiro de três turnos](agente.md). Testes HTTP simulados do
agente não substituem a execução real. As duas bases são em inglês: esta
integração não comprova desempenho em português, detecção de assuntos fora da
taxonomia ou generalização para mensagens bancárias reais.

O contrato amplia a resposta binária inicialmente proposta para o TP4. Versões
locais de `/classify` que utilizem o formato anterior exigem atualização conjunta
de schemas, consumidores e testes. As rotas anteriores mantêm seus nomes.
