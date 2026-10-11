# TRACE quiet studio redesign

Implementation branch: `codex/trace-quiet-studio`. Review base: `codex/trace-react-workspace` at `335c031`. This is a frontend release candidate. Production promotion is intentionally a separate step after the owner reviews the preview.

## Review preview

[Open the Vercel preview](https://trace-agentic-workspace-38qyyey35.vercel.app/). Deployment `dpl_5taeqJ9mnwSRvoewbs4sLs6Bfotw` built successfully from frontend commit `20ef258`. Production has not been promoted.

All five public preview sample routes were checked, with the sample label and result visible and no Turnstile frame mounted. [Preview sample record](evaluation/studio-preview-samples.json). Live execution from this new origin is intentionally not claimed: a non-generating CORS preflight returned **400, Disallowed CORS origin**. [Preflight record](evaluation/studio-preview-cors.json). For live preview testing, add this exact hostname to the existing Turnstile widget and this exact HTTPS origin to `TRACE_ALLOWED_ORIGINS`; preserve the production origin and all verification controls. This is unnecessary for offline sample review. Promotion to the existing production hostname uses its existing allowlisting.

## Introductory entrance

The owner requested a calmer entrance before the tool collection. `/` now provides original atmospheric CSS/SVG folds, a short introduction, native scroll-to-synopsis navigation and an **Explore TRACE** button. `/explore` retains the complete interactive collection. A header shortcut lets returning visitors enter directly. Light and dark themes share the existing preference, and the root provider keeps live drafts intact across both routes. The button changes its arrow and outline on hover/focus; reduced motion removes the transformation. No artwork from Atmos was reused.

The new entrance has no sample renderer, execution controller, session creation or verification component. The existing studio, tool routes, models and generation behavior remain intact. Collection anchors now live at `/explore#tools` and `/explore#about`; the workspace breadcrumb points to the collection, while the TRACE wordmark returns to the introduction.

The entrance was checked at 360, 768, 1024, 1440 and 1920 px in both themes: no horizontal overflow and the primary invitation remained visible. Keyboard activation reaches the synopsis, and both Explore links open the collection. A Research draft survived a round trip through the introduction and collection, including browser Back. The existing 28 frontend tests and production build passed. These checks used no generation requests. [Responsive record](evaluation/studio-intro-layout.json).

Screenshots: [Pearl entrance](screenshots/studio-intro-pearl.jpg), [Ink entrance](screenshots/studio-intro-ink.jpg), [Phone entrance](screenshots/studio-intro-mobile.jpg), [Synopsis](screenshots/studio-intro-story.jpg).

## What changed

| Before | Now |
| --- | --- |
| Large editorial headline and illustrative hero | Atmospheric entrance followed by a collection with a usable Research example |
| Five samples opened from the workspace and replaced the live draft | Five collection examples plus isolated read-only workspace samples; live work survives navigation |
| Warm paper/vermilion styling with accumulated overrides | One pearl/ink token system, restrained ink blue, smaller interface headings and solid reading surfaces |
| Tool discovery mainly through navigation | Searchable/filterable collection with grid/list views and direct links to all fifteen tools |
| One large workspace component | Shared execution controller plus separate navigation, inputs, settings and result surfaces |
| Long stacks of content/document artifacts | Keyboard-operable artifact tabs and a document selector, with complete data still in Details |
| Fixed image preview | Accessible expansion dialog with fit and actual-size views |
| Tool workflow descriptions | Purpose, an implemented choice and a limitation in Behind this tool |
| Inputs always occupy space | Focus on result collapses inputs without discarding them |

All original workspace URLs, group names, inputs, limits, generated API types, providers, mode semantics, quotas, fallback rules, request transport, ownership checks and hosting remain unchanged. No backend files or production dependencies changed. The three added dependencies are test-only: Testing Library React/DOM and jsdom.

The collection Research excerpt is intentionally shorter than the full workspace report. At 360×800 px, its first citation is fully visible at approximately y=766–794, allowing immediate source inspection.

## Reference use

[Atmos Gallery](https://atmos.gallery/) informed spacing and restrained surfaces; [Creative Reference Library](https://crl-2026.webflow.io/library) informed the curated collection; [PinReply](https://pinreply.com/welcome/#practice) informed teaching through an immediately usable example. TRACE's CSS/SVG details, social artwork and implementation are original. No reference artwork was copied.

## State and interaction rules

- Every sample says **Sample result — no live AI request**. Sample views have no run/upload/media-fetch action. Research citations, document sections, code checks, content tabs and support evidence remain interactive locally.
- Sample navigation never creates a file ID, changes selected files, replaces live inputs/results/context or replays a request. An active run continues and updates its original draft even while a sample or another tool is visible.
- The three execution modes and Q&A reprocessing behavior remain intact. Settings cannot change mode or clear a session while a run is active. Advanced keys stay isolated from free/local requests.
- Stage capsules show received events and actual elapsed time, not percentages. The workflow outline is labelled separately from observed stages.
- Evidence overlays trap focus and restore it to their citation. Markdown renderers retain stable citation nodes when an inspector opens. A narrow screen gets a bottom sheet, intermediate widths a side sheet, and wide screens an inline inspector.
- Content narration failures and document/source errors remain visible with useful results. Interrupted requests preserve inputs and require an explicit retry.
- Images use authenticated object URLs and explicit expansion; audio never autoplays. No new export, permanent history, cancellation or AI capability was added.

## Verification performed

| Check | Evidence / outcome |
| --- | --- |
| Existing and new frontend tests | 28 passing tests: all-tool request construction, stream interruption, key isolation, five offline samples, draft/file/context/run isolation, tab interaction, document failures, repair/unavailable checks, citation node identity and Q&A invalidation |
| TypeScript | `npm run typecheck` passes |
| Production build | `npm run build` passes; all fifteen tool paths generated |
| Responsive forms | 150 production-browser cases: 15 tools × 5 widths (360/768/1024/1440/1920) × both themes; no horizontal page overflow; [record](evaluation/studio-layout-matrix.json) |
| Collection samples | All five exercised through their real controls; source inspection, document risks/actions, content captions/prompts and support escalation displayed. The local API request log stayed empty during this pass |
| Live controller in browser | Synthetic research partial success completed after sample navigation; inputs preserved; mode changes disabled during processing; focus mode reversible |
| Q&A | Synthetic URL preparation, question and source-backed answer; changing mode disables answering until reprocessed |
| Failure states | Interrupted request retained input and explicit retry; expired image produced a readable error. Unit fixtures cover document partial failures. Browser fixtures show passed, unavailable and failed compilation checks, initial/final repair comparison and horizontally scrolling wide code without page overflow |
| Media | Synthetic image opened at fit and actual size without page overflow; focus returned to trigger. Local audio fixture played only after clicking Play |
| Navigation | Tool search, collection list view, mobile sheet including selecting current tool, sample return links and keyboard artifact tabs exercised. `/workspace` redirects to Research; an invalid tool renders the existing 404 |
| Focus | Desktop citation and mobile evidence-sheet close/Escape restored the originating citation |
| Contrast | Actual collection text computed against rendered surfaces: 149 text elements per theme, no failures; minimum 5.45:1 light / 7.18:1 dark. This is a focused contrast audit, not full accessibility certification; [record](evaluation/studio-contrast.json) |
| Dependency/contract scope | Production dependency versions, request builder, generated types, provider state, API transport and backend code unchanged |

Tests use mocks and the optional local fixture server. No paid or shared-quota inference was used to verify this redesign. Sample data remains synthetic; mock execution does not establish model quality.

### Performance

The measurements below describe the initial studio collection, now at `/explore`. They are not measurements of the new introductory route.

Local production builds were compared in the Codex WebKit browser at 1440 and 360 px, without CPU/network throttling. Three runs per width/version, each observed for 1.5 seconds. The collection (then at `/`) measured LCP **0.268–0.508 seconds** and CLS **0.0039–0.0526**. These pass the stated local targets under these conditions; they are not field measurements or evidence for slow mobile connections. INP requires additional real usage data. [Raw measurements](evaluation/studio-local-performance.json).

The interactive collection loads the existing Markdown/report rendering code. Its initial compressed JavaScript grew from **219,747 to 316,780 bytes**. The workspace entry shrank from **321,192 to 279,226 bytes** because results are loaded when needed. Shared compressed CSS shrank from **11,582 to 10,029 bytes**. These counts are unique assets referenced by generated route HTML, excluding later-loaded chunks and fonts; gzip sizes are calculated consistently, not network waterfall totals. [Build comparison](evaluation/studio-build-comparison.json).

### Manual checks still needed before production promotion

- Review the preview's visual direction and interactions.
- Independently check real mobile file picking, a PDF Q&A flow and audio playback. This was already outstanding for the live release; the redesign's file/draft behavior has regression coverage, but the in-app browser's file-chooser event did not resolve during the manual long-filename attempt.
- Test 200% browser zoom and the OS reduced-motion preference in a regular browser. The available browser control exposes viewport resizing but not zoom/media emulation. CSS disables transitions/animation and spatial Motion effects honor reduced motion, but a complete OS-level pass is not claimed.
- The preview origin must be specifically allowed by both backend CORS and the existing Turnstile widget before testing live requests from that hostname. Never use wildcard allowlists or disable verification. Local integration checks use synthetic responses; production smoke checks follow promotion.

Existing inference-quality and independent-network limitations in [the live verification record](launch-2026-10-11.md) are not resolved by a visual redesign.

## Reproduce without AI usage

```sh
cd frontend
npm ci
npm run typecheck
npm test
node test-fixtures/mock-api.mjs
```

In a second terminal:

```sh
cd frontend
NEXT_PUBLIC_API_URL=http://127.0.0.1:8811 NEXT_PUBLIC_TURNSTILE_SITE_KEY='' npm run dev -- --port 3100
```

Only use that public-key override for the **local synthetic backend**. It never contacts the real API. The fixture server binds to loopback and is not imported by production code. `[slow]`, `[partial]`, `[interrupt]`, `[error]`, `[expired]` and `[repair]` in relevant text fields select diagnostic responses. It logs method/path/tool/mode only. Do not enter real credentials or private files while testing.

## Screenshots and sharing

- [Pearl collection](screenshots/studio-home-pearl.jpg)
- [Ink collection](screenshots/studio-home-ink.jpg)
- [Phone collection](screenshots/studio-home-mobile.jpg)
- [Research workspace](screenshots/studio-research-desktop.jpg)
- [Mobile evidence sheet](screenshots/studio-evidence-mobile.jpg)

`frontend/public/studio-social.svg` is the editable original artwork; `studio-social.png` is the static 1200×630 sharing image referenced by metadata. It depicts the real sample interface and identifies Archit's AI project.

## Release procedure

1. Review the focused PR against the migration branch and its Vercel preview.
2. Finish the manual checks above. A preview hostname needs its own exact allowlisting for live traffic; samples work without it.
3. Promote only after the owner approves the preview. Keep the previous Vercel production deployment available for rollback.
4. Smoke-test the public homepage, direct routes, all five sample links, settings, mode handling and authenticated image/audio behavior. Do not interpret mock test results as successful live inference.
5. If a regression appears, restore the previous Vercel deployment, retain the branch and diagnose against the saved evidence.
