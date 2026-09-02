# <App Name> — PRD

> Scaffolded by `outsystems-sprint-init`. Fill this in (superpowers:brainstorming
> writes it), save it beside this file as `docs/specs/<name>.md`, and leave
> `TEMPLATE.md` untouched for the next PRD. IDs are assigned HERE — a PRD without
> them costs a retrofit at the plan-coverage step, which is what this template
> exists to prevent.

## Problem & Goal

<what is broken today, and what "done" looks like>

## Scope

In scope: <…>
Out of scope: <…>

## Requirement Inventory

The definition site for every requirement ID. Assign IDs while writing the PRD;
the plan cites these IDs inline, and `check_requirement_coverage.py`
(`outsystems-plan-to-mentor`) computes coverage as a set difference over them.

| ID | Type | Requirement |
|---|---|---|
| BR-DM-001 | Business rule | A visit belongs to exactly one member |
| BR-SC-001 | Business rule | The visit list shows the ten most recent visits |
| BR-SEC-001 | Business rule | Only an Administrator can delete a visit |
| BR-INT-001 | Business rule | Member lookups come from the HR API |
| BR-WF-001 | Business rule | Closing a visit stamps its end time |
| UC-001 | Use case | Log a visit |
| C-001 | Criterion | A new visit appears in the visit list |
| US-1 | User story | As a receptionist I log a visitor's arrival |

Replace every row — the ones above are shape examples, not requirements.

### The grammar

- `BR-NNN` — business rule. Atomic, testable, worded as an invariant. For a
  multi-surface app, namespace it by surface with a scope infix:
  `BR-DM-` data model · `BR-SC-` screens/UI · `BR-SEC-` security/roles ·
  `BR-INT-` integrations · `BR-WF-` workflows/business logic. The plain
  `BR-001` form stays valid for a small single-surface app.
- `UC-NNN` — use case. One per primary actor goal.
- `C-NNN` — acceptance criterion. One per observable behaviour that proves a
  capability works.
- `US-n` — user story. **Unpadded** (`US-1`), one per actor goal the build
  delivers; the plan's Traceability table joins each story to the requirements
  it delivers and the design artifact that draws it.

`NNN` is zero-padded to three digits (`BR-001`), the scope infix is uppercase
and dash-separated (`UC-A-001`, never the fused `UC-A01`).

### Usage notes

- **One obligation per ID.** A rule asserting two things scores as covered the
  moment the plan addresses either half. Split it while writing this table —
  give the second obligation the next free number, never a sub-ID (`BR-007.a`
  is invisible to the checker).
- **IDs are stable.** Never renumber, never reuse a retired ID, keep the same
  IDs across coverage passes. Later passes may append rows; existing rows never
  change.
- **Silence is the only failure mode.** A requirement the build defers is still
  cited — in the plan's scope boundaries or its `## Requirement Dispositions`
  table (`deferred` / `out-of-scope` / `accepted-risk`, each with a reason).

Full rules: `references/requirement-id-conventions.md` in
`outsystems-plan-to-mentor`.

## Screens (first cut)

The screen list is decided properly by `outsystems-screen-inventory`, which
reads this PRD. Sketch what you already know here; do not hand-maintain a
second inventory.

| Screen | Purpose | Requirements |
|---|---|---|
| <Name> | <what the user does here> | BR-SC-001, UC-001 |

## Action Results

<!-- outcome-coverage: success-rows-required -->

The definition site for what each server action can return, the way the
Requirement Inventory above is the definition site for requirement IDs. A
machine reads it: `check_outcome_coverage.py` (`outsystems-plan-to-mentor`)
computes execution-outcome coverage as a set difference between the values
declared here and the outcomes the plan's verification matrix reaches. The
marker above opts every new spec into the checker's success-row and
containment requirements (restaurant-app-v2, 2026-08-27 and 2026-08-28):
every action that declares a refusal also needs a verification row that
reaches its success path, and every row asserting a payload or projection
does NOT contain something pairs with a row asserting what it DOES contain.
Leaving the marker in place is the default; remove it only for a design that
deliberately predates the rule.

Fill this in once the app's capabilities imply server actions. An app with no
server logic leaves the section empty and says so in one line.

### `CreateVisit`

Result is one of `Success`, `MemberNotFound`, `VisitAlreadyOpen`.

### `CloseVisit`

Result is one of `Success`, `VisitNotFound`, `VisitAlreadyClosed`.

Replace both — the ones above are shape examples, not actions.

### The grammar

Matched literally, because a parser reads it:

- The heading is the action name **in backticks** at `###`. Signature text
  after the closing backtick is fine; the name is read from the backticks.
- The declaration is **one sentence ending in a period**, every value in
  backticks: ``Result is one of `Success`, `MemberNotFound`.`` The value list
  stops at that period, so a sentence left unterminated swallows the paragraph
  after it.
- `Success`, `Ok`, `Created`, `Updated` and `Deleted` read as success values.
  Everything else is a refusal.

### What declaring a refusal costs

Every **non-success** value declared here needs at least one `V<N>` row in the
plan's verification matrix that reaches it by executing the action.
With the marker above in place (the default), every action that declares a
refusal also needs one `V<N>` row that names the action and observes its
success value — a guard proven to refuse is worthless when the state it
protects is reachable by nothing. Only a design that removes the marker keeps
the older rule that `Success` needs no dedicated row. A refusal branch is
reached only on purpose, which is exactly why it is the half worth gating.

So declare the refusals the capability genuinely has, and no more. Padding the
list buys verification work you did not need. Omitting one is the worse error:
**the checker proves every refusal you declared is exercised, and cannot prove
you declared every refusal you needed.** A check derived from this section is
structurally blind to what this section leaves out, so a clean run is a
statement about the values below, not about the action.

Declaring result values is capability intent — which outcomes the business
rules distinguish. It is not element design: no data shapes, no logic steps, no
signatures. Those stay downstream with `outsystems-mentor-implementation`.

## Roles & Access

| Role | Sees | Can change |
|---|---|---|

## Open Questions

- <question that must be answered before the plan is written>
