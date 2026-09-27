"""Headers inclusive em erros e limitação antes do processamento do login."""

import secrets

from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send


def security_headers(nonce: str, *, docs: bool = False) -> dict[str, str]:
    # HTML local usa nonce por resposta; a UI Swagger só existe em desenvolvimento.
    styles = " https://cdn.jsdelivr.net" if docs else ""
    csp = (
        "default-src 'none'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' 'nonce-{nonce}'{styles}; "
        "img-src 'self' data:; connect-src 'self'; font-src 'self'; "
        "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; "
        "form-action 'self'"
    )
    return {
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": csp,
        "Referrer-Policy": "no-referrer",
        "Cache-Control": "no-store",
    }


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        nonce = secrets.token_urlsafe(32)
        scope.setdefault("state", {})["csp_nonce"] = nonce

        async def secured_send(message: Message):
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.update(security_headers(nonce, docs=scope["path"] == "/docs"))
            await send(message)

        await self.app(scope, receive, secured_send)


class LoginRateLimitMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if (scope["type"] == "http" and scope["method"] == "POST"
                and scope["path"].rstrip("/") == "/auth/token"):
            # Nunca lê X-Forwarded-For diretamente. Uvicorn deve confiar apenas
            # em proxies conhecidos (ou usar --no-proxy-headers no acesso direto).
            client = scope.get("client")
            key = client[0] if client else "unknown"
            retry_after = scope["app"].state.login_limiter.consume(key)
            if retry_after:
                response = JSONResponse(
                    status_code=429,
                    content={"detail": "Muitas tentativas de login. Tente novamente mais tarde."},
                    headers={"Retry-After": str(retry_after)},
                )
                return await response(scope, receive, send)
        await self.app(scope, receive, send)
