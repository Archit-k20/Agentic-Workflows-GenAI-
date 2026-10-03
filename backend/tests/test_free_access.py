"""Free routing, bounded inputs, persisted quotas, and failure states without paid calls."""

import json
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from fastapi import HTTPException
from pydantic import TypeAdapter
from PIL import Image
from langchain_core.embeddings import Embeddings
from backend import engine, processing, retrieval
from backend.app import app  # install observations as in production
from backend.policy import Policy, Capacity
from backend.providers import Runtime
from backend.storage import LocalStorage
from backend.contracts import RunInput
from backend.events import observer
from workflows.runtime import current


class Tokenizer:
    def encode(self, text, **kwargs):
        return [ord(c) for c in text]

    def decode(self, tokens, **kwargs):
        return "".join(chr(c) for c in tokens)


class Embedding(Embeddings):
    def embed_documents(self, texts):
        return [[float(len(t)), 1.0] for t in texts]

    def embed_query(self, text):
        return [float(len(text)), 1.0]


@pytest.fixture
def free(tmp_path, monkeypatch):
    store = LocalStorage(tmp_path)
    sid = store.session(store.create_session()["token"])
    policy = Policy(store)
    runtime = Runtime("free", "", policy)
    events = []
    calls = []
    token = current.set(runtime)
    observation = observer.set(lambda e, d: events.append((e, d)))
    monkeypatch.setattr(processing, "tokenizer", lambda: Tokenizer())
    monkeypatch.setattr(retrieval, "tokenizer", lambda: Tokenizer())
    monkeypatch.setattr(retrieval, "LocalEmbeddings", Embedding)
    monkeypatch.setattr(
        "workflows.url_qna.fetch_article_text",
        lambda _: (
            "Repair pilot",
            "Mira Chen starts a pilot on October 14 with 40 repair kits.",
        ),
    )
    monkeypatch.setattr(
        "pytesseract.image_to_string",
        lambda *a, **k: "Mira Chen starts October 14 with 40 kits.",
    )
    monkeypatch.setattr(
        "backend.speech.synthesize",
        lambda text, voice, path, check: path.write_bytes(b"test-audio"),
    )

    def hosted(model, payload, output_limit=0):
        runtime.expensive = True
        runtime.record("cloudflare", model)
        calls.append(payload)
        if "prompt" in payload:
            import base64

            buf = io.BytesIO()
            Image.new("RGB", (16, 24), "blue").save(buf, format="PNG")
            return {"image": base64.b64encode(buf.getvalue()).decode()}
        system = payload["messages"][0]["content"]
        lower = system.lower()
        if "goal, sub_questions" in system:
            result = {
                "goal": "Repair",
                "sub_questions": ["When?"],
                "report_sections": ["Findings"],
            }
        elif "key_points" in system:
            result = {
                "label": "S1",
                "title": "Repair",
                "summary": "40 kits on October 14",
                "key_points": ["40 kits"],
                "relevance": "Direct",
            }
        elif "label, title, summary" in system:
            result = {
                "label": "S1",
                "title": "Repair",
                "summary": "40 kits on October 14",
                "relevance": "Direct",
            }
        elif "revised_report" in system:
            result = {
                "passes_review": True,
                "issues": [],
                "revised_report": "Mira Chen starts October 14 with 40 kits. [S1]",
            }
        elif "revised_script" in system:
            result = {
                "passes_review": True,
                "issues": [],
                "revised_script": "Repair pilot",
                "revised_captions": {
                    platform: "Repair pilot" for platform in runtime.platforms
                },
            }
        elif "content_angle" in system:
            result = {
                "content_angle": "Repair",
                "audience": "Visitors",
                "hooks": ["Repair"],
                "sections": ["Pilot"],
                "cta": "Read",
            }
        elif "image_prompts" in system:
            result = {
                "title": "Repair",
                "script": "Repair pilot",
                "image_prompts": ["Workshop"],
                "captions": {
                    platform: "Repair pilot" for platform in runtime.platforms
                },
                "hashtags": ["#Repair"],
                "cta": "Read",
            }
        elif "document_type" in system:
            result = {
                "document_type": "Brief",
                "summary": "40 kits on October 14",
                "entities": {
                    "people": ["Mira Chen"],
                    "organizations": [],
                    "emails": [],
                    "dates": ["October 14"],
                },
                "action_items": [
                    {
                        "task": "Start pilot",
                        "owner": "Mira Chen",
                        "due_date": "October 14",
                        "priority": "medium",
                    }
                ],
                "risks": [],
            }
        elif "requires_human" in system:
            result = {
                "intent": "general",
                "severity": "low",
                "requires_human": False,
                "reason": "Documentation question",
            }
        elif "resolution_type" in system:
            result = {
                "resolution_type": "answer",
                "answer": "40 kits on October 14. [S1]",
                "confidence": 0.9,
                "escalation_reason": "",
                "recommended_next_step": "Review pilot",
            }
        elif "code" in lower:
            result = "def unique(items):\n    return list(dict.fromkeys(items))\n"
        else:
            result = (
                "Mira Chen starts October 14 with 40 kits. [S1]"
                if ("[S1]" in system or "context" in lower)
                else "Mira Chen starts October 14 with 40 kits."
            )
        return {"response": json.dumps(result) if isinstance(result, dict) else result}

    monkeypatch.setattr(runtime, "hosted", hosted)

    def add(name, data):
        item, folder = store.put(sid, "upload", name)
        (folder / "file").write_bytes(data)
        return item

    import fitz

    pdf = fitz.open()
    pdf.new_page().insert_text(
        (40, 40), "Mira Chen starts October 14 with 40 repair kits."
    )
    pdfid = add("brief.pdf", pdf.tobytes())
    pdf.close()
    txtid = add("brief.txt", b"Mira Chen starts October 14 with 40 repair kits.")
    buf = io.BytesIO()
    Image.new("RGB", (200, 80), "white").save(buf, format="PNG")
    imageid = add("scan.png", buf.getvalue())
    yield store, sid, runtime, events, calls, pdfid, txtid, imageid
    current.reset(token)
    observer.reset(observation)


@pytest.mark.parametrize(
    "tool",
    [
        "text-summary",
        "youtube-summary",
        "article-summary",
        "file-summary",
        "ocr",
        "captions",
        "image",
        "speech",
        "code",
        "content",
        "research",
        "documents",
        "support",
        "document-qa",
        "url-qa",
    ],
)
def test_all_fifteen_without_visitor_key(free, tool):
    store, sid, runtime, events, calls, pdfid, txtid, imageid = free
    runtime.tool = tool
    fields = {
        "tool": tool,
        "text": "Mira Chen starts October 14 with 40 kits.",
        "transcript_text": "Mira Chen starts October 14 with 40 kits.",
        "url": "https://example.com/brief",
        "urls": ["https://example.com/brief"],
        "topic": "Repair pilot",
        "question": "When does the pilot start?",
        "prompt": "Create a unique function",
        "idea": "Repair pilot",
        "file_ids": [pdfid],
        "include_audio": tool == "content",
    }
    if tool in {"youtube-summary", "captions"}:
        fields.pop("url")
    if tool == "ocr":
        fields["file_ids"] = [imageid]
    if tool == "documents":
        fields["file_ids"] = [txtid]
    if tool.endswith("-qa"):
        from backend.contracts import DocumentsContext, URLsContext

        inputs = (
            DocumentsContext(file_ids=[pdfid])
            if tool == "document-qa"
            else URLsContext(urls=fields["urls"])
        )
        ctx = engine.context(store, sid, tool, inputs, "")
        fields["context_id"] = ctx["context_id"]
        assert ctx["profile"] == retrieval.PROFILE
    result = engine.execute(
        store, sid, TypeAdapter(RunInput).validate_python(fields), ""
    )
    assert result["tool"] == tool and result["execution"]["mode"] == "free"
    assert not any(v["provider"] == "openai" for v in result["execution"]["engines"])
    if tool == "image":
        assert (result["width"], result["height"]) == (16, 24)
    if tool == "speech":
        assert (
            store.get(sid, result["artifact_id"], "artifact")["folder"]
            .joinpath("file")
            .read_bytes()
            == b"test-audio"
        )
    if tool == "code":
        assert result["final_verification"]["passed"]
    if tool == "research":
        assert not result["citation_check"]["unknown_labels"]
    if tool.endswith("-qa"):
        assert result["sources"][0]["text"]
    if tool == "content":
        assert result["audio_path"] and not result["audio_error"]


def test_fallback_only_unfinished_text_stage(free, monkeypatch):
    _, _, runtime, events, calls, *_ = free
    hosted = []
    local = []

    def failure(*a):
        hosted.append(a)
        raise Capacity("Free quota exhausted")

    monkeypatch.setattr(runtime, "hosted", failure)
    monkeypatch.setattr(
        runtime, "local_text", lambda *a: local.append(a) or "Local answer"
    )
    messages = [
        {"role": "system", "content": "Be faithful"},
        {"role": "user", "content": "Source"},
    ]
    assert runtime.text(messages) == "Local answer"
    assert runtime.text(messages) == "Local answer"
    assert len(hosted) == 1 and len(local) == 2
    assert runtime.metadata()["fallback"] and any(e == "warning" for e, d in events)


def test_local_mode_never_calls_hosted(free, monkeypatch):
    runtime = free[2]
    runtime.mode = "local"
    runtime.local = True
    monkeypatch.setattr(runtime, "hosted", lambda *a: pytest.fail("Hosted request"))
    monkeypatch.setattr(runtime, "local_text", lambda *a: "Local")
    assert (
        runtime.text(
            [
                {"role": "system", "content": "Summary"},
                {"role": "user", "content": "Text"},
            ]
        )
        == "Local"
    )
    with pytest.raises(ValueError, match="requires hosted"):
        runtime.image("A workshop")


def test_review_failure_cannot_pass(free, monkeypatch):
    from workflows import research_agent

    monkeypatch.setattr(free[2], "text", lambda *a, **k: "invalid JSON")
    review = research_agent.critique_report("Pilot", [], "Draft", free[2].client)
    assert (
        review["passes_review"] is False
        and "unavailable" in review["issues"][0].lower()
    )


def test_complete_unicode_chunks_and_limits(free):
    text = "Review 🛠️ October 14. " * 200
    pieces = processing.chunks(text)
    assert all(len(p.encode()) <= 3000 for p in pieces) and pieces[-1].endswith(
        "October 14. "
    )
    with pytest.raises(ValueError, match="nothing was silently truncated"):
        processing.check_text("x" * 12001, free[2], "Input")


def test_context_profile_reprocess_and_restart(free):
    from backend.contracts import DocumentsContext

    store, sid, runtime, *_ = free
    pdfid = free[5]
    ctx = engine.context(
        store, sid, "document-qa", DocumentsContext(file_ids=[pdfid]), ""
    )
    restarted = LocalStorage(store.root)
    assert engine.query(restarted, sid, ctx["context_id"], "When?", "")["sources"]
    runtime.mode = "openai"
    with pytest.raises(ValueError, match="Reprocess"):
        engine.query(restarted, sid, ctx["context_id"], "When?", "key")
    runtime.mode = "free"
    row = store.get(sid, ctx["context_id"])
    bad = {**row["metadata"], "profile": {**retrieval.PROFILE, "version": 0}}
    with store.connect() as db:
        db.execute(
            "UPDATE items SET metadata=? WHERE id=?",
            (json.dumps(bad), ctx["context_id"]),
        )
    with pytest.raises(ValueError, match="Reprocess"):
        engine.query(store, sid, ctx["context_id"], "When?", "")


def test_persistent_session_and_network_quotas(tmp_path):
    store = LocalStorage(tmp_path)
    p = Policy(store)
    a = p.actor("203.0.113.1")
    lease = p.begin("session-a", a, ["image"])
    p.finish(lease)
    p = Policy(LocalStorage(tmp_path))
    assert p.usage("session-b", a)["remaining"]["image"] == 1
    lease = p.begin("session-b", a, ["image"])
    p.finish(lease)
    with pytest.raises(HTTPException, match="Daily image"):
        p.begin("session-c", a, ["image"])
    assert "203.0.113.1" not in a


def test_atomic_active_limit_and_budget(tmp_path):
    p = Policy(LocalStorage(tmp_path))
    a = p.actor("1.2.3.4")

    def start(i):
        try:
            return p.begin(str(i), a, ["text"])
        except HTTPException:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(start, range(2)))
    assert sum(r is not None for r in results) == 1
    p.finish(next(r for r in results if r), ["text"])
    assert p.usage("a", a)["remaining"]["text"] == 20
    p.reserve("text", 7000)
    with pytest.raises(Capacity):
        p.reserve("text", 1)
    p.reserve("image", 1000)
    with pytest.raises(Capacity):
        p.reserve("image", 1)


def test_rollback_multi_category_charge(tmp_path):
    p = Policy(LocalStorage(tmp_path))
    a = p.actor("1.2.3.4")
    with p.storage.connect() as db:
        db.execute("INSERT INTO usage VALUES (?,?,?,?)", (p.day(), a, "audio", 5))
    with pytest.raises(HTTPException):
        p.begin("s", a, ["text", "audio"])
    assert p.usage("s", a)["remaining"]["text"] == 20


def test_hosted_structured_object_is_validated_without_fallback(free, monkeypatch):
    runtime = free[2]
    monkeypatch.setattr(
        runtime,
        "hosted",
        lambda *a: {
            "response": {
                "goal": "Pilot",
                "sub_questions": [],
                "report_sections": ["Findings"],
            }
        },
    )
    reply = runtime.create(
        messages=[
            {
                "role": "system",
                "content": "Return JSON with goal, sub_questions, and report_sections.",
            },
            {"role": "user", "content": "Pilot"},
        ],
        response_format={"type": "json_object"},
    )
    assert (
        json.loads(reply.choices[0].message.content)["goal"] == "Pilot"
        and not runtime.local
    )


def test_only_one_structured_repair(free, monkeypatch):
    runtime = free[2]
    attempts = []
    monkeypatch.setattr(
        runtime, "text", lambda *a, **k: attempts.append(a) or "bad json"
    )
    with pytest.raises(ValueError, match="after one repair"):
        runtime.create(
            messages=[
                {
                    "role": "system",
                    "content": "Return goal, sub_questions, report_sections",
                },
                {"role": "user", "content": "Pilot"},
            ],
            response_format={"type": "json_object"},
        )
    assert len(attempts) == 2


def test_local_model_digest_is_checked(free, monkeypatch):
    import httpx

    runtime = free[2]
    runtime.local = True
    monkeypatch.setattr(
        httpx,
        "get",
        lambda *a, **k: NS(
            raise_for_status=lambda: None,
            json=lambda: {"models": [{"name": "qwen3.5:4b", "digest": "changed"}]},
        ),
    )
    with pytest.raises(ValueError, match="pinned local model"):
        runtime.local_text([{"role": "system", "content": "Summary"}], 100, False, 0.2)


def test_day_reset_and_start_throttle(tmp_path, monkeypatch):
    p = Policy(LocalStorage(tmp_path))
    a = p.actor("1.2.3.4")
    for _ in range(5):
        p.finish(p.begin("s", a, ["text"]))
    with pytest.raises(HTTPException, match="wait a minute"):
        p.begin("s", a, ["text"])
    with p.storage.connect() as db:
        db.execute("DELETE FROM starts")
    monkeypatch.setattr(p, "day", lambda: "2099-01-01")
    assert p.usage("s", a)["remaining"]["text"] == 20
    p.finish(p.begin("s", a, ["text"]))


def test_unknown_qa_citation_cannot_be_accepted(free, monkeypatch):
    from backend.contracts import DocumentsContext
    from workflows import document_qna

    store, sid, runtime, *_ = free
    ctx = engine.context(
        store, sid, "document-qa", DocumentsContext(file_ids=[free[5]]), ""
    )
    monkeypatch.setattr(
        document_qna, "answer_with_context", lambda *a: "Unfounded [S99]"
    )
    with pytest.raises(ValueError, match="unknown citation"):
        engine.query(store, sid, ctx["context_id"], "Who?", "")


def test_local_decoder_schema_covers_nested_fields_and_platforms():
    from backend.structured import schema_for

    document = schema_for(
        "Return JSON with document_type, summary, entities, action_items, risks."
    )
    assert document["properties"]["entities"]["required"] == [
        "people",
        "organizations",
        "emails",
        "dates",
    ]
    assert (
        document["properties"]["action_items"]["items"]["properties"]["due_date"][
            "type"
        ]
        == "string"
    )
    content = schema_for(
        "Return title, script, image_prompts, captions, hashtags, cta.",
        ["linkedin", "x"],
    )
    assert set(content["properties"]["captions"]["required"]) == {"linkedin", "x"}
    assert content["properties"]["captions"]["additionalProperties"] is False


def test_larger_hosted_model_reserves_and_reconciles_its_actual_rate(
    tmp_path, monkeypatch
):
    from backend import free_config as cfg
    import httpx

    monkeypatch.setenv("TRACE_CLOUDFLARE_ACCOUNT_ID", "test-account")
    monkeypatch.setenv("TRACE_CLOUDFLARE_API_TOKEN", "test-token")
    policy = Policy(LocalStorage(tmp_path))
    runtime = Runtime("free", "text-summary", policy)

    def post(url, **kwargs):
        return httpx.Response(
            200,
            request=httpx.Request("POST", url),
            json={
                "success": True,
                "result": {
                    "response": "A summary",
                    "usage": {"prompt_tokens": 100, "completion_tokens": 100},
                },
            },
        )

    monkeypatch.setattr("backend.providers.httpx.post", post)
    runtime.hosted(
        cfg.CHAT_MODEL, {"messages": [{"role": "user", "content": "A source"}]}, 600
    )
    with policy.storage.connect() as db:
        amount = db.execute("select amount from reservations").fetchone()[0]
    assert amount == pytest.approx((100 * 26668 + 100 * 204805) / 1e6)


def test_hosted_only_evaluation_does_not_substitute_local_output(monkeypatch):
    runtime = Runtime("free", "research")
    runtime.allow_fallback = False
    monkeypatch.setattr(processing, "tokenizer", lambda: Tokenizer())
    monkeypatch.setattr(
        runtime,
        "hosted",
        lambda *a, **kw: (_ for _ in ()).throw(Capacity("Daily budget exhausted")),
    )
    with pytest.raises(Capacity, match="Daily budget exhausted"):
        runtime.text(
            [
                {"role": "system", "content": "Summarize"},
                {"role": "user", "content": "Source"},
            ]
        )
    assert runtime.local is False


def test_multibyte_local_prompt_cannot_silently_overrun_context(monkeypatch):
    monkeypatch.setattr(processing, "tokenizer", lambda: Tokenizer())
    monkeypatch.setattr(
        "backend.providers.httpx.get",
        lambda *a, **k: (_ for _ in ()).throw(
            AssertionError("No model request should occur")
        ),
    )
    runtime = Runtime("local", "code")
    with pytest.raises(ValueError, match="safe CPU context budget"):
        runtime.text(
            [
                {"role": "system", "content": "Generate code"},
                {"role": "user", "content": "🙂" * 4000},
            ]
        )


def test_generation_sections_preserve_complete_words_and_all_records():
    text = " ".join(
        f"Inspection record{i:04d} confirms a limited pilot." for i in range(150)
    )
    pieces = processing.chunks(text)
    expected = set(text.split())
    observed = set(word for piece in pieces for word in piece.split())
    assert observed == expected
    assert all(len(piece.encode("utf-8")) <= 3000 for piece in pieces)


def test_caption_validation_cannot_silently_drop_a_selected_platform():
    from backend.structured import validate, shape_hint

    system = "Return title, script, image_prompts, captions, hashtags, cta."
    data = {
        "title": "Title",
        "script": "Script",
        "image_prompts": ["Concept one", "Concept two"],
        "captions": {"linkedin": "Copy"},
        "hashtags": ["#pilot"],
        "cta": "Learn more",
    }
    with pytest.raises(ValueError, match="every requested platform"):
        validate(json.dumps(data), system, ["linkedin", "x"])
    data["captions"]["x"] = "Short copy"
    assert validate(json.dumps(data), system, ["linkedin", "x"])
    assert '"linkedin": "caption text"' in shape_hint(system, ["linkedin", "x"])


def test_all_document_failures_retain_the_specific_diagnostic(free, monkeypatch):
    store, sid, runtime, *_ = free
    monkeypatch.setattr(
        runtime,
        "hosted",
        lambda *a, **kw: (_ for _ in ()).throw(ValueError("Hosted input was rejected")),
    )
    with pytest.raises(ValueError, match="could not process any"):
        engine.execute(
            store,
            sid,
            TypeAdapter(RunInput).validate_python(
                {"tool": "documents", "file_ids": [free[5]]}
            ),
            "",
        )
    assert any("Hosted input was rejected" in warning for warning in runtime.warnings)
