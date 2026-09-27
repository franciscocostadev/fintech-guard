# Dataset BANKING77

Dataset usado para a parte de EDA do projeto.

## Fonte

- Nome: BANKING77
- Fonte principal: `https://huggingface.co/datasets/PolyAI/banking77`
- Repositorio original: `https://github.com/PolyAI-LDN/task-specific-datasets`
- Licenca: Creative Commons Attribution 4.0 International (CC BY 4.0)

Escolhi esse dataset porque ele e de atendimento bancario, tem texto de cliente
e categoria de intencao. Tambem passa com folga do minimo pedido: sao 13.083
mensagens e 77 categorias.

## Arquivos no projeto

| Arquivo | Uso |
|---|---|
| `data/raw/banking77/train.csv` | treino original |
| `data/raw/banking77/test.csv` | teste original |
| `data/processed/banking77/train.csv` | treino depois da limpeza |
| `data/processed/banking77/test.csv` | teste depois da limpeza |
| `scripts/eda_banking77.py` | script da EDA |
| `notebooks/TP1/banking77/01_eda_banking77.ipynb` | EDA em notebook |
| `reports/TP1/figures/banking77_category_distribution.png` | barras por categoria |
| `reports/TP1/figures/banking77_text_length_distribution.png` | histograma de tamanho do texto |

## Colunas

| Coluna | Tipo | Descricao |
|---|---|---|
| `text` | texto | mensagem enviada pelo cliente |
| `category` | texto | intencao/tipo de atendimento |

## EDA inicial

As contagens abaixo saem do script `scripts/eda_banking77.py`, usando Pandas.

| Item | Treino original | Teste original |
|---|---:|---:|
| Linhas | 10003 | 3080 |
| Colunas | 2 | 2 |
| Categorias | 77 | 77 |
| Valores ausentes | 0 | 0 |
| Linhas duplicadas | 0 | 0 |
| Textos repetidos depois de `strip()` | 4 | 1 |
| Textos vazios | 0 | 0 |
| Textos com espaco antes/depois | 9 | 3 |

Tipos das colunas:

| Coluna | Tipo no Pandas |
|---|---|
| `text` | `object` |
| `category` | `object` |

Distribuicao das categorias:

- no teste original, cada categoria tem 40 exemplos;
- no treino, a menor categoria ficou com 35 exemplos;
- no treino, a maior categoria ficou com 187 exemplos.

Categorias mais frequentes no treino processado:

| Categoria | Quantidade |
|---|---:|
| `card_payment_fee_charged` | 187 |
| `direct_debit_payment_not_recognised` | 182 |
| `balance_not_updated_after_cheque_or_cash_deposit` | 181 |
| `wrong_amount_of_cash_received` | 180 |
| `cash_withdrawal_charge` | 177 |

Categorias menos frequentes no treino processado:

| Categoria | Quantidade |
|---|---:|
| `contactless_not_working` | 35 |
| `virtual_card_not_working` | 41 |
| `card_acceptance` | 57 |
| `card_swallowed` | 61 |
| `lost_or_stolen_card` | 82 |

Tamanho das mensagens no treino processado:

| Metrica | Caracteres |
|---|---:|
| Media | 59.48 |
| Mediana | 47 |
| Minimo | 13 |
| Maximo | 433 |

## Limpeza feita

Decisoes:

- mantive apenas `text` e `category`;
- removi espacos no inicio e no fim das mensagens;
- removi 4 linhas duplicadas do treino e 1 do teste que apareceram depois do
  `strip()`;
- nao transformei tudo para minusculo, porque isso pode atrapalhar leitura e
  exemplos futuros;
- nao removi pontuacao, porque pergunta de atendimento costuma usar `?` e isso
  pode ajudar o modelo depois;
- removi do treino 6 mensagens que tambem apareciam no teste quando comparadas
  com `strip().lower()`.

Resultado final:

| Split | Linhas | Colunas |
|---|---:|---:|
| Treino processado | 9993 | 2 |
| Teste processado | 3079 | 2 |

## Graficos

Os graficos ficam em:

- `reports/TP1/figures/banking77_category_distribution.png`
- `reports/TP1/figures/banking77_text_length_distribution.png`

## Hipoteses sobre as intencoes

1. Muitas mensagens giram em torno de cartao: chegada, bloqueio, troca, falha,
   pagamento nao reconhecido e cartao virtual.
2. Transferencia e pagamento devem ser intents importantes, porque aparecem em
   varias categorias separadas: transferencia pendente, falha, taxa, cancelamento
   e destinatario nao recebeu.
3. Parte dos chamados parece ligada a seguranca da conta: identidade, fonte dos
   fundos, aparelho perdido, cartao comprometido e senha/PIN.

Para reproduzir:

```bash
python -m scripts.eda_banking77
```

## Revisão da EDA após o feedback do TP1

O notebook contém os resultados executados de `shape`, `dtypes`, valores ausentes
e `DataFrame.describe(include="all")` para treino e teste originais. Como ambas
as colunas são textuais, o resumo apresenta `count`, `unique`, `top` e `freq`.
O resumo do comprimento das mensagens permanece como análise complementar.

A terceira visualização é `reports/TP1/figures/banking77_text_length_by_category.png`:
boxplots das dez categorias com maior mediana de comprimento no treino limpo.
Ela compara tendência central, dispersão e extremos, sem selecionar categorias
com base no teste. O recorte não representa todas as 77 categorias e não implica
que as categorias com textos longos sejam necessariamente mais difíceis.

Os três gráficos estão incorporados às células do notebook e salvos em PNG.
O notebook mantém as contagens de execução e as saídas para inspeção direta.
BANKING77 classifica intenções; esta EDA não valida um detector de fraude.

Para executar novamente o notebook e salvar seus resultados, na raiz do projeto:

```powershell
uv pip install --python .venv/Scripts/python.exe -r requirements-dev.txt
.\.venv\Scripts\python.exe -m scripts.execute_eda_notebook
```

O executor usa IPython no próprio processo Python, captura tabelas e imagens e
só grava o notebook após todas as células concluírem sem erro. Também é possível
abrir o notebook em um editor com suporte a Jupyter e executar todas as células.
