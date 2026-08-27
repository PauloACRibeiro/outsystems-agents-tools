---
name: atomic-design-methodology
description: Atomic Design composition methodology applied to OutSystems — atoms (built-in widgets), molecules (small Blocks), organisms (composite Blocks), templates (Layouts + Screen Templates), pages. Use when deciding whether to extract a custom Block, where to put logic, or how reusable a UI piece should be.
---

# Atomic Design in OutSystems

> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `common/atomic-design.md` (harvested 2026-08-26).
> **Merge note:** design-filtered harvest — ODC-scoped; see `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.


> A way of thinking about UI composition: build up from small, single-responsibility pieces to full pages. Useful for deciding *where* a piece of UI belongs (a widget? a Block? a screen?) and how reusable it should be.

Adapted from Brad Frost's [Atomic Design](https://atomicdesign.bradfrost.com/chapter-2/) methodology. The full book is the canonical reference; this file translates the five stages into OutSystems' building blocks (widgets / patterns / Blocks / screens) and gives concrete guidance for composing UI in ODC.

## The five stages

Atomic Design borrows a chemistry analogy: small things combine into larger things, and what you build *out of* something matters as much as what you build *with* it.

| Stage | OutSystems analog | Reusability |
|---|---|---|
| **Atoms** | Built-in widgets — `Button`, `Input`, `Label`, `Icon`, `Image`, `Text`, `Expression`, `Container` | App-wide |
| **Molecules** | Small composed Blocks / simple OutSystems UI patterns — `InputWithIcon`, `Tag`, `Badge`, `BreadcrumbsItem`, `TabsHeaderItem`, a custom `LabeledInput` | App-wide / module-wide |
| **Organisms** | Larger OutSystems UI patterns + your own composite Blocks — `Card`, `Accordion`, `Tabs`, `Wizard`, `MasterDetail`, a custom `ProductCard`, a `UserProfileHeader` | Module-wide / feature-wide |
| **Templates** | Layouts + Screen Templates — `LayoutTopMenu`, `LayoutSideMenu`, the `List` / `Detail` / `Dashboard` scaffolds | App-wide |
| **Pages** | Actual screens with real data wired up | One per screen |

The point isn't to assign every UI element a strict label — it's to **think about composition direction** (smaller → larger) and **reusability scope** (where does this thing belong, and how often will it be reused?).

## Atoms

The smallest pieces — single-responsibility primitives that can't be broken down without losing meaning. In OutSystems these are **built-in widgets**.

**OutSystems atoms:**

- Form / input: `Input`, `TextArea`, `Checkbox`, `Switch`, `RadioButton`, `Dropdown`, `Upload`
- Action: `Button`, `Link`
- Display: `Text`, `Expression`, `Label`, `Icon`, `Image`, `AdvancedHtml`
- Structure: `Container`, `Placeholder`

**Guidance:**

- Don't reimplement atoms with custom HTML or `AdvancedHtml`. The built-in widgets carry accessibility, validation, and theming for free.
- Atoms get most of their visual identity from the framework's CSS variables / utility classes — don't hardcode colors or sizes on individual widget instances.
- Naming matters. `Input_FirstName`, not `Input_1`. The name is what `Label.TargetWidget`, ScreenAction args, and `WidgetId` lookups reference.

## Molecules

Simple, **single-responsibility** combinations of atoms. A molecule does one thing well: a labeled input, a search field, a tag chip, a single breadcrumb.

**OutSystems molecules:**

- Existing OutSystems UI patterns that group 2–3 atoms: `InputWithIcon` (Input + Icon), `Tag` (Container + Text), `Badge` (Container + Number), `BreadcrumbsItem`, `TabsHeaderItem`, `WizardItem`, `BottomBarItem`.
- Custom Blocks you build for one focused purpose: a `LabeledInput` Block that pairs a `Label` and an `Input` with the right `TargetWidget` wiring; a `RequiredFieldHint`; a `KPIValue` showing a number + delta.

**Guidance — when to extract a molecule into a custom Block:**

- The same 2–3 atoms appear together **3+ times** with the same wiring.
- The combination has its own validation, label association, or accessibility behavior worth centralising.
- It's small enough to fit on a screen of code and has a clear single purpose.

If your molecule is starting to take 5+ inputs and orchestrate aggregates — that's not a molecule anymore, it's an organism (see below).

## Organisms

**Sections of an interface** — composed from molecules, atoms, and sometimes other organisms. They're large enough to carry their own context and small enough to drop into multiple places.

**OutSystems organisms:**

- Larger built-in patterns: `Card`, `CardSectioned`, `Accordion` (with its `AccordionItem` molecules), `Tabs` (with its header and content items), `Wizard`, `MasterDetail`, `Sidebar`, `BottomSheet`, `Carousel`.
- Custom composite Blocks you build for a feature: a `ProductCard` (image + title + price + add-to-cart), a `UserProfileHeader` (avatar + name + role + actions), a `BookingForm` (date pickers + guest count + price summary + book button).

**Guidance — when to build a custom organism Block:**

- The composition is reused across **2+ screens** and copying it would create drift.
- It has its own internal state (a `LocalVariable` not just a passed-through value) or its own ScreenAction.
- It encapsulates a feature concept (`ProductCard` is a thing in your domain; `Container around an Input and a Button` is not).
- It exposes a clean interface: a few input parameters, 1–3 events, named placeholders.

**Don't build an organism Block when:**

- It's only used on one screen — that's a screen-local concern.
- Its inputs would be 10+ parameters that vary per consumer — that's a leaky abstraction; let the consumer compose atoms / molecules directly.
- The "reuse" is across two screens but each customizes ~half the behavior — extract a smaller molecule and let the screens compose the rest.

## Templates

**Page-level layouts** that articulate the structure without final content. In OutSystems, this is the combination of:

- **Layouts** (`LayoutTopMenu`, `LayoutSideMenu`, `LayoutBlank`) — the chrome (header, menu, footer, content area) into which screens slot.
- **Screen Templates** (the scaffolds: `List`, `Detail`, `Form`, `Dashboard`, `Empty`) — pre-built screen archetypes containing a layout, the typical patterns for that archetype, and sample data.

**Guidance:**

- Pick the closest Screen Template archetype when scaffolding a new screen. See [`screen-templates.md`](screen-templates.md).
- Templates own *structure*, not content: the `List` template lays out a search input, table, and pagination, but doesn't dictate what fields the list shows.
- Don't reach for `Empty` (the blank scaffold) unless the screen is genuinely an outlier. Most screens fit one of the standard archetypes — even if you have to swap a few patterns afterwards.
- A custom Layout (an organisation-specific shell) is a template when it's used across the app. A one-off layout for a single landing page is a screen, not a template.

## Pages

**Specific instances of a template with real data**. In OutSystems, this is your actual `UIScreen` definitions: aggregates fetching real data, ScreenActions wired to server actions, real text and images.

**Guidance:**

- Pages are where edge cases surface — empty states, long names, slow networks, permission denials. Always test:
  - The empty state (use `BlankSlate`).
  - The loading state (rely on the aggregate's `IsDataFetched` or render a skeleton).
  - The permission-denied / forbidden state.
  - Long content (a 200-character title, a list with 10,000 items).
- If a page reveals that a pattern doesn't work for real content (the title overflows, the table doesn't paginate well), fix the pattern or switch to a different one — don't hack the page.
- A page-only tweak that you're tempted to repeat across screens is the signal to push the change down into an organism or template.

## Composition direction

**Build up, don't build sideways.**

```
Atoms → Molecules → Organisms → Templates → Pages
```

When designing a new screen:

1. Pick the **template** (Screen Template + Layout) closest to the archetype.
2. Identify which **organisms** you need (existing OutSystems UI patterns, then your own custom Blocks).
3. Compose organisms from **molecules** — small combinations that already exist or are worth extracting.
4. Molecules use **atoms** — the built-in widgets — for their primitives.
5. Wire the **page** to real data: aggregates, ScreenActions, navigation arguments.

When auditing existing UI:

- "Is this a molecule masquerading as an organism?" If a Block has 12 inputs and 5 events, it's probably trying to be too many things — split it.
- "Is this an organism we keep recreating as page-local code?" If three screens have a copy-pasted product-summary container, extract it into a `ProductSummary` Block.
- "Is this a page-level concern leaking into an organism?" If a Block fetches data from a specific aggregate by name, it's coupled to a screen — pass the data in via inputs.

## Anti-patterns

- **Building a "GodBlock"** — one Block that orchestrates a whole feature with 20 inputs. It becomes a copy of the screen, just less reusable.
- **Custom atoms** — replacing `Button` or `Input` with your own widget. You'll lose accessibility, validation, theming, and platform behavior.
- **Skipping the molecule layer** — going straight from atoms to a custom organism every time. You miss the cheap reuse wins (the labeled-input pair that appears in every form).
- **Page-specific organisms** — a "Block" used only on one screen. It adds indirection without reuse benefit; inline the composition.
- **Treating Screen Templates as one-shot scaffolds** — modifying every pattern they ship until the template's structure is unrecognizable. Either commit to the template's archetype or pick a different one.
- **Pages without templates** — a screen built from `Empty` because "the templates don't fit," when in fact the closest template would have worked with one or two pattern swaps.

## Quick decision aid

| You're about to… | Ask yourself |
|---|---|
| Add raw HTML via `AdvancedHtml` | Is there a built-in atom or pattern I'm replicating? Use that instead. |
| Copy-paste 4 widgets from one screen to another | Should this be a molecule (custom Block)? |
| Wrap an existing pattern in a Container with always-the-same-styling | Yes, extract a tiny custom Block. |
| Build a 600-line custom Block with its own aggregates | Should this be the screen, not a Block? Or split into smaller organisms? |
| Build the whole screen from `Empty` | Which Screen Template archetype is closest? |
| Override a pattern's internal styles to make it look different | Are you using the wrong pattern, or fighting the framework? |

## Related

- [Atomic Design (Brad Frost)](https://atomicdesign.bradfrost.com/chapter-2/) — the source.
- [`screen-templates.md`](screen-templates.md) — the template archetypes.
- [`blocks-index.md`](blocks-index.md) — the OutSystems UI organisms / molecules catalog.
- [`ui-reference.md`](ui-reference.md) — atom-level widget rules.
- Upstream `common/css-customization.md` (not bundled); see [`styles-and-utilities.md`](styles-and-utilities.md) — where atom-level styling lives.
