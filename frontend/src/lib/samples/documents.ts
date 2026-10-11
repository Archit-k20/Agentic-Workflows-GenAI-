import type { Sample } from "../sample-state";
import { source } from "./source";
const sample = {
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
} satisfies Sample;
export default sample;
