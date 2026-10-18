# Planejamento técnico de T2 - Dados e IA
Integrante A | TP3 | Revisão: 17/10/2026 | Plano prospectivo, sem treinamento de classificador

## 1. Objetivo e decisão de classes
Propor como tarefa principal benigno versus ameaça, com ameaça positiva, mantendo os seis
rótulos originais para diagnóstico. A justificativa e as contagens estão em
`pergunta_classificacao.md`. Comparação multiclasse é secundária, não requisito para aceitar
um bom resultado binário. Não renomear as classes como intenções bancárias nem misturar BANKING77.

O alvo descreve conteúdo de segurança segundo os rótulos disponíveis. Um cliente legítimo
pode citar uma ameaça, portanto a previsão não prova intenção maliciosa do remetente. O
roteamento de intenções de atendimento constitui uma tarefa complementar, com taxonomia e
avaliação próprias. Antes de consolidar o plano da dupla, registrar o alinhamento deste recorte
com o integrante B e a orientação da disciplina; não há aprovação específica presumida.

## 2. Modelos candidatos e representação textual
Referência mínima: DummyClassifier com estratégia de classe majoritária. Candidato principal:
Pipeline de TF-IDF e LogisticRegression com regularização L2. Comparador: LinearSVC.
Modelos lineares regularizados são uma hipótese inicial compatível com poucos exemplos e
representação esparsa; não se presume que vencerão a referência antes de medir.

Planejar TF-IDF de palavras, unigrams/bigrams, lowercase, sem remover indiscriminadamente
negações, números ou palavras de urgência. Comparar, dentro da validação de treino, com
n-gramas de caracteres (3–5) para variações de escrita. Ajustar vocabulário/IDF exclusivamente
em cada fold de treino. Não traduzir automaticamente a base e tratar a tradução como dado
original independente. Não usar IDs, hashes, categoria ou qualquer informação pós-rótulo como feature.

Grade pequena inicial: C em {0,1; 1; 10}, class_weight em {None; balanced}, min_df em {1; 2};
testar representações em etapas, registrando todas as tentativas. Atributos numéricos de TP2
podem ser uma ablação posterior: comparar texto sozinho versus texto + atributos, evitando
duplicar caracteres/palavras sem justificar. `n_links` permanece excluído se constante.

## 3. Separação e prevenção de vazamento
Antes de treinar, revisar duplicatas exatas e similares, agrupar templates/variações quando
identificáveis e impedir que um grupo apareça em treino e teste. Sem metadados de autores,
independência total não é garantida. Definir e persistir o manifesto e seed antes dos resultados.
Proposta: reservar 20% para teste interno, com estratificação e respeito aos grupos; usar
validação cruzada de cinco folds no restante, reduzindo folds se os grupos/classes inviabilizarem
a composição. Escolher hiperparâmetros e limiar somente no treino/validação.

A partição usada na regressão do TP3 é pedagógica e já avaliada. Não reutilizar seus resultados
para selecionar classificador nem alegar teste externo preservado. A base inteira já passou
pela EDA; obter conjunto externo independente é a evidência necessária de generalização.
O teste interno futuro será aberto uma vez após congelar decisões; mudanças posteriores
exigem registrar a reutilização e nova avaliação independente.

## 4. Métricas, erros e decisão
Reportar matriz de confusão, suporte, precisão, recall e F1 de cada classe, macro-F1 e balanced
accuracy. Para binária, complementar com PR-AUC usando scores adequados e documentar a prevalência;
acurácia isolada pode esconder erros. Relatar média/dispersão dos folds, não apenas o melhor.
Falsos negativos deixam ameaças passar; falsos positivos interrompem atendimento legítimo.
Definir com o integrante B o custo relativo e o limite aceitável de falsos positivos antes de
escolher um limiar; não inventar meta operacional sem dados.

Separar falsos negativos por subtipo original. Em eventual experimento multiclasse, examinar
explicitamente a confusão Phishing/Pretexting. Revisar exemplos apenas de treino/validação
durante desenvolvimento, com registro de mudanças de taxonomia e de decisões. Não corrigir
rótulos do teste em função da previsão; problemas de anotação requerem revisão independente.

## 5. Validação externa e integração futura
Confirmar direitos de uso/redistribuição do dataset, coletar mensagens bancárias em português
com anonimização, consentimento/base de uso adequada e protocolo de anotação. Separar mensagens
reais de sintéticas; estas não substituem avaliação representativa. Incluir relatos legítimos
de golpes e mensagens que citam conteúdo ameaçador, evitando confundir o tema relatado com
intenção maliciosa do cliente. Planejar dupla anotação e adjudicação de casos ambíguos.
Congelar os exemplos externos antes da avaliação final.

Antes de integrar ao agente, alinhar contrato de classes/scores, incerteza e revisão humana,
comprimento máximo (API: 1.000 caracteres na base atual; dataset: até 3.693), idioma, custo e
latência. Não truncar silenciosamente. O modelo será suporte de triagem, sem liberar ações
sensíveis por conta própria. Persistência, autenticação e controles da API são do integrante B.

## 6. Dependências do integrante B - campos obrigatórios do plano conjunto

| Campo | Estado |
|---|---|
| Recorte da pergunta de classificação | PROPOSTO - registrar alinhamento entre segurança de conteúdo e intenções de atendimento |
| Colega adversário | PENDENTE - nome e identificação a confirmar pela dupla |
| URL/IP da API adversária | PENDENTE - não informado; não inferir a partir do GitHub |
| Autorização, escopo e janela de pentest | PENDENTE - alinhar antes de qualquer teste adversarial |
| Testes de segurança, workflow e proteção de merge | Integrante B - validar no TP3 integrado; workflow de Dados no fork não substitui CI de segurança |
| Auditoria final, findings e OpenAPI | Integrante B - atualizar evidências da versão integrada |

Esses campos impedem considerar o plano conjunto completo. A execução histórica de 47 testes
em 14/10/2026 está registrada em `resultado_validacao.md`; a revisão de 17/10 executou
o notebook e aprovou 58 testes em Windows, com evidências próprias em `local_validation/`. Nenhum scan, ataque ou alteração de infraestrutura foi
realizado nesta etapa de Dados.

## 7. Rastreabilidade e fontes
Para cada experimento futuro: pergunta, hipótese, hash dos dados, manifesto, versões, seed,
features, hiperparâmetros, métricas, erros, limitações e decisão. Guardar notebook executado
por TP; manter dataset original e histórico do TP1/TP2.

- [Pipeline e vazamento de dados](https://scikit-learn.org/stable/common_pitfalls.html)
- [TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- [Regressão logística](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- [SVM linear](https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html)
