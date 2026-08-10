---
name: osui-layouts
description: How to pick the right Layout block for a Reactive Web screen, and the placeholder structure each Layout exposes. Load this BEFORE building any screen — picking the wrong layout (especially defaulting to LayoutBlank) is the #1 source of fake-looking screens.
---

# OutSystems UI — Layouts


> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `ui-frameworks/outsystems-ui/layouts.md` (harvested 2026-07-29, two-way merge onto local wireframe-tuned base).
> **Merge note:** local corrections preserved where noted in `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.

Every Reactive Web screen wraps in **exactly one Layout block** at the root. The Layout owns the chrome (sidebar, top bar, header, footer) and exposes named placeholders for content. **Pick the Layout first** — it dictates everything that comes after.

Layouts live in the **app's own `Layouts` flow** (not in the OutSystemsUI library).

## Picking a Layout

| Request says… | Layout | Why |
|---|---|---|
| "sidebar nav" / "side menu" / "left navigation panel" | `LayoutSideMenu` | Persistent left sidebar with `Navigation` placeholder + main content area. **Top bar is baked in** (don't add a second Layout). |
| Sidebar nav AND top header bar (banking apps, B2B dashboards, admin consoles, most authenticated SaaS) | `LayoutSideMenu` | Top bar is built in. Fill the `Header` placeholder for per-screen middle content. |
| "top nav" / horizontal menu with tabs across the top, NO left sidebar | `LayoutTopMenu` | Top bar with `Menu` block + 6-placeholder content tree. |
| Modal / popup with no chrome at all (login, embed, print stylesheet) | `LayoutBlank` | No menu, no chrome, just `MainContent`. |
| Marketing / landing page — long scrolling page of stacked sections | `LayoutBase` | Two main placeholders (`Header`, `MainContent`) and a menu already on top. Simpler than `LayoutTopMenu`; same input parameters. |
| A **section within** a `LayoutBase` landing page | `LayoutBaseSection` | Not a screen-root chrome choice in the normal case — ODC's Themes doc describes it as nesting *inside* `LayoutBase` to define landing-page sections. It carries no menu of its own. |

**Don't default to `LayoutBlank` for full screens.** It gives nothing — no header, no nav, no chrome. Most user requests imply `LayoutSideMenu` or `LayoutTopMenu`. If the request mentions a left sidebar with nav items, use `LayoutSideMenu` (even if the design also has a top header bar — that comes for free).

**Exactly ONE Layout per screen — never nest.** Two Layout blocks at the screen root = duplicate placeholders, broken responsive grid, unfilled chrome, wireframe-sandwich rendering.

## ⚠️ MANDATORY: delete the default `LayoutTopMenu` before adding your chosen Layout

**The platform scaffolds every new screen with a default `LayoutTopMenu` widget at the screen root.** If you skip this step and just add your chosen Layout, you end up with **two Layouts at the screen root** — the default `LayoutTopMenu` (still there with empty placeholders) AND your new one. The page renders both stacked.

Spec rule: **inspect, delete the default, then add the chosen Layout** — and add an acceptance-checklist item: *"Screen root has exactly one widget whose SourceBlock name starts with `Layout`."*

## Placeholder structure

### `LayoutSideMenu`

| Placeholder | Required content | Notes |
|---|---|---|
| `Navigation` | **`Menu` block instance** (from app's `Common` flow), with nav entries as `Link` widgets inside `Menu.PageLinks` | The left rail. **MUST** wrap a `Menu` block — never raw `Container` of nav items, never `AdvancedHtml Tag="nav"`. |
| `Header` | (often empty) | **Middle slot of the top bar only.** Brand and user widget are baked in (see anatomy below) — use this for per-screen content like a search box, breadcrumbs, or quick filters. |
| `Breadcrumbs` | (often empty or `Breadcrumbs` block) | |
| `Title` | `AdvancedHtml` `Tag: "h1"` with screen title | **MUST** go here — never inline in `MainContent`. |
| `Actions` | (often empty or primary action button) | Screen-level actions. |
| `MainContent` | Screen body | |
| `Footer` | (often empty) | |

**Top-bar anatomy** — three regions, only the middle one is per-screen:

```
┌──────────────────────┬─────────────────────────────┬──────────────────────┐
│  ApplicationTitle    │       Header  placeholder   │        UserInfo      │
│  (block in Common)   │       (per-screen content)  │  (block in Common)   │
└──────────────────────┴─────────────────────────────┴──────────────────────┘
```

- **Brand wordmark** → already exists as the `ApplicationTitle` block in `Common`, with an Expression bound to the app name. To restyle, edit `Common/ApplicationTitle` (add `ExtendedClass` + a theme CSS rule). **Don't hand-roll a wordmark** elsewhere.
- **Right side (user avatar, name, dropdown, AND chrome icons like notification bell, mailbox, theme toggle)** → owned by `Common/UserInfo`. Add chrome icons there, not in the `Header` placeholder.

### `LayoutTopMenu`

Six placeholders, in this order:

| Placeholder | Required content |
|---|---|
| `Header` | **`Menu` block** (REQUIRED — `Link` widgets in `Menu.PageLinks`) |
| `ActionButton` | header-level action button (often empty) |
| `Breadcrumbs` | breadcrumb trail (often empty) |
| `Title` | `AdvancedHtml` `Tag: "h1"` with screen title |
| `Actions` | screen-level action buttons (often empty) |
| `MainContent` | screen body |

Brand and user widget are baked into the Layout block's own widget tree — not placeholders. To change them, edit `LayoutTopMenu` in the app's `Layouts` flow.

### `LayoutBlank`

Single `MainContent` placeholder. **Truly no chrome** — no brand, no user widget, no top bar. Use ONLY for popup screens / modal content / explicit "no chrome" requests.

### `LayoutBase`

Two main placeholders — `Header` and `MainContent` — and a **menu already on top**. ODC's Themes doc positions it for landing pages "due to its simplicity". Same input parameters as `LayoutTopMenu` (fixed-on-scroll menu, accessibility options, extended CSS classes). Because it carries a menu, a blueprint choosing it should also carry `app_chrome.menu` — the validator warns when it does not, exactly as for `LayoutTopMenu`/`LayoutSideMenu`.

### `LayoutBaseSection`

The section block a `LayoutBase` page stacks to build landing-page sections, "similar to what you find in traditional website landing pages". **It carries no chrome of its own** and is not menu-bearing. Normally it appears *nested inside* `LayoutBase` rather than as the screen root — reach for it as a screen's `layout_block` only when the screen genuinely is one such section.

## When the design feels "too custom" for a Layout block (the dark-mode trap)

> ⚠️ **A bespoke visual design does NOT mean `LayoutBlank` + custom flex shell.** This is the failure mode where the agent looks at a rich design spec — dark mode, custom sidebar styling, non-default spacing, brand colors — and concludes "I need full control of the page surface." It then picks `LayoutBlank` and writes 100–300 lines of custom CSS re-implementing the sidebar grid, header strip, scrollable main area, hover states, scrollbar styling, etc. **Every line of that custom shell is regression to fake UI.**

The right move when the design looks visually custom:
1. **Pick the same Layout you'd pick if the design were "default styled"** — sidebar nav → `LayoutSideMenu`, top nav → `LayoutTopMenu`.
2. **Override OS UI CSS variables on the THEME's StyleSheet** (`--color-background-body`, `--color-neutral-0`–`-10`, `--color-primary`, etc.) — see [`styles-and-utilities.md#theming-the-app-dark-mode-full-rebrand-palette-swap`](styles-and-utilities.md#theming-the-app-dark-mode-full-rebrand-palette-swap).
3. **Fill placeholders with OS UI blocks** — `Card`, `CardSectioned`, `Columns*`, `IList` + `ListItemContent`, `UserAvatar`, `IconBadge`, `ProgressBar`, `Tag`, `Counter`. The blocks pick up the new theme variables automatically. You get dark mode for free.
4. **For per-screen visual flourishes** (a hero gradient, a specific card's accent border) — write a SHORT custom class on the screen's StyleSheet and apply via `Style` / `ExtendedClass`. Maximum ~5–15 lines of custom CSS per screen.

**Concrete heuristic — if you're about to write any of these in a screen StyleSheet, you've taken a wrong turn:**

| About to write | Stop and use |
|---|---|
| `min-height: 100vh; display: flex` for the page shell | `LayoutSideMenu` / `LayoutTopMenu` (the layout owns the shell) |
| `.sidebar { width: 240px; position: sticky; }` | `LayoutSideMenu` (the layout owns the sidebar grid) |
| `.topbar { display: flex; justify-content: space-between }` for the page header strip | `LayoutSideMenu`'s baked-in top bar + the `Header` placeholder for middle content |
| `.main { flex: 1; overflow-y: auto; padding: 24px }` | `LayoutSideMenu.MainContent` placeholder — overflow + padding handled by the layout |
| `.card { background: ...; border: ...; border-radius: ...; padding: ... }` | `Card` block (theme-aware shadow, radius, padding via `UsePadding` arg) |
| `.avatar { border-radius: 50%; background: linear-gradient(...) }` with initials inside | `UserAvatar` block (handles initials fallback, theme-aware) |
| `.notif-badge { position: absolute; top: -4px; right: -4px; ... }` over an icon | `IconBadge` block from `OutSystemsUI/Numbers` |
| `.progress-track { ... } .progress-fill { width: 68%; ... }` | `ProgressBar` block from `OutSystemsUI/Numbers` |
| `display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px` | `Columns4` block from `OutSystemsUI/Adaptive` |
| `.tx-list { display: flex; flex-direction: column }` of `.tx-row` divs | `IList` widget over an aggregate, with `ListItemContent` block per row (or `CardItem`) |
| `.donut { background: conic-gradient(...) }` | `DonutChart` block from `OutSystemsCharts/Charts` + `ChartLegend` addon |

If five or more rows in this table apply to the screen you're building, **you're rebuilding OutSystems UI inside `LayoutBlank`.** Switch to `LayoutSideMenu` (or `LayoutTopMenu`) and refactor the divs into blocks. The result is shorter, theme-aware, accessible, and responsive without any of the custom CSS.

### What "highly custom" actually justifies

A truly custom visual treatment justifies:
- A custom theme StyleSheet (variable overrides at `:root` on the theme).
- Per-screen visual flourishes via short `ExtendedClass` rules (a gradient on one card, a hero header background, an animation keyframe).
- A handful of bespoke utility classes (e.g. `.hb-vcard__chip` for a card-chip ornament).

It does NOT justify:
- A custom layout shell (the layout block does this).
- Custom card / avatar / badge / progress / chart / list reimplementations (the OS UI blocks do this).
- Hand-rolled responsive grid (the `Columns*` blocks + their `PhoneBehavior` arg do this).
- Hand-rolled scrollable main / sticky sidebar / overflow handling (the layout block does this).

### Reality check before you reach for LayoutBlank

Ask: "Of the visual specifics I want, which can be expressed as (a) theme variable override, (b) extended class on an existing block, (c) per-screen StyleSheet rule applied via ExtendedClass on a specific block?" If the answer for >80% of the specifics is "yes, those three," use `LayoutSideMenu` / `LayoutTopMenu`. The remaining 20% is what `Style` / `ExtendedClass` / per-screen StyleSheet rules are FOR.

`LayoutBlank` is for: modal popup screens, embed views, print-stylesheet variants — things that genuinely have no chrome. It is NOT for: "this design looks too custom for a layout block." That's the trap.

### The same trap applies to "card" surfaces

The exact same intuition that pushes the agent toward `LayoutBlank` under design pressure pushes it toward `Container` + custom class instead of `Card` block. Whenever the design says "card" — whether it's a stat card, a metric tile, a payment card surface, a toggle card, a perk chip — that ALWAYS means a real `Card` (or `CardSectioned` / `CardItem` / `CardBackground`) block. The visual treatment (gradients, dark surface, glow, scale-on-hover) goes via `ExtendedClass` arg + a SHORT custom class defined in the theme — NOT via wholesale `Container` + 200-line stylesheet.

**If you find yourself giving a `Container` a project-prefix-shaped class (`<project-prefix>-card`, `<project-prefix>-stat-card`, `hb-vcard--indigo`):**
1. Stop. The widget you're styling should be a `Card` block instance.
2. Replace the `Container` with `IMobileBlockInstanceWidget` whose `SourceBlock` is the OS UI `Card` (or `CardSectioned` / `CardItem`).
3. If you still want a one-off visual treatment, pass it via the `Card.ExtendedClass` argument (value `"linear-background-primary"`) and define `linear-background-primary` in the theme StyleSheet (NOT the screen StyleSheet).
4. **Verify the class is actually defined somewhere**. Applying a class name without defining `.my-class` in any stylesheet is a no-op — the widget renders with default styling and the visual treatment never appears.

The same rule applies to:
- **`UserAvatar`** — never a `Container` + `.hb-avatar` with `border-radius: 50%` + gradient. Use the block.
- **`IconBadge`** — never a `Container` + `position: absolute; top: -4px;`. Use the block.
- **`ProgressBar`** — never `<div class="track"><div class="fill" style="width: 68%">`. Use the block.
- **`Tag`** — never a `Container` + `.hb-perk-chip` with `border-radius: 99px`. Use the block.
- **`StackedCards`** — never a custom-CSS card-stack with hand-rolled swipe handlers. Use the block from `OutSystemsUI/Interaction`.

See [`structural-skeleton.md`](structural-skeleton.md) § "Block-inventory commitment" for the forcing function: explicit "this region → that block" mapping before anything is emitted.

## Where Layouts live in the model

Layouts are **local to the app** in the `Layouts` flow (NOT in the OutSystemsUI library). In blueprints, name the layout block bare (`LayoutSideMenu`, `LayoutTopMenu`, `LayoutBlank`). Placeholder names are usually consistent across templates but can vary slightly — the build side verifies the exact names against the app's own `Layouts` flow.

## Title placeholder — always `AdvancedHtml` h1

The screen title goes in the `Title` placeholder using `AdvancedHtml` with `Tag: "h1"`, never as plain text in `MainContent`:

```jsonc
{
  "Object": "PlaceholderContentWidget", "Placeholder": "Title",
  "Widgets": [{
    "Name": "ScreenTitle", "Object": "AdvancedHtml", "Tag": "h1",
    "content": [{ "Object": "TextWidget", "Text": "Request List" }]
  }]
}
```

This pattern (named widget + `Object: "AdvancedHtml"` + `Tag: "h1"` + a `TextWidget` child) is the canonical OS UI title — preserves heading semantics for accessibility and theme styling.

## Anti-patterns

❌ **Nesting two Layout blocks** because the design has both a sidebar AND a top header bar. `LayoutSideMenu` already includes a top bar (ApplicationTitle / `Header` placeholder / UserInfo). Use `LayoutSideMenu` alone — fill `Header` for per-screen middle content; edit the Layout block in the app's `Layouts` flow if the brand or user widget needs to change. Two Layout blocks at the screen root means duplicate placeholders, wasted chrome, and a broken responsive grid.

❌ **Renaming the Layout instance to "Layout"** (or any generic name). Keep the SourceBlock name (`LayoutSideMenu`, `LayoutTopMenu`) as the instance name so the widget tree stays self-documenting.

❌ **Trying to put a logo / brand image / user avatar inside the `Header` placeholder** of `LayoutSideMenu` or `LayoutTopMenu`. Those are baked-in widgets owned by the Layout block (`ApplicationTitle`, `UserInfo`) — the placeholder is only the middle slot. To change brand or user widget, edit the matching block in the app's `Common` flow (`Common/ApplicationTitle`, `Common/UserInfo`) — not the Layout.

❌ **Hand-rolling a brand wordmark as an `AdvancedHtml h1` + styled `TextWidget`** (e.g. inserting "WISE" / "ACME" inside the Menu block or as a custom widget in the sidebar). Every OS app already has an `ApplicationTitle` block in `Common` with an Expression bound to the app name. The correct move is to open `Common/ApplicationTitle`, style its existing expression via `ExtendedClass` + a theme-StyleSheet rule (font, weight, letter-spacing, transform, color), and let the binding own the text. Hand-rolled wordmarks duplicate the brand text, drift on app rename, and end up rendering twice (in `ApplicationTitle` AND wherever you placed the duplicate).

❌ **Putting the notification bell / mailbox icon / status indicator / quick-action icon in the `Header` placeholder** of `LayoutSideMenu` or `LayoutTopMenu`. The `Header` placeholder is the MIDDLE slot of the top bar — for per-screen content (search box, breadcrumbs, quick filters). Chrome icons that cluster with the user avatar (bell-with-badge, mail icon, theme toggle, language switcher) belong inside `Common/UserInfo` — that block owns the entire right side of the top bar and is the canonical home for those affordances. Adding the bell to `Header` drifts it left of the avatar and reads as a header artifact instead of a chrome control. To add a bell to UserInfo: open `Common/UserInfo`, drop in an `IconBadge` block (with `IIcon` Phosphor `bell` in its `Icon` placeholder) to the left of the existing avatar widget.

❌ **Defaulting to `LayoutBlank`** and building a custom `<Container Style="my-sidebar">` for the sidebar. `LayoutSideMenu` already has the right grid + collapse behavior.

❌ **Putting the screen title as plain text or `<h1>` directly in `MainContent`.** Use the `Title` placeholder with `AdvancedHtml Tag="h1"`.

❌ **Skipping empty placeholders in widget JSON** for `LayoutTopMenu`. All 6 must be present in order — missing ones cause silent layout failures.

❌ **Using `Container` to mimic a layout** (e.g. `Container > Container > Container` to fake `LayoutTopMenu`'s grid). Lose responsive behavior, theme integration, and accessibility roles.

❌ **Putting raw `Link` widgets, `Container`s, or `AdvancedHtml Tag="nav"` directly in `LayoutSideMenu.Navigation` or `LayoutTopMenu.Header`.** These placeholders are for `Menu` block instances. Nav links go inside `Menu.PageLinks` as `Link` widgets — see the upstream `recipes/sidebar-navigation.md` (not bundled).

### Chrome-placement variance (wireframe vs stock layout)

Wireframes routinely draw chrome in non-stock positions — the user identity at the
bottom of the sidebar, the brand centered, a bell in the footer. The rule: **map the
element to its stock block anyway** (`Common/UserInfo`, `Common/ApplicationTitle`,
etc.) **and disclose the placement delta** as a `review_notes` entry plus an
acceptance-checklist item ("resolve deliberately"). Never invent a custom widget,
never nest a second Layout, and never relocate a stock block's markup to honor the
drawn position — placement fidelity is a theme/implementation decision that belongs
downstream, not a structure decision for the blueprint.
- ❌ **Defaulting to `LayoutBlank`** because the design "looks too custom." A bespoke visual treatment goes via theme variable overrides + `ExtendedClass`, not a custom layout shell.
- ❌ **Putting the screen title as plain text in `MainContent`.** Use the `Title` placeholder with `AdvancedHtml Tag="h1"`.
- ❌ **Skipping empty placeholders in `LayoutTopMenu`** — all 6 must be present in order.
- ❌ **Using `Container` to mimic a layout** (`Container > Container > Container` to fake the grid). Loses responsive behavior, theme integration, accessibility roles.
- ❌ **Putting raw `Link` widgets, `Container`s, or `AdvancedHtml Tag="nav"` directly in `Navigation` / `Header`.** These placeholders are for `Menu` block instances; nav links go inside `Menu.PageLinks`.
