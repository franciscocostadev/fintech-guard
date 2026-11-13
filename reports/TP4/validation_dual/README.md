# Validação da arquitetura dupla — TP4 — 13/11/2026

Esta validação corresponde à implementação local de Dados e IA: BANKING77 para
intenções bancárias e segurança como componente ativo separado.

| Verificação | Resultado observado | Evidência |
| --- | --- | --- |
| Notebook BANKING77 integral | 12 células de código executadas, seis figuras incorporadas e interpretações visíveis, sem erros | [Notebook](../../../notebooks/TP4/banking77/01_classificacao_intencoes.ipynb), [conferência estática](static.json) |
| Notebook de segurança | 12 células de código executadas, cinco figuras; nota de arquitetura e interpretações visíveis | [Notebook](../../../notebooks/TP4/security/01_classificacao.ipynb) |
| Dados, inferência e API existente | **124 testes aprovados**: 95 anteriores, 14 de segurança/classificação e 15 de BANKING77/composição | [Log](data_api.log), [JUnit](data_api.xml) |
| Agente offline | **53 testes aprovados**, usando SDK real com modelo e HTTP simulados | [Log](agent_offline.log), [JUnit](agent_offline.xml) |
| Resultado das suítes | Saída 0; nenhuma falha, erro ou skip | [Totais e data UTC](tests.json) |
| Preparação BANKING77 | 9985 treino, 3079 teste, 8 exclusões; 77 classes em cada fold, sem cruzamento dos grupos | [Auditoria](../banking77/data_audit.json), [manifesto](../banking77/split_manifest.csv) |
| Conteúdo do artefato BANKING77 | IDF recalculado somente no treino; recarga reproduz os scores das 3079 linhas de teste | Testes `test_banking_artifact_idf_uses_training_only` e `test_banking_serialization_matches_all_saved_probabilities` no log |
| Métricas BANKING77 | Macro-F1 e ROC-AUC macro/ponderada recalculados a partir dos scores dos três modelos | Teste `test_banking_metrics_recompute_from_scores_and_labels` |
| Contrato entre ambientes | Inferências dos dois modelos reais aceitas pelo validador do agente em três mensagens sintéticas | [Resultado local](contract_local.json) |
| Segurança preservada | Artefato, metadados, protocolo, partição e script de treinamento originais com os mesmos hashes | [Preservação](preservation.json) |
| Histórico e API preservados | Código, dados e resultados anteriores preservados; ajustes no README, workflow, atributos Git e redação da matriz TP3; fontes históricas BANKING77 mantêm os blobs originais | [Preservação](preservation.json), [ajuste de CI](workflow.md) |
| Workflow e portabilidade Git | YAML conferido; 16 cenários do check final aprovados; dois ambientes sem conflitos e 15 arquivos com bytes de trabalho preservados pelos filtros | [Validação do workflow](workflow.md), [resultado](workflow.json) |

## Comandos executados

Em ambientes separados, conforme os requirements do projeto:

```text
python scripts/execute_tp4_banking_notebook.py
python scripts/execute_tp4_notebook.py
python -m pytest tests/ -v -p no:cacheprovider
python -m pytest agent_tests/ -v -p no:cacheprovider
```

Os dois notebooks foram executados integralmente, com interpretações e gráficos
preservados nas células. A reprodução manteve protocolo, grade, features, decisões
estatísticas e métricas. O artefato original de segurança foi preservado após
confirmar igualdade de vocabulário, IDF, coeficientes e intercepto com a reprodução;
os testes confirmam equivalência dos scores persistidos.

Os testes usam dados/usuários sintéticos e banco temporário. Não houve chamada
OpenAI, API externa, novo scan ZAP ou pentest. Logs foram saneados para retirar
caminhos pessoais e hostname; nenhuma credencial integra os artefatos.

## Limites da evidência

`contract_local.json` registra inferência Python real e validação do formato em
ambientes separados. Foram observadas `lost_or_stolen_card`, `card_arrival` e
`cancel_transfer`. Não houve transporte HTTP, JWT real, Runner/LLM nessa checagem;
ela **não é a conversa real de três turnos**. Os testes do Runner também são
explicitamente simulados.

Ainda faltam integração de `/classify` com JWT, carregamento no startup e OpenAPI
por B; configuração de chave/modelo OpenAI; e execução/revisão da conversa real.
O escopo de pentest depende de B. Estes logs registram a validação local;
a execução desta revisão no GitHub Actions permanece pendente.

O workflow instala as dependências TP4 em jobs separados. A configuração
preserva o código validado dos modelos, do agente e da API.
A proteção dos finais de linha foi verificada sem modificar os dados ou reexecutar
treinamento. A reprodução por clone/checkout Git está descrita em [workflow.md](workflow.md).

A [validação anterior](../validation/README.md) é registro histórico da versão
binária inicial. Para o estado atual, usar esta pasta e a
[conferência atual das rubricas](../rubricas_TP4.md).
