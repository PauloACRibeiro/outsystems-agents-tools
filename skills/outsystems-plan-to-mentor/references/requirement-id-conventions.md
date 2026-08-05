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

`NNN` is zero-padded to three digits (`BR-001`). An optional uppercase scope
infix is allowed for large sources (`BR-VISIT-001`). IDs are stable: never
renumber, never reuse a retired ID, keep the same IDs across coverage passes.

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

## What the checker computes

`scripts/check_requirement_coverage.py <inventory-or-prd> <plan>`:

- uncovered = IDs defined in the source, never referenced in the plan.
- dangling = IDs referenced in the plan, never defined in the source.
- Verdict: `READY` only when both sets are empty; otherwise `NOT READY`.

The checker proves every requirement is cited somewhere; it cannot prove the
citation is honest. The coverage matrix's Evidence column stays a judgement
check on top of the mechanical gate: the reviewer verifies each cited section
actually addresses its requirement.
