"""Request-local observations; never token streaming or simulated stages."""

from contextvars import ContextVar
from functools import wraps

observer = ContextVar("observer", default=lambda event, data: None)


def emit(event, **data):
    observer.get()(event, data)


def observe(fn, label):
    @wraps(fn)
    def run(*args, **kwargs):
        emit("stage", name=label, status="running")
        try:
            result = fn(*args, **kwargs)
        except Exception:
            emit("stage", name=label, status="failed")
            raise
        emit("stage", name=label, status="completed")
        return result

    return run


def install():
    from workflows import (
        research_agent as r,
        support_triage as s,
        document_intelligence as d,
        code_copilot as c,
        content_pipeline as p,
    )

    stages = [
        (
            r,
            {
                "plan_research": "Plan research",
                "fetch_source": "Read source",
                "summarize_source": "Digest source",
                "synthesize_report": "Draft report",
                "critique_report": "Review report",
                "validate_citations": "Check citation labels",
                "revise_report": "Revise report",
            },
        ),
        (
            s,
            {
                "classify_intent": "Classify intent",
                "fetch_support_source": "Read support source",
                "summarize_support_source": "Digest source",
                "draft_support_resolution": "Draft resolution",
                "finalize_triage": "Apply escalation rules",
            },
        ),
        (
            d,
            {
                "extract_document_text": "Extract document",
                "analyze_document": "Analyze document",
            },
        ),
        (
            c,
            {
                "generate_initial_code": "Generate code",
                "verify_code": "Verify syntax / compilation",
                "repair_code": "Repair code once",
            },
        ),
        (
            p,
            {
                "build_content_plan": "Plan content",
                "build_content_package": "Create artifacts",
                "critique_content_package": "Review content",
                "generate_speech": "Generate narration",
            },
        ),
    ]
    for module, mapping in stages:
        for name, label in mapping.items():
            setattr(module, name, observe(getattr(module, name), label))
    for module in [r, s, d, p]:
        original = module._chat_json

        def with_fallback(*args, _fn=original, **kwargs):
            result = _fn(*args, **kwargs)
            fallback = kwargs.get("fallback", args[-1] if args else None)
            if result is fallback:
                emit(
                    "warning",
                    message="A provider or JSON parsing fallback was used. Inspect details and review important conclusions manually.",
                )
            return result

        module._chat_json = with_fallback
    original_text = r._chat_text

    def text_fallback(*args, **kwargs):
        result = original_text(*args, **kwargs)
        if not result:
            emit(
                "warning",
                message="The research provider returned no report text. Existing fallback behavior was retained; inspect the result before using it.",
            )
        return result

    r._chat_text = text_fallback

    # Keep workflow verification logic intact while restricting child-process I/O.
    import subprocess
    import sys
    import tempfile
    import shutil
    from pathlib import Path

    class IsolatedCompiler:
        @staticmethod
        def run(command, **kwargs):
            source = next(
                Path(arg)
                for arg in command
                if Path(arg).suffix in {".js", ".java", ".c", ".cpp"}
            )
            with tempfile.TemporaryDirectory(prefix="trace-check-") as folder:
                private = Path(folder) / source.name
                shutil.copyfile(source, private)
                isolated = [
                    str(private) if arg == str(source) else arg for arg in command
                ]
                return subprocess.run(
                    [sys.executable, "-m", "backend.compiler_guard", *isolated],
                    **kwargs,
                )

    c.subprocess = IsolatedCompiler
