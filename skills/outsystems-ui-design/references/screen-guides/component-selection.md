# Component Selection Guide


> **Harvested from:** a curated OutSystems UI screen-guide reference set (`component-selection.md`) (read-only source, harvested 2026-07-13; the tabular-data row was locally corrected 2026-08-19, the accordion-detail row added 2026-08-27, and the master-detail and list-with-popup rows plus the entity-dependents eligibility gate added 2026-09-01 — see Merge-preserved table).
> **Upstream origin:** OutSystems UI pattern reference, curated upstream reference (no further upstream repo cited in source).
> **Merge note:** local corrections preserved where noted in `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.

Choose the right UI component for the content and interaction pattern. Using the wrong component causes usability failures regardless of styling.

## Data Display

| Content Type | Correct Component | Wrong Choice |
|---|---|---|
| Read-only tabular data (structured rows/columns, 10+ items) | Data table (TableRecords) with sort, filter, pagination | Cards (too much scrolling, no column comparison) |
| Spreadsheet-grade tabular data — inline cell editing, column grouping, virtual scrolling over very large datasets | OutSystems Data Grid (`Grid` block) — see `references/data-grid.md` | TableRecords with per-cell Input widgets (rebuilds a grid by hand) |
| Image-heavy browsing (products, files, team) | Card grid (Gallery block or responsive card layout) | Table (images don't fit tabular layout) |
| Hierarchical data (org chart, file tree) | Tree view or nested list with expand/collapse | Flat table (loses hierarchy) |
| Key metrics at a glance | Counter tiles or KPI cards | Table row with numbers (no visual weight) |
| Trends over time | Line or area chart | Table of numbers (pattern invisible) |
| Part-of-whole comparison | Donut or pie chart | Bar chart (harder to see proportions) |
| Category comparison | Bar or column chart | Pie chart (hard to compare similar values) |

## Navigation & Organization

**Three rows below reveal a record's detail in place, and one question settles
before any of them: does the entity have dependents?** An entity that has
dependents — another entity holds a single foreign key reference to it — **cannot
use the list-with-popup or master-detail patterns at all**, so the size gates on
those two rows never come up. Rule them out first, then choose among what is left.

> **Source for the eligibility gate above, and for the same gate in the
> `MasterDetail` and `Popup` rows below** (official ODC documentation, checked
> 2026-09-01 at live upstream `879ee91b`): `docs-odc`
> `src/eap/agentic-development/mentor-web/prompts.md`, "Pattern constraints" —
> *"Entities with dependents: Cannot use popup or master-detail patterns"* — with
> the same two exclusions repeated in its "Select a pattern" rows (*"entities with
> dependents"*; *"Entities with more than 5 attributes or dependent entities"*).
> The definition is the one the same repository's linked requirement-document
> generator prompt gives (`.../mentor-web/resources/mentor-prompt-generator.txt`):
> *"Dependent entities have a single foreign key reference to the target entity."*
> Unlike the attribute ceilings in the rows, this is not a limit the page says
> Mentor resolves by switching pattern — that sentence is scoped to an entity
> exceeding a pattern's *attribute* limit — so the exclusion is stated and nothing
> is claimed about what a dependent entity yields instead.

| Pattern | Correct Component | Wrong Choice |
|---|---|---|
| Mutually exclusive content sections | Tabs (Tabs block) | Stacked accordions (forces users to manage open/close state) |
| Supplementary/optional content | Accordion (Accordion block) | Tabs (hides content that may need simultaneous viewing) |
| Sequential flow | Wizard with step indicator | Single long form (overwhelming) |
| Breadcrumb trail for deep navigation | Breadcrumbs (Breadcrumbs block) | Back button only (loses context) |
| Date selection | Date picker (DatePicker block) | Free text input (error-prone formatting) |
| Date range selection | Date range picker (DatePickerRange block) | Two separate date pickers (disconnected UX) |
| Compact record browsing with the detail revealed in place | Card list with an `Accordion` detail — only where the detail is at most **5 detail fields**, with `Accordion.MultipleItems` left at its `False` default so one item is open at a time | Accordion detail with more than 5 fields, or a comparison that needs several details open at once — use a sidebar or master-detail layout instead |
| Browsing a list and inspecting the selected record beside it | `MasterDetail` split — where the list portion is a table, at most **5 attributes** in it (see `references/screen-guides/master-detail.md`) | A table list portion carrying more than 5 attributes — make the list portion a card list or gallery instead; or an entity with dependents, which cannot use this pattern at all |
| Viewing or editing a record over the list, without navigating away | `Popup` widget over the list — only for entities with **5 or fewer non-ID attributes** | A popup over an entity with more non-ID attributes than that — such entities use the table pattern instead; or an entity with dependents, which cannot use this pattern at all |

> **Source for the three pattern-limit rows above** — accordion detail, master-detail
> list portion, and list-with-popup (official ODC documentation; the accordion row was
> checked 2026-08-27, the other two 2026-09-01 at upstream `879ee91b`): `docs-odc`
> `src/eap/agentic-development/mentor-web/prompts.md`. Its "Select a pattern" table
> carries all three ("max 5 fields in detail" / "Avoid when … more than 5 detail fields
> or multiple sections need to be open"; "Browse and inspect a record (max 5 attributes
> in table view)"; "Entities with 5 or fewer non-ID attributes"), and its "Pattern
> constraints" list states two of them as limits Mentor enforces — *"Popup and
> accordion: Max 5 non-ID attributes"* and *"Master detail table view: Max 5 attributes
> in list portion"* — by switching an entity that exceeds a limit to a compatible
> pattern rather than by failing. The accordion's one-open-at-a-time half comes from the
> same page ("Only one accordion item expands at a time to avoid visual clutter") and is
> also the block's own default: `Accordion.MultipleItems` is `False`
> (`references/patterns/content.md`).

## Form Controls

| Input Need | Correct Component | Wrong Choice |
|---|---|---|
| Select one from 2-5 options | Radio buttons (RadioGroup) | Dropdown (overhead for few options) |
| Select one from 6+ options | Dropdown (Dropdown widget) or search dropdown (DropdownSearch block) | Radio buttons (too much vertical space) |
| Select one from 20+ options | Searchable dropdown (DropdownSearch block) | Plain dropdown (hard to find items) |
| Select multiple from any set | Checkboxes (Checkbox widgets) | Radio buttons (single-select only — misuse) |
| Boolean on/off | Toggle switch (Switch widget) | Checkbox (switches convey immediate effect) |
| Long text | Text area (TextArea widget) | Single-line input (truncates content) |
| Free text where structured input exists | N/A — use the structured component | Free text input (error-prone) |

## Actions & Feedback

| Interaction | Correct Component | Wrong Choice |
|---|---|---|
| Single primary action | Button (btn-primary) | Link styled as button (inconsistent affordance) |
| Related actions (2-3) | Button group or split button | Separate scattered buttons (no grouping) |
| Destructive action confirmation | Custom modal with clear explanation | Browser dialog / window.confirm() (not branded, no context) |
| Secondary information on hover | Tooltip (Tooltip block) | Modal (too heavy for glanceable info) |
| Detailed preview on hover | Popover / hover card | Modal (interrupts flow) |
| Status indicators | Tags/badges with semantic colors | Plain text (no visual weight) |
| Inline simple messages | Toast / snackbar notification | Full modal (too disruptive for simple confirmation) |

## Universal Rules

- Same action = same control everywhere. Don't mix toggles and checkboxes for the same purpose on the same screen
- Labels always persistent above inputs — never use placeholder text as the only label (disappears on entry)
- Checkboxes for multi-select, radio buttons for single-select — never misuse
- Goal-oriented search (finding a specific item) → pagination. Casual browsing → infinite scroll is acceptable
- Progressive disclosure for complex forms: show only relevant fields per step, not all at once
- Data Grid is a **separate Forge component installed per tenant**, not a built-in widget. Where it is not installed, TableRecords is the correct tabular answer — state which the design assumes
