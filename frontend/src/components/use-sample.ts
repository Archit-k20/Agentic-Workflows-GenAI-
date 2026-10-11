"use client";
import { useEffect, useState } from "react";
import type { ToolId } from "../lib/tools";
import { hasSample, sampleLoaders, type Sample } from "../lib/sample-state";
export function useSample(id: ToolId, enabled: boolean, initial?: Sample) {
  const [loaded, setLoaded] = useState<{ id: ToolId; value: Sample } | null>(
    initial ? { id, value: initial } : null,
  );
  const [error, setError] = useState("");
  useEffect(() => {
    if (!enabled || !hasSample(id)) return;
    let active = true;
    setError("");
    sampleLoaders[id]()
      .then(({ default: value }) => {
        if (active) setLoaded({ id, value });
      })
      .catch(() => {
        if (active)
          setError(
            "This example could not load. Reload the page to try again.",
          );
      });
    return () => {
      active = false;
    };
  }, [id, enabled]);
  return {
    sample: enabled && loaded?.id === id ? loaded.value : undefined,
    error,
  };
}
