from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response

router = APIRouter(tags=["home"])


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)


@router.get("/", include_in_schema=False, response_class=HTMLResponse)
async def home() -> str:
    return """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Fintech Guard</title>
  <style>
    body {
      margin: 0;
      background: #fff;
      color: #222;
      font-family: Arial, Helvetica, sans-serif;
      font-size: 15px;
    }

    .page {
      max-width: 980px;
      margin: 28px auto;
      padding: 0 18px;
    }

    header {
      border-bottom: 1px solid #bbb;
      padding-bottom: 12px;
      margin-bottom: 18px;
    }

    h1 {
      margin: 0 0 6px;
      font-size: 24px;
      font-weight: 700;
      letter-spacing: 0;
    }

    .muted { color: #555; }

    nav { margin-top: 10px; }
    nav a { margin-right: 14px; }
    a { color: #0645ad; }

    .grid {
      display: grid;
      grid-template-columns: 300px 1fr;
      gap: 18px;
      align-items: start;
    }

    fieldset {
      border: 1px solid #aaa;
      padding: 14px 16px 16px;
      margin: 0 0 16px;
      background: #fafafa;
    }

    legend {
      padding: 0 5px;
      font-weight: 700;
    }

    label {
      display: block;
      margin: 11px 0 5px;
      font-weight: 700;
      color: #333;
    }

    input, textarea, select {
      width: 100%;
      border: 1px solid #aaa;
      border-radius: 2px;
      background: #fff;
      color: #222;
      font: inherit;
      padding: 8px;
    }

    textarea {
      min-height: 110px;
      resize: vertical;
    }

    button {
      margin-top: 12px;
      border: 1px solid #666;
      border-radius: 2px;
      background: #e9e9e9;
      color: #111;
      padding: 7px 12px;
      font: inherit;
      cursor: pointer;
    }

    button:hover { background: #ddd; }

    .msg {
      margin-top: 10px;
      min-height: 20px;
    }

    .ok { color: #176a2c; }
    .erro { color: #9f1d1d; }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      background: #fff;
    }

    th, td {
      border: 1px solid #aaa;
      padding: 8px;
      text-align: left;
      vertical-align: top;
    }

    th {
      width: 150px;
      background: #eee;
      font-weight: 700;
    }

    .raw {
      margin-top: 12px;
      border: 1px solid #aaa;
      padding: 10px;
      background: #f7f7f7;
      font-family: Consolas, Monaco, monospace;
      font-size: 13px;
      white-space: pre-wrap;
      overflow-wrap: anywhere;
    }

    @media (max-width: 760px) {
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="page">
    <header>
      <h1>Fintech Guard</h1>
      <nav>
        <a href="/health">/health</a>
        <a href="/docs">/docs</a>
      </nav>
    </header>

    <div class="grid">
      <aside>
        <fieldset>
          <legend>Status</legend>
          <button id="btnHealth" type="button">Consultar health</button>
          <div id="healthMsg" class="msg muted">Ainda não consultado.</div>
        </fieldset>

        <fieldset>
          <legend>Login</legend>
          <form id="loginForm">
            <label for="username">Usuário</label>
            <input id="username" name="username" autocomplete="username" value="analista">

            <label for="password">Senha</label>
            <input id="password" name="password" type="password" autocomplete="current-password" value="Troque@Esta#Senha123">

            <button type="submit">Gerar token</button>
          </form>
          <div id="loginMsg" class="msg muted">Sem token.</div>
        </fieldset>
      </aside>

      <main>
        <fieldset>
          <legend>Predict</legend>
          <form id="predictForm">
            <label for="message">Mensagem do cliente</label>
            <textarea id="message" name="message">Meu cartão foi bloqueado, como desbloqueio?</textarea>

            <label for="channel">Canal</label>
            <select id="channel" name="channel">
              <option value="chat">chat</option>
              <option value="whatsapp">whatsapp</option>
              <option value="email">email</option>
              <option value="telefone">telefone</option>
            </select>

            <button type="submit">Enviar para /predict</button>
          </form>

          <div id="predictMsg" class="msg muted">Nenhuma requisição enviada.</div>
          <div id="result"></div>
        </fieldset>
      </main>
    </div>
  </div>

  <script>
    let token = localStorage.getItem("fg_token") || "";

    const healthMsg = document.querySelector("#healthMsg");
    const loginMsg = document.querySelector("#loginMsg");
    const predictMsg = document.querySelector("#predictMsg");
    const result = document.querySelector("#result");

    function setMsg(el, text, type) {
      el.className = "msg " + (type || "muted");
      el.textContent = text;
    }

    function renderResult(data) {
      const rows = [
        ["intent", data.intent],
        ["confidence", data.confidence],
        ["risk_level", data.risk_level],
        ["model_version", data.model_version],
        ["detail", data.detail]
      ];

      result.innerHTML = `
        <table>
          <tbody>
            ${rows.map(([key, value]) => `<tr><th>${key}</th><td>${value ?? ""}</td></tr>`).join("")}
          </tbody>
        </table>
        <div class="raw">${JSON.stringify(data, null, 2)}</div>
      `;
    }

    async function checkHealth() {
      setMsg(healthMsg, "Consultando...", "muted");
      try {
        const response = await fetch("/health", { cache: "no-store" });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Falha no health.");
        setMsg(healthMsg, `${data.status} - banco ${data.database}`, data.status === "ok" ? "ok" : "erro");
      } catch (error) {
        setMsg(healthMsg, error.message, "erro");
      }
    }

    async function login(event) {
      event.preventDefault();
      setMsg(loginMsg, "Enviando credenciais...", "muted");

      try {
        const form = new FormData(event.currentTarget);
        const response = await fetch("/auth/token", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams(form)
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Login recusado.");

        token = data.access_token;
        localStorage.setItem("fg_token", token);
        setMsg(loginMsg, "Token gerado.", "ok");
      } catch (error) {
        setMsg(loginMsg, error.message, "erro");
      }
    }

    async function predict(event) {
      event.preventDefault();
      if (!token) {
        setMsg(predictMsg, "Gere o token antes.", "erro");
        return;
      }

      setMsg(predictMsg, "Enviando...", "muted");
      result.innerHTML = "";

      try {
        const response = await fetch("/predict", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            message: document.querySelector("#message").value,
            channel: document.querySelector("#channel").value
          })
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Erro no /predict.");

        setMsg(predictMsg, "Resposta recebida.", "ok");
        renderResult(data);
      } catch (error) {
        setMsg(predictMsg, error.message, "erro");
      }
    }

    document.querySelector("#btnHealth").addEventListener("click", checkHealth);
    document.querySelector("#loginForm").addEventListener("submit", login);
    document.querySelector("#predictForm").addEventListener("submit", predict);
  </script>
</body>
</html>
"""
