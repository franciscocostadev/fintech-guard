# Documentação do dataset de segurança

## Identificação

- **Nome:** Multiclass NLP Dataset for Phishing and Social Engineering Threat Detection
- **Domínio:** cibersegurança e engenharia social
- **Tarefa:** classificação multiclasse de mensagens
- **Idioma:** inglês
- **Quantidade original:** 624 registros
- **Quantidade tratada:** 603 registros
- **Quantidade de classes:** 6

## Origem e referência

- **Fonte oficial:** https://zenodo.org/records/15235123
- **DOI:** https://doi.org/10.5281/zenodo.15235123
- **Autor institucional:** Engineering Ingegneria Informatica Spa
- **Editores:** Jessica Testa e Marco Angelini
- **Publicação:** 17 de abril de 2025, versão v1
- **Arquivo:** `phishing_nlp_dataset.xlsx`

Referência sugerida pelo registro:

> Engineering Ingegneria Informatica Spa. Multiclass NLP Dataset for Phishing and Social Engineering Threat Detection. Zenodo, 2025. DOI: 10.5281/zenodo.15235123.

O registro informa que as mensagens são anonimizadas e não contêm dados pessoais.

## Licença

O campo de direitos do registro consultado não apresenta uma licença explícita. O acesso ao dataset está aberto no Zenodo, mas acesso aberto não deve ser interpretado automaticamente como autorização para qualquer forma de redistribuição.

Para a continuidade acadêmica do projeto, essa ausência foi documentada como limitação. A confirmação das condições de uso e redistribuição com os responsáveis pelo dataset permanece pendente.

## Atributos utilizados no projeto

| Atributo | Tipo | Significado | Papel no modelo |
|---|---|---|---|
| `text` | string | Conteúdo de uma mensagem semelhante a e-mail ou SMS. | Entrada do classificador. |
| `category` | string | Classe de ameaça ou conteúdo benigno associada à mensagem. | Rótulo que o classificador deverá prever. |

## Classes

| Categoria | Significado no projeto |
|---|---|
| `Phishing` | Mensagem fraudulenta que tenta induzir acesso a links, confirmação de conta ou fornecimento de informações. |
| `Malware` | Mensagem relacionada à indução de instalação, acesso ou execução de conteúdo malicioso. |
| `Scareware` | Mensagem que utiliza medo ou urgência para induzir uma ação. |
| `Baiting` | Mensagem que oferece prêmio, benefício ou oportunidade como isca. |
| `Pretexting` | Mensagem baseada em um pretexto ou identidade alegada para obter informações ou cooperação. |
| `NOT-Malicious General Class` | Mensagem considerada benigna no conjunto original. |

As definições acima orientam a leitura das classes, mas não substituem uma taxonomia formal fornecida pelos autores. A sobreposição semântica observada entre `Phishing` e `Pretexting` é uma limitação do conjunto.

## Localização no projeto

Arquivo original:

- `data/raw/security/phishing_nlp_dataset.xlsx`

Arquivo intermediário reconstruído:

- `data/interim/security/phishing_nlp_dataset.csv`

Arquivo tratado:

- `data/processed/security/phishing_nlp_dataset.csv`

Notebooks por entrega:

- TP1: `notebooks/TP1/security/01_dataset_understanding.ipynb` — análise inicial.
- TP2: `notebooks/TP2/security/01_validacao_e_eda_estatistica.ipynb` — revalidação e aprofundamento estatístico.

## Problema estrutural do arquivo original

Embora o registro do Zenodo descreva as colunas `Corpus` e `Label`, no arquivo analisado 621 rótulos estavam anexados ao final de `Corpus` por um caractere de tabulação. Em outras 3 linhas, mensagens longas estavam divididas entre `Corpus` e `Labels`.

A reconstrução uniu os fragmentos das três mensagens, separou o último campo após tabulação como rótulo e padronizou os nomes para `text` e `category`. O `.xlsx` original foi preservado sem alterações.

## Resultados da EDA

- 624 mensagens reconstruídas;
- 6 categorias;
- nenhum valor ausente;
- nenhum texto ou rótulo vazio;
- nenhum espaço excedente nas extremidades após a reconstrução;
- 9 ocorrências excedentes de duplicatas exatas;
- 24 linhas envolvidas em duplicatas normalizadas;
- 6 textos normalizados com rótulos conflitantes, envolvendo 15 linhas;
- mediana de 99 caracteres por mensagem;
- média de aproximadamente 184,62 caracteres;
- máximo de 3.693 caracteres;
- desbalanceamento moderado, com classes entre 78 e 171 exemplos antes da limpeza.

## Tratamento realizado

Os seis grupos com rótulos contraditórios foram removidos integralmente, totalizando 15 linhas. Essa decisão evita escolher uma categoria correta sem evidência externa.

Depois da remoção dos conflitos, as repetições do mesmo texto normalizado e da mesma categoria foram deduplicadas, removendo 6 ocorrências excedentes. A normalização com `strip()` e `lower()` foi utilizada somente como chave de comparação; capitalização, pontuação e texto original dos registros mantidos foram preservados.

Mensagens longas não foram removidas: o comprimento, por si só, não é evidência de erro de reconstrução ou justificativa para excluir exemplos rotulados como phishing. Nenhum balanceamento foi aplicado nesta etapa.

## Validação final

- 603 registros;
- 2 colunas: `text` e `category`;
- 6 categorias preservadas;
- nenhum valor ausente;
- nenhuma duplicata normalizada restante;
- nenhum texto normalizado associado a categorias diferentes;
- arquivo exportado sem índice do pandas.

## Limitações e próximos passos

- licença não especificada no registro do Zenodo;
- dataset pequeno para uma classificação em 6 classes;
- desbalanceamento moderado;
- proximidade semântica entre algumas ameaças;
- ausência de inspeção manual exaustiva de todas as mensagens.

Antes do treinamento, o conjunto deverá ser dividido de forma estratificada. Técnicas de balanceamento, se necessárias, deverão ser aplicadas somente ao treino. O desempenho deverá ser avaliado com Accuracy, Precision, Recall, F1-score por classe e matriz de confusão.

## Revalidação no TP2 — 23/09/2026

Reconstrução e limpeza reproduzidas: **624 − 15 − 6 = 603 mensagens**. Excel preservado e CSVs existentes idênticos em valores e ordem. O MD5 local coincide com o publicado no [Zenodo](https://zenodo.org/records/15235123): `7213a3ee515a713f4eee2a6948f1756e`. O campo de licença da página consultada continua sem identificação explícita.

| Categoria | Antes | Conflitos excluídos | Duplicatas excluídas | Depois | % final |
|---|---:|---:|---:|---:|---:|
| Baiting | 80 | 0 | 0 | 80 | 13,27% |
| Malware | 78 | 0 | 1 | 77 | 12,77% |
| NOT-Malicious General Class | 171 | 0 | 0 | 171 | 28,36% |
| Phishing | 117 | 7 | 0 | 110 | 18,24% |
| Pretexting | 78 | 8 | 5 | 65 | 10,78% |
| Scareware | 100 | 0 | 0 | 100 | 16,58% |
| **Total** | **624** | **15** | **6** | **603** | **100%** |

A auditoria completa está em `reports/TP2/security_validation/row_audit.csv`; as exclusões estão em `excluded_rows.csv`. A preservação se refere ao texto **após a reconstrução**, que junta fragmentos com um espaço e aplica `strip()`. A escolha por excluir todos os rótulos conflitantes evita arbitrar classes, mas remove casos ambíguos e pode tornar uma avaliação futura mais fácil.

Reprodução: `python -m scripts.validate_security_dataset` e `python -m scripts.execute_security_notebook`. O relatório do TP2 fica em `reports/TP2/relatorio_eda.md`.
