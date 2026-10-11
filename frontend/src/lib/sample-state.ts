import type { Result } from "./types";
import type { ToolId } from "./tools";
import type { Draft } from "../components/provider";
export type Sample = { input: Record<string, string>; result: Result };
export type SampleId =
  | "research"
  | "documents"
  | "code"
  | "content"
  | "support";
export const sampleLabel = "Sample result — no live AI request";
export const sampleIds: SampleId[] = [
  "research",
  "documents",
  "code",
  "content",
  "support",
];
export function hasSample(id: ToolId): id is SampleId {
  return sampleIds.includes(id as SampleId);
}
export const sampleLoaders: Record<
  SampleId,
  () => Promise<{ default: Sample }>
> = {
  research: () => import("./samples/research"),
  documents: () => import("./samples/documents"),
  code: () => import("./samples/code"),
  content: () => import("./samples/content"),
  support: () => import("./samples/support"),
};
// A sample is a derived view, never an update to the live draft store.
export function sampleDraft(sample: Sample): Draft {
  return {
    input: { ...sample.input },
    files: [],
    fileIds: [],
    result: sample.result,
    status: "success",
    stages: [],
    warnings: [],
    sample: true,
  };
}
export function displayedDraft(live: Draft, sample?: Sample): Draft {
  return sample ? sampleDraft(sample) : live;
}
