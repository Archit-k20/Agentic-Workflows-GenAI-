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
