import { it, expect } from "vitest";
import { buildInput } from "./inputs";
import { tools } from "./tools";
const input = {
  text: "Text",
  url: "https://youtu.be/abcdefghijk",
  urls: "https://example.com/one\nhttps://example.com/two",
  topic: "Topic",
  question: "Question",
  prompt: "Task",
  idea: "Idea",
  voice: "shimmer",
  language: "c++",
  tone: "social-first",
  platforms: "x,blog",
  include_audio: "true",
};
it("builds a discriminated request for all fifteen tools", () => {
  for (const tool of tools) {
    const request = buildInput(tool.id, input, ["file-id"], "context-id");
    expect(request.tool).toBe(tool.id);
    if ("file_ids" in request) expect(request.file_ids).toEqual(["file-id"]);
    if ("context_id" in request) expect(request.context_id).toBe("context-id");
  }
});
it("retains all creative options and source URLs", () => {
  expect(buildInput("content", input, [])).toEqual({
    tool: "content",
    idea: "Idea",
    tone: "social-first",
    platforms: ["x", "blog"],
    include_audio: true,
    voice: "shimmer",
  });
  expect(buildInput("code", input, [])).toEqual({
    tool: "code",
    prompt: "Task",
    language: "c++",
  });
  expect(buildInput("research", input, [])).toEqual({
    tool: "research",
    topic: "Topic",
    urls: ["https://example.com/one", "https://example.com/two"],
  });
});
it("uses pasted transcripts and preserves free voice choices", () => {
  expect(
    buildInput(
      "youtube-summary",
      {
        ...input,
        source_type: "transcript",
        transcript_text: "Full transcript",
      },
      [],
    ),
  ).toEqual({ tool: "youtube-summary", transcript_text: "Full transcript" });
  expect(
    buildInput(
      "captions",
      {
        ...input,
        source_type: "transcript",
        transcript_text: "Full transcript",
      },
      [],
    ),
  ).toEqual({ tool: "captions", transcript_text: "Full transcript" });
  expect(buildInput("speech", { ...input, voice: "af_heart" }, [])).toEqual({
    tool: "speech",
    text: "Text",
    voice: "af_heart",
  });
});
