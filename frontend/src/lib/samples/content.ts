import type { Sample } from "../sample-state";
import { source } from "./source";
const sample = {
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
} satisfies Sample;
export default sample;
