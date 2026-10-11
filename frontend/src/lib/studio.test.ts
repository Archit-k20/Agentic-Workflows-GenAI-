import { describe, it, expect } from "vitest";
import { emptyDraft } from "../components/provider";
import { displayedDraft, hasSample, sampleLoaders } from "./sample-state";
import { samples } from "./samples";
import { tools } from "./tools";
import { presentation, filterTools } from "./presentation";
describe("studio presentation contracts", () => {
  it("covers the original fifteen tool IDs without renaming routes", () => {
    expect(Object.keys(presentation).sort()).toEqual(
      tools.map((t) => t.id).sort(),
    );
    expect(Object.values(presentation).filter((p) => p.sample)).toHaveLength(5);
    for (const p of Object.values(presentation)) {
      expect(p.decision.length).toBeGreaterThan(20);
      expect(p.limitation.length).toBeGreaterThan(20);
    }
  });
  it("filters names, groups and descriptions without hiding tools from the default view", () => {
    expect(filterTools("", "All")).toHaveLength(15);
    expect(filterTools("", "Generator")).toHaveLength(5);
    expect(filterTools("  code ", "All").map((t) => t.id)).toContain("code");
    expect(filterTools("code", "Summarizer")).toHaveLength(0);
  });
  it("keeps dynamic fixtures equivalent to the five existing samples", async () => {
    for (const [id, loader] of Object.entries(sampleLoaders)) {
      expect((await loader()).default).toEqual(
        samples[id as keyof typeof samples],
      );
    }
    expect(hasSample("image")).toBe(false);
  });
  it("never replaces input, files, context or a processing result when presenting a sample", () => {
    const live = {
      ...emptyDraft(),
      status: "processing" as const,
      input: { topic: "My draft" },
      fileIds: ["owned-file"],
      context: {
        context_id: "owned-context",
        kind: "document-qa" as const,
        errors: [],
      },
      stages: [{ name: "Read", status: "running" as const }],
      result: samples.research.result,
    };
    const before = structuredClone(live);
    const view = displayedDraft(
      live as ReturnType<typeof emptyDraft>,
      samples.research,
    );
    expect(view).not.toBe(live);
    expect(view.sample).toBe(true);
    expect(view.fileIds).toEqual([]);
    expect(view.context).toBeUndefined();
    expect(view.stages).toEqual([]);
    expect(live).toEqual(before);
    expect(displayedDraft(live as ReturnType<typeof emptyDraft>)).toBe(live);
  });
});
