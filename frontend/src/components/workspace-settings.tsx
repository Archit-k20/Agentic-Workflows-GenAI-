"use client";
import { Sun, Moon } from "lucide-react";
import { Sheet, ExternalLink as OutLink } from "./ui";
import { github } from "../lib/tools";
import { useWorkspace } from "./provider";
export function WorkspaceSettings({
  settings,
  setSettings,
  clear,
  clearNote,
}: {
  settings: boolean;
  setSettings: (v: boolean) => void;
  clear: () => Promise<void>;
  clearNote: string;
}) {
  const { mode, setMode, key, setKey, theme, toggleTheme, drafts } =
    useWorkspace();
  return (
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
            Cloudflare. When Cloudflare rejects image capacity, image prompts
            may go to our private Hugging Face worker; its quota also applies.
            Local mode keeps AI inference on our server; fetching your source
            URLs still contacts their websites. Switching modes requires Q&amp;A
            context reprocessing. English-first.
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
            <p>{theme === "dark" ? "Ink" : "Pearl"}</p>
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
  );
}
