# Auditoria do dataset de segurança — TP2

Resultado: 624 linhas reconstruídas, 15 excluídas por conflito de rótulo, seis duplicatas adicionais removidas e 603 mantidas em seis classes.

## Arquivos

- `row_audit.csv`: decisão sobre cada uma das 624 linhas.
- `excluded_rows.csv`: subconjunto de 21 exclusões.
- `class_counts.csv`: reconciliação por classe, antes e depois da limpeza.
- `describe_reconstructed.csv` e `describe_clean.csv`: saídas de `DataFrame.describe(include="all")`.
- `summary.json`: indicadores, comparações com CSVs existentes, versão do pandas e hashes de integridade.

## Como localizar uma mensagem

Abra a aba `in` do Excel original e consulte `excel_row`, que usa a numeração visível do Excel (cabeçalho na linha 1). Nenhuma linha foi excluída do Excel. A origem também é identificada pelos hashes das células `Corpus` e `Labels`.

`text_sha256` identifica o texto reconstruído. `normalized_text_sha256` identifica o grupo por `strip().lower()`; esse hash é uma chave de auditoria, não uma garantia de anonimização. Os textos completos continuam nos arquivos de dados existentes.

## Decisões

- `kept`: linha mantida. `processed_csv_row` aponta sua linha no CSV tratado, incluindo o cabeçalho.
- `excluded_label_conflict`: texto normalizado tem mais de um rótulo; todo o grupo foi excluído. `labels_in_normalized_group` lista as classes. A referência fica vazia porque nenhuma ocorrência foi mantida.
- `excluded_duplicate`: repetição remanescente do mesmo texto normalizado e classe; `reference_excel_row` aponta a primeira ocorrência mantida na ordem do Excel.

## Reconstrução e preservação

`split_Corpus_last_tab` separa a última tabulação de `Corpus`. `join_Corpus_Labels` junta fragmentos com um espaço antes da separação (linhas 382, 390 e 404). O texto e a categoria são aparados nas extremidades. A coluna `outer_text_whitespace_removed` registra esse ajuste no campo de texto. Caixa e pontuação dos textos reconstruídos mantidos são preservadas exatamente.

## Reprodução

Na raiz do projeto: `python -m scripts.validate_security_dataset`.

O validador lê o Excel e os CSVs existentes sem alterá-los. Se a reconstrução, a limpeza ou a comparação divergir, a execução falha. O MD5 da fonte é conferido contra o valor publicado no [Zenodo](https://zenodo.org/records/15235123), consultado em 23/09/2026. As condições de licença continuam sem esclarecimento. Não há treinamento ou teste de hipótese nesta validação.
