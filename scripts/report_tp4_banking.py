"""Gera o relatório de intenções a partir das evidências salvas; não treina modelos."""
from pathlib import Path
import json

import pandas as pd


def main():
    root=Path(__file__).resolve().parents[1]
    out=root/'reports/TP4'
    metrics=pd.read_csv(out/'banking77/metrics.csv').set_index('model')
    selected=json.loads((out/'banking77/selection.json').read_text(encoding='utf-8'))
    meta=json.loads((root/'models/TP4/banking77/metadata.json').read_text(encoding='utf-8'))
    per_class=pd.read_csv(out/'banking77/per_class_tuned.csv')
    distribution=pd.read_csv(out/'banking77/class_distribution.csv')
    predictions=pd.read_csv(out/'banking77/predictions.csv').query("model == 'tuned'")
    confusion=pd.read_csv(out/'banking77/confusion_pairs.csv')
    table='\n'.join(
        f'| {name} | {row.cv_macro_f1_mean:.4f} ± {row.cv_macro_f1_std:.4f} | {row.test_accuracy:.4f} | '
        f'{row.test_macro_f1:.4f} | {row.test_weighted_f1:.4f} | {row.test_roc_auc_ovr_macro:.4f} |'
        for name,row in metrics.iterrows())
    weak='\n'.join(f'| `{r.intent}` | {r.precision:.4f} | {r.recall:.4f} | {r["f1-score"]:.4f} | {int(r.support)} |'
                   for _,r in per_class.sort_values(['f1-score','intent']).head(10).iterrows())
    pairs='\n'.join(f'| `{r.actual}` | `{r.predicted}` | {r["count"]} |' for _,r in confusion.head(10).iterrows())
    gain_cv=metrics.loc['tuned','cv_macro_f1_mean']-metrics.loc['initial','cv_macro_f1_mean']
    gain_test=metrics.loc['tuned','test_macro_f1']-metrics.loc['initial','test_macro_f1']
    gain_baseline=metrics.loc['tuned','test_macro_f1']-metrics.loc['majority','test_macro_f1']
    errors=int(predictions.error.sum())
    content=f'''# TP4 — Classificação das 77 intenções bancárias

Fintech Guard | Integrante A — Dados e IA | Experimento `{meta['model_version']}`

## 1. Problema, dados e arquitetura

Pergunta: dado o texto de atendimento, qual das **77 solicitações bancárias** ele expressa?
Esse é o classificador principal de intenções do TP4. O [classificador de segurança](classificacao.md)
continua ativo para analisar conteúdo benigno/ameaça; seus rótulos não são intenções bancárias.
Os dois modelos recebem o mesmo texto e devolvem resultados separados, conforme o
[adendo de arquitetura](arquitetura_dupla.md) e o [contrato de integração](contrato_classify.md).
Relatar um golpe não torna o cliente malicioso.

BANKING77 foi disponibilizado pela PolyAI com mensagens em inglês, 77 categorias,
10.003 registros de treino e 3.080 de teste na fonte original. A limpeza histórica do TP1
produziu 9.993/3.079. Os CSVs históricos foram preservados; no TP4, oito linhas do treino
em componentes de similaridade que tocavam o teste foram excluídas do **treino derivado**.
Resultado: **9.985 treino e 3.079 teste**, com as 77 classes presentes em ambos.
Fonte, licença CC BY 4.0 e citação permanecem em [dataset_banking77](../../docs/dataset_banking77.md).

As classes têm entre {int(distribution.train.min())} e {int(distribution.train.max())} exemplos no treino
retido e entre {int(distribution.test.min())} e {int(distribution.test.max())} no teste.
Os rótulos originais, incluindo `Refund_not_showing_up` e `reverted_card_payment?`,
foram preservados. A [distribuição completa](banking77/class_distribution.csv) registra
os 77 rótulos e exclusões; não há renomeação ou concatenação com rótulos de ameaça.

![Distribuição das classes](figures/banking77/distribuicao.png)

O gráfico apresenta as dez classes mais e menos frequentes no treino. A distribuição
é relativamente equilibrada; prever uma única classe cobre aproximadamente 1/77 do teste.

## 2. Protocolo e prevenção de vazamento

O [protocolo](banking77/protocol.json) e o [manifesto](banking77/split_manifest.csv)
foram persistidos antes da avaliação. Cada linha tem ID da fonte, hash do texto, rótulo,
grupo, destino e fold. A [auditoria](banking77/data_audit.json) e as
[oito exclusões](banking77/excluded_training_rows.csv) tornam a preparação rastreável.

Agrupamento sem consultar rótulos: normalização NFKC/casefold/espaços e substituição de
URLs, e-mails e números **somente para comparação**; templates iguais em qualquer tamanho
ou Jaccard ≥0,90 de conjuntos de 5-gramas de caracteres para textos com pelo menos
40 caracteres. Componentes conexos permanecem juntos. O algoritmo de prefixos gera
candidatos, mas a decisão usa a similaridade exata dos conjuntos completos.
Foram identificados 25 pares e 22 componentes com mais de uma linha, sem conflitos de
rótulo. Um componente tem duas linhas no teste preservado. A heurística reduz sobreposição
detectável, mas não prova independência por autor ou ausência de paráfrases.

Removemos do treino todos os componentes que tocavam o teste. As 3.079 linhas de teste,
seus textos e rótulos permaneceram intactos. Não foram usadas previsões para excluir dados.
No treino retido, StratifiedGroupKFold, cinco folds e seed 42, mantém cada grupo em um
único fold; as 77 classes aparecem em todas as partes de ajuste e validação.
TF-IDF aprende vocabulário e IDF **dentro do pipeline de cada fold**. IDs, grupos e hashes
não entram no modelo. O artefato final usa exclusivamente as 9.985 linhas do treino.

O teste já apareceu na EDA: é um benchmark interno do mesmo domínio, não uma amostra
externa inédita. Não houve alteração de grade, features ou limiar em resposta aos seus
erros. Reexecuções idênticas reproduzem este experimento, sem criar nova avaliação independente.

## 3. Pipeline, baseline e otimização

Pipeline scikit-learn: TfidfVectorizer → LogisticRegression multiclasse.
TF-IDF: lowercase, sublinear_tf=True, min_df=2, max_features=30000, sem remoção de stopwords.
Estimador: solver lbfgs, regularização L2, max_iter=1000, random_state=42.
Configuração inicial: C=1 e unigramas/bigramas. Não houve aviso de falha de convergência.

Baseline `DummyClassifier(strategy="prior")`: prevê sempre a classe mais frequente e
retorna a distribuição de classes do treino como scores constantes. A mesma partição
e os mesmos cinco folds permitem comparar baseline, inicial e modelo selecionado.

GridSearchCV testa **C=[0.1,1,10]** e **ngram_range=[(1,1),(1,2),(1,3)]**:
dois parâmetros com três valores cada, nove candidatos, 45 ajustes e refit do vencedor.
A métrica de seleção é macro-F1 médio dos folds, dando o mesmo peso a cada intenção.
Melhor configuração: **C={selected['best_params']['classifier__C']:g},
ngram_range={tuple(selected['best_params']['tfidf__ngram_range'])}**.
Não se usa o teste para escolher parâmetros, limiares ou modelos.

![Busca de hiperparâmetros](figures/banking77/grid.png)

A grade mostra que adicionar n-gramas não garante melhora neste protocolo.
Os [resultados dos nove candidatos](banking77/cv_results.csv) documentam a comparação.
A média do vencedor é selecionada entre candidatos e pode ser otimista;
o desvio padrão dos folds não é intervalo de confiança.

## 4. Avaliação, métricas por classe e erros

| Modelo | Macro-F1 CV (média ± DP) | Acurácia teste | Macro-F1 teste | F1 ponderado teste | ROC-AUC OvR macro |
| --- | --- | --- | --- | --- | --- |
{table}

O ganho sobre a configuração inicial foi **{gain_cv:+.4f} de macro-F1 na CV** e
**{gain_test:+.4f} no teste** (cerca de {100*gain_test:.2f} pontos percentuais).
Sobre a baseline, o ganho no teste foi **{gain_baseline:+.4f}**.
Há aprendizado útil das associações lexicais neste corpus: o resultado supera amplamente
a previsão de uma única classe. Isso não comprova compreensão robusta, adequação ao
português ou desempenho em atendimento bancário real.

O selecionado acertou **{len(predictions)-errors} de {len(predictions)}** mensagens e errou **{errors}**.
A matriz completa tem 77 linhas reais e 77 colunas previstas, na ordem validada de `classes_`.
As probabilidades completas foram guardadas para recalcular ROC-AUC, e a serialização
é verificada contra todas as previsões e scores do teste.

![Matriz de confusão completa](figures/banking77/confusao_completa.png)

Predomínio da diagonal indica acertos, mas há trocas entre serviços próximos. Consulte
a [matriz CSV](banking77/confusion_tuned.csv) para os valores individuais e as
[métricas das 77 classes](banking77/per_class_tuned.csv), também impressas no notebook.
As dez classes com menor F1 são:

| Intenção | Precisão | Recall | F1 | Exemplos no teste |
| --- | --- | --- | --- | --- |
{weak}

![Vinte menores F1 por classe](figures/banking77/f1_menores.png)

O desempenho agregado não substitui a avaliação por intenção. Cada classe tem cerca
de 40 exemplos no teste, de modo que poucos erros alteram bastante seu recall/F1.
Não se apresenta ranking de classes como diferença estatisticamente estabelecida.

| Intenção real | Intenção prevista | Trocas observadas |
| --- | --- | --- |
{pairs}

![Pares mais confundidos](figures/banking77/maiores_confusoes.png)

Há, por exemplo, trocas entre saldo não atualizado após transferência e transferência
não recebida, e entre cartão virtual indisponível e obtenção de cartão descartável.
Proximidade semântica é uma hipótese para futura revisão; a contagem não comprova sua causa.
Esse diagnóstico posterior à avaliação não foi usado para reajustar o modelo neste teste.

ROC-AUC usa scores contínuos e estratégia **One-vs-Rest**: cada classe contra as outras 76.
A média macro é {metrics.loc['tuned','test_roc_auc_ovr_macro']:.6f}; a média ponderada é
{metrics.loc['tuned','test_roc_auc_ovr_weighted']:.6f}. AUC alta mede ordenação dos scores,
**não** a proporção de classificações corretas nem calibração das probabilidades.
Muitos negativos fáceis em cada comparação podem coexistir com confusões entre intenções
semelhantes. Por isso macro-F1 e a matriz são centrais, além de ROC-AUC.

![ROC com agregação micro](figures/banking77/roc_micro.png)

A curva acima agrega as decisões classe versus demais de forma **micro**, apenas como
visualização complementar. Não é uma curva macro. As médias macro/ponderada e AUC por
classe são calculadas separadamente nas tabelas. A baseline tem ROC-AUC OvR 0,5.

## 5. Artefatos, agente e integração

O [modelo serializado](../../models/TP4/banking77/classifier.joblib) contém TF-IDF e estimador.
Os [metadados](../../models/TP4/banking77/metadata.json) registram classes, versões,
hashes e treinamento sem o teste. O [wrapper](../../ml/banking_classifier.py) verifica
integridade e compatibilidade antes de carregar e rejeita entradas inválidas ou acima de
4000 caracteres. Hash de integridade não substitui confiança na origem de um joblib.

`ClassificationService` carrega BANKING77 e segurança uma vez e devolve os dois resultados.
A probabilidade da intenção fica no nível principal; segurança fica em `security` com
scores e versão próprios. Não há soma das probabilidades dos dois modelos.
O [agente](agente.md) utiliza intenção para orientar atendimento e segurança para cuidados,
sem realizar operações financeiras nem presumir que um relato de golpe é intenção maliciosa.

**Pendências:** B integra `/classify` com JWT, startup e contratos OpenAPI; a dupla configura
chave/modelo OpenAI e registra uma conversa real de três turnos. Testes offline não
substituem essa evidência. O [alinhamento com Francisco](alinhamento_francisco.md) detalha
as ações.

## 6. Limitações e próximos passos

- Ambas as bases estão em inglês. Tradução automática não constitui validação em português.
- BANKING77 é de conjunto fechado: o classificador sempre escolhe uma das 77 intenções.
  Não foi validada rejeição de assuntos desconhecidos, aconselhamento de investimentos
  ou conteúdo que não corresponda a uma solicitação bancária.
- Scores não calibrados; argmax não é um limiar validado de segurança ou autorização.
- A coleta e a EDA prévias limitam generalização. Agrupamento heurístico não resolve
  toda dependência entre textos; falta teste externo com direitos de uso e rótulos revisados.
- O componente de segurança mantém suas limitações próprias, incluindo corpus pequeno,
  licença não esclarecida e possível confusão entre relato legítimo e ameaça.

Próximos passos: integrar e testar o contrato real; executar a demonstração; coletar
avaliação externa em português e próxima do uso pretendido; estudar calibração, tratamento
de assuntos desconhecidos e revisão humana com validação própria. Novos experimentos
devem preservar uma avaliação independente, sem otimizar repetidamente neste teste.

## Reprodução e fontes

O [notebook executado](../../notebooks/TP4/banking77/01_classificacao_intencoes.ipynb)
reúne preparação, seleção, avaliação, seis figuras e carregamento do artefato.
Ver [instruções](README.md), [validação atual](validation_dual/README.md) e
[conferência das rubricas](rubricas_TP4.md).
Para regenerar apenas este relatório: `python scripts/report_tp4_banking.py`.

- [BANKING77 — fonte original e licença](https://github.com/PolyAI-LDN/task-specific-datasets#banking).
- [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html).
- [ROC-AUC multiclasse](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html).
- [Boas práticas contra vazamento](https://scikit-learn.org/stable/common_pitfalls.html).
'''
    (out/'classificacao_banking77.md').write_text(content,encoding='utf-8')
    print('Relatório BANKING77 gerado das evidências persistidas; nenhum treinamento realizado.')


if __name__=='__main__':
    main()
