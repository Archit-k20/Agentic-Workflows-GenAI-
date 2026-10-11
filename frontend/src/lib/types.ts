import type { components, operations } from "./api-types";
export type Result =
  | components["schemas"]["TextResult"]
  | components["schemas"]["ArtifactResult"]
  | components["schemas"]["CodeResult"]
  | components["schemas"]["ResearchResult"]
  | components["schemas"]["ContentResult"]
  | components["schemas"]["DocumentResult"]
  | components["schemas"]["QAResult"]
  | components["schemas"]["SupportResult"];
export type RunInput =
  operations["run_api_v1_runs_post"]["requestBody"]["content"]["application/json"];
export type Source = components["schemas"]["Source"];
export type ContextResult = components["schemas"]["ContextResult"];
export type Stage = {
  name: string;
  status: "running" | "completed" | "failed";
};
export type Event = {
  event: "started" | "stage" | "warning" | "result" | "error";
  data: unknown;
};
