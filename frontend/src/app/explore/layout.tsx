import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Explore the tools",
  description:
    "Try five interactive examples and explore all fifteen TRACE tools for research, documents, code, images, speech and content.",
};

export default function ExploreLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
