# Divergent alternatives — an optional round before the refinement loop

Origin: written for this skill (shapers-workspace disposition T1, adopted
2026-08-26). Nothing here is harvested — the upstream this generalises is React
and a different design system, so only the authoring discipline transferred.

Their
`/generate-prototype --lowfi` mode builds N throwaway low-fidelity variants in
parallel, compares them, and only then commits to one direction. This file is the
same *authoring discipline* for this skill's HTML previews; none of their React,
Fusion DS, or parallel-agent machinery is adopted.

## When this round applies — and when it does not

Run it only when the **direction is genuinely open**: the wireframe is a rough
sketch that does not commit to one layout, the user asks to see options before
converging, or the screen's archetype read at Step 1 was a close call the user
could not settle.

Do **not** run it when a wireframe already commits to a layout. This skill's normal
job is to read a wireframe faithfully, and inventing alternatives to a decided
design is the same defect as inventing a chart: it manufactures choice the input
never offered. When in doubt, ask; do not open the round unprompted.

## The round is throwaway

Alternatives are exploration, not deliverables:

- They live under `design/<screen-slug>/alternatives/<variant-slug>/preview.html`,
  with a one-page index at `design/<screen-slug>/alternatives.md`.
- They **never** emit `blueprint.json`, never run the validator, and never satisfy
  Step 3's approval. Exactly one alternative is picked; that pick becomes round 1
  of the ordinary refinement loop, and everything else is discarded.
- Hard gates 1–5 still bind each preview (a layout block is chosen, zero
  `Container` nodes, every region gets a named block or an explicit flag). A
  variation that violates a gate is not a cheaper variation, it is a wrong one.

## How many

Three by default. Floor three — the point is comparing several bets, and two reads
as a binary. Cap six; past that the previews stop being read. State the count you
chose and why.

## Hold the chrome constant when it is already decided

When a screen-inventory brief exists, the shared chrome decision (`layout_block`,
`app_title`, the menu) arrived pre-decided and hard gate 1 is already satisfied by
it. **Chrome is then a held constant, not a divergence axis** — every alternative
reproduces the same shell and diverges only inside the content region. Diverging on
chrome in that case would put the alternatives in conflict with every sibling screen
in the same app.

With no inventory and no chrome evidence in the wireframe, chrome is a legitimate
axis like any other.

## Choose divergence axes — solution-level before layout-level

Pick the axes on which a difference would most inform the decision. Prefer at least
one from the first group, and hold the axes you did **not** pick roughly constant, so
each comparison isolates one bet:

**Solution-level (prefer these):**

- **Archetype** — is this a `list-table`, a `master-detail`, or a `dashboard`? The
  archetype changes what the screen *is*, not how it looks.
- **Disclosure depth** — everything on one screen, versus a list that navigates to a
  detail screen, versus a list with an inline expand or side panel.
- **Where the work happens** — edit in place, edit in a modal, or edit on a dedicated
  screen.
- **Automation and agency** — the user configures each field, versus sensible
  defaults with an "advanced" escape hatch.
- **Scope** — the minimum that does the job, versus the comprehensive view.

**Layout-level (secondary):** grid arrangement, information density, which regions
share a card. Reach for these only when the open questions really are only about
presentation.

## One alternative must be a contrarian bet

At least one of the set must **reject a stated assumption** and solve the screen's
job a materially different way — naming the assumption it rejects. Its purpose is to
pressure-test the framing, not to win. Three safe neighbours are one design rendered
three times, and produce no information.

At four or more, aim for a spectrum: conventional → adjacent → contrarian.

## What each alternative carries

Each one names, in `alternatives.md`:

| Field | Meaning |
|---|---|
| `slug` | `alternative-1` … `alternative-N` |
| `title` | Short human name |
| `bet` | *How* it differs, in solution terms — "detail lives in a side panel, list never navigates away", not the axis name |
| `axis` | The divergence dimension chosen above |
| `challenges` | The assumption this one rejects — empty for a conventional bet |
| `rationale` | One line: why this bet is worth a preview |

## Present, pick, converge

Print the table in chat with the previews' paths, say plainly that these are
throwaway, and ask the user to pick one — or to steer and re-author the set. Cap
re-authoring at two rounds; after that, build with what the latest pass produced and
say so.

On the pick, state the chosen alternative and the discarded bets in one line, then
enter Step 3 round 1 with the pick as the current tree. The what-changed statement
(hard gate 5) applies from round 2 onward as usual — the pick itself is round 1, not
a diff.
