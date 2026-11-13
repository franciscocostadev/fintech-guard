# Integração do TP4 — Dados e IA e API

Atualizado em 13/11/2026. Este documento reúne os artefatos de Dados e IA,
os requisitos de integração da API e as responsabilidades dos integrantes.

## Decisão de projeto

A arquitetura utiliza **dois componentes ativos**:

1. **BANKING77:** identifica uma das 77 solicitações bancárias. É o classificador
   principal para a rubrica de intenções do TP4.
2. **Segurança:** classifica conteúdo como `benign` ou `threat`. Continua sendo
   usado pelo agente como sinal complementar, sem acusar o cliente de fraude.

A evolução está descrita na [arquitetura](arquitetura_dupla.md). Os experimentos
e documentos dos TPs 1 a 3 permanecem preservados; os dois datasets não são
misturados em um treinamento. Cada modelo tem seu próprio artefato e métricas.

## Artefatos do Integrante A

| Entrega de Dados e IA | Uso por B |
| --- | --- |
| Notebook BANKING77 e relatório de classificação | Evidência de TF-IDF, LogisticRegression, GridSearchCV, baseline e métricas multiclasse. |
| Modelo e metadados em `models/TP4/banking77/` | Carregar o classificador de intenções na API. |
| Modelo e metadados em `models/TP4/security/` | Manter a análise de segurança ativa. |
| `ml.classification_service.ClassificationService` | Uma interface de inferência que devolve os dois resultados. |
| `ml/banking77_labels.json` | Taxonomia original para validação do contrato. |
| `fintech_agent/` | Agent, Runner e ferramenta que consome `/classify` com JWT. |
| [Contrato HTTP](contrato_classify.md) | Entrada, resposta composta, limites, erros e critérios de aceite. |

O preparo BANKING77 mantém as 3079 linhas de teste processadas no TP1 e cria um
treino derivado com 9985 linhas. Oito linhas do treino anterior foram excluídas
por pertencerem a grupos de texto semelhantes que tocavam o teste. A decisão,
os hashes e IDs estão em `reports/TP4/banking77/`. Não houve alteração dos CSVs
históricos. A seleção dos hiperparâmetros usa somente o treino.

### Resultados e validação

- BANKING77: macro-F1 **0,9001**, acurácia **90,00%** e ROC-AUC OvR macro
  **0,9980** no teste interno. Macro-F1 inicial 0,8592; baseline 0,0003.
  GridSearchCV selecionou C=10 e unigramas entre nove candidatos, somente no treino.
- [Notebook executado](../../notebooks/TP4/banking77/01_classificacao_intencoes.ipynb):
  12 células de código, seis figuras, métricas das 77 classes e interpretação.
- [Relatório de intenções](classificacao_banking77.md) e
  [relatório de segurança](classificacao.md), com resultados e limitações separados.
- [Validação final local](validation_dual/README.md): **124 testes de dados/API
  e 53 testes offline do agente aprovados**, sem falhas, erros ou skips.
- As três inferências sintéticas com modelos reais foram aceitas pelo validador
  do agente. Isso não substitui o endpoint real nem a conversa com LLM.

Esses resultados descrevem o benchmark interno em inglês. AUC não é acurácia,
e os scores não comprovam calibração ou generalização para português.

## Requisitos de integração — Integrante B (Francisco)

1. **Conferir o contrato antes de integrar.** O `/classify` inicialmente proposto
   retornava apenas segurança. Agora retorna `intent`, `probability` e
   `model_version` para BANKING77, além de `security` com resultados próprios.
   Se já existir uma rota local em desenvolvimento, atualizar também os schemas
   e testes que dependem do formato anterior.
2. **Instalar as dependências de inferência compatíveis** com os metadados dos
   artefatos usando `requirements-tp4-dados.txt`; verificar a suíte da API depois
   da resolução. O workflow local já instala esse arquivo no job de dados/API
   e executa os testes do agente em outro job, com dependências próprias.
   O check final `security-tests` exige aprovação dos dois. A execução no GitHub
   deve ser conferida conforme a [validação do CI](validation_dual/workflow.md).
   O ambiente do agente é separado e não deve sobrescrever o da API.
3. **Carregar o serviço uma vez por processo no lifespan/startup.** Ambos os
   modelos devem estar disponíveis para a aplicação ficar pronta. Falha de
   arquivo, hash ou versão deve impedir prontidão; não produzir fallback fictício.
4. **Implementar `POST /classify` com JWT.** Receber JSON com somente `text`, string
   estrita de 1 a 4000 caracteres, rejeitando vazio, apenas espaços, extras e
   tipos incorretos com 422. Usar o texto integral na inferência.
5. **Chamar `service.classify(text)` e devolver o schema composto.** Usar rota
   síncrona ou threadpool apropriado para inferência; não treinar ou recarregar
   modelos a cada chamada. Mapear indisponibilidade para 503 sem expor detalhes.
6. **Documentar OpenAPI e executar testes HTTP.** Conferir JWT, schemas, limites,
   resposta composta, falhas de inicialização e equivalência com o serviço Python.
   Rodar também a suíte anterior, preservando headers, CORS, rate limiting e BOLA.
7. **Preparar o ambiente de demonstração.** Disponibilizar a API em execução e
   uma conta sintética com JWT para a chamada do agente; a dupla configura chave
   e modelo OpenAI localmente e registra os três turnos reais.
8. **Completar o escopo de segurança do TP4.** Executar e documentar os ataques
   autorizados e o log parcial. Acrescentar a nova rota ao inventário da própria
   API e revisar sua superfície de entrada. O trabalho de Dados e IA não fornece
   evidência de JWT attacks, Kiterunner/Nmap, BOLA/BFLA/IDOR ou fuzzing adversarial.

Exemplo de interface Python a integrar:

```python
from ml.classification_service import ClassificationService

service = ClassificationService()  # lifespan/startup
response = service.classify(text)  # rota autenticada
```

A entrada e a saída JSON completas estão no [contrato](contrato_classify.md).
Essa interface permite integrar os modelos sem repetir o treinamento ou
reimplementar a lógica estatística na API.

## Conferência conjunta antes da entrega

| Evidência | Responsabilidade | Condição de conclusão |
| --- | --- | --- |
| Notebook e relatório de intenções | A | Outputs preservados, métricas por 77 classes, baseline e GridSearchCV reproduzíveis. |
| Dois artefatos e inferência | A | Metadados, versões, validação e testes coerentes com os modelos entregues. |
| `/classify` com JWT e startup | B | HTTP real e OpenAPI verificados com ambos os modelos. |
| Suíte da API atual | B | Execução integral aprovada e registrada na versão integrada. |
| Agent + Runner + ferramenta | A | Testes offline separados da evidência de execução real. |
| Conversa real de pelo menos três turnos | A + B | API real, classificações registradas e respostas revisadas. |
| Pentest e log parcial | B | Método, payload, resposta, evidência e avaliação preliminar por ataque. |

**Pendências atuais de integração:** rota `/classify` real, carregamento na API,
OpenAPI/testes HTTP integrados, chave/modelo OpenAI e conversa real de três turnos.
O guia [`agente.md`](agente.md) contém o comando e as variáveis necessárias.
Manter chaves e JWT na configuração local de execução, sem incluí-los em
relatórios ou no repositório.

As mensagens da demonstração são sintéticas e em inglês, compatíveis com o idioma
das bases. A classificação de segurança não representa a intenção moral do
cliente; o agente pode orientar um cliente legítimo que relata um golpe.
Resultados internos não comprovam desempenho em português ou em atendimento
real, calibração dos scores nem detecção de assuntos fora das 77 intenções.
