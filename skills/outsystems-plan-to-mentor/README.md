# outsystems-plan-to-mentor

Use this skill after you already have an OutSystems implementation plan and
need to turn it into Mentor-ready work. It coverage-audits the plan against the
source PRD or original request, writes a minimally patched plan file, asks how
the result should be delivered, then routes the patched plan to
`outsystems-mentor-implementation`.

The skill works with Codex and Claude because the core workflow is plain
Markdown, uses project-local files, and treats MCP delivery as optional. It does
not depend on agent-private config, private caches, or a single plan generator.

## What It Is For

Use it when you have a saved OutSystems plan from any source and want a
reviewable gate before Mentor conversion:

- a plan from `superpowers:writing-plans`
- a spec-driven OutSystems workflow
- a hand-written plan
- a plan copied from another agent or conversation

Do not use it to write the first PRD or the first plan. Create or save the plan
first, then run this skill as the post-plan gate.

## Missing Plan Behavior

If the source PRD exists but the saved plan file does not, stop before coverage
review. Do not suggest `write-and-review-plan`. Use `superpowers:writing-plans`
or another explicit plan generator to create the saved plan first, then rerun
`outsystems-plan-to-mentor` with the new plan path.

## Business Intent Plan Boundary

The missing-plan fallback should create a business/capability implementation
plan, not an ODC Studio element recipe. Do not map writing-plans tasks directly
to ODC elements.

The first plan should stay focused on capabilities, user workflows, acceptance
criteria, scope boundaries, dependencies, and open decisions. Studio-native
pseudocode belongs in `outsystems-mentor-implementation`, after
`outsystems-plan-to-mentor` has completed the coverage loop and patched plan.

Do not create ODC element inventory sections. Do not list entity attributes,
server action inputs, client actions, aggregates, or screen widgets. Use
capability headings such as users and goals, workflows, business rules,
acceptance criteria, dependencies, open decisions, and scope boundaries.

Do not include generic Superpowers execution headers. Do not copy
scanner-forbidden token strings into saved plan text, even inside negative
wording. Use an OutSystems-specific handoff header that sends the plan through
`outsystems-plan-to-mentor` first, then `outsystems-mentor-implementation`.

## Required Inputs

- Source PRD or original request: the source of truth for coverage review.
- Saved plan file: the implementation plan to audit and patch.
- Target app name or app key: only needed if you may choose OutSystems MCP
  delivery.

## Main Strategy

The strategy from the design session is to keep plan creation interchangeable
and make this skill own the review-to-Mentor handoff:

```text
PRD / original request
        |
any plan generator
(superpowers:writing-plans, spec-driven, hand-written, etc.)
        |
outsystems-plan-to-mentor
        |
bounded coverage loop + patched plan file
        |
delivery mode question
        |
outsystems-mentor-implementation
        |
Mentor-ready file
        |
paste manually OR send via OutSystems MCP
```

This keeps the workflow deterministic: the original plan is not treated as
Mentor-ready until it has been checked against the source request, patched, and
scanned for generic execution handoffs.

In short, the skill still produces a coverage audit + patched plan file; it now
does so through a bounded loop rather than a single review.

## Companion Availability

With `outsystems-mentor-implementation` available, this skill runs the full flow:

```text
coverage audit + patched plan
        |
outsystems-mentor-implementation
        |
full deterministic Mentor package
        |
Manual Setup Gate + Session Readiness Matrix + Studio-native pseudocode + Mentor executable sessions
```

Without `outsystems-mentor-implementation` available, this skill still provides value but has a smaller boundary:

- It can complete the coverage loop.
- It can write the full patched plan.
- It can stop and tell you to install or use `outsystems-mentor-implementation` for the full deterministic Mentor package.
- If degraded paste mode is acceptable, it can write a DEGRADED OUTPUT file using the 10-section Mentor spec format only.

The degraded paste-mode Mentor spec is paste mode only and does not include Studio-native pseudocode packages. It does not include Data Model Pseudocode, Server Action Pseudocode, Client Action Pseudocode, Screen/UI Pseudocode, Navigation Pseudocode, or Verification Pseudocode.

Install or use `outsystems-mentor-implementation` for the full deterministic Mentor package.

## Coverage Loop

The skill always runs at least two passes before delivery mode. Each pass writes
a visible matrix headed `Coverage Audit -- Patched Plan vs Spec`:

```markdown
| Requirement | Status | Evidence | Patch / Risk |
|---|---|---|---|
```

Pass 1 reviews the original plan and writes the first full patched plan. Pass 2
reviews the patched plan as if it came from someone else. A third pass is used
only when remaining Missing or Partial rows, weak evidence, or ODC/Mentor
precision issues still need closure. The delivery mode question comes after the
final matrix and scanner pass, not before.

The `-patched.md` artifact is the full patched plan, not a summary wrapper. If
the original plan is also edited in place, the full final content still needs to
be copied into `-patched.md` because the scanner and Mentor conversion use the
same `-patched.md` file.

## Outputs

By default the skill writes project-local artifacts:

- `docs/superpowers/plans/<plan-stem>-coverage-review.md`
- `docs/superpowers/plans/<plan-stem>-coverage-review-v2.md`
- `docs/superpowers/plans/<plan-stem>-coverage-review-final.md`, only when a
  third pass is needed
- `docs/superpowers/plans/<plan-stem>-patched.md`
- `docs/superpowers/plans/<plan-stem>-mentor-output.md`
- `docs/superpowers/reviews/<plan-stem>-mentor-result.json`, only when MCP
  delivery is used

The Mentor-ready file is always written before any optional MCP send.

## Codex Prompt

```text
$outsystems-plan-to-mentor

Source PRD or original request:
<path or pasted source>

Saved plan file:
<path to the plan>

Target app, if MCP delivery may be used:
<app name or app key, or "paste mode only">
```

## Claude Prompt

```text
Use the `outsystems-plan-to-mentor` skill.

Source PRD or original request:
<path or pasted source>

Saved plan file:
<path to the plan>

Target app, if MCP delivery may be used:
<app name or app key, or "paste mode only">
```

## Portability Notes

- Keep durable artifacts in the active project.
- Keep Codex adapter metadata isolated to `agents/openai.yaml`.
- Keep the core workflow free of Claude tool names and Codex tool names.
- Use paste mode when OutSystems MCP tools are unavailable.
- Do not publish, deploy, roll back, promote, package, push, or create pull
  requests from this skill without separate explicit approval.
