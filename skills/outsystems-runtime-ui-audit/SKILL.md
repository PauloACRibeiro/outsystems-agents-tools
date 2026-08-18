---
name: outsystems-runtime-ui-audit
description: Audit a live runtime URL against the 16-criterion UI Quality Assessment rubric. Use when the user asks to "audit this runtime", "check the live app", "review the deployed screen", "score the running app's UI", or gives a runtime link and wants a UI quality assessment. Captures screenshots (desktop + mobile), a shallow in-app crawl, interaction states (focus ring, hover), and a mechanical probe (tap-target sizes, motion signals), then scores each criterion Market Leading→Broken with evidence and a weighted total + tier. Read-only — never modifies the app.
---

> ODC error codes: see `../shared/reference/odc-error-registry.md` for the canonical index of every code named below.

# Runtime UI Audit

> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `.claude/skills/runtime-ui-audit/SKILL.md` (harvested 2026-07-29, renamed on install).
> Upstream content adapted only where paths/names required; scoring rubric unchanged.


You're auditing a **live runtime** — a deployed app reached by URL — against the **UI Quality Assessment** rubric in [`rubric.md`](rubric.md) next to this file. Unlike the companion `outsystems-ui-review` skill (which greps the OML/theme to judge *how it was built*), this skill judges *what the user sees and experiences* from captures of the running app.

> **Full rubric (canonical):** [`rubric.md`](rubric.md). Read it before scoring — it defines the 16 criteria, tier boundaries, weights, and N/A rules. When a criterion's intent is ambiguous, that file wins.

## Read-only contract

This skill **never modifies** the app or the codebase. It navigates a URL, captures artifacts, and reports. No edits, no deploys, no "fixed it." If the user asks for fixes after the audit, that's a separate task.

## Not the same score as ODC Code Quality (Mentor)

This skill's **UI Quality** score is independent of OutSystems' own **ODC
Code Quality (Mentor)** tenant analysis (a different rubric, covering
Security/Performance/Maintainability/Architecture from the OML/theme, not
what a visitor sees at runtime). Don't conflate the two, and don't attribute
a Mentor code-quality number to this report or vice versa. This also isn't
the same "Mentor" as the [Mentor handoff](#mentor-handoff-compare-and-converge)
section below — that's Mentor as an editing agent; ODC Code Quality (Mentor)
is Mentor's separate tenant code-analysis feature.

If an audit is ever asked to cite or gather a tenant's Mentor code-quality
score alongside this rubric, these coverage facts apply — **measured
2026-07-27 by the OutSystems Solutions team; coverage is evolving, re-check
periodically, don't assume it still holds on a later tenant build:**

| Asset type | Mentor analysis | ODC Portal display |
|---|---|---|
| `WebApplication`, `LowCodeLibrary` | Analyzed, real score | Real score |
| `Agent`, `Workflow` | Not analyzed — trigger 404s (`OS-AIMS-40401`) | Absent from the console entirely |
| `MobileApplication` | Not analyzed — API returns `Failed` | Shows a **false `100`** — never quote it as a passing gate |

The portal's "last analysis" banner and "next analysis in Xh" countdown only
advance on the tenant's *scheduled* sweep, not on-demand runs — trust the
per-asset score, not that timestamp. To trigger/poll/report the real Mentor
score on demand, use the `outsystems-code-quality-score` skill.

## Scope & assumptions

- **Access:** the runtime URL is assumed **public / no auth**. If a capture lands on a login page, consent wall, or error screen *instead of* the app, **stop and tell the user** — do not score a login form as if it were the app. (Auth-gated runtimes are out of scope.) A landing page that merely *links* to a login is fine — that login is one of the shallow-crawl surfaces, not the audit target.
- **Captures:** landing URL at **desktop 1440×900 + mobile 390×844**, plus a **shallow crawl** of a few in-app surfaces, **interaction states** (focus ring, hover before/after), and a **mechanical probe** (`probe.json`) with measured tap-target sizes and computed motion/transition/focus signals. This is what lets the accessibility (C6) and behaviour (C10–C12) criteria be scored rather than defaulted to N/A.
- **Rubric:** 16 criteria, 6 categories. Per-criterion tier ∈ {Market Leading=4, Delightful=3, Acceptable=2, Unpleasant=1, Broken=0, N/A}. Weights: C1–C13 = 1×, C14/C15/C16 = 1.5×. See scoring below.

## Inputs to gather first

| Input | Required? | Notes |
|---|---|---|
| Runtime URL | **Required** | The live link to audit. If missing, ask — do not guess. |
| Output path | Optional | Defaults to `output/<slug>/runtime-audit.md` (`<slug>` from URL host+path). |
| Max crawl screens | Optional | Defaults to 4. Pass `Max screens: 0` to disable crawling. |
| Viewports | Optional | Defaults to `desktop,mobile`. |

## Step 1 — Capture

Capture with Playwright driving the **system Google Chrome** (no Chromium download). The script ships next to this skill at `capture.mjs`. Node resolves ESM imports relative to the **script's own directory**, so copy it into a working dir where `playwright` is installed and run it there — do not run it in place from the skill folder.

```bash
SKILL_DIR="<this skill's own directory>"   # resolve from where THIS SKILL.md was loaded — do not hardcode an agent-specific install path
WORK="${TMPDIR:-/tmp}/rua"                 # or your session's designated scratch/work directory
URL="<runtime url>"

mkdir -p "$WORK" && cd "$WORK"
npm i playwright >/dev/null 2>&1        # JS package only (~1s), no browser download
npx playwright install ffmpeg >/dev/null 2>&1   # required: the session.webm recording fails without playwright's ffmpeg (cached after first install)
cp "$SKILL_DIR/capture.mjs" .
node capture.mjs "$URL" ./shots         # add --max-screens=N or --no-crawl / --viewports=desktop as needed
```

The script writes into `./shots/` and prints one JSON line per capture plus a final `{probe:...}` summary:

| Artifact | Feeds |
|---|---|
| `desktop.png`, `mobile.png` | landing, full-page — primary evidence for most criteria (C1–C5, C7, C8, C13, C14, C16) |
| `screen-NN-<slug>.png` | crawled in-app surfaces — C9 app depth, C10 states (empty/detail/error screens) |
| `focus.png` + `probe.focus` | C6 keyboard — the focused element and its computed outline |
| `hover-before.png` / `hover-after.png` + `probe.hover` | C12 micro-interactions — resting vs hover |
| `probe.tapTargets` | C5 — measured bounding boxes, `pctGte44`, and a sample of undersized controls |
| `probe.motion` | C11/C12 — count of elements with transitions, durations, and whether `prefers-reduced-motion` is handled |
| `probe.identity` | C16 — measured design tokens (fonts, palette by frequency, radii, shadows, imagery counts) and explicit hits on the `#1068eb`/`#f3f6f8` platform defaults; cross-checks C1/C14 |
| `session.webm` | C11 — a recording for optional human review (you can't watch it; use `probe.motion` + hover pair) |

- **A blank capture exits 3 and writes no `probe.json`.** If the landing page reports zero interactive elements, the script writes `CAPTURE-FAILED.json` instead and exits **3** — it never scores a page that did not render. This is deliberate: a blank capture does not read as an error, it reads as a *clean app*, and it fails **optimistically** (zero tap targets, null focus, `osDefaults.present: false` — which scores C16 better than the truth). **The remedy is almost always to re-run against an explicit screen URL rather than the app's base path**, where a client-side redirect to the default screen can outrun the readiness window. Measured on a live run 2026-08-11: the documented base URL produced a blank white capture while every crawled screen rendered perfectly.
- **Sanity-check the printed desktop `title`/`url`.** If the final `url` is a login/SSO host or the title reads like an error/login page, the app is auth-gated — stop and report (see Scope).
- If `channel: 'chrome'` fails (no system Chrome), run `npx playwright install chromium` once and drop the `channel` option in your working copy. Note the fallback in the report's Method section.

## Step 2 — Read the captures and score each criterion

View every PNG with an image-capable file reader, and read `probe.json` for the mechanical signals. Judge **desktop** as the primary artifact; use **mobile** to check responsive breakage (overflow, clipping, collapse) and the **crawled screens** for app depth and states.

For each of the 16 criteria in [`rubric.md`](rubric.md):

1. **Gather evidence** from the relevant capture(s) + probe signals.
2. **Map to a tier** (Market Leading / Delightful / Acceptable / Unpleasant / Broken) using the rubric's tier definitions, or **N/A** per its rules.
3. **Record** `{criterion, tier, score_value, weight, evidence}`. Evidence MUST be concrete — a hex colour you see, a named component, a measured value from `probe.json`, a region ("the two hero cards"), a measured misalignment. Never a generalization. **C14 and C15 must include their numeric 1–5 score in the evidence.**

**How the probe resolves the criteria that would otherwise be N/A:**
- **C5 Tap targets** — use `probe.tapTargets.pctGte44` against the rubric bands (100 / ≥95 / 80–94 / 60–79 / <60). The measured sample is authoritative over eyeballing.
- **C6 Keyboard** — `probe.focus`: no focus state → N/A; a **default** browser ring (`outlineStyle: auto`, browser blue, no custom design) caps at **Acceptable**; a designed, consistent ring → Delightful+. Confirm the ring is visible in `focus.png`.
- **C11 Animations** — `probe.motion`: transitions present with sane durations (0.15–0.25s) but `prefersReducedMotionHandled:false` caps at **Acceptable**; zero transitions and no recording insight → lean Unpleasant/N/A per what's observable.
- **C12 Micro-interactions** — compare `hover-before.png`/`hover-after.png` and `probe.hover.changed` plus per-element transitions; inert hover + no other crafted moments → Unpleasant.
- **C10 State Communication** — score only if a loading/error/empty/completion state appears in any capture (often a crawled screen); otherwise N/A.
- **C9 IA & App Depth** — use the crawl: a landing page that leads only to a login is legitimately **shallow** (Unpleasant/Acceptable) — score the depth actually observed, don't assume unseen depth.
- **C16 Visual Identity** — `probe.identity` measures the four identity dimensions the rubric asks for: `fonts` → Typography, `colors` + `osDefaults` → Palette, `radii`/`shadows` → Shape & depth, `imagery` → Imagery & iconography. Judge each authored or default and count. Each `osDefaults.hits[].where` entry gives a `selector`, the control's `text`, and the `property` that carries the default — quote that in the evidence, with `identity.screen` for the surface. `where` is a bounded sample; `hits[].count` is the true total. If `identity.truncated` is true the scan hit its runaway guard and "no hits" is not proof of no defaults.

Calibration guards (these trip up automated evaluators):
- **Don't invent failures for absent things.** No shadows anywhere is not automatically a fail; one instance of a component type is coherent unless there's an obvious conflict.
- **OutSystems-default tells are the highest-signal mechanical checks:** primary/CTA `#1068eb` or background `#f3f6f8` drag down C1, C14, and C16 hard. Call them out explicitly when present — `probe.identity.osDefaults` detects both by measurement.
- **Don't let one observation score three criteria.** The same default tell may be cited under C1, C14 and C16, but it cannot on its own set C16 (3.5 weight units from one look at one button) — C16 requires all four identity dimensions judged. Likewise C15 scores the Craft axis; an app with no AI claim records `AI: not claimed` and is never marked down for it.
- **Charts and user-submitted content (avatars, thumbnails) are exempt** from palette/consistency criteria (C1).
- **N/A is a real answer.** Prefer it over guessing. If ≥ 6 criteria are N/A, the score is flagged low-confidence.

## Step 3 — Compute the score

```
Numerator   = Σ  score_value(i) × weight(i)          [non-N/A only]
Denominator = Σ  4 × weight(i)                        [non-N/A only]
Final %     = round( Numerator ÷ Denominator × 100 )
```

Weights: C1–C13 = 1×, C14/C15/C16 = 1.5×. Map the % to an overall tier:

| Range | Tier |
|---|---|
| ≥ 85% | Market Leading |
| 65–84% | Delightful |
| 45–64% | Acceptable |
| 25–44% | Unpleasant |
| < 25% | Broken |

Flag **low-confidence** if ≥ 6 criteria are N/A.

## Step 4 — Output format

Produce a Markdown report **and write it to a file** (default `output/<slug>/runtime-audit.md`; overwrite if present). Copy the captures into an adjacent `shots/` folder and embed them by relative path so the report is self-contained. Lead with the headline, then the table, then per-criterion evidence. After writing, tell the user the path and print the headline + table to the conversation.

Emit the report using the skeleton in [references/prompt-templates/runtime-audit-report.md](references/prompt-templates/runtime-audit-report.md), filling its angle-bracket placeholders (`<app / URL>`, `<NN>`, `<Tier>`, numerator/denominator/N-A counts, `<url>`/`<final>`, `<M>` crawled surfaces, findings, and the N/A list) with measured values — headline, per-criterion score table (one row per scored criterion, evidence per the rules above), notable findings, embedded screenshots, and Method.

## Optional — Runtime health evidence (internal-only)

> Added 2026-08-13 (P6, dossier rev. 17) from `OutSystems/rd-ai-ase-toolkit` RAOPST-3994: the internal `odc` CLI's `app health` verb reads per-app runtime telemetry from ODC Analytics API v5.

An **optional** enrichment: measured runtime telemetry (appScore, requests, errors, error %, P95/P99 latency, unique users, last error) rendered as a separate evidence block after the report. It is telemetry beside the visual audit — the health block **never feeds, changes, or affects the 16-criterion score, weights, or tier**; the rubric is untouched, exactly like the mechanical probe feeding evidence without being a criterion.

**Availability gate (this decides everything):** the `odc` CLI is **internal-only** and the pack-shipped variant of this skill must degrade gracefully. Probe with `odc app health --help` and require it to **exit 0** — a mere binary-exists check is not enough, because an older internal CLI installs the same `odc` name without this verb. If the probe fails — the default for colleagues — **omit the section entirely**: no placeholder, no "health unavailable" row, no error. Section absent is the normal shipped behaviour.

When the verb exists and the audited URL maps to a known ODC app:

```bash
odc app health "<app name|key>" --stage <env> > "$WORK/app-health.json"   # read-only; JSON is the default output
python3 "$SKILL_DIR/health_evidence.py" "$WORK/app-health.json"           # renders the report block on stdout
```

Append the renderer's stdout to the report verbatim, per [references/prompt-templates/runtime-health-evidence.md](references/prompt-templates/runtime-health-evidence.md). Never compose the block by hand: the renderer is what mechanically enforces the CLI's semantics —

- **`noData.status: "undetermined"` renders as "no data", never as a score.** The CLI only lists an app as traffic-free when the response proved the page complete; an undetermined read carries the reason and nothing else.
- **`appScore` is an Apdex-style latency score, not a health verdict** — it says nothing about failures, and **an app with no traffic scores 100**. The caveats print on every render and a score on thin traffic (<100 requests) is flagged inline, so `appScore: 100` on a quiet app can never read as praise.
- **An absent metric is the absence of a reading, never a zero**; unresolved app inputs are surfaced as reduced coverage.

`odc app health` is a read (a GET against the Analytics API); the read-only contract of this skill is unchanged. Default window is 24h — pass `--hours` for a different look-back, and leave `--limit`/`--offset` alone so `noData` stays determinable.

## Batch mode

If the user passes multiple URLs, run Steps 1–4 per URL (each to its own `output/<slug>/runtime-audit.md`) and finish with a comparison table:

| App / URL | Score | Tier | Worst criterion | Best criterion |
|---|---|---|---|---|
| app-a | 58% | Acceptable | C5 Tap Targets (Unpleasant) | C14 Modern (Delightful) |

## Mentor handoff (compare-and-converge)

Emit this section only when the user requests convergence (e.g. "audit and fix", "iterate until Delightful") or names a target ODC app for the audited URL. Adopted from the Enzyme investigation (2026-08-06): their service turns a vision gap report into the next iterate instruction and loops until the deployed app converges.

After the report, append a `## Mentor handoff` block using the skeleton in [references/prompt-templates/mentor-handoff.md](references/prompt-templates/mentor-handoff.md), filling its placeholders. Its first line states the loop's target tier, for any convergence request (generic "audit and fix" included): the tier the user asked for, else one tier above the current audit result — record the default explicitly. If the audit already scores Market Leading there is no tier above: emit the handoff only when the user supplied an explicit goal; otherwise report the app as converged instead of emitting one. Then list **at most five** fix instructions, worst-first by weighted criterion impact. Each item must cite its criterion number and quote the evidence line it comes from — never invent a fix the scored evidence does not support, and never pad the batch to five. Phrase each item as a screen-scoped, imperative OutSystems instruction ("On <screen>, increase the nav link tap targets to ≥44px"), not as a rubric complaint.

**Design-scope gaps are skipped, not manufactured (C15-C16 design pass, 2026-08-07).** A criterion the report declares a design-scope gap — currently only C15's design-scope note (rubric.md § C15) — is never ranked into a fix item, because no bounded token or config change can close it. Skip it and rank the next-worst actionable criterion in its place; record the skip as one line above the numbered list ("Skipped: C15 — design-scope gap, see report.") so it reads as a decision, not an omission. This does not relax the five-item cap or the worst-first order for the criteria that are ranked.

**C16 is now handoff-targetable per dimension.** `probe.identity` and the redesigned C16 (rubric.md § C16) judge four named dimensions — Palette, Typography, Shape & depth, Imagery & iconography — each authored or default. When more than one is reported default, split C16 into one item per unauthored dimension instead of one generic C16 fix: tag each `C16 (<Dimension>)`, and quote that dimension's evidence line, including the `probe.identity` locator (selector, visible text, CSS property) when the evidence is an `osDefaults` hit — e.g. "On Search_Query, replace the `#1068eb` primary button (`body > main > button.btn`, "Search by query") with the product's authored accent." Per-dimension C16 items still count toward the overall five-item cap and occupy C16's ranked position in the worst-first order; they don't get extra slots beyond it.

This skill still does not run Mentor, publish, or modify the app — the handoff is text. Execution belongs to `outsystems-mentor-implementation` (Converge iteration), whose digest gate decides whether the publish changed anything. The loop closes by re-audit: after the converge iteration publishes, re-run this skill on the same URL and compare scores. Stop when the target tier is reached, or when two consecutive audits show no weighted-score improvement — a flat re-audit means the remaining gaps need a human, not another batch.

## What this skill does NOT do

- Does not modify, deploy, or fix the app.
- Does not attempt to log in; the crawl stays within the app's public path. **So this skill cannot discharge a render gate for a role-gated screen** — a clean audit here is evidence about the public surface only, and on one measured app the authenticated surface was half the application and held the defects. A gated screen needs a principal holding the role to open it and report what rendered; until then it is `unverified`, not `N/A` and not passed.
- Does not inspect the OML/theme/CSS — that's the companion `outsystems-ui-review` skill.
- Does not produce vibes-based scores — every tier cites a concrete observation or a `probe.json` measurement.

If you cannot capture a usable landing screenshot (auth wall, error page, blank render), say so and stop. Prefer reporting the blocker over scoring a page that isn't the app.
