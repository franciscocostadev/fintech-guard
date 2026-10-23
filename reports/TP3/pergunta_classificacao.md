# Pergunta de classificação — Fintech Guard

Integrante A | TP3 | Revisão: 17/10/2026

## Tarefa e recorte do projeto

**Dado o texto de uma mensagem, seu conteúdo pertence à classe benigno ou apresenta uma ameaça de engenharia social, conforme os rótulos do dataset?** A unidade de análise é uma mensagem; a entrada é texto, e a saída planejada é uma classe de segurança para apoiar triagem.

O Fintech Guard reúne atendimento bancário e proteção contra engenharia social. Este documento adapta a pergunta de intenções do enunciado ao componente de segurança estudado no TP1 e TP2. **Conteúdo ameaçador e intenção do remetente são conceitos distintos:** um cliente legítimo pode relatar ou citar uma tentativa de phishing. O classificador proposto não comprova intenção maliciosa, fraude ou identidade e não autoriza transações.

As classes abaixo não representam pedidos de fatura, cancelamento ou investimento. O roteamento de intenções de atendimento é uma tarefa complementar, que exigiria outro protocolo com BANKING77; as duas bases não serão misturadas. O plano conjunto deve registrar o alinhamento desse recorte com o integrante B e a orientação da disciplina. Não se presume aprovação específica dessa adaptação.

## Dados, classes e distribuição

Fonte: dataset de segurança descrito em `docs/dataset_security.md`. Dos 624 registros reconstruídos, foram excluídas 15 linhas com rótulos conflitantes e seis duplicatas excedentes, restando 603 mensagens em inglês. As definições são operacionais; há sobreposição entre categorias.

| Classe original | Definição operacional | n | % |
|---|---|---:|---:|
| NOT-Malicious General Class | Conteúdo benigno segundo o dataset | 171 | 28,36 |
| Phishing | Indução a fornecer dados ou acessar conteúdo fraudulento | 110 | 18,24 |
| Scareware | Medo ou urgência para induzir uma ação | 100 | 16,58 |
| Baiting | Prêmio ou benefício usado como isca | 80 | 13,27 |
| Malware | Indução a instalar ou executar conteúdo malicioso | 77 | 12,77 |
| Pretexting | Pretexto ou identidade alegada para obter cooperação | 65 | 10,78 |
| **Total** | | **603** | **100,00** |

**Proposta para T2:** classificação binária principal, benigno (171; 28,36%) versus ameaça (432; 71,64%), agrupando as cinco categorias de ameaça. Ameaça será a classe positiva. Essa escolha reduz a fragmentação de uma amostra pequena, mas não elimina desbalanceamento ou ambiguidade. Os seis rótulos originais serão preservados para análise de erros por subtipo. A comparação multiclasse será secundária, condicionada à viabilidade de avaliar cada classe; os 65 exemplos de Pretexting não representam toda a variedade de situações reais.

## Justificativa para aprendizado supervisionado

Existem exemplos rotulados e o conteúdo envolve combinações de termos além da extensão textual. No TP2, o Mann–Whitney resultou em p ≈ 0,1912, com efeito pequeno: não rejeitar H₀ não prova igualdade nem estabelece um limiar útil de detecção. No TP3, a regressão estima caracteres a partir de atributos de extensão; seu R² elevado e seu RMSE baixo refletem relações estruturais entre essas medidas, não desempenho de classificação.

Aplicar regressão linear a códigos de classe imporia ordem e distâncias arbitrárias e não garantiria probabilidades válidas. TF-IDF com regressão logística poderá aprender associações entre termos e rótulos, avaliadas por precisão, recall e F1 por classe. A regressão logística também é um método estatístico: a escolha é de um objetivo categórico supervisionado adequado, em lugar de regressão contínua ou análise descritiva isolada.

## Limites e evidência necessária

Licença ainda não esclarecida, amostra pequena em inglês, possível dependência por templates e ambiguidade Phishing/Pretexting limitam a generalização. A EDA expôs toda a base; o futuro teste interno não será considerado intocado desde a origem. Será necessária avaliação externa independente, com condições de uso e anotações documentadas, próxima do atendimento bancário em português e incluindo relatos legítimos de ameaças. O planejamento detalhado está em `planejamento_T2.md`. Nenhum classificador foi treinado no TP3.
