# Master-Detail Screen


> **Harvested from:** a curated OutSystems UI screen-guide reference set (`master-detail.md`) (read-only source, harvested 2026-07-13; the list-portion attribute ceiling and the dependents eligibility gate were both added locally 2026-09-01 — see Merge-preserved table).
> **Upstream origin:** OutSystems UI pattern reference, curated upstream reference (no further upstream repo cited in source).
> **Merge note:** local corrections preserved where noted in `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.

## ⛔ FIRST: does the entity have dependents? Then this pattern is not available.

**An entity that has dependents cannot use the master-detail pattern.** A dependent
entity is one holding a single foreign key reference to this one. This is an
eligibility question rather than a sizing one, and it is settled before any of the
anatomy below applies — before the list portion's attribute ceiling comes up at all.

Where a design source shows a split over such an entity, say so and ask. The
wireframe still decides the layout, as it does everywhere in this bundle; what a
design run must not do is map the split without saying that the documentation rules
the pattern out.

> **Source for the eligibility gate** (official ODC documentation, checked
> 2026-09-01 at live upstream `879ee91b`): `docs-odc`
> `src/eap/agentic-development/mentor-web/prompts.md` states it twice — the "Pattern
> constraints" bullet (*"Entities with dependents: Cannot use popup or master-detail
> patterns"*) and the "Select a pattern" row, which gives *"entities with
> dependents"* as a case to avoid the pattern in. The definition above is the one
> the same repository's linked requirement-document generator prompt gives
> (`.../mentor-web/resources/mentor-prompt-generator.txt`): *"Dependent entities
> have a single foreign key reference to the target entity."*
>
> This is **not** one of the attribute limits that same list says are resolved by
> switching to a compatible pattern — that sentence is scoped to an entity exceeding
> a pattern's *attribute* limit, and the page does not say what a dependent entity
> yields instead. So this guide does not say either: it states the exclusion, and
> stops where the documentation does.

## Anatomy

A split-panel layout showing a selectable list on one side and the selected record's detail on the other. Best for workflows where users browse and inspect records without full page navigation.

1. **List panel** (left, ~1/3 width): Compact list of records showing primary identifier + brief metadata. **Where the list portion is a table, show at most 5 attributes** — for more than that, the list portion becomes a card list or gallery instead. Includes:
   - Search input at top
   - Scrollable list of items
   - Selected item highlighted with distinct background
   - Item count indicator
2. **Detail panel** (right, ~2/3 width): Full detail view of the selected record (follows the [detail-view recipe](detail-view.md)):
   - Record header with title + status
   - Label-value field pairs
   - Related data or action buttons
   - Placeholder / empty state when no record is selected ("Select an item to view details")
3. **Optional action bar**: Above the split, with bulk actions or "Add New" button

> **Source for the list-portion attribute ceiling** (official ODC documentation,
> checked 2026-09-01 at upstream `879ee91b`): `docs-odc`
> `src/eap/agentic-development/mentor-web/prompts.md` carries it three times — the
> "Select a pattern" table row (*"Browse and inspect a record (max 5 attributes in
> table view)"*), the "Pattern constraints" bullet (*"Master detail table view: Max 5
> attributes in list portion"*), and the pattern's own section (*"When using table
> pattern for the list portion, limit to 5 attributes. For more attributes, use card
> list or gallery pattern"*). That constraint list opens by stating that Mentor
> switches an entity exceeding a pattern's attribute limit to a compatible pattern —
> so overrunning this ceiling does not fail loudly, it quietly yields a different
> screen than the one designed. The ceiling is stated for the **table** list portion;
> the page's own remedy for more attributes is to make the list portion a card list or
> gallery, not to widen the table.

## Layout

- Split container: responsive columns (ColumnsSmallLeft block) — ~33% left, ~67% right
- List panel: fixed height with vertical scroll, search pinned at top
- Detail panel: scrolls independently
- Responsive collapse: on phone, show only the list; tapping an item navigates to a full-screen detail view

## Styling

- List items: padding-s vertically, border-bottom divider between items
- Selected item: background-primary with text-neutral-0, or background-neutral-2 for subtle highlight
- List hover: background-neutral-1 on hover
- Detail panel: card container or plain background with padding
- Split gutter: minimal (gutter-s or gutter-none with a vertical border separator)

## Data Patterns

- List aggregate: fetch all records (or filtered subset) with minimal columns for compact display — at most 5 attributes where the list portion is a table (see the source note under Anatomy)
- Detail aggregate: fetch full record by the selected Id (local variable tracking selection)
- On list item click: update selected Id, detail panel re-fetches
- Handle empty selection: show placeholder in detail panel initially

## Responsive Behavior

- Desktop/Tablet: side-by-side split layout
- Phone: list-only view; selecting an item navigates to a separate detail screen (or uses a slide-in panel)
