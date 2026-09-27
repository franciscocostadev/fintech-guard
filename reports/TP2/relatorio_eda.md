# Relatório de EDA — Fintech Guard — TP2

**Responsável:** Integrante A — Engenharia de Dados e IA.
**Entrega:** relatório de EDA do TP2, consolidado em 26/09/2026. Escopo do Integrante A; evidências de API e auditoria de segurança pertencem à entrega do Integrante B.

**Leitura:** seis seções - problema, dados, análise, insights principais, limitações e próximos passos. A versão PDF reproduz o conteúdo deste Markdown, com as cinco figuras incorporadas.

## 1. Problema

### Problema do Fintech Guard

O Fintech Guard é um agente de atendimento bancário e investimentos. Seu desafio de IA é identificar indícios de fraude ou engenharia social nas mensagens recebidas. A proteção de saldos, CPF e outros dados sensíveis, incluindo prevenção de vazamento de dados pela IA, é um requisito do sistema; a EDA, isoladamente, não demonstra essa proteção.

### Objetivo da análise

Investigar características das mensagens benignas e das diferentes classes de ameaça, avaliando a qualidade dos dados e possíveis diferenças estatísticas que apoiem a futura classificação.

**Pergunta orientadora:** quais características observáveis dos textos e quais limitações do dataset devem orientar o planejamento de um classificador de mensagens benignas e ameaças de engenharia social?

### Papel dos datasets

| Dataset | Papel no projeto | Limite de interpretação |
|---|---|---|
| Multiclass NLP Dataset for Phishing and Social Engineering Threat Detection | Principal para a EDA do TP2 ligada ao desafio de segurança das mensagens. | Seus rótulos representam classes de ameaça ou conteúdo benigno; não comprovam ocorrência de fraude bancária real nem intenção do autor. |
| BANKING77 | Complementar para identificar intenções de atendimento bancário e contextualizar o domínio. | Seus rótulos são intenções de atendimento, não rótulos de fraude; uma categoria sobre segurança da conta não torna a mensagem maliciosa. |

### Continuidade em relação ao TP1

A EDA corrigida do BANKING77 permanece preservada em `notebooks/TP1/banking77/01_eda_banking77.ipynb`. O notebook inicial de segurança foi preservado em `notebooks/TP1/security/01_dataset_understanding.ipynb`. O desenvolvimento do TP2 ocorre em `notebooks/TP2/security/01_validacao_e_eda_estatistica.ipynb`. No TP2, este conjunto passa a ser o foco principal da análise estatística, por estar mais diretamente relacionado ao desafio de IA definido para o Fintech Guard. Os dois datasets não serão concatenados nem tratados como se compartilhassem a mesma taxonomia.

A observação do TP1 sobre mensagens longas de Phishing foi localizada e formalizada no passo 5. Trata-se de um desdobramento exploratório, não de uma hipótese já testada no TP1.

### Responsabilidade e limites desta entrega

- **Integrante A:** qualidade e tratamento dos dados, atributos exploratórios, correlações, visualizações, teste de hipótese com interpretação e relatório de EDA.
- **Integrante B:** API, autenticação, controles OWASP, rate limiting, testes de segurança e auditoria ZAP.
- **TP3:** formular a pergunta de classificação e planejar a arquitetura de IA a partir das evidências do TP2. A escolha entre classificação binária e multiclasse permanece em aberto; não haverá treinamento nesta etapa.

O dataset de segurança contém textos em inglês e não é exclusivamente bancário. A adequação ao contexto de atendimento pretendido, a representatividade e as condições de uso documentadas no TP1 precisam ser examinadas. Padrões estatísticos serão tratados como evidências exploratórias, não como prova de capacidade de detecção ou de proteção contra vazamento.

## 2. Dados

### Fonte e integridade

Dataset principal: *Multiclass NLP Dataset for Phishing and Social Engineering Threat Detection*, arquivo `data/raw/security/phishing_nlp_dataset.xlsx`, aba `in`.

Fonte consultada em 23/09/2026: [Zenodo, registro 15235123](https://zenodo.org/records/15235123). O MD5 do arquivo local coincide com o publicado: `7213a3ee515a713f4eee2a6948f1756e`. O Excel foi somente lido.

SHA-256 local: `651fb58e1a3ff7808aad12eb5a24a44dc0ba95a4f4da356640d17a830dd8bd32`.

### Reconstrução e inspeção

O Excel tem 624 registros e duas colunas (`Corpus`, `Labels`). Existem 621 células ausentes em `Labels`; nessas linhas, o rótulo está no final de `Corpus`, separado pela última tabulação. Nas linhas **382, 390 e 404** do Excel, o texto está dividido entre as duas colunas. A reconstrução junta os fragmentos com um espaço, separa a última tabulação e remove espaços nas extremidades do texto e do rótulo.

O DataFrame reconstruído tem **624 × 2**, colunas `text` e `category`, ambas `object` no ambiente do projeto (pandas 2.2.3). Não há ausentes nem campos vazios. O notebook contém as saídas de dimensões, tipos, ausentes e `describe(include="all")` para o Excel, os dados reconstruídos e os dados tratados.

### Limpeza reproduzida

- Nove ocorrências excedentes de duplicatas exatas, envolvendo 14 linhas, antes da limpeza.
- 24 linhas envolvidas em duplicação por texto normalizado com `strip().lower()`.
- Seis grupos de textos normalizados com rótulos conflitantes: todas as suas 15 linhas foram excluídas.
- Após essa exclusão, seis duplicatas restantes foram removidas, mantendo a primeira ocorrência na ordem do Excel.
- Resultado: **624 − 15 − 6 = 603 registros**, duas colunas e seis classes.

Esses diagnósticos se sobrepõem: não se somam nove duplicatas exatas às 15 exclusões por conflito.

### Distribuição das classes

| Categoria | Antes | Conflitos excluídos | Duplicatas excluídas | Depois | % final |
|---|---:|---:|---:|---:|---:|
| Baiting | 80 | 0 | 0 | 80 | 13,27% |
| Malware | 78 | 0 | 1 | 77 | 12,77% |
| NOT-Malicious General Class | 171 | 0 | 0 | 171 | 28,36% |
| Phishing | 117 | 7 | 0 | 110 | 18,24% |
| Pretexting | 78 | 8 | 5 | 65 | 10,78% |
| Scareware | 100 | 0 | 0 | 100 | 16,58% |
| **Total** | **624** | **15** | **6** | **603** | **100%** |

Percentuais arredondados a duas casas. A maior classe tem aproximadamente 2,63 vezes o tamanho da menor.

### Preservação e rastreabilidade

Após a reconstrução, os textos e rótulos retidos permanecem exatamente iguais aos respectivos registros de origem reconstruídos. Caixa, pontuação e conteúdo não são substituídos pela versão normalizada. Não houve corte de mensagens por tamanho nem balanceamento. Isso não significa identidade literal com as duas células do Excel: a junção e o `strip()` descritos acima fazem parte da reconstrução.

Os CSVs intermediário e tratado existentes coincidem, em valores e ordem, com os resultados reexecutados; não foram regravados. A auditoria em `reports/TP2/security_validation` registra as 624 linhas de origem e isola as 21 exclusões, com motivo, classe, hashes e referência à linha mantida quando aplicável. O conjunto final não possui ausentes, textos vazios, duplicatas normalizadas ou conflitos de rótulo remanescentes segundo essa regra.

### Condições de uso

A licença não está identificada na consulta da fonte documentada em 23/09/2026. Não se presume autorização irrestrita de uso ou redistribuição; esclarecer essas condições permanece pendente. A anonimização é declarada pelos autores, sem auditoria independente nesta análise.

### Como reproduzir

Na raiz do projeto, com as dependências instaladas:

```bash
python -m scripts.validate_security_dataset
python -m scripts.execute_security_notebook
```

O primeiro comando verifica os arquivos existentes e exporta a auditoria; o segundo executa o notebook completo e salva suas saídas.

## 3. Análise

### 3.1 Atributos numéricos exploratórios — passo 3

As sete medidas são calculadas sobre o texto tratado preservado, antes de qualquer conversão de caixa. A extração não usa `category`, IDs ou hashes; esses campos servem apenas para agrupamento e rastreabilidade e não entram no heatmap.

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


As medidas são exportadas em `reports/TP2/security_features/features.csv`, com linha do Excel, linha do CSV tratado, hash do texto e classe. `describe.csv` e `quality.csv` registram estatísticas e controles de qualidade. Não há duplicação dos textos nessa exportação.

Teste com SciPy concluído na seção 3.3, incluindo premissas, significância, p-valor e efeito.

### Resultados do passo 3

Foram calculados sete atributos para as 603 mensagens, sem valores ausentes ou infinitos. Textos, rótulos, ordem e seis classes foram preservados. A mediana é 101 caracteres e 17 palavras; as médias são aproximadamente 188,07 e 33,01, respectivamente. O máximo de 3.693 caracteres mostra que mensagens longas podem influenciar médias e correlações; não houve corte ou exclusão por tamanho.

Há 52 mensagens com dígitos e 36 com exclamações. Nenhuma contém links reconhecidos pela regra explícita adotada: `n_links` tem 603 zeros e é constante. Isso não prova ausência de referências externas, pois domínios nus e ofuscados não são reconhecidos. A coluna foi preservada nas evidências, mas excluída do heatmap: correlação com uma variável de variância zero é indefinida, não zero.

Seis testes automatizados verificam exemplos calculados manualmente, texto vazio/sem letras, apóstrofos e hífens, URLs, Unicode e rejeição de entradas inválidas. Reprodução: `python -m unittest discover -s tests -p test_security_features.py -v`.

Esses resultados descrevem a amostra inteira; não demonstram associação com uma classe, causalidade ou capacidade de detectar fraude. Visualizações registradas no passo 4; teste exploratório concluído no passo 5.


### 3.2 Visualizações — passo 4

#### Método

Somente os atributos listados em `FEATURES` entram na correlação. Classe, linha do Excel, linha do CSV e hash ficam de fora. A categoria é usada apenas como agrupamento visual, sem códigos numéricos arbitrários. Mantemos todos os 603 registros, inclusive extremos, sem balanceamento. As figuras são salvas em `reports/TP2/figures` e incorporadas às saídas deste notebook.

Pearson descreve associação linear; Spearman descreve associação monotônica por postos, reduzindo a influência da magnitude dos extremos. São medidas descritivas desta amostra, sem interpretação causal ou teste formal de significância nesta etapa.

#### 1 Heatmap de correlação com seaborn

![Visualização da EDA](figures/01_heatmap_correlations.png)

**Interpretação:** caracteres e palavras medem aspectos próximos do comprimento; sua associação positiva elevada pode refletir redundância entre medidas, não um sinal de fraude. Diferenças entre os painéis mostram que associação linear e ordenação dos valores não são equivalentes, especialmente com extremos e muitos zeros. `n_links` foi excluído por variância zero: sua correlação seria indefinida, não zero. Nenhum coeficiente mede relação com a classe, pois rótulos não entram nas matrizes. A diagonal igual a 1 é a correlação de cada atributo consigo mesmo. Neste dataset, caracteres × palavras têm Pearson = 0.9986 e Spearman = 0.9580; o valor 1,00 no heatmap de Pearson resulta do arredondamento, não de identidade perfeita.

#### 2 Scatter plot — palavras × caracteres

![Visualização da EDA](figures/02_scatter_words_characters.png)

**Interpretação:** mensagens com mais palavras tendem a ter mais caracteres. A visão completa evidencia casos muito longos, enquanto a ampliação permite inspecionar a concentração de mensagens curtas e a sobreposição visual entre classes. O painel ampliado limita apenas a janela exibida: os pontos fora dela continuam na base e no painel completo. A tabela identifica os cinco textos mais longos pela linha de origem, sem reproduzir o conteúdo. Comprimento isolado não demonstra separação confiável entre classes; os extremos devem ser examinados, não removidos automaticamente.

#### 3 Comprimento × links — gráfico não produzido

`n_links` é zero em todas as 603 mensagens. Um scatter produziria apenas pontos alinhados no zero, sem variação para investigar associação. Por isso, este gráfico condicional foi omitido. A ausência de links reconhecidos não equivale à ausência de endereços ofuscados, domínios sem prefixo ou conteúdo malicioso. A coluna e sua definição continuam preservadas nas evidências do passo 3.

#### 4 Boxplots — comprimento por classe

![Visualização da EDA](figures/03_boxplots_length_by_class.png)

**Interpretação e legenda:** a linha interna é a mediana; a caixa vai do primeiro ao terceiro quartil; os bigodes alcançam os valores dentro de 1,5 vezes a amplitude interquartil e os pontos além deles são extremos segundo essa regra. Todos permanecem na análise. O eixo logarítmico acomoda a grande amplitude: distâncias iguais representam razões, não diferenças absolutas. As caixas são calculadas nos valores originais e depois exibidas nessa escala. Diferenças entre medianas e dispersões motivam investigação estatística, mas o gráfico não estabelece significância nem desempenho de classificação. As classes estão identificadas diretamente no eixo vertical. Nesta amostra, Phishing apresenta a maior dispersão e concentra os textos mais longos, mas suas caixas se sobrepõem às de outras classes. Isso não permite concluir que toda mensagem longa seja maliciosa.

#### 5 Distribuição das classes após a limpeza

![Visualização da EDA](figures/04_class_distribution.png)

**Interpretação:** a classe benigna tem 171 mensagens (28,36%) e Pretexting, a menor, 65 (10,78%); a razão entre elas é aproximadamente 2,63. As barras representam contagens, e os rótulos mostram contagem e percentual do total. Essas proporções descrevem o dataset após a limpeza, não a prevalência de ameaças no atendimento bancário. O desbalanceamento deve orientar a divisão estratificada e a avaliação por classe no planejamento do TP3; nesta etapa não houve reamostragem.

#### 6 Scatter plot — caracteres × proporção de maiúsculas

![Extensão e capitalização](figures/05_scatter_characters_uppercase.png)

**Interpretação:** este segundo relacionamento compara extensão e capitalização. A proporção de maiúsculas varia entre as mensagens e as classes se sobrepõem visualmente; ela não oferece, por si só, uma fronteira de detecção. O eixo de caracteres está em escala logarítmica apenas para exibição, sem excluir os textos longos ou transformar os valores usados nas correlações. Pearson indica associação positiva fraca (aproximadamente 0,14), enquanto Spearman indica associação negativa por postos (aproximadamente -0,38). Essa diferença reforça a necessidade de examinar a forma da relação e os extremos. A proporção divide maiúsculas pelo total de letras: uma inicial maiúscula pode representar uma fração maior em textos curtos. Portanto, parte do padrão pode decorrer da construção da medida, não de um comportamento de fraude. Não foi feito novo teste de hipótese nem seleção de atributo por desempenho.

### 3.3 Hipótese formal — passo 5

#### Origem no TP1 e natureza exploratória

O notebook `notebooks/TP1/security/01_dataset_understanding.ipynb`, seção **7. Comprimento das mensagens**, célula Markdown 29 (contagem a partir de 1), registra: “As mensagens mais longas pertencem a `Phishing`”. A mesma interpretação descreve assimetria à direita e recomenda preservar os textos longos. Era uma observação descritiva do conjunto reconstruído de 624 registros, não uma hipótese formal testada. No TP2, a comparação é formalizada sobre os 603 registros tratados.

O protocolo em `reports/TP2/hypothesis_test/protocol.json` foi salvo antes do primeiro cálculo de U e p, com data e hashes da fonte e dos dados. Isso **não é pré-registro confirmatório**: os mesmos dados já foram explorados no TP1 e nos passos 2–4. O resultado é exploratório e exige confirmação em dados independentes.

#### Protocolo definido antes do cálculo

- **H₀:** as distribuições de comprimento em caracteres de Phishing e mensagens benignas são iguais.
- **H₁:** as distribuições diferem; alternativa bilateral.
- **Variável:** `n_chars = len(text)`, conforme a definição do passo 3. Sem logaritmo no teste.
- **Grupos:** X = todos os 110 registros `Phishing`; Y = todos os 171 registros `NOT-Malicious General Class`. As outras quatro classes não entram. Aplicam-se somente as exclusões já documentadas no passo 2; nenhum extremo é retirado.
- **Significância:** α = 0,05. Um único teste planejado; p < α implica rejeitar H₀. Caso contrário, não rejeitar H₀. Não serão tentadas novas comparações para obter significância.
- **Teste:** `scipy.stats.mannwhitneyu`, `alternative='two-sided'`, `method='asymptotic'`, `use_continuity=True`, `nan_policy='raise'`. A aproximação assintótica incorpora correção de empates e continuidade; o método exato não é escolhido porque há comprimentos repetidos e grupos de tamanho suficiente para a aproximação.
- **Justificativa:** comprimentos assimétricos, com extremos, e dois grupos não pareados favorecem uma comparação por postos sem exigir normalidade dos comprimentos. A escolha não depende de um teste de normalidade nem do p-valor obtido.
- **Efeito:** A = U de Phishing / (110 × 171), proporção de pares em que Phishing é mais longo com meio peso para empates. Correlação bisserial por postos `r_rb = 2*A − 1`, entre −1 e 1; sinal positivo indica tendência a comprimentos maiores em Phishing. Não é acurácia de um classificador nem probabilidade de fraude.

#### Premissas e alcance

Pressupõem-se observações independentes dentro e entre grupos, comprimentos comparáveis e rótulos adequados. A deduplicação exata não garante independência: não temos IDs de autor, campanha ou família de templates. A amostra não é comprovadamente aleatória ou representativa. Essas limitações restringem a inferência para mensagens reais.

Mann–Whitney investiga ordenação relativa; não tem sensibilidade garantida a toda diferença possível de formato. Com dispersões diferentes, não será interpretado como teste exclusivo de medianas. Não rejeitar H₀ não prova distribuições iguais. Um p-valor pequeno indica incompatibilidade com H₀ sob as premissas; não informa a probabilidade de H₀ ser verdadeira.

Referência metodológica: [documentação oficial do SciPy — Mann–Whitney](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html).


#### Resultado e interpretação do teste

| Grupo | n | Mediana (caracteres) | Q1 | Q3 | IQR | Mínimo | Máximo |
|---|---:|---:|---:|---:|---:|---:|---:|
| Phishing | 110 | 111 | 76 | 385 | 309 | 50 | 3.693 |
| Benignas | 171 | 108 | 79,5 | 155,5 | 76 | 10 | 572 |

Quartis calculados por interpolação linear; IQR = Q3 − Q1. As médias são 518,99 e 128,18 caracteres e os desvios-padrão amostrais, 860,54 e 77,16, respectivamente. Os extremos elevam especialmente a média de Phishing; por isso, média e mediana contam aspectos diferentes da distribuição.

**Mann–Whitney bilateral:** U de Phishing = **10.274,5**, p = **0,1911706933**, α = **0,05**. Portanto, **não rejeitamos H₀**. Não há evidência suficiente, por este teste e sob suas premissas, para concluir diferença na ordenação dos comprimentos entre os grupos. Isso não prova que as distribuições sejam iguais nem que a diferença observada na cauda seja irrelevante: o teste não detecta necessariamente toda diferença de forma ou dispersão.

**Tamanho de efeito:** A = **0,5462** e correlação bisserial por postos = **0,0925**. Entre os 18.810 pares possíveis, Phishing é mais longo em 10.222, há 105 empates e é mais curto em 8.483. Incluindo meio peso para empates, a proporção favorável a Phishing é **54,62%**, próxima do ponto neutro de 50%; o efeito por postos é próximo de zero. Essa descrição não é uma acurácia avaliada nem a probabilidade de uma mensagem ser fraudulenta.

O p-valor indica a probabilidade aproximada, sob H₀ e as premissas, de uma estatística tão ou mais extrema que a observada. **Não é a probabilidade de H₀ estar correta.** Se fosse pequeno, forneceria evidência contra H₀; mesmo assim não demonstraria que comprimento identifica fraude. Neste caso, p excede o limiar definido antes do cálculo.

#### Relação com o TP1 e implicações para o TP3

A observação do TP1 sobre mensagens muito longas em Phishing permanece válida descritivamente. Entretanto, ela não implica que uma mensagem de Phishing típica seja muito mais longa: as medianas são 111 e 108 e há ampla sobreposição. A dispersão de Phishing é maior, mas esta análise não realizou um teste específico de dispersão. Não alteramos a alternativa, removemos extremos ou procuramos outro teste após conhecer p.

Para o TP3, comprimento pode continuar como atributo candidato, cuja utilidade terá de ser avaliada com outros sinais textuais e dados de teste independentes. Não se justifica criar uma regra “mensagem longa = fraude”. A exploração prévia, o tamanho e a seleção da amostra, a ambiguidade dos rótulos e a independência não comprovada limitam a generalização. Uma futura investigação da cauda deverá ser identificada como nova análise e validada separadamente, não como resgate deste resultado.

**Verificação:** U e a orientação do efeito foram conferidos pela contagem de todos os pares, com meio peso para empates. O p-valor foi conferido independentemente pela aproximação normal com correção de empates e continuidade. O notebook utiliza SciPy 1.18.1; resultados e versões estão em `reports/TP2/hypothesis_test/result.json`.


## 4. Insights principais

### Quais classes têm mais e menos exemplos?

Após a limpeza, temos **603 mensagens em seis classes**. A classe benigna (`NOT-Malicious General Class`) é a maior, com **171 exemplos (28,36%)**. Em seguida vêm Phishing, com 110; Scareware, com 100; Baiting, com 80; Malware, com 77; e Pretexting, a menor, com **65 (10,78%)**. A maior classe tem cerca de 2,63 vezes o tamanho da menor. Por isso, uma avaliação futura deve mostrar os resultados de cada classe: uma medida global pode esconder dificuldades nas classes menores. Essas proporções pertencem ao dataset e não representam a frequência de fraude no atendimento real.

### Existem diferenças relevantes entre mensagens benignas e ameaças?

Há diferenças descritivas que merecem atenção, principalmente na dispersão dos comprimentos. Na comparação realizada, Phishing tem mediana de **111 caracteres**, próxima dos **108** das mensagens benignas. Entretanto, os 50% centrais dos comprimentos de Phishing estão entre **76 e 385 caracteres**; nas benignas, entre **79,5 e 155,5**. Isso mostra maior variação no grupo Phishing, não uma separação clara entre os grupos.

O teste de Mann–Whitney retornou **p = 0,1912**, acima do nível de 5% definido antes do cálculo. Portanto, **não rejeitamos H₀**: esse teste não forneceu evidência suficiente para concluir diferença na ordenação dos comprimentos. Isso não prova que as distribuições sejam iguais e não elimina a diferença descritiva de dispersão. O efeito por postos foi **0,0925**, próximo de zero, coerente com ampla sobreposição.

O teste abrangeu **somente Phishing e mensagens benignas**. Não testamos todas as ameaças juntas, todas as combinações de classes ou diferenças de dispersão. Não podemos estender esse resultado às outras quatro classes nem concluir que os atributos detectam fraude. Um resultado sem significância é uma conclusão válida da análise; não foi substituído por outra comparação para buscar um p-valor menor.

### Os atributos parecem redundantes?

**Quantidade de caracteres e quantidade de palavras carregam informação muito semelhante**: a correlação foi 0,9986 por Pearson e 0,9580 por Spearman. Em termos simples, as mensagens com mais palavras quase sempre também têm mais caracteres. Usar ambos não significa necessariamente acrescentar duas informações independentes. A decisão de manter um ou os dois dependerá da avaliação futura do modelo, sem eliminar atributos apenas por esta exploração.

Os demais pares não apresentam correlações tão próximas de 1, mas isso não comprova independência ou utilidade preditiva. A contagem de links é um caso diferente: ficou em zero em todas as mensagens pela regra adotada. Portanto, não ajuda a diferenciar registros nesta base e foi excluída do heatmap por falta de variação. Isso não demonstra ausência de endereços ofuscados ou sem os prefixos reconhecidos.

### Há mensagens longas que exigirão atenção no processamento?

Sim. O conjunto tem mediana de **101 caracteres e 17 palavras**, mas alcança **3.693 caracteres e 635 palavras** nas respectivas medidas máximas. Os textos mais longos aparecem em Phishing, conforme já observado no TP1. Eles foram preservados: comprimento elevado não é, por si só, erro de coleta nem razão suficiente para exclusão.

No planejamento do processamento, será necessário verificar como o método escolhido lida com esses textos. Antes de cortar mensagens, devemos medir quantos exemplos seriam afetados em cada classe e qual informação poderia ser perdida. A contagem de palavras desta EDA **não equivale à contagem de tokens de um modelo**; o limite dependerá do tokenizador adotado. Não foi aplicado truncamento nesta etapa e ainda não foi definido um limite de entrada.

### Quais classes podem ser difíceis de distinguir?

**Phishing e Pretexting merecem atenção especial**: a auditoria identificou seis grupos de textos normalizados com rótulos conflitantes, envolvendo 15 registros dessas classes. Isso fornece evidência concreta de ambiguidade na rotulagem do dataset, mas não mede a frequência de erros de um classificador. A remoção desses casos resolve as contradições exatas encontradas; não garante que todos os demais exemplos sejam claros ou corretamente rotulados.

Os gráficos também mostram sobreposição dos comprimentos entre classes. Assim, tamanho sozinho não oferece uma fronteira evidente para distingui-las. Ainda não há modelo treinado nem matriz de confusão; não podemos afirmar qual par será o mais difícil. No TP3, essa dúvida deve orientar a revisão dos rótulos, a avaliação por classe e a inspeção dos erros, incluindo exemplos ambíguos.

### Até onde podemos generalizar os resultados?

As conclusões descrevem **este conjunto de 603 mensagens**, em inglês e de domínio não exclusivamente bancário. A amostra é pequena, não tem representatividade demonstrada e não informa grupos de autores ou campanhas que permitam garantir independência entre mensagens. Além disso, a comparação estatística foi motivada pela exploração dos mesmos dados; não é uma confirmação em amostra independente.

Portanto, os resultados não demonstram desempenho em conversas bancárias reais, em português ou diante de novas ameaças. Também não avaliam a proteção de CPF, saldos ou outros dados sensíveis da API. A exclusão de exemplos conflitantes pode tornar uma avaliação futura mais favorável do que seria em mensagens ambíguas reais. As condições de licença permanecem pendentes conforme a consulta documentada em 23/09/2026.

Para avançar ao TP3, a EDA sustenta o planejamento de uma comparação entre sinais textuais e atributos de comprimento, com divisão dos dados e métricas por classe bem definidas. **Ainda não sustenta uma regra de detecção nem uma promessa de desempenho.** A escolha entre classificação binária e multiclasse continua aberta e deverá considerar as ambiguidades e o número de exemplos disponíveis.

**Rastreabilidade:** contagens e conflitos em `reports/TP2/security_validation/`; medidas em `reports/TP2/security_features/`; correlações e gráficos em `reports/TP2/figures/`; protocolo e teste em `reports/TP2/hypothesis_test/`. Esta síntese utiliza as evidências já produzidas, sem novos testes de hipótese.

## 5. Limitações

- Amostra pequena: 603 mensagens, com classes entre 65 e 171 exemplos; não representa necessariamente a frequência de ameaças no atendimento real.
- Textos em inglês e domínio não exclusivamente bancário: transferência para o uso pretendido ainda não foi validada.
- Conflitos entre classes: a exclusão elimina contradições exatas observadas, mas não resolve toda a ambiguidade semântica nem comprova a correção dos demais rótulos. Remover casos ambíguos pode tornar uma avaliação futura mais otimista.
- Preservação limitada à reconstrução documentada: a separação dos campos e a união dos fragmentos são decisões de processamento, não recuperação garantida de uma mensagem original externa ao arquivo.
- Licença: na página oficial consultada em 23/09/2026, o campo Rights/License não identifica uma licença. As condições de uso e redistribuição continuam pendentes de esclarecimento; não foi atribuída uma licença presumida.
- A anonimização é uma informação dos autores. Não houve inspeção manual exaustiva nem auditoria de dados pessoais nesta etapa.
- Os resultados de qualidade, visualização e inferência exploratória não constituem evidência de desempenho preditivo ou de proteção contra vazamento. O teste foi motivado pela exploração dos mesmos dados; não há confirmação independente nem garantia de independência entre mensagens.

## 6. Próximos passos

### Pergunta de classificação para o TP3

**Pergunta candidata:** em que medida o conteúdo textual, combinado ou não com atributos de comprimento, permite distinguir mensagens benignas das classes de ameaça deste dataset em dados não utilizados no ajuste do modelo?

Essa pergunta será refinada no TP3. A EDA não escolheu um modelo, não treinou um classificador e não estabeleceu metas de desempenho. O resultado não significativo do teste de comprimento será preservado como parte da evidência, sem impedir a avaliação futura de atributos em conjunto.

### Decisões de planejamento

| Decisão | Evidência da EDA e encaminhamento para o TP3 |
|---|---|
| Binária ou multiclasse? | Há seis classes e conflitos entre Phishing e Pretexting. Definir se a tarefa inicial será benigno versus ameaça ou distinção das seis classes, documentando a perda de detalhe de qualquer agrupamento. |
| Como separar os dados? | Planejar divisão estratificada, verificar textos próximos e possíveis templates antes de separar treino e avaliação. Registrar uma semente e evitar ajustar transformações ou selecionar atributos usando a avaliação final. A independência por campanha não está garantida. |
| Como representar os textos? | Planejar uma referência simples baseada em texto e comparar a inclusão dos atributos exploratórios. Caracteres e palavras são quase redundantes; links são constantes nesta amostra. Não definir utilidade apenas pela correlação ou pelo p-valor. |
| Como tratar textos longos? | Medir tokens com o tokenizador escolhido e documentar eventual corte ou segmentação, incluindo quantos exemplos de cada classe seriam afetados. Preservar os textos de origem. |
| Como avaliar? | Planejar precisão, recall e F1 por classe, F1 macro e matriz de confusão; usar acurácia como complemento. Examinar falsos positivos em mensagens benignas e falsos negativos em ameaças, considerando os custos no atendimento. |
| Como investigar ambiguidades? | Revisar exemplos e critérios de rótulo, especialmente Phishing e Pretexting; registrar decisões sem inventar rótulos corretos. Não assumir que excluir conflitos exatos resolveu toda a ambiguidade. |
| Como integrar com a API? | Alinhar com o integrante B o formato de entrada e saída, nomes das classes, limites de entrada e tratamento de incerteza. Distinguir classificação textual dos controles que protegem dados sensíveis. |
| Como validar o domínio e o uso? | Esclarecer a licença e planejar avaliação independente com mensagens compatíveis com o domínio bancário e o idioma pretendido antes de alegar generalização. |

### Evidências e reprodução

O notebook executado está em `notebooks/TP2/security/01_validacao_e_eda_estatistica.ipynb`, com 15 células de código e cinco figuras incorporadas. O relatório é entregue em `reports/TP2/relatorio_eda.md` e `reports/TP2/relatorio_eda.pdf`. Auditorias, atributos, gráficos e teste permanecem nas subpastas indicadas na seção 4.

Na raiz do projeto, instalar as dependências de `requirements-dev.txt` e executar `python -m scripts.execute_security_notebook` reproduz a análise. A reprodução depende dos arquivos de dados preservados e das regras versionadas; os hashes estão nas evidências de validação e no protocolo do teste. A primeira execução estatística ocorreu em 23/09/2026; cada reexecução registra seu horário em `hypothesis_test/result.json` e renova a verificação independente de U e p. A consolidação editorial e a inspeção da entrega ocorreram em 26/09/2026.

A entrega de EDA está consolidada. A entrega completa do TP2 depende também do trabalho do integrante B: API, controles, testes e relatório ZAP, que não são comprovados por este documento.

### Passagem para o TP3: decisões ainda abertas

**Estado da transição:** a EDA está concluída. Não há modelo treinado, divisão de dados criada ou conjunto de teste reservado nesta etapa. As alternativas abaixo são propostas para discussão e registro no TP3, não escolhas já executadas.

**Alvo e domínio.** Na opção binária, a classe benigna teria 171 exemplos e as cinco classes de ameaça somariam 432; o agrupamento simplifica a saída, mas perde o tipo de ameaça e pode esconder dificuldades nas categorias menores. A opção multiclasse preserva seis rótulos, com apenas 65 exemplos em Pretexting e ambiguidades com Phishing. Decidir qual saída é útil ao agente e se os rótulos sustentam essa distinção. Confirmar também o idioma de uso: o dataset é inglês e não exclusivamente bancário. BANKING77 contextualiza intenções de atendimento, mas não fornece rótulos equivalentes de fraude. Uma tradução, se considerada, não substitui validação no domínio e deverá manter original e tradução no mesmo grupo de particionamento.

**Separação e preservação do teste.** Antes de qualquer ajuste de modelo no TP3, definir as classes e o protocolo de avaliação, identificar duplicatas aproximadas e possíveis famílias de templates e manter mensagens relacionadas na mesma partição. Comparar uma divisão fixa em treino, validação e teste com a alternativa de reservar teste e usar validação cruzada apenas no conjunto de desenvolvimento. As proporções e o número de divisões ainda serão decididos: devem considerar grupos e quantidade de exemplos de cada classe, evitando avaliações baseadas em pouquíssimos casos.

Registrar semente, IDs/hashes de cada partição, contagens por classe e versão dos dados. Usar treino para aprender parâmetros, vocabulário TF-IDF e eventuais escalas; usar validação para escolher representação, hiperparâmetros, atributos e limiar de decisão. Qualquer balanceamento ocorrerá somente no treino, inclusive dentro de cada divisão de validação cruzada. O teste deverá ficar fora dessas escolhas e ser consultado após congelar o procedimento. Se seus resultados motivarem mudanças, a avaliação deixa de ser final e precisará de nova confirmação independente.

**Limite importante:** as 603 mensagens já participaram da EDA e do teste exploratório. Reservar uma parte agora protege contra ajustes futuros sobre o teste, mas não desfaz essa exposição anterior. Não será chamado de teste completamente intocado desde a origem. Uma avaliação confirmatória exigirá dados novos e independentes, adequados ao domínio e idioma pretendidos. Enquanto não houver esses dados, o resultado futuro deverá ser apresentado como avaliação interna com essa limitação.

**Métricas e custos dos erros.** Definir com o integrante B o custo de deixar uma ameaça passar (falso negativo) e de interromper atendimento legítimo (falso positivo). Para classificação binária, relatar recall da classe ameaça, sua precisão, F1 e matriz de confusão; decidir o limiar na validação, sem escolher um valor pelo teste. Para multiclasse, relatar precisão, recall e F1 de cada classe, F1 macro e suporte (número de exemplos); distinguir ameaça classificada como benigna de confusão entre dois tipos de ameaça. Acurácia será complementar, pois pode esconder erros nas classes menores. Metas mínimas, tolerância a falsos positivos e forma de apresentar incerteza ainda precisam ser acordadas; não há meta de desempenho demonstrada pela EDA.

**Representações e referências candidatas.** Planejar uma referência trivial pela classe mais frequente e modelos simples com TF-IDF de palavras ou caracteres, como regressão logística e SVM linear. São candidatos a comparar, não modelos escolhidos ou treinados. Avaliar texto sozinho e texto combinado com atributos exploratórios, usando a mesma divisão de desenvolvimento. Caracteres e palavras são quase redundantes, e links são constantes nesta amostra. Não usar rótulos, índices de linha ou hashes como atributos; eles servem à supervisão e à rastreabilidade. A definição de tokens e o tratamento de textos longos serão documentados antes de avaliar o teste.

O aprendizado do vocabulário e das transformações deve ocorrer dentro de um pipeline ajustado somente no treino de cada divisão, para evitar que informações de validação/teste influenciem o ajuste. Referências técnicas: [prevenção de vazamento de dados no scikit-learn](https://scikit-learn.org/1.8/common_pitfalls.html) e [pipeline de representação e classificação textual](https://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_text_feature_extraction.html).

**Pendências antes da integração ao agente.** Esclarecer a licença, revisar a taxonomia e os casos ambíguos, documentar limitações de domínio/idioma, avaliar textos longos e obter evidências de desempenho em dados separados. Alinhar com o integrante B o contrato de entrada/saída, versão dos rótulos, limites de entrada e comportamento em casos incertos ou fora do domínio, incluindo eventual encaminhamento humano. Uma pontuação de modelo não será tratada automaticamente como probabilidade calibrada. O classificador não substitui autenticação, autorização ou controles contra vazamento de dados sensíveis.

**Critério para avançar:** registrar essas decisões em um plano de classificação do TP3 e congelar o protocolo antes dos experimentos. Nenhuma etapa deste relatório autoriza concluir que o agente detecta fraude; os resultados da EDA orientam o que avaliar a seguir.
