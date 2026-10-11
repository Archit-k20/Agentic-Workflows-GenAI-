# Evaluation evidence

This directory contains **dated, immutable observations**, including failed runs. It is not a second setup guide and does not describe the current UI. Use the [verification summary](../verification.md), [interface guide](../interface.md) and [current screenshots](../screenshots/README.md) for those purposes.

Earlier interface images have been removed. A screenshot path inside an old JSON record is historical capture metadata, not a current documentation link. Raw model results, fingerprints, measured timings and failures remain intact so quality claims can be audited.

## Latest quality evidence

**Full current-profile quality acceptance remains incomplete.** Successful transport, valid JSON, expected-fact presence and a model's own review are not equivalent to factual accuracy. Syntax checks are not correctness or security proofs.

| Evidence | Meaning |
| --- | --- |
| [Release source review, 11 October](release-review-2026-10-11.json) | Source-based findings, inference fingerprints and unresolved acceptance gates |
| [Hosted final targets](hosted-final-targets-2026-10-11.json) and [metrics](hosted-final-targets-2026-10-11.metrics.json) | 9/20 cases completed; provider capacity blocked completion. Includes actual code checks, summaries and policy-conflict handling |
| [Local final targets](local-final-targets-2026-10-11.json) and [metrics](local-final-targets-2026-10-11.metrics.json) | One long CPU content run retained material facts but invented owner confirmation and repeated wording; not a quality pass |
| [Earlier release batch](hosted-release-2026-10-11.json) and [metrics](hosted-release-2026-10-11.metrics.json) | Earlier fingerprint; useful evidence of failures, not a substitute for final-profile results |
| [9 October source review](launch-review-2026-10-09.json) and [VM review](vm-local-launch-review-2026-10-09.json) | Prior hosted/local defects and targeted improvements; current code must be assessed separately |

All benchmark fixtures use synthetic English source text. Inference is real, but fixture URLs can be supplied locally by the harness; these runs do not prove live URL extraction. The inference fingerprint and fixture hashes establish which code/model profile each result describes. Null rubric-review fields mean unreviewed, not passed.

## Public integration and media

| Evidence | Scope |
| --- | --- |
| [Final public wiring](public-wiring-final-2026-10-11.json) | API configuration/security checks without inference |
| [Complex image](public-complex-image-2026-10-11.json), [exact prompt](complex-image-prompt-2026-10-11.txt) | Real Cloudflare output and honest visual rubric: composition worked; exact counts, hands and clock details had failures |
| [Code](public-code-2026-10-11.json) | Real Python generation and individual checks |
| [Contexts and questions](public-contexts-2026-10-11.json) | Real DOCX/URL indexing, cited answers, local-fallback disclosure and ownership checks |
| [YouTube recovery](public-youtube-fixed-2026-10-11.json) | Readable extraction failure and pasted-transcript recovery |
| [Public runtime](public-runtime-2026-10-09.json) | Earlier speech, browser entry and fallback checks |
| [HF transport](hf-transport-2026-10-09.json) | Actual Gradio REST/queue behavior with a synthetic image, no GPU |
| [HF generation](hf-live-2026-10-09.json) | One pinned FLUX generation; visual inspection found a malformed handle |
| [HF VM integration](hf-production-2026-10-09.json) | Actual generation, workflow events, artifact ownership and clearing in a separate diagnostic process; production quotas were not reset |
| [Fixed cold concurrency](vm-concurrency-fixed-2026-10-11.json) | Two admitted CPU summaries complete; third request rejected as busy |
| [VM memory samples](vm-resource-samples-2026-10-11.json) | Observations during selected work, not continuous peak-load measurements |

## Current studio verification

These records describe frontend checks and consume no shared AI quota:

- [All-tool width/theme matrix](studio-layout-matrix.json).
- [Intro widths/themes](studio-intro-layout.json) and [motion checks](studio-intro-motion.json).
- [Offline samples](studio-preview-samples.json) and [preview CORS](studio-preview-cors.json).
- [Rendered contrast samples](studio-contrast.json).
- [Build comparison](studio-build-comparison.json) and [local performance conditions](studio-local-performance.json).

Preview hostnames in raw records identify where a test was performed. The project README contains the one current visitor link.

## Earlier evidence retained for reproducibility

The `hosted-70b-final*`, `hosted-grounded`, `hosted-qwen-metrics`, `local-staged*`, `source-checks-review` and boundary-run files document previous profiles. Complete earlier 60-case runs exposed grounding errors even when schema and fact-presence metrics were strong. In particular, some marketing copy invented facts, research revisions dropped required citations, and support boundaries were misinterpreted. Subsequent changes must be judged against fresh evidence; those historical results remain unchanged.

`cloudflare-capacity-check.json` and `dashboard-quota-recheck.json` record a provider-enforcement/dashboard mismatch. They do not prove that the account had consumed the allowance shown by the API error. Application reservation estimates are not provider billing measurements.

## Further evaluation

Run intentionally with the existing shared allowance; do not enable paid overflow or reset ledgers to complete a benchmark. A hosted run that falls back locally cannot count as hosted-only evidence. Use new output files after model, fixture or inference-code changes. Explicit resume is appropriate only for an unchanged profile and a deliberate retry decision.

See [evaluation commands and acceptance rules](../free-access.md#quality-evaluation). Inspect sources and output usefulness in addition to automatic screening. No paid OpenAI live acceptance or universal factual-quality claim is made.
