# Revisão do documento do integrante B

**Data da revisão:** 27 de setembro de 2026

**Material analisado:** texto anexado com a versão proposta do README

**Resultado:** conteúdo em geral alinhado ao repositório; um exemplo de login foi corrigido. As lacunas da EDA estão corretamente identificadas.

Esta revisão compara o material preparado pelo integrante B com o código, os
notebooks e as evidências versionadas. O conteúdo do anexo é atribuído ao
integrante B; esta página registra as verificações e a correção identificada.

## Conferência das afirmações

| Assunto | Verificação no repositório | Resultado |
| --- | --- | --- |
| API com JWT e classificação por regras | Implementados em `app/core/security.py` e `app/services/predictor.py`. Não há modelo de machine learning treinado. | Alinhado. |
| SQLModel e ownership nas consultas por ID | `GET /predictions/{prediction_id}` filtra simultaneamente pelo ID e pelo usuário autenticado. | Alinhado. |
| Headers e CORS | Middleware define HSTS, X-Frame-Options, X-Content-Type-Options e CSP. CORS usa uma lista explícita de origens configuradas. | Alinhado. |
| Limite do login | `/auth/token` limita 5 tentativas por IP em 300 segundos. O contador em memória exige um worker e essa limitação está documentada. | Alinhado; convém manter a ressalva de um worker. |
| Resultado do ZAP | O relatório do scan passivo final registra 0 findings High, Medium ou Low e 5 alertas Informational. | Alinhado com `reports/security/zap-final/execution.json`. |
| Testes | A evidência versionada registra 37 testes aprovados. Há casos de token ausente, tentativa de acesso a predição alheia e campo extra. | Alinhado com `reports/security/pytest.txt` e `tests/`. |
| Estado da EDA BANKING77 | O notebook tem checagens iniciais, dois gráficos e hipóteses qualitativas. As células não têm outputs salvos; não há heatmap, scatter plot nem teste formal com p-valor. | Correto indicar esses itens como pendentes. |
| Relatório da EDA BANKING77 | `docs/dataset_banking77.md` resume fonte, colunas, limpeza, gráficos e hipóteses; não contém todas as seções de relatório pedidas nesta entrega. | Lacuna corretamente apontada. O relatório de phishing é de outro dataset. |
| Declaração de uso de IA | A versão atual do README tem uma declaração e referência ao ChatGPT. | Alinhado com a instrução de citar ferramentas de IA. |

## Correção aplicada ao exemplo de login

O texto anexado usava `password=troque-esta-senha`, que não corresponde ao
`SEED_PASSWORD` de exemplo (`Troque@Esta#Senha123`) em `.env.example`. O valor
foi corrigido no README. No banco recém-criado sem alterar os valores do arquivo
de exemplo, o login é:

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  --data-urlencode 'username=analista' \
  --data-urlencode 'password=Troque@Esta#Senha123'
```

Use as credenciais configuradas em `SEED_USERNAME` e `SEED_PASSWORD` se tiver
alterado `.env`. Para produção, substitua sempre os valores de desenvolvimento.

## Itens que continuam pendentes na entrega

O texto do integrante B não deve apresentar a EDA avançada como concluída. Para
fechar a rubrica ainda é preciso:

1. Acrescentar ao notebook do BANKING77 o heatmap de correlação, scatter plots e
   um teste de hipótese (t-test ou Mann–Whitney via SciPy), com hipótese, p-valor
   e interpretação acessível.
2. Executar o notebook e salvar suas saídas, inclusive dimensões, tipos, valores
   ausentes, estatísticas descritivas e gráficos.
3. Completar um relatório `.md` ou `.pdf` próprio para o BANKING77 com problema,
   dados, análise, insights principais, limitações e próximos passos do
   classificador.

O texto apresentado pelo integrante descreve corretamente as lacunas principais
em vez de alegar que a EDA avançada já está pronta. O requisito de declarar o uso
de IA deve permanecer na entrega; ele já aparece no README.

### Precisão em relação à rubrica enviada

O enunciado colado exige heatmap de correlação, scatter plots e um teste de
hipótese formal. Esses requisitos explícitos faltam no notebook do BANKING77.
O parecer recebido também menciona um mínimo de três visualizações e uma chamada
literal a `DataFrame.describe()`, mas essas exigências não aparecem com essas
palavras no enunciado colado. O notebook calcula `describe()` para os comprimentos
das mensagens (`Series`), não para o dataframe inteiro. Se o docente confirmar
que os dois critérios extras pertencem à rubrica oficial, vale adicionar também
um resumo `DataFrame.describe(include="all")` e garantir ao menos três gráficos
no notebook do BANKING77. O segundo notebook contém gráficos de outro dataset e
não substitui os gráficos pedidos para o BANKING77.
