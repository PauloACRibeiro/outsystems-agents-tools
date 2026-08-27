---
name: outsystems-screen-inventory
description: Use when an OutSystems app needs more than one screen and nobody has decided yet which screens those are — turns a requirements doc/PRD (or an existing app's screen list) into one validated screen-inventory.json holding the screen list with per-screen purpose, archetype and behaviour, entity/action bindings by name, the single shared chrome decision, and cross-screen navigation. This is the shared artifact every per-screen outsystems-ui-design run reads from. Route to outsystems-ui-design instead once the screens are known and a wireframe is in hand; route to superpowers:writing-plans for the capability plan, which reads its entity names out of this inventory.
compatibility: Agent-neutral (Codex and Claude Code). Python 3.7+ stdlib only. No MCP server and no tenant access required.
allowed-tools: AskUserQuestion, Bash, Read, Write, Edit
---

# OutSystems Screen Inventory — from requirements to the screen list

**Status: DRAFT.** Read the Provenance section before relying on this: the
method is harvested from one real 23-screen fusion and the Phase 1 chain
trial's friction log, and it has **never been run on a live multi-screen
build**.

Decide, once and in one file, *which screens exist* — then let N per-screen
design runs share that decision instead of each inventing it. The emitted
`screen-inventory.json` is the artifact the chain's step 1 has always produced
by hand, and it is the single place both downstream routes read their shared
names from.

This skill is **fully local**. It has no OutSystems MCP tools and performs no
tenant operation of any kind — no app read, no Mentor session, no publish. It
produces one JSON file, one validation report, and chat. Same boundary
`outsystems-ui-design` states, for the same reason: everything here is a
decision, and decisions are files until step 5.

## Where it sits in the chain

```
1. brainstorming / PRD
        ▼
1b. outsystems-screen-inventory      ← THIS SKILL, once per app
        │  output: design/screen-inventory.json
        │  (screen list · behaviour · bindings · ONE chrome decision · navigation)
        ▼
2. superpowers:writing-plans          ← reads entity/action names from the inventory
        ▼
3. outsystems-ui-design               ← ONE RUN PER SCREEN, all sharing this inventory
```

The chain's ordering rule is that *a multi-screen app is N design runs sharing
one screen inventory and one chrome decision made up front*
(`docs/superpowers/workflows/outsystems-ui-delivery-chain.md`). This skill
produces exactly that shared artifact and nothing else.

## Scope guards (hard limits, not preferences)

- **Screens and navigation only.** No wireframes, no region mapping, no block
  choices, no visual design. The moment you are choosing between two
  OutSystems blocks you have left this skill — that is `outsystems-ui-design`,
  one run per screen, starting from a wireframe the human brings.
- **No logic or data design** beyond naming the entities and actions each
  screen binds to, and recording their behavioural contracts. Do not design
  server actions, aggregates, or business rules.
- **One inventory per app**, not per feature. A later feature adds candidates
  and screens to the existing inventory; it does not start a second one.
  **Bounded exception — a new AREA on an existing app** (greenfield trial
  finding G-02, Codex-accepted AH-2026-08-08-012): when the new surface is a
  distinct area with its own audience and entry conditions (an admin area on
  an operator app), an **area-scoped inventory** is sanctioned. It makes the
  area's own chrome decision — extending the existing app's menu is not
  expressible here and is not the goal — and its blueprints chrome-validate
  as **their own batch**: running the cross-blueprint pass across areas fails
  by design, because two areas are two chrome decisions. This is an exception
  for existing apps only; the default one-inventory-per-app rule is unchanged,
  and a feature inside an existing area still extends that area's inventory.
- **No tenant mutation and no tenant reads.** Where an existing app's facts are
  needed, they come from an offline scaffold inventory or as-built snapshot the
  operator already has.
- **Fewer than 3 screens: skip this skill.** Go straight to `outsystems-ui-design`
  and record the chrome decision in the first blueprint. The inventory earns
  its cost on 6+ screens.

## Hard gates

Every gate below stops for a human. What is worth raising there — or anywhere
in this skill — is decided by one criterion, stated once in
`references/ask-or-settle.md` and restated nowhere else: decompose, run the
convergence test, then require every leg of its conjunction. Read it before you
ask, and settle what it says to settle.

1. **Candidates before screens.** Enumerate every screen-worthy thing the
   source names *before* deciding what the screens are. Deciding the screen
   list first and back-filling candidates reproduces the source's structure,
   which is exactly the failure rule R1 exists to prevent.
2. **Nothing is silently dropped.** Every candidate resolves to at least one
   screen, is explicitly **dissolved** into something that is not a screen with
   a stated destination, or is explicitly **excluded from this build** with a
   stated reason — `deferred` (a later build takes it), `out-of-scope` (it
   belongs to another product) or `accepted-risk` (a known gap nobody owns).
   The validator enforces the accounting. Dissolved and excluded make opposite
   claims and a candidate may hold only one: `dissolved` says the capability
   still lives somewhere in this build, the excluded three say nobody builds
   it. Those three words are `outsystems-plan-to-mentor`'s, borrowed verbatim
   so an excluded candidate keeps its meaning downstream — do not coin a
   fourth here.
3. **One chrome decision for the whole app**, made here and carried into every
   blueprint: `layout_block` (exactly one of the five ODC layouts —
   `LayoutSideMenu`, `LayoutTopMenu`, `LayoutBlank`, `LayoutBase`,
   `LayoutBaseSection`) and `app_title` copy verbatim; the menu entries carry over
   **in order** but change shape - the inventory records `{label, target}`,
   a blueprint records `{label, active}`, and the validator's
   `blueprint_menu_for_screen` performs that translation per screen (`target`
   never enters a blueprint; it becomes the screen's `active` flag). Never let
   a design run decide chrome for itself.

   **When a requirement localizes the UI copy: translate `label`, keep
   `target`.** The two fields are not two spellings of one thing. `label` is
   what a user reads, so a PRD written in Portuguese gets Portuguese labels.
   `target` is the screen identity — the same name `screens[].name` carries,
   the one the capability plan's traceability and every blueprint resolve
   against — so it stays in whatever language the screen names are in, and
   translating it turns every menu entry into a dead link and every downstream
   join into a miss. `validate_blueprint --inventory` compares labels exactly,
   so the translation has to happen here, once, rather than screen by screen at
   design time.

   **On a greenfield `Web` target the decision is adopt-or-replace, not
   invent.** A template-backed app arrives with a default chrome already in it
   — `LayoutTopMenu` and a `Menu` block, in every app measured so far — so
   state which of the two this inventory is doing, having read the target
   rather than assumed it. Adopting is the default; replacing is the answer
   that needs a reason, because a replacement is rebuild cost on chrome that
   already works.
4. **Behaviour, not names** (trial F-11). Every screen states what it *does*
   and its key interactions; every binding states its behavioural contract.
   A validator error, not a style note.
5. **Human confirmation before emitting.** Present the candidate list, the
   proposed fusion, and the chrome decision, and get explicit approval. In the
   real case the human **split one fusion back apart** at this gate, moving the
   answer from 8 screens to 9 — the gate is where the least-confident fusion
   gets caught.

   **Autonomous-run disclosure** (greenfield trial finding G-03,
   Codex-accepted AH-2026-08-08-012): when this gate cannot run — an
   unattended session with no human available — the skill does NOT skip it,
   it defers it. Mark the inventory and everything derived from it
   **PROPOSED, NOT APPROVED**, and name the **least-confident fusion**
   explicitly (the one this gate exists to catch) so the deferred review
   knows where to look. This is disclosure, not an approval bypass: gate 5
   remains a real human gate, and a PROPOSED inventory does not proceed to
   build steps until someone runs it.

   **Record the deferral in `open_decisions[]`, not in chat.** The disclosure
   above used to live only in prose, and the artifact carried none of it: a
   later reader got a validated inventory with no trace that a decision had
   been deferred. `open_decisions[]` is the typed slot that carries it —
   each entry is the decision, a **category**, and **2–4 options, every one
   naming the consequence** it would have on this inventory (the screen that
   appears or disappears, the menu entry gained or lost). The validator
   enforces that shape, and an open entry makes the report say
   **PROPOSED, NOT APPROVED** and rides every affected screen's `--brief`,
   so a design run cannot settle the question without knowing it is one.

   An open decision does **not** fail validation — deferring is legitimate,
   and an error here would only teach authors to delete the entry.

## Workflow — four steps, all local

### Step 1 — Harvest candidates

Read the source (PRD, requirements doc, brief; or an existing app's screen list
from an offline scaffold inventory). List every screen-worthy thing it names,
each with the place in the source it came from. Do not filter yet, and do not
group yet.

**On a requirements document, "the place it came from" means the requirement
ID**, not a section number: `source_ref: "BR-SC-002 - the room list section"`,
the ID first and free prose as an optional trailing note. Use the grammar
`outsystems-plan-to-mentor` owns (`BR-`/`UC-`/`C-`, optionally with a scope
infix), because the same IDs are what the capability plan's Traceability table
joins on. Recording the binding here is what stops it being invented a second
time downstream, from memory, with nothing checking the two agree. On an
**existing-app modernization** there is no ID grammar to cite and the validator
does not ask for one — candidates trace to the app's own screens.

Some requirements produce no screen at all — a hashing rule, a retention
policy, a scheduled job. Those are not candidates; put them in
`non_screen_requirements` with the reason. That slot exists so the absorption
check below can tell a deliberate decision from an oversight, which silence
cannot.

**Acceptance criteria belong there too, and in bulk.** A `C-` row states how a
screen is *verified*, not that a screen exists — so it produces no candidate and
the absorption check has nowhere else to put it. This is the normal shape of the
slot on a PRD that numbers its criteria, not a sign the artifact went wrong:
sixteen `C-` rows on a nine-screen inventory is one decision made sixteen times,
not sixteen oversights. Give every one the same one-line reason —
`acceptance criterion - verified against <screen>, produces no screen` — so the
block reads as that one decision, and name the screen so a criterion filed
against a screen nobody built is still visible.

Split off what is not a candidate at all: template filler on an existing app
(eight of 31 screens in the real case were stock freebies — redesigning them
would have been pure cost), and, on a PRD, anything that is plainly an
affordance rather than a destination.

**A greenfield `Web` target is not a blank app either.** An ODC Web app created
from the standard template arrives carrying the `Common` authentication screens
— `Login`, `ChangePassword`, `RecoverPasswordRequest`, `RecoverPasswordReset`,
`UserProfile`, `InvalidPermissions` — which the ODC documentation names as
pre-built and editable. Template-backed apps are also observed carrying the
`Layouts` blocks, a `Menu` block and one app-named role, though that part is
expectation rather than established template contents; the evidence and its
limits are in
`outsystems-mentor-implementation/references/odc-app-shell-first-scaffold.md`. A PRD asking for sign-in, password
recovery or a profile page is asking to **override or extend** one of those, not
to build a new one. Keep such a row only when this build genuinely changes the
screen — a custom login look, extra profile fields — and say which in its
`purpose`; otherwise dispose of the candidate as `dissolved` into the template
screen. A build-new row for a screen the template already ships is work the app
pays for twice. Nothing checks this for you — the inventory does not record
what kind of shell it is targeting, so the judgement is yours at gate 5.

**An app the ODC App Generator produced has entity-derived screens, and that is
a property of the generator, not of the requirements.** Reading such an app as a
modernization source, expect its screens to come in per-entity triads — a list,
a record view, an edit form — plus dashboards; that is the shape the generator
emits. Our own observation, checkable against any generated app in a tenant:
**no screen in App Generator output corresponds to our `wizard`, `settings`,
`instructional`, `kanban`, `timeline`, `calendar` or `inbox-notifications`
archetypes**, because nothing in the generator derives a screen from anything
but an entity. So on this source the
absence of those screens is **not** evidence the app's users never needed them —
it is evidence of what the generator can produce. Treat a missing multi-step
flow, configuration page or guided first-run as an open question to put to the
user at gate 5, not as a settled scope boundary you inherited. (The contrast
cuts the other way too: an entity with no screen at all in a generated app is
unusual and worth asking about.)

State the count and ask the user to confirm nothing is missing before
continuing.

### Step 2 — Ground each candidate in data

For each candidate, name the entities and actions it reads or writes, from what
the source states — and record their **behavioural contracts**: caps, limits,
states, async semantics (rule R6). A capability the source never grounds in
data is a candidate to interrogate with the user, not a screen to draw.

Load `references/method.md` (rules R1–R9) before Step 3; it is short and it is
the whole judgement content of this skill.

### Step 3 — Fuse, and put it to the user

Cluster by what the user is trying to do, never by the source's own naming or
section structure (R1, R2). For each proposed screen state: name, purpose,
archetype (one of the 14 `outsystems-ui-design` archetypes — the inventory's
archetype **is** that skill's Step 1 answer, so it must come from that
vocabulary), what it does, its key interactions, and which candidates it
absorbs. State each dissolution and where the capability went instead, and each
exclusion — a candidate this build is deliberately **not** implementing — with
which of the three it is and why. An exclusion is a decision to put to the user
at gate 5 like any other, not a quiet omission: it is the only disposition
where nothing downstream will ever surface the capability again.

Then decide the chrome once and lay out the navigation: menu entries in order,
and the cross-screen edges with what triggers each. Where an edge hands
something to the target screen, name the payload and add it to that screen's
`accepts` (R7).

**Present all of it and stop for approval** (hard gate 5). Name your
least-confident fusion explicitly and say why — that is the one most likely to
come back.

**What may be left open, and how.** A question you would put to the user and
cannot — or one the user declines to settle now — goes into `open_decisions[]`
rather than into a guess or a chat line. The taxonomy is exactly this skill's
scope, one category per thing this artifact decides:

| Category | The question it holds |
|---|---|
| `candidate-disposition` | Is this candidate a screen at all, or does it dissolve — and into what? (hard gate 2) |
| `screen-fusion` | Are these one screen or two? (hard gate 5's least-confident fusion) |
| `chrome` | The one layout / app title / menu decision (hard gate 3) |
| `navigation` | Does this edge exist, and what does it carry? (R7) |
| `binding` | Which entity or action does this screen bind to, by name? (R6, R8) |

Anything outside that list is not this skill's to defer: a block choice or a
visual question belongs to `outsystems-ui-design`, an attribute shape or a
server action to the capability plan. Recording it here creates a second
declaration site neither of them reads.

Each entry needs **2–4 options**, and each option must name **its
consequence** — what this inventory would say if that option were taken, not
just what the option is called. One option is a position, five is a survey, and
a label with no consequence is the prose the slot replaces; the validator
rejects all three. Set `affects` to the screens a decision bears on; omit it
when the decision is app-wide, and it will reach every screen's brief. When the
decision is later taken, set `status: "resolved"` and `resolution` to the
option's id — the record of what was chosen outlives the question.

### Step 4 — Emit and validate

Write `design/screen-inventory.json` (the parent of the per-screen
`design/<screen-slug>/` directories `outsystems-ui-design` creates; an operator
who names a different output directory gets that one verbatim).

#### The field contract

`schemas/screen-inventory.schema.json` is the contract. Read it before
emitting; the table below is an index into it, not a substitute — it lists only
the **required** keys, while the schema carries the optional ones, the enums,
and the per-field descriptions. Nothing loads the schema at run time, so the
validator is what actually fails a run; a drift test in this skill's source repo
pins the two to each other, and also fails if this table stops naming a key the
schema requires.

| Where | Required keys |
|---|---|
| top level | `schema_version` (the string `"1"`), `app_name`, `source`, `app_chrome`, `candidates`, `screens`, `navigation` |
| `source` | `kind`, `refs` |
| `app_chrome` | `layout_block`, `app_title` |
| each `app_chrome` `menu` entry | `label`, `target` |
| each `candidates` entry | `id`, `source_ref`, `disposition`, `rationale` |
| each `non_screen_requirements` entry | `id`, `reason` |
| each `screens` entry | `name`, `purpose`, `archetype`, `behavior`, `key_interactions`, `data_bindings` |
| each `data_bindings` entry | `name`, `kind`, `usage` |
| each `open_decisions` entry | `id`, `about`, `category`, `options`, `status` |
| each `options` entry | `id`, `label`, `consequence` |
| each `navigation` entry | `from`, `to`, `trigger` |

Two field names that appear in this file are **not** keys of this artifact and
must never be written into the inventory: `main_content` and the per-screen
`active` flag belong to the blueprint's shape downstream, and `--brief` derives
`active` for a design run (see "Contracts borrowed from downstream").

Then validate:

```bash
python3 scripts/validate_screen_inventory.py design/screen-inventory.json
```

Exit 0 valid, 1 contract errors, 2 unreadable. The report is written beside the
inventory as `screen-inventory-validation.txt`. **Do not hand a failing
inventory downstream** — a design run that reads a broken inventory produces
blueprints that disagree with each other, and the cross-blueprint chrome pass
will only tell you so N runs later.

**Grading the run as a handoff.** While you are still deciding, some findings
are advice. Once a design run depends on them they are defects. Add `--handoff`
at the moment you hand the inventory over:

```bash
python3 scripts/validate_screen_inventory.py design/screen-inventory.json --handoff
```

The graduating warnings — here, a data binding with no `behavior_notes` — then
print under `HANDOFF BLOCKED:` and exit 1 instead of advising. The finding text
is identical; only the channel and the exit code change. A warning graduates
only if you can always clear it by editing the inventory, so there is no waiver
and none is needed; a warning that can be a legitimate final state (an inventory
that genuinely is one screen per candidate) stays advisory under the flag.
**Without `--handoff` the report is byte-for-byte what it was before the flag
existed** — nothing changes for a run that does not ask.

**Placeholder markers are rejected.** `TODO`, `TBD`, `FIXME`, `PLACEHOLDER`, a
bracketed `<fill in>`, or a value that is nothing but `...` is a contract error
in any gate-bearing field — the app name, chrome, candidate ids and rationales,
screen names, purposes, behaviour, interactions, bindings and navigation. An
inventory whose screen purpose is `TODO` satisfies every shape rule and every
design run downstream reads it as the purpose, so this fails closed rather than
warning. `source.grounding_notes` is deliberately exempt: record what is still
open there, never in the field itself.

When the source is a requirements document, pass it and check the whole thing
was absorbed:

```bash
python3 scripts/validate_screen_inventory.py design/screen-inventory.json --source docs/prd.md
```

Every requirement ID the document defines must be either cited by a candidate's
`source_ref` or listed in `non_screen_requirements` with a reason. A `PROVENANCE:
n/n` line reports the split on the passing path, so a run that skipped the check
is distinguishable from one that passed it. Both dangling directions are errors
too — a `source_ref` citing an ID the document never defines proves nothing, and
an ID that is both cited and dispositioned is a contradiction.

If the document defines **no** requirement IDs, the check declines with a note
rather than failing every candidate: the fix is to give the source a Requirement
Inventory (`outsystems-plan-to-mentor/references/requirement-id-conventions.md`),
not to work around the validator. Note the asymmetry — that degradation needs the
ID-less document shown. Omitting `--source` leaves the per-candidate rule an
error, so it is not a way to switch the gate off.

To hand one screen to a design run, print its kickoff facts:

```bash
python3 scripts/validate_screen_inventory.py design/screen-inventory.json --brief "Migration Console"
```

That prints the archetype, purpose, behaviour, interactions, **the requirement
IDs this screen realizes**, bindings, the
chrome in the blueprint's own shape (layout and title verbatim, the menu
already translated to `{label, active}` for this screen), the declared
assertions, and the screen's navigation edges **in both directions** —
outgoing, and incoming with each edge's trigger and payload, the receiving
half of the `accepts` contract (greenfield trial G-05: without it the design
run walked back to the full inventory to learn who sends what it receives).

It also leads with any **open decision** affecting that screen — app-wide ones
reach every brief — because the brief is the only thing a design run reads. A
design run that meets one must take it back to the inventory, not settle it in
a blueprint.

**The requirements line** is the provenance from Step 1 arriving where it is
used. It carries the IDs of every candidate that resolves to this screen, then
each candidate's `source_ref` verbatim so the design run reads the author's own
note about what the requirement asked for. Recording provenance and stopping at
the inventory would leave the capability plan's Traceability table the only
place the requirement-to-screen binding appears — the duplication this skill's
`source_ref` rule exists to end.

Two cases print a reason rather than a bare "none recorded", because an empty
list with no explanation reads as a defect in the inventory:

- **A modernization source** has no requirement-ID grammar at all; the line says
  so and names why.
- **A dissolved candidate** that cites requirement IDs gets its own line on
  every brief, marked as bound to no screen. `dissolved_into` is free text
  ("the Rooms filter bar"), not a screen reference, so nothing can join it — but
  `--source` absorption counts that ID as accounted for, which makes the brief
  the single place the requirement could go missing between the source document
  and the build. Reporting it on every brief and asking is the honest handling;
  guessing a screen from the prose is not.

Two more kickoff facts ride the brief, both G-05 findings:

- **Entities born in this inventory** (bindings marked
  `introduced_here: true`) get an explicit delegation line: their names are
  authoritative here (R8), but their attribute shapes are **the capability
  plan's to type** — a design run must not invent typed attributes for them.
  In the trial the design run invented them because no other author existed;
  that is exactly the unilateral naming R8 exists to prevent.
- **A design-tokens pointer**: `design_tokens_source` verbatim when the
  inventory records one (an approved sibling blueprint, an as-built theme);
  otherwise derived from `source.kind` — modernization points at the as-built
  theme of the app being redesigned, and a requirements-doc inventory states
  there is **no source yet**, so the first design run knowingly establishes
  the design system instead of silently mining for one.

And when the inventory excludes anything, the brief ends with the
**excluded-scope block**: every excluded candidate with its disposition word,
source reference and rationale, under an explicit *do NOT design or implement*
heading. The list is app-wide rather than per-screen on purpose — what nothing
in this build implements must not be drawn on this screen either — and it is
printed only when there is something to print. Carry the same IDs and words
onward as `outsystems-plan-to-mentor`'s `Excluded scope:` field, so the
exclusion reaches that skill's `## Requirement Dispositions` table and Section 8
of the Mentor spec instead of stopping here.

**The brief is no longer the only thing holding this boundary.** Pass the same
inventory back to the design run's validator as
`validate_blueprint.py --inventory design/screen-inventory.json`, and the
blueprint it produced is checked against what the brief told it: screen name,
chrome, and any declared assertions are errors there; entity bindings are a
warning.

## What the validator checks

Errors (exit 1) — every one traceable to the method or the trial:

| Check | Why |
|---|---|
| Every candidate has a disposition; mapped ones resolve to real screens; dissolved ones say where the capability went; excluded ones (`deferred`, `out-of-scope`, `accepted-risk`) carry neither `resolves_to` nor `dissolved_into` | R4 — nothing silently dropped, and a candidate cannot be both excluded from the build and rehomed inside it |
| Every screen absorbs at least one candidate | a screen that traces back to nothing was invented, not derived |
| On a requirements-doc source, every candidate's `source_ref` cites a requirement ID | the requirement-to-screen binding is recorded once, here, instead of being invented again in the plan's Traceability table. Not asked of a modernization source, which has no ID grammar |
| With `--source`: every ID the document defines is cited by a candidate or dispositioned in `non_screen_requirements` with a reason; no ID is cited that the document does not define; no ID is both | silence is the third state between "it became a screen" and "it deliberately did not" |
| `behavior` and `key_interactions` present on every screen | R6 / trial F-11 — names alone are not a contract |
| `archetype` is one of the 14 `outsystems-ui-design` archetypes | the inventory's archetype is that skill's Step 1 answer |
| Where `presentation_pattern` is declared: it is one of the five ODC presentation blocks | the field is optional, but a declared one names a block a design run will build; see below |
| `layout_block` is exactly one of the five ODC layouts; `app_title` present; menu-bearing layouts have a menu and `LayoutBlank` has none | hard gate 3, and OUD gate 1's vocabulary |
| Every menu target names a real screen | a menu entry pointing nowhere ships as a dead link |
| Navigation endpoints are real screens; a payload edge finds its payload in the target's `accepts` | R7 / trial F-12 |
| Every screen is reachable — in the menu or the target of an edge | a screen nothing leads to is built and never seen |
| `assertions` keys are only `links`, `buttons`, `inputs`, non-negative integers | shared vocabulary; see below |
| `introduced_here` is boolean and marks entities only; `design_tokens_source` is non-empty text | G-05 — the brief's delegation line and design-tokens pointer key on them; a new action's name is born in the plan, never here (R8's greenfield asymmetry) |
| Every `open_decisions[]` entry has 2–4 options, each with a non-empty `consequence`, and a category from the five above | hard gate 5 — a deferred decision has to be a choice someone can take, not a note that one exists |
| A resolved decision names one of its own options in `resolution`; an open one carries none; `affects` names real screens | otherwise the record says a decision was taken without saying which way |
| Duplicate screen names, candidate ids, menu labels, decision ids, or option ids/labels within a decision | ambiguity downstream; two spellings of one choice leaves a decision with fewer real options than it claims |
| Where `access_classification` is declared: it is one of the five values, an `unresolved` screen is refused, a `role` screen names its `access_role`, and no other classification carries one. An `access_role` with **no** classification is refused too | see below — the field is optional, but a declared one is held to its rules, and a lone role name asserts a gate nothing declared |

Warnings (do not block): a binding with no `behavior_notes` (F-11's exact
shape), and an inventory where **every** screen absorbs exactly one candidate —
which means the source's structure was restated rather than an architecture
decided (R1).

**The template-screen check is deliberately not one of them.** It shipped
briefly as an advisory warning keyed on the screen name and was removed the
same day (Codex review, AH-2026-08-26-015, 2026-08-26): an inventory records no
target-shell fact — `source.kind` splits greenfield from modernization, not Web
from Mobile from an intentionally blank shell — so the warning fired on targets
where the template screens do not exist and the row was correct. Gating it
needs a fact this artifact does not decide, and coining one for a single
warning would fork a contract. It stays guidance in Step 1 until a target-shell
fact exists here for its own reasons.

## Who each screen is for — `access_classification`

Optional, and worth declaring on any app where some screens are gated and
others are not. It records access as **intent**, so a later run reconciles the
built app against a decision instead of re-deriving one from the model — which
is what turns a later render check from probe-and-report into
reconcile-against-declaration. Four rules travel with the field:

1. **The writer default is never the policy.** Whatever a generator does when
   nobody said — usually the most open thing — is a fact about the writer, not
   a decision. A screen nobody decided is `unresolved`, not `public`.
2. **`unresolved` blocks the screen from being built.** It is an error, not a
   warning: stop and ask. This is the one place the inventory refuses to hand
   a screen downstream, because guessing access is the failure that produced
   the RoomBooking anonymous-access dispute.
3. **A `role` screen's role must exist before the screen is created** — a
   precondition, not a post-check. Name it in `access_role` so it can be
   checked at all. **The validator does not and cannot check it**: this
   artifact is authored offline against a requirements doc, with no tenant to
   ask. All it enforces is that a `role` screen names a role; whether that
   role exists is settled by whoever builds the screen, against the tenant.
   Treat a named role as a claim to verify, never as a verified fact.
4. **Reconciliation keys on `anonymousAccess` plus `roles[]`, never on a
   `Public:true` flag.** The render-gate check derivation already measured
   why: a non-empty `roles[]` alone is not evidence a screen is gated, so
   `anonymousAccess` is the field that decides and `roles[]` says which grants
   the principal needs.

`preview_public` is the build-time convenience — open while the app is being
assembled — and it is the value a promotion audit exists to catch. It must
never survive to promotion, and neither must `unresolved`.

Disclosure (does not block): an inventory with at least one **open** decision
prints `PROPOSED, NOT APPROVED` and lists each decision with its options, in
the report file as well as on stdout. Deferring is legitimate; deferring
silently is what this replaces.

## Contracts borrowed from downstream — do not fork them

These vocabularies are deliberately not this skill's own:

- **`app_chrome.layout_block` / `app_title` / `menu`** feed the fields
  `outsystems-ui-design`'s cross-blueprint chrome pass compares across the
  blueprints of one app: layout and title copy verbatim, and the menu
  translates from the inventory's `{label, target}` to the blueprint's
  `{label, active}` via `blueprint_menu_for_screen` (label order preserved -
  the order IS what the downstream pass compares; `target` stays here, and
  `active` is derived per screen). `--brief` prints each screen's translated
  menu. The two downstream chrome checks treat `active` **oppositely, and both
  are right**: comparing blueprints to each other still excludes it, because
  each screen legitimately highlights its own entry, while
  `validate_blueprint.py --inventory` checks it — against this inventory the
  active entry is not a matter of opinion, it is whichever one targets that
  screen.
- **Reachability is a graph walk, not an incoming-edge check**: every screen
  must be reachable from a menu entry or a screen marked `entry_point: true`
  (deep link / external URL / notification). Two screens pointing only at each
  other are an island and an error.
- **`assertions`** accepts only `links`, `buttons`, `inputs` — the vocabulary
  `outsystems-ui-design`'s validator recomputes from `main_content` and
  `outsystems-mentor-implementation/scripts/recompute_assertions.py` re-checks
  against the built model after publish. A new key here would be silently
  unchecked at both. It is **optional**: declare a count only where the
  requirement itself pins one. An inventory is early to be counting buttons,
  and a wrong count declared here propagates.
- **`archetype`** is one of the 14 archetypes `outsystems-ui-design` confirms
  at its Step 1.
- **`presentation_pattern`** is **optional**, and refines `archetype` with the
  ODC block the screen's main collection is laid out in — one of `TableRecords`,
  `Gallery`, `IList+Card`, `MasterDetail`, `Accordion`, named in
  `outsystems-ui-design`'s block vocabulary
  (`outsystems-ui-design/references/blocks-index.md`).
  Declaring it takes the list-vs-gallery-vs-cards decision **once, for the whole
  app**, instead of leaving N design runs to re-take it independently from the
  same requirements. `--brief` prints it as a **hint**: a design run may diverge,
  but not silently — a divergence is a design decision it has to state. **Omit
  it** wherever the screen lays out no collection (`edit-form`, `wizard`,
  `settings`, `instructional`), and omit it for a plain non-card list
  (`IList` + `ListItemContent`), which deliberately has no value here — an
  approximation would be read downstream as a decision.
- **The requirement-ID grammar** in `candidates[].source_ref` and
  `non_screen_requirements[].id` is `outsystems-plan-to-mentor`'s
  (`outsystems-plan-to-mentor/scripts/check_requirement_coverage.py`, `ID_PATTERN`). This skill carries a
  duplicate rather than importing it, because the two skills ship in different
  packs and no cross-skill Python import exists — a shared module would buy a
  packaging dependency to deduplicate one regex. A drift test
  (`test_requirement_id_pattern_matches_plan_to_mentors`) pins the two copies
  equal, and unlike the layout drift test it **fails rather than skips** when
  the sibling skill is absent: a silently skipped drift test is how drift
  hides. Change both copies together.

Changing any of these without changing them downstream breaks the loop. If a
fourth assertion key is ever wanted, it lands in all three places or in none.

## Provenance — read this before relying on the skill

**This skill ships on method-log provenance, not on trial evidence.**

- The method (`references/method.md`, rules R1–R9) is harvested from a **real**
  23→9 screen fusion carried out 2026-07-14 and logged while it happened, plus
  two rules (R6, R7) paid for by the 2026-08-08 Phase 1 chain trial.
- The Phase 1 trial that gated this program **did not exercise this judgement
  at all**: it built a single screen on an existing app, so the "requirements
  doc → these are the N screens" decision never came up. The master plan says
  so in as many words — Phase 2 "proceeds on the pre-existing method log, not
  on Phase 1 evidence."
- The worked example in `references/examples/elastic-sandbox-inventory.json` is
  that same 2026-07-14 decision reconstructed into this format: 23 candidates,
  9 screens, one dissolution, one candidate split across two screens. It is a
  **regression fixture** proving the format can carry a real decision — not a
  second, independent trial.
- The direction the method was harvested from is **modernization** (existing
  screens in, fused screens out). The direction the chain actually needs is
  **greenfield** (a PRD in, screens out). The accounting discipline transfers
  cleanly and the format is the same; the judgement in that direction is
  untested. `source.kind` records which direction any given inventory ran.

**What that means in practice:** treat the validator as trustworthy (it checks
accounting, vocabulary and reachability — all mechanical) and the workflow as a
first draft. The first real multi-screen run should keep a friction log, the
same way the design skill was hardened.

## Install (both agents) — installed 2026-08-08

Installed as symlinks on all three estate surfaces (stdlib-only, no other
dependency), with the registry row at `status: active` / `install_modes:
symlink`. The deferral this section originally recorded ran its course the
same day it was written: skill review Codex-approved (AH-2026-08-08-011,
two rounds), then the required greenfield trial ran (Search Engine Sandbox
admin area: PRD → 13 candidates → 5 screens, validator exit 0 first pass,
one design run consumed the brief), Codex judged the gate satisfied
(AH-2026-08-08-012), and the install was approved. The two sections above
marked G-02 and G-03 are that trial's findings, landed with this install.

## Tests

```bash
python3 -m pytest skills/outsystems-screen-inventory/tests -q
```
