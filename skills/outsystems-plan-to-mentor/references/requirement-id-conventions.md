# Requirement ID Conventions

Every requirement in the source of truth gets a stable ID, and every plan
cites the IDs it addresses. Coverage then stops being a number the reviewer
reports about itself: it is a set difference `scripts/check_requirement_coverage.py`
computes over the IDs.

## ID grammar

- `BR-NNN` — business rule. Atomic, testable, worded as an invariant.
- `UC-NNN` — use case. One per primary actor goal.
- `C-NNN` — acceptance criterion. One per observable behavior that proves a
  capability works.
- `US-n` — user story. Unpadded (`US-1`), one per actor goal the plan
  delivers; stories join requirement sets to design artifacts in the
  Traceability table below. Story IDs participate in the checker only when
  the plan carries that table; a legacy no-table plan keeps the exact
  pre-traceability ID universe.
- `T-NNN` — optional task stamp on plan tasks, so a finished plan's items
  trace back to the requirements they serve. Task IDs are plan-internal:
  the checker ignores them entirely (they are never dangling references).

`NNN` is zero-padded to three digits (`BR-001`). An optional uppercase scope
infix is allowed for large sources (`BR-VISIT-001`). IDs are stable: never
renumber, never reuse a retired ID, keep the same IDs across coverage passes.

### Surface namespaces

For multi-surface plans, namespace business rules per surface with the scope
infix, so a rule's home is readable from its ID (adopted from the upstream
`BR-BP-`/`BR-SP-` pattern, adapted to this loop's surfaces):

- `BR-DM-NNN` — data model
- `BR-SC-NNN` — screens / UI
- `BR-SEC-NNN` — security / roles
- `BR-INT-NNN` — integrations
- `BR-WF-NNN` — workflows / business logic

The plain form (`BR-001`) stays valid for small single-surface sources; do
not renumber an existing inventory to add namespaces.

## Definition site: the Requirement Inventory

IDs are defined exactly once, in the source of truth. If the source PRD or
original request already carries IDs, use them unchanged. If it does not,
coverage pass 1 assigns IDs and records them in a `## Requirement Inventory`
table at the top of the coverage review artifact:

```markdown
## Requirement Inventory

| ID | Type | Requirement |
|---|---|---|
| BR-001 | Business rule | A visit belongs to exactly one member |
| UC-001 | Use case | Log a visit |
| C-001 | Criterion | A new visit appears in the visit list |
```

The inventory file (or the ID-carrying PRD) is the definition side of the set
difference. Later passes reuse the same inventory; they may append new IDs
when the source reveals a missed requirement, but existing rows never change.

### One obligation per ID

The rule is one obligation per ID. The checker's unit is the ID token, so a
requirement asserting two things is one binary over two obligations:
`BR-007 — a booking belongs to exactly one room and cannot overlap another`
scores as covered the moment the plan addresses either half, and the other
half leaves no trace anywhere. The failure has a name — two obligations
wearing one ID — and splitting them is the fix.

Split at pass 1, while the inventory is being written and before any plan
cites the IDs — never a sub-ID. `BR-007.a` is invisible to the checker, which
matches whole tokens against the grammar above, so a sub-ID scores only when
an author happens to type it and reads as a dangling reference when they do.
Give the second obligation the next free number instead, and leave every
existing row untouched: the stability rule outranks the split. After pass 1
the plan already cites the IDs, so renumbering would break those citations —
a later pass records the compound in its findings rather than resplitting it.

## Reference site: the plan

The plan cites IDs inline where each requirement is addressed — in the
section or step that implements it, not in a detached list. Deliberate
exclusions still cite the ID: a deferred or out-of-scope requirement is
referenced in the plan's scope boundaries or accepted-risk section with its
disposition, or — better — carried in the Requirement Dispositions table
below. Silence is the only failure mode.

- Reference by ID, not by position ("BR-003", never "the third rule").
- Every ID cited in the plan must exist in the inventory; a citation of an
  undefined ID is a dangling reference and fails the checker.

## The Requirement Dispositions table

Citing a deferred ID in the scope boundaries discharges it, and the checker
scores that citation as covered. That is the designed behaviour and it is not
wrong — but it costs a distinction: a `12/12 READY` verdict reads the same
whether twelve requirements were built or three were built and nine deferred.
The plan carries an optional `## Requirement Dispositions` section to recover
it:

```markdown
## Requirement Dispositions

| ID | Disposition | Reason |
|---|---|---|
| BR-014 | deferred | member data lands in the next build |
| UC-007 | out-of-scope | belongs to the admin product |
| C-011 | accepted-risk | no owner for the reconciliation data |
```

- The vocabulary is closed: `built`, `deferred`, `out-of-scope`,
  `accepted-risk`. Anything else fails the checker.
- Each of the three terminal dispositions requires a non-empty Reason. A
  terminal disposition is a decision, not a silence.
- A dispositioned requirement **leaves the denominator** as well as the
  numerator — neither gap nor win. The checker reports the rate over the
  in-scope set and prints the defined and dispositioned counts beside it.
- `built` is the state every requirement is already in, so a `built` row
  changes nothing: the ID stays in the denominator and still needs its inline
  citation. Like the Traceability table, this table is excised from the
  inline-citation scan, so declaring an ID built here is not evidence the plan
  builds it.
- One row per requirement, no duplicates; every ID in the table must be
  defined in the source. A malformed row is a failure, never silently skipped.
- A dispositioned requirement needs no Traceability row: no story delivers it.
- A plan that dispositions every defined requirement builds nothing, and the
  checker fails it rather than reporting a vacuous full-coverage verdict.

The table is optional. A plan without one keeps the exact citation-only
behaviour described above, including the sanctioned scope-boundaries
discharge — nothing about existing plans changes.

## The Traceability table

The plan carries a `## Traceability` section joining each user story to the
requirement set it delivers and the design artifact that draws it — the
loop's design artifacts are the enriched `blueprint.json`
(`outsystems-ui-design`) and `screen-inventory.json`
(`outsystems-screen-inventory`), both keyed by `screens[].name`:

```markdown
## Traceability

| Story | Requirements | Design |
|---|---|---|
| US-1 | BR-DM-001, UC-001, C-001 | inventory:RoomList |
| US-2 | BR-SEC-001 | blueprint:RoomDetail |
| US-3 | BR-WF-002 | none |
```

- Exactly one story per row, no duplicate story rows; every story defined
  in the inventory owns a row, and every row's story is defined in the
  inventory. A malformed row is a failure, never silently skipped.
- The Requirements cell cites at least one requirement ID. Every requirement
  defined in the source must appear in at least one row — a requirement in
  no row has no downstream reference, and the checker fails it as
  `unmapped`. The table never satisfies the inline-citation gate: an ID
  cited only in the table still reads as uncovered inline.
- A story whose **whole** Requirements cell is dispositioned still owns its
  row, and the checker names it: `note: 1 story delivers no in-scope
  requirement`, with the row, the story and each ID's disposition word. It is
  a note and never a failure, and `--strict` does not escalate it — the two
  rules above mean the row can neither be dropped (every defined story owns
  one) nor emptied (the cell cites at least one ID), so there is no compliant
  plan shape to fail the author toward. The counts were always right; what
  the note fixes is a row that reads as live work while carrying none. If the
  story really is out of this build, the honest fix is upstream — drop it
  from the source's story list — not a rewrite of the plan.
- The Design cell carries comma-separated `blueprint:<ScreenName>` or
  `inventory:<ScreenName>` refs (the `<ScreenName>` is the artifact's
  `screens[].name` value verbatim, e.g. `inventory:SearchConsole`), or an
  explicit `none` for a story with no drawn surface. Since 2026-09-02 both
  upstream artifacts hold the ODC **element** name there — letters, digits and
  underscore, the human title having moved to `display_name`
  (AH-2026-09-02-006) — so a spaced ref means the upstream artifact is wrong,
  not the plan. The checker still parses a spaced cell rather than choking on
  it, so the failure is reported by the artifact's own validator, where the
  repair is. An empty cell fails; silence is the only failure mode.

## What the checker computes

`scripts/check_requirement_coverage.py <inventory-or-prd> <plan>
[--blueprint <blueprint.json>] [--inventory <screen-inventory.json>]
[--strict]`:

- uncovered = in-scope IDs never referenced in the plan. Each uncovered ID is
  printed with its Type and Requirement text when the source carries a
  `## Requirement Inventory` table, so the gap names the obligation and not
  just the token; a source without that table prints bare IDs.
- dangling = IDs referenced in the plan, never defined in the source.
- When the plan has a `## Requirement Dispositions` table: the in-scope set is
  the defined IDs minus the dispositioned ones, and the reported rate is
  `covered/in-scope` with the defined and dispositioned counts beside it.
  Unknown disposition values, terminal dispositions with no reason, duplicate
  or undefined rows, and a plan that dispositions everything all fail.
- When the plan has a `## Traceability` table: unmapped requirements
  (defined but in no row), undefined or row-less stories, and missing
  design cells. With `--blueprint`/`--inventory`, each design ref must name
  an actual `screens[].name` in that artifact.
- A Traceability row whose whole Requirements cell is dispositioned is named
  as a note, with each ID's disposition word. It never moves a count or the
  verdict, and unlike an unresolved design ref it has no `--strict` form.
- A design ref whose artifact was **not** supplied cannot be resolved at all.
  The checker names each such ref, counts them, and says which flag would
  resolve it. By default that is a note and the verdict is unchanged; with
  `--strict` it is a failure. `check_handoff_gate.py` always passes
  `--strict`, so through the gate an unresolved ref fails the
  `requirement-coverage` clause — supply the artifact, write the story's
  design cell as an explicit `none`, or waive the clause with a reason.
- With `--inventory`: every destination reachable from a screen the plan
  builds must itself be built by the plan. The inventory names both ends —
  a `navigation[]` edge's `trigger` is the control and its `to` is the
  destination, and a `record_actions` entry resolving to a screen name is the
  same binding for a record action. Each unbuilt one is reported as an
  **unbuilt destination** and fails the run. "The plan builds screen X" is
  "the plan names X somewhere", deliberately generous: a screen can be built
  by an item that owns no traceability row, and keying this on the Design
  column alone accused a screen the plan really did build. An action declared
  `inline` or `out-of-scope` names no destination and is not checked — the
  second is the author's recorded statement that the control is not built.
  Without `--inventory` there is nothing to compare and the check does not
  run; a plan citing `inventory:<Screen>` refs without supplying the file is
  already failed by the unresolved-ref rule above.
- Verdict: `READY` only when every set is empty; otherwise `NOT READY`.

### Migration note — plans without a Traceability table

Plans written before this scheme (in-flight runs) carry no Traceability
table. The checker accepts them: it prints
`note: no Traceability table found` and checks inline citation coverage
only, exactly the pre-2026-08-13 behavior. New plans include the table; do
not rewrite in-flight run artifacts to add one.

The checker proves every requirement is cited somewhere; it cannot prove the
citation is honest. The coverage matrix's Evidence column stays a judgement
check on top of the mechanical gate: the reviewer verifies each cited section
actually addresses its requirement.
