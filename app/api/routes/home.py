from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

router = APIRouter(tags=["home"])


@router.get("/favicon.ico", include_in_schema=False)
async def favicon() -> Response:
    return Response(status_code=204)


@router.get("/", include_in_schema=False, response_class=HTMLResponse)
async def home(request: Request) -> str:
    html = """
<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="color-scheme" content="dark">
  <title>Fintech Guard — Console de Triagem</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 2l7 3v6c0 4.5-3 8.3-7 9-4-0.7-7-4.5-7-9V5z' fill='%235EA0FF'/%3E%3Cpath d='M9 12l2 2 4-4' fill='none' stroke='%230A0D13' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
  <style>
    :root {
      --ink: #0A0D13;
      --ink-grid: rgba(255,255,255,.022);
      --panel: #121823;
      --panel-2: #161E2B;
      --panel-3: #1B2534;
      --line: rgba(255,255,255,.075);
      --line-2: rgba(255,255,255,.14);
      --text: #E9EEF6;
      --text-2: #9BA8BC;
      --text-3: #647084;
      --accent: #5EA0FF;
      --accent-2: #3F7DE0;
      --accent-soft: rgba(94,160,255,.14);
      --benign: #4BCB72;
      --benign-soft: rgba(75,203,114,.14);
      --threat: #FF6961;
      --threat-soft: rgba(255,105,97,.15);
      --warn: #F5B94D;
      --radius: 16px;
      --radius-sm: 11px;
      --radius-xs: 8px;
      --shadow-lg: 0 24px 60px -20px rgba(0,0,0,.72), 0 6px 18px -8px rgba(0,0,0,.55);
      --shadow-md: 0 14px 34px -16px rgba(0,0,0,.6), 0 2px 6px -2px rgba(0,0,0,.5);
      --ease: cubic-bezier(.16,.84,.3,1);
      --font: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      --mono: ui-monospace, "SF Mono", "JetBrains Mono", "Cascadia Code", Menlo, Consolas, monospace;
    }

    * { box-sizing: border-box; }

    html, body {
      height: 100%;
    }

    body {
      margin: 0;
      font-family: var(--font);
      font-size: 15px;
      line-height: 1.5;
      color: var(--text);
      background: var(--ink);
      -webkit-font-smoothing: antialiased;
      text-rendering: optimizeLegibility;
      overflow: hidden;
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      z-index: 0;
      background:
        radial-gradient(1000px 560px at 82% -10%, rgba(94,160,255,.10), transparent 62%),
        radial-gradient(900px 640px at -8% 110%, rgba(75,203,114,.045), transparent 58%);
      pointer-events: none;
    }

    ::selection { background: rgba(94,160,255,.34); color: #fff; }
    ::-webkit-scrollbar { width: 11px; height: 11px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
      background: rgba(255,255,255,.1);
      border: 3px solid transparent;
      border-radius: 99px;
      background-clip: content-box;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,.2); background-clip: content-box; }
    * { scrollbar-width: thin; scrollbar-color: rgba(255,255,255,.14) transparent; }

    :focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 2px;
      border-radius: 4px;
    }

    button, input, textarea { font: inherit; color: inherit; }
    button { cursor: pointer; }

    /* ---------- Brand ---------- */
    .brand { display: inline-flex; align-items: center; gap: 10px; }
    .brand .shield {
      width: 30px; height: 30px; flex: none;
      display: grid; place-items: center;
      color: var(--accent);
    }
    .brand .wordmark { font-weight: 650; font-size: 16px; letter-spacing: -.02em; }
    .brand .wordmark b { color: var(--accent); font-weight: 650; }

    /* ---------- Login ---------- */
    .auth {
      position: relative; z-index: 1;
      min-height: 100svh;
      display: grid; place-items: center;
      padding: 24px;
    }
    /* enquanto a sessão é verificada, não pisca a tela de login */
    html.authed .auth { display: none; }

    .boot {
      position: fixed; inset: 0; z-index: 3;
      display: none; place-items: center;
      background: var(--ink);
    }
    html.authed .boot { display: grid; }
    .boot .shield { width: 46px; height: 46px; color: var(--accent); animation: pulse 1.5s var(--ease) infinite; }
    @keyframes pulse { 0%, 100% { opacity: .35; transform: scale(.985); } 50% { opacity: 1; transform: scale(1); } }
    .auth-card {
      width: 100%; max-width: 408px;
      background: linear-gradient(180deg, var(--panel-2), var(--panel));
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow-lg);
      padding: 34px 32px 30px;
      animation: rise .6s var(--ease) both;
    }
    .auth-card .brand { margin-bottom: 26px; }
    .auth-card .shield { width: 34px; height: 34px; }
    .auth-card .wordmark { font-size: 17px; }
    .auth h1 {
      margin: 0 0 7px;
      font-size: 24px; font-weight: 640; letter-spacing: -.03em;
    }
    .auth .sub { margin: 0 0 26px; color: var(--text-2); font-size: 14px; }

    .field { margin-bottom: 15px; }
    .field label {
      display: block; margin-bottom: 7px;
      font-size: 12.5px; font-weight: 560; letter-spacing: .01em;
      color: var(--text-2);
    }
    .control {
      display: flex; align-items: center;
      background: var(--ink);
      border: 1px solid var(--line-2);
      border-radius: var(--radius-sm);
      transition: border-color .18s, box-shadow .18s, background .18s;
    }
    .control:focus-within {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-soft);
    }
    .control input {
      flex: 1; min-width: 0;
      border: 0; background: transparent;
      padding: 12px 13px; font-size: 15px;
    }
    .control input::placeholder { color: var(--text-3); }
    .control input:focus { outline: none; }
    .ghost-btn {
      border: 0; background: transparent; color: var(--text-3);
      padding: 0 12px; height: 100%; display: grid; place-items: center;
    }
    .ghost-btn:hover { color: var(--text); }
    .ghost-btn svg { width: 18px; height: 18px; display: block; }

    .btn {
      width: 100%;
      display: inline-flex; align-items: center; justify-content: center; gap: 9px;
      border: 1px solid transparent;
      border-radius: var(--radius-sm);
      padding: 12px 16px;
      font-size: 14.5px; font-weight: 600; letter-spacing: -.01em;
      color: var(--ink);
      background: linear-gradient(180deg, #78B0FF, var(--accent));
      box-shadow: 0 12px 26px -14px rgba(0,0,0,.65), inset 0 1px 0 rgba(255,255,255,.28);
      transition: transform .14s var(--ease), box-shadow .18s, filter .18s, opacity .18s;
    }
    .btn:hover { filter: brightness(1.05); box-shadow: 0 16px 30px -12px rgba(0,0,0,.7), inset 0 1px 0 rgba(255,255,255,.28); }
    .btn:active { transform: translateY(1px); }
    .btn[disabled] { opacity: .55; cursor: progress; filter: saturate(.7); }
    .btn .spinner { display: none; }
    .btn.loading .spinner { display: block; }
    .btn.loading .label { opacity: .85; }

    .auth .btn { margin-top: 8px; }

    .spinner {
      width: 16px; height: 16px; flex: none;
      border: 2px solid rgba(10,13,19,.35);
      border-top-color: var(--ink);
      border-radius: 50%;
      animation: spin .7s linear infinite;
    }
    .spinner.light { border-color: rgba(255,255,255,.25); border-top-color: #fff; }

    .notice {
      display: none;
      align-items: flex-start; gap: 9px;
      margin-top: 16px; padding: 11px 13px;
      border-radius: var(--radius-xs);
      font-size: 13.5px; line-height: 1.45;
      border: 1px solid var(--threat-soft);
      background: var(--threat-soft);
      color: #FFC7C3;
    }
    .notice.show { display: flex; animation: rise .32s var(--ease) both; }
    .notice svg { width: 17px; height: 17px; flex: none; margin-top: 1px; }


    /* ---------- App shell ---------- */
    .app { display: none; position: relative; z-index: 1; height: 100svh; flex-direction: column; }
    .app.show { display: flex; }

    .topbar {
      flex: none;
      display: flex; align-items: center; gap: 16px;
      padding: 13px 22px;
      border-bottom: 1px solid var(--line);
      background: rgba(12,16,23,.72);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
    }
    .topbar .spacer { flex: 1; }

    .status-dot {
      display: inline-flex; align-items: center; gap: 7px;
      font-size: 12.5px; color: var(--text-2);
      padding: 5px 11px 5px 9px;
      border: 1px solid var(--line); border-radius: 99px;
    }
    .status-dot .led {
      width: 7px; height: 7px; border-radius: 50%;
      background: var(--text-3); box-shadow: 0 0 0 0 transparent;
      transition: background .3s, box-shadow .3s;
    }
    .status-dot.ok .led { background: var(--benign); }
    .status-dot.down .led { background: var(--threat); }

    .user-chip {
      display: inline-flex; align-items: center; gap: 10px;
      padding: 5px 7px 5px 12px;
      border: 1px solid var(--line); border-radius: 99px;
    }
    .user-chip .who { line-height: 1.15; text-align: right; }
    .user-chip .who .name { font-size: 13px; font-weight: 560; }
    .user-chip .who .role { font-size: 11px; color: var(--accent); letter-spacing: .02em; }
    .avatar {
      width: 30px; height: 30px; border-radius: 50%; flex: none;
      display: grid; place-items: center;
      font-size: 12px; font-weight: 650; color: var(--ink);
      background: linear-gradient(145deg, #8FBCFF, var(--accent));
    }
    .icon-btn {
      display: grid; place-items: center;
      width: 34px; height: 34px;
      border: 1px solid var(--line); border-radius: 9px;
      background: transparent; color: var(--text-2);
      transition: color .16s, border-color .16s, background .16s;
    }
    .icon-btn:hover { color: var(--text); border-color: var(--line-2); background: var(--panel-2); }
    .icon-btn svg { width: 17px; height: 17px; }

    /* ---------- Thread ---------- */
    .thread-wrap { flex: 1; overflow-y: auto; overflow-x: hidden; scroll-behavior: smooth; }
    .thread {
      max-width: 820px; margin: 0 auto;
      min-height: 100%; box-sizing: border-box;
      padding: 30px 22px 18px;
      display: flex; flex-direction: column; gap: 22px;
    }

    .empty {
      margin: auto 0; padding: 48px 20px;
      text-align: center;
      animation: rise .6s var(--ease) both;
    }
    .empty .glyph {
      width: 60px; height: 60px; margin: 0 auto 22px;
      display: grid; place-items: center;
      color: var(--accent);
      border: 1px solid var(--line-2); border-radius: 18px;
      background: radial-gradient(120% 120% at 50% 0%, var(--accent-soft), transparent 70%);
      box-shadow: var(--shadow-md);
    }
    .empty .glyph svg { width: 28px; height: 28px; }
    .empty h2 { margin: 0 0 9px; font-size: 22px; font-weight: 630; letter-spacing: -.03em; }
    .empty p { margin: 0 auto; max-width: 46ch; color: var(--text-2); font-size: 14.5px; line-height: 1.55; }
    .steps {
      display: flex; align-items: center; justify-content: center;
      gap: 12px; margin: 30px auto 0; flex-wrap: wrap;
    }
    .step { display: inline-flex; align-items: center; gap: 9px; font-size: 13px; font-weight: 500; color: var(--text-2); }
    .step .ic {
      width: 32px; height: 32px; flex: none;
      display: grid; place-items: center;
      border: 1px solid var(--line-2); border-radius: 9px;
      color: var(--accent); background: var(--panel);
    }
    .step .ic svg { width: 16px; height: 16px; }
    .steps .sep { width: 26px; height: 1px; background: var(--line-2); flex: none; }
    .empty .hint { margin: 30px auto 0; max-width: 46ch; font-size: 12.5px; color: var(--text-3); line-height: 1.5; }
    @media (max-width: 560px) {
      .steps { flex-direction: column; gap: 12px; }
      .steps .sep { display: none; }
    }

    /* message rows */
    .turn { display: flex; flex-direction: column; gap: 12px; animation: msg-in .5s var(--ease) both; }
    .bubble {
      align-self: flex-end;
      max-width: min(80%, 560px);
      background: linear-gradient(180deg, #2C76E0, var(--accent-2));
      color: #fff;
      padding: 11px 15px;
      border-radius: 16px 16px 5px 16px;
      box-shadow: var(--shadow-md);
      font-size: 14.5px; line-height: 1.5;
      white-space: pre-wrap; overflow-wrap: anywhere;
    }

    .analysis {
      align-self: stretch;
      background: linear-gradient(180deg, var(--panel-2), var(--panel));
      border: 1px solid var(--line);
      border-radius: 5px 16px 16px 16px;
      box-shadow: var(--shadow-md);
      overflow: hidden;
    }
    .analysis-head {
      display: flex; align-items: center; gap: 10px;
      padding: 12px 16px;
      border-bottom: 1px solid var(--line);
      font-size: 12px; font-weight: 560; letter-spacing: .03em; text-transform: uppercase; color: var(--text-3);
    }
    .analysis-head .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); }
    .analysis-body { padding: 18px 16px 16px; display: grid; gap: 18px; }
    @media (min-width: 560px) { .analysis-body { grid-template-columns: 1fr 1fr; } }

    .block .block-label {
      font-size: 11.5px; font-weight: 600; letter-spacing: .05em; text-transform: uppercase;
      color: var(--text-3); margin-bottom: 9px;
    }
    .intent-name {
      font-size: 18px; font-weight: 600; letter-spacing: -.02em;
      line-height: 1.25; margin-bottom: 12px;
      overflow-wrap: anywhere;
    }
    .meter {
      display: flex; align-items: center; gap: 10px;
    }
    .meter .track {
      flex: 1; height: 7px; border-radius: 99px;
      background: rgba(255,255,255,.08); overflow: hidden;
    }
    .meter .fill {
      height: 100%; width: 100%; border-radius: 99px;
      background: linear-gradient(90deg, var(--accent-2), var(--accent));
      transform: scaleX(0); transform-origin: left; transition: transform .9s var(--ease);
    }
    .meter .pct { font-family: var(--mono); font-size: 13px; font-weight: 600; font-variant-numeric: tabular-nums; min-width: 46px; text-align: right; }

    .verdict {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 7px 13px 7px 11px; border-radius: 10px;
      font-size: 13.5px; font-weight: 600; letter-spacing: -.01em;
      margin-bottom: 14px;
    }
    .verdict svg { width: 16px; height: 16px; }
    .verdict.benign { color: var(--benign); background: var(--benign-soft); border: 1px solid rgba(75,203,114,.3); }
    .verdict.threat { color: var(--threat); background: var(--threat-soft); border: 1px solid rgba(255,105,97,.34); }

    .split { display: grid; gap: 7px; }
    .split-row { display: grid; grid-template-columns: 62px 1fr 46px; align-items: center; gap: 10px; font-size: 12.5px; }
    .split-row .k { color: var(--text-2); }
    .split-row .track { height: 6px; border-radius: 99px; background: rgba(255,255,255,.07); overflow: hidden; }
    .split-row .bar { height: 100%; width: 100%; border-radius: 99px; transform: scaleX(0); transform-origin: left; transition: transform .9s var(--ease); }
    .split-row .bar.g { background: var(--benign); }
    .split-row .bar.r { background: var(--threat); }
    .split-row .v { font-family: var(--mono); font-variant-numeric: tabular-nums; text-align: right; color: var(--text-2); }

    .analysis-foot {
      display: flex; flex-wrap: wrap; gap: 6px 14px;
      padding: 11px 16px; border-top: 1px solid var(--line);
      font-size: 11.5px; color: var(--text-3);
    }
    .analysis-foot code { font-family: var(--mono); }

    /* pending */
    .pending { align-self: stretch; display: flex; align-items: center; gap: 11px; color: var(--text-2); font-size: 14px; padding: 4px 2px; }
    .typing { display: inline-flex; gap: 4px; }
    .typing i { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); animation: blink 1.1s var(--ease) infinite; }
    .typing i:nth-child(2) { animation-delay: .18s; }
    .typing i:nth-child(3) { animation-delay: .36s; }

    .flash {
      align-self: stretch; display: flex; align-items: flex-start; gap: 9px;
      padding: 11px 14px; border-radius: 11px; font-size: 13.5px; line-height: 1.5;
      border: 1px solid var(--warn); background: rgba(245,185,77,.12); color: #FBD99A;
    }
    .flash svg { width: 17px; height: 17px; flex: none; margin-top: 1px; }

    /* ---------- Composer ---------- */
    .composer {
      flex: none;
      border-top: 1px solid var(--line);
      background: rgba(12,16,23,.72);
      backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
      padding: 14px 22px calc(14px + env(safe-area-inset-bottom));
    }
    .composer-inner { max-width: 820px; margin: 0 auto; }
    .input-shell {
      display: flex; align-items: flex-end; gap: 10px;
      background: var(--panel);
      border: 1px solid var(--line-2);
      border-radius: 15px;
      padding: 8px 8px 8px 14px;
      transition: border-color .18s, box-shadow .18s;
    }
    .input-shell:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
    .input-shell textarea {
      flex: 1; border: 0; background: transparent; resize: none;
      padding: 7px 0; font-size: 15px; line-height: 1.5;
      max-height: 180px; min-height: 24px;
    }
    .input-shell textarea:focus { outline: none; }
    .input-shell textarea::placeholder { color: var(--text-3); }
    .send {
      flex: none; width: 40px; height: 40px; padding: 0;
      border-radius: 11px; border: 1px solid transparent;
      display: grid; place-items: center;
      color: var(--ink);
      background: linear-gradient(180deg, #78B0FF, var(--accent));
      box-shadow: 0 8px 18px -10px rgba(0,0,0,.55), inset 0 1px 0 rgba(255,255,255,.25);
      transition: transform .14s var(--ease), filter .16s, opacity .16s;
    }
    .send svg { width: 18px; height: 18px; }
    .send:hover { filter: brightness(1.06); }
    .send:active { transform: translateY(1px) scale(.97); }
    .send[disabled] { opacity: .4; cursor: not-allowed; background: var(--panel-3); color: var(--text-3); box-shadow: none; }
    .send .spinner { width: 17px; height: 17px; }

    .composer-meta {
      display: flex; align-items: center; justify-content: space-between;
      margin-top: 8px; padding: 0 4px;
      font-size: 11.5px; color: var(--text-3);
    }
    .composer-meta .count { font-family: var(--mono); font-variant-numeric: tabular-nums; }
    .composer-meta .count.warn { color: var(--warn); }
    .composer-meta .count.over { color: var(--threat); }
    .composer-meta kbd {
      font-family: var(--mono); font-size: 10.5px;
      border: 1px solid var(--line-2); border-radius: 5px;
      padding: 1px 5px; color: var(--text-2);
    }

    @keyframes spin { to { transform: rotate(360deg); } }
    @keyframes blink { 0%, 60%, 100% { opacity: .25; transform: translateY(0); } 30% { opacity: 1; transform: translateY(-2px); } }
    @keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
    @keyframes msg-in { from { opacity: 0; transform: translateY(14px); filter: blur(5px); } to { opacity: 1; transform: none; filter: blur(0); } }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
    }

    @media (max-width: 560px) {
      .topbar { padding: 11px 14px; gap: 10px; }
      .user-chip .who { display: none; }
      .thread { padding: 22px 14px 14px; }
      .composer { padding: 12px 14px calc(12px + env(safe-area-inset-bottom)); }
      .status-dot span.txt { display: none; }
    }
  </style>
  <script>
    // Decide antes da primeira pintura: se há sessão salva, esconde o login
    // (evita o flash "login aparece e some" ao atualizar a aba).
    try { if (sessionStorage.getItem("fg_token")) document.documentElement.classList.add("authed"); } catch (e) {}
  </script>
</head>
<body>
  <div class="boot" id="bootView" aria-hidden="true">
    <span class="shield">
      <svg viewBox="0 0 24 24" fill="none"><path d="M12 2.5l7.5 3.2v5.6c0 4.7-3.2 8.7-7.5 9.4-4.3-.7-7.5-4.7-7.5-9.4V5.7z" fill="currentColor" opacity=".16"/><path d="M12 2.5l7.5 3.2v5.6c0 4.7-3.2 8.7-7.5 9.4-4.3-.7-7.5-4.7-7.5-9.4V5.7z" stroke="currentColor" stroke-width="1.5"/><path d="M8.7 12.2l2.2 2.2 4.4-4.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </span>
  </div>

  <!-- ======= LOGIN ======= -->
  <section class="auth" id="authView">
    <div class="auth-card">
      <div class="brand">
        <span class="shield" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 2.5l7.5 3.2v5.6c0 4.7-3.2 8.7-7.5 9.4-4.3-.7-7.5-4.7-7.5-9.4V5.7z" fill="currentColor" opacity=".16"/><path d="M12 2.5l7.5 3.2v5.6c0 4.7-3.2 8.7-7.5 9.4-4.3-.7-7.5-4.7-7.5-9.4V5.7z" stroke="currentColor" stroke-width="1.5"/><path d="M8.7 12.2l2.2 2.2 4.4-4.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="wordmark">Fintech <b>Guard</b></span>
      </div>

      <h1>Acessar o console</h1>
      <p class="sub">Entre com suas credenciais.</p>

      <form id="loginForm" novalidate>
        <div class="field">
          <label for="username">Usuário</label>
          <div class="control">
            <input id="username" name="username" autocomplete="username" placeholder="ex.: analista" autocapitalize="none" spellcheck="false" required>
          </div>
        </div>
        <div class="field">
          <label for="password">Senha</label>
          <div class="control">
            <input id="password" name="password" type="password" autocomplete="current-password" placeholder="••••••••" required>
            <button type="button" class="ghost-btn" id="togglePw" aria-label="Mostrar senha">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></svg>
            </button>
          </div>
        </div>

        <button type="submit" class="btn" id="loginBtn">
          <span class="spinner" aria-hidden="true"></span>
          <span class="label">Entrar</span>
        </button>
      </form>

      <div class="notice" id="loginNotice" role="alert">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 8v4m0 3.5v.01"/></svg>
        <span id="loginNoticeText"></span>
      </div>
    </div>
  </section>

  <!-- ======= APP ======= -->
  <div class="app" id="appView">
    <header class="topbar">
      <div class="brand">
        <span class="shield" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none"><path d="M12 2.5l7.5 3.2v5.6c0 4.7-3.2 8.7-7.5 9.4-4.3-.7-7.5-4.7-7.5-9.4V5.7z" fill="currentColor" opacity=".16"/><path d="M12 2.5l7.5 3.2v5.6c0 4.7-3.2 8.7-7.5 9.4-4.3-.7-7.5-4.7-7.5-9.4V5.7z" stroke="currentColor" stroke-width="1.5"/><path d="M8.7 12.2l2.2 2.2 4.4-4.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </span>
        <span class="wordmark">Fintech <b>Guard</b></span>
      </div>

      <div class="spacer"></div>

      <div class="status-dot" id="statusDot" title="Status do serviço">
        <span class="led" aria-hidden="true"></span><span class="txt" id="statusTxt">verificando…</span>
      </div>

      <div class="user-chip">
        <div class="who">
          <div class="name" id="userName">—</div>
          <div class="role" id="userRole"></div>
        </div>
        <div class="avatar" id="userAvatar" aria-hidden="true">?</div>
      </div>

      <button class="icon-btn" id="logoutBtn" title="Sair" aria-label="Sair">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M15 17l5-5-5-5M20 12H9M11 4H6a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h5"/></svg>
      </button>
    </header>

    <div class="thread-wrap" id="threadWrap">
      <div class="thread" id="thread" aria-live="polite">
        <div class="empty" id="empty">
          <div class="glyph" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H8l-4 4V6a2 2 0 0 1 2-2h13a2 2 0 0 1 2 2z"/><path d="M9.2 10.5l1.7 1.7 3.9-3.9"/></svg>
          </div>
          <h2>Analise uma mensagem</h2>
          <p>Cole a mensagem de um cliente abaixo. O console identifica a intenção de atendimento e avalia a segurança do conteúdo.</p>
          <div class="steps" aria-hidden="true">
            <div class="step">
              <span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><rect x="8" y="2" width="8" height="4" rx="1"/><path d="M8 4H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2"/></svg></span>
              Cole a mensagem
            </div>
            <span class="sep"></span>
            <div class="step">
              <span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V3h9l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg></span>
              Intenção
            </div>
            <span class="sep"></span>
            <div class="step">
              <span class="ic"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5l7.5 3.2v5.6c0 4.7-3.2 8.7-7.5 9.4-4.3-.7-7.5-4.7-7.5-9.4V5.7z"/><path d="M8.7 12.2l2.2 2.2 4.4-4.6"/></svg></span>
              Segurança
            </div>
          </div>
          <p class="hint">O classificador foi treinado em inglês (BANKING77). Para melhor precisão, envie mensagens em inglês e em frases completas.</p>
        </div>
      </div>
    </div>

    <div class="composer">
      <div class="composer-inner">
        <form id="sendForm">
          <div class="input-shell">
            <textarea id="input" rows="1" maxlength="4000" placeholder="Mensagem do cliente…" aria-label="Mensagem do cliente"></textarea>
            <button type="submit" class="send" id="sendBtn" aria-label="Analisar" disabled>
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M7 11l5-5 5 5M12 6v13"/></svg>
            </button>
          </div>
          <div class="composer-meta">
            <span><kbd>Enter</kbd> envia · <kbd>Shift</kbd>+<kbd>Enter</kbd> quebra linha</span>
            <span class="count" id="count">0 / 4000</span>
          </div>
        </form>
      </div>
    </div>
  </div>

  <script>
    (function () {
      "use strict";

      var TOKEN_KEY = "fg_token";
      var token = "";
      try { token = sessionStorage.getItem(TOKEN_KEY) || ""; } catch (e) { token = ""; }

      var bootView = document.getElementById("bootView");
      var authView = document.getElementById("authView");
      var appView = document.getElementById("appView");

      var loginForm = document.getElementById("loginForm");
      var loginBtn = document.getElementById("loginBtn");
      var loginNotice = document.getElementById("loginNotice");
      var loginNoticeText = document.getElementById("loginNoticeText");
      var usernameEl = document.getElementById("username");
      var passwordEl = document.getElementById("password");
      var togglePw = document.getElementById("togglePw");

      var thread = document.getElementById("thread");
      var threadWrap = document.getElementById("threadWrap");
      var emptyEl = document.getElementById("empty");
      var input = document.getElementById("input");
      var sendForm = document.getElementById("sendForm");
      var sendBtn = document.getElementById("sendBtn");
      var countEl = document.getElementById("count");

      var statusDot = document.getElementById("statusDot");
      var statusTxt = document.getElementById("statusTxt");
      var userName = document.getElementById("userName");
      var userRole = document.getElementById("userRole");
      var userAvatar = document.getElementById("userAvatar");
      var logoutBtn = document.getElementById("logoutBtn");

      var busy = false;

      // ---------- helpers ----------
      function el(tag, cls, text) {
        var n = document.createElement(tag);
        if (cls) n.className = cls;
        if (text != null) n.textContent = text;
        return n;
      }
      function svg(markup) {
        var span = document.createElement("span");
        span.innerHTML = markup; // markup estático, nunca dados do servidor
        return span.firstChild;
      }
      function pct(x) { return Math.round((Number(x) || 0) * 100); }
      function humanize(s) {
        if (!s) return "—";
        var base = String(s).replace(/_/g, " ").replace(/[?]+$/, "");
        return base.charAt(0).toUpperCase() + base.slice(1);
      }
      function roleLabel(r) {
        if (r === "admin") return "Supervisor";
        if (r === "analyst") return "Analista";
        return r ? (r.charAt(0).toUpperCase() + r.slice(1)) : "Operador";
      }
      function scrollDown() { threadWrap.scrollTop = threadWrap.scrollHeight; }

      // ---------- view switching ----------
      function showApp() {
        bootView.style.display = "none";
        authView.style.display = "none";
        appView.classList.add("show");
        input.focus();
      }
      function showAuth(msg) {
        document.documentElement.classList.remove("authed");
        bootView.style.display = "none";
        appView.classList.remove("show");
        authView.style.display = "grid";
        if (msg) notify(msg);
        setLoginLoading(false);
        passwordEl.value = "";
        usernameEl.focus();
      }
      function notify(msg) {
        loginNoticeText.textContent = msg;
        loginNotice.classList.add("show");
      }
      function clearNotice() { loginNotice.classList.remove("show"); }
      function setLoginLoading(on) {
        loginBtn.classList.toggle("loading", on);
        loginBtn.disabled = on;
        loginBtn.querySelector(".label").textContent = on ? "Entrando…" : "Entrar";
      }

      // ---------- auth ----------
      function persist(t) { token = t; try { sessionStorage.setItem(TOKEN_KEY, t); } catch (e) {} }
      function forget() { token = ""; try { sessionStorage.removeItem(TOKEN_KEY); } catch (e) {} }

      loginForm.addEventListener("submit", function (ev) {
        ev.preventDefault();
        clearNotice();
        var u = usernameEl.value.trim();
        var p = passwordEl.value;
        if (!u || !p) { notify("Informe usuário e senha."); return; }

        setLoginLoading(true);
        var body = new URLSearchParams();
        body.set("username", u);
        body.set("password", p);
        body.set("grant_type", "password");

        fetch("/auth/token", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: body.toString()
        }).then(function (res) {
          if (res.status === 429) {
            var ra = res.headers.get("Retry-After");
            throw new Error("Muitas tentativas. Aguarde " + (ra ? ra + "s" : "alguns minutos") + " e tente de novo.");
          }
          return res.json().then(function (data) {
            if (!res.ok) throw new Error(data.detail || "Usuário ou senha inválidos.");
            return data;
          });
        }).then(function (data) {
          persist(data.access_token);
          return loadIdentity();
        }).then(function () {
          clearNotice();
          showApp();
          checkHealth();
        }).catch(function (err) {
          setLoginLoading(false);
          notify(err.message || "Falha ao entrar.");
        });
      });

      togglePw.addEventListener("click", function () {
        var show = passwordEl.type === "password";
        passwordEl.type = show ? "text" : "password";
        togglePw.setAttribute("aria-label", show ? "Ocultar senha" : "Mostrar senha");
        passwordEl.focus();
      });

      logoutBtn.addEventListener("click", function () {
        forget();
        thread.querySelectorAll(".turn, .flash, .pending").forEach(function (n) { n.remove(); });
        emptyEl.style.display = "";
        showAuth();
      });

      function authHeaders(extra) {
        var h = extra || {};
        h["Authorization"] = "Bearer " + token;
        return h;
      }
      function handle401() { forget(); showAuth("Sua sessão expirou. Entre novamente."); }

      function loadIdentity() {
        return fetch("/auth/me", { headers: authHeaders({}) }).then(function (res) {
          if (res.status === 401) { handle401(); throw new Error("sessão expirada"); }
          if (!res.ok) throw new Error("Não foi possível carregar o usuário.");
          return res.json();
        }).then(function (me) {
          var name = me.full_name || me.username || "Usuário";
          userName.textContent = name;
          userRole.textContent = roleLabel(me.role);
          userAvatar.textContent = (name.trim()[0] || "?").toUpperCase();
        });
      }

      function checkHealth() {
        fetch("/health", { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; })
          .then(function (d) {
            if (d && d.status === "ok") { statusDot.className = "status-dot ok"; statusTxt.textContent = "Operacional"; }
            else { statusDot.className = "status-dot down"; statusTxt.textContent = "Degradado"; }
          }).catch(function () { statusDot.className = "status-dot down"; statusTxt.textContent = "Offline"; });
      }

      // ---------- composer ----------
      function autoGrow() {
        input.style.height = "auto";
        input.style.height = Math.min(input.scrollHeight, 180) + "px";
      }
      function updateCount() {
        var n = input.value.length;
        countEl.textContent = n + " / 4000";
        countEl.classList.toggle("warn", n > 3600 && n <= 4000);
        countEl.classList.toggle("over", n >= 4000);
        sendBtn.disabled = busy || input.value.trim().length === 0;
      }
      input.addEventListener("input", function () { autoGrow(); updateCount(); });
      input.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" && !ev.shiftKey) { ev.preventDefault(); sendForm.requestSubmit(); }
      });

      sendForm.addEventListener("submit", function (ev) { ev.preventDefault(); send(); });

      function setBusy(on) {
        busy = on;
        sendBtn.innerHTML = on
          ? '<span class="spinner light" aria-hidden="true"></span>'
          : '<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M7 11l5-5 5 5M12 6v13"/></svg>';
        updateCount();
      }

      function send() {
        if (busy) return;
        var text = input.value;
        if (!text.trim()) return;

        emptyEl.style.display = "none";
        addUserBubble(text);
        input.value = ""; autoGrow(); updateCount();
        setBusy(true);
        var pending = addPending();

        fetch("/classify", {
          method: "POST",
          headers: authHeaders({ "Content-Type": "application/json" }),
          body: JSON.stringify({ text: text })
        }).then(function (res) {
          if (res.status === 401) { pending.remove(); handle401(); throw new Error("sessão expirada"); }
          if (res.status === 429) {
            var ra = res.headers.get("Retry-After");
            pending.remove();
            addFlash("Limite de análises atingido. Aguarde " + (ra ? ra + "s" : "um momento") + " antes de enviar outra mensagem.");
            throw new Error("rate limit");
          }
          return res.json().then(function (data) {
            if (res.status === 422) { pending.remove(); addFlash("Mensagem inválida: precisa ter de 1 a 4000 caracteres."); throw new Error("422"); }
            if (res.status === 503) { pending.remove(); addFlash("O serviço de classificação está indisponível no momento."); throw new Error("503"); }
            if (!res.ok) { pending.remove(); addFlash(data.detail || "Não foi possível analisar a mensagem."); throw new Error("erro"); }
            return data;
          });
        }).then(function (data) {
          pending.remove();
          addAnalysis(data);
        }).catch(function () { /* já tratado acima */ })
          .then(function () { setBusy(false); input.focus(); });
      }

      // ---------- render ----------
      function addUserBubble(text) {
        var turn = el("div", "turn");
        turn.appendChild(el("div", "bubble", text));
        thread.appendChild(turn);
        scrollDown();
        return turn;
      }
      function addPending() {
        var p = el("div", "pending");
        p.appendChild(svg('<span class="typing" aria-hidden="true"><i></i><i></i><i></i></span>'));
        p.appendChild(el("span", null, "Analisando mensagem…"));
        thread.appendChild(p);
        scrollDown();
        return p;
      }
      function addFlash(msg) {
        var f = el("div", "flash");
        f.appendChild(svg('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4m0 3.5v.01"/></svg>'));
        f.appendChild(el("span", null, msg));
        thread.appendChild(f);
        scrollDown();
      }

      function addAnalysis(data) {
        var sec = (data && data.security) || {};
        var probs = sec.probabilities || {};
        var isThreat = sec.label === "threat";

        var card = el("div", "analysis");

        var head = el("div", "analysis-head");
        head.appendChild(svg('<span class="dot" aria-hidden="true"></span>'));
        head.appendChild(el("span", null, "Análise do console"));
        card.appendChild(head);

        var body = el("div", "analysis-body");

        // --- intent block ---
        var b1 = el("div", "block");
        b1.appendChild(el("div", "block-label", "Intenção · BANKING77"));
        b1.appendChild(el("div", "intent-name", humanize(data.intent)));
        var meter = el("div", "meter");
        var track = el("div", "track");
        var fill = el("div", "fill");
        track.appendChild(fill);
        meter.appendChild(track);
        meter.appendChild(el("span", "pct", pct(data.probability) + "%"));
        b1.appendChild(meter);
        body.appendChild(b1);

        // --- security block ---
        var b2 = el("div", "block");
        b2.appendChild(el("div", "block-label", "Segurança do conteúdo"));
        var verdict = el("div", "verdict " + (isThreat ? "threat" : "benign"));
        verdict.appendChild(svg(isThreat
          ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4m0 3.5v.01"/></svg>'
          : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5l7.5 3.2v5.6c0 4.7-3.2 8.7-7.5 9.4-4.3-.7-7.5-4.7-7.5-9.4V5.7z"/><path d="M8.7 12.2l2.2 2.2 4.4-4.6"/></svg>'));
        verdict.appendChild(el("span", null, isThreat ? "Conteúdo suspeito" : "Conteúdo benigno"));
        b2.appendChild(verdict);

        var split = el("div", "split");
        split.appendChild(splitRow("Benigno", probs.benign, "g"));
        split.appendChild(splitRow("Ameaça", probs.threat, "r"));
        b2.appendChild(split);
        body.appendChild(b2);

        card.appendChild(body);

        // --- footer (sem versões de modelo: não expõe pista ao atacante) ---
        var foot = el("div", "analysis-foot");
        foot.appendChild(el("span", null, "Analisado às " + timeNow()));
        card.appendChild(foot);

        var turn = thread.lastElementChild;
        if (turn && turn.classList.contains("turn")) turn.appendChild(card);
        else { var t = el("div", "turn"); t.appendChild(card); thread.appendChild(t); }

        // animate meters after paint
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            fill.style.transform = "scaleX(" + (pct(data.probability) / 100) + ")";
            card.querySelectorAll(".split-row .bar").forEach(function (bar) {
              bar.style.transform = "scaleX(" + (Number(bar.getAttribute("data-w")) / 100) + ")";
            });
          });
        });
        scrollDown();
      }

      function splitRow(label, value, cls) {
        var row = el("div", "split-row");
        row.appendChild(el("span", "k", label));
        var track = el("div", "track");
        var bar = el("div", "bar " + cls);
        bar.setAttribute("data-w", String(pct(value)));
        track.appendChild(bar);
        row.appendChild(track);
        row.appendChild(el("span", "v", pct(value) + "%"));
        return row;
      }
      function timeNow() {
        var d = new Date();
        return d.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
      }

      // ---------- boot ----------
      updateCount();
      if (token) {
        loadIdentity().then(function () { showApp(); checkHealth(); })
          .catch(function () { showAuth(); });
      } else {
        showAuth();
      }
    })();
  </script>
</body>
</html>
"""
    return html.replace("<style>", f'<style nonce="{request.state.csp_nonce}">').replace(
        "<script>", f'<script nonce="{request.state.csp_nonce}">'
    )
