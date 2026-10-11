"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  Sun,
  Moon,
  Search,
  LayoutGrid,
  List,
  BookOpen,
  Plus,
} from "lucide-react";
import { Wordmark, ExternalLink } from "../components/ui";
import { useWorkspace } from "../components/provider";
import { tools, groups, github, linkedin, type Tool } from "../lib/tools";
import { presentation, filterTools, portfolio } from "../lib/presentation";
import {
  sampleIds,
  sampleLabel,
  hasSample,
  type SampleId,
  type Sample,
} from "../lib/sample-state";
import research from "../lib/samples/research";
import { useSample } from "../components/use-sample";
import { ArtifactTabs } from "../components/artifact-tabs";
import { EvidenceContent } from "../components/evidence";
import { ToolIcon } from "../components/tool-visuals";
import { Sheet } from "../components/ui";
import type { Source } from "../lib/types";
const Results = dynamic(
  () => import("../components/results").then((m) => m.Results),
  { loading: () => <p className="loading-note">Opening example…</p> },
);
const exampleNames: Record<SampleId, string> = {
  research: "Research",
  documents: "Documents",
  code: "Code",
  content: "Content",
  support: "Support",
};
function previewText(sample: Sample) {
  const r = sample.result;
  if (r.tool === "research")
    return r.final_report.split("\n")[0].replace(/^# /, "");
  if (r.tool === "code") return r.final_code;
  if (r.tool === "content") return r.final_script;
  if (r.tool === "support") return String(r.final.answer);
  if (r.tool === "documents")
    return String(
      (r.documents[0]?.analysis as Record<string, unknown>)?.summary ||
        "Document overview",
    );
  return "";
}
function CollectionEntry({ tool }: { tool: Tool }) {
  const ref = useRef<HTMLElement>(null),
    [visible, setVisible] = useState(false);
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { rootMargin: "80px" },
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, []);
  const { sample } = useSample(tool.id, visible && hasSample(tool.id));
  return (
    <article
      className={`collection-entry family-${presentation[tool.id].family}`}
      ref={ref}
    >
      <div
        className="collection-preview"
        aria-label={sample ? "Sample excerpt" : "Input and output illustration"}
      >
        {sample ? (
          <>
            <span className="preview-caption">Sample excerpt</span>
            <p className={tool.id === "code" ? "mono" : ""}>
              {previewText(sample).replace(/\[S\d+\]/g, "")}
            </p>
          </>
        ) : (
          <>
            <span className="preview-caption">Illustration</span>
            <div className="tool-diagram" aria-hidden="true">
              <span>
                <ToolIcon name={tool.icon} size={26} />
              </span>
              <svg viewBox="0 0 96 24">
                <path
                  d="M0 12h90m-6-5 7 5-7 5"
                  fill="none"
                  stroke="currentColor"
                />
              </svg>
              <span className="diagram-lines">
                <i />
                <i />
                <i />
              </span>
            </div>
          </>
        )}
      </div>
      <div className="collection-description">
        <span className="eyebrow">{tool.group}</span>
        <h3>
          <Link href={`/workspace/${tool.id}`}>{tool.name}</Link>
        </h3>
        <p>{tool.description}</p>
        <div className="collection-links">
          <Link href={`/workspace/${tool.id}`}>
            Open tool <ArrowUpRight size={15} />
          </Link>
          {hasSample(tool.id) && (
            <Link href={`/workspace/${tool.id}?sample=1`}>View example</Link>
          )}
        </div>
      </div>
    </article>
  );
}
export default function Home() {
  const { theme, toggleTheme, drafts } = useWorkspace();
  const [selected, setSelected] = useState<SampleId>("research"),
    [pinned, setPinned] = useState<Source | null>(null),
    [sheet, setSheet] = useState(false),
    [wide, setWide] = useState(false);
  const [query, setQuery] = useState(""),
    [group, setGroup] = useState("All"),
    [view, setView] = useState<"grid" | "list">("grid");
  const search = useRef<HTMLInputElement>(null),
    sourceTrigger = useRef<HTMLElement | null>(null);
  const { sample, error } = useSample(selected, true, research);
  useEffect(() => {
    const media = window.matchMedia("(min-width:1024px)");
    const update = () => setWide(media.matches);
    update();
    media.addEventListener("change", update);
    return () => media.removeEventListener("change", update);
  }, []);
  useEffect(() => {
    const listener = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        search.current?.focus();
        search.current?.scrollIntoView({
          block: "center",
          behavior: window.matchMedia("(prefers-reduced-motion: reduce)")
            .matches
            ? "instant"
            : "smooth",
        });
      }
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, []);
  const shown = filterTools(query, group);
  function pin(source: Source) {
    sourceTrigger.current = document.activeElement as HTMLElement;
    setPinned(source);
    if (!wide) setSheet(true);
  }
  function closeEvidence() {
    setSheet(false);
    requestAnimationFrame(() => sourceTrigger.current?.focus());
  }
  return (
    <div className="studio-home">
      <header className="studio-masthead">
        <Link href="/" aria-label="TRACE home">
          <Wordmark />
        </Link>
        <span className="masthead-note">An AI project by Archit Kumar</span>
        <nav aria-label="Main navigation">
          <a href="#tools">The tools</a>
          <a href="#about">About this project</a>
          <ExternalLink href={github}>GitHub</ExternalLink>
          <button
            className="icon-button"
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
            onClick={toggleTheme}
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </nav>
      </header>
      <main id="main">
        <section className="studio-intro">
          <div>
            <span className="eyebrow">
              <span className="trace-dot" /> Built to be explored
            </span>
            <h1>
              A collection of AI tools <span>I built.</span>
            </h1>
          </div>
          <p>
            Try an example. Bring your own question.
            <br className="desktop-break" /> See the sources, decisions and
            checks behind the result.
          </p>
        </section>
        <section
          className="example-stage"
          aria-label="Explore a working example"
        >
          <div className="example-topline">
            <ArtifactTabs
              label="Choose an example"
              panelId="home-example-panel"
              value={selected}
              onChange={(id) => {
                setSelected(id as SampleId);
                setPinned(null);
                setSheet(false);
              }}
              items={sampleIds.map((id) => ({ id, label: exampleNames[id] }))}
            />
            <span className="example-number">01—05 / Selected work</span>
          </div>
          <div className="example-label">
            <BookOpen size={15} />
            <span>{sampleLabel}</span>
          </div>
          <div
            id="home-example-panel"
            className="example-workbench"
            role="tabpanel"
            aria-label={`${exampleNames[selected]} example`}
          >
            <aside className="example-context">
              <span className="eyebrow">The starting point</span>
              <h2>
                {selected === "research"
                  ? "A campus repair pilot."
                  : presentation[selected].preview}
              </h2>
              <p>
                {sample
                  ? Object.values(sample.input).filter(Boolean)[0] ||
                    "A fictional planning brief, with people, tasks and a few unanswered questions."
                  : "Opening the selected example…"}
              </p>
              <div className="example-context-note">
                <span className="trace-mark" aria-hidden="true">
                  <i />
                  <i />
                  <i />
                </span>
                <span>{presentation[selected].purpose}</span>
              </div>
            </aside>
            <div className="example-result" key={selected}>
              {error ? (
                <p role="alert">{error}</p>
              ) : sample ? (
                <Results
                  result={sample.result}
                  onPin={pin}
                  mode="sample"
                  compact
                />
              ) : (
                <p className="loading-note">Loading example…</p>
              )}
            </div>
            {
              <aside className="example-evidence" aria-label="Example evidence">
                {pinned ? (
                  <>
                    <button
                      className="text-link"
                      onClick={() => {
                        setPinned(null);
                        sourceTrigger.current?.focus();
                      }}
                    >
                      Close evidence
                    </button>
                    <EvidenceContent source={pinned} />
                  </>
                ) : (
                  <>
                    <span className="eyebrow">A closer look</span>
                    <div className="evidence-glyph" aria-hidden="true">
                      <span>S1</span>
                      <span />
                      <span />
                    </div>
                    <h3>
                      {selected === "research" || selected === "support"
                        ? "Follow the source."
                        : "Look inside the result."}
                    </h3>
                    <p>
                      {selected === "research" || selected === "support"
                        ? "Select a citation to inspect its source."
                        : selected === "code"
                          ? "Each check describes exactly what it inspected. The example checks are illustrative."
                          : "Switch between the sections to see what this workflow produces."}
                    </p>
                    <p className="helper">
                      Fictional example. No AI request or checks were executed.
                    </p>
                  </>
                )}
              </aside>
            }
          </div>
          <div className="example-footer">
            <span>
              {!wide && (selected === "research" || selected === "support")
                ? "Select a citation to inspect its source."
                : "Your own inputs stay separate from examples."}
            </span>
            <div>
              <Link
                className="text-link"
                href={`/workspace/${selected}?sample=1`}
              >
                Open full example
                <ArrowUpRight size={15} />
              </Link>
              <Link className="button primary" href={`/workspace/${selected}`}>
                {drafts[selected] ? "Return to my draft" : "Use this tool"}
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        </section>
        <section id="tools" className="tool-collection">
          <div className="section-heading">
            <div>
              <span className="eyebrow">The collection / 15 tools</span>
              <h2>Different ways to work with an idea.</h2>
            </div>
            <p>
              Read, make, investigate.
              <br />
              Choose a starting point.
            </p>
          </div>
          <div className="collection-controls">
            <div className="collection-search">
              <Search size={18} />
              <input
                ref={search}
                aria-label="Search all tools"
                placeholder="Find a tool…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <kbd>⌘ K</kbd>
            </div>
            <div className="group-filters" aria-label="Filter tools">
              {["All", ...groups].map((g) => (
                <button
                  key={g}
                  aria-pressed={group === g}
                  onClick={() => setGroup(g)}
                >
                  {g}
                </button>
              ))}
            </div>
            <div className="view-switch" aria-label="Collection layout">
              <button
                className="icon-button"
                aria-label="Grid view"
                aria-pressed={view === "grid"}
                onClick={() => setView("grid")}
              >
                <LayoutGrid size={17} />
              </button>
              <button
                className="icon-button"
                aria-label="List view"
                aria-pressed={view === "list"}
                onClick={() => setView("list")}
              >
                <List size={18} />
              </button>
            </div>
          </div>
          <p className="sr-status" role="status">
            {shown.length} {shown.length === 1 ? "tool" : "tools"} found
          </p>
          <div className={`collection-${view}`}>
            {shown.map((tool) => (
              <CollectionEntry tool={tool} key={tool.id} />
            ))}
          </div>
          {!shown.length && (
            <div className="empty-collection">
              <h3>No tools match that search.</h3>
              <button
                className="button secondary"
                onClick={() => {
                  setQuery("");
                  setGroup("All");
                }}
              >
                Show all tools
              </button>
            </div>
          )}
        </section>
        <section id="about" className="studio-about">
          <div className="about-intro">
            <span className="eyebrow">Behind the project</span>
            <h2>
              The answer is one
              <br />
              part of the work.
            </h2>
            <p>
              I built TRACE to bring fifteen AI workflows into one place—and
              make the parts around an answer easier to inspect.
            </p>
            <div className="about-links">
              <ExternalLink href={github}>Source & documentation</ExternalLink>
              <ExternalLink href={portfolio}>My portfolio</ExternalLink>
              <ExternalLink href={linkedin}>LinkedIn</ExternalLink>
            </div>
          </div>
          <div className="project-decisions">
            <article>
              <span>01</span>
              <div>
                <h3>Keep the evidence close.</h3>
                <p>
                  Research and Q&A place source material beside the answer. You
                  can inspect what the workflow used, while keeping the limits
                  of that evidence in view.
                </p>
              </div>
            </article>
            <article>
              <span>02</span>
              <div>
                <h3>Make it possible to try.</h3>
                <p>
                  Examples work without a backend. Live free access uses shared
                  hosted capacity and server tools, with optional OpenAI access
                  in settings.
                </p>
              </div>
            </article>
            <article>
              <span>03</span>
              <div>
                <h3>Be clear about the limits.</h3>
                <p>
                  Models can be wrong. Syntax checks do not prove a program
                  works. Free capacity is shared, and some local workflows take
                  several minutes. This is a personal project with those
                  tradeoffs visible.
                </p>
              </div>
            </article>
          </div>
        </section>
      </main>
      <footer className="studio-footer">
        <Wordmark />
        <span>Built by Archit Kumar</span>
        <a href="#tools">
          Explore the collection
          <ArrowUpRight size={15} />
        </a>
      </footer>
      <Sheet
        open={sheet}
        onOpenChange={(open) => {
          if (!open) closeEvidence();
        }}
        title="Example evidence"
        description="Source details from the synthetic example."
        className="responsive-evidence-sheet"
        onCloseAutoFocus={(e) => {
          e.preventDefault();
          sourceTrigger.current?.focus();
        }}
      >
        {pinned && <EvidenceContent source={pinned} />}
      </Sheet>
    </div>
  );
}
