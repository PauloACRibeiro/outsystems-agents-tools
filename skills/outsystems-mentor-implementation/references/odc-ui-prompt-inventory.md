# ODC UI Prompt Generation Inventory

Use this reference after `odc-ui-framework-selection.md` and before `odc-ui-generation.md` emits UI prompt text.

This inventory helps `outsystems-mentor-implementation` choose the lowest sufficient UI building block tier before writing Mentor Studio prompts or catalog-backed guidance.

## Core Rule

Choose the lowest sufficient tier:

1. Start with standard ODC Studio widgets, using `odc-studio-widget-catalog.json` for catalog evidence, missing facts, and prompt guidance.
2. Upgrade to an OutSystems UI pattern when a documented pattern improves the requested layout or interaction.
3. Use special dependency/component rules when the requested UI depends on public reusable elements, external component references, or exact dependency setup.

Do not use this file to claim Mobile UI paste-ready generation. Mobile UI requests still follow `odc-ui-framework-selection.md` guardrails.

## Tier 1: Standard ODC Studio Widgets

Use standard widgets for baseline structure, display, form input, and simple actions. Before writing prompt text, read the matching entry from `odc-studio-widget-catalog.json`; the catalog entry decides whether the current ODC evidence is `Current official` or `Unverified gap`. If the entry has `o11_candidate_support`, use that field as support-only reference guidance, not current ODC authority, and label the generated output `O11-supported ODC candidate` unless current ODC evidence already supports a stronger label.

| Widget | Use when | Prompt guidance | Evidence status |
| --- | --- | --- | --- |
| Container | Group content, define layout areas, or wrap related widgets. | Use the catalog entry; include `missing_facts` when recorded. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Expression | Display text, numbers, dates, labels, and computed values. | Use the catalog entry; include binding guidance only when source-backed. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Form | Edit or create a single record. | Use the catalog entry; create or confirm the form record before consumer widgets. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Input | Capture text, numbers, dates, or other scalar values. | Use the catalog entry; bind only to existing local variables or form fields. If `current_contextual_sources` is present, use those current ODC notes for binding, `OnChange`, and `Prompt` review guidance only; they are not an exact widget reference and do not promote evidence beyond the catalog entry. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Button | Trigger a client action or navigation. | Use the catalog entry; create or confirm the target action before wiring the button. If `current_contextual_sources` is present, use those current ODC notes for `On Click`, `New Client Action`, destination Screen, and direct URL review guidance only; they are not an exact widget reference and do not promote evidence beyond the catalog entry. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| If | Conditional UI rendering. | Use the catalog entry; confirm the Boolean condition or producer first. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Text | Add static copy. | Use the catalog entry; prefer `Expression` when binding dynamic values. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Link | Navigate to another screen or external URL. | Use the catalog entry; confirm the target screen or URL source before adding the link. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| List | Repeat record content in a compact layout. | Use the catalog entry; create or confirm the data producer before the List. If `current_contextual_sources` is present, use those current ODC notes for Aggregate/List source binding, `GetEmployees.List`-style sources, and attribute-display review guidance only; they are not an exact widget reference and do not promote evidence beyond the catalog entry. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| List Item | Add child row/content inside `List`. | Use the catalog entry; confirm the parent `List` and data source first. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Table | Show tabular record lists. | Use the catalog entry; create or confirm the data producer before the Table. If `current_contextual_sources` is present, use those current ODC notes for Aggregate/list-source review guidance only; they are not an exact widget reference and do not promote evidence beyond the catalog entry. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Label | Label a form input. | Use the catalog entry; confirm the target input or accessible purpose before adding the label. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Text Area | Capture multi-line text input. | Use the catalog entry; bind to an existing local variable or form field. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Checkbox | Capture boolean values. | Use the catalog entry; bind to an existing Boolean variable or form field. When there are no `current_contextual_sources`, use `o11_candidate_support` as support-only guidance, confirm the exact binding and accessibility behavior in ODC Studio, and do not invent exact properties or events. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Switch | Capture Boolean toggle values. | Use the catalog entry; bind to an existing Boolean variable or form field. When there are no `current_contextual_sources`, use `o11_candidate_support` as support-only guidance, confirm the exact toggle binding and accessibility behavior in ODC Studio, and do not invent exact properties or events. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Radio Group | Capture one option from a small set. | Use the catalog entry; confirm the option source before binding. Treat `Radio Button` only as a legacy/supporting O11 alias when present in `o11_candidate_support`. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Button Group | Add grouped actions or selection controls. | Use the catalog entry; confirm actions or options first. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Dropdown | Select one value from a known list. | Use the catalog entry; create or confirm the options list before binding the selected value. If `current_contextual_sources` is present, use those current ODC notes for Aggregate-backed options list, options text, and Max. Records review guidance only; they are not an exact widget reference and do not promote evidence beyond the catalog entry. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Popover Menu | Add contextual actions. | Use the catalog entry; confirm menu actions and target handlers first. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Image | Display static or dynamic images. | Use the catalog entry; confirm the image source and accessibility text. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Icon | Add simple iconography. | Use the catalog entry; do not infer Mobile UI from icon library alone. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Upload | Capture files or binary content. | Use the catalog entry; confirm the upload handling action and storage flow before wiring events. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Screen | Define UI destinations and screen-level layout structure. | Use the catalog entry; confirm the target screen exists or add it before binding consumer UI. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |
| Web Block | Create reusable UI fragments for cross-screen reuse. | Use the catalog entry; confirm block inputs, producer dependencies, and consumer wiring before reuse. | Catalog entry decides: `Current official`, `O11-supported ODC candidate`, or `Unverified gap` |

Standard widget prompts must still follow producer-first order:

```text
1. Confirm data and logic producers.
2. Confirm screen or block shell.
3. Add standard widgets bound to existing producers.
4. Wire events only after target actions exist.
5. Add review notes.
```

## Tier 2: OutSystems UI Patterns

Use this tier only when the exact pattern exists in `odc-ui-pattern-catalog.json`.

The OutSystems UI (ODC) Forge documentation bridge routes the ODC component documentation to O11 "Using Mobile and Reactive Patterns". Treat that as current official routing evidence for OutSystems UI pattern documentation in ODC, while keeping exact pattern facts tied to the generated catalog or current docs.

Before emitting guidance, copy or summarize the relevant catalog facts:

- pattern name
- applies-to
- mandatory properties
- important optional properties
- events
- placeholders
- compatibility notes
- security or sanitization notes
- evidence label

Rules:

- Use `Catalog-backed official` when exact pattern facts come from the catalog and no curated recipe exists.
- Use curated recipes only for supported paste-ready generation after framework selection confirms the target.
- Do not imply catalog-backed patterns have proven Mentor Studio recipes.
- For Mobile app + OutSystems UI, use catalog facts only when `applies_to` includes `mobile apps`, and emit catalog-backed guidance/review unless mobile Mentor generation is verified.

## Tier 3: Special Dependencies And Components

Use this tier when the requested UI depends on public dependencies, shared producers, or component-specific references before consumer UI can be generated.

| Component or dependency | Use when | Required setup before consumer prompts | Evidence status |
| --- | --- | --- | --- |
| OutSystems Data Grid for ODC | Editable or advanced grid behavior is requested. | Confirm Data Grid dependency is added or list manual preflight when missing; read `odc-data-grid-reference.json` for exact documented facts before writing consumer prompts. | `Current official` for documented Data Grid facts; `Unverified gap` for source gaps |
| Reusable Web Block from Library | A consumer screen should reuse a public block. | Create or confirm producer Library, public block, and consumer dependency first. | `Current official` for library placement; `Unverified gap` for app-specific block details |
| OutSystems UI public implementation evidence reference | A property, event, placeholder, dependency, compatibility detail, SCSS family, deprecated/preview marker, ODC/O11 variant, or non-`*Config.ts` TypeScript/API clue is not covered by current docs, generated catalogs, or curated recipes, but the local `OutSystems/outsystems-ui` mirror has a source-backed note. | Read `outsystems-ui-implementation-reference.json` after framework selection and catalog checks; consult its top-level `gap_analysis` first for family discovery, SCSS coverage, non-config TypeScript/API surface, deprecated/preview markers, and ODC/O11 implementation variants; include source-backed review notes only. | `OutSystems-public implementation evidence` when repo-only facts materially affect the answer; state they are not current ODC product-contract authority unless current ODC docs, Forge routing/version evidence, or tenant observations confirm the exposed behavior |
| Shared theme or UI asset from Library | Multiple apps should share visual assets. | Create or confirm producer Library and versioned consumer dependency first. | `Current official` for library placement; `Unverified gap` for app-specific theme details |
| Future dependency-sensitive component | A component requires explicit dependency setup or external reference facts. | Confirm source coverage and manual setup before consumer UI generation. | `Unverified gap` until source coverage is added |

For approved pattern-specific fallbacks, route to `odc-ui-generation.md` > `Approved Pattern Review Note Matrix`. That matrix currently covers Dropdown Search, Tabs, Date Picker, Carousel, Range Slider, Range Slider Interval, Month Picker, Time Picker, Date Picker Range, Dropdown Tags, Gallery, Accordion, Flip Content, Tooltip, Animated Label, Bottom Sheet, Notification, Search, Sidebar, Video, Section Index, Submenu, Progress Bar, Progress Circle, Rating, Button Loading, Inline SVG, Swipe Events, Touch Events, Columns, Display on Device, Master Detail, Alert, Blank Slate, Card, Card Background, Card Item, Card Sectioned, Chat Message, Floating Content, List Item Content, Section, Section Group, Tag, User Avatar, Action Sheet, Animate, Floating Actions, Input with Icon, Lightbox Image, Scrollable Area, Stacked Cards, Bottom Bar Item, Breadcrumbs, Pagination, Timeline Item, Wizard, Badge, Counter, Icon Badge, Align Center, Center Content, Margin Container, Mouse Events, Separator. Keep catalog-backed facts from Tier 2 as the primary authority. Use source-backed implementation entries only as review notes, label them `OutSystems-public implementation evidence` when used, and state they are not current ODC product-contract authority unless current ODC docs, Forge routing/version evidence, or tenant observations confirm the exposed behavior. For matrix rows with no bounded implementation-reference entry, keep the guidance catalog-primary, label the output `Catalog-backed official`, and use the row as ODC Studio review guidance rather than repo-evidence guidance.

For catalog-wide pattern coverage maintenance, use `odc-ui-pattern-coverage-queue.md` as the durable catalog-wide pattern coverage queue. Every practical non-Data-Grid catalog pattern must have `matrix-row` disposition with matrix and fixture coverage; the `web_catalog_depth_*.md` fixture set provides the richer pattern-by-pattern prompt guidance examples, while `web_catalog_wide_pattern_review_notes.md` remains the broad review-note fixture. Data Grid task-style entries stay `covered-by-reference` through `odc-data-grid-reference.json`. `catalog-only` remains an allowed historical disposition for queue parsing, but the active completion target is zero `catalog-only` rows.

Special dependency prompts must include:

```text
Manual setup required before this prompt:
- Add dependency on [ProducerName] through Manage Dependencies.
```

Mentor Studio cannot add public dependencies by itself. Tell Paulo when a manual dependency update is required.

## Selection Checklist

Before writing a UI prompt or guidance block:

```text
1. Did framework selection run?
2. Is paste-ready generation supported for this target?
3. Can standard widgets satisfy the request?
4. Is an OutSystems UI pattern justified and catalog-backed?
5. Is a dependency-sensitive component involved?
6. Are all producers and dependencies listed before consumers?
```

If the answer to step 2 is no, emit guidance/review only and do not emit `### Mentor Studio Prompt`.
