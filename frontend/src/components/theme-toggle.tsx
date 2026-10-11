"use client";
import { Moon, Sun } from "lucide-react";
import { useWorkspace } from "./provider";

export function ThemeToggle() {
  const { theme, toggleTheme } = useWorkspace();
  return (
    <button
      className="icon-button"
      onClick={toggleTheme}
      aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} theme`}
    >
      {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </button>
  );
}
