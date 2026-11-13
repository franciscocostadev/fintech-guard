# TP4 — configuração e validação local do GitHub Actions

Validação local: 13/11/2026. A execução desta revisão no runner Linux do
GitHub permanece pendente.

## Configuração

O [workflow](../../../.github/workflows/security-tests.yml) mantém os eventos
`push`, `pull_request` e `workflow_dispatch` e as permissões `contents: read`.

| Job | Ambiente e função |
| --- | --- |
| `data-api-tests` | Python 3.13, `requirements-tp4-dados.txt`, `pip check` e `python -m pytest tests/ -v`; abrange dados, inferência e segurança da API existente. |
| `agent-tests` | Python 3.13, `requirements-tp4-agent.txt`, `pip check` e `python -m pytest agent_tests/ -v`; usa modelo/HTTP simulados e não exige credenciais ou serviços externos. |
| `security-tests` | Check final com o nome já utilizado pelo projeto. Depende das duas suítes e só aprova quando ambas têm resultado `success`. |

As suítes executam em paralelo, com ambientes e caches separados. Cada uma exporta
seu próprio JUnit, inclusive quando os testes falham. Falha de instalação pode
impedir a criação do JUnit; nesse caso o job falha e o check final não aprova.

O check final usa `needs` e `if: always()`, avaliando explicitamente os resultados.
Isso evita tratar uma dependência ignorada como aprovação da validação. É o padrão
de dependências documentado pelo [GitHub Actions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-jobs).
Preservar o nome do check facilita manter a regra existente; sua aplicação como
requisito de merge continua dependendo da configuração do repositório remoto.

## O que foi validado localmente

- YAML analisado e estrutura dos três jobs, eventos, requirements, comandos,
  artefatos, caches, Python e dependências entre jobs conferida.
- O script Bash do check final foi executado nas 16 combinações de `success`,
  `failure`, `cancelled` e `skipped`. Somente `success/success` retornou código 0;
  as outras 15 retornaram código 1.
- `uv pip check` confirmou compatibilidade nos dois ambientes locais já usados
  nas suítes. O runner do GitHub usa `python -m pip check` após instalar os requirements.
- Os [124 testes de dados/API e 53 do agente](tests.json) já estavam aprovados;
  este ajuste não mudou o código testado nem repetiu o treinamento.
- `git diff --check` não indicou problemas de whitespace.

O [resultado estruturado](workflow.json) registra o hash do workflow, os 16 casos
e as verificações de integridade. Essas verificações locais não equivalem a uma
execução do GitHub Actions nem garantem disponibilidade futura do índice de pacotes.

## Integridade entre Windows e Linux

A auditoria e os metadados usam hashes dos bytes, incluindo finais de linha.
As fontes BANKING77 locais têm CRLF, inclusive dentro de uma mensagem. A
conversão implícita para LF alteraria o hash dessa mensagem e dos arquivos.

O [arquivo de atributos Git](../../../.gitattributes) agora define:

- Para as duas fontes históricas BANKING77, `text eol=crlf`: os blobs originais
  LF no Git permanecem idênticos, e o checkout em qualquer sistema restaura os
  bytes CRLF usados no experimento.
- Para protocolos, manifestos, scripts de treinamento, metadados e treino derivado
  TP4 usados na rastreabilidade, `-text`: não há conversão automática.
- Para os artefatos joblib e npz, tratamento binário explícito.

Foram comparados os hashes Git com e sem filtros em 15 arquivos. Nas duas fontes
históricas, o conteúdo normalizado continua igual ao blob do HEAD, e
`git cat-file --filters` restaura exatamente os bytes da auditoria. Esse
comportamento também foi conferido com `core.autocrlf=false`,
`true` e `input`. Nenhum texto, rótulo, partição, peso do modelo ou métrica mudou.
Ver [documentação de atributos Git](https://git-scm.com/docs/gitattributes).

**Reproduzir por git clone/checkout.** Download ZIP, `git archive` e arquivos raw
não aplicam a conversão do checkout. A auditoria pode rejeitar seus hashes; não
silenciar essa verificação nem atualizar o protocolo apenas para fazê-la passar.
O `actions/checkout` utilizado no CI aplica os atributos do repositório.

## Conferência após publicação

Conferir a execução de ambos os jobs e do check final `security-tests`, baixar
os JUnit e verificar os totais. Falha de instalação, incompatibilidade de plataforma
ou divergência de hash deve ser investigada antes do merge. Os testes offline não
substituem a integração HTTP real, a conversa com LLM ou o pentest de B.
