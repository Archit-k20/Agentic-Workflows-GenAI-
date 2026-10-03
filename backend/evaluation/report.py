"""Summarize measured fixture outcomes without claiming factual certification."""

import argparse
import json
from pathlib import Path


def summarize(cases, rows, mode):
    by_id = {row["id"]: row for row in rows}

    def score(case):
        row = by_id.get(case["id"], {})
        return row.get("score") or {}

    fact_count = sum(len(case["facts"]) for case in cases)
    retained = sum(
        score(case).get("fact_coverage", 0) * len(case["facts"]) for case in cases
    )
    absent = [case for case in cases if case.get("absent")]
    code = [case for case in cases if case["kind"] == "code"]
    escalation = [case for case in cases if case.get("escalate")]
    failures = [
        {
            "id": case["id"],
            "error": by_id.get(case["id"], {}).get("error") or "Missing result",
        }
        for case in cases
        if case["id"] not in by_id or by_id[case["id"]].get("error")
    ]
    return {
        "mode": mode,
        "expected_cases": len(cases),
        "completed_cases": sum(case["id"] in by_id for case in cases),
        "execution_failures": failures,
        "fact_presence": {
            "matched": round(retained, 6),
            "expected": fact_count,
            "rate": retained / fact_count if fact_count else None,
            "definition": "Expected-fact-weighted output-only presence; zero-fact cases do not inflate this rate. Errors/missing results score zero.",
        },
        "absent_answer_refusal": {
            "passed": sum(score(c).get("abstained") is True for c in absent),
            "expected": len(absent),
        },
        "compiler_checks": {
            "passed": sum(score(c).get("verification_passed") is True for c in code),
            "expected": len(code),
            "scope": "Syntax/compilation only, not behavior or security.",
        },
        "required_escalations": {
            "passed": sum(score(c).get("escalated") is True for c in escalation),
            "expected": len(escalation),
        },
        "invalid_citation_cases": [
            c["id"] for c in cases if score(c).get("citation_labels_valid") is False
        ],
        "hosted_fallback_cases": [
            r["id"]
            for r in rows
            if mode == "free" and r.get("execution", {}).get("fallback")
        ],
        "rubric_gate": "Separate grounding/usefulness review required; these screening metrics cannot certify accuracy.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("report")
    args = parser.parse_args()
    cases = json.loads(Path(__file__).with_name("cases.json").read_text())
    report = json.loads(Path(args.report).read_text())
    print(json.dumps(summarize(cases, report["rows"], report["mode"]), indent=2))


if __name__ == "__main__":
    main()
