
# OutSystems UI — Styles & Utility Classes

> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `ui-frameworks/outsystems-ui/styles-and-utilities.md` (harvested 2026-07-29).
> **Merge note:** local corrections preserved where noted in `maintenance/refresh-checklist.md`.
> See `maintenance/refresh-checklist.md` for the refresh procedure.


> **Reference for everything OutSystems UI exposes via CSS:** utility classes you can apply with the `Style` argument, the canonical color palette, the spacing scale, typography classes, and the CSS custom properties on `:root` for theming.
>
> **Stack:** OutSystems UI (Reactive Web + Phone App Template). Mobile UI uses `--token-*` design tokens — different system, see [`design-tokens.md`](design-tokens.md).

## Naming convention

Three parallel forms for almost every value:

| Form | Pattern | Example |
|---|---|---|
| Utility class (background) | `.background-<name>` | `background-primary`, `background-neutral-7` |
| Utility class (text/foreground) | `.text-<name>` | `text-primary`, `text-error` |
| CSS custom property | `--color-<name>` / `--space-<name>` / etc. | `--color-primary`, `--space-base` |

For dimensions (spacing, sizes, shadows, radius), the convention is `.padding-<name>` / `.margin-<name>` / `.shadow-<name>` / `.border-radius-<name>` paired with `--space-<name>` / `--shadow-<name>` / `--border-radius-<name>`.

## Spacing

### Scale

| Name | Value | Class (padding) | Class (margin) | CSS variable |
|---|---|---|---|---|
| `none` | 0 | `padding-none` | `margin-none` | `--space-none` |
| `xs` | 4px | `padding-xs` | `margin-xs` | `--space-xs` |
| `s` | 8px | `padding-s` | `margin-s` | `--space-s` |
| `base` | 16px | `padding-base` | `margin-base` | `--space-base` |
| `m` | 24px | `padding-m` | `margin-m` | `--space-m` |
| `l` | 32px | `padding-l` | `margin-l` | `--space-l` |
| `xl` | 40px | `padding-xl` | `margin-xl` | `--space-xl` |
| `xxl` | 48px | `padding-xxl` | `margin-xxl` | `--space-xxl` |

### Directional

For each scale value, all four sides are available individually:

```
padding-{top|right|bottom|left}-{none|xs|s|base|m|l|xl|xxl}
margin-{top|right|bottom|left}-{none|xs|s|base|m|l|xl|xxl}
```

Examples: `padding-top-base`, `margin-bottom-l`, `padding-left-xs`.

### Axis (vertical / horizontal)

For vertical (top + bottom) or horizontal (left + right) shorthand:

```
padding-{x|y}-{none|xs|s|base|m|l|xl|xxl}
margin-{x|y}-{none|xs|s|base|m|l|xl|xxl}
```

Examples: `padding-x-base` (left + right 16px), `margin-y-l` (top + bottom 32px).

## Colors

Every color has three forms: `.background-<name>`, `.text-<name>`, `--color-<name>`.

### Brand

| Name | Hex |
|---|---|
| `primary` | `#1068eb` |
| `secondary` | `#303d60` |

### Semantic

Each has a Base and Light variant:

| Name | Base | Light |
|---|---|---|
| `info` | `#017aad` | `#e5f5fc` (`info-light`) |
| `success` | `#29823b` | `#eaf3eb` (`success-light`) |
| `warning` | `#e9a100` | `#fdf6e5` (`warning-light`) |
| `error` | `#dc2020` | `#fceaea` (`error-light`) |

Use `.background-success-light` / `.text-success` (etc.) — the dark "Base" version usually goes on backgrounds when paired with white text, and the Light version pairs with the matching `.text-<name>` color (e.g. green text on light-green background for an Alert).

### Neutrals

11 shades from white (`neutral-0`) to near-black (`neutral-10`):

| Name | Hex | Common use |
|---|---|---|
| `neutral-0` | `#ffffff` | Surfaces, white text on dark |
| `neutral-1` | `#f8f9fa` | Page body background, lightest fills |
| `neutral-2` | `#f1f3f5` | Subtle backgrounds, hover states |
| `neutral-3` | `#e9ecef` | Card backgrounds, dividers |
| `neutral-4` | `#dee2e6` | Borders, separators |
| `neutral-5` | `#ced4da` | Disabled borders |
| `neutral-6` | `#adb5bd` | Disabled text, placeholder text |
| `neutral-7` | `#6a7178` | Secondary text |
| `neutral-8` | `#4f575e` | Body text alt |
| `neutral-9` | `#272b30` | Body text |
| `neutral-10` | `#101213` | Headings, high-contrast text |

### Color families

12 color families. Each has 7 shades: `darkest`, `darker`, `dark`, base (no suffix), `light`, `lighter`, `lightest`. Class form: `.background-<family>-<shade>` / `.text-<family>-<shade>`. CSS variable: `--color-<family>-<shade>`.

| Family | Base | Notes |
|---|---|---|
| `red` | `#f22800` | (red has the slightly different naming for `red-darkest/darker/dark/light/lighter/lightest`) |
| `orange` | `#f76707` | |
| `yellow` | `#f59f00` | |
| `lime` | `#74b816` | |
| `green` | `#37b24d` | |
| `teal` | `#087f5b` | |
| `cyan` | `#0d8091` | |
| `blue` | `#1a79cb` | |
| `indigo` | `#4263eb` | |
| `violet` | `#7048e8` | |
| `grape` | `#ae3ec9` | |
| `pink` | `#d6336c` | |

Examples: `.background-blue-light`, `.text-pink-darkest`, `var(--color-violet-lighter)`.

For brand and semantic colors, prefer `primary`/`secondary`/`info`/`success`/`warning`/`error` over the raw color family names — they survive a rebrand.

## Typography

### Font sizes

| Class (heading-style) | Class (size-only) | CSS variable | Desktop / Tablet / Phone |
|---|---|---|---|
| — | `font-size-display` | `--font-size-display` | 36 / 34 / 32 px |
| `heading1` | `font-size-h1` | `--font-size-h1` | 32 / 30 / 28 px |
| `heading2` | `font-size-h2` | `--font-size-h2` | 28 / 26 / 24 px |
| `heading3` | `font-size-h3` | `--font-size-h3` | 26 / 24 / 22 px |
| `heading4` | `font-size-h4` | `--font-size-h4` | 22 / 21 / 20 px |
| `heading5` | `font-size-h5` | `--font-size-h5` | 20 / 19 / 18 px |
| `heading6` | `font-size-h6` | `--font-size-h6` | 18 / 17 / 16 px |
| — | `font-size-base` | `--font-size-base` | 16 (body) |
| — | `font-size-s` | `--font-size-s` | 14 (body small) |
| — | `font-size-xs` | `--font-size-xs` | 12 (body extra small) |
| — | `font-size-label` | `--font-size-label` | 11 (label) |

Headings have responsive sizing built in (smaller on tablet/phone). Body sizes are flat 1.5 line-height.

Two ways to apply: `.heading2` (sets size + weight + spacing as a heading) vs `.font-size-h2` (sets only the size). Use `.heading*` for actual headings, `.font-size-h*` when you want just the size on something else (like a numeric Counter value).

### Font weight

| Class | Weight | Notes |
|---|---|---|
| `font-light` | 300 | Light |
| `font-regular` | 400 | Regular (body default) |
| `font-semibold` | 600 | Semibold |
| `font-bold` | 700 | Bold |

### Text transform

| Class | Effect |
|---|---|
| `text-lowercase` | All lowercase |
| `text-uppercase` | ALL UPPERCASE |
| `text-capitalize` | Title Case |
| `text-ellipsis` | Single-line overflow with `…` |

## Borders

### Radius

| Name | Value | Class | CSS variable |
|---|---|---|---|
| `none` | 0 | `border-radius-none` | `--border-radius-none` |
| `soft` | 4px | `border-radius-soft` | `--border-radius-soft` |
| `rounded` | 100px | `border-radius-rounded` | `--border-radius-rounded` |
| `circle` | 100% | `border-radius-circle` | `--border-radius-circle` |

**Per-corner / per-side variants** for `none`, `soft`, and `rounded`:

```
.border-radius-{top|right|bottom|left}-{none|soft|rounded}
.border-radius-{top-right|top-left|bottom-right|bottom-left}-{none|soft}
.border-radius-{top|right|bottom|left}-rounded
```

Examples: `.border-radius-top-soft` (rounds top-left and top-right at 4px), `.border-radius-bottom-right-none` (un-rounds the bottom-right corner of an otherwise rounded element).

### Border size

| Name | Value | Class | CSS variable |
|---|---|---|---|
| `none` | 0 | `border-size-none` | `--border-size-none` |
| `s` | 1px | `border-size-s` | `--border-size-s` |
| `m` | 2px | `border-size-m` | `--border-size-m` |
| `l` | 3px | `border-size-l` | `--border-size-l` |

## Shadows

| Name | Class | CSS variable |
|---|---|---|
| `none` | `shadow-none` | `--shadow-none` |
| `xs` | `shadow-xs` | `--shadow-xs` |
| `s` | `shadow-s` | `--shadow-s` |
| `m` | `shadow-m` | `--shadow-m` |
| `l` | `shadow-l` | `--shadow-l` |
| `xl` | `shadow-xl` | `--shadow-xl` |

Use `shadow-s` for cards, `shadow-l`/`shadow-xl` for popovers and modals.

## Buttons

### Types

```
.btn                  Secondary (default outlined)
.btn .btn-primary     Primary (filled brand color)
.btn .btn-cancel      Cancel (subtle, dismissive)
.btn .btn-success     Success (green)
.btn .btn-error       Error / destructive (red)
```

### Sizes

```
.btn .btn-small
.btn                  (default)
.btn .btn-large
```

### Shapes

Apply shape via `border-radius-*`:

```
.btn .border-radius-none
.btn .border-radius-soft       (default)
.btn .border-radius-rounded    (pill-shaped)
```

### Colors (override)

For a custom-colored button, layer color utilities on top:

```
.btn .background-yellow .text-neutral-0       (filled yellow with white text)
.btn .text-yellow                              (outlined, yellow text)
```

## CSS custom properties (on `:root`)

Override these in your Application Theme to rebrand without touching the framework.

### App settings

| Variable | Default |
|---|---|
| `--header-color` | `#ffffff` |
| `--color-background-body` | `#f3f6f8` |
| `--color-background-login` | `#ffffff` |
| `--header-size` | `56px` |
| `--header-size-content` | `48px` |
| `--side-menu-size` | `300px` |
| `--bottom-bar-size` | `56px` |
| `--footer-height` | `0px` |

### Brand colors

| Variable | Default |
|---|---|
| `--color-primary` | `#1068eb` |
| `--color-secondary` | `#303d60` |
| `--color-primary-hover` | `#295fd6` |
| `--color-primary-selected` | `rgba(20, 110, 245, 0.12)` |
| `--color-primary-lightest` | `linear-gradient(rgba(255, 255, 255, .9), rgba(255, 255, 255, .9))` |
| `--color-focus-outer` | `#FFD337` |
| `--color-focus-inner` | `var(--color-neutral-10)` |

To rebrand, just override `--color-primary` and `--color-primary-hover` in your Theme:

```css
:root {
  --color-primary: #ff6600;
  --color-primary-hover: #e55a00;
}
```

### iOS safe areas (notch support)

| Variable | Source |
|---|---|
| `--os-safe-area-top` | `env(safe-area-inset-top)` |
| `--os-safe-area-right` | `env(safe-area-inset-right)` |
| `--os-safe-area-bottom` | `env(safe-area-inset-bottom)` |
| `--os-safe-area-left` | `env(safe-area-inset-left)` |

Built into the Mobile and Phone App layouts — only relevant when building custom layouts.

### Pattern-scoped (set dynamically by patterns)

| Pattern | Variables |
|---|---|
| `Carousel` | `--{carousel.parentNode.id}-width` |
| `FloatingActions` | `--delay` |
| `MasterDetail` | `--master-detail-height`, `--left-percentage` (default `50`) |
| `Gallery` | `--grid-desktop` (4), `--grid-tablet` (2), `--grid-phone` (1), `--grid-gap` (`var(--space-base)`) |
| `Rating` | `--rating-size` (`16px`) |
| `ScrollableArea` | `--scrollable-area-width`, `--scrollable-area-height` |

These are set by the pattern at runtime; rarely something you'd override.

## Theming the app (dark mode, full rebrand, palette swap)

**The single most important rule:** put theme CSS on the **Theme's StyleSheet** (not a screen StyleSheet) and override the **existing OutSystems UI CSS variables** at `:root` (not invented variable names, not classes scoped to a wrapper).

OutSystems UI widgets read variables like `var(--color-neutral-0)` and `var(--color-background-body)` from their internal CSS — override at `:root` once and the entire app re-themes automatically.

### Canonical OS UI variables to override

| Variable | Override when |
|---|---|
| `--color-background-body` | Changing the page surface (mandatory for dark mode) |
| `--color-neutral-0` through `--color-neutral-10` | Inverting the contrast scale for dark mode |
| `--color-primary` / `-hover` / `-selected` | Brand recolor (set all three together) |
| `--color-secondary` | Secondary brand color |
| `--color-success` / `--color-warning` / `--color-error` / `--color-info` | Semantic color overrides |
| `--header-color` | Top bar color independent of page body |
| `--header-size` / `--side-menu-size` | Layout grid dimensions (rare) |
| `--color-focus-outer` / `--color-focus-inner` | Focus ring colors (must remain visible) |

### Dark mode template

```css
:root {
  /* Surfaces */
  --color-background-body: #0a0e1a;
  --header-color: #131829;
  --color-background-login: #0a0e1a;

  /* Neutrals — inverted scale */
  --color-neutral-0:  #131829;   /* surface */
  --color-neutral-1:  #1a2035;   /* subtle fill */
  --color-neutral-2:  #232944;   /* dividers */
  --color-neutral-3:  #2d3450;
  --color-neutral-4:  #3a4060;
  --color-neutral-5:  #4a5070;
  --color-neutral-6:  rgba(255, 255, 255, 0.35);
  --color-neutral-7:  rgba(255, 255, 255, 0.55);
  --color-neutral-8:  rgba(255, 255, 255, 0.75);
  --color-neutral-9:  rgba(255, 255, 255, 0.90);
  --color-neutral-10: #ffffff;

  /* Brand */
  --color-primary:          #6c5ce7;
  --color-primary-hover:    #7f70f0;
  --color-primary-selected: rgba(108, 92, 231, 0.18);

  /* Focus ring — keep visible on dark backgrounds */
  --color-focus-outer: #ffd337;
  --color-focus-inner: #131829;
}
```

### Theming anti-patterns

- ❌ **Inventing custom variable names** (`--bg-deep`, `--accent`). OS UI widgets read existing variables — custom names won't bridge.
- ❌ **Scoping theme CSS to a wrapper class** (`.banking-dark { … }`). Override `:root` directly; the cascade reaches everything.
- ❌ **Theme-wide CSS on a screen's StyleSheet** — only that one screen re-themes.
- ❌ **`!important` to override framework styles** — work with the cascade by overriding `:root` variables instead.
- ❌ **Hardcoding hex in widget Style** — breaks dark mode / theme variants. Use utility classes or variables.
- ❌ **Forgetting `--color-background-body`** when going dark — produces "floating dark cards on light page".

---

## Utility classes catalog

Apply via `Style: "\"<class names>\""` on a widget or `ExtendedClass` on a pattern.

### Display

| Class | Effect |
|---|---|
| `display-block` | `display: block` |
| `display-none` | `display: none` |
| `display-inline` | `display: inline` |
| `display-inline-block` | `display: inline-block` |
| `display-inline-flex` | `display: inline-flex` |
| `display-flex` | `display: flex` |
| `display-grid` | `display: grid` |
| `display-contents` | `display: contents` (children take parent role) |
| `hidden` / `placeholder-empty` | Hide widget |
| `hide-on-service-studio` | Hide in Service Studio editor preview only |
| `hide-scrollbar` | Suppress visible scrollbar (still scrolls) |

### Position

| Class | Effect |
|---|---|
| `sticky` | `position: sticky` |
| `fixed` | `position: fixed` |
| `position-relative` | `position: relative` |
| `position-absolute` | `position: absolute` |

### Absolute positioning helpers

For an element with `position-absolute`:

```
absolute-top      absolute-right      absolute-bottom      absolute-left
absolute-top-right        absolute-top-left
absolute-bottom-right     absolute-bottom-left
absolute-center           absolute-center-top
absolute-center-right     absolute-center-bottom
absolute-center-left
absolute-top-plus-header   (offset by --header-size)
```

### Width / Height

| Class | Effect |
|---|---|
| `full-width` | `width: 100%` |
| `full-width-vw` | `width: 100vw` |
| `half-width` | `width: 50%` |
| `half-width-vw` | `width: 50vw` |
| `full-height` | `height: 100%` |
| `full-height-vh` | `height: 100vh` |
| `full-height-minus-header` | `100vh - var(--header-size)` |
| `half-height` | `height: 50%` |
| `half-height-vh` | `height: 50vh` |
| `auto-height` | `height: auto` |
| `tablet-full-width` | Full width on tablets |
| `phone-full-width` | Full width on phones |

### Text

| Class | Effect |
|---|---|
| `text-align-left` / `-center` / `-right` | Text alignment |
| `wcag-hide-text` | Visually hide but keep accessible to screen readers |
| `white-space-nowrap` | Prevent text wrapping |
| `break-word` | Wrap long words |
| `text-ellipsis` | Truncate with ellipsis |
| `font-size-h1`–`h6` | Apply heading size only (no weight/spacing) |

### Images

| Class | Effect |
|---|---|
| `img-cover` | `object-fit: cover` |
| `img-rounded` | Soft corners |
| `img-circle` | Full circle (avatars) |
| `thumbnail` | Bordered thumbnail style |

### Flex layout

```
display-flex                  (enable flex on parent)

align-items-baseline / -center / -flex-start / -flex-end / -initial / -stretch
align-self-flex-start / -flex-end / -center / -stretch / -baseline
align-content-flex-start / -flex-end / -center / -space-between
                / -space-around / -space-evenly / -stretch / -baseline
justify-content-center / -flex-start / -flex-end
                / -space-between / -space-around / -space-evenly

flex1 / flex2 / flex3                 (flex-grow shorthand)
flex-direction-row / -row-reverse / -column / -column-reverse
flex-wrap / -wrap-reverse / -nowrap
```

### Flex placement shortcuts

For common combinations of `align-items` + `justify-content`:

```
top-left      top-center      top-right
center-left   center           center-right
bottom-left   bottom-center   bottom-right
```

### Flex gap

```
gap-{xs|s|base|m|l|xl|xxl}
row-gap-{xs|s|base|m|l|xl|xxl}
column-gap-{xs|s|base|m|l|xl|xxl}
```

Apply `gap-base` on a `display-flex` parent for consistent 16px spacing between children.

### Border radius (directional)

Already covered above under [Borders → Radius](#radius).

### Other utilities

| Class | Effect |
|---|---|
| `remove-card-gradient` | Strip default Card hover gradient |
| `no-transition` | Disable CSS transitions |
| `no-transform` | Disable CSS transforms |
| `overflow-hidden` | `overflow: hidden` |
| `overflow-horizontal` | Horizontal scroll, no vertical |
| `overflow-vertical` | Vertical scroll, no horizontal |
| `table-responsive` | Make a TableRecords scroll horizontally on small screens |
| `table-no-responsive` | Disable responsive table behavior |
| `is-horizontal` | Layout flag for some patterns (e.g. RangeSlider) |
| `list-item-no-click-effect` | Remove ListItem hover/click visual |
| `list-item-no-hover` | Remove ListItem hover state |

## Recipes

### Standard card with shadow + soft corners

```jsonc
{ "Object": "Container",
  "Style": "\"background-neutral-0 border-radius-soft shadow-s padding-base\"",
  "content": [/* … */] }
```

### KPI counter — accent on a Counter pattern

```jsonc
{ "type_": "IMobileBlockInstanceWidget", "SourceBlock": "Counter",
  "Arguments": [
    { "type_": "IArgument", "Parameter": "Counter.ExtendedClass",
      "Value": "\"background-primary text-neutral-0 shadow-s\"" }
  ],
  "PlaceholdersContent": [/* … */]
}
```

### Centered hero section

```jsonc
{ "Object": "Container",
  "Style": "\"display-flex center full-height-vh background-neutral-1\"",
  "content": [/* … */] }
```

(`center` here = `align-items-center` + `justify-content-center` shortcut.)

### Two columns with consistent gap

```jsonc
{ "Object": "Container",
  "Style": "\"display-flex gap-base align-items-center\"",
  "content": [/* left + right children, both with flex1 if equal width */] }
```

### Brand override for the whole app

```css
/* In Application Theme stylesheet */
:root {
  --color-primary: #ff6600;
  --color-primary-hover: #e55a00;
  --color-secondary: #1a1a2e;
}
```

Every `.btn-primary`, `.background-primary`, `.text-primary` updates automatically.

### Dark mode toggle

```css
.theme-dark {
  --color-background-body: #121212;
  --color-neutral-0: #1e1e1e;
  --color-neutral-10: #f5f5f5;
  /* … flip the neutral scale … */
}
```

Toggle the `theme-dark` class on `<body>` from a client action.

## Anti-patterns

- **Hardcoded hex codes in custom CSS.** Use the framework variables (`var(--color-primary)`) so theme changes propagate.
- **Inline `style="..."` on widgets.** Use the `Style` argument with class names — keeps theming consistent.
- **Custom CSS rules duplicating utilities.** Before writing `.my-card { padding: 16px; box-shadow: …; }`, check if `padding-base shadow-s` would do it.
- **Reaching for `--token-*`** in OutSystems UI. Tokens are Mobile UI. Use `--color-*`, `--space-*`, `--shadow-*`, `--border-radius-*`, etc.
- **Picking raw color families** (`text-blue`, `text-violet`) when a semantic color fits (`text-primary`, `text-info`). Semantics survive rebranding.
- **`!important` to override framework styles.** Almost always means the override is at the wrong cascade level.

## Reference

- [OutSystems UI CheatSheet](https://outsystemsui.outsystems.com/OutSystemsUIWebsite/CheatSheet) — the live source this doc tracks.
- Upstream `outsystems-ui/README.md` (not bundled) — framework overview.
- [`ui-reference.md`](ui-reference.md) — Style attribute quoting rules (`"\"btn btn-primary\""`).
- Upstream `common/css-customization.md` (not bundled) — where custom CSS belongs (Theme > Screen > Block).
- Upstream `common/accessibility.md` (not bundled) — uses `wcag-hide-text`, `--color-focus-outer/inner`.
