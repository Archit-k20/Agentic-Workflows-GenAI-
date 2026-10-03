import type { Result } from "./types";
export const sampleLabel = "Sample result — no live AI request";
const source = {
  text: "",
  metadata: {},
  label: "S1",
  title: "Synthetic field notes: a campus repair service",
  url: "",
  summary:
    "A fictional pilot pairs student volunteers with a small inventory of repair parts. Appointments reduce queues, while repeat faults require specialist review.",
  key_points: [
    "Appointments help distribute demand.",
    "Escalation is needed for electrical faults.",
  ],
  relevance: "Illustrates a small, bounded service workflow.",
};
export const samples: Partial<
  Record<string, { input: Record<string, string>; result: Result }>
> = {
  research: {
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
  },
  documents: {
    input: {},
    result: {
      tool: "documents",
      documents: [
        {
          name: "campus-pilot-brief.txt",
          source_type: "txt",
          text_preview:
            "Fictional planning brief: Mira Chen will prepare the repair inventory by Oct 14. The pilot needs a safety review before opening.",
          analysis: {
            document_type: "Project brief",
            summary:
              "A fictional repair pilot needs an inventory, a booking form, and a safety review before launch.",
            entities: {
              people: ["Mira Chen"],
              organizations: ["Campus Repair Collective"],
              emails: ["mira@example.com"],
              dates: ["Oct 14"],
            },
            action_items: [
              {
                task: "Prepare repair inventory",
                owner: "Mira Chen",
                due_date: "Oct 14",
                priority: "High",
              },
              {
                task: "Arrange specialist safety review",
                owner: "Unknown",
                due_date: "Not specified",
                priority: "High",
              },
            ],
            risks: [
              "Safety review has no assigned owner.",
              "This document is synthetic.",
            ],
          },
        },
      ],
      errors: [],
    },
  },
  code: {
    input: {
      prompt:
        "Write a Python function that returns unique repair categories in their original order.",
      language: "python",
    },
    result: {
      tool: "code",
      language: "python",
      initial_code:
        "def unique_categories(categories):\n    return list(dict.fromkeys(categories))\n",
      final_code:
        "def unique_categories(categories):\n    return list(dict.fromkeys(categories))\n",
      repair_attempted: false,
      initial_verification: {
        language: "python",
        passed: true,
        checks: [
          {
            name: "ast_parse",
            passed: true,
            details: "Synthetic example of an AST parse result.",
          },
          {
            name: "py_compile",
            passed: true,
            details: "Synthetic example of a bytecode compilation result.",
          },
        ],
      },
      final_verification: {
        language: "python",
        passed: true,
        checks: [
          {
            name: "ast_parse",
            passed: true,
            details: "Synthetic example of an AST parse result.",
          },
          {
            name: "py_compile",
            passed: true,
            details: "Synthetic example of a bytecode compilation result.",
          },
        ],
      },
    },
  },
  content: {
    input: {
      idea: "Introduce a fictional campus repair pilot",
      tone: "educational",
    },
    result: {
      tool: "content",
      plan: {
        content_angle: "Repair is a shared skill",
        audience: "Students",
        hooks: ["Give your everyday essentials a second life."],
        sections: ["Invitation", "What to bring", "Safety boundary"],
        cta: "Book a pilot appointment.",
      },
      package: {
        title: "A second life for everyday things",
        script:
          "Before you replace it, see if you can repair it. Our fictional campus pilot pairs everyday problems with practical skills. Bring a loose handle or a worn backpack. Specialist repairs get a clear referral. Book a pilot appointment and help us learn.",
        image_prompts: [
          "Editorial overhead photograph of a neatly arranged repair kit, canvas bag, and handwritten appointment card; warm daylight and generous negative space.",
          "Close-up of hands stitching a canvas strap on a clean wooden workbench; natural textures, restrained colors.",
        ],
        captions: {
          linkedin:
            "A small repair pilot with a clear scope and a learning mindset.",
        },
        hashtags: ["#RepairCulture", "#CampusCommunity"],
        cta: "Book a pilot appointment.",
      },
      critique: {
        passes_review: true,
        issues: [],
        revised_script: "Synthetic review.",
        revised_captions: {},
      },
      final_script:
        "Before you replace it, see if you can repair it. Our fictional campus pilot pairs everyday problems with practical skills. Bring a loose handle or a worn backpack. Specialist repairs get a clear referral. Book a pilot appointment and help us learn.",
      final_captions: {
        linkedin:
          "A small repair pilot. A clear safety boundary. A chance to learn together.",
        x: "Repair, reuse, repeat. Our fictional campus pilot starts with everyday fixes.",
      },
      audio_path: null,
      audio_error: null,
      artifact_id: null,
    },
  },
  support: {
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
  },
};
