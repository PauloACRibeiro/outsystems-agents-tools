
# OutSystems UI — Structural Skeleton

> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `ui-frameworks/outsystems-ui/structural-skeleton.md` (harvested 2026-07-29).
> **Merge note:** local corrections preserved where noted in `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.


> **What this is:** the missing step between "I picked a Layout" and "I'm filling placeholders with widgets." Most underused-block failures (custom containers everywhere, no Columns, no Cards) come from skipping it.

> **When to use:** Right after [`layouts.md`](layouts.md) tells you which Layout's `MainContent` placeholder you're filling — and BEFORE you load any `patterns/*.md`.

The output of this step is a **skeleton tree of OS UI blocks** (Columns + Card variants only). Patterns and platform widgets come later, inside that skeleton.

## The two questions

For everything you're about to put inside `MainContent` (or any other Layout placeholder), answer in order:

1. **What is the column grid?** Multi-element rows are always a `Columns*` block, never flex containers.
2. **What are the card surfaces?** Any rectangular grouping of related content (a metric, a list row, a profile, a settings group) is a `Card`-family block.

If you can't answer both before placing widgets, you don't have a skeleton yet — keep sketching.

## Step 1 — Pick the column grid for the screen type

| Screen type | Default skeleton |
|---|---|
| **Dashboard / overview** | `Columns3` or `Columns4` for a KPI / counter row at the top, then full-width content rows below (or `ColumnsMediumLeft` if there's a side rail of secondary info) |
| **Detail screen** (with side info) | `ColumnsMediumLeft` (main content ~60%, sidebar ~40%) or `ColumnsSmallRight` (main wide, narrow rail) |
| **Detail screen** (no sidebar) | Single column — no `Columns*`, content stacks in `MainContent` |
| **List / table screen** | Single column — full-width list. Rows are `CardItem` or `ListItemContent` inside `IList`, never `Columns*` per row |
| **Form screen** | Single column for short forms; `ColumnsMediumLeft` only when the request explicitly asks for a two-column form |
| **Gallery / card grid** | `Columns3` or `Columns4` of `Card` / `CardSectioned` blocks — never hand-rolled flex grids |
| **Settings / preferences** | Single column, sections grouped via `AdvancedHtml Tag="section"` + `h2` headings, content surfaces as `Card` |
| **Empty / blank** | Use `BlankSlate` block; do NOT custom-build "no data" containers |

For column-block details (args, gutter, breakpoint behavior), see [`patterns/adaptive.md`](patterns/adaptive.md). The lookup of a `Columns*` block uses the same canonical pattern as any OS UI block — see [`blocks-index.md`](ui-reference.md#how-to-look-up-an-os-ui-block-the-lookup-pattern).

### Asymmetric grids

| Asymmetric need | Block |
|---|---|
| 60 / 40 (main + sidebar) | `ColumnsMediumLeft` |
| 40 / 60 (sidebar + main) | `ColumnsMediumRight` |
| 33 / 67 (narrow nav + wide content) | `ColumnsSmallLeft` |
| 67 / 33 (wide content + narrow rail) | `ColumnsSmallRight` |

Don't simulate these with `Columns2` + a CSS width override.

### Responsive defaults

Every `Columns*` instance MUST set:

```
GutterSize     = Entities.GutterSize.Base    (or Medium for KPI rows)
PhoneBehavior  = Entities.BreakColumns.All   ← ALWAYS All. No exceptions.
TabletBehavior = Entities.BreakColumns.All   ← Default to All. Only set None
                                                if you've explicitly verified
                                                the row stays readable on tablet.
```

**`PhoneBehavior = All` is non-negotiable.** Even a 2-column row with short content needs to stack on phone — the columns get too narrow at < 480px otherwise. There is no "stays readable on phone" exception. Skipping or setting it to `None` is a polish-checklist failure.

### Row spacing — stacked `Columns*` siblings need explicit margin

When you place two or more `Columns*` instances vertically inside the same placeholder (e.g. a KPI row of `Columns4` followed by a content row of `Columns2`), **the second and subsequent rows need a top margin** — `Columns*` blocks have NO baked-in vertical spacing relative to their siblings.

Apply via `ExtendedClass`:

```
Row 1 (Columns4 — KPI tiles):    ExtendedClass = ""             ← no top margin (first row)
Row 2 (Columns2 — content):      ExtendedClass = "margin-top-l"
Row 3 (Columns3 — secondary):    ExtendedClass = "margin-top-l"
```

For tighter pairings use `margin-top-base`; for major section breaks use `margin-top-xl`. Without these, the rows visually run together — the screen looks like one giant grid instead of distinct sections.

Same rule applies to a `Columns*` followed by an `IList`, a `Card`, or any other block at the same level: the second sibling needs a margin-top utility class.

### Equal-height cards across a row — `full-height`

When a `Columns*` row hosts a `Card` (or `CardSectioned`) per cell — KPI tiles, metric cards, currency tiles — set `ExtendedClass = "full-height"` on EVERY card so they all match the tallest sibling. Without it, a card with shorter content is visibly shorter than its neighbors and the row looks ragged.

```
Columns4
├── Column1 → Card  ExtendedClass="full-height"   ← all 4 share this
├── Column2 → Card  ExtendedClass="full-height"
├── Column3 → Card  ExtendedClass="full-height"
└── Column4 → Card  ExtendedClass="full-height"
```

This also applies to `CardSectioned`, `CardBackground`, and any other Card-family block in a multi-cell `Columns*` row. Single-card rows (one Card spanning the whole row) don't need it.

## Step 2 — Identify card surfaces

Every visual grouping of related content is a card. Pick the variant by content shape, not by visual style:

| Content shape | Block |
|---|---|
| Generic surface — anything from a metric tile to a settings group to a content panel | `Card` |
| Row layout: left icon/avatar · title · body · right action (transaction row, list row, contact row) | `CardItem` (standalone) — or `ListItemContent` if it's inside an `IList` |
| Hero / promo card with background image and overlay text | `CardBackground` |
| Image + title + content + footer split (vertical = image on top; horizontal = image on side) | `CardSectioned` |

If your skeleton has rectangular regions and none of them are Card-family blocks, **stop** — you're about to build fake cards. The anti-pattern table in `SKILL.md` (upstream, not bundled) catches this; this step prevents it.

For Card args/placeholders see [`patterns/content.md#card`](patterns/content.md#card).

## Step 3 — Sketch the skeleton, then validate it

Before writing any widget JSON, write the tree as nested block names. Here's a Wise-style dashboard:

```
MainContent
├── AdvancedHtml Tag="h2" — "Account"
├── Tabs                                             ← navigation pattern
│   └── (filled in step 4)
├── AdvancedHtml Tag="h2" — "Currencies"             with Style="margin-top-xl"
├── Columns4 (GutterSize=Base, PhoneBehavior=All)
│   ├── Column1 → Card → currency tile
│   ├── Column2 → Card → currency tile
│   ├── Column3 → Card → currency tile
│   └── Column4 → Card → currency tile
├── AdvancedHtml Tag="h2" — "Transactions"           with Style="margin-top-xl"
└── IList
    └── ListItemContent rows (4–5)
```

That's the skeleton. **No `Container` appears in it.** Compare to the failure mode you're trying to avoid:

```
MainContent
└── Container Style="dashboard"
    ├── Container Style="kpi-row"
    │   ├── Container Style="card"     ← fake card #1
    │   ├── Container Style="card"     ← fake card #2
    │   ├── Container Style="card"     ← fake card #3
    │   └── Container Style="card"     ← fake card #4
    └── Container Style="transactions-section"
        ├── Container Style="header"
        └── Container Style="transaction-row"   ← fake row, repeated
```

If your sketch has `Container` nodes for anything other than (a) wrapping a recipe's internal grouping or (b) `Columns*` cell content that needs a wrapper, the sketch is wrong. Re-pick blocks.

## Step 4 — Fill the skeleton

Only NOW load the relevant pattern / recipe files for what goes inside each block:

- KPI tile content → `recipes/kpi-counters.md` (upstream, not bundled)
- Tabs content → `recipes/tab-switcher.md` (upstream, not bundled)
- Transaction row → `CardItem` placeholders (`Left` icon, `Title` recipient, `Content` date, `Right` amount) — see [`patterns/content.md#carditem`](patterns/content.md#carditem)
- Currency tile content → `Card.Content` placeholder + typography hierarchy + Counter or `<strong>` for the amount

Loading a pattern file BEFORE you have a skeleton means you'll over-fetch and you'll often pick a sub-pattern that doesn't fit the grid shape.

## When to skip column blocks

Single-column layouts are common and correct for: short forms, settings screens, single-detail pages, list-only screens, modal dialogs. **Don't reach for `Columns2` to put a label next to a value** — that's `CardItem`'s `Left` + `Title` placeholders, or a `dl`/`dt`/`dd` triple via `AdvancedHtml`, or just inline strong + text.

`Columns*` is for **page-level grid layout**, not for inline label-value pairs.

## When to skip card blocks

Not every region is a card. Skip cards when:
- The content is one paragraph or one heading + one button — that's just `AdvancedHtml Tag="section"` with widgets inside.
- The region is a `Tabs` content panel — the tab itself is the surface, no extra `Card` needed.
- The region is full-screen-width hero copy — `AdvancedHtml Tag="header"` + `h1` + `p`, no Card.

Cards are for **bounded, content-grouping surfaces**. If there's no real grouping, no card.

## Sanity checks before moving on

1. Multi-element rows in your skeleton: are they all `Columns*` blocks?
2. Rectangular content groupings: are they all `Card` family blocks?
3. List rows: are they `CardItem` or `ListItemContent` (inside `IList`) — not custom row containers?
4. Asymmetric splits (sidebar layouts): are they `ColumnsMediumLeft/Right` or `ColumnsSmallLeft/Right` — not `Columns2` with width hacks?
5. Every `Columns*` has `PhoneBehavior` set?

If all five answers are yes, the skeleton is good. Move to step 4.

## Step 3.5 — Block-inventory commitment (mandatory, before emitting the blueprint)

> **OUD note:** commit the region→block mapping here, before emitting `blueprint.json` — the inventory is the contract the blueprint must honor. (Upstream frames this step around its build tooling; in this design-only skill the blueprint IS the build artifact.)

> **Why this exists**: when the design feels rich/custom/dark/premium, the agent's intuition flips into "I'll style this with Containers + custom CSS classes" mode. By the time it's writing widget JSON, real OS UI blocks (`Card`, `UserAvatar`, `IconBadge`, `ProgressBar`, `StackedCards`, `Tag`, `Counter`) get bypassed in favor of `Container` + `Style="\"hb-stat-card\""` / `Style="\"hb-vcard--indigo\""` / etc. The custom classes often aren't even defined anywhere (the theme stylesheet got reverted, or the agent forgot to define them) and the visual surface ends up looking default.

**Before you emit the blueprint for a screen**, output an explicit block inventory: every visual region in the skeleton, mapped to a real OS UI block or platform widget. Format:

```
| Region                          | Block / Widget                | Why                                              |
|---------------------------------|-------------------------------|--------------------------------------------------|
| Page chrome (sidebar+top bar)   | LayoutSideMenu                | Layout owns the shell                            |
| Sidebar nav                     | Menu block (Common flow)      | Theme-aware nav, ARIA, mobile drawer             |
| Sidebar user (avatar + name)    | UserAvatar block              | Initials/photo fallback, theme size              |
| Top-bar notif bell + count      | IconBadge block               | Positions the badge correctly                    |
| Balance hero section            | Card                          | Theme shadow/radius/padding                      |
| Quick-action buttons            | IButton + IIcon (Phosphor)    | Keyboard, focus, theme color                     |
| Stat cards row (4 tiles)        | Columns4 → Card per cell      | Responsive grid + theme-aware card surface       |
| Savings goal progress bar       | ProgressBar block             | Theme-aware, accessible, animatable              |
| Spending overview chart         | DonutChart + ChartLegend      | Real chart, mock DataPointList if no aggregate   |
| Recent transactions list        | IList → ListItemContent rows  | Aggregate-bound, virtualizable                   |
| Payment cards carousel (Cards)  | StackedCards + Card per slide | Real swipeable interactive block                 |
| Card toggle controls            | Card per toggle + Switch wid. | Real switch, real card surface                   |
| Card details / perks strip      | CardSectioned, Tag (perks)    | Title/Content/Footer split, real chip pills      |
```

This is a forcing function. **If you can't fill the right column with a real block / widget name (no `Container + .hb-something`), you don't yet have a viable skeleton — go back and re-pick.**

### Hard rule: no project-prefix custom classes in widget Style

If you find yourself about to give a widget any `<project-prefix>-<component>` class name (`hb-stat-card`, `my-app-button`), **stop**. That's the tell that you're in custom-CSS mode and bypassing a real OS UI block.

Two replacements:
- **The visual region IS a known shape** (card, button, avatar, badge, list row, progress bar, chart, tag) → use the real OS UI block from the inventory above.
- **The region is genuinely custom** (a one-off ornament, a screen-specific decoration) → pass utility classes (`background-neutral-1 border-radius-soft padding-base text-neutral-7 display-flex column-gap-s`), not a project-prefixed name.

The **only legitimate use of a project-prefixed custom class** is when the visual treatment can't be expressed via OS UI utility classes AND you're scoped to a specific block instance — e.g. setting the block's `ExtendedClass` argument to `"linear-background-primary"` where `linear-background-primary` is defined in the theme stylesheet as a one-off gradient. **Even then, the class must be defined somewhere** — applying a class name without defining it is a no-op, and the widget renders with default styling.

### When the mapping is forced: ask, don't bypass

The two replacements above assume one of them fits. Sometimes neither does — the
region is a known shape but the nearest block distorts what the wireframe shows,
or the fallback ladder in `ui-reference.md` (block → `AdvancedHtml` with a
semantic tag → `Container` + utility classes) only reaches the region by
spending its last rung. Both cases feel like friction while you are filling the
inventory, and **the awkwardness is the signal to ask, not the signal to
bypass.** Taking the forced block quietly, or dropping a rung because the block
is uncomfortable, converts a design question into a mapping the user never saw.

The surface already exists: the refinement round prints the pattern tree with
every flagged ambiguity as a numbered question. A forced mapping is one of those
questions. Give it (1) the region and what it has to do, (2) the closest blocks
and why each falls short, (3) the mapping you would otherwise take — forced
block, semantic-HTML fallback, or a wrapper block per `extensibility.md` — and
let the answer come back before the blueprint commits to it. A round is the cheap
surface; a blueprint that has already committed is not.

This does not turn every close call into a question. If competent engineers given
this same wireframe and this same block set would converge on the mapping, it is
settled, not raised. So are the degradations already decided elsewhere: a
genuinely one-off ornament takes utility classes, a region that needs more than a
pattern's inputs goes through `extensibility.md`'s four levels before anything is
declared custom, and a tabular region stays `TableRecords` wherever the Data Grid
is not installed. **A composed workaround that the compose-and-disclose rule
already covers is disclosed, not asked** — disclosure is the settled path.
What earns a numbered question is the narrower case where the composition itself
distorts what the design is asking for, and no amount of honest disclosure makes
that a decision the mapper should take alone.

> Scope: this is the block-level statement. The inventory-level criterion — which
> screens exist, how they fuse, what chrome they share — lives in
> `outsystems-screen-inventory` and stays there; it already routes block and
> visual questions here rather than restating them.

### Why this catches the v3 fintech failure

In the v3 fintech run, the agent's plan said "use Card, UserAvatar, IconBadge, ProgressBar, StackedCards, ListItemContent." The execution wrote ZERO instances of those blocks; everything was a `Container` with classes like `hb-stat-card`, `hb-vcard--indigo`, `hb-toggle-card`, `hb-progress-track`. The **plan and the execution diverged** because the agent never committed to specific block names per-region. The block-inventory step closes that gap by requiring an explicit "for THIS region, the block is X" mapping before any code runs.
