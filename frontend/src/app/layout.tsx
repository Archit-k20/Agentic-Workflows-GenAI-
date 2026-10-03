import type { Metadata } from "next";
import { Provider } from "../components/provider";
import "./globals.css";
export const metadata: Metadata = {
  title: { default: "TRACE — Agentic AI Workspace", template: "%s · TRACE" },
  description:
    "Fifteen focused AI tools. Trace an idea from input to evidence to a clear result. Built by Archit Kumar.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" data-theme="dark" suppressHydrationWarning>
      <body>
        <a href="#main" className="skip-link">
          Skip to content
        </a>
        <Provider>{children}</Provider>
      </body>
    </html>
  );
}
