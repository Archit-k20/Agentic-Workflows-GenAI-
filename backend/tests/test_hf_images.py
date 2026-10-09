"""Independent image capacity, private credentials and no-duplicate transport."""

import base64
import io
import json
import time

import httpx
import pytest
from PIL import Image

from backend import free_config as cfg, hf_images
from backend.events import observer
from backend.policy import Capacity, ConfirmedCapacity, Policy
from backend.providers import Runtime
from backend.storage import LocalStorage


@pytest.fixture
def image_runtime(monkeypatch):
    monkeypatch.setenv("TRACE_HF_SPACE_ID", "owner/worker")
    monkeypatch.setenv("TRACE_HF_API_TOKEN", "private-read-token")
    events = []
    token = observer.set(lambda e, d: events.append((e, d)))
    runtime = Runtime("free", "image")
    yield runtime, events
    observer.reset(token)


def payload(**changes):
    buf = io.BytesIO()
    Image.new("RGB", (1024, 1024), "blue").save(buf, format="PNG")
    return {"image": base64.b64encode(buf.getvalue()).decode(), "model": cfg.HF_IMAGE_MODEL,
            "revision": cfg.HF_IMAGE_REVISION, "steps": 4, **changes}


def test_confirmed_capacity_uses_independent_worker_once(image_runtime, monkeypatch):
    runtime, events = image_runtime
    calls = []
    def hosted(*args):
        calls.append("cloudflare")
        raise ConfirmedCapacity("Quota exhausted")
    def hf(prompt, deadline, check):
        calls.append("huggingface")
        return payload()
    monkeypatch.setattr(runtime, "hosted", hosted)
    monkeypatch.setattr(hf_images, "generate", hf)
    assert runtime.image("A blue lamp").size == (1024, 1024)
    assert calls == ["cloudflare", "huggingface"]
    assert runtime.metadata()["fallback"] is True
    assert runtime.metadata()["engines"][0]["provider"] == "huggingface-zerogpu"
    assert ("stage", {"name": "Hugging Face image fallback", "status": "completed"}) in events


@pytest.mark.parametrize("failure", [Capacity("Timeout"), ValueError("Invalid input"), Capacity("Bad credential")])
def test_ambiguous_or_input_errors_do_not_submit_fallback(image_runtime, monkeypatch, failure):
    runtime, events = image_runtime
    def hosted(*args):
        raise failure
    monkeypatch.setattr(runtime, "hosted", hosted)
    monkeypatch.setattr(hf_images, "generate", lambda *args: pytest.fail("Duplicate submission"))
    with pytest.raises(type(failure)):
        runtime.image("A blue lamp")
    assert events[-1] == ("stage", {"name": "Generate image", "status": "failed"})


def test_exhausted_local_cf_budget_still_uses_hf(image_runtime, monkeypatch, tmp_path):
    runtime = image_runtime[0]
    runtime.policy = Policy(LocalStorage(tmp_path))
    runtime.policy.reserve("image", 8000)
    monkeypatch.setenv("TRACE_CLOUDFLARE_ACCOUNT_ID", "account")
    monkeypatch.setenv("TRACE_CLOUDFLARE_API_TOKEN", "cf-secret")
    monkeypatch.setattr("httpx.post", lambda *a, **k: pytest.fail("CF budget was exhausted"))
    monkeypatch.setattr(hf_images, "generate", lambda *a: payload())
    assert runtime.image("Lamp").size == (1024, 1024)


def test_fallback_failure_retains_actual_failed_stages(image_runtime, monkeypatch):
    runtime, events = image_runtime
    def rejected(*args):
        raise ConfirmedCapacity("CF quota exhausted")
    def hf(*args):
        raise Capacity("HF quota exhausted")
    monkeypatch.setattr(runtime, "hosted", rejected)
    monkeypatch.setattr(hf_images, "generate", hf)
    with pytest.raises(Capacity, match="HF quota"):
        runtime.image("Lamp")
    assert events[-2:] == [("stage", {"name": "Hugging Face image fallback", "status": "failed"}),
                           ("stage", {"name": "Generate image", "status": "failed"})]


@pytest.mark.parametrize("status,expected", [(429, ConfirmedCapacity), (500, Capacity), (403, Capacity), (400, ValueError)])
def test_cloudflare_error_classification(image_runtime, monkeypatch, status, expected):
    runtime = image_runtime[0]
    monkeypatch.setenv("TRACE_CLOUDFLARE_ACCOUNT_ID", "account")
    monkeypatch.setenv("TRACE_CLOUDFLARE_API_TOKEN", "secret")
    monkeypatch.setattr(httpx, "post", lambda *a, **k: httpx.Response(status, request=httpx.Request("POST", "https://api.cloudflare.com")))
    with pytest.raises(expected) as error:
        runtime.hosted(cfg.IMAGE_MODEL, {"prompt": "Lamp"})
    if status != 429:
        assert not isinstance(error.value, ConfirmedCapacity)


def mock_client(monkeypatch, handler):
    original = httpx.Client
    monkeypatch.setattr(hf_images.httpx, "Client", lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs))


def handler_for(calls, result=None, failure=None):
    def handler(request):
        calls.append(request)
        if request.url.host == "huggingface.co":
            return httpx.Response(200, json={"id": "owner/worker", "private": True, "host": "https://owner-worker.hf.space", "runtime": {"stage": "RUNNING"}})
        if request.url.path == "/config":
            return httpx.Response(200, json={"api_prefix": "/gradio_api"})
        if request.method == "POST":
            assert json.loads(request.content) == {"data": ["Lamp"]}
            return httpx.Response(200, json={"event_id": "abc123"})
        if failure:
            raise failure
        return httpx.Response(200, text="event: heartbeat\ndata: null\n\nevent: complete\ndata: " + json.dumps([result or payload()]) + "\n\n")
    return handler


def test_private_rest_transport_has_one_submission_and_no_artifact_fetch(image_runtime, monkeypatch):
    calls = []
    mock_client(monkeypatch, handler_for(calls))
    result = hf_images.generate("Lamp", time.monotonic() + 900, lambda: None)
    assert result["revision"] == cfg.HF_IMAGE_REVISION
    assert len(calls) == 4 and sum(r.method == "POST" for r in calls) == 1
    assert all(r.headers["Authorization"] == "Bearer private-read-token" for r in calls)
    assert {r.url.host for r in calls} == {"huggingface.co", "owner-worker.hf.space"}


@pytest.mark.parametrize("failure", [httpx.ReadTimeout("timeout"), httpx.ReadError("interrupted")])
def test_interrupted_rest_stream_is_never_replayed(image_runtime, monkeypatch, failure):
    calls = []
    mock_client(monkeypatch, handler_for(calls, failure=failure))
    with pytest.raises(Capacity, match="no request was replayed"):
        hf_images.generate("Lamp", time.monotonic() + 900, lambda: None)
    assert sum(r.method == "POST" for r in calls) == 1


@pytest.mark.parametrize("change", [{"model": "other"}, {"revision": "new"}, {"steps": 1}, {"image": "invalid-base64"}])
def test_changed_profile_or_invalid_image_rejected(change):
    with pytest.raises(ValueError):
        hf_images._payload([payload(**change)])


@pytest.mark.parametrize("host", ["http://owner-worker.hf.space", "https://127.0.0.1", "https://owner-worker.hf.space.evil.org", "https://key@owner-worker.hf.space", "https://owner-worker.hf.space:8443"])
def test_credentials_cannot_be_forwarded_to_another_destination(host):
    with pytest.raises(Capacity):
        hf_images._host({"host": host, "private": True, "runtime": {"stage": "RUNNING"}})


def test_redirect_does_not_forward_credentials(image_runtime, monkeypatch):
    calls = []
    def handler(request):
        calls.append(request)
        return httpx.Response(302, headers={"Location": "https://another-site.example"})
    mock_client(monkeypatch, handler)
    with pytest.raises(Capacity):
        hf_images.generate("Lamp", time.monotonic() + 900, lambda: None)
    assert len(calls) == 1


def test_response_bound_applies_before_parsing_long_lines(image_runtime, monkeypatch):
    calls = []
    monkeypatch.setattr(hf_images, "MAX_RESPONSE", 20)
    mock_client(monkeypatch, handler_for(calls))
    with pytest.raises(ValueError, match="permitted size"):
        hf_images.generate("Lamp", time.monotonic() + 900, lambda: None)


def test_hf_secret_redacted_from_workflow_events(monkeypatch):
    from backend.app import scrub
    monkeypatch.setenv("TRACE_HF_API_TOKEN", "private-read-token")
    assert scrub({"message": "private-read-token"}, "") == {"message": "[redacted]"}


@pytest.mark.parametrize("private,hardware", [(False, "zero-a10g"), (True, "a10g-small")])
def test_deployment_refuses_public_or_paid_space(monkeypatch, private, hardware):
    from types import SimpleNamespace as NS
    from backend import hf_deploy

    api = NS(space_info=lambda _: NS(private=private, sdk="gradio"),
             get_space_runtime=lambda _: NS(hardware=None, requested_hardware=hardware))
    monkeypatch.setattr(hf_deploy, "HfApi", lambda **kwargs: api)
    monkeypatch.setattr(hf_deploy, "hf_hub_download", lambda *a, **k: pytest.fail("Model download before safety check"))
    with pytest.raises(ValueError):
        hf_deploy.publish({"TRACE_HF_SPACE_ID": "owner/worker", "TRACE_HF_API_TOKEN": "read", "TRACE_HF_DEPLOY_TOKEN": "write"})


def test_first_deployment_uses_only_read_secret_and_explicit_source_files(monkeypatch):
    from types import SimpleNamespace as NS
    from backend import hf_deploy

    actions = []
    def api(token):
        def secret(*args):
            actions.append(("secret", token, args))
        def upload(**kwargs):
            actions.append(("upload", token, kwargs))
            return NS(oid="reviewed-source-commit")
        return NS(space_info=lambda _: NS(private=True, sdk="gradio"),
                  get_space_runtime=lambda _: NS(hardware=None, requested_hardware="zero-a10g"),
                  add_space_secret=secret, upload_folder=upload)
    monkeypatch.setattr(hf_deploy, "HfApi", api)
    monkeypatch.setattr(hf_deploy, "hf_hub_download", lambda *a, **k: actions.append(("model_access", k)))
    report = hf_deploy.publish({"TRACE_HF_SPACE_ID": "owner/worker", "TRACE_HF_API_TOKEN": "read-only", "TRACE_HF_DEPLOY_TOKEN": "local-write"})
    assert report["private"] and report["commit"] == "reviewed-source-commit"
    assert actions[0][1]["token"] == "read-only"
    assert actions[1] == ("secret", "local-write", ("owner/worker", "HF_TOKEN", "read-only"))
    assert actions[2][2]["allow_patterns"] == ["README.md", "app.py", "requirements.txt"]
