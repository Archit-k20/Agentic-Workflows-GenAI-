"use client";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect, useRef, Suspense } from "react";
import {
  Orbit,
  ScanText,
  Files,
  Link as LinkIcon,
  LifeBuoy,
  AlignLeft,
  Video as Youtube,
  Newspaper,
  ScanLine,
  Image as ImageIcon,
  AudioLines,
  Captions,
  SquareCode,
  Layers,
  Search,
  Settings2,
  Sun,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Menu,
  ArrowRight,
  ArrowUpRight,
  Plus,
  X,
  FileText,
  Upload,
  AlertTriangle,
  Command,
  ExternalLink,
  ChevronRight,
  BookOpen,
} from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import {
  tools,
  groups,
  voices,
  platforms,
  tones,
  github,
  type Tool,
  type ToolId,
} from "../lib/tools";
import { buildInput } from "../lib/inputs";
import { samples, sampleLabel } from "../lib/samples";
import { useWorkspace, emptyDraft, type Draft } from "./provider";
import { Sheet, Wordmark, ExternalLink as OutLink } from "./ui";
import { Status } from "./status";
import { Results } from "./results";
import { EvidenceInspector, EvidenceContent } from "./evidence";
import { VoicePicker } from "./voice-picker";
import { VisitorVerification } from "./visitor-verification";
import { stream, upload, clearSession, usage } from "../lib/api";
import type {
  Result,
  Source,
  RunInput,
  ContextResult,
  Event,
} from "../lib/types";
const toolIcons = {
  Orbit,
  ScanText,
  Files,
  Link: LinkIcon,
  LifeBuoy,
  AlignLeft,
  Youtube,
  Newspaper,
  FileText,
  ScanLine,
  Image: ImageIcon,
  AudioLines,
  Captions,
  SquareCode,
  Layers,
};
function ToolIcon({ name, size = 17 }: { name: string; size?: number }) {
  const Icon = toolIcons[name as keyof typeof toolIcons] || FileText;
  return <Icon size={size} strokeWidth={1.65} />;
}
function AttachmentPreview({ files }: { files: File[] }) {
  const reduced = useReducedMotion();
  const [image, setImage] = useState("");
  useEffect(() => {
    const file = files[0];
    if (!file || !file.type.startsWith("image/")) {
      setImage("");
      return;
    }
    const url = URL.createObjectURL(file);
    setImage(url);
    return () => URL.revokeObjectURL(url);
  }, [files]);
  return image ? (
    <motion.div
      layout={!reduced}
      transition={{ duration: 0.26 }}
      className="attachment-preview"
    >
      <img src={image} alt={`Input preview: ${files[0].name}`} />
    </motion.div>
  ) : null;
}
function SampleLoader({ id }: { id: ToolId }) {
  const params = useSearchParams();
  const { update } = useWorkspace();
  const loaded = useRef("");
  useEffect(() => {
    const signature = `${id}:${params.get("sample")}`;
    if (params.get("sample") === "1" && loaded.current !== signature) {
      const sample = samples[id];
      if (sample)
        update(id, {
          ...emptyDraft(),
          input: { ...emptyDraft().input, ...sample.input },
          result: sample.result,
          status: "success",
          sample: true,
        });
    }
    loaded.current = signature;
  }, [id, params, update]);
  return null;
}
export function Workspace({ tool }: { tool: Tool }) {
  const router = useRouter();
  const state = useWorkspace();
  const {
    mode,
    setMode,
    key,
    setKey,
    theme,
    toggleTheme,
    drafts,
    update,
    reset,
  } = state;
  const draft = drafts[tool.id] || emptyDraft();
  const reduced = useReducedMotion();
  const [collapsed, setCollapsed] = useState(false),
    [navigation, setNavigation] = useState(false),
    [command, setCommand] = useState(false),
    [settings, setSettings] = useState(false),
    [search, setSearch] = useState(""),
    [pinned, setPinned] = useState<Source | null>(null),
    [mobile, setMobile] = useState(false),
    [clearNote, setClearNote] = useState("");
  const [remaining, setRemaining] = useState<Record<string, number> | null>(
    null,
  );
  const transcriptTool =
    tool.id === "youtube-summary" || tool.id === "captions";
  const pasted = transcriptTool && draft.input.source_type === "transcript";
  const selectedVoice =
    mode === "openai"
      ? voices.includes(draft.input.voice as (typeof voices)[number])
        ? draft.input.voice
        : "alloy"
      : draft.input.voice?.startsWith("af_") ||
          draft.input.voice?.startsWith("am_") ||
          draft.input.voice === "bf_emma"
        ? draft.input.voice
        : "af_heart";
  const fileInput = useRef<HTMLInputElement>(null);
  const busy = draft.status === "processing";
  const qa = tool.id === "document-qa" || tool.id === "url-qa";
  useEffect(() => {
    const media = window.matchMedia("(max-width: 767px)");
    const change = () => setMobile(media.matches);
    change();
    media.addEventListener("change", change);
    return () => media.removeEventListener("change", change);
  }, []);
  useEffect(() => {
    setPinned(null);
    setNavigation(false);
  }, [tool.id]);
  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setCommand((v) => !v);
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);
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
  function loadSample() {
    const sample = samples[tool.id];
    if (sample) {
      update(tool.id, {
        ...emptyDraft(),
        input: { ...emptyDraft().input, ...sample.input },
        result: sample.result,
        status: "success",
        sample: true,
      });
      setPinned(null);
    }
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
    setPinned(null);
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
      setPinned(null);
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
  const nav = (
    <>
      <Link href="/" className="rail-brand" aria-label="TRACE home">
        <Wordmark compact={collapsed && !mobile} />
        {!collapsed && (
          <span className="brand-subtitle">AGENTIC AI WORKSPACE</span>
        )}
      </Link>
      <div className="nav-tools">
        {groups.map((group) => (
          <div className="nav-group" key={group}>
            <span className="nav-group-label mono">
              {collapsed ? group.slice(0, 1) : group}
            </span>
            {tools
              .filter((t) => t.group === group)
              .map((t) => (
                <Link
                  href={`/workspace/${t.id}`}
                  key={t.id}
                  className={`nav-tool ${t.id === tool.id ? "selected" : ""}`}
                  aria-current={t.id === tool.id ? "page" : undefined}
                  title={collapsed ? t.name : undefined}
                  onClick={() => setNavigation(false)}
                >
                  <ToolIcon name={t.icon} />
                  {!collapsed && <span>{t.name}</span>}
                  {t.id === tool.id && !collapsed && (
                    <span className="nav-active-dot" />
                  )}
                </Link>
              ))}
          </div>
        ))}
      </div>
      <div className="rail-footer">
        <button
          onClick={() => setSettings(true)}
          className="nav-tool"
          title="Settings"
        >
          <Settings2 size={17} />
          {!collapsed && <span>Settings</span>}
        </button>
        {!collapsed && (
          <>
            <a href={github} target="_blank" rel="noreferrer">
              Built by Archit Kumar <ArrowUpRight size={13} />
            </a>
            <span className="mono">TRACE / v1.0</span>
          </>
        )}
      </div>
    </>
  );
  return (
    <div className={`workspace ${collapsed ? "collapsed" : ""}`}>
      <VisitorVerification />
      <Suspense fallback={null}>
        <SampleLoader id={tool.id} />
      </Suspense>
      <aside className="navigation-rail" aria-label="Tool navigation">
        {nav}
      </aside>
      <div className="workspace-main">
        <header className="workspace-topbar">
          <button
            className="icon-button desktop-toggle"
            onClick={() => setCollapsed(!collapsed)}
            aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
          >
            {collapsed ? (
              <PanelLeftOpen size={18} />
            ) : (
              <PanelLeftClose size={18} />
            )}
          </button>
          <button
            className="icon-button mobile-toggle"
            onClick={() => {
              setCollapsed(false);
              setNavigation(true);
            }}
            aria-label="Open tool navigation"
          >
            <Menu size={20} />
          </button>
          <Link href="/" className="breadcrumb">
            Workspace
          </Link>
          <ChevronRight size={13} />
          <span className="breadcrumb current">{tool.group}</span>
          <div className="topbar-actions">
            <button
              className="command-trigger"
              aria-label="Open command menu"
              onClick={() => setCommand(true)}
            >
              <Search size={15} />
              <span>Find a tool</span>
              <kbd>⌘ K</kbd>
            </button>
            <button
              className="icon-button"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            >
              {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
            </button>
            <button
              className="icon-button"
              onClick={() => setSettings(true)}
              aria-label="Open settings"
            >
              <Settings2 size={17} />
            </button>
          </div>
        </header>
        <main id="main" className="work-area">
          <div className="workspace-heading">
            <div>
              <div className="eyebrow">
                <span className="trace-dot" />
                {tool.group.toUpperCase()} /{" "}
                {String(tools.findIndex((t) => t.id === tool.id) + 1).padStart(
                  2,
                  "0",
                )}
              </div>
              <h1>
                {tool.name}
                <span className="brand-dot">.</span>
              </h1>
              <p>{tool.description}</p>
            </div>
            <Status draft={draft} />
          </div>
          <div className="workflow-ribbon" aria-label="Workflow overview">
            {tool.steps.map((step, i) => (
              <span key={step}>
                <span className="mono">0{i + 1}</span> {step}
                {i < tool.steps.length - 1 && <ArrowRight size={13} />}
              </span>
            ))}
            <span className="workflow-model mono">
              {draft.sample
                ? "SAMPLE"
                : mode === "openai"
                  ? tool.model
                  : tool.id === "speech"
                    ? "Kokoro"
                    : tool.id === "ocr"
                      ? "Tesseract"
                      : tool.id === "captions"
                        ? "Transcript"
                        : tool.id === "image"
                          ? "FLUX"
                          : mode === "local"
                            ? "Local AI"
                            : "Hosted + local"}
            </span>
          </div>
          {draft.sample && (
            <div className="sample-banner">
              <BookOpen size={17} />
              <div>
                <strong>{sampleLabel}</strong>
                <span>
                  Fictional inputs and outputs. No stages or checks were
                  executed.
                </span>
              </div>
              <button
                onClick={() => {
                  update(tool.id, {
                    sample: false,
                    inputsChanged: false,
                    result: undefined,
                    status: "ready",
                    stages: [],
                    warnings: [],
                  });
                  router.replace(`/workspace/${tool.id}`);
                }}
              >
                Start live workflow <ArrowUpRight size={14} />
              </button>
            </div>
          )}
          <div
            className={`working-panels ${pinned && !mobile ? "with-inspector" : ""}`}
          >
            <section className="input-panel">
              <div className="panel-label">
                <span className="mono">01 / INPUT</span>
                <ToolIcon name={tool.icon} />
              </div>
              <form
                onSubmit={(event) => {
                  event.preventDefault();
                  void execute();
                }}
              >
                {tool.files && (
                  <>
                    <label className="field-label" htmlFor="files">
                      {tool.maxFiles === 1
                        ? "Select a file"
                        : `Select up to ${tool.maxFiles} files`}
                    </label>
                    <label className="file-drop" htmlFor="files">
                      <Upload size={22} />
                      <strong>
                        Choose {tool.id === "ocr" ? "an image" : "your files"}
                      </strong>
                      <span>
                        {tool.files
                          .split(",")
                          .map((v) => v.slice(1).toUpperCase())
                          .join(" / ")}{" "}
                        · up to 200 MB each
                        {mode !== "openai" &&
                          " · PDFs: 50 pages · extracted text: 12,000 tokens per file"}
                      </span>
                    </label>
                    <input
                      ref={fileInput}
                      className="visually-hidden"
                      id="files"
                      type="file"
                      accept={tool.files}
                      multiple={(tool.maxFiles || 1) > 1}
                      disabled={busy}
                      onChange={(e) => selectFiles(e.target.files)}
                    />
                    <div className="attachment-tray">
                      {draft.files.map((file, i) => (
                        <div
                          className="attachment-chip"
                          key={`${file.name}-${i}`}
                        >
                          <FileText size={15} />
                          <div>
                            <span title={file.name}>{file.name}</span>
                            <small className="mono">
                              {(file.size / 1024 / 1024).toFixed(2)} MB
                            </small>
                          </div>
                          <button
                            type="button"
                            disabled={busy}
                            aria-label={`Remove ${file.name}`}
                            onClick={() =>
                              update(tool.id, {
                                files: draft.files.filter((_, j) => j !== i),
                                fileIds: [],
                                context: undefined,
                                inputsChanged: !!draft.result,
                                status:
                                  draft.files.length > 1 ? "ready" : "empty",
                              })
                            }
                          >
                            <X size={14} />
                          </button>
                        </div>
                      ))}
                    </div>
                    <AttachmentPreview files={draft.files} />
                  </>
                )}
                {tool.urls && (
                  <div className="field">
                    <label htmlFor="urls">
                      Source URLs <span className="mono">MAX {tool.urls}</span>
                    </label>
                    <textarea
                      id="urls"
                      value={draft.input.urls || ""}
                      onChange={(e) => change("urls", e.target.value)}
                      placeholder={
                        "https://example.com/article\nOne source URL per line"
                      }
                      disabled={busy}
                      rows={tool.urls === 3 ? 3 : 4}
                    />
                    <p className="helper">
                      Use public pages you want the workflow to read.
                    </p>
                  </div>
                )}
                {qa && (
                  <div className="context-control">
                    <button
                      type="button"
                      className="button secondary full"
                      disabled={busy}
                      onClick={() => void execute(true)}
                    >
                      {draft.context
                        ? "Reprocess context"
                        : tool.id === "document-qa"
                          ? "Process files"
                          : "Process URLs"}
                      <ArrowRight size={15} />
                    </button>
                    {draft.context && (
                      <span className="context-ready">
                        <span className="trace-dot" /> Context ready · ask a
                        question below
                      </span>
                    )}
                  </div>
                )}
                {transcriptTool && (
                  <div className="field">
                    <label htmlFor="transcript-source">Transcript source</label>
                    <select
                      id="transcript-source"
                      value={draft.input.source_type || "url"}
                      disabled={busy}
                      onChange={(e) => change("source_type", e.target.value)}
                    >
                      <option value="url">YouTube URL</option>
                      <option value="transcript">Paste transcript</option>
                    </select>
                    <p className="helper">
                      If YouTube blocks extraction or captions are unavailable,
                      paste the transcript here.
                    </p>
                  </div>
                )}
                {pasted && (
                  <div className="field">
                    <label htmlFor="transcript-text">Transcript text</label>
                    <textarea
                      id="transcript-text"
                      rows={10}
                      disabled={busy}
                      value={draft.input.transcript_text || ""}
                      onChange={(e) =>
                        change("transcript_text", e.target.value)
                      }
                    />
                  </div>
                )}
                {tool.field && !pasted && (
                  <div className="field">
                    <label htmlFor="primary-input">{tool.label}</label>
                    {tool.field === "url" ? (
                      <input
                        id="primary-input"
                        type="url"
                        value={draft.input[tool.field] || ""}
                        onChange={(e) => change(tool.field!, e.target.value)}
                        placeholder={tool.placeholder}
                        disabled={busy}
                      />
                    ) : (
                      <textarea
                        id="primary-input"
                        value={draft.input[tool.field] || ""}
                        onChange={(e) => change(tool.field!, e.target.value)}
                        placeholder={tool.placeholder}
                        disabled={busy}
                        rows={qa ? 3 : tool.id === "text-summary" ? 10 : 5}
                      />
                    )}
                  </div>
                )}
                {tool.id === "code" && (
                  <div className="field">
                    <label htmlFor="language">Language</label>
                    <select
                      id="language"
                      value={draft.input.language}
                      onChange={(e) => change("language", e.target.value)}
                      disabled={busy}
                    >
                      {["python", "javascript", "java", "c", "c++"].map(
                        (language) => (
                          <option key={language}>{language}</option>
                        ),
                      )}
                    </select>
                  </div>
                )}
                {tool.id === "content" && (
                  <>
                    <div className="field">
                      <label htmlFor="tone">Tone</label>
                      <select
                        id="tone"
                        value={draft.input.tone}
                        disabled={busy}
                        onChange={(e) => change("tone", e.target.value)}
                      >
                        {tones.map((tone) => (
                          <option key={tone}>{tone}</option>
                        ))}
                      </select>
                    </div>
                    <fieldset className="platform-field">
                      <legend>Target platforms</legend>
                      <div>
                        {platforms.map((platform) => (
                          <label key={platform}>
                            <input
                              type="checkbox"
                              checked={
                                draft.input.platforms
                                  ?.split(",")
                                  .includes(platform) || false
                              }
                              disabled={busy}
                              onChange={(e) =>
                                change(
                                  "platforms",
                                  (e.target.checked
                                    ? [
                                        ...draft.input.platforms
                                          .split(",")
                                          .filter(Boolean),
                                        platform,
                                      ]
                                    : draft.input.platforms
                                        .split(",")
                                        .filter((p) => p !== platform)
                                  ).join(","),
                                )
                              }
                            />
                            {platform}
                          </label>
                        ))}
                      </div>
                    </fieldset>
                    <label className="checkbox-label">
                      <input
                        type="checkbox"
                        checked={draft.input.include_audio === "true"}
                        disabled={busy}
                        onChange={(e) =>
                          change("include_audio", String(e.target.checked))
                        }
                      />{" "}
                      Generate narration
                    </label>
                  </>
                )}
                {tool.voice &&
                  (tool.id === "speech" ||
                    draft.input.include_audio === "true") && (
                    <div className="field">
                      <label htmlFor="voice">Voice</label>
                      {mode !== "openai" ? (
                        <VoicePicker
                          value={selectedVoice}
                          disabled={busy}
                          onChange={(voice) => change("voice", voice)}
                        />
                      ) : (
                        <select
                          id="voice"
                          value={selectedVoice}
                          disabled={busy}
                          onChange={(e) => change("voice", e.target.value)}
                        >
                          {voices.map((voice) => (
                            <option key={voice}>{voice}</option>
                          ))}
                        </select>
                      )}
                    </div>
                  )}
                <div className="submit-area">
                  <button
                    className="button primary full"
                    type="submit"
                    disabled={busy || (qa && !draft.context)}
                  >
                    {busy
                      ? "Working…"
                      : draft.status === "error"
                        ? "Retry explicitly"
                        : qa
                          ? "Ask question"
                          : tool.id === "ocr"
                            ? "Extract text"
                            : `Run ${tool.name}`}
                    <ArrowRight size={17} />
                  </button>
                  <p className="key-note">
                    {mode === "free"
                      ? "Free access · text and images use hosted AI; retrieval, OCR and speech run on our server. Text may fall back locally."
                      : mode === "local"
                        ? "Local processing · inference stays on our server. Multi-stage CPU reports can take several minutes. Image generation needs hosted mode."
                        : "Optional OpenAI mode · your key is held only in this tab’s memory."}
                    <button type="button" onClick={() => setSettings(true)}>
                      Change mode <ArrowUpRight size={12} />
                    </button>
                    {remaining && mode !== "openai" && (
                      <span>
                        Remaining today: {remaining.text} text ·{" "}
                        {remaining.image} images · {remaining.audio} audio ·{" "}
                        {remaining.context} contexts. Resets at 00:00 UTC;
                        shared networks share limits.
                      </span>
                    )}
                  </p>
                </div>
              </form>
              {samples[tool.id] && !draft.sample && (
                <button
                  className="try-sample"
                  disabled={busy}
                  onClick={loadSample}
                >
                  Explore a sample result <ArrowUpRight size={14} />
                </button>
              )}
              <div className="input-footnote mono">
                DRAFTS STAY IN THIS OPEN TAB
              </div>
            </section>
            <section className="output-panel" aria-label="Workflow output">
              <div className="panel-label">
                <span className="mono">02 / OUTPUT</span>
                <span className="mono">
                  {draft.sample
                    ? "SAMPLE"
                    : busy
                      ? "IN PROGRESS"
                      : draft.result
                        ? "ARTIFACT READY"
                        : "WAITING"}
                </span>
              </div>
              <div role="status" aria-live="polite" className="sr-status">
                {busy
                  ? "Workflow processing"
                  : draft.status === "success"
                    ? "Result ready"
                    : draft.status === "partial-success"
                      ? "Result ready with warnings"
                      : draft.status === "error"
                        ? "Workflow needs attention"
                        : ""}
              </div>
              {draft.error && (
                <div className="error-banner" role="alert">
                  <AlertTriangle size={19} />
                  <div>
                    <strong>Couldn’t complete this step</strong>
                    <p>{draft.error}</p>
                    <small>
                      Your inputs are preserved. Retrying requires an explicit
                      action.
                    </small>
                  </div>
                </div>
              )}
              {draft.inputsChanged && draft.result && (
                <p className="result-note" role="status">
                  {draft.sample
                    ? "Inputs changed. The sample below remains illustrative; run explicitly to use your inputs."
                    : "Inputs changed. The result below is from the previous run."}
                </p>
              )}
              {draft.warnings.length > 0 && (
                <details className="warning-banner" open>
                  <summary>
                    {draft.warnings.length} processing{" "}
                    {draft.warnings.length === 1 ? "note" : "notes"}
                  </summary>
                  <ul>
                    {draft.warnings.map((warning, i) => (
                      <li key={i}>{warning}</li>
                    ))}
                  </ul>
                </details>
              )}
              {(draft.result?.execution || draft.context?.execution) && (
                <details className="result-note">
                  <summary>Execution details</summary>
                  <pre className="execution-details">
                    {JSON.stringify(
                      draft.result?.execution || draft.context?.execution,
                      null,
                      2,
                    )}
                  </pre>
                </details>
              )}
              {draft.result ? (
                <Results
                  result={draft.result}
                  onPin={setPinned}
                  onSummarize={summarize}
                />
              ) : busy ? (
                <div className="processing-state">
                  <div className="processing-trace">
                    <motion.svg
                      width="144"
                      height="90"
                      viewBox="0 0 144 90"
                      aria-hidden="true"
                    >
                      <path
                        d="M0 45h40l20-24h28l20 24h36"
                        stroke="var(--line)"
                        fill="none"
                      />
                      <motion.path
                        d="M0 45h40l20-24h28l20 24h36"
                        stroke="var(--accent)"
                        fill="none"
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: 1 }}
                        transition={{ duration: reduced ? 0 : 0.26 }}
                      />
                    </motion.svg>
                  </div>
                  <h2>Following the trace.</h2>
                  <p>
                    {draft.stages.findLast((s) => s.status === "running")
                      ?.name || "Connecting to your workflow…"}
                  </p>
                  <span className="mono">
                    ACTUAL STAGES · NO SIMULATED PROGRESS
                  </span>
                </div>
              ) : draft.context ? (
                <div className="empty-output">
                  <BookOpen size={36} />
                  <h2>Context is ready.</h2>
                  <p>
                    Ask a question to retrieve relevant chunks and produce a
                    sourced answer.
                  </p>
                </div>
              ) : (
                <div className="empty-output">
                  <div className="empty-frame">
                    <ToolIcon name={tool.icon} size={32} />
                    <span className="frame-corner top-left" />
                    <span className="frame-corner bottom-right" />
                  </div>
                  <span className="eyebrow">
                    A CLEAR SURFACE FOR YOUR NEXT IDEA
                  </span>
                  <h2>
                    {tool.id === "research"
                      ? "Start with a question."
                      : tool.id === "code"
                        ? "From intent to implementation."
                        : tool.id === "documents"
                          ? "Bring the details into focus."
                          : "Your output starts here."}
                  </h2>
                  <p>
                    {tool.id === "research"
                      ? "Add a topic and the source URLs you want to investigate. The report, citations, and review will appear together."
                      : qa
                        ? "Process your selected inputs first. Then ask a question and inspect the retrieved sources."
                        : "Add your inputs on the left and run the workflow. Your result and its details will stay here."}
                  </p>
                  {samples[tool.id] && (
                    <button className="button secondary" onClick={loadSample}>
                      See a sample <ArrowUpRight size={15} />
                    </button>
                  )}
                </div>
              )}
            </section>
            {pinned && !mobile && (
              <EvidenceInspector
                source={pinned}
                onClose={() => setPinned(null)}
              />
            )}
          </div>
          <div className="workspace-bottom">
            <span className="mono">TRACE — AGENTIC AI WORKSPACE</span>
            <span>
              Built by Archit Kumar <OutLink href={github}>View source</OutLink>
            </span>
          </div>
        </main>
      </div>
      <Sheet
        open={settings}
        onOpenChange={setSettings}
        title="Workspace settings"
        description="Configure live execution and your viewing preferences."
      >
        <div className="settings-body">
          <div className="field">
            <label htmlFor="execution-mode">Execution mode</label>
            <select
              id="execution-mode"
              value={mode}
              disabled={Object.values(drafts).some(
                (d) => d?.status === "processing",
              )}
              onChange={(e) => setMode(e.target.value as typeof mode)}
            >
              <option value="free">Free access — recommended</option>
              <option value="local">Local inference on our server</option>
              <option value="openai">Advanced — my OpenAI key</option>
            </select>
            <p className="helper">
              Free hosted requests send relevant text and image prompts to
              Cloudflare. Local mode keeps AI inference on our server; fetching
              your source URLs still contacts their websites. Switching modes
              requires Q&amp;A context reprocessing. English-first.
            </p>
          </div>
          {mode === "openai" && (
            <div className="field">
              <label htmlFor="api-key">Optional OpenAI API key</label>
              <input
                id="api-key"
                type="password"
                autoComplete="off"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="sk-…"
              />
              <p className="helper">
                Kept in browser memory and sent only with your live requests. It
                is not saved across sessions.
              </p>
            </div>
          )}
          <div className="settings-theme">
            <div>
              <strong>Appearance</strong>
              <p>
                {theme === "dark" ? "Dark instrument" : "Light reading surface"}
              </p>
            </div>
            <button className="button secondary" onClick={toggleTheme}>
              {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />} Switch
              theme
            </button>
          </div>
          <div className="settings-session">
            <h3>Temporary session</h3>
            <p>
              Uploads, indexes, and generated media expire within 24 hours. You
              can clear them immediately.
            </p>
            <button
              className="button secondary"
              disabled={Object.values(drafts).some(
                (d) => d?.status === "processing",
              )}
              onClick={() => void clear()}
            >
              Clear session and drafts
            </button>
            <p role="status">{clearNote}</p>
          </div>
          <OutLink href={github}>Project source and documentation</OutLink>
        </div>
      </Sheet>
      <Sheet
        open={command}
        onOpenChange={setCommand}
        title="Go anywhere"
        description="Find a tool or open workspace settings."
        className="command-dialog"
      >
        <div className="command-search">
          <Search size={20} />
          <input
            autoFocus
            aria-label="Search tools"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search all 15 tools…"
          />
        </div>
        <div className="command-results">
          {tools
            .filter((t) =>
              `${t.name} ${t.group}`
                .toLowerCase()
                .includes(search.toLowerCase()),
            )
            .map((t) => (
              <button
                key={t.id}
                onClick={() => {
                  router.push(`/workspace/${t.id}`);
                  setCommand(false);
                  setSearch("");
                }}
              >
                <ToolIcon name={t.icon} />
                <span>
                  {t.name}
                  <small>{t.group}</small>
                </span>
                <ArrowUpRight size={15} />
              </button>
            ))}
          {!tools.some((t) =>
            `${t.name} ${t.group}`.toLowerCase().includes(search.toLowerCase()),
          ) && <p>No matching tools.</p>}
          <button
            onClick={() => {
              setCommand(false);
              setSettings(true);
            }}
          >
            <Settings2 size={17} />
            <span>Workspace settings</span>
            <ArrowUpRight size={15} />
          </button>
        </div>
        <div className="command-footer mono">
          TAB TO NAVIGATE · ENTER TO OPEN · ESC TO CLOSE
        </div>
      </Sheet>
      <Sheet
        open={navigation}
        onOpenChange={setNavigation}
        title="Workspace tools"
        description="Choose a tool to continue."
        className="mobile-navigation"
      >
        {nav}
      </Sheet>
      {mobile && (
        <Sheet
          open={!!pinned}
          onOpenChange={(open) => {
            if (!open) setPinned(null);
          }}
          title="Evidence inspector"
          description="Pinned source details."
          className="bottom-sheet"
        >
          {pinned && <EvidenceContent source={pinned} />}
        </Sheet>
      )}
    </div>
  );
}
