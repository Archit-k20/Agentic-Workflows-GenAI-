import type { Sample } from "../sample-state";
import { source } from "./source";
const sample = {
  input: {
    topic: "How could a campus repair service improve access and trust?",
    urls: "",
  },
  result: {
    tool: "research",
    plan: {
      goal: "Evaluate a fictional campus repair pilot",
      sub_questions: [
        "How is demand managed?",
        "What needs specialist oversight?",
      ],
      report_sections: ["Executive Summary", "Findings", "Risks and Gaps"],
    },
    sources: [source],
    source_errors: [],
    invalid_urls: [],
    draft_report: "Appointments may make demand easier to manage. [S1]",
    final_report:
      "# Small service. Clear boundaries.\n\n## Executive Summary\nA fictional campus repair pilot uses scheduled appointments to make repair support more predictable. Its most important design choice is a clear boundary between routine fixes and specialist work. [S1]\n\n## Findings\n**Access starts with predictability.** Appointment slots distribute demand and help volunteers prepare the right parts. [S1]\n\n**Trust comes from knowing when to stop.** Repeat faults and electrical repairs should move to a qualified specialist. [S1]\n\n## Risks and Gaps\nThese synthetic notes do not provide measured outcomes, cost data, or safety testing. The benefits remain hypotheses. [S1]\n\n## Recommended Next Questions\nTrack wait times, repeat visits, and referrals before expanding the pilot.\n\n## Source List\n[S1] Synthetic campus repair field notes.",
    critique: {
      passes_review: true,
      issues: [],
      revised_report: "Synthetic model review for demonstration only.",
    },
    citation_check: {
      has_any_citation: true,
      cited_labels: ["S1"],
      unknown_labels: [],
    },
  },
} satisfies Sample;
export default sample;
