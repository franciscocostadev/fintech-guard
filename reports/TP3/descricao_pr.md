## Entrega de Dados do TP3

Consolida a análise do dataset de segurança e documenta a passagem para a classificação supervisionada. Acrescenta um notebook executado com pré-processamento, regressão linear simples e múltipla, comparação com a média do treino, R², RMSE, análise dos resíduos e Q-Q plot.

O experimento usa as 603 mensagens tratadas, com 482 exemplos de treino e 121 de avaliação. A regressão simples obteve R² de 0,99877 e RMSE de 13,05 caracteres; a múltipla, R² de 0,99946 e RMSE de 8,61 caracteres. O notebook explica que esses resultados refletem relações entre medidas de extensão do texto e não demonstram capacidade de detectar fraude ou classificar intenções.

## Alterações

- Notebook, figuras, métricas, previsões e manifesto da divisão em pastas próprias do TP3, com rastreabilidade dos registros e preservação das saídas de execução.
- Pergunta de classificação em Markdown e PDF de duas páginas: classes, distribuição, decisão proposta entre binária e multiclasse e justificativa do aprendizado supervisionado.
- Planejamento T2 com TF-IDF, regressão logística e comparação com SVM linear, prevenção de vazamento, métricas por classe e avaliação externa em mensagens bancárias em português.
- Verificador de evidências que confere IDs, hashes, rótulos, partições, valores observados, previsões e resíduos, além de recalcular R²/RMSE; 11 testes adicionais cobrem inconsistências nesses artefatos.
- Dependências de desenvolvimento centralizadas, incluindo scikit-learn, e README com instruções de instalação e reprodução do TP3.
- Workflow de validação de Dados no fork, com execução integral do notebook e da suíte pytest.

## Validação

- **GitHub Actions (Ubuntu): 58 testes aprovados**, notebook e verificador concluídos no commit `ead6000`. [Execução de 18/10/2026](https://github.com/Victorbicalhoa/fintech-guard/actions/runs/39137515437).

- **58 testes aprovados** em ambiente Windows novo com Python 3.13.15 e instalação por `requirements-dev.txt`.
- Notebook executado do início ao fim: sete células de código, três gráficos incorporados e nenhum erro.
- Métricas reproduzidas e evidências verificadas. A tabela de diagnóstico apresenta os maiores erros de cada modelo separadamente.
- Integridade de 78 arquivos da API, datasets e histórico TP1/TP2 confirmada por hashes, sem alterações.
- Registros da revisão local: [`reports/TP3/resultado_validacao.md`](https://github.com/Victorbicalhoa/fintech-guard/tree/feat/tp3-dados/reports/TP3/resultado_validacao.md) e [`reports/TP3/local_validation/`](https://github.com/Victorbicalhoa/fintech-guard/tree/feat/tp3-dados/reports/TP3/local_validation/).

## Alinhamento para a entrega conjunta

Este PR cobre o escopo do integrante A. O alvo proposto é conteúdo benigno versus ameaça segundo os rótulos do dataset; isso não equivale à intenção real do cliente ou ao roteamento de pedidos bancários. A adaptação da pergunta do enunciado deve ser alinhada com o integrante B e com a orientação da disciplina antes da entrega conjunta. BANKING77 permanece separado.

O integrante B conclui o workflow de segurança da versão integrada e a proteção de merge, identifica o colega adversário e a URL/IP autorizada e consolida a auditoria final, os findings e a disponibilidade do OpenAPI. O workflow de Dados está restrito ao fork e não substitui esses itens. Nenhum classificador foi treinado nesta etapa.
