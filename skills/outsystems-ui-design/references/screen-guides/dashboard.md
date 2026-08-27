# Dashboard / Analytics Screen


> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `.claude/skills/references/dashboard.md` (harvested 2026-07-29; upstream body REJECTED — local softened body retained, see Merge-preserved table).
> **Merge note:** local corrections preserved where noted in `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.

## ⛔ FIRST: is there a wireframe? Then this section does not apply.

**If you are working from a wireframe, sketch, or any approved design source, map what
it shows and nothing else.** No charts, no counters, no summary list unless the design
has them. **A wireframe that shows no chart is a decision, not an omission.**

This is the `outsystems-ui-design` skill's governing rule and it **overrides everything
below**: inventing UI the user never approved is the precise failure this skill exists to
prevent. If a region seems missing, *ask* — do not fill it in.

Phase 3 evidence: this guide was pointed at a **launcher screen with zero numeric data**
— four cards listing API names, nothing to count, nothing to group, nothing to plot — and
the section below still demanded a KPI row, charts, and a summary list. It is written for
a *prompt-only* dashboard, and it is actively dangerous applied to a designed one.

## Anatomy

A dashboard presents a high-level overview of key metrics and recent activity.

**These are the sections a dashboard *may* have — a menu, not a checklist.** When a
wireframe is present it decides which of them exist; the wireframe wins. Sections
listed here and absent from the design are **not** missing.

Sections, top to bottom:

1. **Page header**: Title (heading3) + optional date range or period selector
2. **KPI counter row**: 3-5 counter tiles in a responsive grid (columns layout, 3-4 columns desktop). Each tile contains:
   - Icon or small graphic representing the metric
   - Large numeric value (heading2 or heading3 weight)
   - Label describing the metric
   - Optional trend indicator (up/down arrow + percentage change)
3. **Charts row**: 1-2 charts showing trends or distributions (bar, line, donut). Place in a 2-column layout or full-width depending on chart count
4. **Summary list**: Recent or top items (5-10 rows), sorted by recency or priority. Use a compact data table (TableRecords) or card list (List widget)
5. **Optional filter bar**: Date range selector, category dropdown, status filter — placed above the KPI row or in the header

## Layout

- Use the `Columns2` / `Columns3` layout blocks to arrange sections side-by-side. Without them, all sections stack vertically. The full set is `Columns2`–`Columns6` plus four asymmetric splits — see `references/patterns/adaptive.md`
- Counter tiles: wrap 3 counters in a `Columns3`, or 2 in a `Columns2` — so they appear as a row
- Charts: wrap 2 charts of comparable weight in a `Columns2` so they appear side-by-side
- Two charts of *unequal* weight — a trend line beside a small donut — go in an asymmetric split instead: `ColumnsSmallLeft` / `ColumnsSmallRight` (~33/67) or `ColumnsMediumLeft` / `ColumnsMediumRight` (~60/40), putting the part-to-whole chart in the narrow column. Keep a summary list out of the narrow column; a table needs the width
- Summary list: place as a flat section below the columns — it takes full width
- See the `VO_AddSalesDashboardWithChartAndAnonymousAccess` example for the exact code pattern

## Styling

- Counter tiles: card container with soft shadow, border-radius, and internal padding. Background neutral-0 or neutral-1. Icon on the left or top, value prominently sized
- Charts: card container with title heading and padding. Ensure minimum height for readability (~300px)
- Summary list: compact table with striping for readability, or card-based list items
- Trend indicators: semantic colors — green/success for positive, red/error for negative, neutral for flat
- Grid: use gutter-m or gutter-base between columns. Add phone-break-all for responsive stacking

## Data Patterns

- Each KPI counter needs its own data source (aggregate or data action) — do not share data sources between counters
- Charts need aggregated/grouped data — typically a separate data source per chart with appropriate grouping
- Summary list: sorted by date descending or by priority, limited to 5-10 rows (no pagination needed)
- Optional: auto-refresh timer or manual refresh button to keep data current

## How to Decide What to Show — **prompt-only, no design source**

Everything in this section applies **only** when the user asked for a "dashboard" in prose
and gave you **no wireframe, sketch, or design source at all**. If you have one, stop and
re-read the block above.

A prompt-only dashboard is usually not just counters — prefer charts and a summary list
where the data model supports them. Use the data model to decide:

1. **Counters**: One count per entity the user named. **If the user named no entities, do
   not invent them** — a counter over an entity nobody asked for is fabricated data
   lineage, and it flows straight into whatever gets built. Ask which entities matter.
2. **Charts**: Examine each entity's attributes for groupable fields:
   - A `Status`, `State`, `Type`, `Category`, `Priority`, or `Level` attribute → Bar or Donut chart grouping records by that attribute's values
   - A `CreatedAt`, `Date`, `DueDate`, or datetime attribute → Line chart showing records over time (grouped by month/week)
   - Pick the 1-2 most meaningful groupings. Prefer Status-based charts (they show operational health)
3. **Summary list**: Pick the entity with a date/time attribute and show the 5-10 most recent records. Display: primary name/title + status + date + assigned user (if applicable). This gives users a "what happened recently" view.

## Responsive Behavior

- Desktop: 3-4 column KPI grid, 2-column charts, full-width summary
- Tablet: 2-column KPI grid, charts stack vertically
- Phone: single-column everything, charts full-width, summary list simplified
