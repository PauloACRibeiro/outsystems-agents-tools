# Reading a live mockup page

> Origin: written for this skill, 2026-08-27, from the measured behaviour of the
> 2026-08-27 restaurant-app-v2 design run, whose design source was a hosted
> mockup SPA rather than a screenshot. Nothing here is harvested from
> OutSystems documentation — it is browser-automation method, not platform fact.

Load this when the design source of a run is a **live URL or a local HTML file**
(the Live-URL / HTML source mode in SKILL.md Step 1). It covers two things: how
to drive such a page without misreading it, and how to pull its design tokens.

## The SPA traps

A hosted mockup is usually a single-page app, and often renders inside an
iframe with a DOM written entirely by JavaScript after load. Two consequences,
both measured:

- **Page-text and accessibility-tree reads come back empty or near-empty.** The
  content is not in the top-level document; it is in the iframe, and it may not
  exist at all until the framework has hydrated. An empty read is the symptom of
  a shell page, not of an empty design — do not conclude the mockup is blank.
- **Screenshot pixel coordinates misclick.** Iframe offsets, device-pixel
  scaling, and post-render layout shifts all move the target between the capture
  and the click. Clicks land on a neighbour, or on nothing.

## Drive it by text, never by coordinates

Query the element by its visible text in JavaScript and call `.click()` on it.
This is stable across iframe nesting, scroll position and pixel scaling, and it
fails loudly (no match) instead of silently hitting the wrong element.

```js
// Find a control by its visible text anywhere in the rendered DOM, then
// activate it. Works the same whether the SPA rendered it top-level or inside
// an iframe document.
const doc = document.querySelector('iframe')?.contentDocument ?? document;
const hit = [...doc.querySelectorAll('button, a, [role="button"], [role="tab"]')]
  .find(el => el.textContent.trim().toLowerCase().includes('reservations'));
hit ? (hit.click(), 'clicked: ' + hit.textContent.trim()) : 'NO MATCH';
```

Rules that follow from this:

- **Never by coordinates.** No pixel clicking, no drag-by-offset, on a live
  mockup — screenshots stay a reading aid, not a control surface.
- **Assert the match before acting.** A `NO MATCH` result is information: the
  screen or state is not on this page. That is the wireframe-absent path in
  SKILL.md Step 1, not a reason to retry blind.
- **Wait for content, not for time.** Re-query until the expected text appears
  rather than assuming a fixed delay was enough.
- Same rule for reading: pull the anatomy out of the DOM (`textContent`,
  tag/role, child counts) rather than transcribing a screenshot by eye.

## Pull the design tokens from computed style

This is the highest-value thing a live source offers over a screenshot: the real
values, not a colour-picked approximation. Read them off representative rendered
elements with `getComputedStyle`, then seed the blueprint's `design_system` from
what came back.

```js
const doc = document.querySelector('iframe')?.contentDocument ?? document;
const cs = el => el && getComputedStyle(el);
const pick = sel => cs(doc.querySelector(sel)) || {};
JSON.stringify({
  brand:      pick('button, .btn, [class*="primary"]').backgroundColor,
  radius:     pick('button, .card, [class*="card"]').borderRadius,
  fontStack:  pick('body').fontFamily,
  bodyBg:     pick('body').backgroundColor,
  inputBg:    pick('input, textarea, select').backgroundColor,
  inputBorder:pick('input, textarea, select').borderColor,
  elevation:  pick('.card, [class*="card"], [class*="shadow"]').boxShadow,
}, null, 2);
```

What to capture, at minimum:

| Token | Read from | Lands in |
|---|---|---|
| Brand / accent colour | the primary action control's `background-color` | `design_system.colors`, and `primary_color` |
| Corner radius | a card or button's `border-radius` | `design_system.visual_rules` |
| Font stack | `body`'s `font-family` (plus heading sizes if they differ) | `design_system.typography` |
| Surface + input background | `body` and an `input`'s `background-color` | `design_system.colors` |
| Elevation | a card's `box-shadow` | `design_system.visual_rules` |
| Spacing rhythm | repeated `padding` / `gap` values on the main containers | `design_system.spacing` |

Two honesty rules:

- **Record the raw values in `wireframe.md`** — the numbers as read, with the
  selector each came from. A token in `design_system` with no recorded source is
  indistinguishable from one this run invented.
- **Translate, do not import.** These are the source's values; the blueprint
  still expresses them as OutSystems UI theming decisions. Raw CSS never becomes
  a region's block mapping, and a styled `div` in the mockup is still mapped to a
  named block like any other region.

## What this file is not

It is not licence to treat the live page as authority on **scope**. What the
mockup contains is a visual fact; what the product should contain is the PRD's
decision. See the scope-vs-visual conflict protocol in SKILL.md Step 1.
