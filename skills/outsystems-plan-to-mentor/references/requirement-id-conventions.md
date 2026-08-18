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

## Reference site: the plan

The plan cites IDs inline where each requirement is addressed — in the
section or step that implements it, not in a detached list. Deliberate
exclusions still cite the ID: a deferred or out-of-scope requirement is
referenced in the plan's scope boundaries or accepted-risk section with its
disposition. Silence is the only failure mode.

- Reference by ID, not by position ("BR-003", never "the third rule").
- Every ID cited in the plan must exist in the inventory; a citation of an
  undefined ID is a dangling reference and fails the checker.

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
- The Design cell carries comma-separated `blueprint:<ScreenName>` or
  `inventory:<ScreenName>` refs (the `<ScreenName>` is the artifact's
  `screens[].name` value verbatim — spaces allowed, e.g.
  `inventory:Search Console`), or an explicit `none` for a story with no
  drawn surface. An empty cell fails; silence is the only failure mode.

## What the checker computes

`scripts/check_requirement_coverage.py <inventory-or-prd> <plan>
[--blueprint <blueprint.json>] [--inventory <screen-inventory.json>]`:

- uncovered = IDs defined in the source, never referenced in the plan.
- dangling = IDs referenced in the plan, never defined in the source.
- When the plan has a `## Traceability` table: unmapped requirements
  (defined but in no row), undefined or row-less stories, and missing
  design cells. With `--blueprint`/`--inventory`, each design ref must name
  an actual `screens[].name` in that artifact.
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
