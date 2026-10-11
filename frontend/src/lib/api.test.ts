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

it("never sends an advanced key in an explicitly free/local request", async () => {
  const { vi } = await import("vitest");
  vi.resetModules();
  const requests: RequestInit[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn(async (_url: string, init: RequestInit) => {
      requests.push(init);
      if (requests.length === 1)
        return new Response(JSON.stringify({ token: "test-session" }), {
          status: 200,
        });
      return new Response(
        body([
          'event: result\ndata: {"tool":"text-summary","text":"Result"}\n\n',
        ]),
        { status: 200 },
      );
    }),
  );
  try {
    const api = await import("./api");
    await api.stream(
      "/runs",
      { tool: "text-summary", text: "Source" },
      "advanced-key",
      () => {},
      "free",
    );
    await api.stream(
      "/runs",
      { tool: "text-summary", text: "Source" },
      "advanced-key",
      () => {},
      "local",
    );
    await api.stream(
      "/runs",
      { tool: "text-summary", text: "Source" },
      "advanced-key",
      () => {},
      "openai",
    );
    expect(new Headers(requests[1].headers).get("X-OpenAI-Key")).toBeNull();
    expect(new Headers(requests[2].headers).get("X-OpenAI-Key")).toBeNull();
    expect(new Headers(requests[3].headers).get("X-OpenAI-Key")).toBe(
      "advanced-key",
    );
    expect(new Headers(requests[1].headers).get("X-Trace-Mode")).toBe("free");
  } finally {
    vi.unstubAllGlobals();
  }
});
