# Verification and release status

This is the current verification summary for TRACE. The [interface guide](interface.md) and [dark screenshots](screenshots/README.md) describe the current studio. The [evaluation index](evaluation/README.md) preserves dated raw results and failures; older model runs are not relabeled as current passes.

## Repository cleanup — 11 October 2026

- Removed the retired application entry points, duplicate tool UI modules, obsolete dependency/setup files and unused logo.
- Replaced overlapping migration/launch guides with current architecture, tool contracts, interface, deployment and verification guides.
- Removed earlier interface screenshots. Four current dark screenshots are the documentation's visual reference.
- Kept one visitor website link in the root README. Preview deployments are release artifacts, not alternate visitor destinations.
- Preserved the shared Python workflow functions, prompts, advanced mode, free providers, quotas and backend contracts.
- Rebuilt the backend container and ran **266 passing tests**, including parity, parsers, indexing, isolation, safeguards and compiler checks. Deprecation warnings remain in third-party libraries.

The cleanup also passed a clean Node.js 24 Linux dependency install, 28 frontend tests, TypeScript checks and a production build. The lockfile now contains missing optional native bindings, with no changes to the versions of existing dependencies. No model requests were made for this documentation/interface release.

## Current production release

Frontend source `69e8f70` was built and released as `dpl_96nEWCpzmxcGvpriNws9Cmdi8Pep`. The permanent visitor address now opens the current introduction and studio. The previous Vercel production deployment, `dpl_F5FMTnrKFjsTapNzd2UroSWL6stA`, remains available for rollback. This cleanup does not change the running backend's behavior or configuration.

Post-release inspection at 1440×940 in dark mode confirmed the introduction, collection, all fifteen direct tool routes, five fully loaded examples, settings/provider descriptions and explicit bundled voice-preview playback. No tool form overflowed horizontally at that viewport. All 18 public API wiring checks passed. This is a scoped release smoke check, not a new model benchmark or repetition of the earlier full responsive matrix. [Release evidence](evaluation/studio-production-release.json).

## Interface verification

The studio implementation has 28 frontend regression tests covering typed requests, event handling, routing/presentation, sample isolation and live draft protection. The recorded browser matrix covers all 15 entry forms at 360, 768, 1024, 1440 and 1920 px in both themes. It found no page-level horizontal overflow. Five sample workflows remained visibly labeled and operated without a backend; examples did not make session, upload or generation requests.

Research citations and the mobile evidence sheet, command search, settings, content tabs, document switching, image expansion and failure fixtures have scoped browser checks. Intro records cover the moving background, pause control and seamless scroll treatment. These are development checks, not a complete accessibility audit or a guarantee for every browser.

Evidence: [layout matrix](evaluation/studio-layout-matrix.json), [intro layouts](evaluation/studio-intro-layout.json), [intro motion](evaluation/studio-intro-motion.json), [sample isolation](evaluation/studio-preview-samples.json), [contrast](evaluation/studio-contrast.json), [build comparison](evaluation/studio-build-comparison.json), [local performance conditions](evaluation/studio-local-performance.json).

## Backend and live integration evidence

| Area | Recorded outcome | Scope and limitation |
| --- | --- | --- |
| Automated backend | 266 tests passed in the cleanup container | Mocked providers alongside real parsers, storage, retrieval and installed language checks; not paid-provider live acceptance |
| Native runtime | CI builds/tests on AMD64 and ARM64, including CPU-only tensors, pinned retrieval/speech assets and local inference | Inspect the release's actual [GitHub checks](https://github.com/Archit-k20/Agentic-Workflows-GenAI-/actions); emulation cannot substitute for native isolation checks |
| Public API wiring | 18 checks recorded on 11 October | HTTPS/CORS/capabilities/missing-proof rejection; no AI generation in this check |
| Image generation | Public Cloudflare FLUX returned a 1024×1024 complex scene in about 21 seconds | Broad composition worked; exact object count, clock text and hand anatomy failed parts of the visual rubric |
| Code generation | Public Python result and real AST/bytecode checks passed | A few function assertions do not establish general software correctness or security |
| Document and article Q&A | Real DOCX/official-documentation inputs indexed and returned cited answers; session isolation checked | Some answers explicitly used CPU fallback; not a benchmark for arbitrary documents |
| YouTube recovery | Blocked transcript extraction gave readable guidance and accepted pasted transcript text | Availability of a particular public video remains outside TRACE's control |
| Speech | Public keyless speech generation and browser playback recorded | Independent physical-phone playback remains unconfirmed |
| HF image fallback | Two controlled real generations and VM artifact/session checks passed | Public-browser generation after forcing this fallback remains unverified; a Cloudflare success does not prove it |
| CPU concurrency | Two admitted cold summaries completed after the initialization fix; a third request received a busy response | About 94 and 125 seconds in that check; local text can take several minutes, and sampled memory is not a peak-load guarantee |

Detailed evidence: [public wiring](evaluation/public-wiring-final-2026-10-11.json), [image rubric](evaluation/public-complex-image-2026-10-11.json), [code](evaluation/public-code-2026-10-11.json), [Q&A](evaluation/public-contexts-2026-10-11.json), [transcript recovery](evaluation/public-youtube-fixed-2026-10-11.json), [public runtime](evaluation/public-runtime-2026-10-09.json), [HF verification](huggingface-images.md#recorded-live-verification), [cold concurrency](evaluation/vm-concurrency-fixed-2026-10-11.json), [memory samples](evaluation/vm-resource-samples-2026-10-11.json).

## Model quality is still a separate gate

The latest complete hosted benchmark is not accepted as a general quality pass. Earlier full runs surfaced unsupported content, misleading reviews, research citation loss and support decision errors despite high fact-presence scores. Subsequent guards and targeted checks improved specific cases, but the final hosted target suite stopped at provider capacity and the latest local content check still found an unsupported owner-confirmation claim.

The 11 October final hosted targets completed 9 of 20 cases; the remaining 11 failed or were blocked by capacity. Six code outputs passed available checks, two summaries and one policy-conflict case completed. These results cannot be combined with different inference fingerprints to claim a complete current-profile pass. [Release review](evaluation/release-review-2026-10-11.json), [hosted targets](evaluation/hosted-final-targets-2026-10-11.json), [local targets](evaluation/local-final-targets-2026-10-11.json).

Remaining checks:

- Deliberate final-profile hosted and CPU evaluation, including source-based review and varied real documents. Do not equate expected-fact presence with factual accuracy.
- Independent phone/network upload, question and audio playback check; the owner has not yet reported the result.
- Public-browser HF fallback generation with available quota, and controlled advanced OpenAI checks if a test key is explicitly supplied.
- Full keyboard/zoom/reduced-motion audit and representative field performance. Local layout checks do not certify field LCP, CLS or INP.

## Reproduce checks

From the repository root:

```sh
npm ci --prefix frontend
npm --prefix frontend run typecheck
npm --prefix frontend test
npm --prefix frontend run build
docker build -f backend/Dockerfile -t trace-backend:test .
docker run --rm -e TRACE_REQUIRE_COMPILER_ISOLATION=1 trace-backend:test \
  python -m pytest backend/tests -q -p no:cacheprovider
```

Compiler checks require a native Linux kernel with supported Landlock isolation. The API reports checks as unavailable instead of disabling isolation when the kernel cannot provide it. This can occur with AMD64 emulation on an ARM Mac.

Model evaluations consume shared provider capacity and must be run intentionally. See [free access](free-access.md#quality-evaluation) for commands and evaluation rules. Keep original output files and fingerprints; use a fresh filename after inference changes.
