"use client";
import Script from "next/script";
import { useEffect, useRef, useState } from "react";
import { Sheet } from "./ui";
import { setProofProvider } from "../lib/api";
type Turnstile = {
  render: (element: HTMLElement, options: Record<string, unknown>) => string;
  remove: (id: string) => void;
};
declare global {
  interface Window {
    turnstile?: Turnstile;
  }
}
export function VisitorVerification() {
  const sitekey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;
  const [open, setOpen] = useState(false),
    [ready, setReady] = useState(false),
    [error, setError] = useState("");
  const container = useRef<HTMLDivElement | null>(null);
  const pending = useRef<{
    resolve: (token: string) => void;
    reject: (error: Error) => void;
  } | null>(null);
  useEffect(() => {
    if (!sitekey) return;
    setProofProvider(
      () =>
        new Promise<string>((resolve, reject) => {
          pending.current = { resolve, reject };
          setError("");
          setOpen(true);
        }),
    );
    return () => {
      setProofProvider(null);
      pending.current?.reject(
        new Error("Visitor verification was interrupted. Retry explicitly."),
      );
      pending.current = null;
    };
  }, [sitekey]);
  useEffect(() => {
    if (!open || !ready || !container.current || !window.turnstile || !sitekey)
      return;
    const id = window.turnstile.render(container.current, {
      sitekey,
      action: "trace-session",
      theme: "auto",
      size: "flexible",
      callback: (token: string) => {
        pending.current?.resolve(token);
        pending.current = null;
        setOpen(false);
      },
      "error-callback": () =>
        setError("Verification failed. Close this panel and retry explicitly."),
      "expired-callback": () =>
        setError(
          "Verification expired. Close this panel and retry explicitly.",
        ),
    });
    const timer = window.setTimeout(() => {
      pending.current?.reject(
        new Error("Visitor verification timed out. Retry explicitly."),
      );
      pending.current = null;
      setOpen(false);
    }, 120000);
    return () => {
      window.clearTimeout(timer);
      window.turnstile?.remove(id);
    };
  }, [open, ready, sitekey]);
  if (!sitekey) return null;
  return (
    <>
      {open && (
        <Script
          src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit"
          onReady={() => setReady(true)}
          onError={() =>
            setError(
              "Verification could not load. Check your connection and retry explicitly.",
            )
          }
        />
      )}
      <Sheet
        open={open}
        onOpenChange={(next) => {
          if (!next) {
            pending.current?.reject(
              new Error("Verification was closed. Retry explicitly."),
            );
            pending.current = null;
          }
          setOpen(next);
        }}
        title="Verify visitor"
        description="A quick verification protects the shared free allowance. No account or API key is needed."
      >
        <div className="settings-body">
          <div ref={container} />
          <p role="status">
            {error ||
              (ready
                ? "Complete the verification to continue your request."
                : "Loading verification…")}
          </p>
        </div>
      </Sheet>
    </>
  );
}
