import httpx
import pytest

from backend.deployment_check import inspect, public_origin


@pytest.mark.parametrize("origin", [
    "http://trace.example", "https://localhost:8000", "https://127.0.0.1",
    "https://10.0.0.2", "https://[::1]", "https://user:secret@trace.example",
    "https://trace.example/api/v1", "https://trace.example?token=secret",
])
def test_public_origin_rejects_unusable_or_sensitive_configuration(origin):
    with pytest.raises(ValueError):
        public_origin(origin)


def test_public_origin_normalizes_trailing_slash():
    assert public_origin("https://trace.example/") == "https://trace.example"


def check_backend(protection, missing_proof_status):
    requests = []
    frontend = "https://trace.example"

    def handle(request):
        requests.append(request)
        headers = {"access-control-allow-origin": frontend} if request.headers.get("origin") == frontend else {}
        if request.method == "OPTIONS":
            return httpx.Response(200, headers=headers)
        if request.url.path.endswith("/health"):
            return httpx.Response(200, headers=headers, json={
                "ready": True, "public_protection": protection,
                "hosted_configured": True, "local_text_ready": True,
                "speech_installed": True, "max_concurrent_runs": 2,
                "retention_hours": 24,
                "capabilities": dict.fromkeys(("ocr", "javascript", "java", "c", "c++"), True),
            })
        if request.url.path.endswith("/capabilities"):
            return httpx.Response(200, json={"default_mode": "free", "turnstile_required": protection})
        if request.url.path.endswith("/sessions"):
            return httpx.Response(missing_proof_status, json={"detail": "Visitor proof rejected"})
        raise AssertionError("Preflight must not invoke workflows, upload files or request media.")

    with httpx.Client(base_url="https://api.trace.example", transport=httpx.MockTransport(handle)) as client:
        return inspect(client, frontend), requests


def test_ready_api_with_protection_disabled_cannot_pass_public_check():
    report, requests = check_backend(False, 200)
    assert report["passed"] is False
    assert not any(request.method == "POST" for request in requests)


def test_missing_proof_must_be_rejected_not_merely_configured():
    report, _ = check_backend(True, 200)
    assert report["passed"] is False


def test_public_wiring_pass_does_not_claim_ai_quality_or_trigger_inference():
    report, requests = check_backend(True, 403)
    assert report["passed"] is True
    assert "No inference" in report["scope"]
    assert {r.url.path for r in requests} <= {
        "/api/v1/health", "/api/v1/capabilities", "/api/v1/runs", "/api/v1/sessions",
    }
    assert all(r.method == "OPTIONS" for r in requests if r.url.path.endswith("/runs"))
