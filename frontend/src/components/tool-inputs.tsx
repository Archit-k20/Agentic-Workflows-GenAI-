"use client";
import { ArrowRight, ArrowUpRight, Upload, FileText, X } from "lucide-react";
import { voices, platforms, tones, type Tool } from "../lib/tools";
import { hasSample } from "../lib/sample-state";
import { useWorkspace } from "./provider";
import { useToolController } from "./use-tool-controller";
import { ToolIcon, AttachmentPreview } from "./tool-visuals";
import { VoicePicker } from "./voice-picker";
export function ToolInputs({
  tool,
  controller,
  setSettings,
  loadSample,
}: {
  tool: Tool;
  controller: ReturnType<typeof useToolController>;
  setSettings: (v: boolean) => void;
  loadSample: () => void;
}) {
  const { mode, update } = useWorkspace();
  const {
    draft,
    busy,
    qa,
    pasted,
    transcriptTool,
    selectedVoice,
    fileInput,
    remaining,
    change,
    execute,
    selectFiles,
  } = controller;
  return (
    <section className="input-panel">
      <div className="panel-label">
        <span className="mono">Your input</span>
        <ToolIcon name={tool.icon} />
      </div>
      <form
        onSubmit={(event) => {
          event.preventDefault();
          void execute();
        }}
      >
        {tool.files && (
          <>
            <label className="field-label" htmlFor="files">
              {tool.maxFiles === 1
                ? "Select a file"
                : `Select up to ${tool.maxFiles} files`}
            </label>
            <label className="file-drop" htmlFor="files">
              <Upload size={22} />
              <strong>
                Choose {tool.id === "ocr" ? "an image" : "your files"}
              </strong>
              <span>
                {tool.files
                  .split(",")
                  .map((v) => v.slice(1).toUpperCase())
                  .join(" / ")}{" "}
                · up to 200 MB each
                {mode !== "openai" &&
                  " · PDFs: 50 pages · extracted text: 12,000 tokens per file"}
              </span>
            </label>
            <input
              ref={fileInput}
              className="visually-hidden"
              id="files"
              type="file"
              accept={tool.files}
              multiple={(tool.maxFiles || 1) > 1}
              disabled={busy}
              onChange={(e) => selectFiles(e.target.files)}
            />
            <div className="attachment-tray">
              {draft.files.map((file, i) => (
                <div className="attachment-chip" key={`${file.name}-${i}`}>
                  <FileText size={15} />
                  <div>
                    <span title={file.name}>{file.name}</span>
                    <small className="mono">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </small>
                  </div>
                  <button
                    type="button"
                    disabled={busy}
                    aria-label={`Remove ${file.name}`}
                    onClick={() =>
                      update(tool.id, {
                        files: draft.files.filter((_, j) => j !== i),
                        fileIds: [],
                        context: undefined,
                        inputsChanged: !!draft.result,
                        status: draft.files.length > 1 ? "ready" : "empty",
                      })
                    }
                  >
                    <X size={14} />
                  </button>
                </div>
              ))}
            </div>
            <AttachmentPreview files={draft.files} />
          </>
        )}
        {tool.urls && (
          <div className="field">
            <label htmlFor="urls">
              Source URLs <span className="mono">MAX {tool.urls}</span>
            </label>
            <textarea
              id="urls"
              value={draft.input.urls || ""}
              onChange={(e) => change("urls", e.target.value)}
              placeholder={
                "https://example.com/article\nOne source URL per line"
              }
              disabled={busy}
              rows={tool.urls === 3 ? 3 : 4}
            />
            <p className="helper">
              Use public pages you want the workflow to read.
            </p>
          </div>
        )}
        {qa && (
          <div className="context-control">
            <button
              type="button"
              className="button secondary full"
              disabled={busy}
              onClick={() => void execute(true)}
            >
              {draft.context
                ? "Reprocess context"
                : tool.id === "document-qa"
                  ? "Process files"
                  : "Process URLs"}
              <ArrowRight size={15} />
            </button>
            {draft.context && (
              <span className="context-ready">
                <span className="trace-dot" /> Context ready · ask a question
                below
              </span>
            )}
          </div>
        )}
        {transcriptTool && (
          <div className="field">
            <label htmlFor="transcript-source">Transcript source</label>
            <select
              id="transcript-source"
              value={draft.input.source_type || "url"}
              disabled={busy}
              onChange={(e) => change("source_type", e.target.value)}
            >
              <option value="url">YouTube URL</option>
              <option value="transcript">Paste transcript</option>
            </select>
            <p className="helper">
              If YouTube blocks extraction or captions are unavailable, paste
              the transcript here.
            </p>
          </div>
        )}
        {pasted && (
          <div className="field">
            <label htmlFor="transcript-text">Transcript text</label>
            <textarea
              id="transcript-text"
              rows={10}
              disabled={busy}
              value={draft.input.transcript_text || ""}
              onChange={(e) => change("transcript_text", e.target.value)}
            />
          </div>
        )}
        {tool.field && !pasted && (
          <div className="field">
            <label htmlFor="primary-input">{tool.label}</label>
            {tool.field === "url" ? (
              <input
                id="primary-input"
                type="url"
                value={draft.input[tool.field] || ""}
                onChange={(e) => change(tool.field!, e.target.value)}
                placeholder={tool.placeholder}
                disabled={busy}
              />
            ) : (
              <textarea
                id="primary-input"
                value={draft.input[tool.field] || ""}
                onChange={(e) => change(tool.field!, e.target.value)}
                placeholder={tool.placeholder}
                disabled={busy}
                rows={qa ? 3 : tool.id === "text-summary" ? 7 : 5}
              />
            )}
          </div>
        )}
        {tool.id === "code" && (
          <div className="field">
            <label htmlFor="language">Language</label>
            <select
              id="language"
              value={draft.input.language}
              onChange={(e) => change("language", e.target.value)}
              disabled={busy}
            >
              {["python", "javascript", "java", "c", "c++"].map((language) => (
                <option key={language}>{language}</option>
              ))}
            </select>
          </div>
        )}
        {tool.id === "content" && (
          <>
            <div className="field">
              <label htmlFor="tone">Tone</label>
              <select
                id="tone"
                value={draft.input.tone}
                disabled={busy}
                onChange={(e) => change("tone", e.target.value)}
              >
                {tones.map((tone) => (
                  <option key={tone}>{tone}</option>
                ))}
              </select>
            </div>
            <fieldset className="platform-field">
              <legend>Target platforms</legend>
              <div>
                {platforms.map((platform) => (
                  <label key={platform}>
                    <input
                      type="checkbox"
                      checked={
                        draft.input.platforms?.split(",").includes(platform) ||
                        false
                      }
                      disabled={busy}
                      onChange={(e) =>
                        change(
                          "platforms",
                          (e.target.checked
                            ? [
                                ...draft.input.platforms
                                  .split(",")
                                  .filter(Boolean),
                                platform,
                              ]
                            : draft.input.platforms
                                .split(",")
                                .filter((p) => p !== platform)
                          ).join(","),
                        )
                      }
                    />
                    {platform}
                  </label>
                ))}
              </div>
            </fieldset>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={draft.input.include_audio === "true"}
                disabled={busy}
                onChange={(e) =>
                  change("include_audio", String(e.target.checked))
                }
              />{" "}
              Generate narration
            </label>
          </>
        )}
        {tool.voice &&
          (tool.id === "speech" || draft.input.include_audio === "true") && (
            <div className="field">
              <label htmlFor="voice">Voice</label>
              {mode !== "openai" ? (
                <VoicePicker
                  value={selectedVoice}
                  disabled={busy}
                  onChange={(voice) => change("voice", voice)}
                />
              ) : (
                <select
                  id="voice"
                  value={selectedVoice}
                  disabled={busy}
                  onChange={(e) => change("voice", e.target.value)}
                >
                  {voices.map((voice) => (
                    <option key={voice}>{voice}</option>
                  ))}
                </select>
              )}
            </div>
          )}
        <div className="submit-area">
          <button
            className="button primary full"
            type="submit"
            disabled={busy || (qa && !draft.context)}
          >
            {busy
              ? "Working…"
              : draft.status === "error"
                ? "Retry explicitly"
                : qa
                  ? "Ask question"
                  : tool.id === "ocr"
                    ? "Extract text"
                    : `Run ${tool.name}`}
            <ArrowRight size={17} />
          </button>
          <p className="key-note">
            {mode === "free"
              ? "Free access · text and images use hosted AI; retrieval, OCR and speech run on our server. Text may fall back locally."
              : mode === "local"
                ? "Local processing · inference stays on our server. Multi-stage CPU reports can take several minutes. Image generation needs hosted mode."
                : "Optional OpenAI mode · your key is held only in this tab’s memory."}
            <button type="button" onClick={() => setSettings(true)}>
              Change mode <ArrowUpRight size={12} />
            </button>
            {remaining && mode !== "openai" && (
              <span>
                Remaining today: {remaining.text} text · {remaining.image}{" "}
                images · {remaining.audio} audio · {remaining.context} contexts.
                Resets at 00:00 UTC; shared networks share limits.
              </span>
            )}
          </p>
        </div>
      </form>
      {hasSample(tool.id) && !draft.sample && (
        <button className="try-sample" onClick={loadSample}>
          Explore a sample result <ArrowUpRight size={14} />
        </button>
      )}
      <div className="input-footnote mono">Your draft stays in this tab</div>
    </section>
  );
}
