"""Check a public API without credentials or AI requests.

This verifies deployment wiring, not output quality, warmed models or capacity.
Successful browser Turnstile verification remains a separate launch check.
"""

import argparse
import ipaddress
import json
from urllib.parse import urlsplit

import httpx


def public_origin(value):
    parts = urlsplit(value)
    if (
        parts.scheme != "https"
        or not parts.hostname
        or parts.username
        or parts.password
        or parts.query
        or parts.fragment
        or parts.path not in {"", "/"}
    ):
        raise ValueError("Use a public HTTPS origin without credentials, path, query or fragment.")
    host = parts.hostname.lower()
    if host == "localhost" or host.endswith((".localhost", ".local")):
        raise ValueError("A public deployment cannot point visitors to localhost.")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError("A public deployment cannot use a private network address.")
    return value.rstrip("/")


def inspect(client, frontend_origin):
    checks = []

    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})

    health_response = client.get("/api/v1/health", headers={"Origin": frontend_origin})
    health_response.raise_for_status()
    health = health_response.json()
    check("API readiness", health.get("ready") is True)
    check("Exact frontend CORS origin", health_response.headers.get("access-control-allow-origin") == frontend_origin)
    check("Public visitor protection enabled", health.get("public_protection") is True)
    check("Hosted provider configured (availability not tested)", health.get("hosted_configured") is True)
    check("Pinned local model available (inference not tested)", health.get("local_text_ready") is True)
    check("Speech dependencies installed (generation not tested)", health.get("speech_installed") is True)
    for capability in ("ocr", "javascript", "java", "c", "c++"):
        check(capability + " installed", health.get("capabilities", {}).get(capability) is True)
    check("Two workflow slots", health.get("max_concurrent_runs") == 2)
    check("Temporary retention at most 24 hours", 0 < health.get("retention_hours", 0) <= 24)

    capabilities_response = client.get("/api/v1/capabilities")
    capabilities_response.raise_for_status()
    capabilities = capabilities_response.json()
    check("Free visitor mode is the default", capabilities.get("default_mode") == "free")
    check("Browser must supply Turnstile proof", capabilities.get("turnstile_required") is True)

    preflight = client.options("/api/v1/runs", headers={
        "Origin": frontend_origin,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "authorization,content-type,x-trace-mode",
    })
    check("Workflow CORS preflight", preflight.is_success and preflight.headers.get("access-control-allow-origin") == frontend_origin)

    unrelated_origin = "https://trace-preflight.invalid"
    denied = client.get("/api/v1/health", headers={"Origin": unrelated_origin})
    check("Unrelated browser origin not allowed", denied.headers.get("access-control-allow-origin") is None)

    # Do not create anonymous sessions on an accidentally unprotected deployment.
    if health.get("public_protection") is True:
        denied_session = client.post("/api/v1/sessions", json={"turnstile_token": ""})
        check("Missing visitor proof rejected", denied_session.status_code == 403)
    else:
        check("Missing visitor proof rejected", False)
    return {
        "passed": all(item["passed"] for item in checks),
        "checks": checks,
        "scope": "Public HTTP wiring only. No inference, paid requests or credentials. Successful Turnstile, media, persistence, source quality, latency and memory still require launch verification.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontend-origin", required=True)
    parser.add_argument("--api-origin", required=True)
    args = parser.parse_args()
    try:
        frontend = public_origin(args.frontend_origin)
        api = public_origin(args.api_origin)
        with httpx.Client(base_url=api, timeout=15, follow_redirects=False) as client:
            report = inspect(client, frontend)
    except (ValueError, httpx.HTTPError) as exc:
        print(json.dumps({"passed": False, "error_type": type(exc).__name__, "message": "Invalid public origin or API check failed. Check HTTPS, routing and configuration; no AI request was made."}, indent=2))
        raise SystemExit(1) from None
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
