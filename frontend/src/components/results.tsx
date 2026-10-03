"use client";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Check,
  AlertTriangle,
  Minus,
  FileText,
  AudioLines,
  Image as ImageIcon,
  ArrowUpRight,
} from "lucide-react";
import type { Result, Source } from "../lib/types";
import type { components } from "../lib/api-types";
import { CopyButton } from "./ui";
import { Citation } from "./evidence";
import { media } from "../lib/api";
type RecordValue = Record<string, unknown>;
const record = (v: unknown): RecordValue =>
  v && typeof v === "object" && !Array.isArray(v) ? (v as RecordValue) : {};
const text = (v: unknown) =>
  v === null || v === undefined
    ? ""
    : typeof v === "string"
      ? v
      : JSON.stringify(v);
const list = (v: unknown): unknown[] => (Array.isArray(v) ? v : []);
function Markdown({
  value,
  sources = [],
  onPin,
}: {
  value: string;
  sources?: Source[];
  onPin: (s: Source) => void;
}) {
  return (
    <div className="prose">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h2 className="report-title">{children}</h2>,
          h2: ({ children }) => <h3 className="report-section">{children}</h3>,
          a: ({ href, children }) => {
            const source = href?.startsWith("#source-")
              ? sources.find((s) => s.label === href.slice(8))
              : null;
            return source ? (
              <Citation source={source} onPin={onPin} />
            ) : (
              <a href={href} target="_blank" rel="noreferrer">
                {children}
              </a>
            );
          },
        }}
      >
        {value.replace(/\[(S\d+)\]/g, (match, label) =>
          sources.some((s) => s.label === label)
            ? `[${label}](#source-${label})`
            : match,
        )}
      </ReactMarkdown>
    </div>
  );
}
function Review({
  value,
  label = "Model review",
}: {
  value: unknown;
  label?: string;
}) {
  const v = record(value);
  const known = typeof v.passes_review === "boolean";
  return (
    <div className="review-strip">
      <span className={known && v.passes_review ? "good" : "notice"}>
        {known && v.passes_review ? (
          <Check size={15} />
        ) : (
          <AlertTriangle size={15} />
        )}{" "}
        {label}:{" "}
        {known
          ? v.passes_review
            ? "reported passed"
            : "issues flagged"
          : "unavailable"}
      </span>
      {list(v.issues).map((issue, i) => (
        <p key={i}>{text(issue)}</p>
      ))}
    </div>
  );
}
function Sources({
  sources,
  onPin,
}: {
  sources: Source[];
  onPin: (s: Source) => void;
}) {
  return (
    <div className="source-index">
      <span className="mono">
        EVIDENCE / {String(sources.length).padStart(2, "0")}
      </span>
      {sources.map((source, i) => (
        <button key={i} className="source-row" onClick={() => onPin(source)}>
          <span className="citation-label">{source.label}</span>
          <span>
            {source.title ||
              source.metadata?.source?.toString() ||
              "Retrieved source"}
          </span>
          <ArrowUpRight size={15} />
        </button>
      ))}
    </div>
  );
}
function TextArtifact({
  title,
  value,
  sources,
  onPin,
}: {
  title: string;
  value: string;
  sources?: Source[];
  onPin: (s: Source) => void;
}) {
  return (
    <section className="artifact-section">
      <div className="artifact-heading">
        <h3>{title}</h3>
        <CopyButton text={value} />
      </div>
      <Markdown value={value} sources={sources} onPin={onPin} />
    </section>
  );
}
function Verification({
  value,
  title,
}: {
  value: components["schemas"]["Verification"];
  title: string;
}) {
  return (
    <div className="verification-console">
      <div className="console-heading">
        <span className="mono">{title}</span>
        <span className={value.passed ? "good" : "notice"}>
          {value.passed ? "Checks passed" : "Check details"}
        </span>
      </div>
      {value.checks.map((check, i) => {
        const unavailable = /unavailable|not installed/i.test(check.details);
        return (
          <div className="verification-check" key={i}>
            <span
              className={
                unavailable ? "muted" : check.passed ? "good" : "notice"
              }
            >
              {unavailable ? (
                <Minus size={15} />
              ) : check.passed ? (
                <Check size={15} />
              ) : (
                <AlertTriangle size={15} />
              )}
            </span>
            <div>
              <strong className="mono">{check.name}</strong>
              <span className="check-state">
                {unavailable
                  ? "Unavailable"
                  : check.passed
                    ? "Passed"
                    : "Failed"}
              </span>
              <pre>{check.details}</pre>
            </div>
          </div>
        );
      })}
      <p>
        Syntax and compilation checks. They do not establish functional
        correctness or security.
      </p>
    </div>
  );
}
function Media({ id, kind }: { id: string; kind: "image" | "audio" }) {
  const [url, setUrl] = useState(""),
    [error, setError] = useState("");
  useEffect(() => {
    let disposed = false,
      objectURL = "";
    setError("");
    setUrl("");
    media(id)
      .then((value) => {
        objectURL = value;
        if (!disposed) setUrl(value);
        else URL.revokeObjectURL(value);
      })
      .catch((error) => {
        if (!disposed) setError(error.message);
      });
    return () => {
      disposed = true;
      if (objectURL) URL.revokeObjectURL(objectURL);
    };
  }, [id]);
  return (
    <div className={`media-output ${kind}`}>
      {error ? (
        <p role="alert">{error}</p>
      ) : url ? (
        kind === "image" ? (
          <img src={url} alt="Generated image from your prompt" />
        ) : (
          <audio src={url} controls preload="metadata" />
        )
      ) : (
        <span>
          <span className="status-pulse" />
          {kind === "image" ? <ImageIcon /> : <AudioLines />} Loading generated{" "}
          {kind}…
        </span>
      )}
    </div>
  );
}
export function Results({
  result,
  onPin,
  onSummarize,
}: {
  result: Result;
  onPin: (s: Source) => void;
  onSummarize: (text: string) => void;
}) {
  let body;
  switch (result.tool) {
    case "research":
      body = (
        <>
          <div className="result-kicker">
            <span className="eyebrow">RESEARCH / FINAL REPORT</span>
            <CopyButton text={result.final_report} />
          </div>
          <Markdown
            value={result.final_report}
            sources={result.sources}
            onPin={onPin}
          />
          <Review value={result.critique} />
          <div className="citation-check mono">
            Citation labels:{" "}
            {result.citation_check.has_any_citation ? "present" : "missing"} ·
            Unknown labels:{" "}
            {result.citation_check.unknown_labels.join(", ") || "none"}
          </div>
          <Sources sources={result.sources} onPin={onPin} />
          <details className="secondary-details">
            <summary>Research plan</summary>
            <pre>{JSON.stringify(result.plan, null, 2)}</pre>
          </details>
        </>
      );
      break;
    case "code":
      body = (
        <>
          <div className="result-kicker">
            <span className="eyebrow">
              CODE / {result.language.toUpperCase()}
            </span>
            <CopyButton text={result.final_code} />
          </div>
          <pre className="code-output">
            <code>{result.final_code}</code>
          </pre>
          <Verification
            value={result.final_verification}
            title="FINAL VERIFICATION"
          />
          {result.repair_attempted && (
            <>
              <div className="repair-note">
                One repair attempt was made after the initial checks.
              </div>
              <Verification
                value={result.initial_verification}
                title="INITIAL VERIFICATION"
              />
              <div className="code-comparison">
                <section>
                  <h4>Initial code</h4>
                  <pre>
                    <code>{result.initial_code}</code>
                  </pre>
                </section>
                <section>
                  <h4>Final code</h4>
                  <pre>
                    <code>{result.final_code}</code>
                  </pre>
                </section>
              </div>
            </>
          )}
        </>
      );
      break;
    case "content":
      body = (
        <>
          <div className="result-kicker">
            <span className="eyebrow">CONTENT / ARTIFACT WORKBENCH</span>
            <span className="mono">{text(result.package.title)}</span>
          </div>
          <TextArtifact
            title="Final script"
            value={result.final_script}
            onPin={onPin}
          />
          <details className="secondary-details">
            <summary>Content plan</summary>
            <pre>{JSON.stringify(result.plan, null, 2)}</pre>
          </details>
          <section className="artifact-section">
            <h3>Image prompts</h3>
            {list(result.package.image_prompts).map((prompt, i) => (
              <div className="prompt-artifact" key={i}>
                <span className="mono">FRAME / 0{i + 1}</span>
                <p>{text(prompt)}</p>
                <CopyButton text={text(prompt)} />
              </div>
            ))}
          </section>
          <section className="artifact-section">
            <h3>Platform captions</h3>
            {Object.entries(result.final_captions).map(
              ([platform, caption]) => (
                <div className="caption-artifact" key={platform}>
                  <div className="artifact-heading">
                    <span className="mono">{platform.toUpperCase()}</span>
                    <CopyButton text={caption} />
                  </div>
                  <p>{caption}</p>
                </div>
              ),
            )}
          </section>
          <div className="hashtags">
            {list(result.package.hashtags).map((tag, i) => (
              <span key={i}>{text(tag)}</span>
            ))}
          </div>
          {result.package.cta && (
            <p className="cta-note">
              Call to action: {text(result.package.cta)}
            </p>
          )}
          <Review value={result.critique} />
          {result.artifact_id && (
            <section className="artifact-section">
              <h3>Narration</h3>
              <Media id={result.artifact_id} kind="audio" />
            </section>
          )}
          {result.audio_error && <p className="notice">{result.audio_error}</p>}
        </>
      );
      break;
    case "documents":
      body = (
        <>
          <div className="result-kicker">
            <span className="eyebrow">DOCUMENT / INTELLIGENCE</span>
            <span className="mono">{result.documents.length} FILES</span>
          </div>
          {result.documents.map((document, i) => {
            const analysis = record(document.analysis),
              entities = record(analysis.entities);
            return (
              <section className="document-result" key={i}>
                <div className="document-title">
                  <FileText size={20} />
                  <h3>{text(document.name)}</h3>
                  <span className="badge">{text(analysis.document_type)}</span>
                </div>
                <TextArtifact
                  title="Summary"
                  value={text(analysis.summary)}
                  onPin={onPin}
                />
                <h4>Entities</h4>
                <dl className="entity-grid">
                  {Object.entries(entities).map(([key, value]) => (
                    <div key={key}>
                      <dt>{key}</dt>
                      <dd>
                        {list(value).map(text).join(", ") || "None identified"}
                      </dd>
                    </div>
                  ))}
                </dl>
                <h4>Action items</h4>
                {list(analysis.action_items).length ? (
                  <div
                    className="table-scroll"
                    tabIndex={0}
                    aria-label="Action items, scroll horizontally if needed"
                  >
                    <table>
                      <thead>
                        <tr>
                          <th>Task</th>
                          <th>Owner</th>
                          <th>Due date</th>
                          <th>Priority</th>
                        </tr>
                      </thead>
                      <tbody>
                        {list(analysis.action_items).map((item, j) => {
                          const action = record(item);
                          return (
                            <tr key={j}>
                              <td>{text(action.task)}</td>
                              <td>{text(action.owner)}</td>
                              <td>{text(action.due_date)}</td>
                              <td>{text(action.priority)}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p>No action items detected.</p>
                )}
                <h4>Risks and notes</h4>
                <ul className="risk-list">
                  {list(analysis.risks).map((risk, j) => (
                    <li key={j}>{text(risk)}</li>
                  ))}
                </ul>
                <details className="secondary-details">
                  <summary>Extracted text preview</summary>
                  <p>{text(document.text_preview)}</p>
                </details>
              </section>
            );
          })}
        </>
      );
      break;
    case "support": {
      const final = result.final;
      body = (
        <>
          <div className="result-kicker">
            <span className="eyebrow">SUPPORT / DECISION</span>
            <span
              className={
                final.resolution_type === "answer"
                  ? "decision answer"
                  : "decision escalate"
              }
            >
              {final.resolution_type === "answer" ? "Answer" : "Escalate"}
            </span>
          </div>
          <div className="triage-meta">
            <div>
              <span className="mono">CLASSIFICATION</span>
              <strong>
                {text(
                  result.intent.category ||
                    result.intent.intent ||
                    result.intent.intent_type,
                ) || "See details"}
              </strong>
            </div>
            <div>
              <span className="mono">MODEL CONFIDENCE</span>
              <strong>
                {typeof final.confidence === "number"
                  ? `${Math.round(final.confidence * 100)} / 100`
                  : "Unavailable"}
              </strong>
              <small>A model score, not a calibrated probability.</small>
            </div>
          </div>
          <TextArtifact
            title="Recommended response"
            value={text(final.answer)}
            sources={result.sources}
            onPin={onPin}
          />
          {final.escalation_reason && (
            <div className="escalation-note">
              <AlertTriangle size={18} />
              <p>{text(final.escalation_reason)}</p>
            </div>
          )}
          <section className="next-step">
            <span className="eyebrow">NEXT STEP</span>
            <p>{text(final.recommended_next_step)}</p>
          </section>
          <Sources sources={result.sources} onPin={onPin} />
        </>
      );
      break;
    }
    case "document-qa":
    case "url-qa":
      body = (
        <>
          <TextArtifact
            title="Answer from context"
            value={result.answer}
            sources={result.sources}
            onPin={onPin}
          />
          <Sources sources={result.sources} onPin={onPin} />
        </>
      );
      break;
    case "image":
      body = (
        <>
          <div className="result-kicker">
            <span className="eyebrow">IMAGE / 1024 × 1024</span>
          </div>
          <Media id={result.artifact_id} kind="image" />
        </>
      );
      break;
    case "speech":
      body = (
        <>
          <div className="result-kicker">
            <span className="eyebrow">NARRATION / TTS-1</span>
          </div>
          <Media id={result.artifact_id} kind="audio" />
        </>
      );
      break;
    default:
      if ("text" in result)
        body = (
          <>
            <TextArtifact
              title={
                result.tool === "ocr"
                  ? "Extracted text"
                  : result.tool === "captions"
                    ? "Transcript"
                    : "Summary"
              }
              value={result.text}
              onPin={onPin}
            />
            {result.tool === "ocr" && (
              <button
                className="button secondary"
                onClick={() => onSummarize(result.text)}
              >
                Summarize extracted text <ArrowUpRight size={15} />
              </button>
            )}
          </>
        );
  }
  return (
    <div className="result-content">
      {body}
      <details className="secondary-details raw-details">
        <summary>Details · complete structured result</summary>
        <CopyButton text={JSON.stringify(result, null, 2)} />
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </div>
  );
}
