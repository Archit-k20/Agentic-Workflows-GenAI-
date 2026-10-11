import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
from workflows import (
    research_agent as r,
    support_triage as s,
    document_intelligence as d,
    code_copilot as c,
    content_pipeline as p,
    textsummary,
    YT_summary,
    article_summarizer,
    file_summarizer,
    text_to_speech,
)


def test_original_workflow_functions_preserved():
    expected = json.loads(
        Path("backend/tests/fixtures/parity-functions.json").read_text()
    )
    actual = {}
    for module in Path("workflows").glob("*.py"):
        for node in ast.parse(module.read_text()).body:
            if isinstance(node, ast.FunctionDef):
                actual[f"{module.stem}.{node.name}"] = hashlib.sha256(
                    ast.dump(node, include_attributes=False).encode()
                ).hexdigest()
    assert len(expected) > 60
    for name, digest in expected.items():
        assert actual[name] == digest, name


def test_research_revision_and_partial_sources(monkeypatch):
    monkeypatch.setattr(r, "OpenAI", lambda **kw: object())
    monkeypatch.setattr(r, "plan_research", lambda *a: {"goal": "test"})

    def fetch(url):
        if url.endswith("bad"):
            raise ValueError("Unreadable source")
        return {"title": "Source", "text": "Facts", "url": url}

    monkeypatch.setattr(r, "fetch_source", fetch)
    monkeypatch.setattr(
        r,
        "summarize_source",
        lambda source, topic, plan, client, label: {
            **source,
            "label": label,
            "summary": "Facts",
        },
    )
    monkeypatch.setattr(r, "synthesize_report", lambda *a: "Unknown claim [S99]")
    critiques = iter(
        [
            {
                "passes_review": False,
                "issues": ["bad label"],
                "revised_report": "Unknown claim [S99]",
            },
            {"passes_review": True, "issues": [], "revised_report": "Revised [S1]"},
        ]
    )
    monkeypatch.setattr(r, "critique_report", lambda *a: next(critiques))
    repair = Mock(return_value="Revised [S1]")
    monkeypatch.setattr(r, "revise_report", repair)
    result = r.run_research_agent(
        "topic", ["https://example.com/a", "https://example.com/bad"], "test-key"
    )
    assert (
        result["final_report"] == "Revised [S1]" and len(result["source_errors"]) == 1
    )
    assert repair.call_count == 1 and result["citation_check"]["unknown_labels"] == []
    assert r.validate_citations("wrong [S99]", result["sources"])["unknown_labels"] == [
        "S99"
    ]
    assert not r.validate_citations("uncited", result["sources"])["has_any_citation"]


@pytest.mark.parametrize(
    "intent,draft,expected",
    [
        ({"requires_human": False}, {"answer": "OK [S1]", "confidence": 0.9}, "answer"),
        (
            {"requires_human": True},
            {"answer": "OK [S1]", "confidence": 0.9},
            "escalate",
        ),
        ({}, {"answer": "OK [S1]", "confidence": 0.59}, "escalate"),
        ({}, {"answer": "OK [S9]", "confidence": 0.9}, "escalate"),
        ({}, {"answer": "uncited", "confidence": 0.9}, "escalate"),
        (
            {},
            {"answer": "OK [S1]", "confidence": 0.9, "resolution_type": "escalate"},
            "escalate",
        ),
    ],
)
def test_support_decision_rules(intent, draft, expected):
    assert (
        s.finalize_triage("question", intent, draft, [{"label": "S1"}])[
            "resolution_type"
        ]
        == expected
    )


def client_with(content):
    create = Mock(return_value=NS(choices=[NS(message=NS(content=content))]))
    return NS(chat=NS(completions=NS(create=create))), create


def test_document_json_fallback():
    client, create = client_with("not JSON")
    result = d.analyze_document(
        {
            "name": "brief.txt",
            "source_type": "txt",
            "text": "Mira Chen must submit the plan by Oct 14. Email mira@example.com.",
        },
        client,
    )
    assert result["entities"]["emails"] == ["mira@example.com"]
    assert result["action_items"] and "heuristics" in result["risks"][0]
    assert create.call_args.kwargs["temperature"] == 0.2


def test_code_single_repair(monkeypatch):
    client, create = client_with("def broken(:")
    monkeypatch.setattr(c, "OpenAI", lambda **kw: client)
    result = c.run_code_copilot("test", "test-key", "python")
    assert result["repair_attempted"] and not result["final_verification"]["passed"]
    assert (
        create.call_count == 2
    )  # initial generation plus one repair, never a repair loop
    assert create.call_args.kwargs["model"] == "gpt-4o-mini"


@pytest.mark.parametrize("language", ["javascript", "java", "c", "c++"])
def test_compiler_absence(monkeypatch, language):
    monkeypatch.setattr(c.shutil, "which", lambda _: None)
    check = c.verify_code("x", language)
    assert not check["passed"] and "unavailable" in check["checks"][0]["details"]


@pytest.mark.parametrize(
    "language,code",
    [
        ("python", 'print("hello")'),
        ("javascript", "const x = 1;"),
        ("java", "public class Main { public static void main(String[] args) {} }"),
        ("c", "int main(void) { return 0; }"),
        ("c++", "int main() { return 0; }"),
    ],
)
def test_real_language_checks(language, code):
    result = c.verify_code(code, language)
    if any("kernel has no Landlock" in check["details"] for check in result["checks"]):
        import os

        if os.environ.get("TRACE_REQUIRE_COMPILER_ISOLATION") == "1":
            pytest.fail("Native CI kernel must support compiler isolation")
        pytest.skip(
            "Emulated architecture cannot expose Landlock; check runs on native CI instead"
        )
    assert result["passed"]


def test_summary_model_settings(monkeypatch):
    infer = Mock(return_value=[{"summary_text": "summary"}])
    monkeypatch.setattr(textsummary, "get_text_summary_pipeline", lambda: infer)
    assert textsummary.summary("input") == "summary"
    assert infer.call_args.kwargs == {"min_length": 100, "max_length": 300}
    monkeypatch.setattr(YT_summary, "get_transcript", lambda _: "x" * 6000)
    monkeypatch.setattr(YT_summary, "get_text_summary_pipeline", lambda: infer)
    YT_summary.summarize_from_url("https://youtu.be/abcdefghijk", "ignored-key")
    assert (
        len(infer.call_args.args[0]) == 4000
        and infer.call_args.kwargs["do_sample"] is False
    )
    client, create = client_with("summary")
    monkeypatch.setattr(textsummary, "OpenAI", lambda **kw: client)
    textsummary.summary("input", "test-key")
    assert (
        create.call_args.kwargs["model"] == "gpt-3.5-turbo"
        and create.call_args.kwargs["max_tokens"] == 300
    )


def test_speech_isolated_and_options(monkeypatch):
    create = Mock(return_value=NS(content=b"fake-audio"))
    monkeypatch.setattr(
        text_to_speech, "OpenAI", lambda **kw: NS(audio=NS(speech=NS(create=create)))
    )
    first = text_to_speech.generate_speech("text", "nova", "test-key")
    second = text_to_speech.generate_speech("text", "nova", "test-key")
    assert first != second and Path(first).read_bytes() == b"fake-audio"
    assert create.call_args.kwargs == {
        "model": "tts-1",
        "voice": "nova",
        "input": "text",
    }
    Path(first).unlink()
    Path(second).unlink()
