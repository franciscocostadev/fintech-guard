# TP3 — Entrega do integrante A: Dados e IA

Base upstream: `franciscocostadev/fintech-guard`, commit
`649f5c43f91f4b2fa0bbdadfb357061175760377`, obtido em 14/10/2026.
A cópia local TP2 e as evidências anteriores foram preservadas.

## Evidências

| Requisito de Dados | Evidência |
|---|---|
| Pré-processamento, LinearRegression simples e múltipla | `notebooks/TP3/security/01_regressao_e_transicao.ipynb` e `scripts/tp3_regression.py` |
| R², RMSE, resíduos e Q-Q plot | Notebook; `regression/metrics.csv`; `regression/predictions.csv`; `figures/` |
| Limitações da regressão para classificação | Seção 6 do notebook; `pergunta_classificacao.md` |
| Classes, distribuição e justificativa para ML supervisionado | `pergunta_classificacao.md` e sua versão PDF |
| Modelo candidato e estratégia de features para T2 | `planejamento_T2.md` |
| Execução e rastreabilidade | `resultado_validacao.md`; evidências históricas em `ci/` |

## Reprodução no PowerShell, a partir da raiz

Com o ambiente virtual criado:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv/Scripts/python.exe -m scripts.execute_tp3_notebook
.venv/Scripts/python.exe -m pytest tests/ -v -p no:cacheprovider --junitxml=reports/TP3/local_validation/pytest.xml
.venv/Scripts/python.exe -m scripts.verify_tp3_evidence --test-report reports/TP3/local_validation/pytest.xml --output reports/TP3/local_validation/validation.json
```

`requirements-dev.txt` reúne as dependências de desenvolvimento e dos testes, incluindo
scikit-learn. `requirements-tp3-dados.txt` permanece como entrada compatível para a execução
de Dados e inclui esse mesmo arquivo. Se o ambiente foi instalado com uv e não contém pip,
usar `uv pip install --python .venv/Scripts/python.exe -r requirements-dev.txt`.

O notebook também encontra a raiz quando iniciado na própria pasta. O script contém a
implementação compartilhada; o notebook apresenta pipelines ajustados, tabelas e interpretações.
O histórico de bloqueio da extensão nativa do SciPy pelo Windows está registrado em
`resultado_validacao.md`. O resultado da revisão atual identifica separadamente
o ambiente e os comandos executados em `local_validation/`.

## Estado da validação

A execução do GitHub Actions de **14/10/2026** aprovou o notebook daquela revisão e **47 testes**.
O commit e o resultado estão em [resultado_validacao.md](resultado_validacao.md).
A revisão local de **17/10/2026** executou o notebook e aprovou **58 testes** em um novo
ambiente Windows instalado com `requirements-dev.txt`. Os registros próprios estão em
`local_validation/`; os arquivos de `ci/` preservam a execução original em Linux.
A revisão foi publicada no fork e aprovada no [GitHub Actions de 18/10/2026](https://github.com/Victorbicalhoa/fintech-guard/actions/runs/39137515437),
também com 58 testes. Consulte [publicação e revisão do colega](publicacao_github.md).

## Recorte e passagem ao integrante B

O planejamento trata da classificação de **conteúdo benigno versus ameaça**, apoiado no
dataset de segurança. Esse recorte não equivale a inferir a intenção real do cliente nem a
rotear pedidos bancários; a adaptação e seu alinhamento pendente estão descritos na pergunta
de classificação e no plano T2.

O workflow de Dados executa no fork e não substitui o CI de segurança da entrega integrada.
API, workflow de segurança, proteção de merge, auditoria final, OpenAPI e identificação do
adversário cabem ao integrante B. Executar os testes herdados não conclui a auditoria TP3.
Os campos pendentes do plano conjunto estão em `planejamento_T2.md`.

TP1 e TP2 continuam em suas pastas. Os CSVs originais e tratados não são modificados pelo TP3.
Nenhum classificador foi treinado nesta etapa.
