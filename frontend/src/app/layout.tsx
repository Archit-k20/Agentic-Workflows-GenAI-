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
    <html lang="en" data-theme="light" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html:
              "try{const theme=localStorage.getItem('trace-theme');if(theme==='light'||theme==='dark')document.documentElement.dataset.theme=theme;}catch{}",
          }}
        />
        <link
          rel="preload"
          href="/fonts/manrope-latin-400-normal.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <link
          rel="preload"
          href="/fonts/manrope-latin-600-normal.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
        <link
          rel="preload"
          href="/fonts/newsreader-latin-400-normal.woff2"
          as="font"
          type="font/woff2"
          crossOrigin="anonymous"
        />
      </head>
      <body>
        <a href="#main" className="skip-link">
          Skip to content
        </a>
        <Provider>{children}</Provider>
      </body>
    </html>
  );
}
