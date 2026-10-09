import type { Event } from "./types";
export type Mode = "free" | "local" | "openai";
let proofProvider: (() => Promise<string>) | null = null;
export function setProofProvider(provider: (() => Promise<string>) | null) {
  proofProvider = provider;
}
export async function usage() {
  if (!token) return null;
  const response = await request(`${base}/api/v1/sessions/current/usage`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw await responseError(response);
  return (await response.json()) as {
    remaining: Record<string, number>;
    reset_at: number;
  };
}
const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
async function request(url: string, init?: RequestInit) {
  try {
    return await fetch(url, init);
  } catch {
    throw new Error(
      "The backend is unavailable or the connection was interrupted. Check the connection, then retry explicitly.",
    );
  }
}
let token = "";
let sessionPromise: Promise<void> | null = null;
async function session() {
  if (token) return;
  if (!sessionPromise)
    sessionPromise = (async () => {
      const response = await request(`${base}/api/v1/sessions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          turnstile_token: proofProvider ? await proofProvider() : "",
        }),
      });
      if (!response.ok) throw await responseError(response);
      token = (await response.json()).token;
    })().finally(() => {
      sessionPromise = null;
    });
  await sessionPromise;
}
async function responseError(response: Response) {
  let detail: unknown;
  try {
    detail = (await response.json()).detail;
  } catch {
    detail = "";
  }
  if (response.status === 401) token = "";
  return Object.assign(
    new Error(
      typeof detail === "string"
        ? detail
        : `Request failed (${response.status}). Check your inputs and retry explicitly.`,
    ),
    { reprocess: response.status === 401 || response.status === 404 },
  );
}
export async function stream(
  path: string,
  body: unknown,
  key: string,
  onEvent: (event: Event) => void,
  mode?: Mode,
) {
  await session();
  const response = await request(`${base}/api/v1${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(mode !== "free" && mode !== "local" && key
        ? { "X-OpenAI-Key": key }
        : {}),
      ...(mode ? { "X-Trace-Mode": mode } : {}),
    },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw await responseError(response);
  if (!response.body)
    throw new Error("The backend did not return workflow events.");
  await consume(response.body, (event) => {
    if (
      event.event === "error" &&
      (event.data as { code?: string }).code === "session_expired"
    )
      token = "";
    onEvent(event);
  });
}
export async function consume(
  body: ReadableStream<Uint8Array>,
  onEvent: (event: Event) => void,
) {
  const reader = body.getReader(),
    decoder = new TextDecoder();
  let pending = "",
    terminal = false;
  try {
    while (true) {
      const { value, done } = await reader.read();
      pending += decoder.decode(value, { stream: !done });
      pending = pending.replace(/\r\n/g, "\n");
      let boundary;
      while ((boundary = pending.indexOf("\n\n")) !== -1) {
        const block = pending.slice(0, boundary);
        pending = pending.slice(boundary + 2);
        const lines = block.split("\n");
        const event = lines
          .find((l) => l.startsWith("event:"))
          ?.slice(6)
          .trim();
        const data = lines
          .filter((l) => l.startsWith("data:"))
          .map((l) => l.slice(5).trimStart())
          .join("\n");
        if (event && data) {
          if (event === "result" || event === "error") terminal = true;
          onEvent({ event: event as Event["event"], data: JSON.parse(data) });
        }
      }
      if (done) break;
    }
    if (!terminal)
      throw new Error(
        "Connection interrupted. The request was not replayed. Review the completed stages, then retry explicitly.",
      );
  } finally {
    reader.releaseLock();
  }
}
export async function upload(file: File) {
  await session();
  const form = new FormData();
  form.append("file", file);
  const response = await request(`${base}/api/v1/uploads`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: form,
  });
  if (!response.ok) throw await responseError(response);
  return (await response.json()).file_id as string;
}
export async function media(id: string) {
  await session();
  const response = await request(`${base}/api/v1/artifacts/${id}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) throw await responseError(response);
  return URL.createObjectURL(await response.blob());
}
export async function clearSession() {
  if (token) {
    const response = await request(`${base}/api/v1/sessions/current`, {
      method: "DELETE",
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok && response.status !== 401)
      throw await responseError(response);
  }
  token = "";
}
