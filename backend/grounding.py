"""Scoped free-mode source checks. These are not general factual certification.

Original OpenAI workflows are untouched. Source data is request-local; rejected
rewrites remain in Details and never replace a better validated draft.
"""

from contextlib import contextmanager
import json
import re
from decimal import Decimal

SECTIONS = (
    "Executive Summary", "Findings", "Risks and Gaps",
    "Recommended Next Questions", "Source List",
)


def normalized(value):
    return " ".join(value.split()).casefold()


def numbers(value):
    value = re.sub(r"\[S\d+\]|https?://\S+", "", value)
    return {
        format(Decimal(n.replace(",", "")).normalize(), "f")
        for n in re.findall(r"(?<![\w])\d+(?:,\d{3})*(?:\.\d+)?(?![\w])", value)
    }


def sentences(source):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])|\n+", source) if s.strip()]


def material_details(source):
    """Keep quoted numerical conditions/amounts/planned quantities, not invented facts."""
    return list(dict.fromkeys(
        sentence for sentence in sentences(source)
        if numbers(sentence) and re.search(
            r"\b(?:budget|cost|price|total|refunds?|returns?|ship\w*|deliver\w*|deadline|due|quantity|units?|planned|schedule\w*)\b|[$€£₹]",
            sentence, re.I,
        )
    ))


def missing_details(output, source):
    present = numbers(output)
    return [quote for quote in material_details(source) if not numbers(quote) <= present
            or (re.search(r"\b(?:refunds?|returns?)\b", quote, re.I)
                and normalized(quote) not in normalized(output))]


def claim_issues(output, source):
    issues = []
    extra = numbers(output) - numbers(source)
    if extra:
        issues.append("Numbers not present in the supplied source: " + ", ".join(sorted(extra)))
    for pattern in (
        r"\blatest\b", r"\bexclusive\b", r"\bearly adopters\b",
        r"\blimited edition\b", r"\bfirst[- ]ever\b", r"\brevolutionary\b",
        r"\b(?:innovation|innovative|breakthrough|groundbreaking)\b",
        r"\btest and refine\b",
        r"\bguaranteed\b",
    ):
        if re.search(pattern, output, re.I) and not re.search(pattern, source, re.I):
            if pattern == r"\bguaranteed\b" and re.search(
                r"\b(?:no|without)\b[^.!?\n]{0,40}\bguarantees?\b", source, re.I
            ) and all(re.search(r"\b(?:not|never)\s*$", output[max(0, m.start()-16):m.start()], re.I)
                      for m in re.finditer(pattern, output, re.I)):
                continue
            issues.append("Unsupported promotional claim: " + re.search(pattern, output, re.I).group())
    # Naming a project owner/coordinator does not authorize a presenter or
    # launch role. This finite check does not claim general role entailment.
    for match in re.finditer(
        r"\b(?:owner|coordinator)\s+(?:is\s+|:\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
        source,
    ):
        person = match.group(1)
        for action in re.finditer(
            re.escape(person) + r"\s+(introduces?|presents?|launches?|unveils?|announces?|oversees?|manages?)\b",
            output, re.I,
        ):
            if not re.search(re.escape(person) + r"\s+" + re.escape(action.group(1)) + r"\b", source, re.I):
                issues.append("A presentation or launch role, or operational assignment, was not supplied for " + person)
    for contact in re.finditer(r"\b[Cc]ontact\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", output):
        person = contact.group(1)
        if not any(person in s and re.search(r"\b(?:contact|enquiries|inquiries)\b", s, re.I) for s in sentences(source)):
            issues.append("A contact role was not supplied for " + person)
    if re.search(r"\bbudget\b", source, re.I) and re.search(
        r"(?:USD|[$€£₹])\s*\d[\d,.]*\s*(?:per|each|/)|\b(?:per[- ]unit price|unit price)\b", output, re.I
    ) and not re.search(r"\b(?:unit price|per[- ]unit|each costs)\b", source, re.I):
        issues.append("A project budget cannot be presented as a unit price.")
    return issues


def content_claim_issues(output, source):
    issues = claim_issues(output, source)
    # Additional finite content checks target observed purpose/audience
    # inventions. They are conservative phrase checks, not an entailment model.
    for pattern in (
        r"\b(?:designed|intended|created) to\b",
        r"\bpotential customers\b", r"\bstakeholders\b",
        r"\bjust the beginning\b",
        r"\b(?:new|unique) (?:\w+ ){0,2}experience\b",
    ):
        if re.search(pattern, output, re.I) and not re.search(pattern, source, re.I):
            issues.append("Purpose, audience or experience claim was not supplied: " + re.search(pattern, output, re.I).group())
    for sentence in sentences(source):
        if re.search(r"\b(?:not|no)\b[^.!?]{0,100}\b(?:supplied|specified|documented)\b", sentence, re.I):
            for noun in ("guarantee", "forecast"):
                if re.search(r"\b" + noun + r"s?\b", sentence, re.I) and re.search(
                    r"\bno\b[^.!?\n]{0,100}\b" + noun + r"s?\b[^.!?\n]{0,60}\b(?:apply|exist|offered|available)\b",
                    output, re.I,
                ):
                    issues.append("Unspecified " + noun + " evidence cannot establish its absence or non-applicability.")
    return issues


@contextmanager
def scope(runtime, stage, source="", labels=()):
    previous = runtime.grounding_context
    runtime.grounding_context = {"stage": stage, "source": source, "labels": set(labels)}
    try:
        yield
    finally:
        runtime.grounding_context = previous


def instructions(context):
    if not context:
        return ""
    stage = context["stage"]
    if stage == "support-source":
        return (
            "\nSOURCE PROVENANCE: summary must be ONE contiguous verbatim excerpt copied from Source text, "
            "with complete relevant sentences. Do not summarize the customer's question or allegation as source content. "
            "Keep source labels. relevance may explain whether the quoted documentation answers the question."
        )
    if stage == "research-report":
        return (
            "\nREPORT INVARIANTS: every report, including revised_report inside JSON reviews, MUST keep these "
            "five Markdown headings: " + "; ".join("## " + s for s in SECTIONS) + ". "
            "Keep valid inline [S#] labels in Executive Summary and Findings, not only Source List. "
            "A source's missing experiment data is an evidence gap to describe, not a reason to invent methods or "
            "to presume that a study, experiment or measured outcome exists. Proposed research questions are "
            "suggestions, not claims that such activities happened. Missing study evidence alone does not "
            "make a faithful report defective. Do not label sources untrusted, unreliable or lacking credibility "
            "unless source evidence actually establishes that assessment. Preserve a good report unchanged when no report defect exists."
        )
    if stage == "support-draft":
        return (
            "\nPOLICY REASONING: answerable low-risk answers require valid inline source labels [S#]. "
            "Compare numeric limits: 20 days is WITHIN 30 days; 30 days is within an inclusive 30-day limit; "
            "31 days exceeds it. Respect every eligibility condition. The question is an allegation/request, never documentation. "
            "Use a nonempty next step. Escalation requests must not make unsupported policy or account claims."
        )
    if stage == "document":
        return (
            "\nDOCUMENT FACTS: preserve material quantities, total budgets, dates and conditions in the summary. "
            "Each action item must additionally have evidence: a contiguous verbatim source excerpt for that task. "
            "A project owner is NOT an action assignee. Assign owner only when that person is explicitly tasked with "
            "this action in the source. Leave unknown owner, due_date and priority Not specified. "
            "Do not turn a shipment quantity into a physical dimension or fabricate tasks. GROUNDING_ACTION_EVIDENCE"
        )
    if stage.startswith("content"):
        return (
            "\nCLAIM BOUNDARY: the supplied idea is the ONLY factual evidence. Plans are creative proposals, "
            "never facts about product audience, purpose, availability or features. An owner/coordinator is not "
            "automatically a presenter or launcher: do not say a named person introduces, presents, launches or "
            "announces the project, oversees shipments or manages operations unless the input explicitly states "
            "that action. Missing information is unknown: 'no forecast is supplied' cannot become 'no forecasts "
            "apply' or 'no forecasts exist'. Say what evidence was supplied, not what exists in the world. "
            "Do not claim innovation or "
            "breakthroughs from a routine pilot. Do not add latest, exclusive, "
            "early-adopter positioning, guarantees, contact roles or prices unless explicitly supplied. "
            "Keep all material quantities, dates, budget amounts and refund conditions in the complete script. "
            "Publish only supplied facts with stylistic transitions. Do not invent why the pilot exists, "
            "who it targets, future expansion, or a new customer experience. A creative plan's proposed "
            "audience and purpose must not become claims in the script or captions. "
            "A caption may be shorter but cannot change facts. Creative image prompts are proposed illustrations, "
            "not actual photos of named people or evidence of product contents. Use a suggested, generic CTA. "
            "A review must compare its rewrite against the original idea, not merely the generated plan."
        )
    return ""


def validate_response(value, context):
    if not context:
        return
    stage, source = context["stage"], context["source"]
    if stage == "support-source":
        summary = value["summary"].strip().strip('"')
        complete = [normalized(s) for s in sentences(source)]
        quoted = normalized(summary)
        if (not summary or quoted not in normalized(source)
            or not any(quoted.startswith(s) for s in complete)
            or not any(quoted.endswith(s) for s in complete)):
            raise ValueError("Source digest must quote the documentation verbatim, not the customer question.")
    if stage == "support-draft" and value["resolution_type"] == "answer":
        labels = set(re.findall(r"\[(S\d+)\]", value["answer"]))
        if not labels or labels - context["labels"]:
            raise ValueError("An accepted support answer needs valid inline source citations.")
    if stage == "document":
        for item in value["action_items"]:
            quote = item.get("evidence", "")
            if not quote or normalized(quote) not in normalized(source):
                raise ValueError("An action needs a verbatim source evidence excerpt; omit unsupported tasks.")
    if stage == "content" and "script" in value:
        output = "\n".join([value["title"], value["script"], value["cta"], *value["captions"].values(), *value["hashtags"]])
        issues = content_claim_issues(output, source)
        if issues:
            raise ValueError("Content source checks: " + "; ".join(issues))


def normalize_report_citations(report, sources, runtime):
    valid = {s["label"] for s in sources}

    def expand(match):
        labels = re.findall(r"S\d+", match.group(1))
        if not set(labels) <= valid:
            return match.group()
        return " ".join("[" + label + "]" for label in labels)

    result = re.sub(r"\[(S\d+(?:\s*[,;]\s*S\d+)+)\]", expand, report)
    if result != report:
        runtime.warning("Grouped source citations were expanded into individual evidence links.")
    return result


def report_issues(report, sources):
    headings = list(re.finditer(r"(?m)^\s*#{1,6}\s+(.+?)\s*#*\s*$", report))
    section_map = {}
    for i, match in enumerate(headings):
        section_map[match.group(1).strip().casefold()] = report[match.end():headings[i+1].start() if i+1 < len(headings) else len(report)]
    issues = ["Missing report heading: " + s for s in SECTIONS if s.casefold() not in section_map]
    valid = {s["label"] for s in sources}
    cited = set(re.findall(r"\[(S\d+)\]", report))
    citation_blocks = re.findall(r"\[(S\d+[^\]\n]*)\]", report)
    if any(not re.fullmatch(r"S\d+", block) for block in citation_blocks):
        issues.append("Unsupported source citation format; use individual [S#] labels.")
    if not cited or cited - valid:
        issues.append("Missing or unknown source citation labels.")
    for heading in ("Executive Summary", "Findings"):
        body = section_map.get(heading.casefold(), "")
        if not re.search(r"\[S\d+\]", body):
            issues.append("Missing inline citations in " + heading)
    if valid - cited:
        issues.append("A supplied source is missing from the report: " + ", ".join(sorted(valid - cited)))
    if re.search(r"\buntrusted sources?\b|\black(?:s|ing)? credibility\b", report, re.I):
        evidence = " ".join(s.get("summary", "") for s in sources)
        if not re.search(r"untrusted|credibility", evidence, re.I):
            issues.append("Source credibility was not established by the supplied evidence.")
    return issues


def research_review(value, previous, sources, runtime):
    value = dict(value)
    candidate = normalize_report_citations(value.get("revised_report", ""), sources, runtime)
    value["revised_report"] = candidate
    issues = report_issues(candidate, sources)
    if issues:
        previous_issues = report_issues(previous, sources)
        value["rejected_revision"] = candidate
        value["passes_review"] = False
        value["issues"] = list(dict.fromkeys(value.get("issues", []) + issues))
        if previous_issues:
            raise ValueError("No structurally valid Research report was produced. " + "; ".join(previous_issues))
        value["revised_report"] = previous
        runtime.warning("Review rewrite failed source/structure checks; the last valid report was retained. Inspect Details.")
    history = getattr(runtime, "research_rejections", [])
    if issues:
        history.append({"stage": "review", "revision": candidate, "issues": issues})
        runtime.research_rejections = history
    if history:
        value["rejected_revision_history"] = list(history)
    value["source_checks"] = {"scope": "Headings, citation labels and unsupported credibility wording; not factual certification.", "issues": issues}
    return value


def return_window(question, intent, sources):
    """Narrow explicit rule; ambiguous/conditional/conflicting policies stay with triage."""
    if intent.get("requires_human") or intent.get("severity") == "high":
        return None
    if not re.search(r"\b(?:can|may) I (?:return|refund)\b", question, re.I):
        return None
    if not re.search(r"\bunopened\b", question, re.I) or re.search(r"\b(?:not|except|unless|charge|hack|fire|legal|damaged|opened)\b", question, re.I):
        return None
    requested = [a or b for a, b in re.findall(
        r"\b(?:within|on)\s+(\d+)\s+days?\b|\bon\s+day\s+(\d+)\b", question, re.I)]
    if len(requested) != 1:
        return None
    matches = []
    for source in sources:
        for quote in sentences(source.get("summary", "")):
            if not re.search(r"\b(?:returns?|refunds?)\b", quote, re.I):
                continue
            match = re.search(r"\b(?:returns?|refunds?)\b.{0,100}?\bwithin\s+(\d+)\s+days?\b.{0,80}?\bunopened\b", quote, re.I)
            if not match or re.search(r"\b(?:not|except|unless|approval|business|working|receipt|requires?|provided|authorization|packaging|and)\b", quote, re.I):
                return None
            matches.append((int(match.group(1)), source["label"], quote))
    if not matches or len({m[0] for m in matches}) != 1:
        return None
    limit, label, quote = matches[0]
    days = int(requested[0])
    answer = (
        f"Yes. {days} days is within the {limit}-day return/refund window for unopened items [{label}]."
        if 0 <= days <= limit else
        (f"No. A return on day {days} exceeds the {limit}-day window for unopened items [{label}]."
         if re.search(r"\bon\b", question, re.I) else
         f"Returns are allowed only within {limit} days for unopened items; a return on day {days} is outside that window [{label}].")
    )
    return {"answer": answer, "evidence": quote, "requested_days": days, "limit_days": limit}


def support_draft(value, question, intent, sources, runtime):
    value = dict(value)
    limits = []
    if re.search(r"\b(?:returns?|refunds?)\b", question, re.I):
        for source in sources:
            limits.extend((int(n), source["label"]) for n in re.findall(
                r"\b(?:returns?|refunds?)\b.{0,100}?\bwithin\s+(\d+)\s+days?\b",
                source.get("summary", ""), re.I))
    if len({days for days, _ in limits}) > 1:
        value["model_draft"] = dict(value)
        value.update(resolution_type="escalate", confidence=0.0,
                     answer="The supplied documentation gives conflicting return/refund windows "
                            + " ".join("[" + label + "]" for label in dict.fromkeys(label for _, label in limits)) + ".",
                     escalation_reason="Conflicting documented return/refund windows require human review.",
                     recommended_next_step="Ask support to confirm which documented policy applies.")
        runtime.warning("Conflicting documented return windows were escalated; no policy was selected by guessing.")
        return value
    checked = return_window(question, intent, sources)
    if checked:
        if value.get("answer") != checked["answer"]:
            value["model_draft"] = {k: v for k, v in value.items() if k != "model_draft"}
        value.update(resolution_type="answer", answer=checked["answer"], confidence=0.9,
                     escalation_reason="", recommended_next_step="Follow the cited policy for unopened items; confirm any case-specific conditions with support.")
        value["policy_check"] = {**checked, "scope": "Explicit inclusive calendar-day limit and unopened-item condition only; not a general policy interpreter."}
    return value


def support_final(value, draft, sources, runtime):
    value = dict(value)
    answer = draft.get("answer", "")
    labels = set(re.findall(r"\[(S\d+)\]", answer))
    valid = {s["label"] for s in sources}
    issues = []
    if draft.get("resolution_type") == "answer" and (not labels or labels - valid):
        issues.append("Draft answer lacked valid citations.")
    if draft.get("resolution_type") == "answer":
        source = " ".join(s.get("summary", "") for s in sources)
        # Request numbers can legitimately be repeated (e.g. day 20 vs a
        # documented day-30 limit); they are not invented source-policy facts.
        source += " " + " ".join(numbers(value.get("question", "")))
        if draft.get("policy_check"):
            source += " " + str(draft["policy_check"]["requested_days"])
        issues += claim_issues(answer, source)
    if value["resolution_type"] == "escalate" or issues:
        value["rejected_answer"] = answer
        value["answer"] = "This request should be escalated for human review; no answer was accepted as guidance."
        if issues:
            value.update(resolution_type="escalate", escalation_reason=" ".join(issues))
            runtime.warning("The unsupported support draft was withheld. Inspect Details and the escalation reason.")
    value["source_checks"] = {"scope": "Citation labels and source/request numbers; not general semantic verification.", "issues": issues}
    return value


def restore_details(value, source, runtime, label):
    missing = missing_details(value, source)
    if missing:
        runtime.warning(label + ": missing numerical source details were restored verbatim.")
        value += "\n\nSource details: " + " ".join(missing)
    return value, missing


def content_review(value, source, package, runtime):
    value = dict(value)
    candidate = value.get("revised_script") or package.get("script", "")
    captions = value.get("revised_captions") or package.get("captions", {})
    issues = content_claim_issues(candidate + "\n" + "\n".join(captions.values()), source)
    if issues:
        value["rejected_revision"] = {"script": candidate, "captions": captions}
        candidate = package.get("script", "")
        captions = package.get("captions", {})
        remaining = content_claim_issues(candidate + "\n" + "\n".join(captions.values()), source)
        if remaining:
            raise ValueError("Content contains unsupported claims after review: " + "; ".join(remaining))
        runtime.warning("Content review introduced unsupported claims; the source-checked package was retained.")
    candidate, restored = restore_details(candidate, source, runtime, "Content script")
    if restored:
        issues.append("Review omitted material source details; restored from original input.")
    value.update(revised_script=candidate, revised_captions=captions)
    if issues:
        value.update(passes_review=False, issues=list(dict.fromkeys(value.get("issues", []) + issues)))
    value["source_checks"] = {"scope": "Source numbers, numerical material details, listed promotional, role, purpose and audience phrases; not general factual certification.", "issues": issues}
    return value


def explicit_assignee(source, owner, task):
    if not owner or owner.casefold() in {"unknown", "not specified"}:
        return False
    words = re.findall(r"[a-zA-Z]{3,}", task.casefold())
    words = [w for w in words if w not in {"action", "task", "please", "the"}]
    if not words:
        return False
    verb = words[0]
    forms = {verb, verb + "s", verb + "ed", verb + "ing", verb + verb[-1] + "ed", verb + verb[-1] + "ing"}
    if verb.endswith("e"):
        forms.update({verb[:-1] + "ed", verb[:-1] + "ing"})
    for quote in sentences(source):
        match = re.search(re.escape(owner) + r"\s+(?:(?:must|will|shall|is assigned to|is responsible for|has been tasked with|is to)\s+)?(?:" + "|".join(re.escape(v) for v in forms) + r")\b", quote, re.I)
        if match:
            return True
    return False


def document_analysis(value, source, runtime):
    value = json.loads(json.dumps(value))
    issues = claim_issues(value["summary"], source)
    if issues:
        raise ValueError("Document summary contains unsupported details: " + "; ".join(issues))
    value["summary"], restored = restore_details(value["summary"], source, runtime, "Document summary")
    repairs = ["Missing material source details restored verbatim."] if restored else []
    for item in value["action_items"]:
        owner = item["owner"]
        if owner.casefold() not in {"unknown", "not specified", ""} and not explicit_assignee(item.get("evidence", ""), owner, item["task"]):
            item["proposed_owner"] = owner
            item["owner"] = "Not specified"
            repairs.append("An inferred action assignee was removed.")
        if item["priority"].casefold() not in {"unknown", "not specified", ""} and not any(
            re.search(r"\bpriority\b", s, re.I) and item["priority"].casefold() in s.casefold()
            for s in sentences(item.get("evidence", ""))
        ):
            item["proposed_priority"] = item["priority"]
            item["priority"] = "Not specified"
            repairs.append("An inferred priority was removed.")
        if item["due_date"].casefold() not in {"unknown", "not specified", ""} and normalized(item["due_date"]) not in normalized(item.get("evidence", "")):
            item["proposed_due_date"] = item["due_date"]
            item["due_date"] = "Not specified"
            repairs.append("An unsupported action date was removed.")
    if repairs:
        runtime.warning("Document source checks corrected inferred or missing details. Inspect Details.")
    value["source_checks"] = {"scope": "Source numbers, verbatim task evidence and explicit assignment grammar; not general semantic verification.", "repairs": list(dict.fromkeys(repairs))}
    return value
