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
    | "shimmer";
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
      return { tool, text: input.text.trim() };
    case "youtube-summary":
    case "article-summary":
    case "captions":
      return { tool, url: input.url.trim() };
    case "image":
      return { tool, prompt: input.prompt.trim() };
    case "speech":
      return { tool, text: input.text.trim(), voice };
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
