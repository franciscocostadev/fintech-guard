# Estado de preparação do TP3

Atualização: 18/10/2026.

## Evidência disponível

A versão de 14/10/2026 teve notebook e 47 testes aprovados no runner Linux do GitHub Actions.
Commit, URL, métricas e limitações estão em `resultado_validacao.md`. As evidências em `ci/`
registram essa execução histórica. A execução remota não demonstrou funcionamento no
Windows; a revisão de 17/10 registra sua própria execução local em `local_validation/`.

## Revisão local

Foram aplicados os ajustes de dependências, documentação, apresentação dos maiores erros
por modelo e consistência das evidências. A revisão executou as sete células e aprovou
58 testes em um ambiente Windows novo. O PDF de classificação tem duas páginas.
Os registros estão em `local_validation/` e `resultado_validacao.md`.

O documento de classificação distingue ameaça no conteúdo de intenção do cliente e registra
o recorte de segurança proposto para T2. O plano conjunto ainda exige alinhamento desse
recorte, identificação do adversário e URL, além das evidências de API e segurança.

A revisão foi publicada no fork e aprovada no Actions em 18/10, com 58 testes.
A abertura do PR no upstream depende da conta do usuário; ver [publicação](publicacao_github.md). CI de segurança, proteção de merge, auditoria
final e disponibilidade da API adversária continuam sob responsabilidade do integrante B.
