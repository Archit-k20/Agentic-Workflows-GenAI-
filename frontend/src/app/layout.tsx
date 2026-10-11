import type { Metadata } from "next";
import { Provider } from "../components/provider";
import "./globals.css";
export const metadata: Metadata = {
  title: {
    default: "TRACE — An AI project by Archit Kumar",
    template: "%s · TRACE",
  },
  description:
    "A collection of 15 AI tools by Archit Kumar. Explore interactive examples, try your own inputs and inspect the sources and checks behind each result.",
  metadataBase: new URL("https://trace-agentic-workspace.vercel.app"),
  openGraph: {
    title: "TRACE — An AI project by Archit Kumar",
    description:
      "Explore 15 AI tools, from research and documents to code and content.",
    images: [
      {
        url: "/studio-social.png",
        width: 1200,
        height: 630,
        alt: "TRACE: An AI project by Archit Kumar. Start with something on your mind.",
      },
    ],
  },
  twitter: { card: "summary_large_image", images: ["/studio-social.png"] },
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      data-theme="light"
      data-scroll-behavior="smooth"
      suppressHydrationWarning
    >
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
