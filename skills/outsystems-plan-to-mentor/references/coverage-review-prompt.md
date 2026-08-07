# Coverage Review Prompt

Use this prompt after writing or receiving a saved OutSystems implementation
plan and before Mentor conversion. The coverage gate is a bounded convergence
loop: run at least two coverage passes. Even if pass 1 claims full coverage,
run pass 2, and stop after max 3 passes.

Load `references/requirement-id-conventions.md` first. The coverage number
and the coverage verdict come from `scripts/check_requirement_coverage.py`;
they are computed, never hand-authored.

```text
Using the original request/PRD already in this conversation as the source of truth, audit the plan you just produced for coverage and alignment.

First, establish the Requirement Inventory. If the source already carries stable requirement IDs (BR- business rules, UC- use cases, C- acceptance criteria), use them unchanged. If it does not, assign IDs per the requirement ID conventions and write the `## Requirement Inventory` table at the top of the coverage review artifact. IDs stay stable across passes: later passes reuse the same inventory and may only append.

For each requirement in the inventory:

* mark it **Covered / Partial / Missing**
* briefly cite *where* it is addressed in the plan (section name or a short quote). If you cannot point to evidence, treat it as **Partial** or **Missing**.

Write the coverage matrix in this exact shape, one row per inventory ID:

## Coverage Audit -- Patched Plan vs Spec

| ID | Requirement | Status | Evidence | Patch / Risk |
|---|---|---|---|---|

## Platform Feasibility

In the same pass, extract the plan's platform-capability claims: anything the plan assumes the platform can do, such as agent call configuration, structured output, action calling, AI model connections, integration patterns, timers, workflows, or offline behavior.

Add each claim as an extra matrix row (use `--` in the ID column) marked **Feasible / Infeasible / Unverified**:

* **Feasible** only with evidence from a current official OutSystems source retrieved this session: a public knowledge provider (`workspace-knowledge-cc` or `outsystems-public-knowledge` — either provider is acceptable; they expose the same public retrieval role), `outsystems-tech-content`, or live official docs. The companion constraint references from `outsystems-mentor-implementation` (start with its `agentic-routing.md` reference for agentic claims) may route to the official source, but a companion summary alone is not authority. If the official source cannot be retrieved, keep the row Unverified. When the evidence came from a public provider only — OMI's `provider: public-grounded` — the row is Feasible on public-docs authority; do not promote it to implementation-level authority, and keep it Unverified when it depends on exact TrueChange error text, internal/courseware material, or widget rules beyond OMI's generated catalogs, which a public provider cannot ground.
* **Infeasible** when the docs forbid the claimed configuration. Known example: action calling and structured output cannot be combined on the same agent call; a plan that assumes both on one call must be restructured before conversion.
* **Unverified** when no evidence was found either way. Say what was checked.

Do not declare convergence while any platform feasibility row is Infeasible or Unverified. An Infeasible row is an architecture decision for the user, not a silent patch; stop and present options. Feasibility checked here is cheap; the same discovery inside `outsystems-mentor-implementation` ripples back into spec and plan rework.

## Plan Integrity Checks

Audit these in the same pass and record findings in the matrix's Patch / Risk column:

* Every plan section or step cites the requirement IDs it serves, inline where the work happens.
* References resolve: anything a step depends on is defined earlier in the plan or in the recorded existing scaffold, never assumed.
* Producers come before consumers in the plan's ordering.
* Everything the plan introduces is reachable from a user workflow; no orphaned deliverables.
* Deferred or out-of-scope requirements are cited by ID in the scope boundaries or accepted-risk section with their disposition; nothing is silently absent.
* No generic bucket sections ("Misc", "Utilities", "Other").

Then:

1. Run `python3 scripts/check_requirement_coverage.py <inventory-or-prd> <plan-under-review>` and copy its full output verbatim into the review artifact. The coverage numbers, the uncovered and dangling lists, and the `coverage verdict:` line are computed, never hand-authored; do not restate them as your own estimate. The checker proves every ID is cited; the Evidence column stays the judgement check that each citation is honest.
2. List the **top gaps** (uncovered IDs, Partial rows, or unclear assumptions), prioritized by impact.
3. Produce a **patched version of the plan** that closes those gaps with **minimal changes**, preserving the original structure where possible (add/adjust sections rather than rewriting everything). The patched plan cites each requirement ID inline where it is addressed. The patched version must be the full plan text after edits. Do not write a summary-only patched artifact.

Before writing the patched plan file, replace any generic Superpowers execution handoff. The patched plan should point to `outsystems-plan-to-mentor` and `outsystems-mentor-implementation`.

Do not copy scanner-forbidden token strings into generated or patched plan content, even inside negative wording. Refer to them only as generic execution skills.

Repeat against the patched plan until convergence or max 3 passes:

* pass 1: original plan -> `coverage-review.md` and patched plan.
* pass 2: patched plan -> `coverage-review-v2.md`; patch again if any row is Partial, Missing, unsupported by evidence, or has invalid ODC/Mentor implementation detail, or if the checker reports NOT READY.
* pass 3, only if needed: patched plan -> `coverage-review-final.md`; document any remaining accepted risk.

The scanner and Mentor invocation must use the same full patched plan file.

Convergence requires:

* `scripts/check_requirement_coverage.py` reports `coverage verdict: READY` on the patched plan -- no uncovered IDs, no dangling references. An accepted-risk requirement converges by being cited in the plan's scope boundaries with its disposition, not by being waived from the checker.
* no Missing rows.
* no Partial except explicitly accepted platform/runtime uncertainty.
* no Infeasible or Unverified platform feasibility rows.
* top gaps either closed in the patched plan or documented as accepted runtime risk.
* the final matrix and the checker's verdict output are ready to show in the assistant response before delivery mode.
```
