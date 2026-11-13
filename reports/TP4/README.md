# TP4 — Dados e IA: intenções bancárias e segurança

Revisão: 13/11/2026. O projeto usa **dois componentes ativos**: BANKING77 para
prever a solicitação bancária e o dataset de segurança para analisar sinais de
ameaça no conteúdo. O [adendo de arquitetura](arquitetura_dupla.md) registra
essa continuidade da proposta original, preservando o histórico dos TPs 1 a 3.
Base de trabalho: main de Francisco, commit `3933d21c3a9396c52bb108155ca98d70d3d85950`.

## Evidências e estado

| Exigência no escopo de A | Evidência | Estado |
| --- | --- | --- |
| Classificador de 77 intenções TF-IDF + LogisticRegression | [Notebook BANKING77 executado](../../notebooks/TP4/banking77/01_classificacao_intencoes.ipynb), [relatório principal](classificacao_banking77.md) | Treinado e avaliado; 12 células de código executadas e seis figuras |
| GridSearchCV, pelo menos dois parâmetros com três valores | [Protocolo](banking77/protocol.json), [nove candidatos](banking77/cv_results.csv), [seleção](banking77/selection.json) | C e ngram_range com três valores cada; cinco folds agrupados no treino |
| Confusão, precision/recall/F1 por classe e ROC-AUC | [Métricas](banking77/metrics.csv), [77 classes](banking77/per_class_tuned.csv), [matriz completa](banking77/confusion_tuned.csv) | Calculados e interpretados; ROC-AUC One-vs-Rest macro/ponderada |
| Baseline e ganho do modelo | [Relatório BANKING77](classificacao_banking77.md), [comparação](banking77/metrics.csv) | Baseline majoritária, pipeline inicial e selecionado no mesmo teste |
| Modelo de segurança ativo | [Notebook](../../notebooks/TP4/security/01_classificacao.ipynb), [relatório](classificacao.md) | Pipeline binário preservado, com avaliação própria |
| Dois artefatos serializados e inferência composta | [BANKING77](../../models/TP4/banking77/), [segurança](../../models/TP4/security/), [serviço](../../ml/classification_service.py) | Implementados; conferir os testes na [validação atual](validation_dual/README.md) |
| POST /classify + JWT e carregamento no startup | [Contrato para B](contrato_classify.md), [alinhamento](alinhamento_francisco.md) | Integração da API pendente — B |
| Agent + Runner + function_tool usando os dois resultados | [Código](../../fintech_agent/), [guia](agente.md), [validação](validation_dual/README.md) | Implementado; testes offline separados da evidência real |
| Conversa real de três turnos | [Roteiro/CLI](../../fintech_agent/demo.py) | Pendente: chave/modelo OpenAI e endpoint real |
| Ataques e log parcial do pentest | Entrega do integrante B | Fora desta implementação de Dados e IA |

O TP4 completo **ainda não está pronto para entrega**. Startup, HTTP autenticado
e a conversa real não são comprovados pelos testes locais dos wrappers ou por
transportes simulados. Os ataques e o log parcial também dependem de B. Consulte
a [conferência das 12 rubricas](rubricas_TP4.md).

## Resultados do classificador de intenções

| Modelo | Macro-F1 médio na validação cruzada | Macro-F1 no teste | Acurácia no teste | ROC-AUC OvR macro |
| --- | ---: | ---: | ---: | ---: |
| Baseline majoritária | 0,0005 | 0,0003 | 1,30% | 0,5000 |
| Pipeline inicial | 0,8415 | 0,8592 | 86,00% | 0,9964 |
| Pipeline selecionado | 0,8807 | 0,9001 | 90,00% | 0,9980 |

O GridSearchCV escolheu `C=10` e `ngram_range=(1,1)` usando somente o treino.
O macro-F1 do teste aumentou cerca de **4,09 pontos percentuais** em relação ao
pipeline inicial. A comparação com a baseline mostra aprendizado útil neste
benchmark; não demonstra desempenho em português ou generalização externa.
ROC-AUC 0,9980 mede ordenação dos scores One-vs-Rest, **não** 99,8% de acertos.
As 77 métricas individuais e confusões permanecem necessárias para entender erros.

O preparo criou um treino derivado com 9985 mensagens, excluindo oito das 9993
linhas do treino TP1 por componentes de similaridade que tocavam o teste. As 3079
linhas de teste foram preservadas. [Manifesto](banking77/split_manifest.csv),
[auditoria](banking77/data_audit.json) e [exclusões](banking77/excluded_training_rows.csv)
permitem reproduzir a decisão sem alterar CSVs históricos. O teste já foi visto
na EDA: é avaliação interna da base, não um conjunto externo novo.

## Reprodução

Python 3.13 foi usado na validação. Os ambientes de dados/API e agente são
separados. Reproduzir a partir de **git clone/checkout**, que aplica os atributos
de finais de linha usados pelos hashes da auditoria. ZIP e arquivos raw não
aplicam esses atributos; não usar seus bytes como equivalentes ao checkout auditado.
Na raiz do projeto, com Python 3.13:

```powershell
python -m venv .venv/dados
& .venv/dados/Scripts/python.exe -m pip install -r requirements-tp4-dados.txt
& .venv/dados/Scripts/python.exe scripts/audit_tp4_inputs.py
& .venv/dados/Scripts/python.exe scripts/execute_tp4_banking_notebook.py
& .venv/dados/Scripts/python.exe -m pytest tests/ -v

python -m venv .venv/agent
& .venv/agent/Scripts/python.exe -m pip install -r requirements-tp4-agent.txt
& .venv/agent/Scripts/python.exe -m pytest agent_tests/ -v -p no:cacheprovider
```

O notebook BANKING77 executa preparação, GridSearchCV, avaliação, serialização e
figuras. O executor só salva após concluir todas as células, preservando outputs.
Alternativa para treinamento sem notebook: `python -m scripts.tp4_banking77`.
O componente de segurança mantém seu executor `scripts/execute_tp4_notebook.py`.
O [workflow do TP4](validation_dual/workflow.md) instala os requirements adequados
em jobs separados e mantém `security-tests` como check final das duas suítes.
Validação local concluída; a execução no GitHub ainda não está registrada para esta revisão.
Reexecuções idênticas reproduzem a mesma avaliação; não constituem teste novo.
Protocolo e manifesto recusam sobrescrita com decisões ou partições divergentes.

TF-IDF é ajustado dentro dos folds; grupos de textos semelhantes não atravessam
as divisões de treino/validação ou treino/teste após as exclusões. Os artefatos
finais usam somente seus respectivos treinos. Não reajustar nos testes nem
apresentar as métricas atuais como avaliação de um modelo diferente.

## Organização

```text
notebooks/TP4/
  banking77/01_classificacao_intencoes.ipynb
  security/01_classificacao.ipynb
scripts/
  audit_tp4_inputs.py
  tp4_banking77.py, execute_tp4_banking_notebook.py
  tp4_classification.py, execute_tp4_notebook.py
ml/
  banking77_labels.json, banking_classifier.py
  security_classifier.py, classification_service.py
models/TP4/
  banking77/{classifier.joblib,metadata.json}
  security/{classifier.joblib,metadata.json}
fintech_agent/{runtime.py,demo.py}
reports/TP4/
  README.md, rubricas_TP4.md
  classificacao_banking77.md, classificacao.md
  arquitetura_dupla.md, contrato_classify.md, alinhamento_francisco.md
  agente.md, banking77/, classification/, figures/, validation_dual/
requirements-tp4-dados.txt
requirements-tp4-agent.txt
```

Os resultados dos modelos têm significados distintos: o agente não combina
scores nem interpreta conteúdo suspeito como prova contra o cliente. As bases
são em inglês, os scores não têm calibração validada para atendimento real e o
BANKING77 não detecta automaticamente assuntos desconhecidos. Consulte o
[relatório principal](classificacao_banking77.md), o [guia do agente](agente.md)
e as [tarefas concretas para Francisco](alinhamento_francisco.md).
