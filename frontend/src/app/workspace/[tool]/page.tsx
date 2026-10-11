import { notFound } from "next/navigation";
import { tools } from "../../../lib/tools";
import { Workspace } from "../../../components/workspace";
export async function generateMetadata({
  params,
}: {
  params: Promise<{ tool: string }>;
}) {
  const { tool } = await params;
  return { title: tools.find((t) => t.id === tool)?.name || "Workspace" };
}
export function generateStaticParams() {
  return tools.map((tool) => ({ tool: tool.id }));
}
export default async function ToolPage({
  params,
}: {
  params: Promise<{ tool: string }>;
}) {
  const { tool } = await params;
  const selected = tools.find((t) => t.id === tool);
  if (!selected) notFound();
  return <Workspace tool={selected} />;
}
