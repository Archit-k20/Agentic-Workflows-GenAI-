import { describe, it, expect } from "vitest";
import { consume } from "./api";
import { samples, sampleLabel } from "./samples";
import { tools } from "./tools";
function body(chunks: string[]) {
  return new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks)
        controller.enqueue(new TextEncoder().encode(chunk));
      controller.close();
    },
  });
}
describe("workflow transport", () => {
  it("retains stage events across arbitrary network chunks", async () => {
    const events: unknown[] = [];
    await consume(
      body([
        "event: sta",
        'ge\ndata: {"name":"Read source","status":"completed"}\n\n',
        ': keepalive\n\nevent: result\ndata: {"tool":"text-summary","text":"Result"}\n\n',
      ]),
      (event) => events.push(event),
    );
    expect(events).toHaveLength(2);
  });
  it("rejects an interrupted response without replaying", async () => {
    const events: unknown[] = [];
    await expect(
      consume(
        body(['event: stage\ndata: {"name":"Read","status":"completed"}\n\n']),
        (event) => events.push(event),
      ),
    ).rejects.toThrow("not replayed");
    expect(events).toHaveLength(1);
  });
  it("accepts explicit workflow failure as a terminal event", async () => {
    const events: unknown[] = [];
    await consume(
      body(['event: error\ndata: {"message":"Invalid credentials"}\n\n']),
      (event) => events.push(event),
    );
    expect(events).toHaveLength(1);
  });
});
describe("offline samples", () => {
  it("contains five clearly identified local results", () => {
    expect(Object.keys(samples)).toHaveLength(5);
    expect(sampleLabel).toBe("Sample result — no live AI request");
    for (const [tool, sample] of Object.entries(samples)) {
      expect(sample?.result.tool).toBe(tool);
      expect(tools.some((t) => t.id === tool)).toBe(true);
    }
  });
});
