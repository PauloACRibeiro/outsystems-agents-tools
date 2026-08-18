# ODC Visual-Source UI Discipline

Use this guide when an OMI request starts from a visual source: Figma, screenshot, HTML mockup, source HTML/CSS, design brief, screen mockup, or a written UI description that must become a paste-ready Mentor Studio prompt.

This guide migrates the durable discipline from `outsystems-design-to-app` into `outsystems-mentor-implementation`. It does not migrate design-to-app's automatic app creation, Claude-only cache paths, full `spec.json` pipeline, live Mentor execution, or mandatory publish workflow.

## Evidence Boundary

Current official ODC docs support Mentor Web as the new-app generation surface and Mentor Studio as the ODC Studio surface for modifying/extending apps. Current official ODC docs also support using built-in OutSystems UI patterns and adaptive patterns in ODC Studio.

Rules inherited from `outsystems-design-to-app` are field-tested prompt discipline unless separately grounded by current official docs, OMI generated catalogs, OutSystems-public implementation evidence, or tenant observation.

## Intake Gate

Before writing a visual-source Mentor Studio prompt, identify:

- visual source kind: Figma, screenshot, HTML mockup, source HTML/CSS, written UI brief, or generated app snapshot
- target app type and UI framework, using `odc-ui-framework-selection.md`
- target app shell state: verified existing app, verified blank shell, missing shell, or unknown
- target screen/block state: existing verified target, new target, or unknown
- source artifact path when the source is large
- whether the requested deliverable is prompt-only, approved Mentor execution, or review guidance

If no app shell exists, do not create one silently. Use Mentor Web for official no-shell app generation, or use one compact approval gate before any shell-creation action. If the user clearly wants OMI to create the shell, ask for the readable app name, environment context when needed, and exact create action, then verify the canonical app key after creation.
For shell-first scaffold work, see `references/odc-app-shell-first-scaffold.md`.
For visual-source first scaffold work, keep the enriched blueprint as the first
step, then let the scaffold guide consume that artifact for shell approval and
boundary handling before returning here for prompt discipline.

## OMI Visual-Source Enriched Blueprint

Use the enriched blueprint as the primary structured artifact.

Before prompt emission, open `references/odc-visual-source-enriched-blueprint.md`
and build or validate the OMI-owned portable enriched blueprint at
`assets/visual-source-enriched-blueprint.json`.

The blueprint is where OMI should preserve the quality-bearing structure for:

- component selection
- states and feedback
- workflow block-mapping discipline
- gotcha review
- `acceptance_checklist`

The review gates below still apply. They should shape the blueprint first, then
the emitted prompt summary and Mentor prompt.

## Visual-Source UI Prompt Packet

Use the prompt packet as the condensed emission summary that feeds prompt generation.

For OMI, do not copy the full spec.json schema from `outsystems-design-to-app`.
After the enriched blueprint is coherent, derive this smaller packet from it
before prompt emission:

1. Source inventory: every visible region, text element, data element, interaction, icon, media element, and navigation affordance.
2. Layout Skeleton Gate: choose the screen layout, primary regions, card surfaces, and adaptive pattern skeleton before individual widgets.
3. Default Layout Replacement Review: if a generated or existing screen already has default layout/chrome children, review whether they must be removed, reused, or left intact before adding the selected layout.
4. Block Mapping Gate: map each source region to an OutSystems UI block, standard widget, verified existing block, or bounded custom CSS.
5. Component Selection Heuristics: choose table vs cards, tabs vs accordion, radio buttons vs dropdown, list vs gallery, and chart/media patterns based on the source intent instead of screenshot convenience. Record those decisions in the enriched blueprint so the prompt packet and Mentor prompt do not regress to screenshot-matching shortcuts.
6. Chrome Batch Discipline: when app chrome, menu entries, page links, user info, search, theme toggles, or notification badges are source-critical, handle them in a dedicated producer batch before burying them in screen prompts.
7. Producer and binding plan: list every Aggregate, Data Action, local list, static entity list, input parameter, URL variable, value variable, and option list before widgets consume it.
8. Four-part section contract: every section has VISUAL LAYOUT, DATA FLOW, FUNCTIONAL BEHAVIOR, and PRESENTATION ORDER.
9. Data-Flow Parity Gate: every Expression, image, URL, option, selected value, and repeated item in VISUAL LAYOUT has matching DATA FLOW and a source-like input.
10. State plan: loading state, empty state, error state, validation state, and destructive-action confirmation when applicable. Preserve the state and feedback decisions in the enriched blueprint so the emitted prompt packet stays compact without dropping them.
11. Polish acceptance: remove default pattern children, use typography hierarchy, preserve extracted colors/sizes, use realistic sample content, keep section spacing through OutSystems UI utilities when possible, and name manual review checks.
12. Evidence boundary: Current official, Catalog-backed official, OutSystems-public implementation evidence, or Unverified gap.

The prompt packet is not the primary contract. It is the compact preparation or
output summary that carries forward the blueprint decisions into prompt
generation and review. Do not treat it as a mandatory fifth visible section
before `### Mentor Studio Prompt`.

## State Coverage Checklist

Before prompt emission, explicitly review:

- CTA loading state
- empty state anatomy
- validation success state
- destructive-action confirmation
- post-action success feedback

Keep these states visible in the enriched blueprint and in the prompt packet so
Mentor output does not regress into static happy-path screens only.

## Polish Acceptance Review

Before delivery, confirm:

- brand color used sparingly
- one clear focal point
- section headings as the `HTML Element` widget with `Tag="h2"`

Also keep the existing typography hierarchy, realistic placeholder content, and
section-spacing checks explicit instead of assuming the source polish will
survive translation automatically.

## Domain-Aware Styling Heuristics

This section is the detailed review contract for domain-aware styling
decisions.
Business/workspace apps should stay quiet, dense, and scan-friendly. Avoid
editorial or marketing-heavy styling unless the source clearly requires it.
When the source is ambiguous, prefer operational clarity, compact hierarchy,
and predictable scanning over decorative emphasis.

## Tailwind-To-OutSystems Normalization

Read hex / px / direction from Tailwind during extraction, but write
OutSystems UI classes, ThemeValues, CSS variables, and OMI-friendly prose.
Never write Tailwind class names into `outsystems_hints.css_classes`.
`outsystems_hints.block` must stay a bare block name.

Keep Tailwind as extraction evidence only. Any machine-readable hint that looks
like a prose sentence instead of a bare block name should be rewritten before
prompt emission.

## Theme-Collision Review Nuance

Treat theme collision as a review signal, not blanket permission for
`!important`. Prefer theme-token or class-extension fixes first. Only keep a
hard override as a bounded review note when the conflict cannot be explained or
resolved through the existing theme structure.

## Layout Skeleton Gate

Before detailed widget instructions, choose the structural skeleton:

- one screen layout strategy
- main content regions
- repeated surfaces
- card or list structure
- navigation and chrome regions
- adaptive blocks that own multi-child layout

Do not start from a wall of Containers. A Container is allowed for local grouping or styling, but it must not replace a real layout or UI pattern when one exists.

## Default Layout Replacement Review

When a prompt creates or modifies a Screen, review the existing root layout and chrome before adding a new layout. If the source requires `LayoutSideMenu`, `LayoutTopMenu`, or `LayoutBlank`, state whether default generated layout/chrome children should be removed, reused, or left unchanged.

Do not apply a blind "delete default layout" rule to every existing screen. Treat it as a visual-source review gate because existing-app changes may intentionally keep the current layout.

## Block Mapping Gate

Before prompt emission, produce a block mapping table. Every visual region maps to one of:

- OutSystems UI pattern or block
- standard ODC Studio widget
- verified existing Web Block
- bounded custom CSS for details with no known block equivalent

Use OutSystems UI adaptive blocks for multi-child layout:

- `Columns2`
- `Columns3`
- `Columns4`
- `Columns5`
- `Columns6`
- `ColumnsMediumLeft`
- `ColumnsMediumRight`
- `ColumnsSmallLeft`
- `ColumnsSmallRight`
- `Gallery`
- `MasterDetail`
- `DisplayOnDevice`

Reject custom CSS layout for screen-level or section-level multi-child structure. If a section uses `display-flex`, `display-grid`, `flex:`, `flex-1`, `flex-direction-row`, `grid-template-columns`, or `repeat(N, 1fr)` to place independent visual regions side by side or in a grid, rewrite the section to use an adaptive block.

The allowed exception is inline alignment inside a single placeholder, such as icon plus text inside one card slot or title plus command inside one header slot. Keep that exception local to one conceptual element.

## Source-Name To Block Gate

When source metadata names a known pattern, prefer the named pattern over a visually similar layout substitute:

- `Carousel`, `Carrousel`, or `Slider` -> `Carousel`
- `Gallery` -> `Gallery`
- `Tabs` -> `Tabs`
- `Wizard` -> `Wizard`
- `Accordion` -> `Accordion`
- `Sidebar` -> `Sidebar`
- `Stepper` -> `Stepper`

Do not replace a named `Carousel` with `Columns3` only because the captured viewport shows three cards. Use the pattern name and add review notes for required properties, placeholders, events, and producer bindings.

## Component Selection Heuristics

Use the source intent to select the widget or pattern:

- dense comparison or operational records -> Table or Data Grid
- scan-friendly object summaries -> cards inside Gallery or List
- mutually exclusive small choices -> Radio buttons or Button Group
- large or remote option sets -> Dropdown, Dropdown Search, or typed option list
- sibling views with persistent context -> Tabs
- progressive disclosure of long content -> Accordion
- multi-step process -> Wizard or Stepper when catalog evidence supports it
- media inspection -> Lightbox Image, Image, or Video with verified source URL variables

If the source is ambiguous, include the selected heuristic in the Visual-Source UI Prompt Packet instead of silently choosing by visual similarity.
Make the same choice explicit in the enriched blueprint so component selection
stays reviewable before prompt text is emitted.

## Chrome Batch Discipline

When source-critical app chrome exists, keep it producer-first:

- app title or logo
- menu groups and page links
- user info region
- notification badge
- search bar
- theme toggle
- global command buttons

Create or update chrome producers before screen consumers when the screen depends on them. If the implementation route intentionally defers chrome, record that deferral in the prompt packet and summarize it in the Prompt Coverage Audit when it materially affects review.

This rule is enforced, not advisory. Before emitting a prompt package from a blueprint that declares `app_chrome`, run `scripts/check_chrome_coverage.py <blueprint-or-design-dir> <emitted-prompt-file...>`: it compares the declared chrome against the emitted prompts and returns `chrome verdict: READY` or `NOT READY`, exit 0 or 1. It gates four kinds — menu entries, app title, user-info chrome, and the layout block. Declared search bars, theme toggles, notification badges and global command buttons stay ungated because their blueprint form is free prose; they are a disclosed blind spot until the blueprint schema makes them mechanically comparable, and they remain this section's responsibility alone.

Pass the emitted **prompt package**, not the run document that quotes it. A run journal narrates completed work, and narration names the same elements an instruction does — the LoanDesk build-log row listing all three menu entries as `added` is from the very run where the prompts dropped them.

**Emit the chrome batch in this canonical form.** It is the only shape the gate reads:

```text
CHROME BATCH: Menu block (the TopMenu layout's navigation web block)
  menu link: "Catalogue" -> Catalogue
  menu link: "My loans" -> MyLoans
  menu link: "Manage items" -> ManageItems
  app title: "LoanDesk"
  user info: "User profile summary"
```

A `CHROME BATCH:` header opens the block; the contiguous `menu link:` / `menu entry:` / `app title:` / `user info:` / `layout:` lines below it are its directives, and the first line that is neither blank nor a directive closes it. Labels are compared whole after normalising case and punctuation, so `My loans` matches `MyLoans` and nothing matches a substring of another label. The layout block is separately evidenced by the `Layout: <block>` assignment the screen prompts already carry.

**A `menu link` needs a real destination, exactly one of them, and the right one.**

- `-> <screen>`, `-> TODO`, `-> TBD - decide`, `-> ScreenName` and their relatives are the template rather than an answer and count for nothing. The rules are closed sets, and they come in two kinds that behave differently. **Structural** — bracketed text, punctuation only, empty — is never overridable, because no screen can be named `<screen>` or `...`. **Lexical** — a leading placeholder word, or a name for the *kind* of thing wanted — stands down when that entry's own source declares the destination as its exact target, because `Pending Approvals` is a placeholder-shaped string *and* an ordinary screen and nothing inside the string tells you which. So `Pending Approvals`, `Unknown Items` and `Decide Later` pass when `menu[].target` declares them, and the identical strings are still refused with no declared target behind them or against one they do not match. The vouching is per entry: one entry legitimately pointing at `Pending Approvals` does not license that destination for another entry beside it.
- One label gets one destination across the whole prompt package. Wiring the same entry to two different screens has not decided anything, and a correct directive must not launder an incorrect one sitting beside it.
- When the chrome source declares where the entry points — `screen-inventory.json` carries `menu[].target`, the per-screen blueprints do not — the destination must match that target, compared the same whole-label way. A batch that names all three entries and wires them to the wrong screens is a wrong menu, not a covered one, and the report says so: `declared target "My Loans", wired to catalogue`.
- Two sources declaring **different** targets for one label is a failure here, not a question deferred elsewhere. The cross-blueprint report cannot settle it: inventory targets never enter the blueprints, so that pass sees only blueprint label order and never the disagreement.

**Prose is never evidence, however well written.** `In Common UI Flow, edit Menu and add links to Catalogue ...` describes exactly the right change and still reports `NOT READY` — emit the block instead. That is a deliberate trade, made after three rounds of adversarial review each broke a matcher that tried to recognise instructions in English: a vocabulary anchor passed `App chrome: Catalogue, My loans, Manage items`; a base-form action token passed `The navigation menu will add links ...`; a clause-initial rule passed `... will first add links ...` and refused `You must add menu links ...`; and a label-overlap let `Update navigation for Loan entries ...` count the word inside its own label as the destination. Each round closed its own probes and the next found more. A canonical form has no grammar surface to probe, and this skill authors the prompts, so the cost is an emission rule rather than a parser.

**Every declared element is scored — there is no platform-default exemption.** An earlier version exempted user-info chrome that a menu-bearing layout was assumed to supply. The inference was lexical rather than semantic: `Login history shortcut` and `Sign out control` were both exempted, while ODC Screens proves only that `LayoutTopMenu`'s `Header` contains sign-in logic. The app title is scored for the same reason — `LayoutTopMenu`'s `Title` placeholder reserves space for a title rather than filling one, so a document heading containing the app name proves nothing.

There is deliberately no flag that turns the gate off for a recorded deferral. The run that motivated it (LoanDesk, 2026-08-12) also believed it had handled chrome; when chrome is genuinely deferred, do not gate the blueprint that declares it.

## Four-Part Section Contract

Every visual-source section must include:

### VISUAL LAYOUT

Describe the widget tree, blocks, placeholders, order, style classes, and important visual constraints. Name the OutSystems UI block or standard widget selected by the Block Mapping Gate.

### DATA FLOW

For every Expression, image, media URL, option, selected value, repeated item, or displayed attribute, state where the data comes from. Use entity/attribute, Aggregate, Data Action, input parameter, local variable, static entity list, or mapped option list terms.

Do not leave DATA FLOW thinner than VISUAL LAYOUT when the section displays dynamic information. Thin data-flow instructions cause static hardcoded UI.

### FUNCTIONAL BEHAVIOR

Describe what the section does in user terms: display-only, filter, select, navigate, upload, save, refresh, validate, confirm, or show feedback.

Every clickable element must have a target behavior. Buttons need an `OnClick` action or an explicitly named action to create.

### PRESENTATION ORDER

List ordered content such as cards, columns, rows, status steps, nav items, tabs, and timeline items.

## Data-Flow Parity Gate

Before delivering a prompt, compare VISUAL LAYOUT against DATA FLOW:

- every Expression has a producer
- every repeated row/card/list item has a source-like input
- every Table, List, Gallery, Carousel, Dropdown, Data Grid, Lightbox Image, Video, Search, or media widget has its `Source`, `OptionsList`, URL, value, or equivalent source-like input named
- every selected value or input value has a variable
- every empty state, loading state, and error state has a condition or review note

Use producer before consumer ordering. If the producer does not exist, create or verify the producer in an earlier prompt block.

## Gotcha Review

Run a visual-source gotcha review when the source contains the matching pattern:

- theme class collisions (`field-tested hardening guidance`): avoid unprefixed `main-content`, `sidebar`, `header`, `content`, and `footer`
- SVG icon color behavior (`field-tested review guidance`): prefer verified Icon widgets; review raw SVG color behavior before hardening
- font icon classes (`field-tested hardening guidance`): do not emit `ph ph-*` unless the target dependency is verified
- Table/List/data-bound widget source (`field-tested hardening guidance`): never deliver empty `Source`, `OptionsList`, URL, or value bindings
- interactive widgets inside Link or anchor regions (`field-tested review guidance`): avoid putting Upload, Input, Form, or Button inside a Link slot — the rendered Link wraps the widget and intercepts its clicks. The affirmative case: an anchor IS the correct slot wrapper when the slot's content is itself the navigation target, such as a clickable card or a list row that drills into a detail screen.
- duplicate primary actions (`field-tested review guidance`): avoid creating a second Button when source HTML already emits a button for the same action
- source HTML display toggles (`field-tested review guidance`): convert `display:none`/active-section toggles into explicit ODC state and Conditional Display guidance — but only where the toggled section IS the screen's main content. **Transient overlays are the exception: modals, toasts, popovers, and mobile slide-in sidebars keep their `display:none` and get real show/hide wiring to the equivalent OutSystems UI widget.** Stripping the hiding CSS from an overlay renders it permanently open.
- `<table>` tags in source markup (`field-tested review guidance`): `HtmlToWidgets` translates table tags to divs, so a `<table>` carrying no explicit `display:table` / `display:table-row` / `display:table-cell` rules stacks vertically instead of forming a grid. Carry the explicit display rules, or map to a verified Table/List widget instead.
- `<nav>` in source markup (`field-tested review guidance`): `<nav>` does not survive widget translation, so a `.sidebar nav a` selector silently stops matching after the build. Scope link-color selectors to `.sidebar a` directly, and do not nest semantic elements inside the brand or nav area.

Keep gotcha entries as review or hardening guidance according to their evidence boundary. Do not promote field-only notes to current ODC product-contract authority.

External field evidence: an internal OutSystems project (adopted 2026-08-14, round 2); field-observed over the Mentor MCP, not in official docs.

Capture the gotcha review outcomes in the enriched blueprint so downstream
prompt generation and manual review can see which risks were already checked.

### Icon Coverage Checklist

For visual sources, enumerate icon locations as first-class source content
before prompt emission. Do not summarize them as "some icons". Check:

- sidebar nav
- sidebar bottom utility
- top header or search
- KPI or stat cards
- list or table rows
- action chips and links
- agenda or appointment cards
- status badges or pills
- buttons
- card or table headers
- empty states

Capture the expected icon count and location list in the enriched blueprint and
carry material gaps into the Prompt Coverage Audit. Prefer verified OutSystems
UI Icon widgets where possible. If an icon remains a raw SVG or approximation,
mark it as review guidance unless current ODC docs, catalog facts, or tenant
observation confirms the exact rendering path.

### Lucide To Phosphor Mapping

When source material comes from Figma React, shadcn, or another Lucide-based
source, translate source icons to OutSystems/Phosphor intent before prompt
emission; do not add Lucide as a second icon library.

Common mappings:

| Source icon | OMI icon intent |
| --- | --- |
| `lucide-layout-dashboard` | `squares-four` |
| `lucide-users` | `users` |
| `lucide-user` | `user` |
| `lucide-user-plus` | `user-plus` |
| `lucide-briefcase` | `briefcase` |
| `lucide-calendar` | `calendar-blank` |
| `lucide-clock` | `clock` |
| `lucide-bell` | `bell` |
| `lucide-circle-alert` | `warning-circle` |
| `lucide-info` | `info` |
| `lucide-chart-column` | `chart-bar` |
| `lucide-chart-line` | `chart-line` |
| `lucide-trending-up` | `trend-up` |
| `lucide-trending-down` | `trend-down` |
| `lucide-eye` | `eye` |
| `lucide-search` | `magnifying-glass` |
| `lucide-mail` | `envelope` |
| `lucide-phone` | `phone` |
| `lucide-video` | `video-camera` |
| `lucide-settings` | `gear` |
| `lucide-log-out` | `sign-out` |
| `lucide-plus` | `plus` |
| `lucide-arrow-right` | `arrow-right` |
| `lucide-chevron-right` | `caret-right` |
| `lucide-message-circle` | `chat-circle` |
| `lucide-message-square` | `chats` |
| `lucide-file-text` | `file-text` |
| `lucide-house` | `house` |
| `lucide-target` | `target` |
| `lucide-handshake` | `handshake` |

Phosphor exposes weight modifiers — `ph-thin`, `ph-bold`, `ph-fill`. When the
source icon's stroke weight is visually load-bearing, name the matching modifier
in the prompt rather than accepting the default weight.

External field evidence: an internal OutSystems project (adopted 2026-08-14, round 2); field-observed over the Mentor MCP, not in official docs.

Record the mapping in `icon_mapping` with the source icon name, the bare
Phosphor icon name, intended location, and any review note. Use a
bare Phosphor icon name for OutSystems UI Icon widgets, not `ph-*` or
`ph ph-*` class syntax.

### SPA Shell Fidelity Review

When a visual source behaves like a single-page shell or HTML mockup with
JavaScript-initialized state, check these silent fidelity risks before prompt
emission:

- header or breadcrumb title: if source JavaScript updates a `.current`,
  breadcrumb, or page-title element, set the per-screen title explicitly from
  the title map, nav label, or screen `h1`.
- table header color and table header contrast: preserve source table header
  color, including faint-alpha backgrounds. Treat faint-alpha headers as light
  surfaces that need dark text unless source evidence says otherwise.
- styled upload drop-zone: keep the styled drop-zone container, instruction
  copy, border, and icon. Place the native Upload widget inside a
  `<div data-widget-slot="slot">`; do not replace the whole drop-zone with a
  bare Upload widget.
- colored tile icons: when raw SVG is still used inside dark, gradient, or
  colored tiles, review explicit `fill` and `stroke` values instead of relying
  on `currentColor` or descendant CSS. Prefer verified Icon widgets when
  possible.

Capture these checks in the enriched blueprint review notes and summarize any
remaining risk in the Prompt Coverage Audit. Keep raw SVG color behavior as a
review note when the source depends on browser-inherited icon color.

## Portable Source Extraction Discipline

For large visual sources, keep source extraction portable and file-first:

- keep large source artifacts on disk and reference paths instead of pasting
  full payloads into the prompt
- read child frames or sections in small batches when the source is too large
  for one reliable extraction pass
- extract colors from rendered code or style definitions when design-token
  APIs are unavailable or empty
- skip decorative vectors, masks, and short divider lines unless they are
  visible content or meaningful separators
- record uncertainty for approximate colors, spacing, icon names, and hidden
  states instead of converting guesses into confirmed requirements

Do not mention Claude-only cache paths or require a specific Figma plugin.

## Block Primitive Naming Parity

When a source element maps to a known OutSystems UI primitive, always
name the selected OutSystems UI primitive in both the visual description and
the block/review hint. This includes `ProgressBar`, `ProgressCircle`, `Counter`, `Tabs`,
`Carousel`, `Gallery`, `Accordion`, `Wizard`, `Tag`, and `Badge`.

Do not describe a known primitive only as raw HTML, SVG, or generic Containers.
For example, a progress indicator should not be only "a div with height 8px";
the prompt must say `ProgressBar` when that is the selected pattern. If the
exact pattern is not supported for paste-ready generation, keep the primitive
selection as a review note and label the evidence boundary.

## Do Not Migrate Blindly

### No automatic app_create

OMI may guide a shell-first path, but it must not call `app_create` automatically. Shell creation requires explicit approval for the readable app name, environment context when needed, and exact action. Do not turn that into extra ceremony when the user intent is already clear. Verify and echo the canonical id once known. If the user wants no-shell new-app generation, route to Mentor Web guidance.

### No mandatory publish

OMI must not say publish is mandatory. Use the Post-Mentor Preservation Decision Gate after approved Mentor execution. Require explicit publish approval by default, but do not ask twice when the user already clearly approved implementation plus publish to a specific environment.

### Portable file-first artifacts

Large source artifacts and Mentor events should stay on disk as portable file-first artifacts and be referenced by path. Use user-approved or project-local paths. Do not use Claude-only cache paths or other client-private cache paths in portable OMI guidance.

### Do not copy the full spec.json schema

OMI owns the enriched blueprint plus the condensed Visual-Source UI Prompt
Packet, not the full `outsystems-design-to-app` `spec.json` schema. If the
user provides an existing `spec.json`, treat it as an input artifact and map it
through the enriched blueprint first, then the smaller OMI packet before prompt
generation.

## Post-Mentor Preservation Decision Gate

After an approved Mentor execution succeeds, stop and ask which preservation route the user wants:

- publish to a specific environment, requiring explicit current approval before `publish_start` unless the current request already clearly approved implementation plus publish to that exact environment
- stop with the newest Mentor session id/token details and session-expiry risk recorded
- create a prompt-only handoff for manual ODC Studio review

No mandatory publish. No implicit publish. No duplicate publish confirmation when the user already clearly approved publish to a specific environment. No production promotion from this skill.

## Output Addition For Visual-Source UI Prompts

For supported web UI generation, complete the Visual-Source UI Prompt Packet
after the enriched blueprint has been prepared or validated, but do not add
`### Visual-Source UI Prompt Packet` as a mandatory extra visible section ahead
of the prompt. Treat the packet as blueprint-derived preparation or as a
condensed reviewer summary that can be folded into `### Prompt Coverage Audit`
or `### Studio-Native UI Spec` when that improves reviewability.

Keep the visible output contract as:

1. `### Mentor Studio Prompt`
2. `### Prompt Coverage Audit`
3. `### Studio-Native UI Spec`
4. `### Evidence Status`
