/** Local-only UI fixtures. Never contacts an AI provider. No production imports. */
import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import ts from "typescript";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
function fixture(id) {
  const src = readFileSync(
    resolve(root, `src/lib/samples/${id}.ts`),
    "utf8",
  ).replace(/import .*?;\n/g, "");
  const commonSource = {
    label: "S1",
    title: "Synthetic field notes",
    summary:
      "Appointments distribute demand. Specialist repairs need referral.",
    key_points: ["Fictional testing source."],
    text: "Appointments distribute demand.",
  };
  const js = ts.transpile(src, {
    module: ts.ModuleKind.CommonJS,
    target: ts.ScriptTarget.ES2022,
  });
  const exports = {};
  new Function("exports", "source", js)(exports, commonSource);
  return exports.default.result;
}
const fixtures = Object.fromEntries(
  ["research", "documents", "code", "content", "support"].map((id) => [
    id,
    fixture(id),
  ]),
);
let requests = [];
const server = createServer(async (req, res) => {
  res.setHeader(
    "Access-Control-Allow-Origin",
    req.headers.origin || "http://localhost:3100",
  );
  res.setHeader(
    "Access-Control-Allow-Headers",
    "Content-Type, Authorization, X-Trace-Mode, X-OpenAI-Key",
  );
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  if (req.method === "OPTIONS") {
    res.end();
    return;
  }
  if (req.url === "/requests") {
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(requests));
    return;
  }
  if (req.url === "/reset") {
    requests = [];
    res.end("reset");
    return;
  }
  let raw = "";
  for await (const chunk of req) raw += chunk;
  const body = req.headers["content-type"]?.includes("application/json")
    ? JSON.parse(raw || "{}")
    : {};
  requests.push({
    method: req.method,
    path: req.url,
    tool: body.tool,
    mode: req.headers["x-trace-mode"],
  });
  const json = (v) => {
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(v));
  };
  if (req.url === "/api/v1/sessions") {
    json({ token: "synthetic-ui-session" });
    return;
  }
  if (req.url === "/api/v1/uploads") {
    json({ file_id: "fixture-file" });
    return;
  }
  if (req.url === "/api/v1/sessions/current/usage") {
    json({
      remaining: { text: 10, image: 2, audio: 5, context: 3 },
      reset_at: 0,
    });
    return;
  }
  if (req.method === "DELETE") {
    json({ ok: true });
    return;
  }
  if (req.url?.startsWith("/api/v1/artifacts/")) {
    if (req.url.endsWith("expired")) {
      res.statusCode = 404;
      json({
        detail: "This temporary artifact expired. Generate again explicitly.",
      });
      return;
    }
    if (req.url.endsWith("audio")) {
      res.setHeader("Content-Type", "audio/mpeg");
      res.end(readFileSync(resolve(root, "public/audio/voices/af_heart.mp3")));
      return;
    }
    res.setHeader("Content-Type", "image/svg+xml");
    res.end(
      '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1100"><rect width="1600" height="1100" fill="#e9edf3"/><circle cx="800" cy="470" r="230" fill="#3559a8"/><text x="800" y="850" fill="#20252d" font-size="42" font-family="sans-serif" text-anchor="middle">Synthetic image fixture — no AI request</text></svg>',
    );
    return;
  }
  const tool = body.tool;
  const combined = Object.values(body).join(" ");
  res.setHeader("Content-Type", "text/event-stream");
  const event = (name, data) =>
    res.write(`event: ${name}\ndata: ${JSON.stringify(data)}\n\n`);
  event("started", {});
  event("stage", { name: "Inspect fixture inputs", status: "running" });
  const finish = () => {
    event("stage", { name: "Inspect fixture inputs", status: "completed" });
    if (combined.includes("[interrupt]")) {
      res.end();
      return;
    }
    if (combined.includes("[error]")) {
      event("error", {
        message:
          "Synthetic provider quota exhausted. Try again when capacity is available.",
        code: "provider_unavailable",
      });
      res.end();
      return;
    }
    if (combined.includes("[partial]"))
      event("warning", {
        message:
          "One source could not be read; successful sources are retained.",
      });
    let result;
    if (req.url?.includes("/contexts/") && !req.url.endsWith("/query"))
      result = {
        context_id: "fixture-context",
        kind: req.url.includes("documents") ? "document-qa" : "url-qa",
        errors: [],
        profile: { chunks: 3 },
      };
    else if (req.url?.endsWith("/query"))
      result = {
        tool: "document-qa",
        answer: "The repair pilot needs a specialist safety review [S1].",
        sources: [
          {
            label: "S1",
            title: "Synthetic planning brief",
            text: "The pilot needs a safety review before opening.",
            metadata: { source: "brief.txt", chunk: 1 },
          },
        ],
      };
    else if (tool === "image" || tool === "speech")
      result = {
        tool,
        artifact_id: combined.includes("[expired]")
          ? "expired"
          : tool === "speech"
            ? "audio"
            : "image",
        media_type: tool === "speech" ? "audio/mpeg" : "image/svg+xml",
      };
    else if (fixtures[tool]) {
      result = structuredClone(fixtures[tool]);
      if (tool === "research" && combined.includes("[long]"))
        result.final_report +=
          "\n\n" +
          (
            "## More context\n\n" +
            "A fictional follow-up observation remains uncertain [S1]. ".repeat(
              12,
            ) +
            "\n\n"
          ).repeat(20);
      if (tool === "code" && combined.includes("[long]"))
        result.final_code +=
          "\n# " + "Long code comment for horizontal scrolling. ".repeat(35);
      if (tool === "code" && combined.includes("[repair]")) {
        result.repair_attempted = true;
        result.initial_code = "def demo(\n";
        result.initial_verification = {
          language: "python",
          passed: false,
          checks: [
            {
              name: "Python syntax",
              passed: false,
              details: "SyntaxError: expected closing parenthesis",
            },
          ],
        };
        result.final_verification = {
          language: "python",
          passed: false,
          checks: [
            {
              name: "Python syntax",
              passed: true,
              details: "Parsed successfully",
            },
            {
              name: "Optional compiler",
              passed: false,
              details: "Compiler unavailable: not installed",
            },
          ],
        };
      }
      if (tool === "support" && combined.includes("[escalate]")) {
        result.final = {
          ...result.final,
          resolution_type: "escalate",
          answer:
            "Please contact a specialist. The available evidence does not settle this.",
          recommended_next_step: "Ask a specialist to review.",
        };
      }
      if (tool === "content")
        result.audio_error =
          "Synthetic narration failure. Written content is still available.";
    } else
      result = {
        tool,
        text: "A fictional campus repair pilot uses appointments and refers specialist repairs for qualified review.\n\nThis response is a UI fixture, not a live model output.",
      };
    event("result", result);
    res.end();
  };
  setTimeout(finish, combined.includes("[slow]") ? 8000 : 500);
});
server.listen(8811, "127.0.0.1", () =>
  console.log("Synthetic UI API on http://127.0.0.1:8811; no provider calls."),
);
