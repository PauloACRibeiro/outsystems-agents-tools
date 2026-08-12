---
name: osui-screen-templates
description: Catalog of the 17 OutSystems UI Screen Templates (List, Detail, Form, Dashboard, etc.) with the requirement-to-template map, the canonical layout placeholder order, and screen-reachability rules. Use when confirming a screen archetype, choosing the template a blueprint's screen corresponds to, or designing app chrome/navigation content.
---

# OutSystems UI — Screen Templates

> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `ui-frameworks/outsystems-ui/screen-templates.md` (harvested 2026-08-05).
> **Merge note:** design-filtered harvest — the aggregate/LocalVariable/ScreenAction composition walkthroughs are deliberately excluded per the design-only boundary contract (`maintenance/refresh-checklist.md`); the catalog, mapping, placeholder-order, and reachability facts are preserved.
> See `maintenance/refresh-checklist.md` for the refresh procedure.

> **What:** Pre-built screens that ship with OutSystems UI (UIFlow `LSG_ScreenTemplates`).
> For OUD these are **reference context**: they tell you which stock archetype a
> wireframe most resembles, which strengthens the Step 1 archetype read and gives
> OMI a concrete scaffold hint in `evidence_boundary.review_notes`. OUD never
> scaffolds a template itself.

## Catalog

| # | Template | Group | Purpose |
|---|---|---|---|
| 1 | `AdminDashboard` | Dashboards | Counter cards + paginated table with multi-entity joins. |
| 2 | `BulkActions` | Lists | Table with checkbox column + bulk-action toolbar. |
| 3 | `Dashboard` | Dashboards | KPI counters (`Columns3` + `Counter`) + chart card + recent-items list. |
| 4 | `Detail` | Details | Read-only/editable form bound to a by-id data source. |
| 5 | `FourColumnGallery` | Catalogs | 4-col Gallery + sidebar filters (search, category, price). |
| 6 | `HorizontalDetail` | Details | `Columns2` layout with read-only fields. |
| 7 | `List` | Lists | Simple paginated `TableRecords`. |
| 8 | `ListWithFilters` | Lists | Search input + dropdown filter + sortable columns + pagination. |
| 9 | `MasterDetail` | Lists | Side-by-side list + detail panes. |
| 10 | `OnboardingAnimation` | Catalogs | Multi-step onboarding with animations. |
| 11 | `ProductCatalog` | Catalogs | Gallery + category tabs + product cards. |
| 12 | `ProductDetail` | Catalogs | Product image carousel + detail + add-to-cart. |
| 13 | `ProductFeature` | Catalogs | Feature highlight layout. |
| 14 | `RequestCreation` | Details | Create/Edit form with FK dropdown, date picker, file upload. |
| 15 | `RequestDetail` | Details | Read-only detail with status timeline. |
| 16 | `RequestManagement` | Dashboards | Counter cards + status tabs + paginated table. |
| 17 | `TransactionsDashboard` | Dashboards | Chart + transaction list + date-range filter + summary counters. |

## Requirement → template

| Requirement | Template | Why |
|---|---|---|
| "list", "browse", "show all" | `List` | Simple paginated table. |
| "list with filters/search/sort" | `ListWithFilters` | Search + dropdown filter + column sort. |
| "view record / detail" | `Detail` or `RequestDetail` | Form bound to one record. |
| "create new / edit" | `RequestCreation` | Create/Edit form with save action. |
| "dashboard / overview / KPIs" | `Dashboard` | Counter row + chart + recent list. |
| "admin / management" | `AdminDashboard` or `RequestManagement` | Counters + full paginated table. |
| "catalog / product grid" | `FourColumnGallery` or `ProductCatalog` | Gallery with sidebar filters. |
| "bulk actions / multi-select" | `BulkActions` | Table with checkbox column + toolbar. |
| "master-detail / split view" | `MasterDetail` | Left list + right detail. |

**⚠️ Templates are not archetypes.** OUD's 14 screen-guide archetypes classify the
*wireframe*; this catalog names the *stock scaffold* the built screen would start
from. They usually align (`list-table` → `List`/`ListWithFilters`) but the
wireframe wins whenever the two disagree — the archetype-guide caution in
SKILL.md applies here unchanged. A template hint never licenses adding regions
the wireframe does not show.

## Canonical layout placeholder order (every screen)

Every screen wraps content in one layout block. **The layouts do not share one
placeholder set, and there is no `ActionButton` on any of them.**

[`layouts.md`](layouts.md#placeholder-structure) is the single source: it lists
the layouts, and for each one the placeholders it actually exposes, measured
from real apps' own `Layouts` flows. Read it before emitting a blueprint — and
read the *target app's* `Layouts` flow before trusting either, since a
placeholder name that does not exist on the chosen layout fails at build time,
after the design has been approved.

That includes **where the app's `Menu` already lives**, which differs per
layout and determines which placeholders a screen may fill at all.

What the common placeholders are for, where the chosen layout has them:

| Placeholder | Typical content |
|---|---|
| `Title` | The screen title as `AdvancedHtml Tag="h1"`. |
| `Actions` | Screen-level primary buttons ("New course"). |
| `MainContent` | The screen body — everything OUD's `main_content` describes. |
| `Breadcrumbs` | Breadcrumb trail or a back link. Often empty; strip template-seeded default crumbs — see `ui-reference.md`. |

Two facts that matter at design time:

- **The screen title lives in the `Title` placeholder, never in `MainContent`.**
  A wireframe's page heading maps to the layout's `Title` slot (blueprint
  `app_chrome.page_title`), not to a `main_content` region.
- Empty placeholders still exist on the built screen — a wireframe with no
  breadcrumbs is normal, not a missing region.

## Reachability (design fact for app chrome)

Every screen must be reachable from at least one navigation link — an orphaned
screen is a build defect the design can prevent:

| Screen kind | Where its entry link lives |
|---|---|
| No record-id input (lists, dashboards, launchers) | The app menu — a `Link` added **once** inside `Common\Menu`'s `PageLinks` container, recorded in the blueprint as `app_chrome.menu`. The screen itself adds nothing. |
| Takes a record id (detail, edit) | A parent screen — table row link, action button, or contextual link. |

Design implication: a list/dashboard screen that is missing from
`app_chrome.menu` should be flagged during the loop; a detail/edit screen's
wireframe should show (or the pattern tree should note) the parent-screen
affordance that reaches it, and "create new" affordances imply the parent
passes an empty id.

## Anti-patterns

- **Don't put screen titles in `MainContent`.** They go in the `Title` placeholder.
- **Don't design a screen no navigation reaches.** Name its entry point.
- **Don't treat a template's anatomy as license to invent regions.** The
  wireframe wins; the template is a scaffold hint for OMI, nothing more.
