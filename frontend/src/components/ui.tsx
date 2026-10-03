"use client";
import { Button } from "./ui/button";
import * as Dialog from "@radix-ui/react-dialog";
import { X, ArrowUpRight, Copy, Check } from "lucide-react";
import { useState, type ReactNode } from "react";
export function Sheet({
  open,
  onOpenChange,
  title,
  description,
  children,
  className = "",
  onCloseAutoFocus,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  title: string;
  description: string;
  children: ReactNode;
  className?: string;
  onCloseAutoFocus?: React.ComponentProps<
    typeof Dialog.Content
  >["onCloseAutoFocus"];
}) {
  return (
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="sheet-overlay" />
        <Dialog.Content
          className={`sheet ${className}`}
          onCloseAutoFocus={onCloseAutoFocus}
        >
          <div className="sheet-heading">
            <div>
              <Dialog.Title>{title}</Dialog.Title>
              <Dialog.Description>{description}</Dialog.Description>
            </div>
            <Dialog.Close className="icon-button" aria-label="Close">
              <X size={20} />
            </Dialog.Close>
          </div>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
export function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false),
    [failed, setFailed] = useState(false);
  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      setFailed(true);
    }
  }
  return (
    <>
      <Button
        variant="outline"
        size="sm"
        className="copy-button"
        onClick={copy}
        aria-label="Copy output"
      >
        {copied ? <Check size={15} /> : <Copy size={15} />}{" "}
        {copied ? "Copied" : "Copy"}
      </Button>
      {failed && <span role="status">Select the text to copy manually.</span>}
    </>
  );
}
export function ExternalLink({
  href,
  children,
}: {
  href: string;
  children: ReactNode;
}) {
  return (
    <a href={href} target="_blank" rel="noreferrer">
      {children}
      <ArrowUpRight size={13} />
    </a>
  );
}
export function Wordmark({ compact = false }: { compact?: boolean }) {
  return (
    <span className="wordmark">
      <svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true">
        <path
          d="M4 7h24M16 7v18M5 18h7M20 18h7"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
        />
        <circle
          cx="16"
          cy="7"
          r="3"
          fill="var(--bg)"
          stroke="currentColor"
          strokeWidth="1.8"
        />
        <circle cx="5" cy="18" r="2" fill="currentColor" />
        <circle cx="27" cy="18" r="2" fill="currentColor" />
        <path
          d="m12 25 4 4 4-4"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
        />
      </svg>
      {!compact && (
        <span>
          TRACE<span className="brand-dot">.</span>
        </span>
      )}
    </span>
  );
}
