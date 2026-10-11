"use client";
import Link from "next/link";
import { Settings2, ExternalLink, ArrowUpRight } from "lucide-react";
import { Wordmark, ExternalLink as OutLink } from "./ui";
import { ToolIcon } from "./tool-visuals";
import { tools, groups, github, type Tool } from "../lib/tools";
export function WorkspaceNavigation({
  tool,
  collapsed,
  mobile,
  setSettings,
  onNavigate,
}: {
  tool: Tool;
  collapsed: boolean;
  mobile: boolean;
  setSettings: (v: boolean) => void;
  onNavigate: () => void;
}) {
  return (
    <>
      <Link href="/" className="rail-brand" aria-label="TRACE home">
        <Wordmark compact={collapsed && !mobile} />
        {!collapsed && (
          <span className="brand-subtitle">A project by Archit</span>
        )}
      </Link>
      <div className="nav-tools">
        {groups.map((group) => (
          <div className="nav-group" key={group}>
            <span className="nav-group-label mono">
              {collapsed ? group.slice(0, 1) : group}
            </span>
            {tools
              .filter((t) => t.group === group)
              .map((t) => (
                <Link
                  href={`/workspace/${t.id}`}
                  key={t.id}
                  onClick={onNavigate}
                  className={`nav-tool ${t.id === tool.id ? "selected" : ""}`}
                  aria-current={t.id === tool.id ? "page" : undefined}
                  title={t.name}
                  aria-label={t.name}
                >
                  <ToolIcon name={t.icon} />
                  {!collapsed && <span>{t.name}</span>}
                  {t.id === tool.id && !collapsed && (
                    <span className="nav-active-dot" />
                  )}
                </Link>
              ))}
          </div>
        ))}
      </div>
      <div className="rail-footer">
        <button
          onClick={() => setSettings(true)}
          className="nav-tool"
          title="Settings"
        >
          <Settings2 size={17} />
          {!collapsed && <span>Settings</span>}
        </button>
        {!collapsed && (
          <>
            <a href={github} target="_blank" rel="noreferrer">
              Built by Archit Kumar <ArrowUpRight size={13} />
            </a>
            <span className="mono">Personal AI collection</span>
          </>
        )}
      </div>
    </>
  );
}
