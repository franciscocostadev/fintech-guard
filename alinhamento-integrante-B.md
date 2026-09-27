# Revisão do material do integrante B

O texto enviado pelo integrante B descreve o README e o estado atual do projeto.
Conferi as informações com o código, os notebooks e os relatórios versionados.
Em geral, estão corretas; há um erro pequeno no comando de login e uma ressalva
sobre a redação da rubrica.

## API e segurança

A descrição da API bate com o código: usa JWT, persiste com SQLModel e filtra as
consultas por ID pelo usuário autenticado. Os headers, a allowlist CORS e o
limite de cinco tentativas por IP em cinco minutos também estão configurados.
Esse limite é mantido em memória, então pressupõe um único worker — ponto que o
texto já informa.

O relatório final do ZAP registra cinco alertas informativos e nenhum alerta
High, Medium ou Low. A evidência da execução está em
[reports/security/zap-final/execution.json](reports/security/zap-final/execution.json).
A saída versionada do pytest registra 37 testes aprovados, incluindo os casos
sem token, de acesso à predição de outro usuário e de envio de campos extras.

## EDA

O texto acerta ao dizer que a EDA avançada ainda falta. O notebook do BANKING77
mostra duas visualizações, mas não tem heatmap, scatter plots ou teste formal de
hipótese com p-valor. Suas células também não guardam outputs. O documento atual
sobre o BANKING77 cobre fonte, dados, limpeza e hipóteses, mas ainda não tem todas
as seções pedidas para o relatório da entrega. O notebook e relatório de
phishing são de outro conjunto e não preenchem essas lacunas.

O parecer recebido menciona três visualizações e uma chamada direta a
`DataFrame.describe()`. Esses dois critérios não aparecem literalmente no
enunciado enviado. O notebook aplica `describe()` aos comprimentos de mensagens
(`Series`), não a todo o dataframe. Se esses requisitos extras vierem de uma
rubrica confirmada pelo professor, acrescente o resumo geral e os gráficos
solicitados. O que o enunciado pede explicitamente — heatmap, scatter plots e
teste de hipótese — continua pendente de qualquer forma.

## Ajuste feito no login

O comando do texto usava `troque-esta-senha`, mas a senha de exemplo em
`.env.example` é `Troque@Esta#Senha123`. Corrigi o comando no README e usei
`--data-urlencode` para enviar a senha corretamente. Se os valores de
`SEED_USERNAME` e `SEED_PASSWORD` foram alterados, o comando deve usar as novas
credenciais.

O material analisado foi preparado pelo integrante B. Esta revisão conferiu os
pontos factuais e não altera a autoria do texto original.

## Uso de IA nesta revisão

O ChatGPT, da OpenAI, ajudou a comparar o texto com o repositório e a registrar
as correções. A atividade pede que esse apoio seja citado. Referência: OpenAI.
(2026). *ChatGPT*. <https://chatgpt.com/>.
