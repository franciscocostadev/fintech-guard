# Execução de Dados do TP3 no fork

O workflow `.github/workflows/tp3-dados-manual.yml` executa em pushes exclusivamente na
branch `feat/tp3-dados` de `Victorbicalhoa/fintech-guard`, sem atualizar main ou o upstream.
O gatilho manual também está definido; sua disponibilidade na interface depende de o
workflow existir na branch padrão. A validação registrada utilizou o gatilho de push.

O runner Ubuntu 24.04 instala Python 3.13 e `requirements-dev.txt`, executa o notebook,
a suíte completa e `scripts.verify_tp3_evidence`. O token tem acesso somente de leitura;
não há uso de secrets ou deploy.

O artefato `tp3-dados-<run_id>-<tentativa>` guarda notebook, figuras, métricas, manifesto,
versões, commit, logs e JUnit por 14 dias. Também há upload em falhas: a existência de um
artefato não comprova sucesso. É necessário conferir a execução verde, o JUnit e
`ci/validation.json`, além de revisar gráficos e interpretações.

O resultado aprovado em 14/10/2026 está em `resultado_validacao.md` e corresponde ao commit
nele identificado. A revisão de 17/10 foi validada localmente em Windows (58 testes e notebook executado).
O commit `ead6000` executou o workflow em 18/10 e aprovou os 58 testes.
As saídas correspondentes estão em `ci_20261018/`; ver [publicação](publicacao_github.md). As evidências
anteriores permanecem identificadas separadamente dos resultados da revisão publicada.

As notas de bloqueio local são históricas; outputs Linux não demonstram execução Windows.
Este workflow não cobre pull requests ou a branch main e não configura bloqueio de merge.
O CI de segurança da entrega conjunta permanece sob responsabilidade do integrante B.
