---
name: outsystems-charts
description: Catalog of the OutSystems Charts widgets (Charts v3) — area, bar, column, donut, line, pie, radar — with the chart add-ons and the inputs each widget actually carries. Use to pick the right chart widget and add-ons for a spec when the design contains a chart.
---

# OutSystems Charts

> **Origin:** rewritten for this skill 2026-09-03 from the official OutSystems documentation
> and the official OutSystems Charts showcase. It supersedes the 2026-07-13 harvest from the
> upstream reference set: that harvest named three charts no OutSystems source lists, missed
> the Radar chart and two add-ons, and framed the version one major release behind.
> See `maintenance/refresh-checklist.md` for the refresh procedure.
>
> **Citation rule (enforced by this skill's reference-bundle test suite):** every claim below
> carries an adjacent source key resolving against `## Sources`. `[design]` marks this skill's
> own design guidance rather than a platform-behaviour claim, and `Unverified` marks a claim the
> documentation does not settle. Nothing here is sourced from any private repository.

Charts are widgets dragged onto a screen from the ODC Studio Toolbox `[odc-intro]`, and the
per-chart pages carry the note that they apply to the OutSystems UI framework only
`[odc-donut]` `[odc-bar]` `[odc-radar]`.
The current set is **available from OutSystems Charts v3.0.0**, and ODC generates the charts with
Highcharts 13.0.0 `[odc-intro]`.

**Charts v1 is supported, not superseded.** OutSystems states that v1 will not be deprecated and
remains supported, that the only distinction is that v1 will not continue to be evolved, and
recommends — without obligating — a migration `[showcase]`. The add-ons are what settle the
version for a design: the add-on blocks are **not compatible with Charts v1** `[showcase]`, so a
design that shows a custom legend, a styled axis or per-series styling has already chosen the
current charts `[design]`.

## Charts

| Widget | Use when | Source |
|---|---|---|
| **Column Chart** | Comparing values across categories — rectangular bars along the Y-axis, bar height representing the value for a category | `[odc-intro]` |
| **Bar Chart** | The same comparison read horizontally — bars along the X-axis, bar length representing the value | `[odc-intro]` |
| **Line Chart** | Each point is a single value and the points are joined by a line to depict a trend, usually over a period of time | `[odc-intro]` |
| **Area Chart** | The line-chart shape with a coloured area below the line — data points plotted and connected by a line | `[odc-intro]` |
| **Pie Chart** | Part-to-whole — a circular graph of sections, each section a category sized by its value | `[odc-intro]` |
| **Donut Chart** | Part-to-whole in rings rather than sections, with a hole whose size is the `InnerSize` input | `[odc-intro]` `[odc-donut]` |
| **Radar Chart** | Multivariate data in a two-dimensional chart plotted along a radial axis; also called a polar chart | `[odc-intro]` |

That is the whole collection — the ODC page, the O11 Charts API v2 reference and the official
showcase each enumerate exactly these seven `[odc-intro]` `[o11-ref]` `[showcase]`.

**There is no scatter, packed-bubble or treemap chart.** No OutSystems source lists one: the
seven-chart table is closed in both doc sets `[odc-intro]` `[o11-ref]`, the showcase's Chart
Types page lists the same seven `[showcase]`, and the legacy v1 API reference is a strictly
smaller set — Area, Bar, Column, Line and Pie, with no Donut `[o11-v1]`. A design that needs a
correlation plot or a hierarchical breakdown has no chart widget for it, and the honest spec says
so rather than naming a widget that does not exist `[design]`.

The docs name each chart widget with a space — *Donut Chart* — and each add-on without one —
`ChartLegend` `[odc-intro]`. *Unverified:* no OutSystems page states the underlying block
identifier, so where a spec is read by something that resolves names literally, spell the widget
as the documentation does.

## Picking between them

- **Few categories, one metric per category** → Column (vertical) or Bar (horizontal) `[design]`
- **Time series** → Line, or Area when the filled volume carries meaning `[design]`
- **Composition adding to 100%** → Pie, or Donut when the hole holds a total `[design]`
- **One subject scored on several axes at once** → Radar `[design]`

## Add-ons

Add-ons are dropped into the chart's **AddOns** placeholder `[odc-bar]`.

| Add-on | Configures | Source |
|---|---|---|
| `ChartXAxis` | The horizontal axis — or the vertical one on an inverted chart such as the Bar Chart. Carries the axis `Title`, `Visible`, `MinValue`/`MaxValue`, and label, line, gridline and optional-config groups | `[odc-intro]` `[showcase]` |
| `ChartYAxis` | The vertical axis — or the horizontal one on an inverted chart | `[odc-intro]` |
| `ChartLegend` | The box holding a symbol and a name for each series or data point. `Position` and `Layout` are Identifiers — for example `Entities.LegendPosition.TopRight` and `Entities.LegendLayout.Vertical` | `[odc-intro]` `[odc-bar]` |
| `ChartSeriesStyling` | Per-series styling: `SeriesName` picks the series (or leave it unset to style all of them), `SeriesType` changes that series' type — `Entities.SeriesType.Area` — and `Marker`, `Styling` and `ShowDataPointValues` do the rest | `[odc-intro]` `[odc-radar]` `[showcase]` |
| `ChartExport` — **not in the ODC add-on set** | Full-screen view, print, and download as PNG, JPEG, PDF, SVG, CSV or XLS. Documented in the O11 reference and shown in the showcase, but absent from the ODC add-on table, so an ODC design must not assume it | `[o11-ref]` `[showcase]` `[odc-intro]` |

**Compatible add-ons vary by chart.** The showcase states them per chart: the circular
charts — Pie and Donut — take only `ChartLegend` and `ChartSeriesStyling`, while Area, Bar,
Column, Line and Radar add `ChartXAxis` and `ChartYAxis`; none of the seven names `ChartExport`
in its compatible list `[showcase]`. Spec an axis add-on only on a chart that has axes
`[design]`.

Four client actions extend a chart with raw Highcharts configuration:
`SetHighchartsChartConfigs`, `SetHighchartsXAxisConfigs`, `SetHighchartsYAxisConfigs` and
`SetHighchartsSeriesConfigs` `[odc-intro]`. Name the one you need in the spec and let the
implementer wire it from the chart's `Initialized` event `[design]`.

## Chart inputs

`DataPointList` is the mandatory input on every chart `[showcase]`. A data point carries `Label`
and `Value`, and optionally `SeriesName`, `Tooltip` and `Color` `[odc-data]`; setting
`SeriesName` across the points is what produces a multi-series chart `[odc-data]`. The list is
either typed in as fixed data or bound to a list whose attributes are mapped onto `Value` and
`Label` `[odc-data]`.

| Input | Where it appears | Source |
|---|---|---|
| `DataPointList` — mandatory | Every chart | `[showcase]` |
| `Height` — Text, default `300px` | Every chart | `[showcase]` |
| `ExtendedClass` — Text | Every chart | `[showcase]` |
| `ValuesType` — Identifier, default `Entities.ValuesType.Text` | Area, Bar, Column, Line, Radar | `[showcase]` |
| `StackingType` — Identifier, default `Entities.StackingType.NoStacking` | Area, Bar, Column | `[showcase]` |
| `Spline` — Boolean, default False | Area, Line | `[showcase]` |
| `InnerSize` — Text, default `50%` | Donut only | `[odc-donut]` `[showcase]` |

Every chart raises two events: `Initialized`, after the chart instance is ready, and
`OnDataPointClick`, carrying the clicked point's label, value, series name, tooltip and colour
`[showcase]`.

## Spec conventions

- **No chart has a `Title` input** — the input list is `DataPointList`, `Height`,
  `ExtendedClass` and the per-type extras above, on all seven `[showcase]`. Wrap the chart in
  `CardSectioned` and use its `Title` placeholder for the heading, or put the heading on the axis
  via `ChartXAxis`'s own `Title` `[design]` `[showcase]`.
- **No chart has an empty-state input** either `[showcase]`, so spec a `BlankSlate` fallback
  behind an `IfWidget` for the no-data case `[design]`.
- **Name the aggregate, not the binding.** The spec names the source aggregate and the
  `Label`/`Value` attributes it maps onto the data points; the mapping itself is done in the
  Properties tab at build time `[odc-data]`.
- **`Height` is Text, not a number** — `300px` by default `[showcase]` — so a spec that asks for
  a chart height should give it in CSS units `[design]`.
- **Colours have a default worth keeping.** A data point left without `Color` is drawn from the
  OutSystems data-visualization palette `[showcase]`, which is the theme-aware choice `[design]`.

## Anti-patterns

- ❌ Speccing a chart as custom HTML/CSS/JS instead of a chart widget — the widgets are what
  carry the Highcharts rendering, the add-on surface and the documented events `[odc-intro]`
  `[showcase]`.
- ❌ Naming `ScatterChart`, `PackedBubbleChart` or `Treemap` — no OutSystems source lists any of
  them `[odc-intro]` `[o11-ref]` `[showcase]`.
- ❌ One chart per data point — twelve monthly values are one chart with twelve points, not
  twelve single-point charts `[design]`.
- ❌ Hardcoded chart colours — style through `ChartSeriesStyling`, or leave the default palette
  `[showcase]`.
- ❌ Speccing an `AdvancedFormat` input, or any other JSON-format parameter. The v1 charts took
  an `AdvancedFormat` record holding Highcharts JSON `[o11-v1]`; those parameters were removed
  from the current version for security reasons, and the documented replacements are the
  extensibility client actions or JavaScript `[showcase]`.
- ❌ Pairing an add-on with a Charts v1 chart — the add-on blocks are not compatible with v1
  `[showcase]`.
- ❌ Putting an axis add-on on a Pie or Donut chart, which the showcase lists as compatible only
  with `ChartLegend` and `ChartSeriesStyling` `[showcase]`.
- ❌ A `_v2`-suffixed widget name such as `DonutChart_v2`. No OutSystems page names a widget
  that way — the ODC table, the O11 reference and the showcase all name it *Donut Chart*
  `[odc-intro]` `[o11-ref]` `[showcase]` — and `-v2` appears only inside the O11
  documentation's own file and URL names `[o11-ref]`.
- ❌ Colour alone to communicate categories — pair it with shape or pattern for colour-blind
  users `[design]`.

## Sources

Every citation key above resolves here. Mirror paths are read-only copies of the official
OutSystems documentation under the workspace public-knowledge tree. All six mirror pages cited
below were re-fetched live on 2026-09-03 — the five ODC pages from `docs-odc` at upstream
`58e7e4cc`, the O11 page from `docs-product` at upstream `49325bcf` — and every one is
byte-identical to its mirror copy, so these citations are live-verified rather than only pinned.

| Key | Source |
|---|---|
| `[odc-intro]` | `docs-odc` `src/eap/reference/apis/chart-intro.md` — <https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/user_interface/charts_extensibility/> |
| `[odc-data]` | `docs-odc` `src/eap/reference/apis/data.md` — the fixed-data, variable-data and multiple-series walkthroughs |
| `[odc-donut]` | `docs-odc` `src/eap/reference/apis/donut.md` |
| `[odc-bar]` | `docs-odc` `src/eap/reference/apis/bar.md` |
| `[odc-radar]` | `docs-odc` `src/eap/reference/apis/radar.md` |
| `[o11-ref]` | `docs-product` `src/ref/apis/charts-v2/chart-charts-v2.md` — <https://success.outsystems.com/documentation/11/reference/outsystems_apis/charts_api_v2/>. O11, cited only where it corroborates or where a difference from ODC is the point |
| `[o11-v1]` | `docs-product` `src/ref/apis/auto/charts-api.final.md` — the generated legacy Charts API (v1) reference |
| `[showcase]` | The official OutSystems Charts showcase, linked from both doc pages as the Charts sample — <https://charts.outsystems.com>. Read 2026-09-03: the Chart Types page, each chart's Properties / Events / Compatible Add-ons panel, the add-on pages, and the FAQ |
| `[design]` | This skill's own design guidance — not a platform-behaviour claim, and deliberately uncited |
