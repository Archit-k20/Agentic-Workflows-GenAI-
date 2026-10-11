"use client";
import { useId, type ReactNode } from "react";
export function ArtifactTabs({
  label,
  panelId,
  items,
  value,
  onChange,
}: {
  label: string;
  panelId?: string;
  items: { id: string; label: string }[];
  value: string;
  onChange: (id: string) => void;
}) {
  const uid = useId();
  return (
    <div className="artifact-tabs" role="tablist" aria-label={label}>
      {items.map((item, index) => (
        <button
          type="button"
          role="tab"
          key={item.id}
          id={`${uid}-${item.id}`}
          aria-selected={value === item.id}
          aria-controls={value === item.id ? panelId : undefined}
          tabIndex={value === item.id ? 0 : -1}
          onClick={() => onChange(item.id)}
          onKeyDown={(e) => {
            let next = index;
            if (e.key === "ArrowRight") next = (index + 1) % items.length;
            else if (e.key === "ArrowLeft")
              next = (index - 1 + items.length) % items.length;
            else if (e.key === "Home") next = 0;
            else if (e.key === "End") next = items.length - 1;
            else return;
            e.preventDefault();
            onChange(items[next].id);
            document.getElementById(`${uid}-${items[next].id}`)?.focus();
          }}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}
export function ArtifactPanel({
  id,
  label,
  children,
}: {
  label: string;
  children: ReactNode;
  id?: string;
}) {
  return (
    <div
      id={id}
      className="artifact-tab-panel"
      role="tabpanel"
      aria-label={label}
      tabIndex={0}
    >
      {children}
    </div>
  );
}
