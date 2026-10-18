# Publicação do TP3 - Dados

Atualização: 18/10/2026.

## Revisão publicada e testada
- Fork: [Victorbicalhoa/fintech-guard](https://github.com/Victorbicalhoa/fintech-guard/tree/feat/tp3-dados).
- Branch: `feat/tp3-dados`.
- Commit executado: [`ead6000`](https://github.com/Victorbicalhoa/fintech-guard/commit/ead6000d643d6c25236d291174fd99cc52f79536).
- GitHub Actions: [execução aprovada](https://github.com/Victorbicalhoa/fintech-guard/actions/runs/39137515437), Ubuntu 24.04.
- **58 testes aprovados**, 14 avisos de depreciação; sete células executadas e três imagens incorporadas.
- Verificador aprovado: 603 registros, seis classes, divisão 482/121, 363 previsões e seis métricas recalculadas.
- API, datasets e histórico TP1/TP2 preservados; nenhuma alteração na main do colega.

## Evidências arquivadas
Os registros do runner de 18/10 estão em [ci_20261018/](ci_20261018/), incluindo JUnit,
logs, ambiente, hash do commit, URL e resultado do verificador. O ZIP baixado teve SHA-256
`9ed8620db54bb46195aa8d8373bcdddb9f1fa90cc02483e01f5a4ef81c8edd36`, igual ao digest publicado pelo GitHub.
O notebook executado no runner tem o mesmo código da cópia local; R²/RMSE conferem dentro
da precisão numérica. O notebook versionado conserva as saídas locais de 17/10.

`ci/` preserva a execução de 14/10; `local_validation/` preserva a execução Windows de 17/10.
Os hashes em `local_validation/source_sha256.json` descrevem a revisão publicada no commit
`ead6000`. A atualização posterior de publicação acrescenta apenas documentação e
evidências, sem alterar código, dependências ou notebook testados.

## Revisão do integrante B
O PR ainda não foi aberto: a integração retornou `403 Resource not accessible by integration`
ao criar a solicitação no upstream, e não havia navegador conectado disponível.
O [comparativo está pronto](https://github.com/franciscocostadev/fintech-guard/compare/main...Victorbicalhoa:fintech-guard:feat/tp3-dados?expand=1) e a [descrição completa](descricao_pr.md) está preparada.
Abrir o PR para `franciscocostadev/fintech-guard:main`, usando `Victorbicalhoa:feat/tp3-dados`.
Não foi realizado merge. A dupla ainda deve alinhar o recorte de classificação; CI de segurança,
adversário/URL e auditoria final permanecem sob responsabilidade do integrante B.
