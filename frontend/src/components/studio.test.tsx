// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { Provider, useWorkspace } from "./provider";
import { useSample } from "./use-sample";
import { Results } from "./results";
import { ArtifactTabs } from "./artifact-tabs";
import { useToolController } from "./use-tool-controller";
import { samples } from "../lib/samples";
import { tools, type ToolId } from "../lib/tools";
import type { Event } from "../lib/types";
import { sampleDraft } from "../lib/sample-state";
const { stream, upload, usage, clearSession, push } = vi.hoisted(() => ({
  stream: vi.fn(),
  upload: vi.fn(),
  usage: vi.fn(),
  clearSession: vi.fn(),
  push: vi.fn(),
}));
vi.mock("../lib/api", () => ({
  stream,
  upload,
  usage,
  clearSession,
  media: vi.fn(() => {
    throw Error("Media request forbidden in a sample");
  }),
}));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
beforeEach(() => {
  vi.clearAllMocks();
  vi.stubGlobal(
    "ResizeObserver",
    class {
      observe() {}
      unobserve() {}
      disconnect() {}
    },
  );
  usage.mockResolvedValue(null);
  vi.stubGlobal("matchMedia", () => ({
    matches: false,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  }));
  vi.stubGlobal(
    "fetch",
    vi.fn(() => {
      throw Error("Unexpected network request");
    }),
  );
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
function SampleSurface({ id }: { id: ToolId }) {
  const { sample } = useSample(id, true);
  return sample ? (
    <Results result={sample.result} mode="sample" onPin={() => {}} />
  ) : null;
}
describe("offline sample surfaces", () => {
  for (const id of Object.keys(samples) as (keyof typeof samples)[])
    it(`${id} renders without any network or media request`, async () => {
      const { container } = render(
        <Provider>
          <SampleSurface id={id} />
        </Provider>,
      );
      await waitFor(() =>
        expect(
          container.querySelector(`[data-artifact="${id}"]`),
        ).not.toBeNull(),
      );
      expect(fetch).not.toHaveBeenCalled();
      expect(stream).not.toHaveBeenCalled();
      expect(upload).not.toHaveBeenCalled();
    });
  it("switches content artifacts while preserving review and narration errors", () => {
    render(
      <Provider>
        <Results
          result={{
            ...samples.content.result,
            audio_error: "Narration provider unavailable",
          }}
          mode="sample"
          onPin={() => {}}
        />
      </Provider>,
    );
    fireEvent.click(screen.getByRole("tab", { name: "Captions" }));
    expect(
      screen.getByText(samples.content.result.final_captions.x),
    ).toBeTruthy();
    fireEvent.click(screen.getByRole("tab", { name: "Narration" }));
    expect(
      screen.getByText(/Narration provider unavailable/, { selector: "p" }),
    ).toBeTruthy();
    expect(fetch).not.toHaveBeenCalled();
  });
  it("switches document sections and shows missing owners", () => {
    render(
      <Provider>
        <Results
          result={samples.documents.result}
          mode="sample"
          onPin={() => {}}
        />
      </Provider>,
    );
    fireEvent.click(screen.getByRole("tab", { name: "Action items" }));
    expect(screen.getByRole("cell", { name: "Unknown" })).toBeTruthy();
    fireEvent.click(screen.getByRole("tab", { name: "Risks" }));
    expect(
      screen.getByText(/Safety review has no assigned owner/, {
        selector: "li",
      }),
    ).toBeTruthy();
  });
  it("uses keyboard navigation for tabs", () => {
    const change = vi.fn();
    render(
      <ArtifactTabs
        label="Example tabs"
        value="one"
        onChange={change}
        items={[
          { id: "one", label: "One" },
          { id: "two", label: "Two" },
        ]}
      />,
    );
    fireEvent.keyDown(screen.getByRole("tab", { name: "One" }), {
      key: "ArrowRight",
    });
    expect(change).toHaveBeenCalledWith("two");
    expect(document.activeElement?.textContent).toBe("Two");
  });
});
let active: ReturnType<typeof useToolController>;
let state: ReturnType<typeof useWorkspace>;
function Harness({ id, example = false }: { id: ToolId; example?: boolean }) {
  state = useWorkspace();
  active = useToolController(
    tools.find((t) => t.id === id)!,
    () => {},
    () => {},
  );
  const draft = example ? sampleDraft(samples.research) : active.draft;
  return (
    <div data-testid="view">
      {draft.input.topic || draft.input.text}|{draft.status}
    </div>
  );
}
describe("live controller stays isolated from samples", () => {
  it("preserves selected files and context while viewing examples and changing tools", () => {
    const file = new File(["content"], "brief.pdf", {
      type: "application/pdf",
    });
    const { rerender } = render(
      <Provider>
        <Harness id="research" />
      </Provider>,
    );
    act(() =>
      state.update("research", {
        input: { topic: "Keep my question" },
        files: [file],
        fileIds: ["file-a"],
        context: { context_id: "context-a", kind: "document-qa", errors: [] },
        status: "ready",
      }),
    );
    rerender(
      <Provider>
        <Harness id="research" example />
      </Provider>,
    );
    expect(state.drafts.research?.input.topic).toBe("Keep my question");
    rerender(
      <Provider>
        <Harness id="code" />
      </Provider>,
    );
    rerender(
      <Provider>
        <Harness id="research" />
      </Provider>,
    );
    expect(active.draft.files[0]).toBe(file);
    expect(active.draft.fileIds).toEqual(["file-a"]);
    expect(active.draft.context?.context_id).toBe("context-a");
    expect(active.draft.input.topic).toBe("Keep my question");
  });
  it("finishes a pending run in its original draft after navigating to a sample and another tool", async () => {
    let receive: (event: Event) => void = () => {};
    let finish: () => void = () => {};
    stream.mockImplementation((_path, _body, _key, callback) => {
      receive = callback;
      return new Promise<void>((resolve) => {
        finish = resolve;
      });
    });
    const { rerender } = render(
      <Provider>
        <Harness id="text-summary" />
      </Provider>,
    );
    act(() => active.change("text", "Keep this live input"));
    let run: Promise<void>;
    act(() => {
      run = active.execute();
    });
    expect(active.draft.status).toBe("processing");
    rerender(
      <Provider>
        <Harness id="research" example />
      </Provider>,
    );
    act(() =>
      receive({
        event: "stage",
        data: { name: "Summarize", status: "running" },
      }),
    );
    rerender(
      <Provider>
        <Harness id="code" />
      </Provider>,
    );
    await act(async () => {
      receive({
        event: "result",
        data: { tool: "text-summary", text: "Completed result" },
      });
      finish();
      await run!;
    });
    rerender(
      <Provider>
        <Harness id="text-summary" />
      </Provider>,
    );
    expect(active.draft.result).toMatchObject({ text: "Completed result" });
    expect(active.draft.input.text).toBe("Keep this live input");
    expect(stream).toHaveBeenCalledTimes(1);
  });
  it("keeps failed inputs and does not retry an interrupted request", async () => {
    stream.mockRejectedValue(
      new Error("Connection interrupted. The request was not replayed."),
    );
    render(
      <Provider>
        <Harness id="text-summary" />
      </Provider>,
    );
    act(() => active.change("text", "Preserve this"));
    await act(() => active.execute());
    expect(active.draft.status).toBe("error");
    expect(active.draft.input.text).toBe("Preserve this");
    expect(stream).toHaveBeenCalledTimes(1);
  });
  it("retains successful output with partial source failures", async () => {
    stream.mockImplementation(async (_p, _b, _k, callback) => {
      callback({ event: "warning", data: { message: "One source failed" } });
      callback({ event: "result", data: samples.research.result });
    });
    render(
      <Provider>
        <Harness id="research" />
      </Provider>,
    );
    act(() => {
      active.change("topic", "A question");
      active.change("urls", "https://example.com");
    });
    await act(() => active.execute());
    expect(active.draft.status).toBe("partial-success");
    expect(active.draft.result?.tool).toBe("research");
    expect(active.draft.warnings).toEqual(["One source failed"]);
  });
});

describe("presentation edge cases", () => {
  it("keeps a citation node mounted across inspector updates", () => {
    const { rerender } = render(
      <Provider>
        <Results
          result={samples.research.result}
          onPin={() => {}}
          mode="sample"
        />
      </Provider>,
    );
    const citation = screen.getAllByRole("button", {
      name: /Inspect source S1/,
    })[0];
    citation.focus();
    rerender(
      <Provider>
        <Results
          result={samples.research.result}
          onPin={() => {}}
          mode="sample"
        />
      </Provider>,
    );
    expect(citation.isConnected).toBe(true);
    expect(document.activeElement).toBe(citation);
  });
  it("retains document failures alongside a usable document", () => {
    render(
      <Provider>
        <Results
          result={{
            ...samples.documents.result,
            errors: [{ name: "unreadable.pdf", error: "no readable text" }],
          }}
          onPin={() => {}}
        />
      </Provider>,
    );
    expect(
      screen.getByText(/unreadable.pdf.*no readable text/, { selector: "p" }),
    ).toBeTruthy();
    expect(screen.getByRole("combobox", { name: "Document" })).toBeTruthy();
  });
  it("distinguishes a failed initial check, repair and an unavailable compiler", () => {
    render(
      <Provider>
        <Results
          result={{
            ...samples.code.result,
            repair_attempted: true,
            initial_code: "def broken(",
            initial_verification: {
              language: "python",
              passed: false,
              checks: [
                {
                  name: "Initial parse",
                  passed: false,
                  details: "Unclosed parenthesis",
                },
              ],
            },
            final_verification: {
              language: "python",
              passed: false,
              checks: [
                {
                  name: "Optional compiler",
                  passed: false,
                  details: "Compiler unavailable: not installed",
                },
              ],
            },
          }}
          onPin={() => {}}
        />
      </Provider>,
    );
    expect(screen.getByText("Initial code")).toBeTruthy();
    expect(screen.getByText("Final code")).toBeTruthy();
    expect(
      screen.getByText("Compiler unavailable: not installed", {
        selector: "pre",
      }),
    ).toBeTruthy();
  });
  it("invalidates a Q&A context when mode changes but retains input and files", () => {
    render(
      <Provider>
        <Harness id="document-qa" />
      </Provider>,
    );
    const file = new File(["brief"], "brief.txt");
    act(() =>
      state.update("document-qa", {
        input: { question: "What is due?" },
        files: [file],
        context: { context_id: "old", kind: "document-qa", errors: [] },
      }),
    );
    act(() => state.setMode("local"));
    expect(active.draft.context).toBeUndefined();
    expect(active.draft.files[0]).toBe(file);
    expect(active.draft.input.question).toBe("What is due?");
  });
});
