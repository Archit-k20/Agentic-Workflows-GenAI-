# TRACE interface

TRACE uses a pearl-and-ink visual system with a personal-project introduction and a practical workspace. The website link is in the [README](../README.md). All screenshots here show the current design in dark mode.

## Routes and interaction

| Route | Purpose |
| --- | --- |
| `/` | Short introduction, moving SVG atmosphere, glass navigation and native scroll to a synopsis. Explore TRACE enters the collection. |
| `/explore` | Five interactive examples, all fifteen tools, search, group filters, grid/list controls and project context. |
| `/workspace` | Opens Research Agent. |
| `/workspace/[tool]` | Direct tool entry, inputs, observable execution stages, results and settings. |
| `?sample=1` | Read-only synthetic sample for Research, Documents, Code, Content or Support. |

The introductory background moves continuously through the page. A visible pause/resume control and device reduced-motion preferences stop motion. The glass treatment is limited to the masthead, with a more opaque fallback for unsupported filters or reduced-transparency preferences. Reading/input surfaces remain solid.

Manrope is used for the interface, Newsreader selectively for reports, and IBM Plex Mono for code/metadata. Fonts are self-hosted. Themes share a single token system. Original CSS/SVG artwork supplies the atmosphere; no 3D engine or additional animation library is used.

## Workspace behavior

Navigation groups remain Summarizer, Generator and Assistant. Tool search is available through a visible command trigger and Cmd/Ctrl+K. Settings explains Free, Local and Advanced modes; local inference means the project's server. Active-run restrictions and Q&A context invalidation remain enforced.

Inputs and results are separate panels. Focus on result collapses the input without discarding it. Behind this tool explains its purpose, an implemented choice and a limitation. Raw structured results remain in Details. Citation activation pins returned source metadata; keyboard focus and touch are supported. Content artifacts use tabs, documents have a selector, images have an accessible fit/actual-size dialog, and media playback is explicit.

Below 768 px, navigation is a sheet and evidence uses a bottom sheet. Intermediate layouts use stacked/compact work areas and an evidence side sheet. Large screens can show input, result and pinned evidence together. Wide code/tables scroll within their own containers.

## Sample isolation

Each example says **Sample result — no live AI request**. It does not initialize an anonymous session, upload a file, request Turnstile verification or run AI. Example data and live drafts are separate. Navigating to a sample during execution does not cancel, restart or replace the live run. Returning restores its inputs/result; theme is the only preference persisted across browser sessions.

## Current screenshots

| View | Image |
| --- | --- |
| Introduction and glass navigation | [Dark introduction](screenshots/readme/intro-dark.jpg) |
| Collection with source preview | [Dark collection](screenshots/readme/collection-dark.jpg) |
| Report and evidence inspector | [Dark Research workspace](screenshots/readme/research-dark.jpg) |
| Code and individual checks | [Dark Code workspace](screenshots/readme/code-dark.jpg) |

The result screens are synthetic fixtures, not proof of model performance. The screenshot set has no images from superseded interfaces. [Screenshot provenance](screenshots/README.md).

## Verification and development

[Verification](verification.md) separates current release checks, earlier measured evidence and remaining manual/model-quality gates. Relevant regression coverage includes sample isolation, active-run continuity, Q&A mode changes, partial failures, artifact tabs, citations and request construction.

For local synthetic-response testing, run `node frontend/test-fixtures/mock-api.mjs`, then start the frontend with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8811` and an empty public Turnstile site key. This override is for the local fixture server only; public deployments retain verification and exact origin allowlists. No live quota is needed for interface tests.

`frontend/public/studio-social.svg` is the original editable sharing artwork; its matching PNG is used by page metadata. It is a static illustration of the current introduction, not a generated workflow result.
