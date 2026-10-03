import json
import time
from pathlib import Path
from fastapi.testclient import TestClient
from backend import app as module, engine
from backend.storage import LocalStorage
from backend.contracts import RunInput
from pydantic import TypeAdapter
import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "storage", LocalStorage(tmp_path / "data"))
    with TestClient(module.app) as c:
        yield c


def headers(client):
    return {
        "Authorization": "Bearer " + client.post("/api/v1/sessions").json()["token"]
    }


def test_upload_ownership_artifacts_and_clear(client):
    a = headers(client)
    b = headers(client)
    upload = client.post(
        "/api/v1/uploads",
        headers=a,
        files={"file": ("brief.txt", b"private", "text/plain")},
    )
    assert upload.status_code == 200
    sid = module.storage.session(a["Authorization"][7:])
    item, folder = module.storage.put(
        sid, "artifact", "audio/mpeg", {"media_type": "audio/mpeg"}
    )
    (folder / "file").write_bytes(b"private-media")
    assert (
        client.get("/api/v1/artifacts/" + item, headers=a).content == b"private-media"
    )
    assert client.get("/api/v1/artifacts/" + item, headers=b).status_code == 404
    with pytest.raises(Exception):
        module.storage.get(
            module.storage.session(b["Authorization"][7:]), upload.json()["file_id"]
        )
    assert client.delete("/api/v1/sessions/current", headers=a).status_code == 204
    assert not folder.exists()
    assert client.get("/api/v1/artifacts/" + item, headers=a).status_code == 401


def test_expiry_and_restart(tmp_path):
    storage = LocalStorage(tmp_path)
    session = storage.create_session()
    sid = storage.session(session["token"])
    item, folder = storage.put(sid, "context", "document-qa")
    (folder / "documents.json").write_text("[]")
    restarted = LocalStorage(tmp_path)
    assert (
        restarted.get(restarted.session(session["token"]), item)["name"]
        == "document-qa"
    )
    with restarted.connect() as db:
        db.execute("UPDATE sessions SET expires=?", (time.time() - 1,))
    with pytest.raises(Exception, match="reprocess"):
        restarted.session(session["token"])
    assert not folder.exists()


def test_events_and_secret_redaction(client, monkeypatch):
    def execute(*a):
        module.observer.get()("stage", {"name": "Actual stage", "status": "running"})
        module.observer.get()("stage", {"name": "Actual stage", "status": "completed"})
        return {"tool": "text-summary", "text": "secret-key result"}

    monkeypatch.setattr(engine, "execute", execute)
    response = client.post(
        "/api/v1/runs",
        headers={**headers(client), "X-OpenAI-Key": "secret-key"},
        json={"tool": "text-summary", "text": "input"},
    )
    assert (
        "event: started" in response.text
        and "event: stage" in response.text
        and "event: result" in response.text
    )
    assert "secret-key" not in response.text and "[redacted]" in response.text


def test_validation_credentials_and_size(client):
    h = headers(client)
    assert (
        client.post(
            "/api/v1/runs",
            headers=h,
            json={"tool": "code", "prompt": "x", "language": "ruby"},
        ).status_code
        == 422
    )
    assert (
        client.post(
            "/api/v1/contexts/urls", headers=h, json={"urls": ["https://example.com"]}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/v1/uploads", headers=h, files={"file": ("evil.pkl", b"data")}
        ).status_code
        == 415
    )
    assert (
        client.post(
            "/api/v1/runs",
            headers={**h, "Content-Length": str(2 * 1024 * 1024)},
            json={"tool": "ocr", "file_ids": ["x"]},
        ).status_code
        == 413
    )


def test_chunked_request_size_is_rejected(client):
    response = client.post(
        "/api/v1/runs",
        headers={**headers(client), "Content-Type": "application/json"},
        content=iter([b" " * (700 * 1024), b" " * (700 * 1024)]),
    )
    assert response.status_code == 413


def test_text_request_preserves_original_input_without_extra_character_cap(client, monkeypatch):
    original = "  Untruncated source text.\n" * 10000
    def execute(storage, session, inputs, key):
        assert inputs.text == original
        return {"tool": "text-summary", "text": "Mocked summary"}
    monkeypatch.setattr(engine, "execute", execute)
    response = client.post("/api/v1/runs", headers=headers(client), json={"tool": "text-summary", "text": original})
    assert "event: result" in response.text


def test_authentication_warning_keeps_research_fallback():
    from types import SimpleNamespace
    from workflows import research_agent
    from backend.events import observer

    class InvalidCredentials(Exception):
        status_code = 401

    def fail(**kwargs):
        raise InvalidCredentials("Do not expose this provider message")

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
    received = []
    token = observer.set(lambda name, data: received.append((name, data)))
    fallback = {"goal": "Preserved original fallback"}
    try:
        assert research_agent._chat_json(client, "system", "user", fallback) is fallback
    finally:
        observer.reset(token)
    assert any("Invalid OpenAI credentials" in data.get("message", "") for name, data in received)
    assert all("provider message" not in str(data) for name, data in received)


@pytest.mark.parametrize(
    "tool",
    [
        "text-summary",
        "youtube-summary",
        "article-summary",
        "file-summary",
        "ocr",
        "image",
        "speech",
        "captions",
        "code",
        "content",
        "research",
        "documents",
        "document-qa",
        "url-qa",
        "support",
    ],
)
def test_all_tools_are_typed(tool):
    fields = {
        "text": "x",
        "url": "https://example.com",
        "file_ids": ["x"],
        "prompt": "x",
        "idea": "x",
        "topic": "x",
        "question": "x",
        "context_id": "x",
        "urls": ["https://example.com"],
    }
    result = TypeAdapter(RunInput).validate_python({"tool": tool, **fields})
    assert result.tool == tool

def test_expired_session_cannot_create_orphan_files(tmp_path):
    storage=LocalStorage(tmp_path);created=storage.create_session();sid=storage.session(created['token'])
    storage.clear(sid)
    with pytest.raises(Exception,match='reprocess'):storage.put(sid,'artifact','image/png')
    assert not (tmp_path/sid).exists()

def test_context_cannot_be_queried_by_other_session(client):
    a=headers(client);b=headers(client)
    sid=module.storage.session(a['Authorization'][7:]);item,folder=module.storage.put(sid,'context','document-qa')
    response=client.post('/api/v1/contexts/'+item+'/query',headers={**b,'X-OpenAI-Key':'mock-key'},json={'question':'Read another session'})
    assert 'event: error' in response.text and 'session_expired' in response.text
    assert 'event: result' not in response.text

def test_two_execution_limit(client):
    module.slots.acquire();module.slots.acquire()
    try:
        response=client.post('/api/v1/runs',headers=headers(client),json={'tool':'text-summary','text':'input'})
        assert response.status_code==429
    finally:module.slots.release();module.slots.release()
