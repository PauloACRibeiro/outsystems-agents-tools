---
name: omi-execution-gates
description: The runtime gates that cover what build-time signals cannot see — execute an action before building on it, check the durable row rather than the badge, render a screen as a principal who can reach it, baseline roles and rendered output before a turn changes them, and never close a fix on the model's report. Ends in the failure-shapes catalog: twelve defect shapes that all validated clean, each with the probe that discriminates it. Use during any live build or fix iteration.
---

# Execution gates

<!-- upstream-pin: 0.16.0 -->

> Mentor operation cadence: see `../../shared/reference/mentor-operations-registry.md` for the canonical index.

> **Mentor MCP surface, measured live 2026-09-02 — read this before any tool
> name below.** The Mentor tools are session-based. `mentor_start`,
> `mentor_cancel`, `publish_start` and `mentor_get_event` are **no longer
> exposed by the server**. The sequence is `mentor_start_session()` ->
> `mentor_load_asset` / `mentor_create_asset` -> `mentor_prompt` ->
> `mentor_get_run(sessionId, runId)` -> `mentor_publish` -> `publish_status`
> -> `mentor_close_session`. Sections 4b and 4c below are **incident
> evidence**: they keep the old names because the names are what the incidents
> were recorded against, and renaming them would make the record claim things
> were measured that were not. §4d states which of those rules still bind and
> what now enforces them. Every gate in this file otherwise stands unchanged —
> the gates are about what a build-time signal cannot see, which no transport
> change affects.

> **Why these exist.** Every other gate in this skill — digest, enumeration,
> assertion recompute — is a **build-time** signal. Each describes whether the
> right *shapes* exist. None can observe whether the logic inside those shapes
> does its job. In the second live run an action passed all of them and could
> never create a record.
>
> Derived by execution from a live two-day build-and-grade run, 2026-08-10/11,
> in which an app was built end to end and then partly broken by a fix accepted
> on the model's report. Each gate below carries the specific observation that
> produced it.

## 1. Execution gate — per server action, before anything is built on it

**After an action's approved publish, execute it** against the verification rows
the plan declares for it, **before building any screen that calls it.**

**What this catches.** `Enrol` passed blueprint validation, coverage review
38/38, cross-blueprint check, plan agreement, enumeration with the exact
specified signature, `change_applied: true`, `internal_retry_count: 1`, and a
clean publish. It could never create an enrolment **for any course**: the create
step held an empty record literal `{}` and its outgoing connector pointed at the
`AlreadyEnrolled` assign instead of `Success`. A codegen defect, not prompt
ambiguity — all four `If` conditions were verbatim correct.

**The load-bearing point is ordering, not cleverness.** One happy-path call at
the moment the action was built would have found it, because the empty literal
breaks *every* path including the successful one. Instead it was found after
five screens had been built on a dead action. The tests existed and were
correct; they ran at the end.

**Refusal-branch coverage is enforced separately and mechanically** by
`check_outcome_coverage.py` in `outsystems-plan-to-mentor`: every non-success
result the design declares must have a verification row that reaches it. That
checker proves the tests were *written*; this gate is what makes them *run in
time*.

## 1b. Post-mutation state check — the durable row, not the badge

**When a mutating action reports success, verify the DURABLE state — a
`db_query` against the record, or a full reload — never the on-screen label.**
§1 is about executing an action before anything is built on it; this row is what
"it executed successfully" is allowed to mean afterwards. The visible label is
not the state: it is a copy of the state, made at some earlier moment, by code
that may never have read the state at all.

**What this catches, and it fails in both directions.** Both measured on
restaurant-app-v2, 2026-08-30:

- **Success reported, nothing written.** An approval returned HTTP 200 and
  changed no row. The guard had inverted, so `UpdateMenu` sat on a branch
  execution never reached; the action returned a result code anyway; and the
  screen action that called it stored that code in a local variable and never
  tested it. Three parts each behaved plausibly and the record stayed
  `Rascunho`. This is shapes 3 and 4 of §6 stacked on one path — which is why
  the durable check is the probe for both.
- **Failure reported over a state that was already correct.** Later, the same
  app reported *"menu cannot be approved"* for a menu whose row was already
  `Aprovada`. Nothing was wrong with the data. The status badge had not
  refreshed, and the screen was arguing from the badge.

One `db_query` on the record the turn claims to have changed settles both, and
costs a single call. **Re-rendering the widget is not a reload** — where the
screen holds the value in a local variable, only re-fetching proves anything,
and the second incident above is what a widget refresh looks like when it
convinces you the write failed.

**The screen you are reading is older than the probe you just ran.** On-screen
feedback messages and list counts persist across probes, so a verdict taken off
a screen that has not been reloaded is a verdict about an earlier probe.
Measured twice on restaurant-app-v2 (2026-08-31): a *"Escreva o nome do
prato."* left standing from earlier empty-name probes was read as a free-text
regression that did not exist, and a pre-refresh item count was read as
"nothing was added" over an item that had been added. Neither screen was
lying — both were answering a question asked several probes ago. **A
verification verdict is valid only from a post-reload read of ground truth**,
which for a message means reloading before believing it and for a count means
re-fetching before comparing it.

## 2. Render gate — per screen

**A screen is not verified until it has been rendered by a principal who can
reach it.** Role-gated screens are verified signed in, or they are not verified.
**Reading the deployed artifact is not a substitute.**

**What this catches.** `CourseEdit`'s date fields were verified from the
compiled JS chunk — a deliberate choice, since the screen is admin-gated and
could not be loaded anonymously. Every structural claim was true: real
`DatePicker` pattern blocks, correct bindings, `TimeFormat` present, zero
`type="date"`. On an **existing** record the fields rendered **blank and
un-typeable**, and the calendar opened on today rather than the record's own
date — so an administrator checking a date could overwrite a value never shown
to them. The defect lived in what the control did with existing data *on load*,
which no artifact read can reach.

**Where displayed values derive from a fetch, render more than once** — or
remove the timing dependence by construction, which is the better fix. A single
green observation cannot distinguish *correct* from *correct this time*: one
revision was verified by loading it in a browser and looked right, while
carrying the same race that made the next revision visibly wrong. It was lucky,
not correct.

**Sizing note.** For the app this came from, the authenticated surface was
**half the application**, and it is where the defects were. A verification pass
that stops at the anonymous surface grades the easy half.

### The tooling cannot satisfy this gate for you

`outsystems-runtime-ui-audit` **does not log in** — auth-gated runtimes are
explicitly out of its scope, and it is right to stop rather than score a login
page as if it were the app. The colleague guide says the same: the URL it audits
must work without login.

**So for a role-gated screen the audit is not a route to this gate**, and
saying "the audit passed" does not discharge it. Two consequences, both learned
the hard way:

- **A clean audit of the anonymous surface is not evidence about the gated one.**
  It is evidence about a different half of the app.
- **An unauthenticated harness is not a substitute either.** A role-gated server
  action invoked without a user context answers *"Not authorised."* — an HTTP
  200 that a sweep can easily record as a correct refusal. Measured 2026-08-12.

**What discharges the gate for a gated screen** is a human or an authenticated
browser session opening the screen **as a principal holding the role**, on an
**existing** record as well as a new one, and reporting what rendered. The
automated route is `outsystems-render-gate` (not part of the colleague sprint-loop pack): the operator
bootstraps a test principal's session once, the run derives a check spec per
screen, and the gate
emits verification rows (naming that principal, with screenshots) for exactly
this discharge — where it cannot run, record it as a manual verification row
with the principal named instead. If nobody does either, the screen is
**unverified** — write that word rather than a tier.

**Only a clean run discharges it.** A run that returns **exit 4 does not
discharge this gate**: exit 4 means `unasserted` rows — nothing failed, but
nothing checked those rows either, and a gap is not a pass. Each such row needs
the recorded **human screenshot verdict** written as a manual verification row
naming the principal, per that skill's Result semantics, before the phase
proceeds. A completed run is not by itself the evidence; its exit code is.

## 2b. Polish gate — per screen, after the render gate

> **Source:** re-expressed from `outsystems-frontend-skills`
> `ui-frameworks/outsystems-ui/polish-checklist.md` (upstream tip `c7a376e7d`,
> 2026-07-20, dormant). The upstream file is written as `execute_code` calls;
> only its criteria are adopted here. Dimension labels are
> `outsystems-runtime-ui-audit` criteria, so build time and audit time argue
> in one vocabulary.

A screen that passes the render gate renders. It does not follow that it looks
finished. OS UI's defaults are functional and vanilla, so a structurally
correct screen reads as a wireframe until an explicit pass fixes it — and the
runtime audit will score exactly that, one full converge iteration later.

Run every item per screen. A "no" is a fix, not a note.

The right-hand column is provenance, not weight: it says where this dimension
gets scored later, so build time and audit time argue in one vocabulary. It is
not a tally. Three rows carry C14 because one unpolished screen commonly fails
all three from a single root cause — nobody made a typography-and-semantics
pass — and that is ONE finding with three symptoms, not three findings. Fix the
cause; do not count the rows.

| # | Check | Scored downstream as |
|---|---|---|
| 1 | Type sizes carry a hierarchy — a heading is not body text at body weight | C14 Modern vs. Dated |
| 2 | The brand colour marks the primary action and little else; it is not spread across every surface | C1 Theme & Styling |
| 3 | Spacing utilities give sections breathing room; nothing is flush against its neighbour or the viewport edge | C8 Margin & Padding |
| 4 | Content is realistic for the domain — real names, plausible amounts, sensible dates. No `Lorem ipsum`, no `Sample_`, no `Title 1` | C13 Content & Data Quality |
| 5 | The active item in any navigation is visually distinguishable from its siblings | C14 Modern vs. Dated |
| 6 | Section headings are real headings, not styled containers | C14 Modern vs. Dated |

Default children are a separate failure with its own owner — see
`odc-mentor-hardening.md`. A block still showing "Use this placeholder to…"
fails that check, not this one.

### The builder's summary does not discharge this gate

The gate is discharged by looking at the rendered screen from the render gate,
against the six rows above. A build summary reporting a completed screen says
nothing about any of them, because none of them are structural — every item
here is true or false on a screen where every widget is the correct type.
Derive the verdict from the render, never from the summary.

### Measured computed style, not class presence

> **Mentor's summaries are reliable about what it wrote and unreliable about whether it works.**
> Adopted verbatim as this rule's motto from the v2 run's verdict (2026-08-28),
> because it is the whole of the rule: the summary is a faithful account of the
> edit and no account at all of the effect.

A UI fix is verified by **measuring the rendered result** — computed style or
geometry, read out of the browser — in the **same tab**, after a **fresh
reload**, at the **breakpoint** where the defect manifests. It is never verified
by the class being present in the markup.

Three ways that run's fixes passed a presence check and changed nothing:

- **A declaration smuggled into the class attribute.** Mentor wrote
  `class="white-space: nowrap"` on 24 widgets across 8 screens. A CSS
  declaration is not a class name, so the attribute is inert. **The sweep is
  mechanical and it is the response lint**: a `class` value containing a `:` is
  reported as `class_attribute_value` by
  `scripts/response_contract_lint.py --answer <draft-file> --mode <mode>`, which
  the Final Self-Check already runs before sending. Run it on the assembled
  prompt package in MCP delivery mode too, where there is otherwise no file —
  the same assembled file the chrome coverage gate needs. On the deployed side
  there is no separate sweep and none is needed: the measurement above catches
  it, because an inert class attribute produces no computed style.
- **A class the theme never defined.** `align-items-end` was applied across the
  build and resolves to no rule at all in this app's theme. In the markup it is
  indistinguishable from a working fix.

  The measured known-bad list for this theme, growing as runs find them:
  `badge-primary`, `align-items-end`, `cursor-pointer`. All three resolve to
  nothing; `cursor-pointer` computes to `cursor: auto`, which is the tell.
  **`cursor-pointer` carries a second failure on top of the silent one** — a
  row made to look clickable by styling alone has no handler behind it, so the
  class not resolving is the visible half of shape 1. Treat a "clickable"
  styled row as unwired until the network log says otherwise.
- **A property with no effect on its target.** `align-self` was set on a widget
  whose parent is not a flex container, where the property does not apply.

All three were reported applied, and one batch of rows was reported "already
correct" **because the class was present** — the report and the check were the
same operation, so the check could not fail.

**Run a utility-class audit once per app, at the first layout fix**, and keep the
answer **cached** for the rest of the run: take the theme classes the build
relies on, resolve each in the running app, and record which ones actually
produce a rule. It is a single pass, and without it every later layout fix
re-argues `align-items-end` from scratch. The audit answers "does this class
resolve in this app?"; the per-fix measurement above answers "did this fix
work?". Neither substitutes for the other.

## 2c. Post-screen checks — per screen, required rows

The render gate asks whether the screen renders and the polish gate asks
whether it looks finished. Neither asks **who can reach it** or **where it
writes**. Both of those were carried as initiative, and both leaked on the same
live run. They are **required rows** now: a screen phase does not complete
until each has an answer written down.

### (a) Enumerate the screen's deployed roles

**The platform grants the app's default role — on a template-scaffolded app
that role is the app's own name with punctuation stripped, measured 2026-09-03;
earlier text here said `Template_WebApp`, which is wrong — to every screen at
creation.** Screen role checks are
**OR** semantics, so a screen the prompt asked to restrict to `PlatformAdmin`
ships readable by anyone holding the default role, which is everyone. Mentor's
summary said "PlatformAdmin role only"; the deployed screen carried both.

So enumerate the roles **on the deployed screen**, per screen, and compare
against the spec. Do not read the roles off the prompt or off the builder's
summary — the leak is precisely the gap between them. This is AB-07, and
2026-08-27 is its **second live confirmation**; one recurrence is why it stops
being initiative.

**Caution — do not strip the default role everywhere.** Login and
password-recovery screens must **keep** it: they are reached by principals who
hold nothing else, and removing it locks every user out of the app's front
door. The row is "enumerate and compare", not "remove the default role".

### (b) Check for client-side database writes

Mentor generated screens that write entities **directly from client flows**,
while the ten server actions built to perform those writes sat unused. The app
worked; the boundary did not exist.

Two halves, and the prompt half is the one that prevents it:

- **Every screen prompt carries this line:** `all writes go through the named
  server actions; no entity CRUD from client flows`.
- **The post-screen check greps the turn's summary and warnings for client-side
  database-operation warnings** and treats any hit as a **fix-before-done**
  item, not a note. Mentor does warn about this — the warning was there and was
  read past.

### (c) Run the static wiring checker after the screens phase publishes — REQUIRED

**After the screens phase publishes, run the wiring checker over every screen
the phase built. Any unwired control = failed phase.** Not a note, not a
follow-up: the phase does not complete.

```
python3 scripts/check_control_wiring.py --oml <published .oml> \
    --blueprint <blueprint.json>      # or --screens A,B,C
```

**Portability boundary:** the checker is estate-internal — it converts the
`.oml` through the internal extraction CLI (`OML_EXTRACT_CLI`) and does not
ship in the colleague pack. On an install without that CLI the REQUIREMENT
stands but the mechanization does not: perform the wiring check manually —
exercise every control the phase built, signed in, expecting an observable
effect (navigation, network request, or DOM change) from each, and treat any
control with no observable effect as the same failed phase. Only the tooling
is internal; the gate is not optional.

The measured rule this row exists for:

> a screen generated from a blueprint reliably contains the right widgets and
> unreliably contains their behaviour; nothing in the pipeline distinguishes a
> wired control from an unwired one — only executing it does
>
> — restaurant-app-v2, nine controls, 2026-08-28

**What this catches.** Nine controls across nine screens rendered perfectly and
had **no handler at all** — no navigation, no network request, no console
error. Both "+ Add" buttons were among them, so the app shipped with **no
data-entry path**. Every one of the nine passed validation (0 errors), publish,
the digest gate, enumeration and role checks, and the assertion recompute. Each
was found only by a human clicking it. The recompute counts widgets; this is the
first check that asks whether any of them do anything.

**Verdict.** A Button or Link must reach a destination — a screen, or a client
action with a non-empty flow; a `Start→End` handler with no body is unwired, not
wired. The input family is judged on `bound Variable OR handler`, because every
Input in the measured revision carries an empty `OnChange` (an input commits
through its variable, not through an event) and failing on that alone would have
produced sixteen false failures on one screen.

**Region coverage, same run.** With `--blueprint` the checker also diffs the
blueprint's `main_content` regions against the built tree — two screens shipped
missing whole regions (filter tabs, empty states) and nothing noticed. Regions
whose token names no asset the model holds are reported `UNSUPPORTED` and do
**not** fail the run; the compensating control is upstream, in
`outsystems-ui-design` Step 4, where a filter region or an empty state now
**requires** per-screen `assertions`.

**Ordering is structural, like the recompute's.** Session edits are server-side;
there is no element tree to inspect before the revision lands. `--oml` needs the
internal extraction CLI (`OML_EXTRACT_CLI`) and there is no portable substitute —
the MCP `context_screens` payload carries no widget data at all.

### (c1) Seed demo data before any UI verification — REQUIRED

After the first full publish, seed through the app's own create screens with a
discriminating dataset, before this skill or any downstream skill renders,
tests, or audits a screen. This is a pointer, not a restatement — follow
`docs/sprint-loop-manual.md`'s Seed demo data step and
`docs/superpowers/workflows/outsystems-ui-delivery-chain.md` step 6 for the
procedure and the evidence this rule is measured against.

### (d) Get the published `.oml` yourself — never ask the operator to export it

Both post-publish checks above, the `.opc` snapshot and the retrospective
diff read the published model. The agent fetches it; the operator does not
open ODC Studio. The internal `odc` CLI downloads the latest published
revision in one command, run from the project folder (the one holding
`outsystems.toml`), **pinned to the revision the digest gate just read** —
`<N>` is the tip `app_revisions` / `app_info` reported after the publish,
never "latest", so a concurrent publish cannot slide a different model under
the gates:

```
odc app download --revision <N> <app-key> --quiet   # writes <app-key>.oml, prints {"revision": N, ...}
mv <app-key>.oml ../sprint-history/<slug>/rev-<N>.oml
```

`.oml` bytes never enter a project repo — `projects/sprint-history/<slug>/`
only. Its login is separate from the MCP's: on `Token expired and refresh
failed. Run odc auth login`, run `odc auth login` (browser OAuth; the
operator only clicks consent) and retry the download. Confirm the printed
`revision` equals the `<N>` you asked for before running a gate on it.

Measured twice — restaurant-app-v2 (2026-08-28) and restaurant-app-v3
(2026-09-02): the phase was reported as "gates pending, operator must
export the `.oml`" when the download was one command away. Fall back to a
manual Studio export only when `odc` is absent from the machine.

### (e) Read the new action bodies back before the turn ends — per screen-creating turn

Row (c) is post-publish and needs the internal extraction CLI. This row is the
per-turn form of the same question, costs one instruction, and runs inside the
turn that built the control.

**Every screen-creating or screen-editing turn ends by asking Mentor to read back
the body of each new or changed client and server action node by node, and to
report the value each named widget's event property now holds. A read-back that
shows an empty body, or a widget with no bound event, means the turn is not clean
regardless of `error_count`.** That is the same verdict row (c) reaches after the
publish — an unwired control is a failed phase — reached one turn earlier, so the
two cannot drift apart.

Ask for the binding as a property of the widget, never for a description of the
action. A question phrased about behaviour is answered from the action, which
exists and is usually correct, so the one field in doubt — the widget's pointer —
is the field the answer never reads (`references/odc-mentor-hardening.md` →
`## Ask What The Event Points At, Not What The Action Does`). Require an explicit
`empty`: an omitted widget is not a wired one.

The prompt-side contract that stops the empty body being built in the first place
— event, action, input arguments, observable result and a stable widget name per
interactive control — is
`references/prompt-templates/control-behaviour-contract.md`, owned by
`references/odc-visual-source-ui-discipline.md` → `## Every Interactive Control
Ships Its Behaviour`. This row is the check; that block is the instruction.

Measured on restaurant-app-v2, 2026-08-27 to 08-31: "+ Adicionar", the reorder
arrows, language promote/remove, the dispatch retry, the digital switch, the
language tabs' `OnTabChange` and a suggestion row all rendered and did nothing,
every one with `error_count: 0`, and each was found by a human clicking it. The
question that found the empty bodies fastest, every time, was asking Mentor to
read the new action's body back node by node. Shapes 1 and 2 in §6.

## 2d. Role-inventory baseline and per-turn diff

**At session start, enumerate every screen's deployed roles (`context_screens`)
and keep that as the baseline. After ANY turn that touches roles, re-enumerate
and diff against it.** §2c(a) compares one screen against the spec; this is the
session-level control that catches what a per-screen read cannot — a change
aimed at one screen removing a role from screens the turn never named.

**Never accept Mentor's prose account of prior state while a baseline exists.**
Asked about a screen that had lost its role, Mentor reported the screen *"was
already in this state before this session"*. It was not: the baseline showed
the role present, and the regression had been published by an earlier turn of
that same session. Prose about prior state is not a reading of prior state — §6's
meta-rule, in its most expensive form, because it converts a live regression
into a closed question.

**The lore that makes this a gate rather than a nicety: removing a role's last
assignment can delete the role OBJECT tenant-wide.** Not the assignment — the
role. The cascade is total and it is silent:

- **every screen holding that role loses it at once**, including screens the
  turn never mentioned and the diff is the only thing that names them;
- **the auto-generated login-time gate logic goes with it** — the `CheckXRole`
  action, its `HasRole` output, and the `If` node in the login flow that reads
  it are all deleted together;
- the turn validates clean, publishes, and reports success.

The full blast radius appeared only in an OML revision diff. No MCP read, no
turn summary, and no validation message named anything beyond the one screen
the turn was pointed at.

**So treat a "Missing roles" validation warning as a stop-and-verify signal,
not something to explain away.** It is the one signal that fires at the moment
of the deletion, and it fires while the turn is still cheap to abandon:
re-enumerate against the baseline **before** that turn's publish, not after.

## 2e. Rendered-output baseline — before any refactor of a rendering path

**A turn that refactors a rendering path requires the affected rendered output
captured BEFORE the turn and compared after.** "Pure performance cleanup" is
not an exemption from this; it is the case the gate was written from.

**What this catches.** A cleanup on restaurant-app-v2 (2026-08-30) replaced
five per-section `MaxRecords = 1` aggregates with flags computed in
`OnAfterFetch`. Structurally it was the better-looking code and it validated
clean. It silently dropped a dish from the customer-facing A4 print sheet:
`OnAfterFetch` fires **after the first paint**, so at render time every flag was
still `False`. `error_count` was 0, the screen rendered, nothing logged, and the
missing dish sat in a page that otherwise looked entirely normal. Only the
before/after comparison of the printed content found it.

**The ODC rule underneath it: in the reactive model, never derive render-time
flags in `OnAfterFetch`.** For per-section emptiness the correct pattern is
exactly the per-section `MaxRecords = 1` aggregate the cleanup removed — the
fetch *is* the flag, and it resolves before paint. A performance argument that
moves a decision from fetch time to post-paint time is not an optimisation; it
is a behaviour change wearing one.

The baseline is cheap and specific: the rendered text or DOM of the affected
region, saved before the turn fires. A screenshot pair suffices where the
content is short; where it is a document — a print sheet, an export, a
generated list — **diff the content**, because one missing row inside a
plausible-looking page is precisely what an eye skims past.

## 3. Remedy gate — per fix

**A fix is not closed on the model's report that it was applied.** Hold a remedy
to the same standard of evidence as its diagnosis: if you can say how you
measured the cause, you must be able to say how you measured the cure.
`change_applied: true` with zero retries does not answer the second question.

**What this catches.** Twice in one afternoon the diagnosis was established
empirically — measured in the DOM, reproduced across three screens — and the
remedy was accepted on the model's report. The diagnosis was right both times.
The remedy was wrong both times, and once took three live screens off the air
with `OS-CLRT-60500 [View] TypeError: Cannot read properties of undefined
(reading 'render')`.

That asymmetry is the failure mode: rigour on the cause, credulity on the cure.

### Check recovery before you need it

**`deploy_rollback` requires prior Deploy operations.** An app changed only
through `publish_start` — which publishes an AVS revision directly into the dev
environment — has none, so `deploy_list` returns zero rows and **there is
nothing to roll back to.** Structural, not transient.

Read `deploy_list` **before** treating rollback as a fallback. Where it is
empty, plan on this basis:

- The only recovery is a forward Mentor turn: a full cycle, the same risk as any
  other change, and observably slower than the change it undoes.
- **"Cancel and retry" is not a recovery plan either.** `mentor_cancel` has been
  observed stuck in `cancelling` past the documented SIGKILL window, and
  `max_turn_time` bounds the agent subprocess's event stream, not the run's
  wall clock — a run also waits, uncapped, on the per-session lock behind a
  prior same-session turn, on the per-replica turn permit, and on S3 I/O, so
  runs have sailed past their bounds without the ceiling ever failing to fire.
  Mechanism and citations: §4c.
- Two wedge signatures exist and neither is visible from `status` alone: a run
  emitting *stalled* events (identical event ids), and one emitting *no* events
  at all.

**So a published change may be irreversible within the session that made it** —
which is precisely why rendering before publishing is the primary protection
here rather than a refinement of it.

### Escalate to ODC Studio after three failed fix turns

**After three Mentor fix turns on the same defect have failed, stop.** A fourth
turn is not a fourth chance: by then the diagnosis and the remedy have both been
argued from the same source — Mentor's account of the model — and were that
account reliable, one of the three would have worked.

Record the defect in the project's `docs/defects/` with an explicit ODC Studio
inspection handoff: the symptom, the measured evidence, what each attempt
*established* rather than merely that it failed, and the specific question
somebody opening the app in ODC Studio should answer. Then continue with the
rest of the phase. The defect is parked with a route out, not dropped.

**Measured.** The v2 run's digital-switch defect consumed four attempts
(revisions 19-22) before being parked. Each of attempts 2, 3 and 4 disproved a
hypothesis, and by the third the evidence had already moved off the action's
contents and onto the widget-to-action binding — precisely the class of question
Mentor cannot answer about itself, since its summaries had asserted that binding
existed across three separate turns while the runtime showed the handler never
running.

That is the general shape, and it is why the threshold is a rule rather than a
judgement call: three failures on one defect usually mean the defect sits in
something the builder *reports on* rather than something it *builds*, and
inspection is the only instrument left. Revisions spent past that point buy
hypotheses, not fixes — and each one publishes, so each one carries the
irreversibility above.

## 3b. The digest gate is per publish, never across a session

**A `modelDigest` can return to a value it held before.** Measured on
TrainingHub: three apply-then-revert pairs — revisions **15 = 17, 18 = 20,
30 = 32** — so **32 distinct digests across 35 revisions**. A digest is a
content hash, not a unique revision id.

**The consequence for the gate.** A before/after comparison that spans a revert
reports `DIGEST: unchanged` while **two deploys actually landed**. Baseline
therefore belongs **immediately before each approved publish**, not once per
iteration — which is how the gate was originally written, and was wrong for
exactly this case.

**And the digest cannot carry the gate alone.** Revisions 3, 6 and 8 each
*minted a revision with a distinct digest after a failed deployment*: rev 3 took
seven attempts, revs 6 and 8 three each, every attempt terminal-with-error. The
digest moved every time. So:

| Signal | Answers |
|---|---|
| `modelDigest` | **the model changed** |
| terminal deploy state | **the deployment succeeded** |

Neither substitutes for the other, and a publish is only verified when both
agree.

**Match the terminal state exactly.** `env_deploy_history` reports **two**
terminal states — `Finished` and `FinishedWithError` — and a prefix or substring
test matches both. Measured on one environment page: **76 `Finished`, 24
`FinishedWithError`**; on TrainingHub, `== "Finished"` returns **30 rows** while
`startsWith("Finished")` returns **43**. A loose match **swallows 13 failed
deployments and reports them as landed.** Failures return in seconds, successes
take ~30s, so speed is a hint but not a test.

> **Provenance.** Measured 2026-08-11 by an independent verification session
> against the run's app and a second control app, after it asked whether our
> digest gate had this hazard. It did.

**Publish mechanics, recorded here because the runbook alone
demonstrably fails to carry them (each bullet carries its own provenance):**

- **`publish_start` rejects a `message` over 500 characters** — a hard
  validation error: the call never fires. Keep the drafted message under ~480
  for headroom and trim to load-bearing nouns (entity/screen/action names plus
  the one-line why) rather than restating Mentor's summary. Rediscovered the
  hard way twice on 2026-08-11; until then the limit lived only in the runbook.
  **Re-confirmed nine times in one run** (restaurant-app-v2, 2026-08-30): the
  limit is enforced tenant-side, so every over-long draft bounces the call
  before it fires and costs a whole round trip. Draft the message short; do not
  trim it after a rejection.
- **The `operation_id` a gateway `publish_start` returns is not the key the
  log tools take.** `publish_logs` and `deploy_messages` both return HTTP 404
  for it. For the per-line error trail, find the app's record in
  `env_deploy_history` and use that record's key as the `operation_key`. The
  bridge works in flight — the row is at the top of the window — but the
  history is a 100-row unpaged window (V73), so retrospectively the row may
  already be gone, and an empty result is not "never deployed".
- **Revision notes attach on publish, not on promotion.** A deployment
  operation carries no comment field of its own; the publish `message` is the
  only place a note is written, and promoting moves an existing revision, so
  the note set at publish is the one that travels to the target environment.
  When a `commit -m`-style comment is asked for on a promotion, point at the
  publish that created the revision rather than reporting it as unsupported.
  (Upstream 0.13.1, verified verbatim, rev.17 P1 re-diff 2026-08-13.)
- **A `failed` publish carrying `indeterminate: true` has no observed outcome, and re-publishing on it is the wedge.** Upstream 0.16.0 states it plainly: the server lost sight of the publish, so it may still be building and may yet succeed. Re-poll `publish_status` with the `publication_key` from the payload, or verify with `env_app`; a second `publish_start` on the same app while the first is still running is exactly what wedges it — and §3a is why that matters here specifically: a `publish_start`-only app has no `deploy_list` rows and no rollback. This is the one publish outcome that must NOT be handed to the digest gate: an unresolved publish has no landed-or-not answer to grade, so resolve it first, then gate. A `failed` without `indeterminate` is genuinely terminal — transient `OS-BEW-*` / `OS-DPL-*` are retried server-side, so a returned code means the retries were exhausted; surface the code rather than re-publishing. **Read the code's band before acting on that sentence: it is a claim about the 5xx band, and a 4xx tail calls for a different action regardless of it.** The build worker's message catalogs group codes by their five-digit tail, and a 4xx tail is a deterministic validation error raised off the model as authored — a static entity with an auto-number identifier, a server action exposed on a weak application reference, a name that is not a valid C# identifier. The catalogs establish that those are deterministic; they say nothing about what the pipeline retries, and the distinction does not matter here. The same OML fails the same way every time, so an unchanged re-publish cannot pass whether or not it was retried first: fix the model. Keep that boundary when citing this — the server-side-retry claim above is the upstream contract's, not the catalogs'. The 5xx band is the one the retry lore is about, and even there it is not uniformly transient — the same band carries deterministic business errors that no retry would clear. Bands decode once, in `odc-error-registry.md`; this bullet does not restate them.
- **`publish_start` can refuse the session outright, and the refusal is not a publish to retry.** Upstream 0.16.0: the refusal message names the reason and the fix, and the remedy is a further Mentor turn that completes the work. The `turn_error` case in §3c is the common cause — a `succeeded` run carrying it is not a finished task, so there is nothing complete for the publish to take. Retrying the publish re-asks the same incomplete session and gets the same refusal.
- **`deploy_list`: read `truncated` before treating `total` as a count.** `total` is exact only when `truncated` is `false`; when `truncated` is `true` it is a **lower bound**, because the upstream endpoint carries no total on the wire and completeness is derived from `next_page_offset`. So "N deploy operations" is "N or more", and an absent row is not proof of absence — the same failure shape as the `env_deploy_history` 100-row unpaged window above. **Paging is not the remedy: `deploy_list` takes no offset argument**, so a truncated result is narrowed by scoping `asset_key` / `env_key`, not by asking for the next page.
- **`env_apps` search is server-side, and it is literal about whitespace.** The `search` argument is sent as the upstream `nameContains` filter — case-insensitive substring, matched by the server, not re-filtered by the client. The server does NOT trim the filter, so a padded `" widget "` requires those spaces inside the app name and silently returns nothing; an empty or whitespace-only search is dropped to "no filter" rather than matching nothing. An empty result therefore means the server's matching rule answered, not that ours narrowed: check the fragment for stray whitespace, then widen it, before concluding an app is absent.

  > **Provenance.** Both bullets verified 2026-08-26 in the upstream plugin's private source repository via `gh api`, not taken from the mining brief that raised them: `src/models/deploy.rs` blob `43270191205a6f9d10a4be9f05efc3ef9cbeea3c` (the `DeployListResponse` doc comment states the lower-bound and no-offset rules verbatim) and `src/clients/publish.rs` blob `86952bcd4dcba8bd19ece8fef14a7695f9cc8008` (the `list_deployed` doc comment and the `nameContains` query construction, including the trim behaviour). Neither fact appears in the plugin's own `SKILL.md` at 0.16.0 — Codex flagged exactly that gap on AH-2026-08-26-008, which is why these carry blob SHAs rather than ticket numbers.
- **`context_*` reads lag a successful publish by ~20–90s** (external field
  measurement, two builds; worst after a phase touching several screens' role
  lists at once), and `context_search` has been observed to catch up faster
  than the paginated listings. Terminal state and digest are the immediate
  signals; content enumeration is the delayed one — see the enumeration gate's
  wait rule in SKILL.md before reading a miss as a failed phase.

> **Provenance.** The `operation_id` bridge and the `context_*` lag figures
> are field evidence from the same external ODC build work as §4 — **not
> measured by us.** The 500-character limit and the window caveat are our own.

### 3c. A `succeeded` publish can mint no revision — the tip is the arbiter

`change_applied: true`, `validation.error_count: 0`, a read-back quoting the new value, and
`publish_status` returning `state: succeeded` with `no_changes_detected: false` are **four
signals that can all be green over a write that never happened**.

**Check `turn_error` as a fifth signal — it was absent here, which is why the four above were
the whole story.** Upstream plugin 0.16.0 adds the rule that a `succeeded` run carrying
`turn_error` is NOT a finished task, and that you must follow the `hint` beside it rather than
report the task done. That is a different failure from this one: it catches a run that admits a
problem in a field agents were ignoring, whereas the no-op below admitted nothing anywhere.
Check both — `turn_error` first because it is cheap and self-declared, then the tip revision
for the silent case.

Measured 2026-08-23 (Elastic Search Sandbox, Login screen): asked twice to change one
inline-style property, Mentor reported success and quoted the new value back both times —
on the retry it claimed to have read the new value out of the model *before* writing — while
the runtime kept serving the old value and `app_revisions` showed the **tip revision never
moved**. The publish created no revision at all.

- **Asking Mentor to confirm its own edit buys nothing.** A read-back is only as trustworthy
  as the writer. Confirm in the rendered DOM or the published client bundle instead.
- **`app_revisions` is the cheap arbiter.** If the tip did not move, nothing shipped —
  regardless of `state`, and regardless of `no_changes_detected`, which reported `false`
  (i.e. "something deployed") across a no-op.
- **Find a control that shares the failure's scope.** Two margin values in the *same* inline
  style string on the *same* element did land, which is what ruled out cache, stale bundle
  and failed publish, and localised the fault to a single property.
- **Stop after two attempts** and route the change to ODC Studio rather than spending a third
  turn on a write the transport cannot perform.

### 3d. Stale-base publishes are last-writer-wins — check the tip BEFORE publishing too

§3c checks the tip *after* a publish to prove something shipped. This gate checks it
*before*, to prove the publish won't erase someone else's work.

**A Mentor session is pinned to the app state at session start, and its publish deploys
that session's full OML snapshot — a whole-app, last-writer-wins swap, not a 3-way merge.**
(Vendor-confirmed: OutSystems, Deniz Arin, Slack, 2026-08-24 — not our measurement.) The
serialization of publishes (`waiting_for_prior`) protects the *build engine* from
concurrent builds; it does nothing for *content*. If sessions A and B both branch from
revision N: A publishes N+1, then B publishes N+2 built from N — **A's changes are
silently gone**. `no_changes_detected` is a no-op check, not a merge signal, and no signal
anywhere reports the overwrite.

This bites a single long-lived session too, not just parallel agents: a session held open
across *anyone else's* publish — ODC Studio, a colleague, another agent session — erases
those revisions the moment it publishes.

The gate:

- **Record the tip revision (`app_revisions`) when the session starts.** Without the
  baseline the pre-publish check has nothing to compare against.
- **Re-check `app_revisions` immediately before `publish_start`.** Tip unchanged → publish.
  Tip advanced → **do not publish**; the session's snapshot no longer contains the newer
  revisions and will destroy them.
- **Attribute the advance before you block on it — your own failed publish is not a foreign writer.** A **`failed`** publish can still advance the tip. Measured 2026-08-27 (restaurant-app-v2): a publish that failed on delete-rule model features moved the app from revision 1 to 2 and its `modelDigest` from `20264c2a` to `fdd82d67`. Read without provenance, "tip advanced ⇒ do not publish" then blocks the session on the wreckage of its own attempt, and the fix turn that would clear it can never ship. So: **record every `publication_key` this session starts.** On a tip advance, resolve the advancing publication — `env_deploy_history` for the app, `publish_status` on the keys you hold — and compare. An advance whose publication matches one of your own is **not** a foreign writer: proceed. An **unmatched** advance still blocks, exactly as above. Provenance is the only thing this relaxes; where the evidence does not settle which publication moved the tip, treat it as unmatched and block.
- **Recovery is replay, not merge.** `fresh_context` does NOT rebase — it re-opens over
  the session's *own* OML (SKILL.md's semantics), never the latest published revision.
  The only rebase is a brand-new `app_key` session (which reads the new tip as its base)
  and replaying the prompts so Mentor regenerates against it.
- **The app is the isolation boundary.** Partition work one app/library per agent;
  a shared app forces the serialize-and-replay discipline above.

## 4. Mid-run loop triage — one `details: true` poll at 5–6 minutes

**A stuck turn is invisible to the normal polling cadence until it is too late.**
`internal_retry_count` — the field that says definitively that a turn is looping
— appears **only in the terminal `result`/`error` object. By the time a
status-only poll can see it, the turn has finished and its whole budget is
spent.**

So at the **5–6 minute mark**, do **one** `details: true` poll with a small
`events_limit` (~10–15) and read the `tool_begin`/`tool_end` payloads:

| Healthy | Looping |
|---|---|
| New Aggregates, nodes and assigns being built one after another — including across a legitimate "delete and rebuild this action" self-correction | The **same action name** with a **near-identical broken expression** recurring across consecutive `tool_begin` events |

**This is a spot-check, not a polling mode.** One poll, then straight back to
status-only. Making it habitual is exactly the token cost the polling-behaviour
discipline exists to avoid.

**A timed-out turn discards its work.** The platform's own error text says
*"Do not create a new app or discard work already applied."* **That is
aspirational, not a guarantee.** Mentor edits an in-memory OML working copy that
is checkpointed only on `status: succeeded`; a hard timeout kills the turn before
any checkpoint, so a resumed session reloads the last good state. On any
`"Agent turn timed out"` result, **ask Mentor to report what currently exists in
the model** rather than building on the assumption partial work survived.

**Turn size is the lever, not the timeout value.** Raising `max_turn_time` does
not reliably help — a scoped-down turn still hangs if it contains a single
operation Mentor can loop on. Split ambitious work into single-concern turns
sized to finish well inside 15–20 minutes, passing the session forward and
telling Mentor explicitly what already exists and not to recreate it. One shape
deserves pre-flight counting rather than triage: a single Server Action asked
to originate several grouped-Aggregate list outputs (the "get all the dashboard
data" shape) has crashed a turn outright on the same external evidence,
discarding all of its work — same remedy at a coarser grain, one small action
per list, decided before the turn is fired (see the hardening guide's
turn-shaping entry).

> **Provenance.** This section is field evidence from another team's ODC build
> work (two production-shaped builds, 2026-08-07 → 08-10).
> **It was not measured by us.** Adopted because it is a read-only diagnostic
> whose only cost is one extra poll. Our own corroboration is negative and partial: two Mentor
> sessions wedged on one objective on 2026-08-11, one repeating identical event
> ids for 15 minutes and one emitting nothing for 20, and in both cases we could
> see *that* they were stuck and nothing about *why*.

**On a large app the turn is also working from a reduced view of the model, so
name every element explicitly.** Above a length threshold, Mentor's coding agent
swaps the app summary it is given for a **simplified, shorter** version and logs
the substitution as a warning — the agent is not told it is working from a
reduced view, and neither is the caller. Verified 2026-08-26 in the
coding agent's private source repository via `gh api`, not from the mining brief
that raised it:
`outsystems.ai.agents.coding/outsystems/ai/agents/coding/model_api_agent/current_asset/summary.py`,
blob `4ca02371b1f0dfcd0eb962d7d007a75827289a29`, whose `resolve_asset_summary`
logs `"App summary length %d exceeds threshold; using simplified %d length
version."` and records `simplified` / `original_length` on the span. (The brief
described this as truncation and pointed at a root-level path; both were wrong —
the mechanism is a simplified substitute, and the paths are nested under
`outsystems.ai.agents.coding/`.) This is mechanism for a symptom this estate has been treating as flakiness —
"Mentor forgets elements on big apps". Three consequences, and they compound
with the turn-size rule above rather than restating it: batch smaller as the app
grows, because the reduction is a property of app size, not turn size; **never
refer to an element by position, by "the screen we just added", or by any
description that assumes the agent can see the whole app** — give the exact
element name every time; and do not read a Mentor summary's silence about an
element as evidence the element is absent, because the summary may simply never
have held it. The enumeration gate in SKILL.md remains the arbiter — a reduced
view makes the summary less trustworthy, not the tenant.

## 4b. Cancel calibration and token hygiene

External field evidence: an internal OutSystems project (adopted 2026-08-14); field-observed over the Mentor MCP, not in official docs.

RECONCILIATION — three existing OMI rules stay binding; this section calibrates the *voluntary* cancel decision underneath them: (1) the caller still bounds every turn explicitly — on the session surface that bound is the caller's own wall-clock ceiling on the `mentor_get_run` poll loop (SKILL.md driving contract), since the pre-2026-09 `max_turn_time` parameter has no counterpart there — and it is a *requested* ceiling, not an enforced terminal bound: §3 records runs sailing past it, so never treat the ceiling as a guarantee that the turn will terminate; (2) the §4 `details: true` poll at 5–6 minutes is diagnostic — it is never by itself a reason to cancel; (3) §3's warning that a cancel (`mentor_cancel_prompt` on the session surface) can wedge in `cancelling` stands — cancel is a last resort, not a recovery plan.

- **A slow Mentor turn is not a wedged one.** Heavy structural turns legitimately run **8–12 minutes with silent stretches** (~7 quiet minutes is normal). Healthy small turns on this estate go terminal in 1–5 minutes — both profiles are real; judge against the turn's size.
- **Give a heavy turn ~12–14 minutes before considering `mentor_cancel_prompt`** — and cancel only if you also intend to split the work smaller. A cancel that re-runs the same oversized prompt buys nothing.
- **Cancel economics:** a cancel costs >3 minutes to settle, a cancelled turn commits **nothing** (failed/cancelled turns never advance OML), and a cancel against an already-succeeded run is a **no-op you will misread as a wedge** — re-poll the `runId` before concluding anything from a cancel.
- **Hang tell:** a `nextCursor` unchanged for ~7–10 minutes is the cursor-side signature of the §4 wedge classes (stalled event ids / no events). One `details: true` poll to confirm, then apply the cancel calibration above.
- **Earlier hang tell: no `currentStep` at all — but only when it PERSISTS.** Upstream plugin 0.16.0 states plainly that `currentStep` and `message` are **optional** fields and that when neither moved you should restate `status` rather than assert progress, so a single poll without `currentStep` proves nothing and must not be read as a wedge. The cursor-side tell above needs ~7–10 minutes; the narration-side tell is readable in about two. A healthy run reports a `currentStep` (`runQuery`, `applyModelApiCode`, `message`, `complete`) within ~60s and keeps advancing it. Measured 2026-08-23 (Elastic Search Sandbox): a wedged turn returned `status: running` with the `currentStep` field **absent entirely** and `events: []` even under `details: true`, for ~15 minutes — while two sibling turns on the **same app and same session** had each reported a step inside 60s, which is the control that makes the absence diagnostic rather than merely slow. `mentor_cancel` then held in `cancelling` for >4 minutes and never reached terminal, so the >3-minute settle figure above is a floor, not a bound: do not wait for a cancel to go terminal before acting.
- **The wedge escape the resume rule does not cover: check publish state, not the error code.** SKILL.md routes a failed turn to "resume the same session", starting fresh only on `session_not_found`. A wedged run never goes terminal, so it emits **no error `code` at all** and that rule has no exit. Decide on unpublished work instead: if the session's edits are already published, a fresh `app_key` session costs nothing — it re-downloads the pristine OML and loses no state (the identical prompt then completed in ~2 minutes). Fight for the wedged session only when unpublished edits are genuinely at stake. One correlation, recorded as correlation and not cause: the wedged turn was the only one in that sequence started with `fresh_context: true`.
- **Call `auth_status` before starting a turn you expect to run past ~5 minutes — as a liveness snapshot, not as protection.** The bearer's lifetime is shorter than the work it has to cover: measured across the restaurant-app-v2 run (2026-08-26 to 09-02) it expired roughly hourly while turns routinely ran 5–20 minutes, so a turn started late in a bearer's life is a turn that expires inside itself. What the call buys is bounded and worth stating exactly: `auth_status` reports whether the bearer is alive **now** and carries no remaining-lifetime field, so it rules out starting a long turn on one that has **already** lapsed and tells you nothing about whether this one survives the next twenty minutes. It therefore cannot prevent a mid-turn expiry, and no client-side discipline can — only a longer bearer or a refresh the client can drive would. Make the call anyway: it is one call against the unpredictable cost of the next rule, and it is the only part of this that is in the client's hands.
- **After any MCP re-authorization, verify the status of in-flight runs rather than assuming they survived.** Survival is not a property of the run. Measured on two separate days (restaurant-app-v2): on 2026-08-28 a run outlived a token expiry mid-flight, kept executing server-side and finished normally, because the Mentor session token is independent and long-lived; on 2026-08-30 at 19:43 a run on the same app died mid-run when the agent's own connection 401'd — terminal `status: failed`, reason `unauthorized`, and the edit it was applying never landed. Two runs, two outcomes, so neither is the rule. Poll every `runId` you hold once the new credentials are in place and read the terminal state before resuming work on the assumption a turn is still building. The adjacent hazard is §4c's principal binding: a re-auth landing on a **different** subject does not fail the run, it makes it unreadable — `run_not_found`, which is not a state you can resume from.
- **Copy `mentor_session_token` verbatim — never retype it.** One mistyped character returns `signature_invalid`. Read the rejection's reason before choosing a recovery path: the server emits `signature_invalid`, `expired` or `malformed` as three distinct reasons under the single `mentor_session_token_rejected` code, and it re-tries the previous signing key before reporting `signature_invalid` — so that reason means transcription, or a token minted before a key rotation older than the previous-key window, and never expiry. Mechanism and citations: §4c.
- **Cancelled-run token recovery — payload token first, last-successful as fallback, established sessions only.** On a failed or cancelled run the terminal `error` payload carries the same `mentor_session_id` plus a freshly minted `mentor_session_token`; resume an established session — one that has already reached at least one successful turn — with those credentials, per the SKILL.md driving contract (verified against upstream 0.13.x; the rule is unchanged in 0.16.0). Keep your last SUCCESSFUL token as the fallback for exactly one case: that established session's freshly minted token is rejected as `signature_invalid`. That rejection has two causes — a hand-transcribed character (see the verbatim rule above) and a payload token the server will not accept — so re-check transcription before concluding the minted token is bad. **This fallback does not apply to a bare first-turn `app_key` init failure**: that error carries no token at all, and by definition no turn in this session has ever succeeded, so no last-successful token can exist to fall back to — SKILL.md routes that case to starting fresh, not to any token fallback. The external source for this section states the last-successful rule unconditionally but names no server version; this estate's version-anchored measurement takes precedence, and the unconditional form is narrowed to the established-session `signature_invalid` case only.

## 4c. What the gateway and the agent services enforce

Source-verified 2026-08-19 against the OutSystems-internal service repositories
that own this surface — the service behind the MCP `mentor_*` tools and the
conversation layer beneath it (repository names and per-fact file:line citations
are recorded in the mining disposition, not here). Everything here describes those services' own
behaviour, for which their source is authoritative — they are **not claims about
ODC or Mentor as a product**, and must not be repeated as one. Deployed figures
come from the gateway's Helm chart (`manifests/helm/values.yaml`), which is
**configuration, not code invariants**: the chart can change without a code
change, so read every number below as dated, not fixed.

**`max_turn_time` is enforced — over the agent subprocess, not the run.** A hard
`tokio::time::timeout` wraps the subprocess event loop, with a real kill behind
it: SIGTERM to the process group, SIGKILL after 5s, and a force-kill of orphaned
helpers (`clients/dotnet_cli.rs:886`, `:1002`, `:541-613`; buffered path
`:1262-1264`). What sits *outside* that timeout is everything before the event
loop starts — the per-session mutex, which a prior same-session turn holds for
its entire duration including its S3 PUT (`http/mentor_handlers.rs:895-905`),
the per-replica turn permit, the first-turn OML download, the resume-path S3
GET — plus the closing S3 PUT. So a turn queued behind another turn on the same
session accrues wall clock its ceiling never sees. **Do not run two turns on one
session**; that, not a higher ceiling, is the lever §4b already points at.

**A second, tighter bound: the inter-event idle timeout.** Each event read is
wrapped in its own timeout (`clients/dotnet_cli.rs:640-657`); on elapse the turn
fails with terminal code `idle_timeout` at HTTP 504 — the same status the
subprocess's own `timeout` returns, so route on the code, never the status
(`http/mentor_handlers.rs:191-199`). It measures **event SILENCE, not elapsed
time**; `0` disables it, and it is clamped to at most `max_turn_time`
(`config.rs:38-48`), so at the deployed 600s
(`MCP_MENTOR_IDLE_EVENT_TIMEOUT_SECS`) it always fires first. Diagnostic
consequence: a long run that never tripped it was **emitting events throughout**
— slow, not hung. OMI's own 26-minute war story is therefore a slow run, not a
silent one.

**`run_not_found` is a single envelope over four causes, and none is
recoverable.** The four (`http/mentor_handlers.rs:694`;
`http/run_registry_redis.rs:940-975`):

- a `runId` that is not a UUID (`http/mentor_handlers.rs:183`);
- the `by-run` pointer absent or **TTL-expired** (`run_registry_redis.rs:947-949`);
- the pointer's tag not matching `<tenant>|<user>|` — the same live run polled by
  a **different principal** (`:952-958`);
- the pointer resolving but the **state HASH** gone (`:965-972`).

They are deliberately indistinguishable, to defeat tenant enumeration
(`commands/mcp_schema.rs:1092-1095`), so the code tells you nothing about which
one you hit. There is **no rebuild path** from any of them: never treat
`run_not_found` as a state you can resume from.

**The run's lookup key expires on a schedule nothing refreshes.** The state
HASH, the event stream and the by-session pointer are all re-`PEXPIRE`d on every
event, so an actively-emitting run keeps them alive
(`run_registry_redis.rs:197-199`). The `by-run` pointer is not: it is set once at
`start_run` and **never refreshed** (`:420-431`), for a lifetime of
`max(1200s, max_turn_time + 300s)` (`http/mentor_run.rs:1283-1291`). A turn that
outlives that window goes invisible to `mentor_get_run` while still running.
This is why the SKILL.md rule is "pass an explicit `max_turn_time`" and not
"pass a small one" — too low a ceiling is its own failure mode.

**That formula now has a ceiling of its own, so the window cannot be bought
arbitrarily long.** Read 2026-08-31 in the same service repository: `max_turn_time`
is clamped server-side to `MCP_MENTOR_MAX_TURN_TIME_CAP_SECS` (chart default
7200s) *before* the TTL formula runs, and the `mentor_start` schema now advertises
that bound as its `maximum` alongside a `minimum` of 1, with the parameter's own
description stating that larger values are clamped. Two consequences: the
pollability window tops out around 7500s, and a caller who asks for more than the
cap gets a **shorter** window than the one they computed, with only a server-side
log to say so. Nothing this skill advises reaches the cap — the retry ceilings
named in the driving contract are 2700/3600 — so this bounds the formula, not the
advice. Chart figure, therefore dated and not a code invariant, per this section's
header.

**Sessions are bound to the principal that created them.** The session key is the
triple `(TenantId, UserId, SessionId)` (`http/mentor_session.rs:50-55`, hashtag
at `:66-68`), and the user component is taken from the authenticated principal on
every call (`http/mentor_handlers.rs:409`, used at `:448-451`). A valid
`mentor_session_id` + `mentor_session_token` pair **will not resume the session
under a different principal**. Nor does the attempt announce itself: polling
another principal's run returns the opaque `run_not_found` above, **not a
permission error**. Relevant wherever a loop changes hands — a second agent
identity, a different OAuth principal, a re-auth that lands on another subject.

**Silent conversation-state loss is a second cause of mid-session amnesia.** In
the AISA layer, restoring a connection's stored agent state is wrapped in a
warn-and-continue `except` — on failure the turn proceeds with a fresh, empty
agent — and the read helper swallows its own failures and returns `None`
(source citations: the mining disposition, §restore-path). Nothing reaches the
client: no error, no code, no notification. Contrast agent *creation* failure,
which raises `ConversationInitializationError` and does surface. So
"Mentor forgot the conversation" has **two causes, not one** — prompt drift, and
context that was silently never restored. The recovery is the same
(`fresh_context: true`), but do not spend a round rewriting a prompt that was
never the problem.

**There is no server-side retry at the AISA layer, and retryability never
reaches the client.** Every error mapping returns an `(error, retryable)` pair
and the chat service discards the flag on the way out —
`app_error, _ = self.error_mapper(exc, connection_id)`
(source citation: the mining disposition, §retryability); each error arm sends the
error and re-raises, and the file contains no retry loop at all. Retry is
entirely the caller's job. The service's own classification, read at source on
2026-08-19 (citations: the mining disposition, §error-classification):

- **Retryable** — OS-AISA-50003 initialize-conversation, OS-AISA-40005
  app-state-retrieval, OS-AISA-50004 session-persistence, OS-AISA-42902
  tenant-too-many-requests, OS-AISA-42901 too-many-requests-to-provider,
  OS-AISA-50301 llm-gateway-down, OS-AISA-50002 ai-provider, OS-AISA-50001
  unknown.
- **Not retryable** — OS-AISA-40001 conversation-context-limit, OS-AISA-40002
  agent-mode-changed, OS-AISA-40006 attachment-download, OS-AISA-42903
  daily-token-limit, OS-AISA-49901 cancelled-conversation.

The catch-all (OS-AISA-50001 unknown) is classified **retryable**, which is what
makes OMI's existing "retry the same session on an unexplained failure" posture
the right one. Because the flag is discarded, none of this is on the wire: the
list is a triage aid for a code you already have, not something to parse.

**`hint` is not a general field.** The terminal `error.hint` OMI relies on for
the max-length recovery is minted only when the upstream message carries the
literal OS-AISA-40001, and only on the Failed/`SubprocessError` arm
(`http/mentor_handlers.rs:875-884`, wired at `:1282-1286`). Cancelled terminals,
idle-timeout terminals and the bookkeeping-failure paths carry none — so do not
build a general "read the hint" rule on it.

**`fresh_context`'s strict typing is load-bearing, not pedantry.** The server
rejects `"true"` and `1` rather than coercing them
(`http/mentor_handlers.rs:221-227`) precisely because silently coercing a
mistyped flag would re-resume the maxed-out conversation straight back into the
OS-AISA-40001 the caller was escaping (`:216-220`).

**Two deployed numbers that change a decision.**

- **A finished run stays readable for 24h**, not minutes
  (`MCP_MENTOR_RUN_RETENTION_SECS`, matched to the session window on purpose,
  `values.yaml:93-95`). A late poll on a terminal run still returns its result.
  This does not soften the separate SKILL.md point that a terminal run's *event
  history* is unreachable — result and event history are different surfaces.
- **The event stream is capped at 2048 entries**
  (`MCP_MENTOR_EVENTS_STREAM_MAXLEN`), and it is the only event-retention
  surface. A verbose long turn trims its own earliest events past that cap,
  which is what produces `cursor_dropped` (`commands/mcp_schema.rs:1094-1097`) —
  recover by re-polling with `cursor` omitted, exactly as the first-poll rule
  already says.

**Why there is no caps-and-limits table here.** W1.6 produced a full one. It is
deliberately not imported: the remaining figures (sessions per tenant, session
inactivity, token TTL, per-replica turn concurrency, byte caps, event-page
limits) are Helm values that can change without a code change and that change no
decision this skill asks an agent to make — carrying them would be maintenance
debt asserted by tests. The two above are recorded because they each change one.
Where a limit already has an OMI rule — the tenant-wide session cap and its ~24h
reap, in `odc-mentor-hardening.md` — that rule is now corroborated at source and
stands unchanged.

## 4d. Pre-2026-09 Mentor contract fields — what replaced each rule

Four fields the driving contract in `SKILL.md` relied on through upstream
0.16.0 have **no counterpart** on the session-based surface (schemas read and
behaviour measured live 2026-09-02). None of the rules they served was dropped;
each is restated here in terms the current surface can express, with the old
evidence pinned so a later reader can tell a migrated rule from an invented one.

| Field (pre-2026-09) | What it was for | Status | What enforces the rule now |
|---|---|---|---|
| `max_turn_time` | Server-side turn ceiling, so a wedged turn had a terminal state to reach. L20, first live colleague run 2026-08-09: the one unbounded session sat on the same internal step for 26 minutes, then returned `run_not_found` — no status, no code, nothing to resume. | **Unverified gap.** `mentor_prompt` accepts only `sessionId`, `message`, `attachmentRefs`. Nothing server-side bounds a turn. | Client-side budget. Decide the turn's budget before sending, watch elapsed wall-clock against the size bands (§4, and healthy 1–5 min / heavy 8–12 min), and call `mentor_cancel_prompt(sessionId, runId)` at the budget. Turn size stays the lever: split the work rather than wait longer. |
| `internal_retry_count` | Friction flag: `>= 3` fired the `submit_feedback` `agent_observation` categorical `builder_retry_friction`, and served as a prompt/platform mismatch detector. | **Unverified gap.** The terminal payload exposes no counter. | Nothing reports friction directly. Terminal *time* was always the health signal and still is. The stuck signature is the event stream: no new events across two consecutive drained polls spanning ~7–10 minutes with `status` still `working`. `builder_retry_friction` is **suspended** — it has no observable field to fire from. Never synthesise a count from event text. |
| `fresh_context: true` | Resume-only flag that started a new conversation over the session's *already-edited* OML — recovering from `OS-AISA-40001` max conversation length, from hallucinated elements, or a task switch — while keeping the session's unpublished edits. | **Unverified gap.** No flag on any session tool does this. | Publish first, then reset. The only reset available is `mentor_close_session` -> `mentor_start_session` -> `mentor_load_asset`, which reloads the *published* asset, so unpublished edits are lost unless published first. The publish keeps its own approval and §3d still binds. If the work is not publishable yet, stop and say so — the loss the flag existed to avoid is now paid every time. |
| `no_changes_detected`, `indeterminate`, `state` (gateway `publish_start` payload) | `no_changes_detected` claimed a publish landed nothing; `indeterminate: true` was the server admitting it never observed the outcome, and the rule was: never re-publish on it. | **Unverified gap.** `publish_status` on a `mentor_publish` key returns `{key, applicationKey, applicationRevision, outcome, status}` and nothing else — measured `outcome: "in_progress"` / `status: "Running"`, then `"success"` / `"Finished"`. (`publish_status`'s own description still documents all three; that half describes the gateway path, which is gone.) | The never-re-publish rule **broadens** rather than weakens: since the server no longer labels which outcomes were unobserved, treat *every* ambiguous publish that way — on any non-`success` outcome, any error, or any lost response, re-poll `publish_status` with the same `publicationKey` or verify with `env_app`, and never publish again. The no-change question falls entirely to the digest gate (§3b), which is the stronger signal anyway: `no_changes_detected` was only ever a self-report with recorded false negatives. |

Two further session-surface facts the gates depend on, both measured 2026-09-02:

- **`app_info` still serves `modelDigest`**, so §3b's digest gate and §3d's
  stale-base gate are intact for any app reached with `mentor_load_asset`.
- **An asset created by `mentor_create_asset` does not exist to `app_info`
  until its first publish** — the call returned HTTP 404 for a created-but-
  unpublished asset. That first publish therefore has no pre-publish baseline
  and no stale-base question to ask. Grade it by the `revision` `mentor_publish`
  returns plus the enumeration gate, and report `DIGEST: not applicable (first
  publish of a session-created asset)` rather than implying a pass. Every later
  publish, and every `mentor_load_asset` flow, is gated normally.

Also renamed, not lost: the terminal result object is camelCase
(`result.changeApplied`, `result.validation.errorCount`), `currentStep` is gone,
and `result.attemptedChange` is new — `attemptedChange: false` on a turn that was
meant to build something is a failed step, not a no-op to accept. The served
poll-interval key is `pollIntervalMs` (was `pollAfterMs`), and the cursor is a
re-read control, so every `mentor_get_run` poll is bare.

### The honest-completion flags and the readback channel swapped roles

Measured 2026-09-03 on a live session (`docs/adoption/mentor-session-surface-live-probe.md`,
Q3) and recorded here because it inverts a rule this file has relied on since the old
backend.

**`changeApplied` behaved as an honest same-turn signal, on one session.** A genuine edit
turn returned `attemptedChange: true` / `changeApplied: true` and the edit matched; a
read-only question turn returned both `false`. On the pre-2026-09 backend these flags fired
on read-only turns inconsistently across days, which is why the standing rule was
"completion flags are not write signals; verify by readback".

**The sample is two turns in one session, and that is not enough to retire the old rule.**
Codex required this qualification on review of `AH-2026-09-03-002`, and it is right: two
turns behaving correctly is consistent with an honest flag and is also consistent with the
old backend's inconsistency, which took *days* of runs to surface. So `changeApplied` is
**provisionally** honest — treat a `false` on a turn meant to build as a failed step, and
treat a `true` as a reason to look for the change, never as proof it is there. Replication
across more sessions is owed before this is a rule rather than an observation.

**The `context_*` readback is now the lagging half.** Immediately after
`changeApplied: true`, `context_entities` did not show the new entity — and still did not
show it immediately after a **successful publish**. It caught up 3–5 minutes later.
Context Service is eventually consistent on the order of minutes, and `app_list`'s search
index lagged similarly for a newly published asset (`app_info` by direct key did not).

**What changes is the reading of a stale readback, not the requirement to confirm.** The
narrow, well-supported rule: **a `context_*` read that disagrees within a few minutes of
the edit is a stale read, not a Mentor no-op.** That much follows directly from the
measured lag, and it is the protection worth having, because applied the old way the rule
manufactures a false negative — wait for the readback, see nothing, conclude the turn did
nothing, and re-prompt an edit that already landed.

**Confirmation stays mandatory; only its timing moves.** Do not treat `changeApplied: true`
as discharging the readback. Where a specific change must be confirmed inside the session,
use the Mentor conversation's own text response; where `context_*` or `app_refs` is the
only channel, **wait and re-check** — a delayed confirmation, not a skipped one. Treating
the first empty read as evidence is the error; treating the flag as the evidence is the
opposite error, and both are still errors. No upper bound on the lag was established, so
"wait and re-check" has no fixed figure yet either.

Two adjacent findings from the same probe, both narrower than they look. The event stream
did **not** carry the assistant's final answer text on the read-only turn, though it did on
the write turn — so `mentor_get_run` events are not a dependable place to read an answer
from. And the schema's "a second prompt while one is running is silently ignored" was
exercised once with an ambiguous outcome (the second call returned its own `runId` with
zero events, but the first run had already gone terminal), so it stays **unconfirmed**.

### The cursor reversal — the server's own `mentor_get_run` description, quoted

Our polling rule reversed on 2026-09-02: every `mentor_get_run` poll is bare,
where the pre-2026-09 rule threaded the previous response's `nextCursor`. That
reversal contradicts `outsystems-mentor-polling-behavior` (not part of the colleague sprint-loop pack), whose Tier 3 section says "Always pass `nextCursor` from the previous response." The authority for the change is the
**server's own tool description**, read from the live MCP tool schema on
2026-09-02 and quoted here verbatim so a later reader — or a reviewer with no
live MCP surface — can check the claim against its source rather than against
our restatement of it:

> Read buffered progress events and current status for a Mentor Web run started
> via mentor_prompt. The run must belong to the supplied session. Status is one
> of working / succeeded / failed / cancelled / not_found. Reading a run on a
> session that has been closed fails with a session-closed error. Keep polling
> until status is terminal AND nextCursor is null. **Each poll without a cursor
> returns only events not yet delivered; pass an explicit cursor (the previous
> nextCursor, or 0 for the start) to re-read already-delivered events, e.g.
> after a rejected response.** When hasMore is true there are more events to
> page through. Oversized events arrive as truncation markers
> (_truncated/_eventId); fetch the full body with mentor_get_event.

(Emphasis added; the rest is the description as served.) The `cursor` parameter
carries the same rule in its own text: *"Omit to receive only events not yet
delivered (recommended). Pass the nextCursor from a previous poll to re-read
from that position, or 0 to re-read from the start."* — the server itself marks
omitting the cursor as the recommended behaviour.

Two caveats this quote also settles. The description still names
`mentor_get_event` for oversized-event bodies, but that tool is **not exposed**
by the server (tool list read the same day), so a `_truncated` marker currently
has no documented way to be resolved — `Unverified gap`. And "keep polling until
status is terminal AND nextCursor is null" matches what was measured: the
terminal poll carried no `nextCursor` key at all.

## 5. Summary admissions — the confession is in the fine print, never the headline

**A turn summary's follow-up notes and caveats are required reading, not
optional colour — especially for anything RBAC-shaped.** Mentor has been
observed to self-report a real spec gap in its own summary — a role's data
scoping passing an empty region list — while the same turn reported
**zero validation errors** and a complete-sounding feature list. A skim that
stops at "zero errors" misses exactly this kind of admission.

This is "the friendly surface lies toward success" (V76) read from the other
side. The summary is **untrustworthy for success claims** — the enumeration
gate exists because one described five parts of an action that was never
created — and **load-bearing for failure admissions.** Its admissions are
findings: anything the summary flags as a scoping gap, a manual step, or a
"needs a follow-up turn" note is either fixed before the phase closes or
carried explicitly as an open item — never silently rolled forward into the
build report as if resolved.

> **Provenance.** The self-reported RBAC gap is field evidence from the same
> external ODC build work as §4 — **not measured by us.** Our own runs supply
> the success-direction half (2026-08-09 enumeration incident, V76).

### 5b. Derive the checklist from the spec, never from the builder's summary

§5 governs how to *read* a summary. This is the separate rule about where the
verification checklist **comes from**: when scoring or verifying a build, derive
the checklist by reading the spec, plan, or blueprint files directly. The
builder's own summary of what it built **must not** set the checklist — a
builder summarizing its own work is precisely the bias a fresh verification pass
exists to remove, and a checklist derived from it can only ever confirm what the
builder already believes it did. Anything the spec required but the summary never
mentions is exactly the item this ordering is designed to catch.

Corollary for verdicts: where some criteria were checked and others could not be
driven at all, the result is PARTIAL, never rounded up to PASS. "Unverifiable"
and "verified" are different findings.

> **Provenance.** External field evidence from an internal OutSystems project
> @ 3524310 (adopted 2026-08-14, round 2); field-observed in that project's own
> verification agent, not in official docs, and **not measured by us.**

### 5c. Post-run triage — order the questions, and stop at hypothesis

§4 is the mid-run spot-check and §5 is how to read a summary. This is the
after-the-fact question: the turn is terminal, the result is wrong, slow, or
looping, and you have to say why. **Answer these in order.** The ordering is the
whole point — each one changes what the next one means, and the usual failure is
jumping to a mechanism from the first error string you see.

1. **Did anything change?** Read the model back — `context_*`, the app's tip
   revision, or an OML diff. Do this *before* opening the run's evidence, so the
   run's own account of itself cannot frame the question. `change_applied` and
   the turn summary are claims about the model; the model is the model.
2. **Did it change the right things, and only those?** §5b's rule holds: derive
   the checklist from the spec, never from the summary. Unrelated mutations are a
   finding in their own right, not noise around the real one.
3. **What was the FIRST error, not the last?** A turn that retried the same
   operation five times has one cause and four echoes. Cluster the near-identical
   attempts (§4's tell — the same target with a near-identical broken
   expression), then report the earliest failure and let the retry count be a
   magnitude, not the finding. A retry count is never itself a diagnosis; §4b
   already says why `internal_retry_count` is not auditable after the fact.
4. **Is the error text the real error?** Very often it is not. A generic
   transport-level message can sit on top of a specific host exception you cannot
   see from here, and a validation rejection may not have been reported as a
   failure at all — the hardening guide's host-execution-model entry has the
   mechanics. Practical effect: a vague error message narrows almost nothing, and
   a *missing* error is not evidence that nothing failed.
5. **If something is missing, do not say "rolled back."** Reach for that only
   with an explicit rollback or undo marker in the evidence. Absence is not a
   marker. The hardening guide lists the three candidates and why they have
   opposite fixes.
6. **Was it slow, or was it stuck?** Different findings, per §4b — heavy
   structural turns legitimately run 8–12 minutes with silent stretches. Judge
   against the turn's size before calling anything a wedge.
7. **Could it have been asked to do the impossible?** A prompt that asks for
   something the target cannot express produces retry friction that looks like a
   platform fault. Check the instruction against the capability matrix before
   filing a product bug.

**Then stop at the right confidence.** An error string is not a mechanism. The
evidence available from this surface shows you *what* happened; it rarely proves
*why*, because the layer where the cause lives is not readable from here. A cause
you have not observed is a **hypothesis — label it one, out loud, in the report.**
Reproducing an outcome is not the same as knowing its cause, and a green re-run
proves less than it appears to: if the failing path is one that never classified
as a failure to begin with, a passing re-run says nothing about whether that path
fired. This is the same discipline §5 applies to summaries, pointed at your own
conclusions.

> **Provenance.** Adapted 2026-08-26 from another team's Mentor session-diagnosis
> practice, and **re-based**: their checklist reads host-side traces and per-call
> ledgers that this surface cannot reach, so every step above was rewritten
> against evidence a run here actually yields. The ordering discipline and the
> stop-at-hypothesis rule are theirs; **not measured by us.** Steps 3 and 6 are
> corroborated by our own §4/§4b measurements. Claims table and provenance detail
> are in the mining disposition under `docs/adoption/`.

### 5d. Record the WARNING count per turn, and treat an unexpected jump as a finding

**Write down the validation WARNING count for every Mentor turn, and diff it
against the previous turn's.** Errors get read because zero is the gate;
warnings get skimmed because they never block. But the count is a structured
field, and by the meta-rule in §6 that makes it fact — the only per-turn number
that moves when a turn does something it was not asked to do.

Measured on restaurant-app-v2, 2026-08-31: a turn whose whole job was to
**remove** a shared aggregate took the count from **61 to 71**. Errors stayed at
zero and the turn published. A removal that adds ten warnings has done
something besides removing.

The rule is narrow: an unexpected delta means **enumerate the new warnings
before publishing** — not that warnings must reach zero, and not that a stable
count clears the turn. A count that holds steady is one signal agreeing with
the others; a count that jumps on a turn with no reason to grow is a cheap read
that has already told you where to look.

## 6. The failure-shapes catalog — twelve shapes, none of which validation could see

A single day of UI review on restaurant-app-v2 (2026-08-30) produced ten
distinct defect shapes; the typeahead work on the same app the next day
(2026-08-31, revisions 47→49) added two more. **Every one passed Mentor
validation with `error_count: 0`**, and most also passed publish, the digest
gate and enumeration. So the useful column is the third one: these shapes are
not distinguishable from one another by any build-time signal — only by the
probe that discriminates them. Reach for the probe, not for another screenshot.

| # | Shape | The probe that discriminates it |
|---|---|---|
| 1 | Handler empty or missing — the control renders, nothing sits behind it | Network log while the control is activated: no request, no navigation, no console error. §2c(c) mechanizes this |
| 2 | Handler exists, but the control's event is not bound to it | Network log, then a Mentor read-back of the **binding**, not the action. Asking about the action returns the action — it exists; ask what the widget's event points at |
| 3 | Logic on an unreachable branch — the guard is inverted | Durable-state check after the reported success (§1b): the action returns, the row is unchanged |
| 4 | A result code nothing reads, behind a catch-all message covering every outcome | Read the **screen action that stores the result**: the variable is assigned and never tested |
| 5 | A style class that does not exist in the theme — a silent no-op | **Computed style** in the running app, never a screenshot: the element looks deliberate either way (§2b caches this answer per run) |
| 6 | Logic that runs at the wrong moment — `OnAfterFetch`, i.e. after first paint | Rendered-content baseline compared before and after (§2e) |
| 7 | A widget built into a block no screen instantiates — `LayoutTopMenu` while the screens use `LayoutSideMenu`, or a placeholder default the consuming screen replaces | **DOM presence** of the widget on the running screen; its presence in the model proves only that it was built |
| 8 | Off-by-one inside a well-formed expression — zero-based `Index()` tested with `> 0` | Vary the input's **position**: prefix, mid-string, and no-match. A mid-string match passes and hides it |
| 9 | Two computations of the same business fact disagreeing — a stored status flag against a live count | Compare both paths **on the same record** |
| 10 | An expression entered as a literal string — the caption renders the raw `If(...)` | Look at the rendered text |
| 11 | Live logic behind a UI-unsatisfiable condition — a complete, correct branch guarded by a condition no user action can make true | For every guarded branch in a new or changed action, **name the UI element that makes the condition true**. No such element, no way to fire it: the branch is dead-but-live, and the aggregate feeding it is fetching for nobody |
| 12 | `.Current` read in a handler bound to something other than the row's own event — a Container's Click inside a list is not the List Item's On Click | Click the row and read what the handler received: **some values set and others cleared**, then the follow-on write does nothing. Pass the row's values as input arguments on the widget's event rather than re-deriving them from the aggregate |

**The meta-rule the day proved: structured fields are fact; prose is
hypothesis.** Mentor's structured fields — `error_count`, the validation
messages, `publish_status` — and the runtime probes — network log, computed
style, DOM, `db_query` — were right **every time**. Mentor's prose was wrong
three times in the same day: it reported a change applied that had not
persisted, it described a turn as clean while the validation block beside it
carried two errors, and it described a prior state it had never read (§2d).

That is not a reason to stop reading summaries — §5 is why you must, since
their admissions are load-bearing. It is a rule about what a summary can
settle: read the fields, and treat the narrative around them as a hypothesis
that costs one probe to check.

**Shapes 11 and 12 are one fallacy at two levels, and the day that produced
them produced both.** Restaurant-app-v2's MenuComposer typeahead, 2026-08-31,
revisions 47→49. Five section "Adicionar" buttons each carried a complete and
correct library-suggestion branch, every branch guarded on
`GetDishSuggestions.List.Current` against **one shared five-record screen
aggregate** — a condition no user action could make true, because no picker
existed and typing drove nothing. Validation saw healthy logic. The `.opc`
rendered a fully implemented feature. Only clicking through the UI showed the
branch could never fire. The corrective turn then wired the suggestion row's
**Container** Click — not the List Item's own On Click — and read name and
price from `GetDishSuggestionsSopa.List.Current` inside that handler. The click
set some values, cleared others, and the add that followed did nothing at all.

Two rules come out of that pairing. First, **delete an aggregate that ends up
with no consumer** rather than leaving it fetching for nobody — dead-but-live
code is exactly what made shape 11 invisible, since every part of it was real.
Second, **pass the row's values as input arguments on the widget's event
instead of re-deriving them from the aggregate inside the handler.** That is
the platform's own pattern for acting on a clicked row: ODC's *Navigate to a
Detail Screen* has the List Item's On Click take the current item's identifier
as an input argument rather than have the target look it up. An argument the
event supplies does not depend on where the cursor sits when the handler runs;
`.Current` inside the handler does.

**Scope this one honestly.** `.Current` is not invalid in a handler — it is
legitimate where the event is bound in the row's own context, and OutSystems
guidance covers that use. What was measured here is the other case: a
Container's Click, which is not the List Item's On Click, reading `.Current`
and getting values that were not the clicked row's. The mechanism behind that
was not measured, so the rule is stated as the binding case it was observed in
and the explicit-argument pattern as the robust alternative — not as a claim
about when expressions evaluate. The prompt-side form is
`references/odc-mentor-hardening.md` →
`` ## Pass The Clicked Row As Arguments, Not As `.Current` ``.
