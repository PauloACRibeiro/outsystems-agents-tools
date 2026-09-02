---
name: outsystems-ui-design
description: Use when the user brings a wireframe screenshot, screen sketch, or screen-design ask and wants to iterate on the design interactively before anything is built — an interactive wireframe-to-blueprint loop that maps every visual region to a named OutSystems UI web block, renders a local HTML preview per round, and emits a validated enriched blueprint.json on approval. Route to outsystems-design-to-app (if that skill is installed — it is not part of the colleague sprint-loop pack) for a one-shot, non-interactive build straight from a design source (Figma URL, image, HTML mockup). Route to outsystems-mentor-implementation instead for Mentor/tenant execution of an already-approved blueprint.
compatibility: Agent-neutral (Codex and Claude Code). Python 3.7+ stdlib only. No MCP server required — outsystems-tech-content and a public knowledge provider (workspace-knowledge-cc or outsystems-public-knowledge) are optional enrichment only.
allowed-tools: AskUserQuestion, Bash, Read, Write, Edit
---

# OutSystems UI Design — Interactive Wireframe-to-Blueprint Loop

Turn one wireframe screenshot into an approved, validated `blueprint.json` through a
short interactive design loop. Every visual region ends up mapped to a **named
OutSystems UI web block** — never a vague approximation — and the user sees an HTML
preview and a compact pattern tree every round until they approve. The emitted
blueprint is the handoff contract consumed by `outsystems-mentor-implementation`
(OMI); this skill designs, it never builds.

This skill is fully local. It has **no OutSystems MCP tools** and performs **no
tenant operation of any kind** — no app creation, no Mentor session, no publish, no
deploy. Everything it produces is files on disk plus chat.

## Target product: OutSystems Developer Cloud (ODC)

**Every name this skill emits is an ODC name.** The layouts, widgets, blocks and
patterns in `references/` describe ODC's OutSystems UI framework, and a blueprint
is built by ODC Mentor against an ODC tenant. OutSystems 11 is **not** a target:
this skill has no O11 mode, and there is no `target_platform` switch to set.

Two consequences worth stating, because leaving them unstated is what caused the
2026-08-09 live run's most expensive defect — a screen built correctly to a plan
that named the wrong product's widget:

- **O11-only names are validator errors, not alternatives.** `validate_blueprint.py`
  carries an `O11_ONLY_BLOCKS` detector map; naming one in a region fails the
  blueprint with a message naming the ODC replacement. The map is deliberately
  small — a name only enters it once it is documented as O11-only *and* absent
  from `references/built-in-widgets.md`, the generated ODC runtime contract.
- **Shared names are not O11 names.** Many widgets exist in both products —
  `TableRecords`, `Dropdown`, `ListItem`, `ListItemAction`, `Form`, `Input`.
  A name appearing in O11 documentation is **not** evidence it is wrong for ODC.
  Check `references/built-in-widgets.md` before treating any name as foreign;
  that file is generated from OutSystems' own ODC widget runtime, so presence
  there settles the question.
- **When that file is absent, say so — do not fall back to guessing.** It is
  excluded from the public distribution on licensing grounds, so on most
  installs it will not be there. That does not license an inference from O11
  documentation; it removes the only thing that could settle one. Two honest
  moves, in order: offer the one-time regeneration in
  `references/built-in-widgets-regeneration.md` if the operator has OutSystems
  org access, and otherwise treat the product question as **unverified** and
  name it as such in the output. The detector map still fires — `ListRecords`
  is grounded independently — but nothing may be *added* to it, and no name may
  be called foreign, on the strength of an O11 doc alone. This is a real
  limitation of the public pack, not a gap to paper over: four findings in the
  2026-08-09 run were wrong precisely because that inference was made without
  this file to check against.

## Scope guards (hard limits, not preferences)

- **OutSystems UI web patterns only.** Mobile patterns are out of scope; if the
  wireframe is clearly a native-mobile design, say so and stop.
- **One screen per run.** A multi-screen app is multiple runs, each feeding its own
  blueprint. Do not attempt to design two screens in one loop.
- **No logic or data design** beyond naming data producers in the blueprint's
  `entities` and `screens` sections. Do not design server actions, aggregates,
  integrations, or business rules.
  **Boundary contract (decided 2026-07-29, maintainer + cross-agent review AH-2026-07-29-005):
  this guard governs what the skill DESIGNS and EMITS** — the conversation, the
  pattern tree, and `blueprint.json`. The bundled `references/` may state
  implementation facts about blocks (event payloads, binding requirements,
  handler expectations) as **reference-only context** so mappings and acceptance
  checklists stay truthful; never copy such facts into a blueprint as designed
  logic, and never elaborate them into action/aggregate designs in chat. What
  the bundle may NOT contain is **executable external build/mutation syntax** —
  modelAPI C#, Mentor/MCP automation calls. Studio-native node/action names and
  pseudocode (`AssignNode`, `RefreshDataNode`, `ExecuteClientActionNode`,
  `<TabsBlock>.SetActiveTab(...)`) ARE allowed when they are reference-only
  implementation facts. Enforced by the banned-term suite.
- **No tenant mutation of any kind.** This skill has no OutSystems MCP tools; do not
  reach for any tenant tool from another skill mid-loop.

## Hard gates (mandatory rules — violating any of these is a defect)

1. **Layout choice first.** Before any region mapping, commit to exactly one layout
   block from ODC's `Layouts` flow: `LayoutSideMenu`, `LayoutTopMenu`, `LayoutBlank`,
   `LayoutBase` (landing pages — Header + MainContent, menu on top), or
   `LayoutBaseSection` (a section container ODC's docs describe as nesting *inside*
   `LayoutBase`; pick it only when the screen genuinely is that section). Never
   combine layouts; never map regions before the layout is chosen.
2. **Skeleton with zero `Container` nodes.** The structural skeleton is built only
   from the `Columns*` and `Card` families. A generic `Container` in the skeleton is
   a validator failure, not a style choice.
3. **Block Mapping Gate.** Every visual region in the wireframe maps to a named
   OutSystems UI block, or is explicitly flagged — either as ambiguous (with
   candidates) or as `custom_block_needed`. On an existing app there is a third
   settled state: a region may instead **bind an app-local block that already
   exists**, via `reuse` (see "The existing-asset channel" in Step 4). Silence is
   not an option: a region with no mapping, no binding and no flag fails the
   gate. **One region, one bare block name.**
   `outsystems_hints.block` is a single bare catalog token (`"Card"`,
   `"AdvancedHtml"`) — **the validator hard-fails any space, qualifier, or
   punctuation in it**. Property/wrapper qualifiers (`UsePadding`, `Tag=p`)
   belong in the region description or the `content[]` element descriptors,
   never in the block hint — and when a property is named there, write it in
   **FULL PATH form** (`Card.UsePadding`, `Tabs.OnTabChange.ActiveTab`; see
   `references/ui-reference.md` § FULL PATH naming — the format modelAPI
   patches use downstream). It is likewise never a comma- or semicolon-joined
   list of several distinct widgets standing in for several regions (e.g.
   `"Card with Form, Columns2, Input, Dropdown, ..., Button"`). When a
   wireframe area contains multiple distinct widgets, split it
   into sibling regions or a `type: group` with one `items[]` entry per widget —
   never collapse them into one region's block string. OMI consumes
   `outsystems_hints.block` as a bare pattern name (see
   `odc-visual-source-ui-discipline.md`'s Tailwind-To-OutSystems Normalization);
   a compound string breaks that downstream contract even when the local
   validator still passes it.
4. **Ambiguity is flagged with the top-2 candidate patterns**, presented as a
   labeled numbered question for the user (`Q1` / `Q1a` / `Q1b` — see the question-label
   protocol in Step 3). Never silently pick one interpretation of an ambiguous
   region, and never guess which question an unmatched answer meant.
5. **Per-round diff statements only.** From round 2 of the refinement loop onward,
   state only *what changed* since the previous round. Never re-describe the whole
   screen — a full re-description buries the diff the user needs to react to.

**User-visible wording is grounded, not invented.** Every string a user reads —
chrome labels in `app_chrome`, headings, button text, empty-state and error
lines — is named from the ODC taxonomy and written to the Product Language and
Style Guide, per `references/copy-grounding.md`, and stays consistent with how
this app already phrases the same action. Deliberate divergence from an
established phrasing is allowed and is **stated in the round's diff**; silent
divergence is not. This is a constraint on generation, not advice to write
carefully — `scripts/check_copy.py` is the mechanical half of it.

## Working directory contract

Each run creates one per-screen directory under the **user's current project root**
(these are user-visible deliverables, not a hidden cache):

```
design/<screen-slug>/
  wireframe.<ext>          # copy of the input screenshot — or, in generated-mock
                           # intake, wireframe.html, a verbatim copy of preview.html
  wireframe.md             # the design-source slot INSTEAD of wireframe.<ext> when
                           # the source is a live URL or local HTML: source URL,
                           # observed anatomy, measured token table
  pattern-tree.md          # current round's tree — overwritten every round
  preview.html             # current round's HTML preview — overwritten every round
  blueprint.json           # emitted only at approval (Step 4)
  validation-report.txt    # validator output for the emitted blueprint
  alternatives.md          # only when the optional pre-loop alternatives round ran
  alternatives/<slug>/preview.html   # throwaway; never emits a blueprint
```

`<screen-slug>` is the kebab-cased screen name (e.g. `work-queue-overview`).
`pattern-tree.md` and `preview.html` always hold the *current* round only; history
lives in the chat transcript, not in versioned files.

**Operator override.** `design/` is only the default parent. When the user (or the
run's kickoff instructions) names a different output directory, use it verbatim with
the same per-screen file set — no permission friction, no dual-writing to `design/`.
Record the effective directory once at intake; every later path in the run derives
from it.

**`blueprint.json` — never a YAML file — is the canonical emitted artifact.** OMI's
canonical asset format is JSON and this skill is stdlib-only (no YAML parser), so
JSON is the only correct emission. Do not emit, mention, or accept a YAML variant of
the blueprint.

## Reference loading (two-tier)

The bundled library under `references/` is the skill's pattern authority. Load in two
tiers — a small default set upfront, everything else strictly on demand.

**Symlinked installs:** this skill is installed elsewhere as a symlink (e.g.
`~/.agents/skills/outsystems-ui-design`). If a shell listing command reports the
`references/` or `scripts/` directory as empty right after `cd`-ing or globbing
into the installed path, that is very likely a `find`/glob tool not following
the symlink by default (a Phase 4 Codex run hit exactly this) — retry with a
symlink-following listing (`ls -la`, `find -L`, or a direct path read) before
concluding an asset is missing. It is not a sign the skill failed to install.

**Tier 1 — load at Step 1, every run:**

| File | Why upfront |
|---|---|
| `references/ui-reference.md` | Master pattern index — the vocabulary for all mapping |
| `references/layouts.md` | The layout-first gate depends on it |
| `references/styles-and-utilities.md` | Spacing/utility classes used throughout the skeleton |
| `references/design-tokens.md` | Seeds `design_system` from wireframe colors / brand input |
| `references/patterns/navigation.md` | Menus, breadcrumbs, tabs — present on nearly every screen |
| `references/patterns/content.md` | Cards, lists, tables — the default region fillers |
| `references/patterns/numbers.md` | Counters, badges, progress — common on most archetypes |
| `references/patterns/adaptive.md` | Responsive/column behavior for the skeleton |
| `references/structural-skeleton.md` | Grid/card skeleton method + block-inventory commitment — run between region mapping and blueprint emission |

**Tier 2 — load only when the trigger appears:**

| Trigger in the wireframe or conversation | Load |
|---|---|
| Any chart (bar, line, pie, donut, sparkline…) | `references/charts.md` |
| Any map region | `references/maps.md` |
| Table region needing inline cell editing, column grouping, or virtual scrolling over a large dataset | `references/data-grid.md` — the OutSystems Data Grid. A **separate Forge component installed per tenant**, so confirm availability with the user; where it is not installed, `TableRecords` stays correct |
| Carousel, Sidebar, DatePicker, Dropdown | `references/patterns/interaction.md` |
| AlignCenter, Separator, gesture affordances | `references/patterns/utilities.md` |
| Need exact block argument/placeholder names without full category detail | `references/blocks-index.md` — one-page args/placeholders/events index, and the first stop for any "what is it called / does one exist" lookup; drop into the matching `patterns/<category>.md` only once the question turns to behavior, composition or events (its `## Lookup order` states the two steps) |
| Verifying a built-in widget's exact properties (Input, Dropdown, TableRecords…) | `references/built-in-widgets.md` — generated runtime contract. **Not included in the public distribution**; if it is absent, generate it once per `references/built-in-widgets-regeneration.md`, and until then say a property list is unverified rather than guessing one |
| Screen strongly resembles a stock scaffold; designing app-chrome nav reachability | `references/screen-templates.md` |
| Proposing any **user-visible string** — heading, button label, menu entry, field label, placeholder, empty/loading/error line, toast | `references/copy-grounding.md` — the OutSystems Product Language and the ODC taxonomy decide product wording; we do not invent it. Its two sources are **not included in the public distribution**; where they are absent the rule degrades to sibling consistency and the run says once that copy is ungrounded |
| A region needs behavior beyond a pattern's inputs — before flagging `custom_block_needed` | `references/extensibility.md` |
| The design source is a **live URL or a local HTML file** rather than an image | `references/live-source-inspection.md` — how to drive a mockup SPA without misreading it, and the computed-style token pull the live-URL intake mode depends on |
| The screen's direction is genuinely open — a rough sketch that commits to no layout, a close-call archetype the user could not settle, or an explicit ask to see options before converging | `references/divergent-alternatives.md` — the optional pre-loop alternatives round. **Not** for a wireframe that already commits to a layout |
| Writing `screens[].render_gate` at Step 4 — any disclosure about what the screen must SHOW, or any requirement id the blueprint cites | `references/render-gate-assertions.md` — the assertion contract, the two discharge rules, and the worked case the rule comes from |
| Screen archetype confirmed at Step 1 | The matching archetype guide (below) |
| A cross-cutting design concern surfaces | The matching cross-cutting guide (below) |

**Screen guides — 19 files under `references/screen-guides/`.** Load the one
archetype guide matching the Step 1 confirmation (14 archetypes): `calendar`,
`dashboard`, `detail-view`, `edit-form`, `gallery-grid`, `inbox-notifications`,
`instructional`, `kanban`, `list-table`, `map-view`, `master-detail`, `settings`,
`timeline`, `wizard`. Load a cross-cutting guide (5 files) only when its concern is
actually in play: `design-system` (theming/token decisions), `component-selection`
(close-call pattern choices), `states-and-feedback` (empty/loading/error states),
`reusable-blocks` (a region repeats and should become a web block), `app-type-styling`
(overall app character: back-office vs. portal vs. consumer).

**`instructional` covers the screen that explains rather than operates** — a
getting-started page, a launcher, a reference card. It exists because Phase 3 found the
archetype list had no slot for one: two of nine screens in a real app were forced to load
a guide describing a different kind of screen and discard most of it (GAP-9). **A
launcher is not a `dashboard`** (it has no metrics, and `dashboard.md` will try to invent
some), and **a page of visible steps is not a `wizard`** (`Wizard` means *content hidden
behind Next*).

⚠️ **The archetype guides are the least trustworthy part of this bundle.** They describe
what a screen of that kind *often* has — they do **not** license adding it. When a guide's
anatomy and the wireframe disagree, **the wireframe wins, every time.** Step 1's
confirmation gate exists precisely because a wrong archetype poisons everything downstream;
if none of the 14 fits, say so and ask rather than forcing the closest one.

Do not preload Tier 2 files "just in case" — the loop stays fast because context
stays small.

## Workflow — five steps, all local

### Step 1 — Intake

The user provides a wireframe screenshot path, plus optional context: app name,
existing entity names, existing theme names, brand color. Then:

1. Copy the screenshot to `design/<screen-slug>/wireframe.<ext>`.
2. Read the image. If it is unreadable or too ambiguous to interpret, follow the
   error-handling rule below (ask for a better crop) — do not push on.
3. Load the Tier 1 references.
4. State a **high-level screen-archetype read** — one of the 14 archetypes (dashboard,
   list-table, edit-form, …) — plus a one-line rationale, and **confirm with the user
   before going deeper**. This confirmation gates Step 2; a wrong archetype poisons
   every downstream mapping.

**Inventory-fed entry** (greenfield trial G-09): when a screen-inventory brief
exists for this screen (`outsystems-screen-inventory`'s `--brief` output, read
from the app's `screen-inventory.json`), the brief is the arriving context, not
a competing opinion. The archetype arrives as the inventory's answer — step 4
above **confirms** it rather than re-deriving it, and a mismatch with the
wireframe is raised as a finding, never silently re-decided. The chrome arrives
pre-translated — `layout_block` and `app_title` verbatim, the menu already in
the blueprint's `{label, active}` shape — and is **not re-decided here** (hard
gate 1 is satisfied by the inventory's decision). The screen's bindings,
behaviour, and navigation contract — including what it `accepts` and who
arrives carrying it — arrive with the brief. The wireframe still wins on visual
anatomy, archetype guides included: the brief pre-answers what the screen *is*,
not what it looks like.

**Generated-mock intake.** Step 1 above assumes an input screenshot. When **no
wireframe exists** and a screen-inventory brief is present for this screen, the
agent MAY generate a self-contained HTML mock and use it as the design source
for the run. Both halves of that condition are required: the brief supplies the
archetype, chrome, bindings and behaviour the mock would otherwise be inventing,
and **a wireframe the user brings always wins** — with one in hand this mode is
not available. Field-proven on the 2026-08-25 restaurant-app run (4 screens),
where it was improvised step by step; this makes it a sanctioned path with a
stated contract.

What the mode is, concretely:

1. Generate the mock and write it as `preview.html` in the run directory, built
   on `templates/preview-shell.html` like any other round's preview.
2. That file is then **copied verbatim to `wireframe.html`** — the design-source
   slot the rest of the workflow reads. Verbatim means byte-identical: the two
   files are the same artifact in two roles, not two drafts.
3. Record the inversion in `evidence_boundary.grounding_notes` at Step 4 — that
   the design source was generated by this run rather than supplied, and that
   the brief is what grounded it.
4. Enter the refinement loop unchanged: **the mock is round 1**, the user reacts
   to it in plain language exactly as they would to a preview built from a
   screenshot, and the loop still exits only on explicit approval. The user
   still approves; nothing here shortens that.

What the mode may not do — each of these is a defect, not a judgement call:

- It **does not skip the archetype confirmation** of step 4 above. The brief's
  archetype is still confirmed with the user before Step 2.
- It **does not skip the pattern tree.** Every round still writes and prints one
  (Step 3), mock-sourced or not.
- The mock **never counts as user evidence.** It is this run's own output; citing
  it as something the user provided, or as grounding for a mapping the brief does
  not carry, is a grounding lie. Say "generated from the inventory brief".

**Live-URL / HTML source mode.** A sibling intake path to generated-mock, for the
opposite situation: the user *does* bring a design source, but it is a **live URL**
(a hosted mockup, usually a single-page app) or a local HTML file rather than an
image. Field-proven on the 2026-08-27 restaurant-app-v2 run, where every step of
it was improvised because the contract above assumes a screenshot file. Read
`references/live-source-inspection.md` before touching the page — a mockup SPA
renders inside an iframe with a JS-written DOM, so text reads come back empty and
pixel coordinates misclick.

**The mode runs in this order**, before Step 2: (1) read the page and select
which screen this run is designing; (2) pull the design tokens; (3) settle any
scope-vs-visual conflict; (4) write `wireframe.md`; (5) confirm the archetype
with the user as step 4 of Step 1 requires. Conflict before archetype, because a
screen that the conflict round rejects is a screen with no archetype to confirm.
**The live page is not round 1** — unlike generated-mock intake, where the mock
*is* round 1, a live source is a source: round 1 is the first `preview.html` this
run authors from it, exactly as it would be from a screenshot.

There is no image to copy, so the design-source slot is a written record:
**`design/<screen-slug>/wireframe.md`**, holding three things —

1. **The source URL** (or file path) and the date it was read.
2. **The observed anatomy** of this screen, read out of the rendered DOM rather
   than transcribed from a screenshot by eye.
3. **The measured token table** — brand/accent colour, corner radius, surface and
   input backgrounds, elevation, spacing rhythm, and **type per role** (family,
   size, weight, letter-spacing and colour for the display heading, the section
   label, body copy and numeric text) — each with the selector it was read from
   and the value exactly as measured.

A screenshot is still a useful reading aid even though no image is required:
keep any capture beside the record as `wireframe-<state>.png` and reference it
from `wireframe.md`, so a later reader sees what was looked at. `wireframe.md`,
not the capture, is the design-source slot.

**Extracting those tokens from computed style is a required step of this mode,
not optional polish.** A live source is the one design input that carries its own
exact values, and they seed the blueprint's `design_system` (and `primary_color`)
directly. Skipping the pull and eyeballing colours or type instead throws away the
only advantage the source has over a screenshot. The recipe is in
`references/live-source-inspection.md`; the values land in `wireframe.md` first so
every token in `design_system` traces to something measured.

**The table comes before the prescription.** Nothing that prescribes a visual
value — a `design_system` token, a region's `typography` descriptor, a restyle
prompt aimed at an already-built screen, which `outsystems-mentor-implementation`
writes later from this run's table — is written for a measured source until the
table exists, and each such value **cites the row it came from**. A prescription
the table does not cover was read off an image by eye, which is the failure this
mode exists to prevent; the trap note is in
`references/live-source-inspection.md`. On the wireframe-absent path below the
table is the page-level one measured from the screens that *do* exist: a row
carried in from a sibling names that sibling's selector and is disclosed under
**EXTRAPOLATED**, never presented as measured on this screen.

Four situations this mode has to answer, three met on the 2026-08-27 v2 run and
the fourth on its 2026-08-30 fidelity pass:

- **A multi-screen mockup.** One page routinely holds every screen of the app,
  while this skill is **one screen per run** (scope guard). Before Step 2, select
  the region or state that is *this run's* screen — a route, a tab, a modal, a
  section — and **record which** in `wireframe.md`: the route or selector used and
  the interaction that reached it, so a later run can reproduce the same view. The
  other screens on that page belong to other runs; do not design them here.
- **The wireframe-absent screen.** A screen in the inventory may have **no mockup
  surface** anywhere on the page. That is not an error and not a reason to stop:
  the run proceeds **EXTRAPOLATED** — `wireframe.md` says so in those terms, names
  what the extrapolation is built from (the inventory brief, the tokens shared with
  the screens that *do* exist, the closest sibling screen), and the same disclosure
  is carried into `evidence_boundary.grounding_notes` at Step 4. Two of seven v2
  screens took this path. Extrapolated anatomy is never presented as observed.
- **A scope-vs-visual conflict.** The source may depict a materially different
  product than the approved PRD — the v2 mockup carried AI assistant panels,
  credentials screens and a multi-restaurant switcher the PRD had no room for. The
  rule is **adopt visually, reject scope**: the mockup is authority on visual
  language — with the deliberate-deviation exception below — and the PRD is
  authority on what the product contains. Run one explicit
  **decision round** that lists each conflict with a recommendation, then record
  the outcome where it outlives the chat. Two different records, because two
  different owners: **this run's own output** carries the decision and every
  adopted deviation — `wireframe.md`, the round's what-changed statement, and
  `evidence_boundary.grounding_notes` at Step 4 — while a conflict implying a
  change upstream is written up as a **proposal** naming the artifact and the
  requirement ID it touches: the PRD under `docs/specs/`, the screen list and
  chrome in `design/screen-inventory.json`. **This skill never edits either
  artifact.** An approved PRD and a validated inventory belong to their owner,
  who applies the correction after the operator approves it — the same routing as
  an inventory count, repaired upstream rather than edited to pass. The round is
  **once per app**, not once per screen —
  the mockup is page-wide, so the first run that meets the conflict settles it and
  records the decision where later runs inherit it. A conflict is **never silently
  absorbed** (adopting the extra scope) and never silently dropped (designing past
  it without saying so).
- **A deliberate deviation.** Not a scope conflict — the conflict round decides
  whether a thing ships and lets the PRD win; a deviation decides how an agreed
  element renders and lets a correctness constraint (locale, accessibility, what
  the ODC block actually does) win against the mockup on its own turf. **If the
  answer changes what the product contains it is a conflict** and takes the
  once-per-app round above; **if it changes only how an agreed element looks or
  reads it is a deviation**, settled in the round it arises. Measured on the
  2026-08-30 fidelity pass: the mockup priced items `€3.84` while the app keeps
  the pt-PT `12,50 €`, because locale correctness beats mockup fidelity.
  Deviating is allowed and is **stated in the round's what-changed statement**,
  on the same records an adopted scope decision uses; deviating silently is not.
  The rule is **symmetric** — taking the mockup's treatment over one this app had
  already established is the same decision as keeping ours over the mockup's. A
  deviation nobody can find later is indistinguishable from a region the mapping
  simply missed.

### Step 2 — Inference pass

Map every visual region to a named OutSystems UI block, in this strict order:

1. **Layout choice first**: exactly one of `LayoutSideMenu`, `LayoutTopMenu`,
   `LayoutBlank`, `LayoutBase`, `LayoutBaseSection` (hard gate 1).
2. **Structural skeleton**: `Columns*` / `Card` family only — zero `Container`
   nodes (hard gate 2).
3. **Widgets and patterns per region**, applying the Block Mapping Gate: every
   region gets a named block, an explicit ambiguity flag with its top-2 candidate
   patterns, or a `custom_block_needed` flag (hard gates 3–4). When no single block
   matches but a reasonable **composition of real primitives** does (e.g. a
   `FloatingContent` anchored to an icon `Button`, with a `Link` stack inside its
   content placeholder, standing in for a pattern the bundle has no named block
   for), prefer composing it over reaching straight for `custom_block_needed` —
   see "Compose-and-disclose" below. Reserve `custom_block_needed` for regions
   where no reasonable composition exists at all.
4. **Before nesting anything inside a named block's placeholder, confirm what
   that placeholder actually accepts** from the matching `patterns/*.md` entry.
   Visual adjacency is not composition license — e.g. `SectionIndex.Content`
   accepts only `SectionIndexItem` children; a visually-adjacent secondary link
   group (like a "view history" link below a section nav) is a **sibling**
   widget, not a child of the block it sits next to.
5. **After mapping the primary interactive controls, sweep the wireframe a
   second time for secondary text** — hint lines, character/item counts,
   disclaimers, "max file size" notes, and similar helper copy sitting beside or
   below a control. These are exactly the kind of region that's easy to skip
   while focused on inputs, dropdowns, and buttons, and each one is still a
   region the Block Mapping Gate applies to (typically `AdvancedHtml Tag="p"`).
6. **Every `Dropdown`, `RadioGroup`, or similar choice widget names its option
   source** — either `data_source.entity` when the options are clearly
   record-backed (e.g. a Department or Project picker), or an explicit
   illustrative static option list (e.g. `["Lead", "Contact", "Opportunity",
   "Account"]`) when the wireframe only shows plain labels with no obvious
   entity behind them. A bare `{"block": "Dropdown"}` with no option source
   at all leaves OMI's Data-Flow Parity Gate with nothing to bind to — treat
   this the same as the secondary-text sweep above: a mapping is not done
   until its data source is named, even if that source is only a disclosed
   placeholder list.

   **And name the option label and value, not just the source.** ODC's
   `Dropdown` widget needs **four co-dependent expressions** — `List` (the data,
   and the property is `List`, never `Source`), `Labels` and `Values` evaluated
   per option, and a `Variable` whose type matches the option value (an
   Identifier for an entity picker). A spec that names only the source leaves
   three of them for the builder to invent, and **each unresolved slot surfaces
   as its own `Invalid Expression`** — this is the measured cause of the
   2026-08-09 run's most expensive screen session, where five such errors came
   from three under-specified dropdowns while `DropdownSearch` in the same
   screen produced none. For a record-backed Dropdown, set `binds.attribute`
   to the attribute shown per option; the value is the source entity's
   identifier, so naming the entity settles it. The validator enforces this
   half. For a static option list, the disclosed list carries both.

   This is a **specification-completeness** rule, not a product-boundary one —
   `Dropdown` is a perfectly valid ODC widget. If a single well-typed option
   input suits the region better, `DropdownSearch` takes one mandatory
   `OptionsList` and has correspondingly less to leave unstated.

**Compose-and-disclose:** composing a workaround from real primitives is always
preferable to two failure modes: silently approximating with a styled
`Container` (never acceptable — see Error handling), and reflexively flagging
`custom_block_needed` the moment a clean single-block match isn't found. When you
compose, **disclose the limitation and the workaround honestly** — name what's
missing, what you built instead, and why — in the pattern tree and in the
blueprint's `evidence_boundary.review_notes` / `acceptance_checklist`. Disclosure
belongs in those places and in chat, **never as literal visible copy inside
`preview.html`** — the preview represents the actual screen a stakeholder or OMI
will look at, not a design-process document; a "disclosure:" paragraph rendered
as page content is itself a defect.

**Enrichment (optional, never a gate):** when `outsystems-tech-content` is reachable,
query it here to verify nesting rules and pattern API facts for the blocks you
chose, and re-query it whenever a later refinement round introduces a thinly covered
pattern. When it is unreachable, apply the degraded-mode rule below and keep going
on the bundled catalog.

### Step 3 — Refinement loop

**Optional first, when the direction is open:** a wireframe that commits to no
layout, an archetype the Step 1 confirmation could not settle, or an explicit ask
for options leaves this loop nothing to refine — it converges on whichever reading
happened first. In that case run the throwaway alternatives round in
`references/divergent-alternatives.md` before round 1, pick one, and enter the loop
with the pick. Where the wireframe already decides the layout, skip it: inventing
alternatives to a decided design manufactures choice the input never offered.

Each round, in order:

1. **Write/overwrite** `design/<screen-slug>/preview.html` — a fully self-contained
   HTML file (inline CSS, no external resources) built on the look established by
   `templates/preview-shell.html`: OutSystems UI-approximate grid, cards, and
   typography, with **every region visually labeled** with its mapped pattern name.
   The preview is a design-communication artifact, explicitly *not* pixel-parity —
   keep the template's disclaimer footer.
2. **Write/overwrite** `design/<screen-slug>/pattern-tree.md` and **print the compact
   pattern tree in chat**, with every flagged ambiguity as a labeled numbered
   question (`Q1`, `Q2`, …) the user can answer by label or in plain language.
3. The user reacts in plain language. **Re-infer only the affected subtree** and
   re-render; untouched regions are never re-derived.

**Question labels are globally unique across the whole message.** Every open
question in a round carries its own label — `Q1`, `Q2`, `Q3` — and every option
under it carries that question's label plus a letter: `Q1a`, `Q1b`, `Q2a`. Never
restart numbering per question, and never label options with bare letters or bare
numbers, so a bare short answer identifies exactly one thing. (Measured
2026-08-25: three questions each offering options `a`/`b` drew the answer "2",
which matched nothing, and cost a clarification round.)

When a reply **matches no label**, ask **one clarification, never a guess** —
quote the labels that are still open and stop there. This is hard gate 4's
never-silently-pick rule applied to the answer rather than to the question.

Every round from the second onward opens with a **what-changed statement** — the
diff since the last round, nothing more (hard gate 5). The loop exits only on
explicit user approval of the current tree.

### Step 4 — Blueprint emission

On approval, fill the OMI enriched blueprint at
`design/<screen-slug>/blueprint.json` (schema:
`schemas/enriched-blueprint.schema.json`), with all of:

- `schema_version` — **`schema_version` is the literal string `"2"`** for this
  blueprint, and the schema admits no other value. It is not a version you
  choose or increment, and it is **not** the screen inventory's `"1"`: those are
  two different artifacts with two independent version lines, and conflating
  them fails the blueprint on its very first key.

- `app_chrome` — the chosen layout block **plus its actual menu/nav content**:
  every top-bar or side-menu page link's label and which one is active, not
  just `{"layout_block": "..."}` on its own. OMI's Chrome Batch Discipline
  needs this content to review shared chrome before screen consumers depend on
  it, and `blueprint.json` is the file that gets handed to OMI — chrome
  content living only in `pattern-tree.md` prose or chat doesn't travel with
  it. **Canonical chrome-content shape** (decided 2026-07-17 from the soak-1
  G4 finding): a `menu` array alongside `layout_block` — `"menu": [{"label":
  "Records", "active": true}, {"label": "Search"}, ...]` — whenever the
  wireframe shows menu content, plus these optional keys when the wireframe
  evidences them: `app_title`, `page_title`, `breadcrumbs`, `user_info`. Use
  exactly these key names; do not invent parallel shapes (`sidebar.nav_groups`
  and `header.content` variants are retired). The schema stays permissive
  (only `layout_block` is required), but the validator emits an advisory
  warning when a menu-bearing layout (`LayoutSideMenu`/`LayoutTopMenu`)
  carries no `menu` content.
  **On an app created from the standard ODC Web template, `app_chrome` maps
  onto chrome that already exists** — such apps are observed carrying
  `LayoutTopMenu` with the `Menu` block, and they ship the `Common`
  authentication and profile screens the ODC documentation calls pre-built and
  editable. Declaring `LayoutTopMenu` plus the real menu entries
  is therefore adopting that chrome, which is the default; a different layout
  block is a deliberate replacement, so say so in the round's what-changed
  statement rather than letting it read as a fresh choice. For the same reason
  the `Common` screens are not designed from scratch by default: a design run
  on `Login` or `UserProfile` is styling a screen that exists. The measured
  template contents are in
  `outsystems-mentor-implementation/references/odc-app-shell-first-scaffold.md`.
- `blocks` — reusable web blocks identified during the loop. **An empty array is a
  legitimate answer** — a screen that shares nothing and repeats nothing has no
  blocks, and inventing one to look thorough is the same defect as inventing a
  chart. When you *do* declare one from a **single** screen, remember the loop has
  only ever seen one caller: **put every caller-specific affordance in a named
  placeholder, never in the block's own definition.** A Phase 3 run declared
  *"`DslEditor`: a labelled TextArea **with an inline 'Escape for JSON' Button**"*
  from one screen; its second caller was a Painless script editor that wanted no
  such button, and the block did not survive contact with it (GAP-8). Assume a
  block you have seen once is **under-observed**.
  Also distinguish a block from a list: **N callers of one shape is a block; N data
  rows through one template is an `IList`.** Nine identical cards bound to nine
  records need no block.
- `design_system` — colors, typography, spacing, visual rules, **seeded from the
  wireframe's observed colors and any brand input from Step 1**. When Step 1 read
  a live URL or an HTML file, the seed is that run's **measured token table** —
  no value read by eye — with a brand colour the operator declared at Step 1
  still overriding the measured accent, recorded as a deliberate deviation.
  Typography carries family, size, weight, letter-spacing and colour per role as
  measured, never a page-level font stack plus assumptions.
- `screens` — the approved region tree; every repeated-content region names its
  data producer. **The Step 2 secondary-text sweep runs *before* approval**, so
  every hint line, count, caption and disclaimer it finds is already in the tree
  the user approved. If you reach Step 4 and notice a wireframe region that is
  missing from the tree, you have found a **Step 2 miss, not a Step 4 decision** —
  reopen the refinement loop and get it approved. Never silently add an unapproved
  region here, and never silently drop one the sweep found (GAP-7).
- `entities` — **named data producers only**; no data-model design beyond that.
  Each array member requires exactly these keys: **`name`**, **`type`**,
  **`attributes`** (an array of attribute names). The key is `attributes` — **not**
  `key_attributes`.
  **A new entity reaches the capability plan in the same round it is emitted.**
  When this blueprint names an entity the plan's **Data Intent** does not carry,
  update the plan's Data Intent **in the same round** — before the handoff, not
  at the next screen. `validate_blueprint.py --plan` will find it either way; the
  difference is *when*. Left to the validator it surfaces N screens later, as a
  batch of unrelated entity names with no memory of which screen wanted which and
  why (measured twice on the 2026-08-27 restaurant-app-v2 run, 11 entity names
  between them). Fixing it while the design decision is still in the room costs
  one line. This is the plan-side half of the `--plan` reconciliation below: that
  flag is the safety net, not the workflow.
- `icon_mapping` — each array member requires **`role`** and **`outsystems_icon`**.
  The key is `outsystems_icon` — **not** `icon`. Its value is a **bare Phosphor icon
  name**: `house`, `gear`, `magnifying-glass`, `arrow-right`, `trash`, `file-text`.
  **Never CSS class syntax** — not `icon-home`, not `ph-house`, not `ph ph-house`,
  not `fa-home`. OMI's reference doc is explicit: *"Use a bare Phosphor icon name
  for OutSystems UI Icon widgets, not `ph-*` or `ph ph-*` class syntax."*
  ⚠️ **OMI's own example asset violates its own rule** (it ships `"icon-home"`), and
  this skill's golden fixture copied that error for a while. **Do not imitate the
  asset on this field — imitate the rule.** `scripts/validate_blueprint.py` now
  rejects class syntax, so a wrong value fails loudly instead of reaching OMI
  unpatched (Phase 3 GAP-6, where it did exactly that across eight screens).
- `screens[].name` — **the ODC element name, never the human title**. This
  artifact requires letters, digits and underscore, first character a letter —
  `A4PrintPreview`, not `A4 Print Preview`. That grammar is **this contract's**,
  a deliberate safe subset of the vocabulary ODC publishes for names it derives
  itself; no screen-element grammar is published. The human title goes in the optional
  **`screens[].display_name`**, which no consumer matches against anything.
  This is not cosmetic: every downstream consumer resolves a screen by matching
  this string against the built model's `Name` **exactly** — OMI's
  `recompute_assertions.py`, and the render-gate spec `--emit-render-gate-spec`
  projects. On restaurant-app-v3 rev 7 (2026-09-02) six of seven screens came
  back `SCREEN_MISSING` from a build that contained all seven, for this reason
  alone. Matching stays exact by decision (Codex, AH-2026-09-02-006): a matcher
  that ignored spaces and case would resolve two different screens to one node
  and hide the collision. `validate_blueprint.py` rejects a display title here
  and names the element name to write instead.
- `screens[].render_gate` — **the one gate-bearing channel for a runtime
  claim**, and the section this step is most likely to skip. Every disclosure
  about what the screen must SHOW, and every requirement the blueprint cites,
  is written here as a **named assertion** — or as an explicit
  `known-unverified` entry saying why none is derivable. Full contract, grammar
  and the worked case: `references/render-gate-assertions.md`.
  **Why it is a slot and not prose:** a disclosure that reads like coverage and
  discharges nothing is worse than silence, because it stops anyone looking —
  the reference carries the run that measured that. Two rules bind, both keyed
  on structure rather than on wording, because the artifact behind them is
  written in European Portuguese and an English phrase trigger fires on
  nothing:
  1. **Every disclosure says where it is discharged.** Each line of
     `evidence_boundary.review_notes`, `evidence_boundary.grounding_notes` and
     `target_context.review_notes` carries `[render-gate: <label>]` naming the
     assertion that checks it, or `[no-runtime-claim]` if it asserts nothing
     observable on the rendered screen. Write the marker **while writing the
     note**. A mistyped one is a contract error, never silent prose.
  2. **Every requirement id the blueprint cites is answered** by some entry's
     `discharges`, `label` or `reason`. Opt-in by your own citation, so it can
     never force invented content.
  `populated` is not the assertion for "shows the right thing" — a placeholder
  is not empty, so it **passes** a populated check. Use `assert: "text"` with
  the expected string.
- `roles`, `acceptance_checklist` — see **When a section is legitimately
  empty** below before writing either one.

## When a section is legitimately empty

Adopted 2026-08-24 from the `OutSystems/-UX-UI-Hub` mining pass (X-16): ceremony
scaling belongs **in the template that produces the artifact**, as a condition
attached to each section, not in the operator's memory.

The schema makes every top-level key required, so no section is ever dropped.
Several are correctly **empty** — and an operator facing a required key with
nothing true to put in it will invent something plausible. **That padding is the
defect this section exists to prevent.** It is the same failure as inventing a
chart: content that exists to make the artifact look complete.

| Section | Empty is the right answer when | Worked case |
|---|---|---|
| `blocks` | the screen shares nothing and repeats nothing | see the `blocks` bullet in Step 4 — it carries the full rule, including why a block seen once is under-observed |
| `entities` | the screen names no data producer at all | an `instructional` screen — a getting-started page, a launcher, a reference card. It explains rather than operates, so there is nothing for it to bind |
| `icon_mapping` | the wireframe shows no icons | a plain form or a text-only detail view. Do not map an icon the wireframe never drew, and do not add one "for polish" — that is a design decision the user never approved |
| `roles` | nothing on the screen is role-gated | a screen every principal the app admits can reach. An empty `roles` says *no gating was designed*; it does not say the app is anonymous |
| `screens[].render_gate` | the screen makes no claim about what it must show at runtime | an `instructional` screen — it explains rather than operates, so there is no displayed state to assert. This is why the missing-assertion warning stays **advisory** and never blocks at handoff: forcing an entry here would produce exactly the padding this section exists to prevent. The rules that DO block are the two discharge rules, and both are triggered by something the author wrote |

**`acceptance_checklist` is never empty.** It is the one required section with
no legitimate empty state: a screen with nothing worth checking is a screen with
nothing worth building. `scripts/validate_blueprint.py` rejects an empty one —
before 2026-08-24 the field was unchecked and an empty list passed clean, which
is exactly how a section quietly stops being produced.

A list of what may be empty, without a statement of what may not, licenses
over-omission. Both halves are the rule.

⚠️ **The schema is the contract, not this prose.** Field names above are listed
because getting them wrong is the single most common way a run fails Step 4 — a
Phase 3 run emitted `INVALID: 13 contract error(s)` by writing `key_attributes`
and `icon` after reading an earlier, vaguer version of this list. **Before
emitting, read `schemas/enriched-blueprint.schema.json` and take the required
keys from it** rather than from memory or from this paragraph. If the two ever
disagree, the schema wins and this text is the bug.

#### How the Columns/Card skeleton projects into `screens[].main_content`

**Read this before writing a single region.** `main_content` has **exactly one
grouping level** — the validator rejects a group inside a group. Hard gate 2
demands a `Columns*` + `Card` skeleton, so the two must be reconciled, and the
reconciliation is not obvious. A Phase 3 operator who worked it out from first
principles concluded the contract was *broken*, invented a non-schema `wrapper`
key, and shipped a false limitation note — all of it validating green (GAP-5).

There are exactly two region shapes, and between them they carry the whole
skeleton:

| Shape | Use it for | Keys |
|---|---|---|
| **Leaf region** | a single full-width surface | `outsystems_hints.block` (one bare block name) + `content[]` |
| **Group region** | a `Columns*` row of surfaces | `type: "group"`, **`columns`** (the Columns block name), optional `columns_config`, and **`items[]`** |

- The **`Columns*` block name goes on the group**, in its **`columns`** key —
  *not* in any region's `outsystems_hints.block`.
- Each entry in **`items[]`** carries **`column: 1|2|…`** (which column it sits in)
  and its own **`outsystems_hints.block`** — normally a bare **`Card`**. Two items
  may share the same `column` number when a column stacks two cards.
- **Widgets *inside* a Card live in that region's `content[]`**, as
  `{element, data, label, typography, action}` descriptors — **not** as nested
  regions. This is the part that looks like a limitation and is not: `content[]`
  is the intra-card channel, and it is exactly how OMI's own asset writes it.

```jsonc
"main_content": [
  { "id": "1", "name": "Subtitle",                       // leaf
    "content": [{ "element": "AdvancedHtml Tag=p", "data": "…" }],
    "outsystems_hints": { "block": "AdvancedHtml" } },        // hint stays bare; the Tag qualifier lives in the element

  { "id": "2", "type": "group", "name": "Workspace",     // group = the Columns row
    "columns": "ColumnsSmallRight",
    "columns_config": { "GutterSize": "Entities.GutterSize.Base" },
    "items": [
      { "id": "2a", "column": 1, "name": "Composer",
        "data_source": { "entity": "Thing" },
        "content": [                                     // the Card's widgets
          { "element": "Columns2 holding Label plus Input and Label plus Dropdown", "data": "…" },
          { "element": "Button x3", "data": "Format · Clear · Run" }
        ],
        "outsystems_hints": { "block": "Card" } },
      { "id": "2b", "column": 2, "name": "Result",
        "content": [{ "element": "TableRecords", "data": "…" }],
        "outsystems_hints": { "block": "Card" } }
    ] }
]
```

**`references/examples/golden-blueprint.json` is the worked example — read it for
*structure*, not only for `target_context`.** If you find yourself wanting a third
nesting level, you want `content[]`.
- `target_context` — leave the app key as the literal `"unresolved"`; OMI resolves
  it on intake. Follow the golden-fixture shape: `target_mode:
  "shell-first scaffold"`, `canonical_app_key: "unresolved"`, and a review note
  saying resolution is OMI's job.
  **On an app that already exists, that shape is a lie.** `target_mode` also
  accepts `"existing-app"` (and `"verified blank shell"`), and the existing-app
  path is: `target_mode` = `"existing-app"`, `verified_shell_required` set to
  `false`, and every verified asset you found named in `existing_assets`.
  Emitting `"shell-first scaffold"` for a live 25-screen app tells OMI to
  scaffold a shell it already has.
  `references/examples/golden-blueprint.json` is **deliberately the greenfield shape**;
  for the existing-app path imitate
  `references/examples/existing-app-blueprint.json` instead (Phase 1 trial F-05).
- `evidence_boundary` — `evidence_status` defaults to `"Catalog-backed official"`
  (pattern facts from the bundled reference catalog). Use `"Current official"`
  **only** for a fact this session actually verified via `outsystems-tech-content`.
  **Never claim `"Current official"` while degraded.**

#### Typed data model (create-only, except what already exists)

Every entity in `entities[]` is one this app will **create**, unless it carries
`exists: true` (see the existing-asset channel below). Declare each attribute in
full, using OMI's exact field names:

- `name` — the attribute name.
- `data_type` — a **closed vocabulary**, enforced by the schema and the
  validator. An open string here is unvalidatable, and what it hides is a
  certain publish failure rather than a style slip (see the class rule below).
  Three admitted forms:
  1. **A basic type**, in the ODC literal register — `Text`, `Integer`,
     `Long Integer`, `Decimal`, `Currency`, `Boolean`, `Date`, `Time`,
     `Date Time`, `Email`, `Phone Number`, `Binary Data`. One register, because
     `outsystems-mentor-implementation` is the semantic authority for this
     vocabulary and its contract states the literal `DataType` string, which is
     what gets rendered verbatim into the Mentor prompt. The camelCase register
     this skill's fixtures used to write (`text`, `longInteger`, `dateTime`) and
     the three identifier tokens (`integerIdentifier`, `longIntegerIdentifier`,
     `platformDefaultIdentifier`) were admitted alongside it between 2026-08-27
     and 2026-09-01 and are now refused, each with a message naming the string
     to write instead.
  2. **A `Text` with its length** — `Text(200)`, `Text(50)`. State it on any
     Text attribute whose content can exceed 50: an unstated length silently
     *chooses* 50 and truncates.
  3. **A relationship** — `"<TargetEntity> Identifier"`, single-token target.
     Note this form has no camelCase spelling, and neither does `Text(200)`:
     a camelCase register could never have covered the whole vocabulary.

  Not members, and refused: the App Generator's engine-side kinds that have no
  ODC basic type (`url`, `percentage`, `rating`, `imageUrl`, `multiLineText`,
  `foreignKey`), and near-miss spellings such as `DateTime` for `Date Time` —
  a near-miss is read as a Text attribute named after a type, which publishes
  cleanly and is wrong.

  **Every primary key is the literal `Long Integer`** — for an ordinary
  auto-number key, with auto-number, mandatory and primary-key set — **and never
  any `Identifier`-suffixed type.** This is a validator predicate over every
  attribute of every blueprint, not advice: any primary key that is not
  `Long Integer` is an error.

  The rule covers static entities too, and a `Text` primary key is the case
  worth naming, because it looks like a legitimate natural key and is not: a
  static entity's key is an `Id` with `IsAutoNumber = No` and an explicit
  non-null integer, with the display value in a **separate `Label` attribute**
  (OMI rule 6) — so a Text key is a static entity modelled wrongly. A design
  that genuinely needs another key type says so in
  `evidence_boundary.review_notes`, never silently.

  `Integer Identifier`, `Long Integer Identifier`
  and `Identifier` all validate cleanly and then fail every publish
  (`OS-RDBS-GEN-40002 Unknown OsAttributeTypes`, masked as `OS-DPL-50203` via the
  MCP path). **The class rule, scoped to the path it was measured on — an
  entity-attribute `DataType`: a string outside the platform's enum passes
  validation and fails at publish** — the model API accepts any string,
  validation checks shape rather than membership in the platform's closed enum,
  and the enum is only enforced by the publish-time migration-script generator.
  Verified 2026-08-11: explicit `Long Integer` published first attempt where
  `Integer Identifier` needed 6 internal retries and failed across two
  environments; independently reproduced on another tenant. If a `DataType`
  string is ever uncertain, read it off an already-published app in the same
  tenant rather than guessing a second name. This applies to **entity
  attributes**; an `Identifier`-suffixed type on an action *parameter* is fine
  and publishes normally. A design that genuinely needs a 64-bit key must
  say so explicitly in `evidence_boundary.review_notes` as a Mentor/publish-path
  limitation to resolve deliberately — never silently narrowed, never silently
  emitted as longIntegerIdentifier.
- `is_primary_key`, `is_foreign_key` — booleans.
- `enum_values` — for a foreign key onto a static entity, the list of that
  entity's records (e.g. `["Draft","InProgress","Done"]`); otherwise `null`.
  **The validator hard-fails `enum_values` set on a non-foreign-key
  attribute** — the field only means something as the record list a foreign
  key points at; on any other attribute it is a contract error, not a hint.
- A foreign key's `data_type` is `<TargetEntity> Identifier`, and **the
  validator hard-fails a target declared nowhere** — the target needs an
  `entities[]` entry (flag `exists: true` if it is already in the target app)
  or an `enum_values` list on this attribute seeding it as a static entity.
  `User Identifier` and `Role Identifier` are platform-supplied types, so they
  need no entry. Announcing the target in `target_context.existing_assets` is
  not a declaration: that field says the app has assets, `exists: true` says
  which entity is one.

A **static entity** may additionally declare its own design-time rows via an
optional entity-level `records` array (e.g.
`{"name": "SampleScript", "type": "static", "records": ["Match all", "Boost by year"], "attributes": [...]}`).
This is the producer expression for a standalone static catalogue or dropdown
source that nothing FK-references — the shape that previously had no populable
record path. **The validator hard-fails `records` on a non-static entity**
(a normal entity is runtime-populated; design-time rows only mean something on
a static). OMI consumes declared records via its standalone-static record
intake (rule 6): one record per value, in declared order, no incoming FK
required. When the same static is seeded **both** ways — declared `records`
and an incoming FK's `enum_values` — identical ordered lists seed it exactly
once, and **differing lists are a contradictory dual seed the validator
hard-fails** (same-file and across blueprints), mirroring OMI's stop-and-return.

#### The existing-asset channel (`reuse` / `exists`)

`target_context.existing_assets` announces **that** the target app has verified
assets. It does not say which region or which entity *is* one. Two optional
fields bind them, and they exist because a blueprint that faithfully followed
every other rule on an existing app told the build to recreate a block and two
entities that were already there — a defect no format validator can see (Phase 1
trial F-02):

- **Region-level** `"reuse": {"block": "MainFlow/RecentQueriesPanel"}` — this
  region **is** an app-local web block the target app already has. It satisfies
  the Block Mapping Gate on its own: no `outsystems_hints.block`, no
  `custom_block_needed` — and the validator **rejects a region that carries
  `reuse` together with either**, because a region binds to an existing block
  OR describes one to build, never both. Unlike a catalog hint, the name is an **asset name and
  may be flow-qualified** (`MainFlow/…`) — the bare-token rule does not apply
  to it.
- **Entity-level** `"exists": true` — this entity is already in the app. Its
  `attributes` are the shape OMI **verifies**, not the shape it creates, and an
  existing static entity needs no `records` and no incoming FK+`enum_values`
  seed (the validator exempts it from the populable-record-path rule).

Both are valid **only** when `target_mode` is `"existing-app"`; the validator
hard-fails either one against any other target mode, because a greenfield target
has no app for the asset to exist in. Name every bound asset in
`existing_assets` too — the validator warns when a binding is not announced
there. OMI folds everything flagged this way into **modification** steps and
never into creation steps (see the Existing-Asset Reuse Channel section of the
enriched-blueprint reference in `outsystems-mentor-implementation`).

Do not reach for this channel from imagination: bind only assets a scaffold
inventory of the target app actually evidenced, and say where that evidence came
from in `evidence_boundary.grounding_notes`.

**Bindings must be true.** Where a widget consumes data, add a `binds` object
(`binds: { "entity": "<Entity>", "attribute": "<Attribute>" }`) next to the prose
`data`. The validator hard-fails a binding whose attribute does not exist on the
declared entity — this is how a ProgressBar can no longer be bound to a field
that was never modelled.

**`main_content` is the source of truth.** The `acceptance_checklist` is
advisory prose and carries no authority. Any count you want enforced goes in the
screen's optional `assertions` object (e.g. `assertions: { "links": 4, "buttons": 0 }`); the
validator recomputes it from `main_content` and hard-fails a mismatch.
**Counting vocabulary (AB-03, learned live):** the counted element families are
exactly Link, Button, and Input — **choice and date widgets (Dropdown,
DropdownSearch, DatePicker, DatePickerRange) are NOT `inputs`**; an operator who
counts them as inputs fails with a bare number mismatch. And declare the
**zero-affordance assertion** (`{"links": 0, "buttons": 0, "inputs": 0}`)
deliberately on read-only screens: it turns a no-editing business rule into a
fact the post-publish recompute checks mechanically.

**Assertions are REQUIRED for filter regions and empty states.** Everywhere else
`assertions` stays optional; on a screen whose `main_content` declares a region
bound to `Tabs`, `ButtonGroup`, `BlankSlate` or `EmptyState`, the validator
**hard-fails a screen that omits them** (an empty `{}` does not satisfy it
either). The trigger is the region's declared **block token**, never its prose —
region names are written in the project's own language, and a keyword rule in
one language is not a rule. `reuse.block` wins over `outsystems_hints.block`,
the same precedence OMI's region diff uses: a region carrying both is already
rejected here, and where two controls read the same field they must not
disagree about which one they read. This is a separate mechanism from the counts and
does **not** extend the counting vocabulary, which stays exactly Link, Button
and Input. Measured (restaurant-app-v2, 2026-08-28/29): two screens shipped with
whole regions missing — the filter tabs and the empty states — and nothing
caught it, because those screens declared no assertions at all, so OMI's
post-publish recompute reported `no screen declares assertions - nothing was
checked`. The regions that went missing are exactly the ones this rule makes
non-optional, so the recompute is never inert for them.

**Type-fit is advice, not law.** A ProgressBar/Counter bound to a non-numeric
attribute, or a status Tag not backed by a static entity, produces a `WARNING`
that never blocks — it flags a likely wrong-widget-for-the-data choice for you to
weigh.

**Unpopulated static data sources hard-fail.** A `static` entity used as a
`data_source` with no seed — no non-empty declared `records` and no incoming
foreign key carrying `enum_values` — is a contract **error**: OMI has no
populable path for that entity's rows and rejects it, returning the blueprint
for producer correction. The producer has three sanctioned shapes: declare the
rows in the entity's `records` array, supply the FK+`enum_values` seed, or
model the data as a normal, runtime-populated entity. In multi-path mode
(below) this is evaluated against the **union** of every blueprint's seeds
(FK-enum targets and records-declaring statics alike), so a legitimate
cross-blueprint projection — one blueprint uses the static entity while
another supplies its seed — is not false-flagged. Cross-blueprint, two
blueprints declaring **different non-empty `records` lists** for the same
entity is a conflict; declaring records in only one of them is a normal
projection.

**One advisory check, non-blocking.** A repeat widget (`List`, `Table`,
`TableRecords`, `Gallery`, `Carousel`, `AccordionList`) over a `data_source`
whose content items carry no structured `binds` produces a `WARNING` — its
columns are prose-only and cannot be checked against the entity's attributes.
It never blocks `VALID`; it is worth fixing before handoff.

Then validate:

```bash
python3 scripts/validate_blueprint.py design/<screen-slug>/blueprint.json \
  | tee design/<screen-slug>/validation-report.txt
```

Windows PowerShell (`python3` is not a command on Windows):

```powershell
python scripts\validate_blueprint.py design\<screen-slug>\blueprint.json |
  Tee-Object design\<screen-slug>\validation-report.txt
```

(Resolve `scripts/validate_blueprint.py` relative to this skill's install
directory — that copy is canonical. If the operator explicitly names another copy
(e.g. a repo-source checkout), use the operator's path and note it in the run; when
no path is named, never go hunting beyond the install directory.) On failure: show the validator output **verbatim**, fix by reopening the
refinement loop, and re-validate. **Never hand off a failing blueprint.** On
success, save the passing output as `validation-report.txt`.

**Grading the run as a handoff.** While the design is still being drawn, some
findings are advice. Once OMI depends on them they are defects. Add `--handoff`
at the moment you hand the blueprint over:

```bash
python3 scripts/validate_blueprint.py design/<screen-slug>/blueprint.json --handoff
```

Windows PowerShell:

```powershell
python scripts\validate_blueprint.py design\<screen-slug>\blueprint.json --handoff
```

The graduating warnings — the prose-only repeat widget above, a bound asset
missing from `target_context.existing_assets`, an undischarged disclosure line,
and a cited requirement id no `render_gate` entry answers — then print under
`HANDOFF BLOCKED:` and exit 1 instead of advising. The finding text is
identical; only the channel and the exit code change, and the contract verdict
is untouched: a graduating warning is not a contract error and the blueprint
still reports `VALID`. A warning graduates only if you can always clear it by
editing the blueprint, so there is no waiver and none is needed; warnings that
can be a legitimate final state — a layout with no menu, an entity the screen
reaches through a reused block — stay advisory under the flag. It works on a
directory run too, blocking if any blueprint carries one. **Without `--handoff`
the report is byte-for-byte what it was before the flag existed.**

**Placeholder markers are rejected.** `TODO`, `TBD`, `FIXME`, `PLACEHOLDER`, a
bracketed `<fill in>`, or a value that is nothing but `...` is a contract error
in any gate-bearing field — names, descriptions, entity and attribute names and
types, region names and `outsystems_hints.block`, roles, icons. A blueprint
whose entity is called `TBD` passes every shape rule and hands OMI a literal
entity called TBD, so this fails closed rather than warning. The free-prose
channels are deliberately exempt: record what is still open in
`evidence_boundary.grounding_notes` / `review_notes`, `target_context.review_notes`
or `acceptance_checklist`, never in the field itself.

**Validating more than one blueprint at once.** Pass a directory or several
paths instead of one file when checking blueprints from separate runs that
share the same app's data model:

```bash
python3 scripts/validate_blueprint.py design/ \
  | tee design/cross-blueprint-report.txt
```

Windows PowerShell:

```powershell
python scripts\validate_blueprint.py design\ |
  Tee-Object design\cross-blueprint-report.txt
```

Directory intake is restricted to **canonical `blueprint.json` files**: a
directory expands to every `*/blueprint.json` under it (or a single screen
directory's own `blueprint.json`); multiple explicit paths work the same way.
A directory holding only arbitrarily-named `*.json` is **not** intaken — it
expands to nothing and the validator reports `no blueprint files found`
(exit 2), so a misnamed file is never silently validated. Each blueprint gets
its own per-file `validation-report.txt` beside it (distinct per-screen
directories, so reports never collide), plus a `CROSS-BLUEPRINT:` verdict: the
same entity name declared with a conflicting shape across blueprints — a
different primary key, or a same-named attribute typed differently — is a
contract error, because OMI merges these into one data model on intake. A
single path behaves exactly as before this check existed.

The multi-blueprint pass also checks **shared chrome**: one app has one
`app_chrome.layout_block`, one `app_title`, and one menu — same entries, same
order, on every screen. A multi-screen app is N runs sharing one chrome
decision made up front, and nothing used to check that the N runs agreed.
`active` is excluded on purpose: each screen highlights its own entry.

**Reconciling against the plan.** Add `--plan <path>` to check the chain's
cross-route boundary — every entity a blueprint declares must be named in the
implementation plan:

```bash
python3 scripts/validate_blueprint.py design/ --plan docs/plans/<plan>.md
```

It runs in one direction only. Plan prose is free-form, so blueprint → plan is
mechanical while plan → blueprint would mean guessing which capitalised words
are entities. Matching is word-bounded, so `QueryHistoryArchive` in the plan
does not satisfy an entity named `QueryHistory`. An entity flagged
`exists: true` is still checked: the build must not create it, but the plan
should still name the data the screen binds to.

**Reconciling against the screen inventory.** When this run was briefed from an
`outsystems-screen-inventory` artifact, add `--inventory <path>` to check the
tier boundary — the inventory decided the app's chrome, its screen list and its
per-screen assertion counts, and the design run received those as a prose brief:

```bash
python3 scripts/validate_blueprint.py design/<screen-slug>/blueprint.json \
  --inventory design/screen-inventory.json
```

Windows PowerShell:

```powershell
python scripts\validate_blueprint.py design\<screen-slug>\blueprint.json `
  --inventory design\screen-inventory.json
```

**This matters most for a single-screen run.** The shared-chrome check above
needs two blueprints to compare, so one screen on its own could drop the whole
menu, or pick a different `layout_block`, and still exit 0. `--inventory` is the
anchor a lone blueprint never had.

Five things are **errors**, because the inventory is definitionally
authoritative on them:

- **Screen name.** A blueprint screen with no inventory entry has no recorded
  purpose, archetype or behaviour anywhere upstream.
- **Chrome.** `layout_block`, `app_title`, and the menu's labels *and order*.
  Here `active` **is** checked, unlike the cross-blueprint pass: the inventory
  records where each entry goes, so the active entry is *derived* from which
  one targets this screen rather than being unknowable. It is compared only
  when the file carries exactly one screen — the menu is app-level while
  `active` is per-screen, so with two screens in one file there is no single
  right answer and the check stays silent rather than becoming unsatisfiable.
- **Carried assertions.** The inventory's counts come from the requirement and
  are carried into the blueprint unchanged. **Do not edit the number to make
  this pass** — the blueprint's own assertion check already forces those counts
  to equal its `main_content`, so editing one breaks the other. The repair is
  upstream: either the design is missing something the requirement asked for
  (add it to the screen and re-derive), or the inventory's count was wrong (fix
  the inventory and re-run its validator). The error message says so.
- **A named destination that names nothing real.** Any control's `opens` must
  be a screen in the inventory, or the literal `inline`.
- **A door the inventory settled and the design did not draw.** Where the
  inventory's `record_actions` resolves a screen's create, edit or detail to
  *another screen*, some control on that screen must carry `opens` naming it.
  `inline` and `out-of-scope` ask for no control and are silent here.

**Name the destination on the control: `opens`.** A control that opens another
screen carries `opens` alongside `element` and `data` — the screen's element
name, or the literal `inline` when the control acts on this screen instead:

```json
{ "element": "Button", "data": "\"+ Add dish\"", "opens": "DishCreate" }
```

It is optional and per control, so a blueprint written before it existed
validates exactly as it did, and it is resolved only under `--inventory`,
because the inventory is the only artifact that knows which screen names are
real. Write it wherever a control opens a screen — including the per-row
buttons inside a group region, which is where the incident's controls sat.

Six screens of one app were never built because no artifact named them
(2026-08-30). Every control that opened one described its destination in prose
inside `data` — "opens the restaurant's configuration" — and prose is resolved
against nothing. Two of the buttons were called inert for a day before the
deployed screen list showed the destinations did not exist. Both rules read
only typed fields, never the prose: the upstream verb-reading in
`outsystems-screen-inventory` is anchored on English openers, and the
blueprints that paid for this rule are written in Portuguese.

One thing is a **warning** and never blocks: an entity the inventory listed as a
data binding for this screen that the blueprint does not declare. A screen may
legitimately reach an entity through a reused block or a foreign-key lookup, so
this is advisory. Bindings of `kind: "action"` are not checked at all — a
blueprint has no home for an action name, so any finding about one would be
undischargeable.

Like `--plan`, it runs in one direction only: an inventory screen with no
blueprint has simply not been designed yet. An unreadable or unparseable
`--inventory` path **fails the run** — a missing file must not silently restore
the unchecked boundary.

### Step 5 — Handoff

Grade the run as a handoff first: `--handoff` is what turns the graduating
findings from advice into defects, and the two discharge rules above are among
them. A blueprint that blocks there is not handed over; reopen the loop, write
the missing assertion or the missing marker, and re-validate.

Then project the assertions rather than leaving them to be retyped later —
retyping is the step that already failed once:

```bash
python3 scripts/validate_blueprint.py design/<screen-slug>/blueprint.json \
  --emit-render-gate-spec design/<screen-slug>/render-gate-screens.json
```

The final message names the exact blueprint path
(`design/<screen-slug>/blueprint.json`), the projected assertions file if one
was written, and the exact next step: **invoke
`outsystems-mentor-implementation` with that file**. Nothing is auto-invoked — the
user decides if and when execution happens. Do not start Mentor work, do not chain
into any other skill. The projected assertions are consumed later, by whoever
runs the render gate (`outsystems-render-gate`, which is not part of the colleague sprint-loop pack) — this skill does not run it and does not need it installed.

## MCP enrichment and degraded mode

- **`outsystems-tech-content`** (widget-library-rules / outsystems-ui-api) is
  queried at Step 2 and whenever a refinement round introduces a thinly covered
  pattern. It verifies nesting rules and pattern API facts. It is enrichment,
  **never a hard gate**.
- **The public knowledge provider** — `workspace-knowledge-cc` or
  `outsystems-public-knowledge`, whichever is bound; they expose the same
  public retrieval role — is **reactive-only**: call it if and only if the
  user's own message in this turn asks a product-behavior question. Do not call
  it during Step 2 inference, during a refinement round, or anywhere else on
  the default path "for extra grounding" — `outsystems-tech-content` is the
  enrichment tool for pattern/nesting facts; the public provider has no
  role in the default intake → inference → refinement loop at all. A Phase 4
  Codex run called it proactively during Step 2 with no product-behavior
  question asked — that is the exact mistake this bullet exists to prevent.

**Degraded mode:** when `outsystems-tech-content` is unreachable (off-VPN, colleague
machine, no MCP configured), state the degradation in **exactly one line containing
the word "degraded"**, e.g.:

> degraded: pattern facts from bundled catalog only — outsystems-tech-content unreachable

…then **continue the loop**. Do not block, do not ask the user to reconnect, do not
repeat the line every round — once per run is the disclosure. Keep
`evidence_boundary.evidence_status` at `"Catalog-backed official"` for the whole
run. This deliberately inverts OMI's hard VPN gate: OMI blocks because it emits
execution claims; this skill emits a design *proposal* that OMI re-validates on
intake, so degraded-with-disclosure is the correct posture and keeps the skill
usable on machines with neither MCP.

## Error handling (mandatory rules)

- **Unreadable or ambiguous wireframe** → say so plainly and ask for a **better
  crop** (or a higher-resolution export) of the unclear area. Never guess the whole
  screen from an image you cannot actually read.
- **Region matching no single OutSystems UI pattern** → first try composing a
  reasonable approximation from real primitives (see "Compose-and-disclose" in
  Step 2) and disclose the workaround plainly in the pattern tree and the
  blueprint — never as visible text inside `preview.html` itself. Fall back to
  flagging it as `custom_block_needed` (that exact JSON field name) in **both**
  the pattern tree and the blueprint, with a one-line description of what the
  custom block must do, only when no reasonable composition exists. **Never
  approximate either way with a styled `Container`** — that hides a real build
  decision from the user and from OMI.
- **Validator failure at Step 4** → show the validator output verbatim, reopen the
  refinement loop, fix, re-validate. A failing blueprint is never handed off.
