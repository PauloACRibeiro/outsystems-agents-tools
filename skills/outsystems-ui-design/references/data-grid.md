---
name: outsystems-data-grid
description: Catalog of the OutSystems Data Grid blocks for ODC (Grid, the column blocks, ContextMenu items, SearchData). Use when a design needs spreadsheet-grade interaction — inline cell editing, grouping, virtual scrolling — rather than a read-only table.
---

# OutSystems Data Grid (ODC)

> **Origin:** written for this skill 2026-08-19 from the official ODC documentation.
> Not harvested from the upstream reference set — that set has no Data Grid counterpart.
> See `maintenance/refresh-checklist.md` for the refresh procedure.
>
> **Citation rule (enforced by this skill's reference-bundle test suite):** every claim
> below carries an adjacent source key resolving against `## Sources`. `[design]` marks this
> skill's own design guidance rather than a platform-behaviour claim, and `Unverified`
> marks a claim the documentation does not settle. Nothing here is sourced from any
> private repository.

Data Grid is a supported component available in Forge `[overview]` `[forge]`, and it applies to the
OutSystems UI framework only `[overview]`. It is built on top of the third-party Mescius
Data Grid `[ref]`. It is installed from **ODC Portal > Forge**, after which the elements
you want are added as public elements in your web app `[overview]`; the fetch walkthrough
repeats both as prerequisites `[fetch]`.

**Availability is a design-time question** `[design]`. A design-time skill cannot check
which components a tenant has installed, so state which widget the design assumes rather
than silently speccing `Grid` `[design]`.

## Data Grid or the built-in table

| The design shows | Map to | Source |
|---|---|---|
| Simple, sequential data in a lightweight widget with no inline editing — the docs route this away from Data Grid and to lists, editable through forms | `TableRecords` (this skill's name for the built-in table widget) | `[overview]` |
| Any read-only tabular region, where no Forge install can be assumed — the fetch-and-display walkthrough uses the built-in List or Table widget with no install step | `TableRecords` | `[display]` |
| Viewing, exploring and editing large amounts of data in a familiar spreadsheet interface | `Grid` (Data Grid) | `[overview]` |
| Data selection and editing in a familiar interface; data sorting by parameter; data grouping; virtual scrolling — the four named key features | `Grid` | `[overview]` |
| Cells edited by double-clicking, with `AllowColumnEdit` set True | `Grid` | `[edit]` |
| Copy, copy-with-headers, export to CSV/Excel, freeze/unfreeze columns from a right-click menu | `Grid` + `ContextMenu` | `[ref]` |

Reach for `Grid` when the *spreadsheet interaction itself* is the requirement; editing a
handful of records is a form `[design]` — which is also where the overview page sends
simple list data `[overview]`.

## Blocks

| Block | Use when | Source |
|---|---|---|
| `Grid` | The container that displays the grid — the block placed on the screen | `[ref]` |
| `TextColumn` | Text field | `[ref]` |
| `NumberColumn` | Number field | `[ref]` |
| `CurrencyColumn` | Money field — takes an additional `CurrencyOptionalConfigs` | `[ref]` |
| `DateColumn` / `DateTimeColumn` | Date / date-time field, each with its own optional-configs input | `[ref]` |
| `CheckboxColumn` | Boolean field | `[ref]` |
| `DropdownColumn` | Field constrained to a list of options — `DropdownOptionList` is **mandatory** | `[ref]` |
| `ImageColumn` | Image field; `ImageUrlFromBinding` must name a field holding a URL | `[ref]` |
| `ActionColumn` | Renders column links, via `TextFixed` or `TextFromBinding` | `[ref]` |
| `ContextMenu` | Right-click menu; default options are copy, copy with headers, export to CSV/Excel, freeze and unfreeze columns | `[ref]` |
| `MenuItem_*` blocks — `_Copy`, `_Copy_WithHeaders`, `_Export`, `_Export_ToCSV`, `_Export_ToExcel`, `_Export_ToExcelWithoutStyles`, `_Rows_Add`, `_Rows_Delete`, `_Column_Freeze`, `_Column_Unfreeze`, `_Column_FreezeUnfreeze`, `_Separator`, `_CustomOption` | Individual entries inside `ContextMenu` | `[ref]` |
| `SearchData` | Searching for data on an already-loaded grid | `[ref]` |
| `OnFiltersChange` | Handling the grid's filter-change event, which fires with all currently active filters | `[ref]` |

Every column block takes a mandatory `Header` giving the column title `[ref]`. All column
blocks except `ActionColumn` and `ImageColumn` take a mandatory `Binding` naming the field
`[ref]`; the expected format is `"{EntityName}.[FieldName]"`, and `"EntityName.FieldName"`
is also accepted — for example `"{Product_Sample}.[Name]"` `[ref]`.

## Grid inputs

| Input | Type | Notes | Source |
|---|---|---|---|
| `Data` | Text — **mandatory** | The content displayed in the grid. Best set by fetching from the database and converting to JSON with either the `ArrangeData` action or the JSON Serialize node | `[ref]` |
| `IsDataFetched` | Boolean — **mandatory** | Defines whether an empty state shows while data is loading; bound to the data action's own `IsDataFetched` | `[ref]` |
| `GridHeight` | Integer — optional | The container's height in pixels, default 400 | `[ref]` |
| `HasGroupPanel` | Boolean — optional | The drag-columns-to-group panel, default True | `[ref]` |
| `OptionalConfigs` | Structure — optional | Carries `AllowColumnEdit`, `AllowColumnReorder`, `AllowColumnResize`, `AllowColumnSort`, `RowHeight` and `RowsPerPage` as one input | `[ref]` |
| `RowHeight` | Integer — optional | Row height in pixels, default 48 | `[fetch]` |
| `RowsPerPage` | Integer — optional | Rows displayed per page, default 50 | `[fetch]` |
| `AllowColumnReorder` / `AllowColumnResize` / `AllowColumnSort` | Boolean — optional | Column reorder, resize and sort, each defaulting to True | `[fetch]` |
| `ShowAggregateValues` | Boolean — optional | Shows a line below the grid with column values aggregated; default False | `[fetch]` |
| `ServerSidePagination` | Boolean — optional | Enables server-side pagination; default False | `[fetch]` |
| `KeyBinding` | Text — optional | Names the data's primary key field, format `'Entity.Attribute'`, for server-side validations | `[fetch]` |
| `SanitizeInputValues` | Boolean — optional | Whether values entered in the grid are sanitized | `[fetch]` |
| `RowHeader` | RowHeader Identifier — optional | What shows in the grid's first column; default `Entities.RowHeader.RowNumber` | `[fetch]` |

*Unverified:* the two ODC pages disagree on `AllowColumnEdit`'s default — the Grid block
properties table gives False `[fetch]` while the `OptionalConfigs` structure gives True
`[ref]`. Spec the value you want explicitly rather than relying on the default `[design]`.

Placeholders on `Grid` are `ContextMenu`, `Loading` (shown while data is fetched from the
server), `NoResults` (shown when no results return), `GridColumns`, and
`ServerSideInformation`, which adds no functionality and only guides server-side
pagination `[fetch]`. Column blocks are dragged into that columns placeholder, which the
reference page names `GridColumnsPlaceholder` `[ref]`.

## Spec conventions

- **`Data` is Text holding JSON.** The screen's data action outputs a **Text** parameter,
  built by placing a `JSONSerialize` after the aggregate and assigning its `JSON` output;
  the Grid's `Data` then binds to that data-action output `[fetch]`. The component's own
  `ArrangeData` action is the documented alternative `[ref]`. Name the producer in the
  spec and leave the serialization to the implementer `[design]`.
- **`IsDataFetched` is mandatory** and binds to the data action's own `IsDataFetched`
  property `[fetch]`, so it is not a property that can be left at a default `[ref]`.
- **Editing needs a save affordance.** Editing a cell marks that cell and its line with a
  change indicator `[edit]`; a Save button in the screen's Actions placeholder runs a
  client action that calls `GetChangedLines`, deserializes the changed JSON, calls a
  server action to update the database, and finally calls `MarkChangesAsSaved` to clear
  the indicators `[save]`. Show that Save affordance in any editable-grid design
  `[design]`.
- **Bulk row add and remove belong to the context menu** — `MenuItem_Rows_Add` inserts as
  many rows as the user selects and `MenuItem_Rows_Delete` deletes the selected rows
  `[ref]` — so do not invent a separate toolbar for them `[design]`.
- **`Grid` has no Title input** — neither the reference page's input list `[ref]` nor the
  Grid block properties table `[fetch]` carries one, so wrap the grid in `CardSectioned`
  and use its `Title` placeholder when the design shows a titled panel `[design]`.

## Anti-patterns

- ❌ Binding `Data` to an aggregate list such as `GetProducts.List` — the input is Text,
  and the documented flow passes `GetProducts.List` to `JSONSerialize` first, binding the
  Grid to the serialized output `[fetch]`.
- ❌ Omitting `IsDataFetched` — it is mandatory and it is what defines the empty state
  shown while data loads `[ref]`.
- ❌ Speccing `Grid` without stating that the Forge component must be installed and its
  public elements added to the app `[overview]`.
- ❌ Using `Grid` for simple, sequential, read-only data — the overview page routes that
  to lists, edited through forms, rather than to Data Grid `[overview]`.
- ❌ Styling `Grid` rows with the table styling utilities this skill documents for
  `TableRecords` in `screen-guides/list-table.md` — `Grid` is built on the third-party
  Mescius Data Grid `[ref]` and applies row CSS through its own `AddClass` and
  `RemoveClass` client actions `[ref]`.
- ❌ Assuming a `Grid` design is portable to a tenant that has not installed the
  component; `TableRecords` is the fallback the design should name `[design]`.

## Sources

Every citation key above resolves here. Mirror paths are read-only copies of the official
OutSystems documentation under the workspace public-knowledge tree, repo `docs-odc`.

| Key | Source |
|---|---|
| `[overview]` | `docs-odc` `src/eap/building-apps/ui/patterns/interaction/data-grid/data-grid-overview.md` — <https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/user_interface/patterns/interaction/outsystems_data_grid_for_odc/> |
| `[fetch]` | `docs-odc` `src/eap/building-apps/ui/patterns/interaction/data-grid/data-grid-fetch-data.md` — <https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/user_interface/patterns/interaction/outsystems_data_grid_for_odc/fetch_data_for_outsystems_data_grid/> |
| `[edit]` | `docs-odc` `src/eap/building-apps/ui/patterns/interaction/data-grid/data-grid-edit.md` — <https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/user_interface/patterns/interaction/outsystems_data_grid_for_odc/edit_data_in_outsystems_data_grid/> |
| `[save]` | `docs-odc` `src/eap/building-apps/ui/patterns/interaction/data-grid/data-grid-save.md` (mirror path only — the published URL was not verified from here) |
| `[ref]` | `docs-odc` `src/eap/reference/data-grid-ref.md` — <https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/odc_data_grid_reference/> |
| `[display]` | `docs-odc` `src/eap/building-apps/ui/interaction/fetch-display.md` (mirror path only — the published URL was not verified from here) |
| `[forge]` | Public Forge component listing — <https://www.outsystems.com/forge/component-overview/15929/outsystems-data-grid-odc> |
| `[design]` | This skill's own design guidance — not a platform-behaviour claim, and deliberately uncited |
