# TP4 — agente de atendimento com intenção e segurança

## Escopo e situação da evidência

O código em `fintech_agent/` implementa `Agent`, a ferramenta
`@function_tool classify_message` e `Runner.run` do OpenAI Agents SDK.
A ferramenta chama `POST /classify` por HTTP com JWT e recebe as duas
classificações separadas: intenção BANKING77 e conteúdo de segurança.

**A conversa real de três turnos está pendente.** Ainda é necessário configurar
chave/modelo OpenAI e integrar o endpoint à API de B. Nenhuma chamada paga foi
feita nesta validação. Testes com modelo falso e transporte HTTP simulado
verificam a implementação; não demonstram comportamento real do LLM.

## Fluxo e significado dos resultados

1. A mensagem atual é preservada integralmente e passada à ferramenta.
2. A ferramenta envia `{"text": "..."}` ao endpoint fixo `/classify`, com JWT.
3. O contrato identifica a tarefa `banking_intent_with_security`.
4. `intent` indica uma das 77 solicitações bancárias; `probability` e
   `model_version` correspondem ao modelo BANKING77.
5. `security` contém a classificação `benign`/`threat`, suas probabilidades,
   versão e tarefa `security_binary`.
6. O agente usa a intenção para orientar o atendimento e a segurança para
   explicar os cuidados. O histórico fica em memória com `result.to_input_list()`
   para o turno seguinte; a classificação se refere apenas à mensagem atual.

Os scores dos modelos não são somados nem comparados como uma confiança única.
Eles não demonstram calibração no mundo real. Conteúdo de ameaça não prova
intenção maliciosa do remetente: um cliente legítimo pode relatar um golpe.

As duas bases são em inglês. Desempenho em português e em atendimento real
precisa de avaliação própria. BANKING77 não cobre todo assunto bancário ou
aconselhamento de investimento; o classificador escolhe uma classe conhecida
mesmo para entrada fora de escopo. O prompt orienta esclarecimento e apoio
humano quando o resultado não corresponde à solicitação, mas isso **não é
um detector de desconhecidos validado** nem uma regra de confiança calibrada.

## Contrato e controles

- Entrada: string não vazia, 1–4000 caracteres, sem truncamento.
- Resposta de primeiro nível: exatamente `task`, `intent`, `probability`,
  `model_version` e `security`. O agente valida a intenção contra
  `ml/banking77_labels.json`, usando apenas a biblioteca padrão; não carrega
  sklearn ou modelos serializados em seu ambiente.
- A resposta de segurança aceita exatamente `task`, `label`, `probability`,
  `probabilities` e `model_version`. Scores finitos em [0,1], soma 1 e valor da
  classe escolhida coerente. Empate de 0,5 retorna benigno, como o wrapper.
- Versões aceitam somente identificadores curtos; campos extras ou instruções
  arbitrárias na resposta são rejeitados antes de chegar ao modelo.
- Destino configurado pelo operador, sempre em `/classify`; HTTPS fora de
  localhost/127.0.0.1/::1. Redirecionamentos e proxies herdados estão desativados.
  Timeout de conexão 5 s e demais operações 15 s.
- JWT permanece no contexto privado Python e no header HTTP. O schema da
  ferramenta expõe somente `text`. Chave OpenAI não entra no prompt/relatório.
- O texto enviado deve coincidir com a mensagem atual armazenada no contexto,
  impedindo que uma paráfrase gerada pelo agente substitua a entrada original.
- Falhas 401, 403, 429, timeout ou conexão retornam códigos controlados; corpos
  de erro e credenciais não são repassados ao modelo.
- O SDK exige ferramenta no início do turno e redefine a seleção depois da
  chamada, com limite de quatro iterações. O turno só é considerado completo
  se uma chamada de classificação retornar o contrato validado.
- `store=False` e tracing desativado. Isso não é uma garantia de retenção zero
  de todos os serviços: as mensagens são enviadas ao provedor para inferência.
  O roteiro de demonstração usa exclusivamente mensagens sintéticas.

O prompt restringe o agente à orientação: não há ferramenta para transações,
consulta de saldo ou cancelamento de cartão. Ele não deve pedir senha, CPF,
número completo de cartão ou códigos de autenticação, nem criar links de
atendimento. Instruções maliciosas dentro do texto são dados para análise.
Essas restrições não demonstram resistência completa a prompt injection;
a avaliação comportamental com LLM real continua necessária.

## Ambiente e testes reproduzíveis

O agente usa ambiente independente do ambiente de dados/API.
`requirements-tp4-agent.txt` fixa a resolução validada com Python 3.13.15,
incluindo `openai-agents==0.24.0`, `openai==3.50.0` e `httpx2==2.16.0`.
Não instalar essas dependências no ambiente de `requirements-dev.txt`.

Na raiz do projeto:

```powershell
python -m venv .venv/agent
& .venv/agent/Scripts/python.exe -m pip install -r requirements-tp4-agent.txt
& .venv/agent/Scripts/python.exe -m pytest agent_tests/ -v -p no:cacheprovider
```

Validação local de 13/11/2026: **53 testes offline aprovados**, com [logs e JUnit](validation_dual/README.md). São cobertos:
taxonomia de 77 intenções, separação dos scores, validação do objeto de segurança,
desempate, entrada/saída inválida, JWT privado, destino HTTP, erros e memória.

O teste `test_runner_three_turns_with_mock_model_and_mock_http_preserves_memory`
usa o Runner real com `Model` falso e `MockTransport`: três chamadas HTTP e seis
chamadas ao modelo falso, com três intenções diferentes e presença da análise
de segurança. As respostas são marcadas como simuladas. Os rótulos de segurança
dessas fixtures são artificiais, para verificar transporte/contrato, e não são
anotações esperadas dos textos nem evidência de desempenho dos modelos.

## Como concluir a demonstração real

1. B integra `/classify` com JWT e o [contrato composto](contrato_classify.md),
   carregando os dois pipelines na inicialização.
2. Configurar `OPENAI_API_KEY` e `OPENAI_MODEL` localmente, com um modelo
   disponível na conta e com suporte a ferramentas. Manter a chave apenas na
   configuração local, fora do prompt, dos relatórios e do repositório.
3. Obter JWT de conta sintética da API e configurar `FINTECH_API_TOKEN`, sem
   prefixo Bearer; `FINTECH_API_BASE_URL` usa por padrão `http://127.0.0.1:8000`.
4. Executar no ambiente do agente:

```powershell
& .venv/agent/Scripts/python.exe -m fintech_agent.demo --output reports/TP4/conversa_real.json
```

O comando faz chamadas reais e pode consumir créditos. Sem as variáveis exigidas,
encerra antes de acessar a rede. O arquivo só é criado após três turnos completos.

| Turno | Mensagem sintética | Assunto proposto |
| --- | --- | --- |
| 1 | I lost my bank card. How can I report it through the official support channel? | Cartão perdido |
| 2 | When will my replacement card arrive? | Chegada do cartão |
| 3 | I made a bank transfer by mistake. How can I request its cancellation? | Cancelamento de transferência |

O roteiro não impõe rótulos ou respostas à execução real. A evidência registra
mensagens, respostas recebidas, eventos da ferramenta, versões, modelo e data UTC.
Inclui `observed_intents`, `distinct_intents_observed` e a indicação de revisão
manual pendente. Não registra chave ou JWT.

Após executar, conferir três intenções efetivamente observadas, adequação das
respostas e uso dos sinais de segurança sem acusar o cliente. Se os resultados
não demonstrarem a competência, registrar a limitação; a mera existência do JSON
não prova aprovação da rubrica. A conversa não é um teste estatístico do modelo.

## Referências

- [OpenAI Docs — agentes e contexto privado](https://developers.openai.com/api/docs/guides/agents/define-agents).
- [OpenAI Docs — execução e continuidade](https://developers.openai.com/api/docs/guides/agents/running-agents).
- [OpenAI Docs — tracing](https://developers.openai.com/api/docs/guides/agents/integrations-observability).

As assinaturas usadas também foram conferidas no SDK instalado. Endpoint real,
credenciais/modelo e conversa efetivamente executada permanecem como pendências.
