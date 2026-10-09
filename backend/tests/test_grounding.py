"""Regression cases from actual Llama failures; no model/billing calls."""

import json
import pytest
from backend import grounding as g
from backend.providers import Runtime
from backend.structured import schema_for

POLICY = "Customer refunds are available within 30 days only for unopened items."
SOURCE = "Project Alder ships 32 kits on November 9, 2026. The owner is Priya Shah. The budget is USD 740. " + POLICY
SOURCES = [{"label": "S1", "summary": SOURCE}]
REPORT = "\n\n".join([
    "## Executive Summary\nProject Alder plans 32 kits [S1].",
    "## Findings\nThe budget is USD 740 [S1].",
    "## Risks and Gaps\nNo performance outcomes are supplied [S1].",
    "## Recommended Next Questions\nSuggested: ask for measured outcomes.",
    "## Source List\n[S1] Pilot brief",
])


def test_report_revision_cannot_remove_citations_and_headings():
    runtime = Runtime("free", "research")
    rejected = {"passes_review": True, "issues": [], "revised_report": "Alder plans 32 kits."}
    accepted = g.research_review(rejected, REPORT, SOURCES, runtime)
    assert accepted["revised_report"] == REPORT
    assert accepted["rejected_revision"] == rejected["revised_report"]
    assert accepted["passes_review"] is False and runtime.warnings
    assert not g.report_issues(accepted["revised_report"], SOURCES)


def test_valid_report_review_is_not_forced_to_fail():
    value = g.research_review({"passes_review": True, "issues": [], "revised_report": REPORT}, REPORT, SOURCES, Runtime("free", "research"))
    assert value["passes_review"] is True and not value["source_checks"]["issues"]


def test_grouped_citations_become_individual_clickable_labels():
    sources = SOURCES + [{"label": "S2", "summary": "A conflicting source."}]
    report = REPORT.replace("32 kits [S1]", "32 kits [S1, S2]") + "\n[S2] Other source"
    runtime = Runtime("free", "research")
    accepted = g.research_review({"passes_review": True, "revised_report": report}, REPORT, sources, runtime)
    assert "[S1] [S2]" in accepted["revised_report"]
    assert "[S1, S2]" not in accepted["revised_report"]
    assert not g.report_issues(accepted["revised_report"], sources)
    assert runtime.warnings


def test_unknown_grouped_citation_is_not_silently_discarded():
    bad = REPORT + "\nClaim [S1, S99]"
    runtime = Runtime("free", "research")
    accepted = g.research_review({"passes_review": True, "revised_report": bad}, REPORT, SOURCES, runtime)
    assert accepted["passes_review"] is False
    assert accepted["revised_report"] == REPORT
    assert "[S1, S99]" in accepted["rejected_revision"]


@pytest.mark.parametrize("verb", ["introduces", "presents", "launches", "announces"])
def test_project_owner_is_not_invented_as_presenter(verb):
    issues = g.claim_issues(f"Priya Shah {verb} Project Alder.", SOURCE)
    assert any("presentation or launch role" in issue for issue in issues)
    assert not g.claim_issues(f"Priya Shah {verb} Project Alder.", SOURCE + f" Priya Shah {verb} Project Alder.")


def test_routine_pilot_is_not_claimed_as_innovation():
    assert g.claim_issues("A lighting innovation.", SOURCE)
    assert not g.claim_issues("A lighting innovation.", SOURCE + " A lighting innovation.")


@pytest.mark.parametrize("claim", [
    "This pilot is designed to introduce the project to potential customers and stakeholders.",
    "A new lighting experience is coming soon.",
    "This pilot is just the beginning.",
])
def test_proposed_content_purpose_or_audience_cannot_become_a_source_fact(claim):
    assert g.content_claim_issues(claim, SOURCE)
    assert not g.content_claim_issues(claim, SOURCE + " " + claim)


def test_content_review_rejects_unprovided_purpose_and_retains_factual_package():
    original = {"script": SOURCE, "captions": {"x": "Alder plans 32 kits."}}
    review = {"passes_review": True, "revised_script": "This pilot introduces Project Alder to potential customers and stakeholders.", "revised_captions": {"x": "A new kit experience."}}
    result = g.content_review(review, SOURCE, original, Runtime("free", "content"))
    assert result["passes_review"] is False
    assert result["revised_script"] == SOURCE
    assert result["revised_captions"] == original["captions"]


@pytest.mark.parametrize("verb", ["oversees", "manages"])
def test_owner_does_not_become_an_operational_assignee_in_content(verb):
    assert g.content_claim_issues(f"Priya Shah {verb} a shipment of 32 kits.", SOURCE)
    explicit = SOURCE + f" Priya Shah {verb} a shipment of 32 kits."
    assert not g.content_claim_issues(f"Priya Shah {verb} a shipment of 32 kits.", explicit)


@pytest.mark.parametrize("claim", [
    "No delivery guarantees or revenue forecasts apply to this run.",
    "No revenue forecasts exist for this project.",
    "No delivery guarantees are available.",
])
def test_unspecified_guarantee_or_forecast_does_not_establish_absence(claim):
    source = SOURCE + " No delivery guarantee or revenue forecast is supplied."
    assert g.content_claim_issues(claim, source)
    assert not g.content_claim_issues("No delivery guarantee or revenue forecast is supplied.", source)


def test_explicit_absence_is_allowed_without_converting_missing_information():
    source = SOURCE + " No delivery guarantees apply to this pilot."
    assert not g.content_claim_issues("No delivery guarantees apply to this pilot.", source)


def test_content_review_keeps_facts_when_revision_converts_unknown_to_absence():
    source = SOURCE + " No delivery guarantee or revenue forecast is supplied."
    original = {"script": source, "captions": {"x": POLICY}}
    result = g.content_review({"passes_review": True, "revised_script": "No delivery guarantees or revenue forecasts apply.", "revised_captions": {"x": POLICY}}, source, original, Runtime("local", "content"))
    assert result["passes_review"] is False
    assert result["revised_script"] == source
    assert result["rejected_revision"]["script"]


def test_report_rejects_citations_only_in_source_list():
    weak = REPORT.replace("32 kits [S1]", "32 kits").replace("USD 740 [S1]", "USD 740")
    assert any("Executive Summary" in issue for issue in g.report_issues(weak, SOURCES))
    assert any("Findings" in issue for issue in g.report_issues(weak, SOURCES))


def test_no_invalid_report_is_promoted_when_both_candidates_fail():
    with pytest.raises(ValueError, match="No structurally valid"):
        g.research_review({"revised_report": "Bad"}, "Also bad", SOURCES, Runtime("free", "research"))


@pytest.mark.parametrize("days,answer", [(20, "Yes"), (30, "Yes"), (31, "No")])
def test_refund_boundary_reasoning_keeps_original_draft_in_details(days, answer):
    runtime = Runtime("free", "support")
    question = f"Can I return an unopened item on day {days}?"
    original = {"resolution_type": "answer", "answer": "No, 30 is not 20 [S1].", "confidence": 0.8}
    checked = g.support_draft(original, question, {"requires_human": False, "severity": "low"}, SOURCES, runtime)
    assert checked["answer"].startswith(answer) and "[S1]" in checked["answer"]
    assert checked["model_draft"] == original
    assert checked["policy_check"]["limit_days"] == 30
    final = g.support_final({"resolution_type": "answer", "answer": checked["answer"]}, checked, SOURCES, runtime)
    assert final["resolution_type"] == "answer" and not final["source_checks"]["issues"]


@pytest.mark.parametrize("question", [
    "Can I return an opened item within 20 days?",
    "Can I return an unopened item after 20 days?",
    "Can I return an unopened item within -20 days?",
    "Can I return an unopened item within 20 days after it caused a fire?",
])
def test_ambiguous_or_high_risk_questions_do_not_use_narrow_policy_rule(question):
    assert g.return_window(question, {}, SOURCES) is None


@pytest.mark.parametrize("policy", [
    POLICY + " Returns require a receipt.",
    "Refunds are available within 30 business days for unopened items.",
    "Refunds are available within 30 days for unopened items unless damaged.",
    "Refunds are not available within 30 days for unopened items.",
])
def test_conditional_policies_are_not_simplified(policy):
    assert g.return_window("Can I return an unopened item within 20 days?", {}, [{"label": "S1", "summary": policy}]) is None


def test_conflicting_policy_windows_are_not_resolved_by_guessing():
    sources = SOURCES + [{"label": "S2", "summary": POLICY.replace("30", "14")}]
    assert g.return_window("Can I return an unopened item within 20 days?", {}, sources) is None


def test_escalated_invalid_answer_is_withheld_not_deleted():
    value = g.support_final({"resolution_type": "escalate", "answer": "Wrong refund rule"}, {"resolution_type": "answer", "answer": "Wrong refund rule"}, SOURCES, Runtime("free", "support"))
    assert value["rejected_answer"] == "Wrong refund rule"
    assert "Wrong refund rule" not in value["answer"]
    assert value["resolution_type"] == "escalate"


def test_source_digest_cannot_restate_customer_allegation():
    context = {"stage": "support-source", "source": SOURCE}
    with pytest.raises(ValueError, match="verbatim"):
        g.validate_response({"summary": "The customer was charged twice."}, context)
    g.validate_response({"summary": POLICY}, context)


def test_content_revision_cannot_invent_audience_or_discard_conditions():
    original = {"script": SOURCE, "captions": {"x": "Alder plans 32 kits."}}
    value = g.content_review({"passes_review": True, "issues": [], "revised_script": "This exclusive pilot is designed for early adopters.", "revised_captions": original["captions"]}, SOURCE, original, Runtime("free", "content"))
    assert value["revised_script"] == SOURCE
    assert value["passes_review"] is False
    assert value["rejected_revision"]["script"].startswith("This exclusive")


def test_material_budget_and_conditions_are_restored_from_source():
    output, repaired = g.restore_details("Alder plans 32 kits on November 9, 2026.", SOURCE, Runtime("free", "content"), "Script")
    assert "USD 740" in output and POLICY in output
    assert repaired and not g.missing_details(output, SOURCE)


def test_unsupported_contact_and_latest_claims_are_detected():
    issues = g.claim_issues("Contact Priya Shah about her latest initiative.", SOURCE)
    assert any("contact role" in issue for issue in issues)
    assert any("latest" in issue for issue in issues)
    assert not g.claim_issues("Contact Priya Shah.", "Contact Priya Shah for information.")


def test_amount_formatting_does_not_create_false_number_mismatches():
    assert g.numbers("USD 1,250.00 [S1]") == g.numbers("$1250")


def test_document_owner_is_not_an_action_assignee():
    value = {"summary": "Project Alder plans 32 kits.", "action_items": [{"task": "Ship 32 kits", "owner": "Priya Shah", "priority": "High", "due_date": "November 9, 2026", "evidence": SOURCE}]}
    checked = g.document_analysis(value, SOURCE, Runtime("free", "documents"))
    item = checked["action_items"][0]
    assert item["owner"] == "Not specified" and item["proposed_owner"] == "Priya Shah"
    assert item["priority"] == "Not specified"
    assert item["due_date"] == "November 9, 2026"
    assert "USD 740" in checked["summary"]


@pytest.mark.parametrize("quote,expected", [
    ("Priya Shah must ship 32 kits by November 9, 2026.", True),
    ("Priya Shah ships 32 kits on November 9, 2026.", True),
    ("The owner is Priya Shah. Project Alder ships 32 kits.", False),
    ("Priya Shah is responsible for Project Alder. Project Alder ships 32 kits.", False),
    ("Deliver 32 kits to Priya Shah.", False),
    ("Priya Shah will review the budget. Ship 32 kits.", False),
])
def test_only_explicit_task_assignment_sets_owner(quote, expected):
    assert g.explicit_assignee(quote, "Priya Shah", "Ship 32 kits") is expected


def test_action_evidence_must_come_from_source_and_is_required_in_local_schema():
    with pytest.raises(ValueError, match="verbatim"):
        g.validate_response({"action_items": [{"evidence": "Priya Shah must ship tomorrow."}]}, {"stage": "document", "source": SOURCE})
    schema = schema_for("document_type GROUNDING_ACTION_EVIDENCE")
    assert "evidence" in schema["properties"]["action_items"]["items"]["required"]


def test_grounding_scope_is_request_local_and_restored_after_failure():
    runtime = Runtime("free", "content")
    with pytest.raises(RuntimeError):
        with g.scope(runtime, "content", "Private synthetic idea"):
            assert runtime.grounding_context["source"] == "Private synthetic idea"
            raise RuntimeError("Test failure")
    assert runtime.grounding_context is None


def test_source_quote_cannot_drop_an_eligibility_condition():
    with pytest.raises(ValueError, match="verbatim"):
        g.validate_response({"summary": "Customer refunds are available within 30 days"},
                            {"stage": "support-source", "source": POLICY})


def test_conflicting_limits_force_triage_instead_of_model_guess():
    sources = SOURCES + [{"label": "S2", "summary": POLICY.replace("30", "14")}]
    checked = g.support_draft({"answer": "Yes [S1].", "confidence": 0.9},
                              "Can I return an unopened item within 20 days?", {}, sources, Runtime("free", "support"))
    assert checked["resolution_type"] == "escalate" and checked["confidence"] == 0
    assert checked["model_draft"]["answer"] == "Yes [S1]."


def test_support_can_repeat_request_numbers_without_inventing_policy_numbers():
    draft = {"resolution_type": "answer", "answer": "At 20 days a receipt is still required [S1]."}
    sources = [{"label": "S1", "summary": POLICY + " Returns require a receipt."}]
    checked = g.support_final({**draft, "question": "Can I return it within 20 days without a receipt?"},
                              draft, sources, Runtime("free", "support"))
    assert checked["resolution_type"] == "answer" and not checked["source_checks"]["issues"]
    draft["answer"] = "There is a 60-day policy [S1]."
    checked = g.support_final({**draft, "question": "Can I return it within 20 days?"},
                              draft, sources, Runtime("free", "support"))
    assert checked["resolution_type"] == "escalate"


def test_source_denial_is_not_mistaken_for_a_promotional_guarantee():
    source = "No delivery guarantee or revenue forecast is supplied."
    assert not g.claim_issues("Delivery is not guaranteed.", source)
    assert g.claim_issues("Delivery is guaranteed.", source)
    assert g.claim_issues("Delivery is not guaranteed; performance is guaranteed.", source)
