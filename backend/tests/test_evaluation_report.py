from backend.evaluation.report import summarize


def test_fact_coverage_does_not_count_zero_fact_cases_or_drop_failures():
    cases = [
        {"id": "a", "kind": "summary", "facts": ["one", "two"]},
        {"id": "b", "kind": "qa", "facts": [], "absent": True},
        {"id": "c", "kind": "summary", "facts": ["three", "four"]},
    ]
    rows = [
        {"id": "a", "error": None, "score": {"fact_coverage": 1.0}},
        {"id": "b", "error": None, "score": {"fact_coverage": 1.0, "abstained": True}},
        {"id": "c", "error": "Engine unavailable", "score": None},
    ]
    report = summarize(cases, rows, "free")
    assert report["fact_presence"]["rate"] == 0.5
    assert report["absent_answer_refusal"]["passed"] == 1
    assert report["execution_failures"] == [{"id": "c", "error": "Engine unavailable"}]


def test_missing_case_remains_visible():
    report = summarize([{"id": "missing", "kind": "code", "facts": []}], [], "local")
    assert report["execution_failures"][0]["id"] == "missing"
    assert report["compiler_checks"] == {
        "passed": 0,
        "expected": 1,
        "scope": "Syntax/compilation only, not behavior or security.",
    }


def test_review_cannot_pass_when_revision_removes_evidence_structure():
    cases = [{"id": "research", "kind": "research", "facts": []}]
    rows = [{
        "id": "research", "error": None,
        "score": {"citation_labels_valid": True, "fact_coverage": 1.0},
        "result": {"final_report": "The pilot is scheduled; further research is suggested."},
    }]
    report = summarize(cases, rows, "free")
    assert report["invalid_citation_cases"] == []
    assert report["missing_required_citation_cases"] == ["research"]
    assert report["missing_research_section_cases"][0]["sections"] == [
        "Executive Summary", "Findings", "Risks and Gaps",
        "Recommended Next Questions", "Source List",
    ]


def test_abstention_and_escalation_do_not_require_answer_citations():
    cases = [
        {"id": "missing", "kind": "qa", "facts": [], "absent": True},
        {"id": "escalate", "kind": "support", "facts": [], "escalate": True},
    ]
    rows = [
        {"id": "missing", "error": None, "score": {},
         "result": {"answer": "Not provided."}},
        {"id": "escalate", "error": None, "score": {},
         "result": {"final": {"resolution_type": "escalate", "answer": "Human review required."}}},
    ]
    assert summarize(cases, rows, "free")["missing_required_citation_cases"] == []


def test_supported_questions_cannot_pass_by_escalating_every_request():
    cases = [{"id": "supported", "kind": "support", "facts": [], "escalate": False}]
    rows = [{"id": "supported", "error": None, "score": {}, "result": {
        "draft": {"resolution_type": "answer", "answer": "40"},
        "final": {"resolution_type": "escalate", "answer": "40"},
    }}]
    report = summarize(cases, rows, "free")
    assert report["supported_support_answers"]["passed"] == 0
    assert report["supported_support_answers"]["expected"] == 1
    assert report["missing_support_draft_citation_cases"] == ["supported"]


def test_evaluation_cannot_bypass_the_live_compute_budget(tmp_path, monkeypatch):
    import json
    import sys
    from backend.evaluation import run
    from backend.storage import LocalStorage
    from backend.policy import Policy
    from backend import free_config as cfg

    live = Policy(LocalStorage(tmp_path / "live"))
    live.reserve("text", 7000)
    fixtures = LocalStorage(tmp_path / "fixtures")
    monkeypatch.setattr(run, "shared_policy", live)
    monkeypatch.setattr(run, "LocalStorage", lambda _: fixtures)
    monkeypatch.setattr(cfg, "configured", lambda: True)
    monkeypatch.setattr(
        run,
        "evaluate",
        lambda case, store, sid, runtime: runtime.hosted(
            cfg.CHAT_MODEL, {"messages": []}, 600
        ),
    )
    output = tmp_path / "report.json"
    monkeypatch.setattr(sys, "argv", [
        "evaluate", "--mode", "free", "--hosted-only", "--stop-on-error",
        "--output", str(output), "--limit", "1",
    ])
    run.main()
    report = json.loads(output.read_text())
    assert "allowance is unavailable" in report["rows"][0]["error"]
    assert report["profile"]["pipeline_sha256"]


def test_priority_evaluation_preserves_remaining_cases(tmp_path, monkeypatch):
    import json
    import sys
    from backend.evaluation import run
    from backend.storage import LocalStorage

    fixtures = LocalStorage(tmp_path / "fixtures")
    monkeypatch.setattr(run, "LocalStorage", lambda _: fixtures)
    monkeypatch.setattr(run, "evaluate", lambda case, *_: {"text": case["source"]})
    output = tmp_path / "priority.json"
    monkeypatch.setattr(sys, "argv", [
        "evaluate", "--mode", "free", "--hosted-only", "--output", str(output),
        "--limit", "2", "--priority", "summary-02",
    ])
    run.main()
    report = json.loads(output.read_text())
    assert [row["id"] for row in report["rows"]] == ["summary-02", "summary-01"]
    assert report["fixture_count"] == 2


def test_unknown_priority_stops_before_inference(tmp_path, monkeypatch):
    import sys
    import pytest
    from backend.evaluation import run
    from backend.storage import LocalStorage

    fixtures = LocalStorage(tmp_path / "fixtures")
    monkeypatch.setattr(run, "LocalStorage", lambda _: fixtures)
    monkeypatch.setattr(sys, "argv", [
        "evaluate", "--mode", "free", "--output", str(tmp_path / "bad.json"),
        "--limit", "1", "--priority", "content-01",
    ])
    with pytest.raises(SystemExit) as stopped:
        run.main()
    assert stopped.value.code == 2
    assert not (tmp_path / "bad.json").exists()


def test_fixture_changes_cannot_be_mixed_by_resume(tmp_path, monkeypatch):
    import json
    import sys
    import pytest
    from backend.evaluation import run
    from backend.storage import LocalStorage
    fixtures = LocalStorage(tmp_path / "storage")
    monkeypatch.setattr(run, "LocalStorage", lambda _: fixtures)
    monkeypatch.setattr(run, "evaluate", lambda case, *_: {"text": case["source"]})
    output = tmp_path / "result.json"
    cases = tmp_path / "cases.json"
    cases.write_text(json.dumps([{"id": "a", "kind": "summary", "source": "First", "facts": []}]))
    argv = ["evaluate", "--mode", "free", "--cases", str(cases), "--output", str(output)]
    monkeypatch.setattr(sys, "argv", argv)
    run.main()
    cases.write_text(json.dumps([{"id": "a", "kind": "summary", "source": "Different", "facts": []}]))
    monkeypatch.setattr(sys, "argv", argv + ["--resume"])
    with pytest.raises(ValueError, match="profile changed"):
        run.main()


def test_hosted_gate_cannot_count_swallowed_provider_failure_as_complete(tmp_path, monkeypatch):
    import json
    import sys
    from backend.evaluation import run
    from backend.events import emit
    from backend.storage import LocalStorage
    fixtures = LocalStorage(tmp_path / "storage")
    monkeypatch.setattr(run, "LocalStorage", lambda _: fixtures)
    def evaluate(case, *_):
        emit("warning", message="A provider or JSON parsing fallback was used. Inspect details.")
        return {"text": "Preserved usable draft"}
    monkeypatch.setattr(run, "evaluate", evaluate)
    output = tmp_path / "result.json"
    monkeypatch.setattr(sys, "argv", ["evaluate", "--mode", "free", "--hosted-only", "--stop-on-error", "--output", str(output), "--limit", "2"])
    run.main()
    rows = json.loads(output.read_text())["rows"]
    assert len(rows) == 1 and rows[0]["score"] is None
    assert "incomplete stages" in rows[0]["error"]
    assert rows[0]["result"]["text"] == "Preserved usable draft"


def test_support_fact_screen_cannot_count_a_rejected_answer():
    from backend.evaluation.run import score
    from backend.providers import Runtime
    value = score({"kind": "support", "facts": ["receipt"]},
                  {"final": {"answer": "Human review required.", "rejected_answer": "No receipt required."}},
                  Runtime("free", "support"))
    assert value["fact_coverage"] == 0


def test_document_fact_screen_cannot_count_source_quotes_or_rejected_assignees():
    from backend.evaluation.run import score
    from backend.providers import Runtime
    value = score({"kind": "documents", "facts": ["32", "Emma Hart"]},
        {"documents": [{"analysis": {"summary": "A shipment is planned.", "action_items": [
            {"task": "Ship kits", "owner": "Not specified", "evidence": "Emma Hart owns the project; 32 kits ship.", "proposed_owner": "Emma Hart"}]}}]},
        Runtime("free", "documents"))
    assert value["fact_coverage"] == 0


def test_document_failure_does_not_count_an_empty_analysis_list_as_usable_output():
    from backend.evaluation.run import score
    from backend.providers import Runtime
    value = score({"kind": "documents", "facts": []},
                  {"documents": [], "errors": [{"error": "Provider failed"}]}, Runtime("free", "documents"))
    assert value["nonempty"] is False
