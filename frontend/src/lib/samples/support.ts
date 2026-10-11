import type { Sample } from "../sample-state";
import { source } from "./source";
const sample = {
  input: {
    question: "Can I bring a damaged power adapter to the repair pilot?",
  },
  result: {
    tool: "support",
    intent: { category: "Safety / specialist repair", requires_human: true },
    sources: [source],
    source_errors: [],
    invalid_urls: [],
    draft: {
      resolution_type: "escalate",
      answer: "Please ask a qualified specialist to assess the adapter. [S1]",
      confidence: 0.82,
      recommended_next_step: "Contact the specialist repair desk.",
      escalation_reason: "Electrical work falls outside the pilot scope.",
    },
    final: {
      question: "Can I bring a damaged power adapter?",
      intent: { requires_human: true },
      resolution_type: "escalate",
      answer:
        "Please ask a qualified specialist to assess the adapter. The pilot’s routine repair scope excludes electrical faults. [S1]",
      confidence: 0.82,
      recommended_next_step: "Contact the specialist repair desk.",
      escalation_reason: "Electrical work falls outside the pilot scope.",
      citation_check: { cited_labels: ["S1"], unknown_labels: [] },
    },
  },
} satisfies Sample;
export default sample;
