# Plan Conversion Manifest (structured schema template)

- version: 1 (2026-08-06 — extracted unchanged from `references/prompt-narrowing-preflight.md` § "Plan Conversion Manifest"; prompts-as-data, Enzyme adoption #3)
- owner: `outsystems-mentor-implementation/references/prompt-narrowing-preflight.md` § "Plan Conversion Manifest"
- placeholders: `[path, URL, or user-provided source label]`, `[commit, timestamp, version, or "user message dated ..."]`, `[stable source requirement id or short quote]`, `[block identifier]`, `[block_id in planned execution order]`, `[stable id]`, `[one concrete implementation goal]`, `[included source requirements and ODC elements]`, `[explicit exclusions deferred to other blocks]`, `[docs, tenant read-only evidence, supplied schema, or none]`, `[facts that must be resolved before execution]`, `[checks that prove this block is complete]`

Emit the manifest using the field skeleton below, replacing each bracketed placeholder. Field names are load-bearing: `scripts/response_contract_lint.py` asserts them as exact strings.

## Template

```text
source_plan_path: [path, URL, or user-provided source label]
source_plan_revision: [commit, timestamp, version, or "user message dated ..."]
coverage_map:
  - source_requirement: [stable source requirement id or short quote]
    block_id: [block identifier]
dependency_order:
  - [block_id in planned execution order]
blocks:
  - block_id: [stable id]
    block_goal: [one concrete implementation goal]
    scope_in: [included source requirements and ODC elements]
    scope_out: [explicit exclusions deferred to other blocks]
    evidence_required: [docs, tenant read-only evidence, supplied schema, or none]
    unknowns: [facts that must be resolved before execution]
    acceptance_checks: [checks that prove this block is complete]
```
