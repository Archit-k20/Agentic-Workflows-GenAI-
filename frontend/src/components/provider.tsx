"use client";
import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from "react";
import { MotionConfig } from "motion/react";
import * as Tooltip from "@radix-ui/react-tooltip";
import type { ToolId } from "../lib/tools";
import type { Result, Stage, ContextResult } from "../lib/types";
export type Draft = {
  input: Record<string, string>;
  files: File[];
  fileIds: string[];
  context?: ContextResult;
  result?: Result;
  status:
    | "empty"
    | "ready"
    | "processing"
    | "success"
    | "partial-success"
    | "error";
  stages: Stage[];
  warnings: string[];
  error?: string;
  started?: number;
  finished?: number;
  sample?: boolean;
  inputsChanged?: boolean;
};
export const emptyDraft = (): Draft => ({
  input: {
    voice: "alloy",
    language: "python",
    tone: "professional",
    platforms: "linkedin,x",
    include_audio: "false",
  },
  files: [],
  fileIds: [],
  status: "empty",
  stages: [],
  warnings: [],
});
type State = {
  key: string;
  setKey: (s: string) => void;
  theme: string;
  toggleTheme: () => void;
  drafts: Partial<Record<ToolId, Draft>>;
  update: (
    id: ToolId,
    change: Partial<Draft> | ((d: Draft) => Partial<Draft>),
  ) => void;
  reset: () => void;
};
const Context = createContext<State | null>(null);
export function Provider({ children }: { children: ReactNode }) {
  const [key, setKey] = useState(""),
    [theme, setTheme] = useState("dark"),
    [themeReady, setThemeReady] = useState(false),
    [drafts, setDrafts] = useState<State["drafts"]>({});
  useEffect(() => {
    try {
      const saved = localStorage.getItem("trace-theme");
      if (saved === "light" || saved === "dark") setTheme(saved);
    } catch {
      /* Preferences remain usable in memory when storage is blocked. */
    }
    setThemeReady(true);
  }, []);
  useEffect(() => {
    if (!themeReady) return;
    document.documentElement.dataset.theme = theme;
    try {
      localStorage.setItem("trace-theme", theme);
    } catch {
      /* Optional preference storage. */
    }
  }, [theme, themeReady]);
  const update: State["update"] = useCallback(
    (id, change) =>
      setDrafts((previous) => {
        const draft = previous[id] || emptyDraft();
        return {
          ...previous,
          [id]: {
            ...draft,
            ...(typeof change === "function" ? change(draft) : change),
          },
        };
      }),
    [],
  );
  return (
    <Context.Provider
      value={{
        key,
        setKey,
        theme,
        toggleTheme: () => setTheme((t) => (t === "dark" ? "light" : "dark")),
        drafts,
        update,
        reset: () => setDrafts({}),
      }}
    >
      <MotionConfig reducedMotion="user">
        <Tooltip.Provider delayDuration={250}>{children}</Tooltip.Provider>
      </MotionConfig>
    </Context.Provider>
  );
}
export function useWorkspace() {
  const state = useContext(Context);
  if (!state) throw new Error("Workspace provider missing");
  return state;
}
