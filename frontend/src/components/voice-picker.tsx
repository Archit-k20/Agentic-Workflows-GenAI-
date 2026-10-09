"use client";
import { useEffect, useRef, useState } from "react";
import { Play, Square, Check, ChevronDown } from "lucide-react";
import { Sheet } from "./ui";
const voices = [
  ["af_heart", "Heart", "Warm · American English"],
  ["af_bella", "Bella", "Bright · American English"],
  ["af_nicole", "Nicole", "Soft · American English"],
  ["am_michael", "Michael", "Steady · American English"],
  ["am_fenrir", "Fenrir", "Expressive · American English"],
  ["bf_emma", "Emma", "Clear · British English"],
];
export function VoicePicker({
  value,
  onChange,
  disabled,
}: {
  value: string;
  onChange: (voice: string) => void;
  disabled: boolean;
}) {
  const [open, setOpen] = useState(false),
    [playing, setPlaying] = useState(""),
    [error, setError] = useState("");
  const audio = useRef<HTMLAudioElement | null>(null);
  const trigger = useRef<HTMLButtonElement | null>(null);
  function stop() {
    audio.current?.pause();
    audio.current = null;
    setPlaying("");
  }
  useEffect(
    () => () => {
      audio.current?.pause();
    },
    [],
  );
  async function preview(id: string) {
    const same = playing === id;
    stop();
    setError("");
    if (same) return;
    const clip = new Audio(`/audio/voices/${id}.mp3`);
    audio.current = clip;
    clip.onended = () => {
      if (audio.current === clip) stop();
    };
    clip.onerror = () => {
      if (audio.current === clip) {
        stop();
        setError("Preview could not play. You can still select the voice.");
      }
    };
    setPlaying(id);
    try {
      await clip.play();
    } catch {
      if (audio.current === clip) {
        stop();
        setError("Audio playback was blocked. Try the preview again.");
      }
    }
  }
  return (
    <>
      <button
        type="button"
        id="voice"
        ref={trigger}
        className="button secondary full"
        disabled={disabled}
        aria-label={`Voice: ${voices.find((v) => v[0] === value)?.[1] || "Heart"}`}
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={() => setOpen(true)}
      >
        {voices.find((v) => v[0] === value)?.[1] || "Heart"}
        <ChevronDown size={16} />
      </button>
      <Sheet
        open={open}
        onOpenChange={(next) => {
          setOpen(next);
          if (!next) stop();
        }}
        onCloseAutoFocus={(event) => {
          event.preventDefault();
          trigger.current?.focus();
        }}
        title="Choose a voice"
        description="Listen to a bundled sample before choosing. Previews need no backend or AI request."
      >
        <div className="voice-list">
          {voices.map(([id, name, description]) => (
            <div className="voice-row" key={id}>
              <button
                className="voice-choice"
                type="button"
                aria-pressed={value === id}
                onClick={() => {
                  onChange(id);
                  stop();
                  setOpen(false);
                }}
              >
                <span>
                  <strong>{name}</strong>
                  <small>{description}</small>
                </span>
                {value === id && <Check size={16} />}
              </button>
              <button
                type="button"
                className="icon-button"
                aria-label={`${playing === id ? "Stop" : "Play"} ${name} preview`}
                onClick={() => void preview(id)}
              >
                {playing === id ? <Square size={16} /> : <Play size={16} />}
              </button>
            </div>
          ))}
          <p className="helper" role="status">
            {error || "Kokoro voices · English · synthesized voice samples"}
          </p>
        </div>
      </Sheet>
    </>
  );
}
