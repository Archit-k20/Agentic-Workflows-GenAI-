import Link from "next/link";
import { ArrowDown, ArrowRight, ArrowUpRight } from "lucide-react";
import { Wordmark } from "../components/ui";
import { ThemeToggle } from "../components/theme-toggle";
import { github } from "../lib/tools";
import styles from "./intro.module.css";

function ExploreLink() {
  return (
    <Link href="/explore" className={styles.explore}>
      <span>Explore TRACE</span>
      <span className={styles.exploreArrow} aria-hidden="true">
        <ArrowUpRight size={24} />
      </span>
    </Link>
  );
}

export default function Introduction() {
  return (
    <div className={styles.introduction}>
      <header className={styles.masthead}>
        <Link href="/" aria-label="TRACE home">
          <Wordmark />
        </Link>
        <span className={styles.byline}>An AI project by Archit Kumar</span>
        <nav aria-label="Introduction navigation">
          <ThemeToggle />
          <Link href="/explore" className={styles.skipIntro}>
            Enter studio <ArrowUpRight size={16} />
          </Link>
        </nav>
      </header>
      <main id="main">
        <section className={styles.arrival} aria-label="Welcome to TRACE">
          <div className={styles.atmosphere} aria-hidden="true">
            <svg viewBox="0 0 1440 1000" preserveAspectRatio="xMidYMid slice">
              <defs>
                <filter id="trace-soft">
                  <feGaussianBlur stdDeviation="28" />
                </filter>
                <filter id="trace-fold">
                  <feGaussianBlur stdDeviation="7" />
                </filter>
                <linearGradient id="trace-ribbon" x1="0" y1="0" x2="1" y2="1">
                  <stop stopColor="currentColor" stopOpacity=".04" />
                  <stop
                    offset=".45"
                    stopColor="currentColor"
                    stopOpacity=".9"
                  />
                  <stop offset="1" stopColor="currentColor" stopOpacity=".08" />
                </linearGradient>
              </defs>
              <g
                fill="none"
                stroke="url(#trace-ribbon)"
                filter="url(#trace-soft)"
              >
                <path
                  d="M-160 710C240 670 30 70 590 80S1090 700 1610 420"
                  strokeWidth="155"
                />
                <path
                  d="M-130 950C310 1160 640 760 1120 840S1550 1130 1620 690"
                  strokeWidth="115"
                />
              </g>
              <path
                d="M-160 720C240 680 60 120 600 110S1100 730 1640 450"
                fill="none"
                stroke="url(#trace-ribbon)"
                strokeWidth="3"
                filter="url(#trace-fold)"
              />
            </svg>
            <div className={styles.grain} />
          </div>
          <div className={styles.hero}>
            <p className={styles.kicker}>A personal exploration of AI</p>
            <h1>
              Start with something
              <br />
              on your mind.
            </h1>
            <p className={styles.invitation}>
              A question. A document. An idea taking shape.
              <br className={styles.desktopBreak} />
              Meet TRACE — a personal collection of AI tools
              <br className={styles.desktopBreak} />
              for seeing where it could go.
            </p>
            <ExploreLink />
          </div>
          <a href="#the-idea" className={styles.scrollCue}>
            <span>A little more about it</span>
            <ArrowDown size={18} />
          </a>
          <span className={styles.marginNote} aria-hidden="true">
            Made with curiosity. Built to be used.
          </span>
        </section>
        <section className={styles.story} aria-labelledby="idea-title">
          <div className={styles.storyHeading}>
            <p id="the-idea" tabIndex={-1} className={styles.sectionLabel}>
              The idea behind TRACE
            </p>
            <h2 id="idea-title">
              Less staring at a blank page.
              <br />
              <span>More finding a way forward.</span>
            </h2>
            <p className={styles.synopsis}>
              I built TRACE to bring the things I keep reaching for into one
              place: making sense of a long document, exploring a question,
              turning a rough idea into something I can work with.
            </p>
            <p className={styles.synopsis}>
              It’s a collection of fifteen tools for research, reading, code,
              images, speech and content. You bring the starting point. Pick a
              tool, try it, and look inside the result.
            </p>
          </div>
          <div className={styles.possibilities}>
            <article>
              <span className={styles.prompt}>“There’s a lot to read.”</span>
              <ArrowDown size={18} aria-hidden="true" />
              <h3>Find the useful part.</h3>
              <p>
                Summarise a report, ask questions of your documents, or follow a
                research answer back to its sources.
              </p>
            </article>
            <article>
              <span className={styles.prompt}>
                “I have the beginnings of an idea.”
              </span>
              <ArrowDown size={18} aria-hidden="true" />
              <h3>Give it a first form.</h3>
              <p>
                Make an image, hear a piece of writing, draft code, or shape a
                brief into a script and captions.
              </p>
            </article>
            <article>
              <span className={styles.prompt}>“How did it get there?”</span>
              <ArrowDown size={18} aria-hidden="true" />
              <h3>Look a little closer.</h3>
              <p>
                Inspect the sources, processing steps and available checks. See
                what the tool did — and what still needs your judgement.
              </p>
            </article>
          </div>
          <div className={styles.threshold}>
            <div className={styles.traceMark} aria-hidden="true">
              <svg viewBox="0 0 180 80" fill="none">
                <path d="M0 40h35c22 0 20-30 48-30s25 60 53 60 25-30 44-30" />
                <path d="M0 40h180" />
                <circle cx="35" cy="40" r="3" />
                <circle cx="136" cy="70" r="3" />
              </svg>
            </div>
            <h2>Take a look around.</h2>
            <p>
              Start with a ready-made example. Or bring something of your own.
            </p>
            <ExploreLink />
            <p className={styles.accessNote}>
              No account needed. Free access uses shared daily capacity.
            </p>
          </div>
        </section>
      </main>
      <footer className={styles.footer}>
        <span>Built by Archit Kumar</span>
        <nav aria-label="Project links">
          <Link href="/explore#about">
            About the project <ArrowRight size={14} />
          </Link>
          <a href={github} target="_blank" rel="noreferrer">
            View the code <ArrowUpRight size={14} />
          </a>
        </nav>
      </footer>
    </div>
  );
}
