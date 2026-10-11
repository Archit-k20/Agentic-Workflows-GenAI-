"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect, useRef, Suspense } from "react";
import {
  Search,
  Settings2,
  Sun,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Menu,
  ArrowRight,
  ArrowUpRight,
  AlertTriangle,
  ChevronRight,
  BookOpen,
} from "lucide-react";
import { motion, useReducedMotion } from "motion/react";
import { tools, github, type Tool } from "../lib/tools";
import {
  hasSample,
  sampleLabel,
  displayedDraft,
  type Sample,
} from "../lib/sample-state";
import { presentation } from "../lib/presentation";
import { useWorkspace, emptyDraft } from "./provider";
import { useToolController } from "./use-tool-controller";
import { useSample } from "./use-sample";
import { WorkspaceSettings } from "./workspace-settings";
import { WorkspaceNavigation } from "./workspace-navigation";
import { ToolInputs } from "./tool-inputs";
import { ToolIcon } from "./tool-visuals";
import { Sheet, ExternalLink as OutLink } from "./ui";
import { Status } from "./status";
import { EvidenceInspector, EvidenceContent } from "./evidence";
import { VisitorVerification } from "./visitor-verification";
import type { Source } from "../lib/types";
const Results = dynamic(() => import("./results").then((m) => m.Results), {
  loading: () => <p className="loading-note">Opening result…</p>,
});
function SampleInputs({ sample, tool }: { sample?: Sample; tool: Tool }) {
  return (
    <section className="input-panel sample-inputs">
      <div className="panel-label">
        Example inputs
        <ToolIcon name={tool.icon} />
      </div>
      {sample ? (
        <>
          <p className="helper">
            Read-only example. Your live inputs stay in their own draft.
          </p>
          {Object.entries(sample.input)
            .filter(([, v]) => v)
            .map(([key, value]) => (
              <div className="sample-input" key={key}>
                <span>{key.replaceAll("_", " ")}</span>
                <p>{value}</p>
              </div>
            ))}
          {tool.files && (
            <p className="sample-input">
              A fictional document fixture supplies this example. No file has
              been uploaded.
            </p>
          )}
          <Link className="button secondary" href={`/workspace/${tool.id}`}>
            Open my input
            <ArrowRight size={16} />
          </Link>
        </>
      ) : (
        <p className="loading-note">Loading example…</p>
      )}
    </section>
  );
}
export function Workspace({ tool }: { tool: Tool }) {
  return (
    <Suspense fallback={<p className="loading-note">Opening workspace…</p>}>
      <WorkspaceView tool={tool} />
    </Suspense>
  );
}
function WorkspaceView({ tool }: { tool: Tool }) {
  const router = useRouter(),
    params = useSearchParams();
  const { theme, toggleTheme, drafts } = useWorkspace();
  const isSample = params.get("sample") === "1" && hasSample(tool.id);
  const { sample, error: sampleError } = useSample(tool.id, isSample);
  const reduced = useReducedMotion();
  const [collapsed, setCollapsed] = useState(false),
    [navigation, setNavigation] = useState(false),
    [command, setCommand] = useState(false),
    [settings, setSettings] = useState(false),
    [search, setSearch] = useState(""),
    [pinned, setPinned] = useState<Source | null>(null),
    [mobile, setMobile] = useState(false),
    [wide, setWide] = useState(false),
    [focused, setFocused] = useState(false);
  const evidenceTrigger = useRef<HTMLElement | null>(null);
  const controller = useToolController(tool, setSettings, () =>
    setPinned(null),
  );
  const { qa, clear, clearNote, summarize } = controller;
  const draft = isSample
    ? displayedDraft({ ...emptyDraft(), sample: true }, sample)
    : controller.draft;
  const busy = draft.status === "processing";
  useEffect(() => {
    const small = window.matchMedia("(max-width:767px)"),
      large = window.matchMedia("(min-width:1440px)");
    const update = () => {
      setMobile(small.matches);
      setWide(large.matches);
    };
    update();
    small.addEventListener("change", update);
    large.addEventListener("change", update);
    return () => {
      small.removeEventListener("change", update);
      large.removeEventListener("change", update);
    };
  }, []);
  useEffect(() => {
    setPinned(null);
    setNavigation(false);
    setFocused(false);
  }, [tool.id, isSample]);
  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCommand((v) => !v);
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);
  function pinEvidence(source: Source) {
    evidenceTrigger.current = document.activeElement as HTMLElement;
    setPinned(source);
  }
  function closeEvidence() {
    setPinned(null);
    requestAnimationFrame(() => evidenceTrigger.current?.focus());
  }
  function loadSample() {
    router.push(`/workspace/${tool.id}?sample=1`);
  }
  const nav = (
    <WorkspaceNavigation
      tool={tool}
      collapsed={collapsed}
      mobile={mobile || navigation}
      setSettings={setSettings}
      onNavigate={() => setNavigation(false)}
    />
  );
  return (
    <div
      className={`workspace ${collapsed ? "collapsed" : ""} ${focused ? "result-focused" : ""}`}
      data-tool={tool.id}
      data-family={presentation[tool.id].family}
    >
      {(!isSample ||
        Object.values(drafts).some((d) => d?.status === "processing")) && (
        <VisitorVerification />
      )}
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
              <div className="eyebrow">{tool.group}</div>
              <h1>{tool.name}</h1>
              <p>{tool.description}</p>
            </div>
            <Status draft={draft} />
          </div>
          <div className="workspace-toolbar">
            <div
              className="workflow-outline"
              aria-label="Workflow outline, not completed stages"
            >
              <span className="muted">Workflow</span> {tool.steps.join(" → ")}
            </div>
            <button
              className="text-link"
              onClick={() => setFocused(!focused)}
              aria-pressed={focused}
            >
              {focused ? (
                <PanelLeftOpen size={16} />
              ) : (
                <PanelLeftClose size={16} />
              )}
              {focused ? "Show input" : "Focus on result"}
            </button>
          </div>
          <details className="builder-note">
            <summary>Behind this tool</summary>
            <div>
              <p>{presentation[tool.id].purpose}</p>
              <p>
                <strong>A design choice.</strong>{" "}
                {presentation[tool.id].decision}
              </p>
              <p>
                <strong>Keep in mind.</strong>{" "}
                {presentation[tool.id].limitation}
              </p>
            </div>
          </details>
          {isSample && (
            <div className="sample-banner">
              <BookOpen size={18} />
              <div>
                <strong>{sampleLabel}</strong>
                <span>
                  Fictional inputs and outputs. No stages or checks were
                  executed.
                </span>
              </div>
              <Link href={`/workspace/${tool.id}`} className="text-link">
                {drafts[tool.id] ? "Return to my draft" : "Use this tool"}
                <ArrowUpRight size={15} />
              </Link>
            </div>
          )}
          {sampleError && <p role="alert">{sampleError}</p>}
          <div
            className={`working-panels ${pinned && wide ? "with-inspector" : ""}`}
          >
            <div className="input-column" hidden={focused}>
              {isSample ? (
                <SampleInputs sample={sample} tool={tool} />
              ) : (
                <ToolInputs
                  tool={tool}
                  controller={controller}
                  setSettings={setSettings}
                  loadSample={loadSample}
                />
              )}
            </div>
            <section className="output-panel" aria-label="Workflow output">
              <div className="panel-label">
                <span className="mono">Result</span>
                <span className="mono">
                  {draft.sample
                    ? "SAMPLE"
                    : busy
                      ? "In progress"
                      : draft.status === "error"
                        ? "Needs attention"
                        : draft.status === "partial-success"
                          ? "Ready with notes"
                          : draft.result
                            ? "Ready"
                            : "Awaiting input"}
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
                  onPin={pinEvidence}
                  onSummarize={summarize}
                  mode={isSample ? "sample" : "live"}
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
                    Waiting for the next workflow event
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
                  <span className="eyebrow">Ready when you are</span>
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
                        : "Add your inputs and run the workflow. Your result and its details will stay here."}
                  </p>
                  {hasSample(tool.id) && (
                    <button className="button secondary" onClick={loadSample}>
                      See a sample <ArrowUpRight size={15} />
                    </button>
                  )}
                </div>
              )}
            </section>
            {pinned && wide && (
              <EvidenceInspector source={pinned} onClose={closeEvidence} />
            )}
          </div>
          <div className="workspace-bottom">
            <span className="mono">TRACE / An AI project</span>
            <span>
              Built by Archit Kumar <OutLink href={github}>View source</OutLink>
            </span>
          </div>
        </main>
      </div>
      <WorkspaceSettings
        settings={settings}
        setSettings={setSettings}
        clear={clear}
        clearNote={clearNote}
      />
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
      {!wide && (
        <Sheet
          open={!!pinned}
          onOpenChange={(open) => {
            if (!open) closeEvidence();
          }}
          title="Evidence inspector"
          description="Pinned source details."
          className={mobile ? "bottom-sheet" : "evidence-sheet"}
          onCloseAutoFocus={(e) => {
            e.preventDefault();
            evidenceTrigger.current?.focus();
          }}
        >
          {pinned && <EvidenceContent source={pinned} />}
        </Sheet>
      )}
    </div>
  );
}
