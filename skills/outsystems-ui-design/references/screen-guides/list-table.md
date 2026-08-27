# List / Data Table Screen


> **Harvested from:** a curated OutSystems UI screen-guide reference set (`list-table.md`) (read-only source, harvested 2026-07-13; the Data Grid variant was added locally 2026-08-19 — see Merge-preserved table).
> **Upstream origin:** OutSystems UI pattern reference, curated upstream reference (no further upstream repo cited in source).
> **Merge note:** local corrections preserved where noted in `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.

## Anatomy

A list screen displays a collection of records with search, filtering, sorting, and pagination. Expected sections:

1. **Page header**: Title (heading3) + optional "Add New" button (primary action, top-right)
2. **Filter bar**: Responsive row containing:
   - Search input with search icon (input-with-icon pattern)
   - Status dropdown filter
   - Category or type dropdown filter
   - Optional: date range picker, additional filters in a collapsible "Advanced Filters" section
3. **Data table** (TableRecords): Sortable columns with header click-to-sort. Columns typically:
   - Name/title (primary identifier, often a clickable link to detail view)
   - Status (displayed as colored tag/badge)
   - Key attributes (date, category, owner, value)
   - Action column: Edit, Delete, or "Details" links
4. **Pagination** (Pagination block): Below the table, showing page numbers or prev/next navigation
5. **Empty state**: Displayed when no records match filters — icon + message + "Clear filters" or "Add first item" action
6. **Optional bulk actions**: Select-all checkbox in header, bulk delete/export buttons above or below table
7. **Optional export**: PDF and CSV export buttons

## Variant: Data Grid (spreadsheet-style)

When the requirement is editing many rows in place — inline cell edit, column grouping,
virtual scrolling over a large dataset, copy/export from a right-click menu — the table
is the OutSystems Data Grid `Grid` block, not TableRecords. It replaces sections 3 and 4
of the anatomy above: sorting, filtering, grouping and paging live inside the grid, so
there is no separate Pagination block, and the empty state moves into the grid's
`NoResults` placeholder. Data Grid is a **separate Forge component installed per tenant**,
so it is a choice the design has to declare — where it is not installed, TableRecords
stays correct. See `references/data-grid.md` for the block catalog and the two binding
traps (`Data` takes serialized JSON Text; `IsDataFetched` is mandatory).

## Variant: Card Grid / Gallery

For image-heavy content (products, assets, team members), replace the table with a responsive card grid (Gallery block or List widget with card items). Each card: thumbnail/image + title + key metadata + action button. Use 3-4 columns desktop, 2 tablet, 1 phone.

## Layout

- Filter bar: responsive columns (ColumnsSmallLeft or Columns2) — search on left, dropdowns on right. Stack on phone
- Table: full-width with horizontal scroll on narrow screens if many columns
- Pagination: centered below table with margin-top-base
- Empty state: centered in the table area with generous padding

## Styling

- Table: striped rows for readability (table-row-stripping). Compact rows (table-row-small) for data-dense views
- Status column: use tag/badge pattern with semantic background color (success for active, warning for pending, error for blocked, neutral for draft)
- Action links: small buttons or text links. Destructive actions (delete) visually separated or confirmable
- Filter bar: margin-bottom-base between filter row and table
- Search input: full-width within its column, with clear/reset capability

## Data Patterns

- Main aggregate with dynamic filters (search keyword, status, category), sorting, and pagination (MaxRecords + StartIndex)
- Separate aggregate or static entity query for filter dropdowns (status options, category options)
- Count query or total count from main aggregate for pagination display
- Sort by: default to name or date ascending; allow column header sort toggle

## Responsive Behavior

- Desktop: filter bar as horizontal row, full table with all columns
- Tablet: filter bar stacks to 2 rows, table may hide lower-priority columns
- Phone: filter bar stacks vertically, table switches to card-based list layout or horizontal scroll
