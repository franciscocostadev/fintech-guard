# Conferência das 12 rubricas do TP3

Conferência documental: **12/11/2026**. Execuções locais: **11/11/2026**.
Base: main integrada `2f71cb7`; revisão na branch `fix/tp3-feedback`.

No print do Rubricator, verde indica a opção selecionada. Oito linhas estão verdes na
coluna **Não demonstrou**, e quatro na coluna **Demonstrou**. A tabela preserva essa
avaliação e apresenta separadamente as evidências disponíveis após a revisão.

| # | Rubrica | Seleção no print | Evidência após a revisão |
|---|---|---|---|
| 1 | Pipeline: pré-processamento, regressão simples e múltipla | Não demonstrou | [Notebook](../../notebooks/TP3/security/01_regressao_e_transicao.ipynb), seção 3: pipelines explícitos, fit apenas no treino e previsões conferidas |
| 2 | R² e RMSE calculados e interpretados | Não demonstrou | Notebook, seção 4: cálculos explícitos; RMSE em caracteres; [métricas](regression/metrics.csv) |
| 3 | Limitações da regressão para intenções | Não demonstrou | Notebook, seção 6: alvo contínuo, categorias nominais, códigos arbitrários, redundância estrutural e ausência de avaliação de classificação |
| 4 | Cinco ou mais casos de segurança | Demonstrou | [Testes do TP3](../../tests/test_security_tp3.py): autenticação, BOLA, entradas inválidas e rate limiting |
| 5 | GitHub Actions configurado e executado | Demonstrou | [Workflow](../../.github/workflows/security-tests.yml), push/PR; [run da base integrada](https://github.com/franciscocostadev/fintech-guard/actions/runs/40040833325). [PR #6](https://github.com/franciscocostadev/fintech-guard/pull/6) com [check aprovado em 8bdec52](https://github.com/franciscocostadev/fintech-guard/actions/runs/43149334149) |
| 6 | Todos os testes passam com pytest tests/ -v | Não demonstrou | [Log completo](revisao_20261111/pytest.txt) e [JUnit](revisao_20261111/pytest.xml): 95 aprovados, zero falhas/erros/skips, 14 avisos de dependências |
| 7 | Pergunta de classificação, classes e distribuição | Não demonstrou | [Pergunta](pergunta_classificacao.md) e [PDF](pergunta_classificacao.pdf): 603 mensagens, seis classes, proposta binária 171 benignas/432 ameaças |
| 8 | Justificativa de ML supervisionado com base nos dados | Não demonstrou | Pergunta, seção de justificativa: rótulos disponíveis, informação textual, p ≈ 0,1912 do TP2 e limites da regressão contínua |
| 9 | Plano T2: candidato, features e justificativa | Não demonstrou | [Plano](planejamento_T2.md): TF-IDF + regressão logística; LinearSVC como comparação; poucos exemplos, representação esparsa, prevenção de vazamento e métricas por classe |
| 10 | Colega adversário e URL/IP registrados | Demonstrou | **Pendente na documentação atual:** colega adversário e URL/IP ainda não definidos; [plano, seção 6](planejamento_T2.md) e [auditoria, seção 7](../../docs/auditoria-final-tp3.md) |
| 11 | Checklist confirma resolução de Medium/High ZAP | Demonstrou | [Auditoria final](../../docs/auditoria-final-tp3.md) e relatórios vinculados: scan final de 23/10 sem Medium/High; não houve novo scan nesta revisão |
| 12 | /docs acessível com schemas de entrada/saída | Não demonstrou | [Validação HTTP](revisao_20261111/openapi-validacao.json) e [OpenAPI](revisao_20261111/openapi.json): HTTP 200, cinco operações, schemas e referências conferidos |

## Leitura da conclusão

Os **oito itens marcados como não demonstrados possuem evidências verificadas** nesta revisão.
Isso permite solicitar reavaliação, sem presumir a nota que será atribuída pelo professor.

Há **11 itens tecnicamente evidenciados** e uma pendência factual: adversário e URL/IP.
O print marca esse item como atendido, mas não há dados confirmados para preencher o registro.
Mantê-lo pendente evita apresentar um alvo inventado ou confundir GitHub/localhost com a API adversária.

O recorte de Dados é classificação de segurança do conteúdo. Ele preserva o dataset do TP1/TP2,
com classes benigno/ameaça e seis rótulos originais; não equivale às intenções de atendimento BANKING77.
O alinhamento desse recorte e do contrato da API com B permanece explícito no planejamento.

## Exigências complementares do enunciado

- Residual plot e Q-Q plot: presentes e interpretados no notebook executado.
- Pergunta de classificação: Markdown e PDF de duas páginas disponíveis.
- Regra que bloqueia merge com falha: ruleset `proteger-main` consultado em 12/11,
  ativo na branch padrão, exige PR e check `security-tests`. [Snapshot](revisao_rubricas_20261112/ruleset-main.json).
- Próximos passos: revisão e merge do novo PR pelo integrante B; definição do adversário,
  URL/IP e autorização; alinhamento do contrato antes de treinar e integrar o classificador.

O [PR #6](https://github.com/franciscocostadev/fintech-guard/pull/6) tem evidência remota de **95 testes aprovados em 8bdec52**.
O [registro do CI](revisao_rubricas_20261112/ci-pr6.json) vincula resultado e commit.
Confira a aba Checks para a revisão mais recente. Em 12/11, o integrante A reconfirmou
que adversário e URL/IP ainda não foram definidos; esse item permanece pendente.
