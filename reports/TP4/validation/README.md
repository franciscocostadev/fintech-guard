# Validação local do TP4 — 12/11/2026

| Verificação | Resultado | Evidência |
| --- | --- | --- |
| Notebook integral | 12 células de código executadas, 5 figuras incorporadas, sem outputs de erro | [Notebook](../../../notebooks/TP4/security/01_classificacao.ipynb) e [conferência estática](static.json) |
| Dados, inferência e regressão da API | 109 testes aprovados; 95 já existentes e 14 novos de classificação | [Log](data_api.log), [JUnit](data_api.xml) |
| Agente offline | 37 testes aprovados, incluindo Runner real com modelo falso e HTTP simulado em três turnos | [Log](agent_offline.log), [JUnit](agent_offline.xml) |
| Totais e códigos de saída | Duas suítes com saída 0, sem falhas, erros ou skips | [tests.json](tests.json) |
| Conteúdo do modelo | IDF coincide exatamente com frequência dos 483 textos de treino; 2827 termos, min_df=2 | [Auditoria posterior](../classification/lexical_audit.json) |
| Serialização | Hash verificado e 120 scores reproduzidos pelo wrapper após recarga | Célula de recarga do notebook e teste de equivalência |
| Preservação | Arquivos anteriores preservados, exceto índice README atualizado | [preservation.json](preservation.json) |

Comandos executados, em ambientes separados:

```text
python scripts/execute_tp4_notebook.py
python -m pytest tests/ -v -p no:cacheprovider
python -m pytest agent_tests/ -v -p no:cacheprovider
```

A execução local concluiu ambas as suítes. Os testes específicos de classificação
também passaram isoladamente (14/14).

Os testes usam banco temporário e usuários sintéticos. Os de agente não acessam OpenAI nem
uma API externa. Não houve novo scan ZAP ou pentest, não há demonstração real de conversa,
e estes resultados não substituem integração HTTP autenticada de `/classify`.

O notebook foi executado durante a preparação local. A cópia para TP4 foi conferida por hashes;
não se trata de execução GitHub Actions desta alteração. Os caminhos pessoais nos logs foram
substituídos por marcadores. O classificador e seus dados/protocolo não foram alterados após
olhar os resultados. A seção de interpretação e os relatórios foram completados depois.

As versões usadas estão nos [metadados](../../../models/TP4/security/metadata.json),
no [ambiente de dados](../classification/environment.json) e nos arquivos de requirements
na raiz. Os artefatos não foram publicados no GitHub nesta etapa.
