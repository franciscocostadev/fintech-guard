# Validação do TP3 — Dados e IA

Este documento preserva a execução histórica em Linux no GitHub Actions, concluída em
14/10/2026. A revisão local de 17/10/2026 também foi executada integralmente em Windows, com
registros próprios em `local_validation/`. As duas execuções são descritas separadamente.

## Execução de 14/10/2026

- Execução: https://github.com/Victorbicalhoa/fintech-guard/actions/runs/38582165258
- Branch: `feat/tp3-dados`, no fork `Victorbicalhoa/fintech-guard`.
- Commit executado: `be6cc45fe7aac090fbf7928b9283f7f53451e7b8`.
- Base upstream: `649f5c43f91f4b2fa0bbdadfb357061175760377`.
- Resultado: **47 testes aprovados**, 14 avisos de dependências, 7,23 segundos.
- Notebook: sete células de código executadas, três figuras incorporadas, sem erros.
- Artefato: `11903233076`; SHA-256 `0ae34fb2d58a3a7098bbe6a2885603db9de47620879ef60ad74c16a1bb11312d`, conferido no download.
- Ambiente efetivo: Python 3.13.16, SciPy 1.18.1, scikit-learn 1.9.1; demais versões em `ci/environment.txt`.

## Resultados de avaliação interna
482 mensagens de treino e 121 de avaliação, semente 42, mesmas partições nos modelos.

| Modelo | R² | RMSE (caracteres) |
|---|---:|---:|
| Média do treino | -0,00182 | 372,33 |
| Regressão simples | 0,99877 | 13,05 |
| Regressão múltipla | 0,99946 | 8,61 |

O erro da múltipla é menor nesta divisão. Como alvo e preditores medem a extensão do mesmo
texto, esse desempenho não valida detecção de fraude nem classificação de intenções.
O Q-Q mostra desvios na cauda positiva; os dois textos mais longos da avaliação permanecem
subestimados. Na revisão publicada após esse run, as interpretações específicas foram
adicionadas somente em células Markdown, mantendo o código e as saídas numéricas do artefato.

## Escopo e integridade
Os quatro testes novos de Dados passaram com os 43 herdados. Dados e evidências TP1/TP2,
bem como a API, permaneceram inalterados. O repositório do colega não recebeu mudanças.
Não foi treinado classificador, nem realizado pentest ou configurada proteção de merge.
O plano conjunto ainda depende da identificação do adversário e URL autorizada pelo integrante B.

## Histórico do ambiente local
Na tentativa local anterior à execução remota, o Windows bloqueou a extensão nativa do SciPy.
O pacote local foi comparado com o wheel
oficial e era idêntico; não se desativou o Controle Inteligente de Aplicativos. A execução
comprovada por esse run é a do runner Linux, e não a do Windows. As evidências foram baixadas para TP3.
O primeiro disparo falhou antes de criar job por configuração de contexto no workflow;
a correção do cache resultou na execução aprovada acima.

O JSON `ci/validation.json` contém a checagem automatizada original. Este documento registra
a revisão posterior das três figuras e das métricas. Logs e JUnit estão em `ci/`.

## Revisão local de 17/10/2026

- Ambiente novo, isolado: Windows, Python 3.13.15; instalação offline pelo cache local com
  `uv pip install --python <ambiente>/Scripts/python.exe -r requirements-dev.txt`.
- Dependências: 83 pacotes; `uv pip check` sem incompatibilidades. A instalação padrão inclui
  scikit-learn; o arquivo específico de TP3 inclui o mesmo conjunto de desenvolvimento.
- Notebook: sete células de código executadas do início ao fim, três gráficos incorporados,
  sem erros. A tabela de diagnóstico agora mostra os três maiores erros de cada modelo.
- Suíte: **58 testes aprovados**, incluindo 11 casos novos do verificador de evidências.
  Comando: `python -m pytest tests/ -v -p no:cacheprovider --junitxml=reports/TP3/local_validation/pytest.xml`.
- Verificador: conferência de IDs, hashes, rótulos, partições, contagens, observados, previsões,
  resíduos e recálculo independente de R²/RMSE nas seis combinações modelo/partição.
- R²/RMSE mantiveram os valores apresentados acima, dentro da precisão numérica; a pergunta
  de classificação tem versão PDF de duas páginas conferida visualmente.
- API, datasets e evidências TP1/TP2 preservados por comparação de hashes. Nenhum
  classificador treinado e nenhuma publicação desta revisão.

As tentativas iniciais aprovaram os 47 testes existentes, mas os 11 casos novos não
inicializaram por falta de acesso aos diretórios criados pela fixture temporária do pytest
neste ambiente Windows, inclusive com uma base nova. Os testes de inconsistência passaram
a alterar uma célula dos CSVs carregados em memória, mantendo a leitura dos arquivos reais,
a função de validação e seus cálculos. Assim, os mesmos casos negativos são exercitados
sem modificar os artefatos ou depender de diretórios privados do pytest. A execução final
usa diretório isolado para `TEMP`, `TMP` e `MPLCONFIGDIR`; nenhuma permissão do sistema foi
alterada. Os 14 avisos restantes são de depreciação de dependências de visualização.

Os novos testes também verificam a rejeição de evidências inconsistentes. Isso não significa
que as métricas originais estivessem incorretas.

Registros: [execução](local_validation/execution.json), [ambiente](local_validation/environment.txt),
[notebook](local_validation/notebook.log), [pytest](local_validation/pytest.log),
[JUnit](local_validation/pytest.xml), [validação](local_validation/validation.json) e
[hashes dos arquivos](local_validation/source_sha256.json). Caminhos absolutos pessoais nos
logs são substituídos por marcadores; os resultados e contagens são preservados.

As evidências históricas em `ci/` continuam vinculadas ao commit de 14/10/2026. A revisão
atual ainda não possui commit nem execução remota própria. O recorte da classificação
continua proposto para alinhamento da dupla; CI de segurança, adversário/URL e prontidão
da API permanecem no plano conjunto sob responsabilidade do integrante B.
