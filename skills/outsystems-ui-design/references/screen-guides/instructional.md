# Instructional / Onboarding / Launcher Screen

> **Origin:** written for this skill (Phase 3, GAP-9), not harvested. The upstream
> screen-guide set has no archetype for a screen that *explains* rather than *operates*,
> and 2 of 9 screens in a real app hit that hole — each forced to load a guide describing a
> different kind of screen and then discard most of it.

## When this is the archetype

The screen's job is to **orient, explain, or route** — not to display a record, edit one,
or list a collection. If the user cannot *do* anything on the screen except read it and
click through to somewhere else, this is the guide.

Typical instances:

- **Getting-started / setup**: numbered steps taking a new user from nothing to working.
- **Launcher / home / index**: grouped links into the rest of the app.
- **Reference card**: "here are the three ways to do X", usually tabbed.
- **Empty-app first-run**: what to do before there is any data.

**It is none of these:** `dashboard` (no metrics — see below), `detail-view` (no record),
`list-table` (no collection), `wizard` (see below), `settings` (nothing is configured here).

## ⛔ Two archetypes it gets mistaken for, and why both are wrong

**Not `dashboard`.** A landing screen is casually called a dashboard, and `dashboard.md`
will then push a KPI row, charts, and a summary list onto a screen with **no numeric data
at all**. There is nothing to count and nothing to plot. If the screen has metrics, it is a
dashboard; if it has *links and prose*, it is this.

**Not `wizard`.** "Three steps to get started" sounds like a wizard, but OutSystems'
`Wizard` block is a **step indicator for a gated flow** — one step active, the rest of the
content hidden behind Next/Previous, driven by a `CurrentStep` variable. An instructions
page **gates nothing**: every step is visible at once and there is no Next button. Using
`Wizard` tells the user the screen behaves in a way it does not. Only reach for `Wizard`
when content is genuinely hidden until the previous step completes.

## Anatomy

**A menu, not a checklist.** Take only what the design shows.

1. **Page header**: `AdvancedHtml Tag="h1"` in the layout's `Title` placeholder, plus a
   one-line `AdvancedHtml Tag="p"` subtitle.
2. **Orientation notice** (optional): a single `Alert` with `AlertType = Info` telling the
   user how to use the screen. Real screen copy, second person.
3. **Ordered steps** (if the screen is a checklist): sibling `TimelineItem` blocks stacked
   vertically — step number in `Left`, heading in `Title`, prose + affordances in `Content`.
   There is no `Timeline` parent block; siblings are the pattern.
4. **Grouped links** (if the screen is a launcher): a `Columns*` row of `Card`s, each with a
   heading, a one-line description, and a stack of `Link` widgets. When the cards share one
   shape, make them a **web block with `Title` / `Description` / `Links` placeholders** —
   the callers supply the content.
5. **Reference content** (optional): `Tabs` for "N ways to do X", with `AdvancedHtml
   Tag="pre"` for any read-only code or config the user must copy.

## Links, not Buttons — the rule this archetype gets wrong most often

Almost everything on an instructional screen **navigates**; almost nothing **acts**. So it
is a `Link`, not a `Button` — even when the design draws it as a button (give it `btn`
styling).

A `Button` that navigates renders as `<button>`: wrong keyboard semantics, announced wrongly
by screen readers, and it **breaks middle-click and open-in-new-tab** — which matters most
here, because external links ("Open the docs", "Create an account") are common on exactly
this kind of screen.

## Data Patterns

**Usually none.** An instructional screen typically fetches nothing and submits nothing.

- `entities` is very often an **empty array**, and that is the correct answer. Do not invent
  a producer to fill it.
- Read-only reference values (setting names, code shapes, endpoints) render as
  `AdvancedHtml Tag="pre"` — **not** as `Input` widgets. The user copies them elsewhere;
  the screen must not carry their values.
- If a launcher's link groups genuinely come from data, name the producer — but a fixed,
  known set of links is static content and needs none.

## Styling

- Calm and readable, not dense. Generous vertical rhythm — this screen is read, not scanned
  for values.
- One clear primary affordance per step or card ("Go to Indexes →"), and few of them.
- No decorative imagery unless the design has it.

## Responsive Behavior

- Desktop: launcher cards 2–3 across; steps full-width.
- Tablet: cards 2 across.
- Phone: single column throughout; step content stacks under its number.
