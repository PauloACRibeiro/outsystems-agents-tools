---
name: outsystems-plan-to-mentor
description: Review and patch saved OutSystems implementation plans before Mentor conversion. Use when the user has a plan from superpowers:writing-plans, an OutSystems spec-driven workflow, or a hand-written plan and needs PRD coverage review, a patched plan, Mentor-ready prompts, or optional OutSystems MCP delivery through outsystems-mentor-implementation.
---

# OutSystems Plan To Mentor

Coverage-review any saved OutSystems implementation plan before Mentor conversion. The plan generator is interchangeable; this skill owns the post-plan gate.

This skill works for both Codex and Claude, writes a patched plan before Mentor conversion, and keeps durable artifacts in the active project.

## Routing Boundary

Use this skill when the user has a saved OutSystems plan and asks to review it for coverage, patch gaps, produce Mentor-ready prompts, or optionally send the prepared prompt through OutSystems MCP.

Do not use this skill to write the original PRD, create the first implementation plan, or produce low-level Studio pseudocode directly. Use the relevant planner first, then use this skill. Delegate Studio-native conversion to `outsystems-mentor-implementation` after the patched plan is written.

Do not execute the plan with generic development skills. OutSystems Mentor delivery must go through this coverage gate and then `outsystems-mentor-implementation`.

Do not publish, deploy, rollback, promote, package, push, or create pull requests from this skill. Those actions require separate explicit approval outside the plan-to-Mentor gate.

## Inputs

Require both inputs before proceeding:

- Source PRD or original request: conversation context or file path.
- Saved plan file: project-local path to the plan being reviewed.

If either input is missing, stop and ask for the missing source. If the plan targets a live app and the user may choose MCP mode, also collect the target app name or app key before MCP delivery.

If the saved plan file is missing, do not continue coverage review and do not suggest `write-and-review-plan`. Offer to create the saved plan with `superpowers:writing-plans` or another explicit plan generator. After the plan is written, restart this workflow from step 1 with the new saved plan path.

### Missing Plan Generator Boundary

The first saved plan must be a business/capability implementation plan, not an ODC Studio element recipe. Do not adapt `superpowers:writing-plans` by mapping tasks directly to ODC elements.

Do not include Studio-native pseudocode, Server Action logic flows, entity attribute recipes, TrueChange steps, publish steps, or browser verification as the primary plan content. The first plan should describe capabilities, user workflows, acceptance criteria, scope boundaries, dependencies, and open decisions.

Do not create sections named `ODC Element Map`, `ODC Elements`, `Business Logic`, or `Screen Aggregates` in the first saved plan.

Do not list entity attributes, server action inputs, client actions, aggregates, screen widgets, role folders, TrueChange checks, publish checks, or browser checks in the first saved plan.

Use capability headings such as users and goals, workflows, business rules, acceptance criteria, dependencies, open decisions, and scope boundaries.

If the first plan seems to need an ODC element map to feel complete, stop at capability intent and let `outsystems-mentor-implementation` create the Studio-native element map later.

Leave Data Model Pseudocode, Server Action Pseudocode, Client Action Pseudocode, Screen And UI Pseudocode, Navigation Pseudocode, and Verification Pseudocode to `outsystems-mentor-implementation`.

The first saved plan must not include a generic Superpowers execution header. Do not copy scanner-forbidden token strings into the generated plan, even inside negative wording.

Refer to those forbidden strings only as generic execution skills in generated plan text.

Use an OutSystems-specific handoff header that points to `outsystems-plan-to-mentor` for coverage review and `outsystems-mentor-implementation` for Mentor conversion.

## Workflow

1. Read the saved plan and the source PRD or original request.
2. Load `references/coverage-review-prompt.md`.
3. Audit the plan against the source of truth using the required coverage matrix.
4. If coverage ambiguity would change requirements, stop and ask before patching.
5. Write the coverage review to `docs/superpowers/plans/{plan-stem}-coverage-review.md`.
6. Write a minimally patched plan to `docs/superpowers/plans/{plan-stem}-patched.md`. The patched plan artifact must be a complete executable plan, not a change summary or wrapper. Copy the full patched plan content into `docs/superpowers/plans/{plan-stem}-patched.md`. Do not patch only the original plan in place and leave `-patched.md` as a short summary. Before writing the patched file, rewrite any generic Superpowers execution header to the OutSystems-specific handoff header.
7. Run at least two coverage passes before delivery mode. Pass 2 audits the patched plan against the same source of truth, writes `docs/superpowers/plans/{plan-stem}-coverage-review-v2.md`, and patches the plan again if any row is Missing, Partial without accepted platform/runtime uncertainty, unsupported by evidence, or invalid for ODC/Mentor implementation.
8. Repeat the coverage loop until convergence or max 3 passes. Convergence means no Missing rows, no Partial except explicitly accepted platform/runtime uncertainty, coverage >= 98, and all top gaps are closed or documented as accepted runtime risk. If a third pass is needed, write `docs/superpowers/plans/{plan-stem}-coverage-review-final.md`.
9. Write each coverage pass to a versioned review artifact and show the final `Coverage Audit -- Patched Plan vs Spec` table before asking how to deliver.
10. Run `scripts/check_plan_handoff.py` against the same full patched plan file that will be sent to `outsystems-mentor-implementation`.
11. If the scanner reports a forbidden generic handoff, patch the plan again and rerun the scanner.
12. Load `references/delivery-modes.md`.
13. Do not ask the delivery mode question until the final coverage matrix is written and the patched plan passes the handoff scanner.
14. Ask the delivery mode question exactly once:

```text
1 - Create prompts ready to paste sequentially in Mentor in ODC Studio
2 - Send to Mentor using the OutSystems MCP
```

15. Load `references/mentor-spec-guardrails.md`.
16. Load `references/mentor-implementation-invocation.md`.
17. Companion Availability Gate: Before invoking `outsystems-mentor-implementation`, determine whether `outsystems-mentor-implementation` is available in the active agent's skill catalog or local skill roots.
18. Prefer the full companion flow whenever `outsystems-mentor-implementation` is available. If `outsystems-mentor-implementation` is available, use the full companion flow. Invoke `outsystems-mentor-implementation` with that same full patched plan path, source PRD or request, selected delivery mode, output file path, and relevant Mentor spec guardrails.
19. Require `outsystems-mentor-implementation` to write the Mentor-ready output file before any MCP send.
20. If `outsystems-mentor-implementation` is not available, ask the missing-companion fallback choice exactly once, separate from the delivery mode question:

```text
1 - Stop after the patched plan and install or use outsystems-mentor-implementation for the full deterministic Mentor package
2 - Write a DEGRADED OUTPUT paste-mode 10-section Mentor spec
```

21. If the user chooses option 1, stop after the patched plan. Report the patched plan path and explain that the full flow requires installing or using `outsystems-mentor-implementation`. State: Install or use `outsystems-mentor-implementation` for the full deterministic Mentor package.
22. If the user chooses option 2, write `docs/superpowers/plans/{plan-stem}-mentor-output.md` as a DEGRADED OUTPUT using only the 10-section Mentor spec format from `references/mentor-spec-guardrails.md`. This is a degraded paste-mode Mentor spec.
23. Degraded paste-mode Mentor spec output must be paste mode only. Do not send degraded output through OutSystems MCP, and do not label degraded output as Studio-native pseudocode.
24. At the top of degraded output, state: `DEGRADED OUTPUT: outsystems-mentor-implementation was not available. This file is a 10-section Mentor spec for paste mode only. It does not include Studio-native pseudocode packages and does not include Data Model Pseudocode, Server Action Pseudocode, Client Action Pseudocode, Screen/UI Pseudocode, Navigation Pseudocode, or Verification Pseudocode. Install or use outsystems-mentor-implementation for the full deterministic Mentor package.`

## Artifact Rules

Use project-local artifacts:

- Coverage review: `docs/superpowers/plans/{plan-stem}-coverage-review.md`
- Coverage review v2: `docs/superpowers/plans/{plan-stem}-coverage-review-v2.md`
- Final coverage review, when needed: `docs/superpowers/plans/{plan-stem}-coverage-review-final.md`
- Patched plan: `docs/superpowers/plans/{plan-stem}-patched.md`
- Mentor output: `docs/superpowers/plans/{plan-stem}-mentor-output.md`
- MCP result, when used: `docs/superpowers/reviews/{plan-stem}-mentor-result.json`

The patched plan file is the source of truth for downstream Mentor conversion.
It must contain the full final plan text after all coverage patches. A separate
change-summary section may be included inside the full file, but a summary-only
artifact is invalid.

Do not write to Claude-private cache/config, Codex-private config, plugin caches, or agent-private runtime folders.

## Compatibility

Keep the canonical workflow compatible with both Codex and Claude:

- Use plain skill and capability names in durable instructions.
- Keep Codex-only tool discovery notes out of the core workflow.
- Keep Claude-only tool names and cache paths out of the core workflow.
- Treat OutSystems MCP delivery as conditional on tools being available in the active agent.
- If MCP mode is selected but tools are unavailable, say so explicitly and fall back to paste mode unless the user chooses to stop.

## Final Response

Report:

- Coverage score and rationale.
- Final `Coverage Audit -- Patched Plan vs Spec` table.
- Top gaps closed.
- Coverage review paths.
- Patched plan path.
- Mentor output path.
- Whether the Mentor output came from the full `outsystems-mentor-implementation` companion flow or degraded paste mode.
- If degraded paste mode was used, state that the output is a 10-section Mentor spec only and does not include Studio-native pseudocode packages.
- MCP result path when MCP mode was used.
- Remaining user decisions.
