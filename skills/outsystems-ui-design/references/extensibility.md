---
name: osui-extensibility
description: The four-level OutSystems UI extensibility ladder — ExtendedClass CSS, typed Set-Provider-Configs/Event Client Actions, the direct JavaScript API, and the custom block wrapper. Use when a wireframe region needs behavior a pattern's inputs don't expose, before flagging custom_block_needed or declaring a reusable block.
---

# OutSystems UI — Pattern Extensibility (design reference)

> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `ui-frameworks/outsystems-ui/extensibility.md` (harvested 2026-08-05).
> **Merge note:** design-filtered harvest — condensed to the decision ladder and reference facts; the full JavaScript wrapper-class implementation is deliberately excluded per the design-only boundary contract (`maintenance/refresh-checklist.md`).
> See `maintenance/refresh-checklist.md` for the refresh procedure.

Patterns ship with inputs and events for the common cases. **Extensibility is
how a stock pattern goes beyond them without being forked.** For OUD this is a
*mapping decision aid*: a region that needs more than a pattern's inputs is
**not automatically `custom_block_needed`** — three of the four levels below
keep the stock block, and only level 4 means the design should declare a
reusable wrapper block. Everything here is reference-only context; OUD never
designs the actions or JavaScript itself.

## The four levels, cheapest first

| Level | Mechanism | Use when |
|---|---|---|
| 1 | `ExtendedClass` argument + theme CSS | Visual tweak only — brand colors, one-off styling. |
| 2 | `Set<Provider>Configs` / `Set<Provider>Event` Client Actions | A provider option or provider-native event the block's inputs don't expose. |
| 3 | Direct JS API (`OutSystems.OSUI.Patterns.<X>API`) | Imperative one-off — read state or call a method (e.g. `Tabs.SetActiveTab`, `Carousel.GoTo`) beyond what level 2 wraps. |
| 4 | Custom block wrapper | Reusable behavior + extra UI + persistent state on top of a stock pattern (e.g. "every DatePicker in this app has Apply/Reset"). |

Start at level 1 and escalate only when the level below doesn't cover the need.

## Provider-based patterns (level 2/3 candidates)

Several patterns are thin wrappers around third-party libraries; their less-common
options are reachable via typed Client Actions named after the provider:

| Pattern | Provider | Configs/Event actions |
|---|---|---|
| `Carousel` | Splide | `SetSplideConfigs`, `SetSplideEvent`, `UnsetSplideEvent` |
| `DatePicker`, `DatePickerRange`, `MonthPicker`, `TimePicker` | Flatpickr | `SetFlatpickrConfigs`, `SetFlatpickrEvent`, … |
| `DropdownSearch`, `DropdownTags` | VirtualSelect | `SetVirtualSelectConfigs`, … |
| `RangeSlider`, `RangeSliderInterval` | noUiSlider | `SetNoUiSliderConfigs`, … |

Reference facts (for honest acceptance checklists, not for OUD to design):
configuration runs from the pattern's `Initialized` event (an
`ExecuteClientActionNode` per config/event call); event handlers set at level
2/3 are torn down on destroy; the legacy `AdvancedFormat` string-JSON parameter
is deprecated in favor of these typed actions.

## How this feeds the Block Mapping Gate

When a wireframe region is *a stock pattern plus something extra*:

1. **Extra is visual only** → map the stock block; note the `ExtendedClass`
   treatment in the region description. Not a custom block.
2. **Extra is a provider capability** (carousel advancing 3-per-click, a date
   picker that stays open, a dropdown with custom no-results text) → map the
   stock block; disclose in `evidence_boundary.review_notes` /
   `acceptance_checklist` that the behavior rides on the pattern's provider
   extensibility (name the level-2 action). Not a custom block.
3. **Extra is genuinely new behavior + UI, and it repeats** (the same enriched
   pattern appears across screens) → this is the legitimate
   **wrapper-block** case: declare it in `blocks` as a wrapper *around* the
   named stock pattern, with the caller-specific affordances in placeholders
   (the under-observed-block rule in SKILL.md Step 4 applies in full).
4. **No stock pattern underneath at all** → only now is `custom_block_needed`
   (or compose-and-disclose) the answer.

**Never design the fork.** A region that seems to need a modified copy of a
pattern's internals maps to the stock pattern + a disclosed extensibility note,
or to a wrapper block — a forked pattern loses updates, accessibility fixes,
and platform support, and is not a shape OUD may emit.
