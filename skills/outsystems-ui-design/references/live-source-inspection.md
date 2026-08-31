# Reading a live mockup page

> Origin: written for this skill, 2026-08-27, from the measured behaviour of the
> 2026-08-27 restaurant-app-v2 design run, whose design source was a hosted
> mockup SPA rather than a screenshot. Nothing here is harvested from
> OutSystems documentation — it is browser-automation method, not platform fact.
>
> Extended 2026-08-30 from the same app's mockup-fidelity pass: the type-by-eye
> trap and the per-role token pull.

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

**Type is the trap, not colour.** A colour read by eye is approximately right; a
typeface read by eye is a *classification*, and classification is what the eye
gets wrong. Measured 2026-08-30 on the restaurant-app-v2 mockup: the operator
asserted twice from screenshots that an A4 heading was "serif, with a rule
beneath it", and `getComputedStyle` returned Geist — sans-serif, 28px, weight
700. The rule beneath was real, which is the shape of this failure: the eye reads
*layout* well and *type* badly, so a confident wrong reading survives a second
look and very nearly reached a restyle prompt. Never classify a family, a size, a
weight, a letter-spacing or a colour off an image — measure the whole row, per
role. **Measurement outranks assertion, including the operator's**: where a
stated reading and a measured row disagree the row wins, and the disagreement is
said out loud in that round rather than quietly absorbed.

```js
const doc = document.querySelector('iframe')?.contentDocument ?? document;
// Type is read off THIS run's screen, not the whole page: on a multi-screen
// mockup a page-wide query returns another screen's heading. Set this to the
// selector the run recorded in wireframe.md; null reads the whole document.
const SCREEN_SELECTOR = null;
const root = (SCREEN_SELECTOR && doc.querySelector(SCREEN_SELECTOR)) || doc.body;
const cs = el => el && getComputedStyle(el);
const pick = sel => cs(doc.querySelector(sel)) || {};
// Type is ENUMERATED, never guessed from a tag: a mockup routinely reserves h1
// for the app title while the screen's display heading is an h2 or a styled div,
// and document order is not role order. Group every text-bearing element by its
// computed style, largest first, then name the roles from what came back.
const styles = new Map();
for (const el of root.querySelectorAll('*')) {
  if (/^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|TITLE)$/.test(el.tagName)) continue;
  const text = [...el.childNodes].filter(n => n.nodeType === 3)
                 .map(n => n.textContent.trim()).join(' ').trim();
  if (!text) continue;                    // own text only, so wrappers drop out
  const s = getComputedStyle(el);
  const key = [s.fontFamily, s.fontSize, s.fontWeight, s.letterSpacing,
               s.textTransform, s.color, s.borderBottom].join(' | ');
  if (!styles.has(key)) styles.set(key, {px: parseFloat(s.fontSize), style: key,
      tag: el.tagName, cls: el.className, sample: text.slice(0, 40), count: 0});
  styles.get(key).count++;
}
JSON.stringify({
  brand:      pick('button, .btn, [class*="primary"]').backgroundColor,
  radius:     pick('button, .card, [class*="card"]').borderRadius,
  bodyBg:     pick('body').backgroundColor,
  inputBg:    pick('input, textarea, select').backgroundColor,
  inputBorder:pick('input, textarea, select').borderColor,
  elevation:  pick('.card, [class*="card"], [class*="shadow"]').boxShadow,
  type: [...styles.values()].sort((a, b) => b.px - a.px),
}, null, 2);
```

**Name the roles from the output, not from the tags.** The list comes back
largest-first with a text sample per style, so the display heading is whichever
row the screen actually renders biggest — not whichever element happens to be an
`h1`. Measured against a reconstruction of the v2 mockup, this returns the
incident's own two rows: `Geist | 28px | 700 | … | 2px solid rgb(212,53,28)` —
the "serif" heading, with the rule beneath it carried in `border-bottom` — and
`Inter | 11px | 600 | 0.66px | uppercase | rgb(155,163,175)` for the section
label. A tag-guessing selector list missed both: `h1` returned the 14px app
title, and widening it to `h1, h2` still did, because the app title comes first
in document order.

Two things the enumeration buys that a selector list cannot. A role can never
come back silently empty — there is no selector to miss, so a table that looks
full is full. And a style used once is visibly separated from one used forty
times by its `count`, which is how a one-off accent is told apart from a real
role.

What to capture, at minimum:

| Token | Read from | Lands in |
|---|---|---|
| Brand / accent colour | the primary action control's `background-color` | `design_system.colors`, and `primary_color` |
| Corner radius | a card or button's `border-radius` | `design_system.visual_rules` |
| Type, **per role** — display heading, section label, body copy, numeric/price | every distinct style the screen renders: `font-family`, `font-size`, `font-weight`, `letter-spacing`, `text-transform`, `color` and any `border-bottom` rule. Enumerated, then named; a page-level font stack is not a substitute | `design_system.typography`, one entry per role |
| Surface + input background | `body` and an `input`'s `background-color` | `design_system.colors` |
| Elevation | a card's `box-shadow` | `design_system.visual_rules` |
| Spacing rhythm | repeated `padding` / `gap` values on the main containers | `design_system.spacing` |

Two honesty rules:

- **Record the raw values in `wireframe.md`** — the numbers as read, with the
  selector each came from. Those rows together are the **measured token table**
  that SKILL.md requires before any prescription is written; every value in the
  blueprint, and every value in a restyle prompt, cites one of them. A token in
  `design_system` with no recorded source is indistinguishable from one this run
  invented.
- **Translate, do not import.** These are the source's values; the blueprint
  still expresses them as OutSystems UI theming decisions. Raw CSS never becomes
  a region's block mapping, and a styled `div` in the mockup is still mapped to a
  named block like any other region.

## What this file is not

It is not licence to treat the live page as authority on **scope**. What the
mockup contains is a visual fact; what the product should contain is the PRD's
decision. See the scope-vs-visual conflict protocol in SKILL.md Step 1.
