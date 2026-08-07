# UI Quality Assessment — Rules and Guidelines

> Canonical rubric for the [`runtime-ui-audit`](SKILL.md) skill. Last rubric version: 12 May 2026; **C15 and C16 redesigned 2026-08-07** after the first live converge run (diagnosis: `prototypes/first-live-converge/C15-C16-DESIGN-PASS.md`). When a criterion's intent or tier boundary seems ambiguous, this file wins.

## What are we measuring?

A framework for scoring the **UI quality** of external-facing apps from captured images. It covers **16 criteria** across 6 categories and produces a single weighted score per assessment. Current scope is **external-facing apps only** — internal tools and designs are out of scope.

This judges *what the user sees and experiences* (perceived quality), not how the app was built. The build-focused counterpart is the companion `outsystems-ui-review` skill, which scores the same 16 criteria against the implementation rather than the runtime.

## Scoring system

Each criterion receives exactly one of: **Market Leading**, **Delightful**, **Acceptable**, **Unpleasant**, **Broken**, or **N/A**.

```
Numerator    = Σ score_value(i) × weight(i)
Denominator  = Σ max_score(i) × weight(i)   [non-N/A items only]
Final %      = Numerator ÷ Denominator × 100
```

**Score values:** Market Leading = 4 · Delightful = 3 · Acceptable = 2 · Unpleasant = 1 · Broken = 0
**Weights:** C1–C13 → 1× · C14, C15, C16 (User Perception) → 1.5×

**Examples:** all 16 Acceptable (2) → 35 ÷ 70 × 100 = **50%** · all 16 Market Leading (4) → **100%**.

**Low-confidence flag:** if **6 or more** criteria are N/A, flag the score as low-confidence (rubric is <63% complete).

**Overall tiers:**

| Range | Tier |
|---|---|
| ≥ 85% | Market Leading |
| 65–84% | Delightful |
| 45–64% | Acceptable |
| 25–44% | Unpleasant |
| < 25% | Broken |

**N/A** means the criterion cannot be evaluated from the provided images. **Prefer N/A over guessing.**

**Default N/A rules** — apply unless evidence explicitly overrides:

- **Keyboard interaction (C6)** → N/A unless a focused-element state is captured (a focus ring visible in a screenshot, or a focus probe).
- **Animations (C11)** → N/A unless motion is captured (recording, filmstrip) or motion signals are probed (computed `transition`/`animation`).
- **Micro-interactions (C12)** → N/A unless hover/active/success states are captured or probed.
- **State Communication (C10)** → N/A only when zero loading, error, empty, and task-completion states are visible across all captures. If any one is present, it must be scored.
- **IA & App Depth (C9)** → N/A only if a single isolated widget with no navigation context is captured.

---

## Criteria at a glance

| # | Category | Criterion | Weight | Min capture | Default N/A |
|---|---|---|---|---|---|
| 1 | Design system | Theme & Styling | 1× | Static screenshot | No product-owned UI visible |
| 2 | | Component Reuse | 1× | Static screenshot | No interactive components visible |
| 3 | | Component Fit & Purposeful Config | 1× | Static screenshot | Not enough UI patterns visible |
| 4 | Accessibility | Color Contrast (WCAG AA) | 1× | Static screenshot | Image quality too low |
| 5 | | Tap / Click Target Size | 1× | Static screenshot | Resolution makes sizing unreliable |
| 6 | | Keyboard Interaction | 1× | Focused-element capture / probe | No focus state captured |
| 7 | Layout | Grid Adherence | 1× | Static screenshot | Image resolution too low |
| 8 | | Margin & Padding | 1× | Static screenshot | Single non-comparable element |
| 9 | | IA & App Depth | 1× | Multiple screenshots | Single isolated widget |
| 10 | Behaviours | State Communication | 1× | Any loading/error/empty state | None of those states visible |
| 11 | | Animations | 1× | Recording / motion probe | No motion captured |
| 12 | | Micro-interactions | 1× | Hover/active/success capture / probe | No interaction state captured |
| 13 | Content | Content & Data Quality | 1× | Static screenshot | No content visible |
| 14 | User perception | Modern vs. Dated | **1.5×** | Static screenshot | Always scoreable |
| 15 | | WoW Effect & AI Integration | **1.5×** | Hero screen / flagship flow | No flagship surface reachable |
| 16 | | Visual Identity & Design Originality | **1.5×** | Static screenshot + `probe.identity` | Always scoreable |

---

## Design system

### C1 — Theme & Styling

**Measure:** Design tokens (color, type, spacing, radius, elevation, iconography, imagery) are consistent AND reflect current best practice. Consistent-but-dated is not Delightful.

Look for: one brand color + neutrals + max 2–3 semantic colors (warm colors only for error/warning/destructive, never decorative); 1–2 type families, ≤3 size/weight steps, body line-height ≥ 1.5; one consistent radius (no mixing 0/4/8/16px); soft shadows (hard drop shadows read dated); icon style scoped by zone (nav one family, content/illustration may differ — only penalise two competing families in the *same* zone); one imagery treatment; disabled elements visually distinct. **FAIL SIGNAL:** OutSystems UI default theme / Bootstrap tells — gray top bar, stock blue (`#1068eb`), pill buttons with heavy shadow, `#f3f6f8` body background.

| Tier | Definition |
|---|---|
| Market Leading | Every token intentional and ownable; visual language unmistakably this product, recognisable without the logo; color science, type ramp, icon system, spatial rhythm cohere as one confident hand. |
| Delightful | Coherent, current token set throughout — modern palette, clean type ramp, soft shadows, one icon family, unified imagery, warm colors for status only. |
| Acceptable | Recognisable theme but drift in 2–3 places (mixed radius, one off-palette color, one mixed icon) OR consistent but dated in one dimension. |
| Unpleasant | Multiple token inconsistencies across categories: mixed radius AND competing accents AND mixed icon sets in the same zones. |
| Broken | Multiple unrelated visual languages on one screen, OR 5+ unrelated accent colors, OR clearly mixed icon sets. |

N/A only if no product-owned UI styling is visible. False positives: user-submitted content (avatars, thumbnails) and chart-library colors are exempt.

### C2 — Component Reuse

**Measure:** Components are reused from a shared library AND well-built (proper variants, states, affordances). Reusing a dated/broken component is not Delightful.

Look for: all primary buttons identical across screens (same for secondary/destructive/ghost); buttons have hover/focus/disabled/loading states; inputs consistently styled with validation/error states; checkboxes for multi-select, radios for single-select (misuse = failure); labels persistent above inputs (never placeholder-only); one version each of cards/tabs/modals/tooltips/breadcrumbs/badges. **RED FLAG:** two visually different "primary" buttons on one screen. Components should feel like current libraries (shadcn, Radix, Material 3), not jQuery UI 2012.

| Tier | Definition |
|---|---|
| Market Leading | Zero competing styles; every instance identical in proportion, color, spacing across the product; well-built with proper states/variants/affordances. |
| Delightful | Single visual language, no competing styles for the same element type; proper states/variants; labels persistent. |
| Acceptable | Visual language present with isolated drift: one or two element types inconsistent, OR coherent library but missing states/variants. |
| Unpleasant | Noticeable inconsistency across multiple component types, or systematic missing states. |
| Broken | Competing visual styles for the same element type, OR components consistently badly built with no states/affordances. |

N/A only if no interactive components visible.

### C3 — Component Fit & Purposeful Config

**Measure:** Components are not only correct for the content type but **purposefully configured** for the use case — real data, domain-appropriate interaction modes, intentional state handling.

Purposeful: Kanban with live counts/WIP limits; step wizard for multi-stage flows; filter tabs with live counts ("Active (12) · Pending (5)"); charts with domain-specific axes/labels; tables with curated (not every-field) columns. Not purposeful: card grid for back-office data management (wrong type); generic KPI cards with no domain specificity; default flat table/chart.

| Tier | Definition |
|---|---|
| Market Leading | Every major surface uses a component purposefully configured for its job; data structures inform the choice (trading terminal, maintenance timeline, pipeline Kanban with live counts); custom configs that wouldn't exist in a generic template. |
| Delightful | Primary surfaces purposefully configured (step wizards, filter tabs with counts, configured charts); some secondary surfaces more generic. |
| Acceptable | Right component, default configuration only — table for tabular data but all columns uncurated; chart present but placeholder-feeling labels. |
| Unpleasant | One or more wrong component choices for the domain, or correct type but broken/misleading config. |
| Broken | Components work against the use case; integration failures exposed (broken tokens, raw IDs where names belong, empty viz with no fallback). |

N/A if not enough UI patterns visible. False positives: card grid for browsing (marketplace, gallery, file picker) is correct; accordions for genuinely secondary content are fine.

---

## Accessibility

### C4 — Color Contrast (WCAG AA)

**Measure:** Text/interactive elements clear WCAG AA (4.5:1 body, 3:1 large text & UI components); color is never the sole differentiator for status/errors.

Look for: near-black on near-white passes; RISKY — light gray text (`#9CA3AF`, `#CCCCCC`) on white, white on light brand colors, colored links on matching-value backgrounds; secondary/tertiary text (captions, placeholders, timestamps, muted tags) are the most common failures; icon-only buttons with low-contrast glyphs; disabled still visible; errors paired with icon/text (red border alone insufficient — ~8% of males have red-green deficiency); links distinguished by more than color (underline/weight); charts use patterns/labels alongside color.

| Tier | Definition |
|---|---|
| Market Leading | All text & interactive elements pass AA; no color as sole differentiator anywhere; charts accessible with patterns/labels. |
| Delightful | Primary and secondary text clearly pass AA; color never sole differentiator; charts accessible. Flag "eye-test pass; automated audit recommended". |
| Acceptable | Primary text passes; 1–2 tertiary/muted elements risky; color sole differentiator in isolated cases. |
| Unpleasant | Multiple contrast failures across secondary text/placeholders/icon buttons; color sole differentiator in several key states. |
| Broken | Obvious low-contrast body text, near-invisible placeholders, white-on-light CTAs, or color as only means to distinguish errors/status. |

N/A if image quality too low or no text/interactive elements visible. False positives: ghost buttons on hero images fine if the image provides contrast.

### C5 — Tap / Click Target Size

**Measure:** % of interactive targets ≥ 44×44px. Market Leading = 100% · Delightful ≥ 95% · Acceptable 80–94% · Unpleasant 60–79% · Broken < 60%.

Look for: primary CTAs/nav/filters/card click areas usually fine; RISKY — icon-only toolbar buttons, kebab/row actions in dense tables, small inline links, chip close buttons, star ratings, narrow tab triggers, pagination; ≥ 8px gap between adjacent targets; checkbox/radio hit zones extend to the label. Mobile minimum is 44px; desktop secondary actions can go lower but primary actions still ≥ 32px. Calibration: use body text (~14–16px) as a scale reference — a target ~3× body-text height ≈ 44px. **A tap-target probe (measured bounding boxes) is authoritative when available.**

| Tier | Definition |
|---|---|
| Market Leading | 100% ≥ 44px; exceptionally generous padding on icon buttons; all labels extend hit zones. |
| Delightful | ≥ 95% ≥ 44px; generous icon-button padding; labels extend hit zones; ≥ 8px spacing. |
| Acceptable | 80–94%; some dense table actions or toolbar icons < 44px but labels carry the hit zone. |
| Unpleasant | 60–79%; multiple controls clearly under 44px in primary/frequent areas. |
| Broken | < 60%; obvious cramping — 12px toolbar icons, 8px close buttons, tightly-stacked inline links with no padding. |

N/A if resolution makes sizing unreliable.

### C6 — Keyboard Interaction

**Measure:** All interactive elements reachable/operable by keyboard, with visible focus state and logical tab order.

Look for: visible focus ring on any captured focused element (outline/ring/background change); focus ring **designed**, not just the default browser ring; tab order follows reading order; modals trap focus, Escape closes; dropdowns support arrow keys; custom components match native keyboard patterns; skip-to-content link near the top.

| Tier | Definition |
|---|---|
| Market Leading | All focus rings custom-designed and distinctive; tab order perfect; all custom components have correct keyboard patterns; skip-to-content present. |
| Delightful | Focus rings visible and consistently designed; tab order follows layout; modals trap focus; Escape works; custom components correct. |
| Acceptable | Some focus styles visible but inconsistent; tab order mostly logical. |
| Unpleasant | Focus rings absent on most elements or broken on custom components; tab order broken in key flows. |
| Broken | `outline:none` with no replacement; no focus styling; or tab order clearly broken throughout. |

N/A unless a focused state is captured/probed. Note: a captured **default** browser focus ring (e.g. `outline: auto 1px`) with no custom design caps this at **Acceptable**, not Delightful.

---

## Layout

### C7 — Grid Adherence

**Measure:** Spacing/sizing snap to an 8pt (or 4pt) grid. Market Leading 100% · Delightful ≥ 95% · Acceptable 80–94% · Unpleasant 60–79% · Broken < 60%.

Look for: vertical rhythm on 16/24/32/48px (not arbitrary); left edges of headings/paragraphs/inputs/buttons line up; column widths as grid multiples; icon sizes 16/20/24 (not 17/22/23); related elements grouped closer than unrelated (Gestalt proximity); critical actions in high-attention zones (top-left, not buried in right rail); scroll affordance (partially visible element below fold); primary actions/required inputs/critical status never in the right rail.

| Tier | Definition |
|---|---|
| Market Leading | 100% on grid; perfect proximity groupings; scroll affordances present; critical actions in prime zones throughout. |
| Delightful | ≥ 95% on grid; proximity/groupings clear; scroll affordances present; critical actions in high-attention zones. |
| Acceptable | 80–94% aligned; minor drift (14 vs 16px gutter, heading 1px off); groupings generally clear. |
| Unpleasant | 60–79%; widespread ragged edges, inconsistent spacing in multiple sections. |
| Broken | < 60%; widespread ragged edges, or groupings ambiguous/misleading. |

N/A if resolution too low. False positives: intentional optical corrections are not violations.

### C8 — Margin & Padding

**Measure:** Margins/padding consistent AND best-practice — generous enough to breathe, not cramped.

Look for: same container padding across equivalent screens; card internal padding consistent per type and at modern scale (16–24px, not 6–8px) — first identify the product's dominant scale (compact vs generous), then flag inconsistency *with its own scale*; form field spacing ≥ 8px label-to-input, ≥ 16px between fields; safe zones around modals/toasts/popovers; whitespace reinforces hierarchy; scrollable containers have inner padding.

| Tier | Definition |
|---|---|
| Market Leading | Perfectly consistent across all screens; whitespace masterfully creates a clear, memorable hierarchy. |
| Delightful | Consistent across screens; values follow best practice (generous but purposeful); whitespace reinforces hierarchy. |
| Acceptable | Minor drift (16 vs 20px between similar cards) OR consistent but tight/cramped throughout. |
| Unpleasant | Visibly inconsistent across screens; some cramped, some over-padded; hierarchy from whitespace unclear. |
| Broken | Visibly inconsistent (one screen cramped, another over-padded), unaligned gutters, or extreme mobile-first dispersion making desktop unreadable. |

N/A if only a single non-comparable element visible.

### C9 — IA & App Depth

**Measure:** Navigation structure is logical and domain-appropriate AND the app shows genuine product depth — multiple surfaces, complete flows, thoughtful edge cases.

Look for: multiple distinct screens with intentional nav hierarchy (not one landing page); pre-action context (onboarding/setup/guidance); post-action feedback (confirmation, updated state, next steps); purposeful detail views; progressive disclosure; nav labels naming main tasks (not "Resources"/"More"); one clear primary CTA per screen; breadcrumbs on deeper views; outcome-describing labels ("Save changes" not "Submit"); search/filter for lists > ~20 items; user can orient in < 10s.

| Tier | Definition |
|---|---|
| Market Leading | Complete product journey — pre-action context, core workflow surfaces, post-action flows, edge cases (empty/error/stale); progressive disclosure throughout; orient within 10s on any screen. |
| Delightful | Multiple distinct surfaces with genuine depth; domain-appropriate nav groupings; key flows have pre/post-action context; some edge cases handled. |
| Acceptable | Multiple nav sections but shallow screens; core content visible but secondary flows incomplete; nav functional but generic. |
| Unpleasant | Single-surface or near-single-surface app; no flows/edge cases/context; or confusing nav labels. |
| Broken | No navigation visible / no orientation; or nav leads to empty/broken screens. |

N/A only if a single isolated widget with no nav context is captured. **Note for landing-page-only captures:** a marketing landing that leads only to a login is legitimately **shallow** — score on the depth actually observed (typically Unpleasant/Acceptable), do not assume depth that wasn't captured.

---

## Behaviours

### C10 — State Communication

**Measure:** The UI responds quickly and communicates state — loading feedback, optimistic updates, graceful error recovery, no jank.

Look for: skeleton/shimmer for async (not blank + spinner); spinners only for short (<3s) unknown-duration ops; progress bars for known duration; CTAs show loading after submit (no dead click); optimistic UI; inline errors explaining what happened and what to do next; every list/table has a designed empty state with a next-action prompt; no layout shift/FOUC; scroll position preserved on back-nav; meaningful task-completion states (a bare success screen = failure).

| Tier | Definition |
|---|---|
| Market Leading | Every async moment intentionally designed — skeletons, loading CTAs, inline errors with recovery, designed empty states, memorable completion states; no jank. |
| Delightful | Loading state on CTAs, graceful inline errors, designed empty states with next-action prompts, scroll preserved, meaningful completion states; no jank. |
| Acceptable | Some async states well-handled but gaps — CTAs missing loading feedback, generic empty states, or bare completion state; skeletons absent. |
| Unpleasant | Most async states absent/poorly handled; dead clicks on some CTAs; empty states missing or "No results"; error modals with no recovery. |
| Broken | Dead clicks, blank white on load, no error recovery beyond "Try again", visible layout shift, missing empty states. |

N/A only when zero loading, error, empty, and task-completion states are visible across all captures.

### C11 — Animations

**Measure:** Motion is purposeful, performant, consistent — clarifies relationships, masks latency, reinforces voice.

Look for: modals/drawers/dropdowns/tooltips ease-out at 150–250ms (not instant pop or slow fade); view transitions communicate spatial relationships; no decorative spin/pulse; routine interactions ≤ 400ms; peripheral motion must be essential; scrolljacking = Broken; `prefers-reduced-motion` honoured. **Motion probe:** computed `transition`/`animation` on interactive elements and whether any stylesheet handles `prefers-reduced-motion` are strong signals when a recording isn't available.

| Tier | Definition |
|---|---|
| Market Leading | Every transition purposeful and perfectly timed; motion consistently communicates spatial relationships; `prefers-reduced-motion` honoured; recognisable, ownable motion personality. |
| Delightful | Purposeful transitions at 150–250ms; no peripheral distractions; `prefers-reduced-motion` honoured; motion communicates spatial relationships consistently. |
| Acceptable | Some transitions but inconsistent timing/presence, OR motion decorative but not distracting. |
| Unpleasant | Inconsistent/distracting motion; some transitions > 400ms; peripheral animations interrupt tasks; no reduced-motion support. |
| Broken | Everything pops instantly (brittle) OR over-animated OR scrolljacking OR peripheral animations interrupting primary tasks. |

N/A unless motion is captured or probed. Note: transitions present with good timing (150–250ms) but **`prefers-reduced-motion` unhandled** caps this at **Acceptable**.

### C12 — Micro-interactions

**Measure:** Small crafted interaction details that make actions feel responsive and give the product personality.

Look for: button hover/active with subtle scale/color/shadow (not instant swap); toggle/switch smooth ease; checkbox/radio fill animation; validation on blur (not every keystroke); destructive actions get an undo toast; copy/save/done show confirmation; rows/list items get hover fill; designed empty states; multi-step flows show progress. Hover before/after captures and computed hover/transition signals are the primary evidence for static audits.

| Tier | Definition |
|---|---|
| Market Leading | Rich crafted details throughout — animated toggles, blur validation with success indicators, undo toasts, designed empty states; recognisable interaction personality. |
| Delightful | Multiple crafted moments — animated toggles, blur validation, undo toasts, designed empty states, hover on all interactive elements. |
| Acceptable | Some micro-interactions present but generic — not unpleasant, nothing memorable. |
| Unpleasant | Most interactions inert; no hover states on many elements; instant state changes with no feedback. |
| Broken | Inert — no hover, instant changes with no feedback, default browser input styling, absent empty states, no validation feedback. |

N/A unless hover/active/success states are captured or probed.

---

## Content

### C13 — Content & Data Quality

**Measure:** Data/content feels real, domain-specific, built for an actual use case — not placeholder filler. AI-enhanced content the user can act on scores highest.

Signals: AI confidence scores with actionable CTAs ("87% confidence · Create work order") → Market Leading; real-looking financial data (tickers, P&L, specific dates) or domain content (equipment IDs, sensor readings, order numbers with status history) → Delightful; generic filler ("Project 2", "System Status: Operational", "User Name", placeholder KPIs) → Unpleasant; raw DB IDs (UUIDs as names) or lorem ipsum everywhere → Broken.

| Tier | Definition |
|---|---|
| Market Leading | AI-enhanced content surfaced at the right workflow moment — confidence % with context, predictive signals with actionable next steps, domain intelligence the user acts on; content makes the app feel genuinely intelligent. |
| Delightful | Real-looking, domain-specific data throughout — plausible names, realistic values, proper timestamps; a domain user would recognise it; no obvious placeholder patterns. |
| Acceptable | Mostly domain-relevant but some generic filler; status labels meaningful ("Shipped", "In Review") but names/values feel assembled rather than authored. |
| Unpleasant | Predominantly generic filler — sequential names, generic status strings ("OK", "Active"), placeholder KPI values with no units. |
| Broken | Raw technical identifiers exposed as content, lorem ipsum visible, critical fields empty, or content misleads about the app's function. |

N/A only if no content visible.

---

## User perception — all three carry **1.5×** weight

### C14 — Modern vs. Dated

**Measure:** Expert review, 1–5 (1 = dated, 5 = modern). Market Leading = 5 · Delightful ≥ 4 · Acceptable = 3 · Unpleasant = 2 · Broken = 1. **Include the numeric 1–5 in the evidence field.**

MODERN: soft shadows; 8–12px card radius; generous whitespace; one intentional accent; clean sans-serif ramp (Inter, SF, Geist); motion where it helps. DATED: hard drop shadows; decorative gradients; glossy buttons; default Bootstrap/jQuery UI; dense gray-on-gray text; rainbow accents; 2012-era stock icons; heavy OS scaffold with no customisation — recognisable OS chrome, unmodified default theme (stock blue `#1068eb`, `#f3f6f8` background). Glassmorphism: subtle is fine, overuse is dated. Dark-mode support is a positive signal; its absence is neutral. Benchmark: 5 = Linear, Notion, Airtable, Stripe, shadcn UIs, Vercel, Figma; 2 = OutSystems UI default theme.

| Tier | Definition |
|---|---|
| Market Leading (5) | Feels like a design reference; matches/exceeds Linear, Notion, Stripe; would be cited by designers as modern UI craft. |
| Delightful (4) | Current patterns — soft shadows, proper radius, whitespace, neutral palette with intentional accent, no unnecessary gradients/skeuomorphism. |
| Acceptable (3) | Some modern elements but outdated patterns mixed in (hard drop shadows, dense gray-on-gray, decorative gradients). |
| Unpleasant (2) | Clearly dated; multiple outdated patterns (heavy borders, hard shadows, recognisable scaffold with minimal customisation). |
| Broken (1) | 2010-era — gloss, gradients, sharp corners, heavy borders, default Bootstrap, skeuomorphism. |

Always scoreable (N/A only if no product UI visible).

### C15 — WoW Effect & AI Integration

**Measure:** two independent axes, scored and reported separately.

- **Craft** — does the app contain a **signature element**: something a user would describe afterwards, that a generic template would not have produced?
- **AI** — is AI output surfaced *in the workflow*, in context, with something to act on?

**The tier is the Craft axis.** A strong AI axis raises it by one tier (capped at Market Leading) when AI output is in-context and actionable. The **absence of AI never lowers the score**: when no capture shows an AI feature and nothing in the app claims one, record `AI: not claimed` and score Craft alone. Scoring an app down for lacking a capability it never claimed is a misapplication of this criterion.

Numeric scale: Market Leading = 5 · Delightful = 4 · Acceptable = 3 · Unpleasant = 2 · Broken = 1. **Include the numeric 1–5 in the evidence field**, in this shape:

`Craft: <signature elements, each named and located, or "none">` · `AI: <in-context use, or "not claimed">` · `<n>/5`

**Signature element** — a closed list. Each one you count must be **named and located** on a specific captured screen ("the confidence-scored match panel on `screen-02-triage`"), never asserted in the abstract:

1. an authored hero or illustration (not stock photography, not a screenshot pasted in as page content)
2. a purpose-built data visualisation with domain axes and labels
3. a composite domain surface no generic template would produce (trading terminal, maintenance timeline, pipeline Kanban with live WIP counts)
4. a keyboard or command affordance (command palette, shortcut layer)
5. a designed empty / completion / error state with authored copy and a next action
6. AI output in context with a CTA ("87% match — Assign to Team A")
7. visible personalisation (name, last action, progress, context-aware defaults)
8. a distinctive, consistent motion personality, evidenced by `probe.motion` plus the hover pair

NOT signature elements: AI hidden behind a "Generate" button with no visible output; animation that slows the task; a templated hero; default empty states. Benchmark: 5 = Linear command bar, Stripe dashboards, Arc tabs, Superhuman shortcuts; 2 = default admin template.

| Tier | Definition |
|---|---|
| Market Leading (5) | Two or more signature elements, at least one central to the app's main job; the product would be cited as a reference for it. |
| Delightful (4) | Exactly one signature element (or two peripheral ones), named and located — the user remembers it. |
| Acceptable (3) | No signature element, but the app is coherent and has real interest — a live count, a purposeful toolbar, a working filter; nothing a user would recall. |
| Unpleasant (2) | No signature element and no interest: generic KPI cards, stock tables, placeholder content, default empty states. |
| Broken (1) | No WoW possibility — unfinished, template-only, or actively broken. |

**Design-scope note.** C15 at Acceptable with `AI: not claimed` and no craft defect to cite is a **design-scope gap**, not a defect: no bounded token or config change creates a signature element. Record it as such in the report ("C15: design-scope gap — needs a design pass, not a fix batch") rather than manufacturing an instruction for it. Score below Acceptable only when there is an observable defect to quote.

N/A only when no flagship surface was reachable — crawling was disabled, or every captured surface is a standard form or list. Once a flagship surface is captured, score it.

### C16 — Visual Identity & Design Originality

**Measure:** how much of the visible design is **authored for this product** rather than inherited from the platform's default theme. Judge four dimensions, each **authored** or **default**, from the screenshots plus `probe.identity`:

| Dimension | Authored when | Read from |
|---|---|---|
| **Palette** | one product accent plus neutrals chosen to sit with it, and no platform-default token on screen | `probe.identity.colors`, `probe.identity.osDefaults` |
| **Typography** | a chosen family rather than the theme's stock stack, with a deliberate size/weight ramp | `probe.identity.fonts` + the heading/body ramp in the screenshots |
| **Shape & depth** | one intentional radius language and one shadow or border treatment, applied as a system | `probe.identity.radii`, `probe.identity.shadows` |
| **Imagery & iconography** | product-specific marks, illustration, or a curated icon set — not stock glyphs alone, and never screenshots pasted in as page content | `probe.identity.imagery` + the screenshots |

Distinctive layout proportions and spacing rhythm are a bonus signal toward the top tier, not a fifth dimension.

| Tier | Definition |
|---|---|
| Market Leading | All four dimensions authored **and** the design passes the **logo-removal test** — identifiable from one screen with the logo removed, not confusable with any other product built on the same platform. |
| Delightful | Three of the four authored, none showing a platform default; the product reads as its own thing even where the scaffold stays recognisable. |
| Acceptable | Two of the four authored; the rest are platform default. |
| Unpleasant | At most one authored, with platform defaults visible in the others. |
| Broken | None authored — indistinguishable from the generator's default output, with `probe.identity.osDefaults.present` on the primary surfaces. |

**Not a re-scoring of C1 and C14.** C1 asks whether the tokens are *consistent*; C14 asks whether the style is *current*; C16 asks whether the tokens are *this product's*. The same observation may legitimately appear in all three, but a platform-default tell cannot on its own set the C16 tier — work the four dimensions. (An app can consolidate to a single authored accent, gaining C1 and C14, and still be Acceptable here because typography, shape and imagery stayed default.)

Always scoreable (N/A only if no product UI visible).
