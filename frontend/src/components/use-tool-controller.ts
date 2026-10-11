"use client";
import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useWorkspace, emptyDraft } from "./provider";
import { voices, type Tool, type ToolId } from "../lib/tools";
import { buildInput } from "../lib/inputs";
import { stream, upload, clearSession, usage } from "../lib/api";
import type { Event, Result, ContextResult } from "../lib/types";
export function useToolController(
  tool: Tool,
  setSettings: (open: boolean) => void,
  onResetEvidence: () => void,
) {
  const router = useRouter();
  const { mode, key, setKey, drafts, update, reset } = useWorkspace();
  const draft = drafts[tool.id] || emptyDraft();
  const busy = draft.status === "processing";
  const qa = tool.id === "document-qa" || tool.id === "url-qa";
  const transcriptTool =
    tool.id === "youtube-summary" || tool.id === "captions";
  const pasted = transcriptTool && draft.input.source_type === "transcript";
  const selectedVoice =
    mode === "openai"
      ? voices.includes(draft.input.voice as (typeof voices)[number])
        ? draft.input.voice
        : "alloy"
      : /^(af_|am_)/.test(draft.input.voice || "") ||
          draft.input.voice === "bf_emma"
        ? draft.input.voice
        : "af_heart";
  const [remaining, setRemaining] = useState<Record<string, number> | null>(
    null,
  );
  const [clearNote, setClearNote] = useState("");
  const fileInput = useRef<HTMLInputElement>(null);
  function change(field: string, value: string) {
    update(tool.id, (d) => {
      const input = { ...d.input, [field]: value };
      const hasContent = transcriptTool
        ? Boolean(
            (input.source_type === "transcript"
              ? input.transcript_text
              : input.url
            )?.trim(),
          )
        : Boolean(
            d.files.length ||
              (tool.field && input[tool.field]?.trim()) ||
              (tool.urls && input.urls?.trim()),
          );
      return {
        input,
        error: undefined,
        inputsChanged: !!d.result,
        ...(field === "urls" ? { context: undefined } : {}),
        status:
          d.status === "processing" ? d.status : hasContent ? "ready" : "empty",
      };
    });
  }
  function receive(id: ToolId, event: Event) {
    if (event.event === "stage") {
      const stage = event.data as {
        name: string;
        status: "running" | "completed" | "failed";
      };
      update(id, (d) => {
        const stages = [...d.stages];
        if (stage.status === "running") stages.push(stage);
        else {
          const index = stages
            .map((s) => s.status === "running" && s.name === stage.name)
            .lastIndexOf(true);
          if (index !== -1) stages[index] = stage;
        }
        return { stages };
      });
    }
    if (event.event === "warning")
      update(id, (d) => ({
        warnings: [...d.warnings, (event.data as { message: string }).message],
      }));
    if (event.event === "error")
      update(id, (d) => ({
        status: "error",
        error: (event.data as { message: string }).message,
        ...((event.data as { code?: string }).code === "session_expired"
          ? { fileIds: [], context: undefined }
          : (event.data as { code?: string }).code === "context_reprocess"
            ? { context: undefined }
            : {}),
        finished: Date.now(),
        stages: d.stages.map((s) =>
          s.status === "running" ? { ...s, status: "failed" } : s,
        ),
      }));
    if (event.event === "result") {
      const result = event.data as Result | ContextResult;
      update(id, (d) =>
        "context_id" in result
          ? {
              context: result,
              status: result.errors.length ? "partial-success" : "success",
              finished: Date.now(),
            }
          : {
              result,
              status: d.warnings.length ? "partial-success" : "success",
              finished: Date.now(),
            },
      );
    }
  }
  async function execute(process = false) {
    if (busy) return;
    if (mode === "openai" && (tool.key || process) && !key) {
      setSettings(true);
      return;
    }
    const urls = (draft.input.urls || "").split("\n").filter((u) => u.trim());
    let problem = "";
    if (tool.files && !draft.files.length)
      problem = "Choose a supported file to continue.";
    else if (
      tool.urls &&
      (!qa || process) &&
      (!urls.length || urls.length > tool.urls)
    )
      problem = `Enter between 1 and ${tool.urls} source URLs, one per line.`;
    else if (!process && pasted && !draft.input.transcript_text?.trim())
      problem = "Paste a transcript to continue.";
    else if (
      !process &&
      tool.field &&
      !pasted &&
      !draft.input[tool.field]?.trim()
    )
      problem = `Enter ${tool.label?.toLowerCase()} to continue.`;
    else if (!process && qa && !draft.context)
      problem = "Process your files or URLs before asking a question.";
    else if (tool.id === "content" && !draft.input.platforms)
      problem = "Choose at least one target platform.";
    if (problem) {
      update(tool.id, { error: problem, status: "error" });
      return;
    }
    const id = tool.id;
    const input: Record<string, string> = {
      ...draft.input,
      voice: selectedVoice,
    };
    onResetEvidence();
    update(id, {
      status: "processing",
      sample: false,
      inputsChanged: false,
      error: undefined,
      warnings: [],
      stages: [],
      started: Date.now(),
      finished: undefined,
      result: undefined,
      ...(process ? { context: undefined } : {}),
    });
    try {
      let ids = draft.fileIds;
      if (tool.files && !ids.length) {
        update(id, (d) => ({
          stages: [
            ...d.stages,
            { name: "Upload selected files", status: "running" },
          ],
        }));
        ids = [];
        for (const file of draft.files) ids.push(await upload(file));
        update(id, (d) => ({
          fileIds: ids,
          stages: d.stages.map((s) =>
            s.name === "Upload selected files"
              ? { ...s, status: "completed" }
              : s,
          ),
        }));
      }
      const callback = (event: Event) => receive(id, event);
      if (process)
        await stream(
          `/contexts/${tool.id === "document-qa" ? "documents" : "urls"}`,
          tool.id === "document-qa" ? { file_ids: ids } : { urls },
          key,
          callback,
          mode,
        );
      else if (qa)
        await stream(
          `/contexts/${draft.context!.context_id}/query`,
          { question: input.question.trim() },
          key,
          callback,
          mode,
        );
      else
        await stream("/runs", buildInput(id, input, ids), key, callback, mode);
      const allowance = await usage().catch(() => null);
      if (allowance) setRemaining(allowance.remaining);
    } catch (error) {
      update(id, {
        status: "error",
        ...(error instanceof Error &&
        (error as Error & { reprocess?: boolean }).reprocess
          ? { fileIds: [], context: undefined }
          : {}),
        error:
          error instanceof Error
            ? error.message
            : "Workflow failed. Retry explicitly.",
        finished: Date.now(),
      });
    }
  }
  function selectFiles(files: FileList | null) {
    if (!files) return;
    const chosen = Array.from(files);
    const error =
      chosen.length > (tool.maxFiles || 1)
        ? `Choose at most ${tool.maxFiles} files.`
        : chosen.some((f) => f.size > 200 * 1024 * 1024)
          ? "Each file must be at most 200 MB."
          : chosen.some(
                (f) =>
                  !tool.files
                    ?.split(",")
                    .some((ext) => f.name.toLowerCase().endsWith(ext)),
              )
            ? "Choose a supported file type."
            : "";
    if (error) {
      update(tool.id, { error, status: "error" });
      return;
    }
    update(tool.id, {
      files: chosen,
      fileIds: [],
      context: undefined,
      status: "ready",
      inputsChanged: !!draft.result,
      error: undefined,
    });
    if (fileInput.current) fileInput.current.value = "";
  }
  async function clear() {
    setClearNote("Clearing…");
    try {
      await clearSession();
      reset();
      setKey("");
      setRemaining(null);
      onResetEvidence();
      setClearNote("Temporary data, drafts and key cleared.");
    } catch (error) {
      setClearNote(
        error instanceof Error ? error.message : "Could not clear session.",
      );
    }
  }
  function summarize(text: string) {
    if (mode === "openai" && !key) {
      setSettings(true);
      return;
    }
    update("text-summary", {
      ...emptyDraft(),
      input: { ...emptyDraft().input, text },
      status: "ready",
    });
    router.push("/workspace/text-summary");
  }

  return {
    draft,
    busy,
    qa,
    transcriptTool,
    pasted,
    selectedVoice,
    remaining,
    clearNote,
    fileInput,
    change,
    execute,
    selectFiles,
    clear,
    summarize,
  };
}
