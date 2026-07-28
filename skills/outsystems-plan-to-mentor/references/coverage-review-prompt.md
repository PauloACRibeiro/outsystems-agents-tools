# Coverage Review Prompt

Use this prompt after writing or receiving a saved OutSystems implementation
plan and before Mentor conversion. The coverage gate is a bounded convergence
loop: run at least two coverage passes. Even if pass 1 claims 100, run pass 2,
and stop after max 3 passes.

```text
Using the original request/PRD already in this conversation as the source of truth, audit the plan you just produced for coverage and alignment.

For each major requirement you can infer from the request:

* mark it **Covered / Partial / Missing**
* briefly cite *where* it is addressed in the plan (section name or a short quote). If you cannot point to evidence, treat it as **Partial** or **Missing**.

Write the coverage matrix in this exact shape:

## Coverage Audit -- Patched Plan vs Spec

| Requirement | Status | Evidence | Patch / Risk |
|---|---|---|---|

## Platform Feasibility

In the same pass, extract the plan's platform-capability claims: anything the plan assumes the platform can do, such as agent call configuration, structured output, action calling, AI model connections, integration patterns, timers, workflows, or offline behavior.

Add each claim as an extra matrix row marked **Feasible / Infeasible / Unverified**:

* **Feasible** only with evidence from a current official OutSystems source retrieved this session: `workspace-knowledge-cc`, `outsystems-tech-content`, or live official docs. The companion constraint references from `outsystems-mentor-implementation` (start with its `agentic-routing.md` reference for agentic claims) may route to the official source, but a companion summary alone is not authority. If the official source cannot be retrieved, keep the row Unverified.
* **Infeasible** when the docs forbid the claimed configuration. Known example: action calling and structured output cannot be combined on the same agent call; a plan that assumes both on one call must be restructured before conversion.
* **Unverified** when no evidence was found either way. Say what was checked.

Do not declare convergence while any platform feasibility row is Infeasible or Unverified. An Infeasible row is an architecture decision for the user, not a silent patch; stop and present options. Feasibility checked here is cheap; the same discovery inside `outsystems-mentor-implementation` ripples back into spec and plan rework.

Then:

1. Give a simple **coverage score (0-100)** and a 1-2 sentence rationale.
2. List the **top gaps** (missing, partially covered, or unclear assumptions), prioritized by impact.
3. Produce a **patched version of the plan** that closes those gaps with **minimal changes**, preserving the original structure where possible (add/adjust sections rather than rewriting everything). The patched version must be the full plan text after edits. Do not write a summary-only patched artifact.

Before writing the patched plan file, replace any generic Superpowers execution handoff. The patched plan should point to `outsystems-plan-to-mentor` and `outsystems-mentor-implementation`.

Do not copy scanner-forbidden token strings into generated or patched plan content, even inside negative wording. Refer to them only as generic execution skills.

Repeat against the patched plan until convergence or max 3 passes:

* pass 1: original plan -> `coverage-review.md` and patched plan.
* pass 2: patched plan -> `coverage-review-v2.md`; patch again if any row is Partial, Missing, unsupported by evidence, or has invalid ODC/Mentor implementation detail.
* pass 3, only if needed: patched plan -> `coverage-review-final.md`; document any remaining accepted risk.

The scanner and Mentor invocation must use the same full patched plan file.

Convergence requires:

* no Missing rows.
* no Partial except explicitly accepted platform/runtime uncertainty.
* no Infeasible or Unverified platform feasibility rows.
* coverage >= 98.
* top gaps either closed in the patched plan or documented as accepted runtime risk.
* the final matrix is ready to show in the assistant response before delivery mode.
```
