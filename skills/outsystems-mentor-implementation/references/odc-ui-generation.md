# ODC UI Generation For Mentor Studio

Use this guide after `odc-ui-framework-selection.md` confirms the request is supported for paste-ready generation or a catalog-backed guidance/review case.

Use this guide when the user asks `outsystems-mentor-implementation` to create or modify Screens, Web Blocks, UI patterns, bindings, or UI event wiring in an existing ODC app. Paste-ready Mentor Studio prompts are web-only and only allowed when framework selection supports generation.

Do not use this guide for Mentor Web requirement documents. Use the separate Mentor Web generator skill for new app generation in ODC Portal.

## Framework Selection Preflight

Before generating UI prompts, open `odc-ui-framework-selection.md` and classify the request.

Continue with this guide only for supported generation or catalog-backed guidance cases:

- Web app + OutSystems UI for paste-ready Mentor Studio generation
- Mobile app + OutSystems UI for catalog-backed guidance and review notes only, unless Mentor Studio mobile generation is verified

For Mobile app + Mobile UI, emit framework guidance and guardrails instead of confident paste-ready Mentor Studio generation until a dedicated Mobile UI widget catalog and recipe layer exists.

If the app type or UI framework is unknown and affects correctness, ask one clarifying question before generating.

## Visual-Source UI Discipline

When the source is Figma, screenshot, HTML mockup, source HTML/CSS, screen mockup, or a written UI brief, build or validate the enriched blueprint first. If the target is a verified blank shell, a first-scaffold shell, or a shell-creation path pending explicit approval, let `odc-app-shell-first-scaffold.md` consume that artifact for shell approval and boundary handling before opening `odc-visual-source-ui-discipline.md` for prompt discipline.

## Visual-Source Enriched Blueprint Requirement

For visual-source UI requests, do not jump directly from source notes to prompt
text. First build or validate the OMI Visual-Source Enriched Blueprint by
opening `odc-visual-source-enriched-blueprint.md`. When the target is a blank
or first-scaffold shell, pass that artifact through
`odc-app-shell-first-scaffold.md` for shell approval and boundary handling
before prompt discipline. Then derive the prompt packet and prompt coverage
audit from it.

Before `### Mentor Studio Prompt`, produce or internally complete the Visual-Source UI Prompt Packet:

- source inventory
- Layout Skeleton Gate
- Block Mapping Gate
- Source-Name To Block Gate
- producer and binding plan
- four-part section contract
- Data-Flow Parity Gate
- state plan
- polish acceptance
- evidence boundary

If the Block Mapping Gate or Data-Flow Parity Gate fails, fix the packet and prompt before delivery. Do not downgrade a real OutSystems UI pattern into custom CSS layout to match a screenshot quickly. Keep the visible output order unchanged: `### Mentor Studio Prompt`, `### Prompt Coverage Audit`, `### Studio-Native UI Spec`, `### Evidence Status`.

## Complex Plan And Design-Source Preflight

When UI work comes from a complex source plan, large feature request,
design-source conversion, or multi-block pseudocode output, open
`prompt-narrowing-preflight.md` before drafting UI prompts. Build the Plan
Conversion Manifest, use block decomposition, not plan shrinking, preserve the
source plan as the control artifact, and route UI work through
dependency-ordered blocks.

For UI delivery, the coverage audit must prove that every source-plan UI
requirement is represented before any paste-safe Mentor Studio prompt is
delivered. Narrowing applies to one UI block at a time; do not merge screen,
Web Block, data producer, and event-wiring work into one vague Mentor prompt
unless the preflight says the merge is safe.

## Prompt Inventory Selection

After framework selection and before prompt emission, open `odc-ui-prompt-inventory.md`.

When the inventory selects Tier 1 standard widgets, read `odc-studio-widget-catalog.json` before describing widget behavior, events, or bindings. When the inventory selects Data Grid, read `odc-data-grid-reference.json` before describing dependency setup, events, or actions.

For source refresh or evidence promotion questions, route to
`retrieval-query-bundles.md` and use the Retrieval Query Bundles `widget catalog
refresh` recipe. This guide owns UI prompt discipline; the bundle owns exact
search intent, tool order, authority class, fallback behavior, stop condition,
and expected file owner. If a widget or pattern cannot be promoted with focused
tests and source references, stop rather than speculate.

Use the lowest sufficient tier:

1. Standard ODC Studio widgets for baseline structure, display, form input, and simple actions.
2. OutSystems UI patterns only when the exact pattern exists in `odc-ui-pattern-catalog.json`.
3. Special dependency/component rules when the UI needs Data Grid, public Library Web Blocks, shared UI assets, or any dependency-sensitive component.

If the selected tier requires manual dependency setup, list that setup in the dependency inventory before any consumer prompt.

## Approved Live Execution Preamble

For global live MCP need decisions, read-only evidence collection, approval
gates, and sanitized evidence rules, open `live-execution-intake.md` first.
This UI guide only owns UI-specific prompt discipline after the global intake
has decided that live validation is needed and approved.

Use this preamble only after explicit approval for a specific target app,
canonical app key, and Mentor action:

```text
Implement the following prompt completely. Do not stop until every item in the
acceptance checklist is satisfied. After applying changes, verify each checklist item
by reading the app state available to Mentor. If any checklist
item fails, fix it before finishing. Do not publish, deploy, promote, or modify
unrelated assets.
```

This preamble improves completion discipline for approved Mentor execution. It
does not authorize publish. After a successful run, use the Post-Mentor Preservation Decision Gate
before any `publish_start`.

## Live UI/Data Grid Preflight

Confirm before live Mentor prompts that the target app, UI route, and named producers are real. Do not treat local fixtures or generated references as proof that the live app already has those assets.

Before any live UI or Data Grid Mentor Studio prompt, confirm:

- The app type and framework dependency, such as Web app + OutSystems UI.
- The required app dependency, such as OutSystems Data Grid for ODC, is already added through Manage Dependencies when the prompt uses dependency-backed widgets.
- The target screen name and flow name are verified through `context_screens` or Paulo's explicit input.
- The entity name and producer action names are verified through `context_entities`, `context_actions`, or Paulo's schema.
- The attribute and column names are verified before binding widgets, table columns, or Data Grid columns.

Do not emit a live Data Grid consumer prompt until the required app dependency, target screen name, entity name, and attribute and column names are confirmed. If any item is unknown, stop with `Unknowns And Fallback Behavior`, label the live-specific claim `Unverified gap`, and ask for the missing dependency or schema evidence.

## Standard Widget Evidence Decision Order

When Tier 1 standard widgets are selected, read `odc-studio-widget-catalog.json` before describing widget behavior.

Use this order:

1. If the widget entry is `Current official`, use current ODC facts first.
2. If the widget entry has `current_contextual_sources`, use those current ODC contextual notes for review guidance only, such as Input binding or event hints, but treat them as not an exact widget reference and do not promote the evidence status.
3. If the widget entry has `o11_candidate_support`, use those O11 facts as support-only guidance, not current ODC authority, and label the output `O11-supported ODC candidate`.
4. If the widget has real-app observations only, use them for naming and placement hints only.
5. If none of those are available, keep `Unverified gap`.

Do not say an O11-supported candidate is fully documented in current ODC docs.

## Widget Evidence Discipline

- Current official means current OutSystems docs, approved internal docs, or current tenant/tool observation.
- `Unverified gap` stays visible until promoted by evidence.
- New widget promotion requires focused tests and source references.
- Do not promote generated, dry-run, fixture-only, O11-support-only, or repo-only implementation evidence to `Current official`.
- Preserve Data Grid evidence in `odc-data-grid-reference.json`; documented Data Grid facts can be current while dependency setup remains a manual preflight gap.
- Preserve producer-bound widget discipline: every Table, List, Dropdown, media, Data Grid, Pagination, or source-like widget must name a producer before consumer UI emission.

## Pre-Delivery Coverage Audit (required)

Before delivering any prompt block to the user, run a coverage audit against the source (design prototype, screenshot, spec, or description). This step fires after drafting the prompt and before outputting it.

For every visual or functional element in the source, assign exactly one disposition:

| Disposition | Meaning |
|---|---|
| `✓ covered` | Element is explicitly named and described in the prompt |
| `⚠ partial` | Structurally covered but a known fidelity risk exists (theme override, Unicode glyph, approximation) — add a note |
| `✗ missing` | Element is absent from the prompt and fixable — add it before delivering |
| `— platform limit` | Cannot be expressed via Mentor Studio prompt alone — document the limit and add a post-Mentor review note |

**Mandatory element categories to audit:**

1. **Layout containers** — every named Container, panel, wrapper, row from the source
2. **Visual decoration** — gradients, overlays (dot grids, masks), borders, shadows
3. **Interactive widgets** — all Buttons, Inputs, Checkboxes, Links, Dropdowns, toggles; every Button must have an OnClick destination — `OnClick = (empty)` is a TrueChange error, flag as `✗ missing` and add a placeholder action; every Checkbox must have a visible label, readable color, and gap — ODC Checkbox default size is tiny and renders nearly invisible without explicit styling; flag unstyled Checkboxes as `⚠ partial`
4. **Icon elements** — logo marks, badge icons, feature row icons (flag SVG vs Icon widget vs Unicode risk); do not emit `ph ph-*` font-icon classes unless the target app's dependency is verified; prefer OutSystems UI Icon widgets, and mark raw SVG color behavior as a review item when it depends on `currentColor` or descendant CSS
5. **Typography** — headline, subheadline, label, body text widgets with correct values and styles
6. **Data bindings** — every Input bound to a variable, every Button wired to an action
7. **Navigation** — every Link/Button with a screen destination
8. **Data source completeness** — every data-bound widget or pattern must name a concrete producer for source-like inputs; `TableRecords Source = (empty)`, `List Source = (empty)`, `OptionsList = (empty)`, an empty placeholder List/item producer, or missing URL/ImageURL/value variables are not deliverable. Bind to a verified Aggregate, Data Action, List variable, mapped option list, static entity list, input parameter, or local variable, or block and ask for a producer/setup step.
9. **Visual-source block mapping** — for Figma, screenshot, HTML mockup, source HTML/CSS, screen mockup, or written UI brief, every visual region must have a Block Mapping Gate disposition. Multi-child layout uses OutSystems UI adaptive blocks instead of custom CSS layout unless the CSS is only inline alignment inside a single placeholder.
10. **Visual-source data-flow parity** — every Expression, media URL, option list, selected value, repeated item, and source-like input named in VISUAL LAYOUT has a matching DATA FLOW producer before consumer UI emission.
11. **Visual-source prompt packet** — confirm the Visual-Source UI Prompt Packet has been prepared from the enriched blueprint. Summarize only the packet details that materially affect review inside `### Prompt Coverage Audit` or `### Studio-Native UI Spec`; do not add a mandatory extra visible output section.
12. **CSS specificity risks** — any element using both an OutSystems UI class AND Extended Properties for the same property (color, background, padding); do not rely on `!important` in Extended Properties because OMI hardening records that it is stripped there. Prefer a dedicated CSS class/stylesheet when available, or drop the conflicting OutSystems UI class and style the element directly. If the only known workaround comes from scaffold/design-to-app guidance, mark it `⚠ partial` and require ODC Studio review before hardening.
13. **Reserved class names** — custom layout classes must avoid unprefixed `main-content`, `sidebar`, `header`, `content`, and `footer`; prefix custom classes with app/screen/block intent unless an existing verified theme convention says otherwise
14. **Framework selection** — include the selected target/framework row, such as `Web app + OutSystems UI`, so the audit shows why paste-ready Mentor Studio generation is allowed
15. **Evidence boundary** — include the evidence label and boundary row, especially when catalog-backed, implementation-reference-only, generated-reference, dry-run, live-signature, or spec-driven-build evidence is not current ODC product-contract authority
16. **SPA shell fidelity** — for visual-source HTML/Figma/mockup imports, check header or breadcrumb title, table header color and contrast, styled upload drop-zone preservation, and colored tile icon color. Mark unresolved fidelity risks as `⚠ partial` with an ODC Studio review note.
17. **Block Primitive Naming Parity** — when the source maps to a known OutSystems UI primitive such as `ProgressBar`, `ProgressCircle`, `Counter`, or `Tabs`, confirm the primitive is named in the prompt and review notes, not described only as raw HTML, SVG, or generic Containers.
18. **Additional design-to-app quality checks** — explicitly audit shared chrome edit discipline, design-system discipline, reusable-block extraction review, state and feedback coverage, domain-aware styling heuristic, Tailwind-to-OutSystems normalization, and theme-collision review nuance. Mark gaps as `✗ missing` or `⚠ partial` instead of assuming the enriched blueprint preserved them automatically.

**If any `✗ missing` items remain after audit, fix the prompt before delivering it.**

Only deliver after all items are `✓ covered`, `⚠ partial` (with note), or `— platform limit` (with review note).

Output the audit as a compact table after the last prompt block and before the Studio-Native UI Spec:

```text
### Prompt Coverage Audit

| Source element | Disposition | Note |
|---|---|---|
| SplitWrapper Container | ✓ covered | |
| BrandPanel gradient | ✓ covered | |
| Dot grid overlay | ✗ missing → fixed | Added GridOverlay as first child of BrandPanel |
| Logo mark icon | ⚠ partial | Unicode/SVG/font-icon rendering is target-sensitive — prefer an OutSystems UI Icon widget, and review raw SVG color behavior before hardening |
| Feature row icon badges | ✗ missing → fixed | Added FeatIcon Container per row |
| Eye toggle button | ✗ missing → fixed | Added Btn_RevealPassword + ShowPassword variable |
| Data-bound widget source | ✗ missing → fixed | Added verified Source/OptionsList/List/URL/value producers before data-bound widget emission |
| Custom layout class names | ✓ covered | Prefixed custom classes; avoided unprefixed main-content/sidebar/header/content/footer |
| btn-primary color | ⚠ partial | Do not rely on Extended Properties !important; use a dedicated CSS class/stylesheet or drop the conflicting OutSystems UI class and review in Studio |
| Checkbox tick styling | — platform limit | ODC Checkbox internal input not reachable via Extended Properties |
| Input_UserEmail binding | ✓ covered | |
| LoginOnClick wiring | ✓ covered | |
| Link_ForgotPassword destination | ✓ covered | |
| Web app + OutSystems UI route | ✓ covered | Framework selection supports paste-ready Mentor Studio generation |
| Evidence boundary | ✓ covered | Catalog-backed notes are not current ODC product-contract authority unless current docs, Forge routing/version evidence, or tenant observations confirm them |
```

## Output Shape

For supported paste-ready generation, return UI generation answers in this order:

```text
### Mentor Studio Prompt
[paste-ready atomic prompt]

### Prompt Coverage Audit
[table: source element | disposition | note]

### Studio-Native UI Spec
[short reviewer notes: screen, data source, pattern, bindings, events, dependencies]

### Evidence Status
[Current official | O11-supported ODC candidate | Mixed official+archived | Course/example-backed | OutSystems-public implementation evidence | Catalog-backed official | Unverified gap]
```

For Mobile app + OutSystems UI catalog-backed guidance/review cases where Mentor Studio mobile generation is not verified, do not emit a paste-ready Mentor Studio prompt. Return guidance answers in this order:

```text
### Catalog-Backed UI Guidance
[official pattern facts, compatibility notes, and implementation guidance]

### Studio-Native Review Notes
[short reviewer notes: app type, UI framework, screen, data source, pattern, bindings, events, dependencies, and manual checks]

### Evidence Status
[Catalog-backed official | Mixed official+archived | Unverified gap]
```

For supported paste-ready generation only, if the work needs multiple prompts, emit separate prompt blocks in producer-first order. Run the coverage audit once across all blocks combined — not per block.

Catalog-depth fixtures are guidance and review artifacts, not full paste-ready Mentor Studio prompt templates. They are exempt from the four-section prompt output contract unless the fixture explicitly represents a user-ready paste prompt; keep their evidence labels and review-note boundaries explicit instead.

## Producer-First Order

Always create producers before consumers:

1. Dependency inventory
2. Data producers: Entities, Static Entities, Structures, data assumptions
3. Logic producers: Server Actions, Data Actions, Aggregates, lookup actions, validation actions, save actions
4. Reusable UI producers: Web Blocks
5. Screen consumers: Screens that bind to the producers
6. Event wiring consumers: Button handlers, OnChanged, OnClick, Refresh Data, navigation, feedback messages
7. Review notes: what Paulo must verify in ODC Studio after Mentor applies changes

If a screen prompt references a producer that has not been created or confirmed as existing, move that producer into an earlier prompt block.

### Screen Navigation Target Ordering

Screens that are **navigation targets** are producers relative to the screens that navigate to them. Apply producer-first ordering to screen-to-screen navigation exactly as to server actions and entities.

**Before ordering screen batches:** build the full screen navigation graph by listing every `Navigate to <Screen>` call across all screens. Any screen that appears as a navigation destination must be created before the screens that reference it.

**Failure pattern**
```text
Batch 3: Dashboard — navigates to RequestDetail (does not exist yet → broken wiring)
Batch 4: Requests  — navigates to RequestDetail (does not exist yet → broken wiring)
Batch 5: RequestDetail — navigation target created too late
```

**Correct pattern**
```text
Batch 3: RequestDetail — navigation target exists first ✓
Batch 4: Dashboard — navigates to RequestDetail ✓
Batch 5: Requests  — navigates to RequestDetail ✓
```

For bidirectional navigation or circular dependency, split the screens into shell and wiring batches. Create the entry-point screen first as a minimal shell, then create the detail/target screen, then complete the shell screen after all destinations exist. Always defer outbound navigation wiring from the target screen until its destination screen exists, or create that destination as the minimal shell first. Do not wire `Navigate to <Screen>` in any prompt block where `<Screen>` is neither already present nor created in an earlier block.

For saved prompt packs, run `scripts/validate_screen_navigation_order.py <prompt-file>` before delivery.

## Mentor Studio Constraints

- Mentor Studio works on web apps.
- Mentor Studio does not detect the current screen, selected widget, or active element. Name every target Screen, Block, Action, Entity, Aggregate, and dependency explicitly.
- Mentor Studio cannot add public dependencies itself. Tell Paulo to add dependencies manually through Manage Dependencies before asking Mentor to use public elements.
- Screen generation and editing is less reliable than logic or data generation. Keep UI prompts atomic and review the result in ODC Studio.
- Do not include real personal data in prompts.

## Live Execution Intake Checklist

Global live validation decisions route to `live-execution-intake.md`. Keep this
checklist only for capturing a concrete UI/Data Grid Mentor Studio miss after a
real approved run.

Use this checklist when a real Mentor Studio run exposes a concrete miss in a
UI prompt, realistic fixture, or review note. Capture the execution evidence
before changing the skill.

1. Capture the exact Mentor prompt that was run.
2. Record the target app, screen, block, and framework.
3. Summarize the observed Mentor output, including any generated widget,
   handler, property, placeholder, or TrueChange message that matters.
4. Name the failure class: wrong property, unsupported event, bad nesting, bad placement, incomplete prompt audit, or TrueChange issue.
5. Classify the evidence boundary for the correction: catalog-backed fact,
   implementation-reference-only note, or live Mentor signature correction.
6. Check `odc-ui-acceptance-coverage-map.md` before adding coverage so the fix
   advances the active queue instead of duplicating a covered workflow.
7. Add one narrow failing acceptance test that reproduces the miss before
   editing the fixture, map, or guidance.
8. Patch the smallest fixture or reference text that makes the test pass, then
   run the focused test and full `outsystems-mentor-implementation` suite.

Do not broaden the fixture queue from a vague quality concern. If the evidence
is only catalog-depth or implementation-reference-only, keep that boundary in
the fixture and do not imply current ODC product-contract authority.

## Dependency Inventory Template

```text
Dependency inventory:
Already exists:
- [Name] ([kind]) - use existing

Manual setup required before this prompt:
- Add dependency on [Producer] through Manage Dependencies

To create in this sequence:
1. [Producer kind/name]
2. [Consumer kind/name]
```

## Catalog-Backed Pattern Use

Use `odc-ui-pattern-catalog.json` for exact official pattern names, families, documented properties, events, placeholders, compatibility notes, and security notes.

The OutSystems UI (ODC) Forge documentation bridge supports using the O11 "Using Mobile and Reactive Patterns" documentation as official routing evidence for OutSystems UI pattern guidance in ODC. This bridge strengthens OutSystems UI pattern coverage; it does not change the Mobile UI guardrail and does not promote repo-only implementation-reference facts to current ODC product-contract authority.

When a pattern has no curated recipe:

1. Read its catalog entry.
2. Use the generic producer-first grammar.
3. Label the output `Catalog-backed official`.
4. Add review notes for mandatory properties, important optional properties, placeholders, events, data bindings, and compatibility notes.

Do not imply a catalog-backed pattern has a proven Mentor Studio recipe.

## OutSystems UI Public Implementation Evidence Fallback

Use `outsystems-ui-implementation-reference.json` only after current ODC docs, generated ODC UI catalogs, and curated recipes do not answer a source-backed implementation detail.

Repo-only facts from `OutSystems/outsystems-ui` are OutSystems-public implementation evidence. They can support dependency checks, property/event review notes, placeholder hints, or gap-filling questions, but they are not current ODC product-contract authority and must not upgrade an answer to `Current official` or `Catalog-backed official` unless current ODC docs, Forge routing/version evidence, or tenant observations confirm the exposed behavior.

Before reading individual pattern entries, check the reference's top-level `gap_analysis` when the missing detail is about one of these surfaces:

- SCSS family discovery, deprecated markers, preview markers, or style-only implementation clues.
- ODC/O11 implementation variant paths, especially when a pattern has both platform-specific files.
- Non-`*Config.ts` TypeScript or API surface that is not represented in the generated pattern entries.

Use `gap_analysis` to decide what to mention in review notes and what to verify in ODC Studio. Do not treat a family name, TS/API count, deprecated marker, preview marker, or ODC/O11 variant path as proof that the behavior is currently supported in ODC.

When this fallback materially affects the answer:

1. Say `OutSystems-public implementation evidence` near the affected fact.
2. State that the fact is not current ODC product-contract authority unless current ODC docs, Forge routing/version evidence, or tenant observations confirm the exposed behavior.
3. Include a review note to verify the property, event, placeholder, or dependency in ODC Studio.
4. Prefer the commit-pinned `source_url` from the generated reference when Paulo asks for provenance.

### Approved Pattern Review Note Matrix

For these approved pattern-specific fallbacks, use catalog facts from `odc-ui-pattern-catalog.json` first and keep the output label `Catalog-backed official` when those facts are sufficient. Use repo evidence as review notes only, after catalog checks, and mark the affected note as `OutSystems-public implementation evidence`.

| Pattern | Catalog anchor | Repo entries | Review-note use | Guardrail |
| --- | --- | --- | --- | --- |
| Dropdown Search | `OptionsList`, `Prompt`, `OptionalConfigs.SearchPrompt`, `OnChanged` | `AbstractVirtualSelectConfig`, `VirtualSelect`, `AbstractDropdownConfig` | Review `OptionsList`, `Prompt`, `SearchPrompt`, `NoOptionsText`, `NoResultsText`, starting selection, disabled/dropbox behavior. | Do not invent Mentor properties or change catalog-backed bindings; not current ODC product-contract authority. |
| Tabs | `StartingTab`, `TabsOrientation`, `TabsVerticalPosition`, `OptionalConfigs.JustifyHeaders`, `OnTabChange` | `TabsConfig`, `TabsHeaderItem`, `TabsContentItem` | Review paired header/content item structure and implementation properties such as `Height`, `JustifyHeaders`, `StartingTab`, `TabsOrientation`, `TabsVerticalPosition`, and `ContentAutoHeight`. | Do not add non-catalog events; keep `OnTabChange` as the catalog-backed event; not current ODC product-contract authority. |
| Date Picker | `DateFormat`, `OptionalConfigs.InitialDate`, `OptionalConfigs.MinDate`, `OptionalConfigs.MaxDate`, `ShowTodayButton`, `TimeFormat`, `OnSelect` | `AbstractDatePickerConfig`, `AbstractFlatpickrConfig`, `FlatpickrSingleDateConfig`, `FlatpickrRangeDateConfig` | Review date-format, min/max, first-week-day, today button, week-number, initial-date, and range-date implementation details. | Do not add non-catalog events or promote Flatpickr provider callbacks such as `OnChange`, `OnClose`, `OnMonthChange`, or `OnOpen`; keep `OnSelect` as the catalog-backed event; not current ODC product-contract authority. |
| Carousel | `Height`, `ItemsPerSlide`, `Navigation`, `OptionalConfigs.AutoPlay`, `OptionalConfigs.ItemsGap`, `OptionalConfigs.Loop`, `OptionalConfigs.Padding`, `OptionalConfigs.StartingPosition` | `AbstractCarouselConfig`, `Splide` | Review Splide-backed carousel configuration such as `AutoPlay`, `Height`, `ItemsDesktop`, `ItemsGap`, `Loop`, `Navigation`, `Padding`, and `StartingPosition`. | Do not add non-catalog events; the catalog has no Carousel events; not current ODC product-contract authority. |
| Range Slider | `OptionalConfigs.IsDisabled`, `OptionalConfigs.ShowFloatingLabel`, `OptionalConfigs.ShowTickMarks`, `OptionalConfigs.Step`, `OptionalConfigs.TickMarksInterval`, `Orientation`, `Size`, `OnChange` | `AbstractRangeSliderConfig`, `NoUiSliderSingleConfig`, `noUiSlider` | Review single-value slider configuration such as `MinValue`, `MaxValue`, `StartingValueFrom`, `InitialValueFrom`, `Step`, `ShowFloatingLabel`, `ShowTickMarks`, `Orientation`, and `Size`. | Do not swap events with Range Slider Interval; keep `OnChange` as the catalog-backed Range Slider event; not current ODC product-contract authority. |
| Range Slider Interval | `OptionalConfigs.IsDisabled`, `OptionalConfigs.ShowFloatingLabel`, `OptionalConfigs.ShowTickMarks`, `OptionalConfigs.Step`, `OptionalConfigs.TickMarksInterval`, `Orientation`, `Size`, `OnValueChange` | `AbstractRangeSliderConfig`, `NoUiSliderIntervalConfig`, `noUiSlider` | Review interval slider configuration such as `IsInterval`, `MinValue`, `MaxValue`, `StartingValueFrom`, `StartingValueTo`, `InitialValueFrom`, `InitialValueTo`, `Step`, and tick-mark behavior. | Do not swap events with Range Slider; keep `OnValueChange` as the catalog-backed Range Slider Interval event; not current ODC product-contract authority. |
| Month Picker | `DateFormat`, `InitialMonth`, `MaxMonth`, `MinMonth`, `OnSelect` | `AbstractMonthPickerConfig`, `FlatpickrMonthConfig`, `Flatpickr` | Review month-format and month-bound configuration such as `DateFormat`, `InitialMonth`, `MaxMonth`, `MinMonth`, and provider date-format handling. | Do not add non-catalog events or promote Flatpickr provider callbacks such as `OnChange`, `OnClose`, or `OnOpen`; keep `OnSelect` as the catalog-backed event; not current ODC product-contract authority. |
| Time Picker | `InitialTime`, `Is24Hours`, `OptionalConfigs.MaxTime`, `OptionalConfigs.MinTime`, `OnSelect` | `AbstractTimePickerConfig`, `FlatpickrTimeConfig`, `Flatpickr` | Review time configuration such as `InitialTime`, `Is24Hours`, `MaxTime`, `MinTime`, `TimeFormat`, and provider date-format handling. | Do not add non-catalog events or promote Flatpickr provider callbacks such as `OnChange`, `OnClose`, or `OnOpen`; keep `OnSelect` as the catalog-backed event; not current ODC product-contract authority. |
| Date Picker Range | `DateFormat`, `OptionalConfigs.InitialStartDate`, `OptionalConfigs.InitialEndDate`, `OptionalConfigs.MinDate`, `OptionalConfigs.MaxDate`, `ShowTodayButton`, `OnSelect` | `AbstractDatePickerConfig`, `AbstractFlatpickrConfig`, `FlatpickrRangeDateConfig`, `Flatpickr` | Review range-date configuration such as `DateFormat`, `InitialStartDate`, `InitialEndDate`, `MinDate`, `MaxDate`, `FirstWeekDay`, today button, and provider date-format handling. | Do not add non-catalog events or promote Flatpickr provider callbacks such as `OnChange`, `OnClose`, `OnMonthChange`, or `OnOpen`; keep `OnSelect` as the catalog-backed event; not current ODC product-contract authority. |
| Dropdown Tags | `OptionsList`, `Prompt`, `SelectedOptions`, `OptionalConfigs.NoOptionsText`, `OptionalConfigs.NoResultsText`, `OptionalConfigs.SanitizeDropdownValues`, `OptionalConfigs.SearchPrompt` | `AbstractDropdownConfig`, `AbstractVirtualSelectConfig`, `VirtualSelectTagsConfig`, `VirtualSelect` | Review multi-select option mapping, selected-options binding, prompt/search/no-results text, sanitize/dropdown value handling, disabled/dropbox behavior, and tags provider setup. | Do not add non-catalog events; the catalog has no Dropdown Tags events; not current ODC product-contract authority. |
| Gallery | `ItemsGap`, `RowItemsDesktop`, `ExtendedClass` | `GalleryConfig` | Review responsive row item counts and item-gap behavior against ODC Studio output. | Do not add non-catalog events; the catalog documents no Gallery events; not current ODC product-contract authority. |
| Accordion | `MultipleItems`, item-level `StartsExpanded`, `Icon`, `IconPosition`, `IsDisabled` | `AccordionConfig`, `AccordionItemConfig` | Review multiple-item expansion, item-level starting state, and item pairing behavior. | Do not put `StartsExpanded` on the parent Accordion; do not add non-catalog events; not current ODC product-contract authority. |
| Flip Content | `FlipOnClick`, `StartsFlipped`, `ExtendedClass` | `FlipContentConfig` | Review flip trigger and initial flipped-state behavior. | Do not add non-catalog events; the catalog documents no Flip Content events; not current ODC product-contract authority. |
| Tooltip | `Position`, `StartsOpen`, `Trigger`, `OnToggle` | `TooltipConfig` | Review tooltip trigger, placement configuration, and toggle handler wiring. | Do not wire `Tooltip.OnClick`; live evidence found `OnToggle` instead; not current ODC product-contract authority. |
| Animated Label | `ExtendedClass` | `AnimatedLabelConfig` | Review label/input pairing and animated-label runtime setup. | Do not add non-catalog events; the catalog documents no Animated Label events; not current ODC product-contract authority. |
| Bottom Sheet | `Shape`, `ShowHandler`, `ExtendedClass`, `OnToggle` | `BottomSheetConfig` | Review bottom-sheet shape, handler configuration, and toggle handler wiring. | Do not invent an open/visibility input parameter; live evidence found `OnToggle`; not current ODC product-contract authority. |
| Notification | `Position`, `StartsOpen`, `Width`, `OptionalConfigs.CloseAfterTime`, `OptionalConfigs.InteractToClose` | `NotificationConfig` | Review notification position, close timing, interact-to-close, and initial open state. | Do not add non-catalog events; the catalog documents no Notification events; not current ODC product-contract authority. |
| Search | `ExtendedClass`, internal Input `Variable` | `SearchConfig`, `VirtualSelectSearchConfig` | Review search pattern setup, styling class, and internal Input value binding only as implementation nuance. | Do not invent block inputs such as `Value` or `Query`, and do not add `OnChange`; not current ODC product-contract authority. |
| Sidebar | `Direction`, `HasOverlay`, `StartsOpen`, `Width`, `OnToggle` | `SidebarConfig` | Review sidebar direction, overlay, width, initial open state, and toggle handler wiring. | `OnToggle` receives `SidebarId` Text and `IsOpen` Boolean in live evidence; not current ODC product-contract authority. |
| Video | `URL`, `Controls`, `Width`, `Height`, `Captions`, `OptionalConfigs`, `StateChanged`, `Initialized` | `VideoConfig` | Review video URL, control, optional config record, sizing, captions, and lifecycle-event need. | Do not use `VideoURL`; put `Autoplay`, `Loop`, `Muted`, and `PosterURL` inside `OptionalConfigs`; not current ODC product-contract authority. |
| Section Index | `ScrollToWidgetId`, `IsFixed`, `SmoothScrolling` | `SectionIndexConfig`, `SectionIndexItemConfig` | Review section/index item pairing and scroll target IDs. | Do not add non-catalog events; the catalog documents no Section Index events; not current ODC product-contract authority. |
| Submenu | `ExtendedClass` | `SubmenuConfig` | Review submenu runtime setup only as implementation nuance. | Do not add non-catalog events; the catalog documents no Submenu events; not current ODC product-contract authority. |
| Progress Bar | `Progress`, `ProgressColor`, `Thickness`, `TrailColor`, `OptionalConfigs.AnimateInitialProgress`, `OptionalConfigs.Shape` | `ProgressBarConfig` | Review progress value, shape, color, trail, thickness, and initial animation configuration. | Do not add non-catalog events; the catalog documents no Progress Bar events; not current ODC product-contract authority. |
| Progress Circle | `Progress`, `ProgressColor`, `Thickness`, `TrailColor`, `OptionalConfigs.AnimateInitialProgress`, `OptionalConfigs.Shape` | `ProgressCircleConfig` | Review circular progress value, shape, color, trail, thickness, and initial animation configuration. | Do not add non-catalog events; the catalog documents no Progress Circle events; not current ODC product-contract authority. |
| Rating | `RatingValue`, `IsEdit`, `RatingScale`, `Size` | `RatingConfig` | Review rating value, editability, scale, and size configuration. | Do not add non-catalog events; the catalog documents no Rating events; not current ODC product-contract authority. |
| Button Loading | `IsLoading`, `ShowLabelOnLoading`, `ExtendedClass` | `ButtonLoadingConfig` | Review loading-state display and label visibility configuration. | Do not add non-catalog events; the catalog documents no Button Loading events; not current ODC product-contract authority. |
| Inline SVG | `SVGCode`, `ExtendedClass` | `InlineSvgConfig` | Review SVG code binding and sanitization-sensitive rendering setup. | Do not add non-catalog events; the catalog documents no Inline SVG events; not current ODC product-contract authority. |
| Swipe Events | `WidgetId` | `SwipeEventsConfig` | Review target `WidgetId` wiring for swipe-sensitive containers. | Do not invent swipe callbacks as catalog events; not current ODC product-contract authority. |
| Touch Events | `WidgetId` | `TouchEventsConfig` | Review target widget wiring for touch-sensitive containers. | Do not invent touch callbacks as catalog events; not current ODC product-contract authority. |
| Columns | `ExtendedClass`, `GutterSize`, `PhoneBehavior`, `TabletBehavior` | `No bounded implementation-reference entry` | Review column count, `GutterSize`, and tablet/phone behavior so responsive breakpoints match the intended layout. | Do not add non-catalog events; the catalog documents no Columns events; not current ODC product-contract authority. |
| Display on Device | `device/content placeholders` | `No bounded implementation-reference entry` | Review which content is shown or hidden per device placeholder so desktop, tablet, and phone variants do not duplicate conflicting UI. | Do not add non-catalog events; the catalog documents no Display on Device events; not current ODC product-contract authority. |
| Master Detail | `Height`, `LeftPercentage`, `OpenedOnPhone` | `No bounded implementation-reference entry` | Review `LeftContent` and `RightContent` placement, `LeftPercentage`, `Height`, and `OpenedOnPhone` for list/detail behavior on phone screens. | Do not add non-catalog events; the catalog documents no Master Detail events; not current ODC product-contract authority. |
| Alert | `AlertType`, `ExtendedClass` | `No bounded implementation-reference entry` | Review `AlertType`, message severity, icon/text content, and spacing so the alert communicates the intended feedback state. | Do not add non-catalog events; the catalog documents no Alert events; not current ODC product-contract authority. |
| Blank Slate | `ExtendedClass`, `FullHeight` | `No bounded implementation-reference entry` | Review empty-state title/body/action placeholders and `FullHeight` so no-result screens guide the next user action. | Do not add non-catalog events; the catalog documents no Blank Slate events; not current ODC product-contract authority. |
| Card | `ExtendedClass`, `UsePadding` | `No bounded implementation-reference entry` | Review card body placeholder, `UsePadding`, and surrounding spacing so grouped content remains scannable. | Do not add non-catalog events; the catalog documents no Card events; not current ODC product-contract authority. |
| Card Background | `Color`, `ExtendedClass`, `Height`, `MinHeight` | `No bounded implementation-reference entry` | Review background color/image intent, `Height`, `MinHeight`, and contrast for text placed over the card. | Do not add non-catalog events; the catalog documents no Card Background events; not current ODC product-contract authority. |
| Card Item | `ExtendedClass` | `No bounded implementation-reference entry` | Review repeated card item content, click target placement, and spacing inside parent card/list contexts. | Do not add non-catalog events; the catalog documents no Card Item events; not current ODC product-contract authority. |
| Card Sectioned | `ExtendedClass`, `ImagePadding`, `IsVertical`, `UsePadding` | `No bounded implementation-reference entry` | Review section order, image padding, vertical/horizontal layout, and `UsePadding` across each card region. | Do not add non-catalog events; the catalog documents no Card Sectioned events; not current ODC product-contract authority. |
| Chat Message | `DisplayOnRight`, `ExtendedClass`, `MessageStatus`, `Time` | `No bounded implementation-reference entry` | Review message alignment, `DisplayOnRight`, `MessageStatus`, timestamp, and sender/content placeholders. | Do not add non-catalog events; the catalog documents no Chat Message events; not current ODC product-contract authority. |
| Floating Content | `Position`, `ExtendedClass`, `UseFullHeight`, `UseFullWidth`, `UseMargin` | `No bounded implementation-reference entry` | Review `Position`, full-width/full-height options, margins, and overlay relationship to the anchored content. | Do not add non-catalog events; the catalog documents no Floating Content events; not current ODC product-contract authority. |
| List Item Content | `ExtendedClass` | `No bounded implementation-reference entry` | Review left/content/right placeholders and repeated-row alignment inside the parent list item. | Do not add non-catalog events; the catalog documents no List Item Content events; not current ODC product-contract authority. |
| Section | `ExtendedClass`, `UsePadding` | `No bounded implementation-reference entry` | Review section title, content placeholder, and `UsePadding` so page regions stay visually distinct. | Do not add non-catalog events; the catalog documents no Section events; not current ODC product-contract authority. |
| Section Group | `ExtendedClass`, `HasStickyTitles`, `TopPosition` | `No bounded implementation-reference entry` | Review grouped section title behavior, `HasStickyTitles`, `TopPosition`, and scroll context. | Do not add non-catalog events; the catalog documents no Section Group events; not current ODC product-contract authority. |
| Tag | `Color`, `ExtendedClass`, `IsLight`, `Shape`, `Size` | `No bounded implementation-reference entry` | Review label text, `Color`, `IsLight`, `Shape`, and `Size` for status/category semantics. | Do not add non-catalog events; the catalog documents no Tag events; not current ODC product-contract authority. |
| User Avatar | `Color`, `ExtendedClass`, `Image`, `IsLight`, `Name`, `Shape`, `Size` | `No bounded implementation-reference entry` | Review image-vs-initials fallback, `Name`, `Image`, `Color`, `Shape`, `Size`, and data binding to user records. | Do not add non-catalog events; the catalog documents no User Avatar events; not current ODC product-contract authority. |
| Action Sheet | `IsOpen`, `OnClick`, `OnClose` | `No bounded implementation-reference entry` | Review `IsOpen` state ownership, action item placeholders, and `OnClick`/`OnClose` handler wiring. | Keep catalog-backed events OnClick, OnClose; do not add provider callbacks; not current ODC product-contract authority. |
| Animate | `AnimationType`, `Delay`, `ExtendedClass`, `Speed` | `No bounded implementation-reference entry` | Review `AnimationType`, `Delay`, `Speed`, and target content so animation supports rather than hides state changes. | Do not add non-catalog events; the catalog documents no Animate events; not current ODC product-contract authority. |
| Floating Actions | `ExtendedClass`, `IsExpanded`, `IsHover` | `No bounded implementation-reference entry` | Review main action, secondary actions, `IsExpanded`, `IsHover`, child Floating Actions Item content, and Button widgets inside each Item placeholder. | Do not add non-catalog events; the catalog documents no Floating Actions events; do not claim internal toggles write back to the bound Boolean without live verification; not current ODC product-contract authority. |
| Input with Icon | `AlignIconRight`, `ExtendedClass` | `No bounded implementation-reference entry` | Review input/icon pairing, `AlignIconRight`, label/accessibility context, and binding to the intended input value. | Do not add non-catalog events; the catalog documents no Input with Icon events; not current ODC product-contract authority. |
| Lightbox Image | `ExtendedClass`, `Group`, `ImageURL`, `ImageZoom`, `Title` | `No bounded implementation-reference entry` | Review `ImageURL`, `ImageZoom`, `Group`, `Title`, thumbnail/full-image relationship, and image source binding. | Do not add non-catalog events; the catalog documents no Lightbox Image events; not current ODC product-contract authority. |
| Scrollable Area | `ExtendedClass`, `Height`, `Orientation`, `ScrollbarStyle`, `Width` | `No bounded implementation-reference entry` | Review `Height`, `Width`, `Orientation`, `ScrollbarStyle`, and nested content size so scrolling is intentional. | Do not use `ScrollbarType`; the live signature uses `ScrollbarStyle`; not current ODC product-contract authority. |
| Stacked Cards | `Items`, `Rotate`, `StackedOptions`, `UseOverlays`, `OnLeftSwipe` | `No bounded implementation-reference entry` | Review card item source, `Items`, `Rotate`, `StackedOptions`, `UseOverlays`, and `OnLeftSwipe` behavior. | Keep catalog-backed events OnLeftSwipe; do not add provider callbacks; not current ODC product-contract authority. |
| Bottom Bar Item | `ExtendedClass` | `No bounded implementation-reference entry` | Review destination/action binding, icon/label pairing, and active-state styling for bottom navigation. | Do not add non-catalog events; the catalog documents no Bottom Bar Item events; not current ODC product-contract authority. |
| Breadcrumbs | `ExtendedClass` | `No bounded implementation-reference entry` | Review breadcrumb item order, labels, current page marker, and navigation targets. | Do not add non-catalog events; the catalog documents no Breadcrumbs events; not current ODC product-contract authority. |
| Pagination | `MaxRecords`, `StartIndex`, `TotalCount`, `ExtendedClass`, `ShowGoToPage` | `No bounded implementation-reference entry` | Review `MaxRecords`, `StartIndex`, `TotalCount`, `ShowGoToPage`, and page-change refresh flow. | Do not add non-catalog events; the catalog documents no Pagination events; not current ODC product-contract authority. |
| Timeline Item | `Color`, `ExtendedClass`, `IsActive` | `No bounded implementation-reference entry` | Review event label/content, `Color`, `IsActive`, and chronological placement inside the timeline. | Do not add non-catalog events; the catalog documents no Timeline Item events; not current ODC product-contract authority. |
| Wizard | `Status`, `ExtendedClass`, `IsVertical`, `UseTopLabel`, `OnClick` | `No bounded implementation-reference entry` | Review step order, `Status`, vertical/top-label presentation, and `OnClick` navigation for each step. | Keep catalog-backed events OnClick; do not add provider callbacks; not current ODC product-contract authority. |
| Badge | `Color`, `ExtendedClass`, `IsLight`, `Number`, `Shape`, `Size` | `No bounded implementation-reference entry` | Review `Number`, `Color`, `IsLight`, `Shape`, and `Size` so counts remain legible and semantically clear. | Do not add non-catalog events; the catalog documents no Badge events; not current ODC product-contract authority. |
| Counter | `BackgroundColor`, `ExtendedClass`, `Height`, `IsVertical` | `No bounded implementation-reference entry` | Review counter value expression, `BackgroundColor`, `Height`, and `IsVertical` for metric display. | Do not add non-catalog events; the catalog documents no Counter events; not current ODC product-contract authority. |
| Icon Badge | `Number`, `Color`, `ExtendedClass`, `IsLight` | `No bounded implementation-reference entry` | Review icon selection, `Number`, `Color`, `IsLight`, and placement relative to the target icon. | Do not add non-catalog events; the catalog documents no Icon Badge events; not current ODC product-contract authority. |
| Align Center | `ExtendedClass`, `IsHorizontal` | `No bounded implementation-reference entry` | Review centered content target and `IsHorizontal` so alignment is applied on the intended axis only. | Do not add non-catalog events; the catalog documents no Align Center events; not current ODC product-contract authority. |
| Center Content | `ExtendedClass` | `No bounded implementation-reference entry` | Review centered content placeholder and parent height so vertical centering has a stable container. | Do not add non-catalog events; the catalog documents no Center Content events; not current ODC product-contract authority. |
| Margin Container | `ExtendedClass` | `No bounded implementation-reference entry` | Review margin/padding purpose and surrounding layout so spacing is intentional and not duplicated. | Do not add non-catalog events; the catalog documents no Margin Container events; not current ODC product-contract authority. |
| Mouse Events | `WidgetId`, `PreventDefaults` | `No bounded implementation-reference entry` | Review `WidgetId`, `PreventDefaults`, and the target widget/action relationship for mouse-sensitive behavior. | Do not add non-catalog events; the catalog documents no Mouse Events events; not current ODC product-contract authority. |
| Separator | `Color`, `ExtendedClass`, `IsVertical`, `Space` | `No bounded implementation-reference entry` | Review `IsVertical`, `Space`, `Color`, and adjacent content so separation improves grouping without excess whitespace. | Do not add non-catalog events; the catalog documents no Separator events; not current ODC product-contract authority. |

Do not use these repo-only facts to invent Mentor properties, change catalog-backed bindings, add non-catalog events, or upgrade the output to `Current official`. If they materially affect generated instructions, say they are `OutSystems-public implementation evidence`, say they are not current ODC product-contract authority unless confirmed by current ODC docs, Forge routing/version evidence, or tenant observations, and include a targeted ODC Studio review note.

### Live ODC Mentor Signature Corrections

Catalog facts remain the primary authority for routing pattern use, but live ODC Mentor signature evidence can correct exact Mentor-facing names when tenant observations confirm the exposed behavior. Use these corrections only for the named patterns and keep the evidence boundary explicit: catalog-backed official facts plus live ODC Mentor signature evidence, not repo-only product-contract authority.

| Pattern | Use in Mentor Studio prompts | Avoid |
| --- | --- | --- |
| Search | Search exposes only ExtendedClass as a block input; bind the nested Search internal Input.Variable to the search Text local variable. | Do not invent Search.Value, Search.Query, or Search.OnChange. |
| Accordion | Parent Accordion owns MultipleItems and ExtendedClass; Accordion Item owns StartsExpanded; Accordion Item placeholders are Title, CustomIcon, and Content. | Do not put StartsExpanded on parent Accordion. |
| Blank Slate | Blank Slate placeholders are Icon, Content, and Actions. | Do not flatten the action button into body copy when an action placeholder is required. |
| List Item Content | List Item Content placeholders are Left, Title, Content, and Right. | Do not collapse left/right adornments into the main content placeholder when alignment matters. |
| Floating Actions | Floating Actions Item exposes only ExtendedClass in current ODC docs; place command behavior in Button widgets inside the Item placeholder; bind IsExpanded only as explicit expansion input unless live evidence proves state synchronization. | Do not prompt Floating Actions Item.OnClick, Floating Actions Item.Command, or Floating Actions Item.Action; do not claim automatic two-way IsExpanded state sync without live verification. |
| Tooltip | Tooltip.Position expects Position Identifier; Tooltip.Trigger expects Trigger Identifier; Tooltip.OnToggle is the live event. Tooltip.OnClick does not exist in the live signature. | Do not wire Tooltip.OnClick. |
| Sidebar | Sidebar.Direction expects Direction Identifier; Sidebar.Width expects Text; Sidebar.OnToggle exposes SidebarId Text and IsOpen Boolean parameters. | Do not treat provider callbacks as catalog-backed events. |
| Bottom Sheet | Bottom Sheet.Shape expects Shape Identifier; Bottom Sheet.OnToggle is available for toggle handling. Bottom Sheet has no open/visibility input parameter. | Do not invent an IsOpen, StartsOpen, or Show* binding for visibility. |
| Animate | Animate.AnimationType expects AnimationType Identifier; Animate.Speed expects Speed Identifier; Animate.Delay expects Integer; content goes in the Content placeholder. | Do not add non-catalog events. |
| Scrollable Area | Scrollable Area uses ScrollbarStyle, not ScrollbarType; bind Height and Width as Text and Orientation as Orientation Identifier. | Do not use Scrollable Area.ScrollbarType. |
| Video | Video uses URL, not VideoURL; Controls is direct; Width and Height are Text; PosterURL, Autoplay, Loop, and Muted belong inside Video.OptionalConfigs. Video StateChanged and Initialized remain unwired unless lifecycle handling is a product requirement. | Do not bind direct Video.PosterURL, Video.Muted, Video.Loop, or Video.Autoplay inputs; do not prompt loose inline record constructors for optional settings. |

## Real-App Observed Evidence

When the user asks to compare a UI prompt with a real ODC app, mine a real app for UI generation knowledge, or decide whether an observed UI pattern should become a curated recipe, open `tenant-context-guardrails.md` when a Tenant Context Packet is needed for target app identity, then open `odc-ui-real-app-evidence.md`.

Treat real app evidence as observed implementation evidence, not as official platform authority. Use it to improve producer-first order, realistic naming, dependency inventories, response/error handling, and pseudocode comparisons.

When using MCP context summaries, do not infer exact widget trees, widget ids, local variables, bindings, or events. If the context tools only expose screens, actions, structures, entities, references, and theme CSS, mark UI structure as inferred and add review notes for ODC Studio verification.

Outputs that rely materially on real app evidence must use `Course/example-backed` unless official docs independently support the exact fact. Do not use real app evidence to upgrade a fact to `Current official`.

## Real-App Pseudocode Comparison Mode

Use this mode when Paulo asks whether a generated UI prompt matches a real ODC app or asks to compare skill output against observed app evidence.

This mode is not a paste-ready Mentor Studio prompt. It is a review and benchmarking output.

Return comparison answers in this order:

```text
### Real-App Benchmark Source
[app, revision if known, evidence source, and observed boundary]

### Inferred Producer Graph
[dependencies, data producers, structure producers, action producers, screen consumers]

### Pseudocode Comparison
[specific pass/fail or gap bullets comparing generated prompt against observed producers and official facts]

### Extra Evidence Needed
[exact evidence required before claiming exact widget tree, exact bindings, exact events, or curated recipe readiness]

### Evidence Status
Course/example-backed
```

Do not label real-app comparison output `Current official`. If a comparison cites an official catalog fact, identify that fact separately from the observed app evidence.

## Recipe Promotion Rule

Promotion from catalog-backed pattern use to a curated recipe is Codex-assisted, not silent. Promote a pattern only when there is evidence such as repeated use, Mentor Studio failure, tricky bindings or events, compatibility constraints, or official docs changes. Recipe promotion must be an explicit skill maintenance change with validation and a handoff ledger update.

## Studio-Native UI Spec Template

```text
Target: Screen|Web Block [Name]
Purpose: [one sentence]
Data producers: [entities, aggregates, actions]
Logic producers: [server/client/data actions]
UI patterns: [exact pattern names]
Bindings:
- [widget/property] = [source]
Events:
- [event] -> [handler/action]
Review in ODC Studio:
- [specific verification]
```

## Evidence Labels

- `Current official`: current OutSystems docs, approved internal docs, or current tenant/tool observation.
- `Catalog-backed official`: exact UI pattern facts come from the generated official catalog, but no curated recipe exists yet.
- `O11-supported ODC candidate`: confirmed ODC Studio target or approved alias with support-only O11 `Designing Screens` reference facts; verify properties and events in ODC Studio.
- `Mixed official+archived`: combines current docs with archived official material.
- `Course/example-backed`: relies materially on courseware, workshop material, or examples.
- `OutSystems-public implementation evidence`: relies materially on the public `OutSystems/outsystems-ui` source repository for implementation details; not current ODC product-contract authority unless confirmed by current ODC docs, Forge routing/version evidence, or tenant observations.
- `Unverified gap`: not confirmed well enough to present as current ODC capability.
