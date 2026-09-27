# Atributos exploratórios — TP2

## 7. Atributos numéricos exploratórios — passo 3

As sete medidas são calculadas sobre o texto tratado preservado, antes de qualquer conversão de caixa. A extração não usa `category`, IDs ou hashes; esses campos servem apenas para agrupamento e rastreabilidade e não entram no futuro heatmap.

| Coluna | Cálculo exato | Unidade |
|---|---|---|
| `n_chars` | `len(text)`: pontos de código Unicode, incluindo espaços, quebras, pontuação e URLs. | caracteres |
| `n_words` | Número de sequências de letras Unicode, admitindo apóstrofos internos retos ou curvos. URLs reconhecidas são removidas apenas da cópia usada na tokenização; números e underscores não são palavras; hífens separam palavras. | palavras |
| `mean_word_length` | Total de letras dos tokens acima dividido por `n_words`; apóstrofos não contam no comprimento. Sem palavras: 0. | letras/palavra |
| `digit_ratio` | Caracteres com `isdecimal()` divididos por `n_chars`, incluindo dígitos em URLs. Texto vazio: 0. | fração de 0 a 1 |
| `uppercase_ratio` | Letras com `isupper()` divididas pelo total de letras (`isalpha()`), incluindo letras em URLs. Sem letras: 0. | fração de 0 a 1 |
| `n_links` | Ocorrências, inclusive repetidas, de prefixos `http://`, `https://` ou `www.`, sem distinguir caixa, seguidos por conteúdo até espaço, `<`, `>`, aspas simples ou duplas. Prefixos não podem ser imediatamente precedidos por letra, número, underscore ou `@`. | ocorrências |
| `n_exclamations` | Contagem literal de `!`; `!!!` conta 3. O caractere de largura completa `！` não conta. | ocorrências |

Implementação única: `scripts/security_features.py` (versão 1). A regex de palavras é `[^\W\d_]+(?:['’][^\W\d_]+)*`. Trata-se de tokenização operacional, não análise linguística completa: `don't` conta uma palavra com quatro letras e `bank-account` conta duas. Não há normalização Unicode adicional; combinações de acentos podem se comportar de forma diferente.

A contagem de links é uma heurística de referências explícitas: não valida domínios, não distingue endereços legítimos de maliciosos e não detecta domínios sem prefixo, `hxxp` ou `[.]`. Endereços não são acessados. Valores zero por ausência de palavras/letras são convenções, não imputações de dados ausentes; entradas nulas são rejeitadas.

**Interpretação:** são atributos exploratórios, não indicadores comprovados de fraude. Tamanho, capitalização, números, links e pontuação também ocorrem em mensagens legítimas. Comprimentos de caracteres e palavras podem ser correlacionados por construção. As proporções usam denominadores diferentes e não são comparáveis diretamente como frequências absolutas. Não há treinamento, seleção de atributos por desempenho, normalização estatística ou codificação numérica das classes nesta etapa.


## Reprodução

Na raiz do projeto: `python -m scripts.execute_security_notebook`.

- `features.csv`: 603 linhas, metadados de rastreabilidade, categoria e sete atributos. Sem coluna de texto.
- `describe.csv`: estatísticas descritivas dos sete atributos.
- `quality.csv`: tipos, ausentes, valores distintos e quantidade de zeros.

A versão 1 das definições e a implementação devem ser versionadas junto com a entrega. A fonte é o CSV tratado validado contra o Excel; os hashes dos dados de entrada estão em `../security_validation/summary.json`. IDs, hash e classe não são atributos numéricos de entrada.
