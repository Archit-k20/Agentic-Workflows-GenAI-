"use client";
import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import { ChevronDown, Check, Clock3, AlertCircle } from "lucide-react";
import type { Draft } from "./provider";
export function Status({ draft }: { draft: Draft }) {
  const [open, setOpen] = useState(false),
    [now, setNow] = useState(0);
  const reduced = useReducedMotion();
  useEffect(() => {
    if (draft.status !== "processing") return;
    setNow(Date.now());
    const timer = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(timer);
  }, [draft.status]);
  const elapsed = draft.started
    ? Math.max(
        0,
        Math.floor(
          ((draft.finished || now || draft.started) - draft.started) / 1000,
        ),
      )
    : 0;
  let outcome = "Result ready";
  const result = draft.result;
  if (result?.tool === "code")
    outcome = result.final_verification.passed
      ? "Syntax checks passed"
      : "Checks need attention";
  if (result?.tool === "research" || result?.tool === "content")
    outcome =
      result.critique.passes_review === true
        ? "Review reported passed"
        : "Review needs attention";
  if (result?.tool === "support")
    outcome =
      result.final.resolution_type === "answer"
        ? "Decision: answer"
        : "Decision: escalate";
  const active = draft.stages.findLast((s) => s.status === "running");
  const title = draft.sample
    ? "Sample workflow"
    : draft.status === "processing"
      ? active?.name || "Connecting…"
      : draft.status === "success"
        ? outcome
        : draft.status === "partial-success"
          ? "Result with notes"
          : draft.status === "error"
            ? "Needs attention"
            : draft.status === "ready"
              ? "Ready to begin"
              : "Awaiting input";
  return (
    <div className="status-wrap">
      <motion.div
        layout={!reduced}
        transition={{ duration: 0.26 }}
        className={`status-capsule ${draft.status}`}
      >
        <button
          onClick={() => setOpen(!open)}
          aria-expanded={open}
          aria-controls="workflow-stages"
        >
          <span
            className={
              draft.status === "processing" ? "status-pulse" : "status-symbol"
            }
          >
            {draft.status === "error" ? (
              <AlertCircle size={15} />
            ) : draft.status === "success" || draft.sample ? (
              <Check size={15} />
            ) : (
              <Clock3 size={15} />
            )}
          </span>
          <span>{title}</span>
          {draft.started && !draft.sample && (
            <span className="mono elapsed">{elapsed}s</span>
          )}
          <ChevronDown size={13} className={open ? "rotate" : ""} />
        </button>
        <AnimatePresence>
          {open && (
            <motion.div
              id="workflow-stages"
              initial={{ opacity: 0, height: reduced ? "auto" : 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: reduced ? "auto" : 0 }}
              transition={{ duration: 0.18 }}
            >
              <div className="stages">
                <p>
                  {draft.sample
                    ? "Illustrative result; stages were not executed."
                    : draft.stages.length
                      ? "Observed execution stages"
                      : "Stages appear when execution reaches them."}
                </p>
                {draft.stages.map((stage, i) => (
                  <div className="stage-row" key={i}>
                    <svg width="18" height="30" aria-hidden="true">
                      <path d="M9 0v30" stroke="var(--line)" />
                      <motion.circle
                        cx="9"
                        cy="15"
                        r="3"
                        fill={
                          stage.status === "completed"
                            ? "var(--accent)"
                            : stage.status === "failed"
                              ? "var(--warning)"
                              : "var(--muted)"
                        }
                        initial={false}
                        animate={{ r: stage.status === "completed" ? 3 : 4 }}
                        transition={{ duration: reduced ? 0 : 0.12 }}
                      />
                    </svg>
                    <span>{stage.name}</span>
                    <span className="mono">
                      {stage.status === "completed"
                        ? "done"
                        : stage.status === "failed"
                          ? "failed"
                          : draft.status === "processing"
                            ? "running"
                            : "interrupted"}
                    </span>
                  </div>
                ))}
                {(draft.status === "success" ||
                  draft.status === "partial-success") &&
                  !draft.sample && (
                    <p>{outcome}. Open the result for details.</p>
                  )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}
