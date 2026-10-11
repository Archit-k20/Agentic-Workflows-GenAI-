import { tools, type ToolId } from "./tools";
import { hasSample } from "./sample-state";
export type ToolPresentation = {
  family:
    | "reading"
    | "image"
    | "audio"
    | "code"
    | "content"
    | "documents"
    | "qa"
    | "support";
  preview: string;
  purpose: string;
  decision: string;
  limitation: string;
  sample: boolean;
};
const descriptions: Record<ToolId, Omit<ToolPresentation, "sample">> = {
  research: {
    family: "reading",
    preview: "Small service. Clear boundaries.",
    purpose: "Read selected sources and build a grounded report.",
    decision:
      "The report keeps citations, source digests and the model review available together.",
    limitation:
      "A citation identifies a source. It does not independently establish that a claim is true.",
  },
  documents: {
    family: "documents",
    preview: "A brief becomes a set of next steps.",
    purpose: "Find useful structure in everyday documents.",
    decision:
      "Summary, entities, action items and risks are grouped by file so their origin stays visible.",
    limitation:
      "Missing owners and dates can remain unknown. Extraction and model interpretation can make mistakes.",
  },
  code: {
    family: "code",
    preview: "A function, with its checks in view.",
    purpose: "Turn a described task into code you can inspect.",
    decision:
      "Syntax and compilation checks run separately, with one repair attempt when needed.",
    limitation:
      "Passing these checks does not prove functional correctness or security.",
  },
  content: {
    family: "content",
    preview: "One brief. Several ways to tell it.",
    purpose: "Develop a script and related content from a brief.",
    decision:
      "The plan, final script, captions, image prompts and review remain separate artifacts.",
    limitation:
      "Model review can miss unsupported claims. Image prompts are text, not generated images.",
  },
  support: {
    family: "support",
    preview: "Know when to ask a specialist.",
    purpose: "Draft a sourced response or a clear escalation.",
    decision:
      "The decision includes its evidence and recommended next step, including human review when needed.",
    limitation:
      "Confidence is a model score, not a calibrated probability. Check policies before acting.",
  },
  "text-summary": {
    family: "reading",
    preview: "Source text → Summary",
    purpose: "Bring a long passage into focus.",
    decision: "The source remains beside its summary so you can compare them.",
    limitation:
      "Summaries compress information and may omit important context.",
  },
  "youtube-summary": {
    family: "reading",
    preview: "Transcript → Summary",
    purpose: "Read the main points of a video.",
    decision:
      "You can paste a transcript when YouTube extraction is unavailable.",
    limitation:
      "Transcript availability depends on the source; visuals are not analysed.",
  },
  "article-summary": {
    family: "reading",
    preview: "Public article → Summary",
    purpose: "Read the essentials of a public article.",
    decision:
      "URL extraction and summarisation are separate observable stages.",
    limitation:
      "Paywalls, blocked pages and incomplete extraction can prevent a useful summary.",
  },
  "file-summary": {
    family: "reading",
    preview: "PDF or DOCX → Summary",
    purpose: "Get an overview of a document.",
    decision:
      "The original filename stays visible with the result and processing notes.",
    limitation:
      "File and extraction limits apply; a summary is not an exhaustive document review.",
  },
  ocr: {
    family: "reading",
    preview: "Image → Extracted text",
    purpose: "Turn text inside an image into copyable text.",
    decision:
      "The image and extracted text appear together, with an explicit optional summary action.",
    limitation:
      "Small, handwritten, rotated or low-contrast text may be misread.",
  },
  image: {
    family: "image",
    preview: "Your description → An image",
    purpose: "Explore a visual idea through a written prompt.",
    decision:
      "Free generation uses Cloudflare, with a private Hugging Face fallback for confirmed capacity failures.",
    limitation:
      "Both providers have limits. Exact counts, lettering and complex spatial instructions can be missed.",
  },
  speech: {
    family: "audio",
    preview: "Written words → Speech",
    purpose: "Give a passage a spoken voice.",
    decision:
      "Free-mode voices have bundled previews so you can listen before generating.",
    limitation:
      "Pronunciation and emphasis vary. The free voices are English-first.",
  },
  captions: {
    family: "reading",
    preview: "Video or transcript → Copyable text",
    purpose: "Read or reuse a video's transcript.",
    decision:
      "Pasted transcripts provide an alternative when remote extraction fails.",
    limitation:
      "This tool extracts available text; it does not transcribe arbitrary audio or video.",
  },
  "document-qa": {
    family: "qa",
    preview: "Documents + Question → Sourced answer",
    purpose: "Ask a question about your selected documents.",
    decision:
      "Documents are processed first; retrieved chunks remain inspectable alongside the answer.",
    limitation:
      "Retrieval can miss relevant text. A source excerpt is not a factual guarantee.",
  },
  "url-qa": {
    family: "qa",
    preview: "Articles + Question → Sourced answer",
    purpose: "Find an answer within selected public articles.",
    decision:
      "Extraction and indexing happen before questions so the context is explicit and reusable.",
    limitation:
      "It searches the selected context, not the entire web. Changing execution mode requires reprocessing.",
  },
};
export const presentation = Object.fromEntries(
  tools.map((t) => [t.id, { ...descriptions[t.id], sample: hasSample(t.id) }]),
) as Record<ToolId, ToolPresentation>;
export function filterTools(query: string, group: string) {
  const q = query.trim().toLowerCase();
  return tools.filter(
    (t) =>
      (group === "All" || t.group === group) &&
      `${t.name} ${t.description} ${t.group}`.toLowerCase().includes(q),
  );
}
export const portfolio = "https://portfolio-updated-ak.vercel.app/";
