import type { ToolId } from "./tools";
import type { RunInput } from "./types";
export function buildInput(
  tool: ToolId,
  input: Record<string, string>,
  file_ids: string[],
  context_id = "",
): RunInput {
  const voice = input.voice as
    | "alloy"
    | "echo"
    | "fable"
    | "onyx"
    | "nova"
    | "shimmer"
    | "af_heart"
    | "af_bella"
    | "af_nicole"
    | "am_michael"
    | "am_fenrir"
    | "bf_emma";
  const urls = (input.urls || "")
    .split("\n")
    .map((u) => u.trim())
    .filter(Boolean);
  switch (tool) {
    case "research":
      return { tool, topic: input.topic.trim(), urls };
    case "support":
      return { tool, question: input.question.trim(), urls };
    case "documents":
    case "file-summary":
    case "ocr":
      return { tool, file_ids };
    case "text-summary":
      return { tool, text: input.text };
    case "youtube-summary":
    case "captions":
      return input.source_type === "transcript"
        ? { tool, transcript_text: input.transcript_text }
        : { tool, url: input.url.trim() };
    case "article-summary":
      return { tool, url: input.url.trim() };
    case "image":
      return { tool, prompt: input.prompt.trim() };
    case "speech":
      return { tool, text: input.text, voice };
    case "code":
      return {
        tool,
        prompt: input.prompt.trim(),
        language: input.language as
          | "python"
          | "javascript"
          | "java"
          | "c"
          | "c++",
      };
    case "content":
      return {
        tool,
        idea: input.idea.trim(),
        tone: input.tone as
          | "professional"
          | "playful"
          | "educational"
          | "launch-ready"
          | "social-first",
        platforms: input.platforms.split(",") as (
          | "linkedin"
          | "x"
          | "instagram"
          | "youtube"
          | "blog"
        )[],
        include_audio: input.include_audio === "true",
        voice,
      };
    case "document-qa":
    case "url-qa":
      return { tool, context_id, question: input.question.trim() };
  }
}
