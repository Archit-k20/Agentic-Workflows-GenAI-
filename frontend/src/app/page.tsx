"use client";
import Link from "next/link";
import {
  ArrowRight,
  ArrowUpRight,
  Sun,
  Moon,
  ArrowDown,
  FileText,
  Braces,
  ScanText,
  Layers,
  LifeBuoy,
} from "lucide-react";
import { Wordmark, ExternalLink } from "../components/ui";
import { useWorkspace } from "../components/provider";
import { tools, featured, github, linkedin } from "../lib/tools";
const icons = [FileText, ScanText, Braces, Layers, LifeBuoy];
export default function Home() {
  const { theme, toggleTheme } = useWorkspace();
  return (
    <div className="landing">
      <header className="landing-nav">
        <Link href="/" aria-label="TRACE home">
          <Wordmark />
        </Link>
        <span className="nav-note">AN AI WORKSHOP / BY ARCHIT KUMAR</span>
        <nav>
          <ExternalLink href={github}>Source code</ExternalLink>
          <button
            className="icon-button"
            onClick={toggleTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
          >
            {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          </button>
          <Link className="small-open" href="/workspace/research">
            Open workspace <ArrowUpRight size={15} />
          </Link>
        </nav>
      </header>
      <main id="main">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="trace-dot" /> SOURCES. IDEAS. WORK IN PROGRESS.
            </div>
            <h1>
              Fifteen tools.
              <br />
              <em>One working desk.</em>
            </h1>
            <p>
              Read a document. Investigate a question. Write, build, or give an
              idea a voice. Keep the source material and the result in view.
            </p>
            <div className="hero-actions">
              <Link
                className="button primary"
                href="/workspace/research?sample=1"
              >
                Explore a sample <ArrowRight size={17} />
              </Link>
              <Link className="text-link" href="/workspace/research">
                Open workspace <ArrowUpRight size={16} />
              </Link>
            </div>
            <div className="hero-byline">
              <span className="tiny-line" /> Built by{" "}
              <strong>Archit Kumar</strong>
              <span className="mono">FREE ACCESS / NO VISITOR KEY</span>
            </div>
          </div>
          <div
            className="hero-instrument"
            aria-label="Illustration of sources becoming a reviewed report"
          >
            <div className="instrument-top mono">
              <span>
                <span className="trace-dot" /> WORKFLOW / RESEARCH
              </span>
              <span>INPUT → EVIDENCE → OUTPUT</span>
            </div>
            <div className="instrument-body">
              <div className="input-stack">
                <div className="document-outline back" />
                <div className="document-outline">
                  <div className="mono">SOURCE / 01</div>
                  <FileText size={24} />
                  <span>Campus repair field notes.</span>
                  <p className="illustration-excerpt">
                    Appointments distribute demand. Electrical faults need
                    specialist review.
                  </p>
                </div>
                <div className="source-tag mono">[S1] FIELD NOTES</div>
              </div>
              <svg
                className="hero-traces"
                viewBox="0 0 130 210"
                aria-hidden="true"
              >
                <path
                  d="M0 65H30Q45 65 45 80V105H130M0 145H30Q45 145 45 130V105"
                  fill="none"
                  stroke="var(--line)"
                />
                <path
                  d="M45 105H130"
                  stroke="var(--accent)"
                  strokeWidth="1.5"
                />
                <circle cx="45" cy="105" r="4" fill="var(--accent)" />
              </svg>
              <div className="report-preview">
                <div className="mono">
                  RESEARCH BRIEF <span>↗</span>
                </div>
                <h2>
                  Small service.
                  <br />
                  <em>Clear boundaries.</em>
                </h2>
                <p>
                  Read the evidence. Name the gaps.
                  <br />
                  Know what to ask next.
                </p>
                <div className="report-rule" />
                <div className="mono mini-proof">
                  <span>[S1]</span> SOURCE-LED SYNTHESIS
                </div>
              </div>
            </div>
            <div className="instrument-bottom">
              <div className="stage-mini">
                <span>01</span> Read
                <ArrowRight size={13} />
                <span>02</span> Synthesize
                <ArrowRight size={13} />
                <span>03</span> Review
              </div>
              <span className="mono">FICTIONAL EXAMPLE / NOT A LIVE RUN</span>
            </div>
          </div>
        </section>
        <section className="tool-atlas">
          <div className="atlas-intro">
            <div>
              <div className="eyebrow">THE WORKSHOP / SELECT A SAMPLE</div>
              <h2>
                Start with the work
                <br />
                <em>you want to do.</em>
              </h2>
            </div>
            <p>
              Each tool has its own working surface.
              <br />
              Every sample is local and makes no AI request.
            </p>
          </div>
          <div className="feature-list">
            {featured.map((id, i) => {
              const tool = tools.find((t) => t.id === id)!;
              const Icon = icons[i];
              return (
                <Link
                  className="feature-row"
                  key={id}
                  href={`/workspace/${id}?sample=1`}
                >
                  <span className="mono feature-number">0{i + 1}</span>
                  <div className="feature-icon">
                    <Icon size={22} />
                  </div>
                  <div>
                    <h3>{tool.name}</h3>
                    <p>{tool.description}</p>
                  </div>
                  <span className="feature-trail mono">
                    {tool.steps.join(" → ")}
                  </span>
                  <span className="sample-link">
                    Explore sample <ArrowUpRight size={17} />
                  </span>
                </Link>
              );
            })}
          </div>
        </section>
        <section className="project-note">
          <div className="eyebrow">A NOTE FROM THE WORKSHOP</div>
          <h2>
            The result is only <em>part of the story.</em>
          </h2>
          <p>
            I built TRACE to bring fifteen AI workflows into one place, with
            source inspection, visible processing stages, and clear limits on
            what a review or code check can tell you. Try the bundled samples,
            then use free access for live work. Optional OpenAI access is
            available in settings.
          </p>
          <div>
            <ExternalLink href={github}>
              Explore the project on GitHub
            </ExternalLink>
            <ExternalLink href={linkedin}>Connect with Archit</ExternalLink>
          </div>
        </section>
      </main>
      <footer className="landing-footer">
        <Wordmark />
        <span>Built by Archit Kumar</span>
        <span className="mono">READ / MAKE / INSPECT</span>
      </footer>
    </div>
  );
}
