"""Run actual model workflows against fixed synthetic source fixtures.

No provider mocks; URL extraction is replaced only with the committed source text.
Local results and hosted results are separate, and hosted fallback cannot pass a hosted gate.
"""

import argparse
import hashlib
import json
import re
import time
from pathlib import Path
from unittest.mock import patch
from contextlib import ExitStack
from pydantic import TypeAdapter
from backend.app import policy as shared_policy  # observations installed on import
from backend import engine, processing
from backend.contracts import RunInput, DocumentsContext
from backend.providers import Runtime
from backend.storage import LocalStorage
from backend.events import observer
from workflows.runtime import current


def load_owner(path):
    import os

    if path and Path(path).exists():
        for line in Path(path).read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                name, value = line.split("=", 1)
                os.environ[name.strip()] = value.strip().strip('"').strip("'")


def evaluate(case, store, sid, runtime):
    source = case["source"]
    if case.get("long"):
        source = (
            (
                "Appendix: routine inspection records confirm that this is a limited pilot. "
                * 80
            )
            + "\nFINAL DECISION:\n"
            + source
        )
    fields = {
        "tool": {"summary": "text-summary", "qa": "document-qa"}.get(
            case["kind"], case["kind"]
        )
    }
    if case["kind"] == "summary":
        fields["text"] = source
    elif case["kind"] in {"qa", "documents"}:
        import fitz

        pdf = fitz.open()
        page = pdf.new_page()
        page.insert_textbox((35, 35, 550, 800), source, fontsize=8)
        # Long input uses DOCX to avoid artificially overflowing one PDF textbox.
        if case.get("long"):
            from docx import Document
            import io

            doc = Document()
            doc.add_paragraph(source)
            buf = io.BytesIO()
            doc.save(buf)
            raw = buf.getvalue()
            name = "brief.docx"
        else:
            raw = pdf.tobytes()
            name = "brief.pdf"
        pdf.close()
        item, folder = store.put(sid, "upload", name)
        (folder / "file").write_bytes(raw)
        if case["kind"] == "qa":
            ctx = engine.context(
                store, sid, "document-qa", DocumentsContext(file_ids=[item]), ""
            )
            fields.update(context_id=ctx["context_id"], question=case["prompt"])
        else:
            fields["file_ids"] = [item]
    elif case["kind"] == "code":
        fields.update(prompt=case["prompt"], language=case["language"])
    elif case["kind"] == "content":
        fields.update(
            idea=case["prompt"] + "\n" + source,
            tone=case["tone"],
            platforms=case["platforms"],
        )
    else:
        fields["urls"] = ["https://trace-evaluation.invalid/source"]
        fields["topic" if case["kind"] == "research" else "question"] = case["prompt"]
        if case.get("partial"):
            fields["urls"].append("https://trace-evaluation.invalid/unavailable")
        if case.get("conflict"):
            fields["urls"].append("https://trace-evaluation.invalid/conflict")

    def fixture_article(url, _runtime):
        if url.endswith("unavailable"):
            raise ValueError("Synthetic source unavailable")
        content = (
            source
            if not url.endswith("conflict")
            else case.get("conflict_source", "A conflicting draft lists only 20 units; its date and authority are not established.")
        )
        return {
            "url": url,
            "title": "Synthetic pilot brief",
            "text": processing.check_text(content, _runtime, url),
        }

    with patch.object(processing, "article", fixture_article):
        return engine.execute(
            store, sid, TypeAdapter(RunInput).validate_python(fields), ""
        )


def score(case, result, runtime):
    kind = case["kind"]
    text = (
        result.get("text")
        or result.get("answer")
        or result.get("final_report")
        or result.get("final_script")
        or json.dumps(result.get("documents") or result.get("final") or result)
    )
    if kind == "support":
        text = result.get("final", {}).get("answer", "")
    if kind == "documents":
        # Rejected suggestions and source quotes are diagnostic/source data,
        # not accepted analysis claims. They must not inflate fact presence.
        text = json.dumps([{
            "summary": d["analysis"].get("summary", ""),
            "entities": d["analysis"].get("entities", {}),
            "risks": d["analysis"].get("risks", []),
            "action_items": [{k: a.get(k, "") for k in ("task", "owner", "due_date", "priority")}
                             for a in d["analysis"].get("action_items", [])],
        } for d in result["documents"]])
    coverage = (
        sum(
            (
                bool(re.search(r"(?<!\d)" + re.escape(f) + r"(?!\d)", text))
                if f.isdigit()
                else f.lower() in text.lower()
            )
            for f in case["facts"]
        )
        / max(1, len(case["facts"]))
        if case["facts"]
        else 1.0
    )
    citations = re.findall(r"\[(S\d+)\]", text)
    valid = {s["label"] for s in result.get("sources", [])}
    labels_valid = (
        not (set(citations) - valid) if kind in {"qa", "research", "support"} else True
    )
    abstained = (
        bool(
            re.search(
                r"not (?:provided|present|available|contain|specified)|insufficient|cannot (?:determine|answer)|do not (?:contain|mention|specify|provide)|does not (?:contain|specify|provide|mention)|no (?:information|evidence|guarantee)|not enough",
                text,
                re.I,
            )
        )
        if case.get("absent")
        else None
    )
    verification = result.get("final_verification", {}).get("passed", True)
    escalated = (
        result.get("final", {}).get("resolution_type") == "escalate"
        if case.get("escalate")
        else None
    )
    nonempty = bool(result.get("documents")) if kind == "documents" else bool(text.strip())
    # Coverage is a fact-presence screen. Rubric grounding review is a separate mandatory gate.
    return {
        "fact_coverage": coverage,
        "citation_labels_valid": labels_valid,
        "abstained": abstained,
        "verification_passed": verification,
        "escalated": escalated,
        "nonempty": nonempty,
        "hosted_only": not runtime.local,
        "rubric_review": {
            "reviewer": None,
            "grounding": None,
            "usefulness": None,
            "unsupported_claims": None,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["free", "local"], required=True)
    parser.add_argument("--owner-env")
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.json"),
                        help="Fixed fixture JSON; its hash is checked when resuming.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--limit", type=int, default=60)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--hosted-only", action="store_true")
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--priority", nargs="+", default=[], metavar="CASE_ID",
        help="Run these selected fixture IDs first, then the remaining cases; does not bypass budgets.",
    )
    args = parser.parse_args()
    load_owner(args.owner_env)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    store = LocalStorage("/data/evaluation")
    # Evaluation and live requests must reserve the same owner compute allowance.
    policy = shared_policy
    sid = store.session(store.create_session()["token"])
    fixture_bytes = args.cases.read_bytes()
    cases = json.loads(fixture_bytes)[
        args.start : args.start + args.limit
    ]
    by_id = {case["id"]: case for case in cases}
    if len(set(args.priority)) != len(args.priority) or any(
        case_id not in by_id for case_id in args.priority
    ):
        parser.error("Priority IDs must be unique and belong to the selected fixture range.")
    cases = [by_id[case_id] for case_id in args.priority] + [
        case for case in cases if case["id"] not in args.priority
    ]
    from backend import free_config as cfg

    profile = {
        "hosted_text": cfg.CHAT_MODEL,
        "hosted_code": cfg.CODE_MODEL,
        "local_digest": cfg.LOCAL_DIGEST,
        "fixtures_sha256": hashlib.sha256(fixture_bytes).hexdigest(),
    }
    # Resume only compatible inference code, not just matching model names.
    root = Path(__file__).resolve().parents[2]
    pipeline = hashlib.sha256()
    for path in sorted(
        [root / "backend" / name for name in (
            "providers.py", "processing.py", "structured.py", "retrieval.py",
            "engine.py", "events.py", "free_config.py", "grounding.py",
        )] + list((root / "workflows").glob("*.py"))
    ):
        pipeline.update(str(path.relative_to(root)).encode())
        pipeline.update(path.read_bytes())
    profile["pipeline_sha256"] = pipeline.hexdigest()
    rows = []
    if args.resume and output.exists():
        previous = json.loads(output.read_text())
        if previous.get("profile") != profile or previous["mode"] != args.mode:
            raise ValueError(
                "Evaluation profile changed; use a new output file rather than mixing model results."
            )
        rows = [r for r in previous["rows"] if not r["error"]]
    completed = {r["id"] for r in rows}
    for case in cases:
        if case["id"] in completed:
            continue
        runtime = Runtime(
            args.mode,
            {"summary": "text-summary", "qa": "qa"}.get(case["kind"], case["kind"]),
            policy,
        )
        runtime.allow_fallback = not args.hosted_only
        token = current.set(runtime)
        events = []
        observation = observer.set(lambda e, d: events.append({"event": e, "data": d}))
        start = time.monotonic()
        try:
            result = evaluate(case, store, sid, runtime)
            incomplete = args.hosted_only and any(
                event["event"] == "warning" and "provider or JSON parsing fallback" in event["data"].get("message", "")
                for event in events
            )
            row = {
                "id": case["id"],
                "kind": case["kind"],
                "score": None if incomplete else score(case, result, runtime),
                "result": result,
                "error": "Hosted evaluation used a provider/JSON fallback; incomplete stages cannot pass the hosted gate." if incomplete else None,
            }
        except Exception as exc:
            row = {
                "id": case["id"],
                "kind": case["kind"],
                "score": None,
                "result": None,
                "error": str(exc),
            }
        finally:
            current.reset(token)
            observer.reset(observation)
        row.update(
            seconds=round(time.monotonic() - start, 2),
            execution=runtime.metadata(),
            events=events,
        )
        rows.append(row)
        output.write_text(
            json.dumps(
                {
                    "mode": args.mode,
                    "profile": profile,
                    "fixture_count": len(cases),
                    "rows": rows,
                    "quality_gate": "pending rubric review",
                },
                indent=2,
            )
            + "\n"
        )
        print(
            case["id"],
            "ERROR" if row["error"] else json.dumps(row["score"]),
            row["seconds"],
            flush=True,
        )
        if row["error"] and args.stop_on_error:
            break
    failures = [
        r
        for r in rows
        if r["error"]
        or not r["score"]["citation_labels_valid"]
        or not r["score"]["nonempty"]
    ]
    print(
        "Completed:",
        len(rows),
        "Hard failures:",
        len(failures),
        "Quality gate requires rubric review.",
        flush=True,
    )


if __name__ == "__main__":
    main()
