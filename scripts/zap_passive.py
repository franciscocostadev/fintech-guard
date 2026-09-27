"""Scan passivo real, com API/banco descartáveis e ZAP em modo safe.

Uso: python -m scripts.zap_passive --zap /tmp/ZAP_2.17.0/zap.sh
Não usa active scan, spider, fuzzing, nem importa OpenAPI para gerar ataques.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import time

import httpx

ROOT = Path(__file__).resolve().parents[1]


def wait_until(check, seconds=120):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        try:
            if check():
                return
        except (httpx.HTTPError, ValueError, KeyError):
            pass
        time.sleep(0.5)
    raise RuntimeError("Timeout aguardando serviço/scan passivo.")


def terminate(process):
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zap", type=Path, required=True)
    parser.add_argument("--app-dir", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "reports/security/zap-final")
    parser.add_argument("--baseline", action="store_true", help="Aceita comportamento da versão anterior aos controles.")
    parser.add_argument("--api-port", type=int, default=18000)
    parser.add_argument("--zap-port", type=int, default=18080)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    app_dir = args.app_dir.resolve()
    base = f"http://127.0.0.1:{args.api_port}"
    zap_url = f"http://127.0.0.1:{args.zap_port}"
    started = datetime.now(timezone.utc).isoformat()
    coverage = []
    api_process = zap_process = None

    with tempfile.TemporaryDirectory(prefix="fintech-zap-") as temporary:
        work = Path(temporary)
        password = secrets.token_urlsafe(24)
        env = {
            **os.environ,
            "SECRET_KEY": secrets.token_urlsafe(64),
            "DATABASE_URL": f"sqlite:///{work / 'scan.db'}",
            "ENVIRONMENT": "development",
            "CORS_ORIGINS": "http://localhost:3000,http://127.0.0.1:3000",
            "LOGIN_MAX_ATTEMPTS": "5", "LOGIN_WINDOW_SECONDS": "300",
            "SEED_USERNAME": "scan_owner", "SEED_PASSWORD": password,
        }
        api_key = secrets.token_urlsafe(32)
        sensitive_values = [api_key, password]
        zap_config = work / "zap.properties"
        zap_config.write_text(f"api.key={api_key}\n")
        zap_config.chmod(0o600)
        with (output / "api.log").open("w") as api_log, (output / "zap.log").open("w") as zap_log:
            try:
                for username in ("scan_owner", "scan_other"):
                    subprocess.run(
                        [sys.executable, "-m", "scripts.seed"], cwd=app_dir,
                        env={**env, "SEED_USERNAME": username}, check=True,
                        stdout=api_log, stderr=subprocess.STDOUT,
                    )
                api_process = subprocess.Popen(
                    [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
                     "--port", str(args.api_port), "--workers", "1", "--no-proxy-headers", "--no-server-header"],
                    cwd=app_dir, env=env, stdout=api_log, stderr=subprocess.STDOUT,
                )
                zap_process = subprocess.Popen(
                    ["bash", str(args.zap.resolve()), "-daemon", "-silent", "-host", "127.0.0.1",
                     "-port", str(args.zap_port), "-dir", str(work / "zap-home"),
                     "-configfile", str(zap_config), "-config", "autoupdate.checkOnStart=false",
                     "-config", "autoupdate.installAddonUpdates=false",
                     "-config", "autoupdate.installScannerRules=false"],
                    stdout=zap_log, stderr=subprocess.STDOUT,
                )
                with httpx.Client(timeout=15, trust_env=False) as control:
                    def zap(component, kind, action, **params):
                        response = control.get(f"{zap_url}/JSON/{component}/{kind}/{action}/",
                                               params={"apikey": api_key, **params})
                        response.raise_for_status()
                        result = response.json()
                        if "code" in result:
                            raise RuntimeError(f"ZAP API error: {result}")
                        return result

                    wait_until(lambda: control.get(base + "/health").status_code == 200)
                    wait_until(lambda: "version" in zap("core", "view", "version"))
                    zap("core", "action", "setMode", mode="safe")
                    assert zap("core", "view", "mode")["mode"] == "safe"
                    zap("pscan", "action", "setEnabled", enabled="true")
                    zap("pscan", "action", "enableAllScanners")
                    version = zap("core", "view", "version")["version"]
                    scanners = zap("pscan", "view", "scanners")["scanners"]
                    assert scanners, "Nenhuma regra passiva instalada."
                    print(f"ZAP {version}: modo safe, {len(scanners)} regras passivas", flush=True)

                    with httpx.Client(proxy=zap_url, timeout=30, trust_env=False, follow_redirects=False) as traffic:
                        def request(method, path, expected=None, **kwargs):
                            response = traffic.request(method, base + path, **kwargs)
                            coverage.append({"method": method, "path": path, "status": response.status_code})
                            if expected is not None:
                                assert response.status_code == expected, (method, path, response.status_code)
                            return response

                        for path in ("/", "/health", "/docs", "/redoc", "/openapi.json", "/favicon.ico", "/missing"):
                            request("GET", path)
                        request("GET", "/auth/me", 401)
                        request("POST", "/predict", 401, json={"message": "Cartão bloqueado"})
                        request("GET", "/predictions/1", 404 if args.baseline else 401)
                        tokens = []
                        for username in ("scan_owner", "scan_other"):
                            login = request("POST", "/auth/token", 200, data={"username": username, "password": password})
                            tokens.append(login.json()["access_token"])
                            sensitive_values.append(tokens[-1])
                        owner, other = [{"Authorization": f"Bearer {token}"} for token in tokens]
                        request("GET", "/auth/me", 200, headers=owner)
                        result = request("POST", "/predict", 200, headers=owner,
                                         json={"message": "Cartão bloqueado", "channel": "chat"}).json()
                        if not args.baseline:
                            path = f"/predictions/{result['id']}"
                            request("GET", path, 200, headers=owner)
                            request("GET", path, 404, headers=other)
                            request("GET", "/predictions/99999999", 404, headers=owner)
                        request("POST", "/predict", 200 if args.baseline else 422, headers=owner,
                                json={"message": "Teste sintético", "role": "admin"})
                        request("POST", "/predict", 422, headers=owner, json={"message": ""})
                        request("POST", "/auth/token", 200 if args.baseline else 422,
                                data={"username": "scan_owner", "password": password, "role": "admin"})
                        request("POST", "/auth/token", 401, data={"username": "scan_owner", "password": "wrong"})
                        request("POST", "/auth/token", 401, data={"username": "scan_owner", "password": "wrong"})
                        if not args.baseline:
                            request("POST", "/auth/token", 429, data={"username": "scan_owner", "password": password})
                        for origin, expected in (("http://localhost:3000", 200), ("https://evil.example", 400)):
                            request("OPTIONS", "/predict", expected, headers={
                                "Origin": origin, "Access-Control-Request-Method": "POST",
                                "Access-Control-Request-Headers": "Authorization,Content-Type",
                            })
                            request("GET", "/health", 200, headers={"Origin": origin})

                    # Fila vazia não basta: uma regra pode já ter retirado a
                    # última mensagem e ainda estar trabalhando nela.
                    def passive_idle():
                        return (
                            int(zap("pscan", "view", "recordsToScan")["recordsToScan"]) == 0
                            and not zap("pscan", "view", "currentTasks")["currentTasks"]
                        )
                    wait_until(passive_idle)
                    time.sleep(1)
                    wait_until(passive_idle)
                    assert zap("ascan", "view", "scans")["scans"] == []
                    assert zap("spider", "view", "scans")["scans"] == []
                    for extension in ("json", "html"):
                        response = control.get(f"{zap_url}/OTHER/core/other/{extension}report/", params={"apikey": api_key})
                        response.raise_for_status()
                        (output / f"report.{extension}").write_bytes(response.content)
                    alerts = zap("core", "view", "alerts", baseurl=base)["alerts"]
                    (output / "alerts.json").write_text(json.dumps(alerts, indent=2) + "\n")
                    # Relatórios nativos não incluem a sessão/proxy history nem
                    # os bodies de login, que contêm as credenciais descartáveis.
                    risk_counts = Counter(alert["risk"] for alert in alerts)
                    summary = {
                        "started_at": started, "finished_at": datetime.now(timezone.utc).isoformat(),
                        "target": base, "environment": "development", "zap_version": version,
                        "mode": "safe", "scan_type": "passive", "active_scans": 0, "spider_scans": 0,
                        "records_to_scan": 0, "passive_tasks_running": 0, "baseline": args.baseline,
                        "credential_values_redacted": True,
                        "source_sha256": {str(p.relative_to(app_dir)): hashlib.sha256(p.read_bytes()).hexdigest()
                                          for p in sorted((app_dir / "app").rglob("*.py"))},
                        "requests": coverage, "alert_instances_by_risk": dict(risk_counts),
                        "passive_scanners": scanners,
                    }
                    (output / "execution.json").write_text(json.dumps(summary, indent=2) + "\n")
                    print(f"Relatórios exportados para {output}: {dict(risk_counts)}", flush=True)
                    zap("core", "action", "shutdown")
                    zap_process.wait(timeout=30)
            finally:
                terminate(api_process)
                terminate(zap_process)
                api_log.flush()
                zap_log.flush()
                # Preserva os findings; remove somente valores efêmeros de
                # senha/JWT/chave da API ZAP de logs e evidências exportadas.
                for artifact in output.iterdir():
                    if artifact.is_file() and artifact.suffix in {".log", ".json", ".html"}:
                        content = artifact.read_text()
                        for value in sensitive_values:
                            content = content.replace(value, "[REDACTED_EPHEMERAL_CREDENTIAL]")
                        artifact.write_text(content)
    checksums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in output.iterdir() if p.is_file() and p.name != "sha256.json"}
    (output / "sha256.json").write_text(json.dumps(checksums, indent=2) + "\n")


if __name__ == "__main__":
    main()
