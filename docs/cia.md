# CIA - Fintech Guard

Analise usando a triade CIA:

- **Confidencialidade:** dado que nao deve vazar.
- **Integridade:** dado ou processo que nao pode ser alterado de forma indevida.
- **Disponibilidade:** parte que precisa continuar funcionando.

## P1 - Login (`POST /auth/token`)

| CIA | Aplicacao no componente |
|---|---|
| Confidencialidade | A senha do usuario e a `SECRET_KEY` precisam ficar protegidas. A senha nao fica em log e no banco fica apenas o hash bcrypt. |
| Integridade | O token precisa ser assinado e validado. O codigo usa JWT com algoritmo definido e validade curta. |
| Disponibilidade | O login precisa continuar funcionando, mas sem aceitar tentativa infinita. Por isso existe limite de tentativas por IP. |

## P2 - Validacao do token

| CIA | Aplicacao no componente |
|---|---|
| Confidencialidade | O JWT nao deve carregar CPF, saldo ou texto do cliente. Ele guarda apenas dados basicos, como usuario e permissao. |
| Integridade | A API verifica a assinatura do token e consulta se o usuario ainda esta ativo no banco. |
| Disponibilidade | A validacao precisa ser rapida, porque acontece em toda rota protegida. |

## P3 - Predict (`POST /predict`)

| CIA | Aplicacao no componente |
|---|---|
| Confidencialidade | A mensagem do cliente pode ter dados sensiveis. A API nao salva o texto original, apenas o hash da mensagem. |
| Integridade | A entrada passa por schema Pydantic. Cada chamada gera registro em `prediction_logs`, com usuario, hash, intencao e horario. |
| Disponibilidade | A rota limita o tamanho da mensagem para evitar entradas muito grandes. |

## P4 - Health (`GET /health`)

| CIA | Aplicacao no componente |
|---|---|
| Confidencialidade | O health nao mostra string de conexao, caminho de arquivo ou detalhes internos do servidor. |
| Integridade | A rota faz um `SELECT 1` no banco para indicar se ele esta respondendo. |
| Disponibilidade | A rota e publica para facilitar teste local e monitoramento simples. |

## D1 - Tabela `users`

| CIA | Aplicacao no componente |
|---|---|
| Confidencialidade | A senha nao e salva em texto puro. O campo exposto para a API nao inclui `hashed_password`. |
| Integridade | `username` e unico. A aplicacao usa SQLAlchemy, evitando montar SQL manualmente. |
| Disponibilidade | Sem essa tabela o login nao funciona. Em um ambiente real seria necessario backup. |

## D2 - Tabela `prediction_logs`

| CIA | Aplicacao no componente |
|---|---|
| Confidencialidade | A tabela guarda hash da mensagem, nao a mensagem completa do cliente. |
| Integridade | O log registra quem chamou, quando chamou e qual intencao foi retornada. |
| Disponibilidade | Os registros ajudam na auditoria. Em producao seria preciso definir retencao e backup. |

## D3 - Logs da aplicacao

| CIA | Aplicacao no componente |
|---|---|
| Confidencialidade | Os logs nao devem guardar senha, token ou texto da mensagem do cliente. |
| Integridade | Os logs ajudam a entender falhas e tentativas de login. |
| Disponibilidade | Em producao seria preciso rotacionar logs para nao encher o disco. |

## D4 - `.env` e segredos

| CIA | Aplicacao no componente |
|---|---|
| Confidencialidade | A `SECRET_KEY` fica no `.env`, que nao vai para o git. |
| Integridade | A aplicacao recusa chave fraca ou igual ao exemplo. |
| Disponibilidade | Sem a chave a API nao consegue gerar nem validar tokens. |

## Fronteira futura com modelo de classificacao

Nesta entrega o classificador usa regras simples. Se depois entrar um modelo de
classificacao, a mensagem do cliente passa a ser um ponto mais sensivel.

| CIA | Cuidado necessario |
|---|---|
| Confidencialidade | Remover ou mascarar CPF, cartao e outros dados antes de mandar para o modelo. |
| Integridade | Conferir se a resposta do modelo esta dentro das intencoes esperadas. |
| Disponibilidade | Tratar erro ou demora do modelo sem derrubar a API. |

## Resumo

| Pergunta | Resposta curta |
|---|---|
| O que e confidencial? | senha, hash de senha, `SECRET_KEY`, token JWT e mensagem do cliente. |
| O que precisa de integridade? | token, usuario, regra de classificacao e registros em `prediction_logs`. |
| O que precisa estar disponivel? | `/health`, `/auth/token`, `/predict` e banco de dados. |
