# Conferência das 12 rubricas do TP4

Revisão local: 13/11/2026. Escopo do Integrante A: Dados e IA. A classificação
principal utiliza as **77 intenções BANKING77**, com segurança binária como
componente ativo separado. A matriz relaciona os critérios da rubrica às
evidências disponíveis e às pendências de integração.

| # | Rubrica | Situação nesta entrega | Evidência / o que falta |
| --- | --- | --- | --- |
| 1 | Pipeline sklearn TF-IDF + estimador e GridSearchCV | Atendido localmente para intenções bancárias | [Notebook executado](../../notebooks/TP4/banking77/01_classificacao_intencoes.ipynb): TF-IDF + LogisticRegression; C e ngram_range com três valores cada, nove candidatos e cinco folds. [Seleção](banking77/selection.json): C=10, unigramas. |
| 2 | Confusão, F1 por classe e ROC-AUC calculados e interpretados | Atendido localmente | [Matriz de 77 classes](banking77/confusion_tuned.csv), [métricas por classe](banking77/per_class_tuned.csv), seis figuras no notebook e [relatório](classificacao_banking77.md). Macro-F1 0,9001 e ROC-AUC OvR macro 0,9980; AUC não é acurácia. |
| 3 | Comparação com baseline e discussão de aprendizado útil | Atendido no benchmark interno | [Baseline, inicial e selecionado](banking77/metrics.csv): macro-F1 no teste 0,0003 / 0,8592 / 0,9001. Ganho do selecionado sobre inicial ≈4,09 pontos percentuais; limitações de idioma, domínio e validação externa explícitas. |
| 4 | POST /classify com JSON, JWT, intenção e probabilidade | Pendente — integração de B | O Integrante A fornece o [serviço composto](../../ml/classification_service.py) e [contrato](contrato_classify.md), retornando intenção BANKING77 e segurança separadamente. Falta rota HTTP real autenticada, schemas e demonstração. |
| 5 | Modelo serializado e carregado na inicialização da API | Parcial | [Artefato BANKING77](../../models/TP4/banking77/classifier.joblib), [metadados](../../models/TP4/banking77/metadata.json) e [artefato de segurança](../../models/TP4/security/classifier.joblib) disponíveis localmente; [validação dos wrappers](validation_dual/README.md). Falta B conectar ao lifespan/startup, comprovar a inicialização e publicar os arquivos na entrega remota. |
| 6 | Agent, Runner e function_tool consumindo /classify | Implementado; integração real pendente | [Código](../../fintech_agent/runtime.py) chama `/classify` por HTTP e valida os dois resultados. [Testes offline](../../agent_tests/test_agent.py) usam modelo/transporte simulados e não comprovam consumo da API real. |
| 7 | Conversa de pelo menos três turnos com respostas adequadas | Pendente — A com integração de B | [Roteiro](agente.md) prevê três solicitações bancárias distintas. Faltam chave/modelo OpenAI, endpoint real, transcrição executada e revisão da adequação das respostas. Fixture ou resposta esperada não conta como conversa real. |
| 8 | Pelo menos dois ataques JWT com jwt_tool documentados | Não demonstrado nesta entrega de A — B | Deve vir do log de B com método, resultado e evidências. O enunciado completo pede três modalidades: None, confusão de algoritmo e tentativa de segredo por wordlist. |
| 9 | Recon Kiterunner e Nmap, endpoints/serviços | Não demonstrado nesta entrega de A — B | B fornece comandos, saídas, endpoints e portas/serviços; executar somente no alvo autorizado. |
| 10 | BOLA/BFLA/IDOR e fuzzing por Burp/Wfuzz | Não demonstrado nesta entrega de A — B | Testes defensivos pytest existentes não substituem os testes adversariais e suas evidências. |
| 11 | Log por tipo de ataque com método, payload, resposta e evidência | Não demonstrado nesta entrega de A — B | Conferir o log parcial TP4 de B; relatórios ZAP de entregas anteriores não substituem esse artefato. |
| 12 | Avaliação preliminar e hipóteses de vulnerabilidades | Não demonstrado nesta entrega de A — B | Hipóteses fundamentadas nos resultados reais dos ataques; não inferir vulnerabilidades sem evidências. |

## Ajuste de domínio e significado das evidências

A proposta inicial do TP4 utilizava apenas a classificação benigno/ameaça do TP3.
O [adendo](arquitetura_dupla.md) retoma BANKING77 como evidência principal de
intenções bancárias e mantém a segurança na resposta composta. Isso resolve o
desalinhamento de tarefa do treinamento; não substitui a integração real nem o
restante das rubricas. Não há equiparação entre intenções bancárias e ameaças.

O notebook BANKING77 contém 12 células de código executadas e seis figuras.
Treino derivado: 9985 mensagens; teste preservado: 3079; 77 classes. Oito linhas
de treino em componentes que tocavam o teste foram excluídas com rastreabilidade.
O melhor candidato foi escolhido somente pela validação cruzada no treino; o
teste não selecionou hiperparâmetros ou limiares. Como o teste já apareceu na
EDA, a avaliação é interna da base, não generalização externa inédita.

As métricas altas não demonstram detecção de intenção desconhecida, calibração
dos scores ou desempenho em português. O agente precisa tratar as probabilidades
separadamente e reconhecer que um cliente legítimo pode relatar uma ameaça.
Os resultados do modelo de segurança permanecem em [seu relatório](classificacao.md).

## Pendências de integração e entrega

1. Integrar a rota, schemas, JWT e carregamento de ambos os modelos com B.
2. Executar testes HTTP e validar o OpenAPI da API integrada, além da suíte atual.
3. Configurar chave/modelo OpenAI e executar os três turnos reais do agente;
   revisar respostas e classificações efetivamente observadas.
4. Conferir as evidências e o log parcial de pentest do Integrante B.
5. Disponibilizar os artefatos da entrega e registrar as execuções do CI no GitHub.

Os [testes locais atuais](validation_dual/README.md) registram as verificações
executadas. As pendências acima exigem evidências próprias de integração.
As responsabilidades do Integrante B estão em
[`alinhamento_francisco.md`](alinhamento_francisco.md).
