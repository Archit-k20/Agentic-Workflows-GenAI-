"use client";
import * as Tooltip from "@radix-ui/react-tooltip";
import { motion, useReducedMotion } from "motion/react";
import { X, ArrowUpRight, Pin, BookOpen } from "lucide-react";
import type { Source } from "../lib/types";
export function Citation({
  source,
  onPin,
}: {
  source: Source;
  onPin: (s: Source) => void;
}) {
  return (
    <Tooltip.Root>
      <Tooltip.Trigger asChild>
        <button
          className="citation"
          onClick={() => onPin(source)}
          aria-label={`Inspect source ${source.label}: ${source.title}`}
        >
          {source.label}
          <ArrowUpRight size={11} />
        </button>
      </Tooltip.Trigger>
      <Tooltip.Portal>
        <Tooltip.Content className="citation-preview" sideOffset={8}>
          <span className="mono">SOURCE / {source.label}</span>
          <strong>{source.title}</strong>
          <p>{source.summary || source.text}</p>
          <span className="mono">Click to pin evidence</span>
          <Tooltip.Arrow className="tooltip-arrow" />
        </Tooltip.Content>
      </Tooltip.Portal>
    </Tooltip.Root>
  );
}
export function EvidenceContent({ source }: { source: Source }) {
  return (
    <div className="evidence-content">
      <span className="eyebrow">{source.label} / SOURCE DETAILS</span>
      <h3>{source.title || "Retrieved context"}</h3>
      {source.url && (
        <a
          className="evidence-url"
          href={source.url}
          target="_blank"
          rel="noreferrer"
        >
          {source.url}
          <ArrowUpRight size={14} />
        </a>
      )}
      {source.summary && (
        <>
          <h4>Source digest</h4>
          <p>{source.summary}</p>
        </>
      )}
      {source.text && (
        <>
          <h4>Retrieved chunk</h4>
          <p className="chunk-text">{source.text}</p>
        </>
      )}
      {!!source.key_points?.length && (
        <>
          <h4>Key points</h4>
          <ul>
            {source.key_points.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </>
      )}
      {source.relevance && (
        <>
          <h4>Relevance</h4>
          <p>{source.relevance}</p>
        </>
      )}
      {source.metadata && Object.keys(source.metadata).length > 0 && (
        <>
          <h4>Metadata</h4>
          <dl>
            {Object.entries(source.metadata).map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd>{String(value)}</dd>
              </div>
            ))}
          </dl>
        </>
      )}
      <div className="inspector-note">
        <BookOpen size={16} />
        <p>
          Source content and retrieved metadata. Citation labels do not
          independently verify factual claims.
        </p>
      </div>
    </div>
  );
}
export function EvidenceInspector({
  source,
  onClose,
}: {
  source: Source;
  onClose: () => void;
}) {
  const reduced = useReducedMotion();
  return (
    <motion.aside
      layout={!reduced}
      className="evidence-inspector"
      initial={{ opacity: 0, x: reduced ? 0 : 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.26 }}
      aria-label="Pinned evidence"
    >
      <header>
        <span>
          <Pin size={15} /> EVIDENCE INSPECTOR
        </span>
        <button
          className="icon-button"
          onClick={onClose}
          aria-label="Close evidence inspector"
        >
          <X size={17} />
        </button>
      </header>
      <EvidenceContent source={source} />
    </motion.aside>
  );
}
