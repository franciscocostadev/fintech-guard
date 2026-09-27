## 9. Hipótese formal — passo 5

### Origem no TP1 e natureza exploratória

O notebook `notebooks/TP1/security/01_dataset_understanding.ipynb`, seção **7. Comprimento das mensagens**, célula Markdown 29 (contagem a partir de 1), registra: “As mensagens mais longas pertencem a `Phishing`”. A mesma interpretação descreve assimetria à direita e recomenda preservar os textos longos. Era uma observação descritiva do conjunto reconstruído de 624 registros, não uma hipótese formal testada. No TP2, a comparação é formalizada sobre os 603 registros tratados.

O protocolo em `reports/TP2/hypothesis_test/protocol.json` foi salvo antes do primeiro cálculo de U e p, com data e hashes da fonte e dos dados. Isso **não é pré-registro confirmatório**: os mesmos dados já foram explorados no TP1 e nos passos 2–4. O resultado é exploratório e exige confirmação em dados independentes.

### Protocolo definido antes do cálculo

- **H₀:** as distribuições de comprimento em caracteres de Phishing e mensagens benignas são iguais.
- **H₁:** as distribuições diferem; alternativa bilateral.
- **Variável:** `n_chars = len(text)`, conforme a definição do passo 3. Sem logaritmo no teste.
- **Grupos:** X = todos os 110 registros `Phishing`; Y = todos os 171 registros `NOT-Malicious General Class`. As outras quatro classes não entram. Aplicam-se somente as exclusões já documentadas no passo 2; nenhum extremo é retirado.
- **Significância:** α = 0,05. Um único teste planejado; p < α implica rejeitar H₀. Caso contrário, não rejeitar H₀. Não serão tentadas novas comparações para obter significância.
- **Teste:** `scipy.stats.mannwhitneyu`, `alternative='two-sided'`, `method='asymptotic'`, `use_continuity=True`, `nan_policy='raise'`. A aproximação assintótica incorpora correção de empates e continuidade; o método exato não é escolhido porque há comprimentos repetidos e grupos de tamanho suficiente para a aproximação.
- **Justificativa:** comprimentos assimétricos, com extremos, e dois grupos não pareados favorecem uma comparação por postos sem exigir normalidade dos comprimentos. A escolha não depende de um teste de normalidade nem do p-valor obtido.
- **Efeito:** A = U de Phishing / (110 × 171), proporção de pares em que Phishing é mais longo com meio peso para empates. Correlação bisserial por postos `r_rb = 2*A − 1`, entre −1 e 1; sinal positivo indica tendência a comprimentos maiores em Phishing. Não é acurácia de um classificador nem probabilidade de fraude.

### Premissas e alcance

Pressupõem-se observações independentes dentro e entre grupos, comprimentos comparáveis e rótulos adequados. A deduplicação exata não garante independência: não temos IDs de autor, campanha ou família de templates. A amostra não é comprovadamente aleatória ou representativa. Essas limitações restringem a inferência para mensagens reais.

Mann–Whitney investiga ordenação relativa; não tem sensibilidade garantida a toda diferença possível de formato. Com dispersões diferentes, não será interpretado como teste exclusivo de medianas. Não rejeitar H₀ não prova distribuições iguais. Um p-valor pequeno indica incompatibilidade com H₀ sob as premissas; não informa a probabilidade de H₀ ser verdadeira.

Referência metodológica: [documentação oficial do SciPy — Mann–Whitney](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html).


## Reprodução

Na raiz: `python -m scripts.execute_security_notebook`. O notebook mostra protocolo, estatísticas e interpretação. `protocol.json` preserva a escolha anterior ao cálculo; `result.json` registra U, p, efeitos, versões e hashes; `group_summary.csv` traz n, mediana, quartis, IQR, mínimo e máximo.


### Resultado e interpretação do teste

| Grupo | n | Mediana (caracteres) | Q1 | Q3 | IQR | Mínimo | Máximo |
|---|---:|---:|---:|---:|---:|---:|---:|
| Phishing | 110 | 111 | 76 | 385 | 309 | 50 | 3.693 |
| Benignas | 171 | 108 | 79,5 | 155,5 | 76 | 10 | 572 |

Quartis calculados por interpolação linear; IQR = Q3 − Q1. As médias são 518,99 e 128,18 caracteres e os desvios-padrão amostrais, 860,54 e 77,16, respectivamente. Os extremos elevam especialmente a média de Phishing; por isso, média e mediana contam aspectos diferentes da distribuição.

**Mann–Whitney bilateral:** U de Phishing = **10.274,5**, p = **0,1911706933**, α = **0,05**. Portanto, **não rejeitamos H₀**. Não há evidência suficiente, por este teste e sob suas premissas, para concluir diferença na ordenação dos comprimentos entre os grupos. Isso não prova que as distribuições sejam iguais nem que a diferença observada na cauda seja irrelevante: o teste não detecta necessariamente toda diferença de forma ou dispersão.

**Tamanho de efeito:** A = **0,5462** e correlação bisserial por postos = **0,0925**. Entre os 18.810 pares possíveis, Phishing é mais longo em 10.222, há 105 empates e é mais curto em 8.483. Incluindo meio peso para empates, a proporção favorável a Phishing é **54,62%**, próxima do ponto neutro de 50%; o efeito por postos é próximo de zero. Essa descrição não é uma acurácia avaliada nem a probabilidade de uma mensagem ser fraudulenta.

O p-valor indica a probabilidade aproximada, sob H₀ e as premissas, de uma estatística tão ou mais extrema que a observada. **Não é a probabilidade de H₀ estar correta.** Se fosse pequeno, forneceria evidência contra H₀; mesmo assim não demonstraria que comprimento identifica fraude. Neste caso, p excede o limiar definido antes do cálculo.

### Relação com o TP1 e implicações para o TP3

A observação do TP1 sobre mensagens muito longas em Phishing permanece válida descritivamente. Entretanto, ela não implica que uma mensagem de Phishing típica seja muito mais longa: as medianas são 111 e 108 e há ampla sobreposição. A dispersão de Phishing é maior, mas esta análise não realizou um teste específico de dispersão. Não alteramos a alternativa, removemos extremos ou procuramos outro teste após conhecer p.

Para o TP3, comprimento pode continuar como atributo candidato, cuja utilidade terá de ser avaliada com outros sinais textuais e dados de teste independentes. Não se justifica criar uma regra “mensagem longa = fraude”. A exploração prévia, o tamanho e a seleção da amostra, a ambiguidade dos rótulos e a independência não comprovada limitam a generalização. Uma futura investigação da cauda deverá ser identificada como nova análise e validada separadamente, não como resgate deste resultado.

**Verificação:** U e a orientação do efeito foram conferidos pela contagem de todos os pares, com meio peso para empates. O p-valor foi conferido independentemente pela aproximação normal com correção de empates e continuidade. O notebook utiliza SciPy 1.18.1; resultados e versões estão em `reports/TP2/hypothesis_test/result.json`.
