# Conferência das 12 rubricas do TP4

Revisão: 13/11/2026 (itens 1-3, Dados e IA) e **atualização de 21/11/2026** (itens
4-12, após a integração do Integrante B pelo [PR #8](https://github.com/franciscocostadev/fintech-guard/pull/8),
commit `006c519`). A classificação principal utiliza as **77 intenções BANKING77**,
com segurança binária como componente ativo separado. **Todos os 12 itens estão
atendidos**; a matriz relaciona cada critério à sua evidência.

| # | Rubrica | Situação nesta entrega | Evidência / o que falta |
| --- | --- | --- | --- |
| 1 | Pipeline sklearn TF-IDF + estimador e GridSearchCV | Atendido localmente para intenções bancárias | [Notebook executado](../../notebooks/TP4/banking77/01_classificacao_intencoes.ipynb): TF-IDF + LogisticRegression; C e ngram_range com três valores cada, nove candidatos e cinco folds. [Seleção](banking77/selection.json): C=10, unigramas. |
| 2 | Confusão, F1 por classe e ROC-AUC calculados e interpretados | Atendido localmente | [Matriz de 77 classes](banking77/confusion_tuned.csv), [métricas por classe](banking77/per_class_tuned.csv), seis figuras no notebook e [relatório](classificacao_banking77.md). Macro-F1 0,9001 e ROC-AUC OvR macro 0,9980; AUC não é acurácia. |
| 3 | Comparação com baseline e discussão de aprendizado útil | Atendido no benchmark interno | [Baseline, inicial e selecionado](banking77/metrics.csv): macro-F1 no teste 0,0003 / 0,8592 / 0,9001. Ganho do selecionado sobre inicial ≈4,09 pontos percentuais; limitações de idioma, domínio e validação externa explícitas. |
| 4 | POST /classify com JSON, JWT, intenção e probabilidade | **Atendido** | [Rota `POST /classify`](../../app/api/routes/classify.py) com JWT, [schemas estritos](../../app/schemas/classify.py) (`text` de 1 a 4000; extras/tipos inválidos → 422) e [18 testes](../../tests/test_classify.py). Retorna intenção BANKING77 + probabilidade + análise de segurança. |
| 5 | Modelo serializado e carregado na inicialização da API | **Atendido** | [Artefatos joblib](../../models/TP4/) carregados uma vez no lifespan por [`build_classification_service`](../../app/services/classifier.py) em [`app/main.py`](../../app/main.py); falha de hash/versão impede o startup (sem fallback fictício). |
| 6 | Agent, Runner e function_tool consumindo /classify | **Atendido** | [`fintech_agent/runtime.py`](../../fintech_agent/runtime.py): `Agent`, `Runner.run` e `@function_tool classify_message` consumindo `/classify` por HTTP com JWT; execução real registrada (item 7). |
| 7 | Conversa de pelo menos três turnos com respostas adequadas | **Atendido** | [Transcrição real](agente_transcricao.json) executada em 21/11 com `gpt-4o-mini`: três turnos, três intenções distintas (`lost_or_stolen_card`, `card_arrival`, `cancel_transfer`), respostas adequadas usando intenção + segurança. |
| 8 | Pelo menos dois ataques JWT com jwt_tool documentados | **Atendido** | [Log de pentest, seção JWT](../../pentest/log-parcial-pentest.md): None attack, Algorithm Confusion e crack de segredo (três modalidades), com [evidências](../../pentest/evidencias/jwt/). |
| 9 | Recon Kiterunner e Nmap, endpoints/serviços | **Atendido** | [Log, seção Recon](../../pentest/log-parcial-pentest.md): Nmap (portas/serviços), Kiterunner (rotas de API) e Gobuster, com [evidências](../../pentest/evidencias/recon/). |
| 10 | BOLA/BFLA/IDOR e fuzzing por Burp/Wfuzz | **Atendido** | [Log, seções Autorização e Fuzzing](../../pentest/log-parcial-pentest.md): A-B testing entre duas contas (BOLA/IDOR), BFLA e fuzzing com **ffuf** (substituto documentado do Wfuzz), com [evidências](../../pentest/evidencias/). |
| 11 | Log por tipo de ataque com método, payload, resposta e evidência | **Atendido** | [`pentest/log-parcial-pentest.md`](../../pentest/log-parcial-pentest.md) estruturado por tipo de ataque, mais o [pentest adversário](../../pentest/log-adversario-healthassist.md). |
| 12 | Avaliação preliminar e hipóteses de vulnerabilidades | **Atendido** | [Conclusão do log](../../pentest/log-parcial-pentest.md): hipóteses fundamentadas (exposição de `/openapi.json` e força do `SECRET_KEY`) a confirmar no alvo adversário. |

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

## Integração concluída (21/11/2026)

A integração do Integrante B foi concluída pelo
[PR #8](https://github.com/franciscocostadev/fintech-guard/pull/8) (commit `006c519`):

1. Rota `/classify`, schemas, JWT e carregamento de ambos os modelos no lifespan — **feito**.
2. Testes HTTP e [validação do OpenAPI](openapi-validacao.md); suíte integral com
   [142 testes aprovados](evidencia_pytest.txt) — **feito**.
3. Conversa real de três turnos do agente com `gpt-4o-mini` — **feito**
   ([transcrição](agente_transcricao.json)).
4. Pentest parcial e adversário com evidências — **feito**
   ([log próprio](../../pentest/log-parcial-pentest.md),
   [log adversário](../../pentest/log-adversario-healthassist.md)).
5. Artefatos publicados na `main`; CI aprovado no PR #8.

As responsabilidades do Integrante B estão em
[`alinhamento_francisco.md`](alinhamento_francisco.md).
