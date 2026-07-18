# Mentor Implementation Invocation

Invoke `outsystems-mentor-implementation` only after the coverage review is written and the patched plan passes `scripts/check_plan_handoff.py`.

Use this invocation payload:

```text
Invocation mode: outsystems-plan-to-mentor
Delivery mode: paste-prompts | outsystems-mcp
Source PRD: docs/superpowers/specs/approved-prd.md
Patched plan: docs/superpowers/plans/feature-patched.md
Output file: docs/superpowers/plans/feature-mentor-output.md
Mentor spec guardrails: references/mentor-spec-guardrails.md
```

When applying this template to another plan, replace the three file paths with the actual project-local source, patched plan, and output paths.

The invoked skill must:

- Treat the patched plan as the implementation source.
- Apply the relevant 10-section Mentor spec format and anti-failure guardrails from `references/mentor-spec-guardrails.md`.
- Preserve OutSystems implementation authority and evidence rules.
- Produce Studio-native, deterministic Mentor content. The 10-section Mentor spec is a summary layer; it does not replace the detailed pseudocode package.
- Include `Manual Setup Gate`, `Session Readiness Matrix`, `Studio-Native Pseudocode`, and `Mentor Executable Sessions`.
- In `Studio-Native Pseudocode`, include `Data Model Pseudocode`, role, server action, client action, screen/UI, navigation, and verification pseudocode for every capability covered by the patched plan.
- Write the output file first.
- Use the selected delivery mode without asking unrelated execution questions.

## Missing Companion Fallback

The fallback is not the default path. When the companion is available, use the invocation payload above and let `outsystems-mentor-implementation` produce the full deterministic Mentor package.

Full flow desired:

- Stop after the patched plan and scanner pass.
- Report the patched plan path and the missing companion.
- Tell the user: `Install or use outsystems-mentor-implementation for the full deterministic Mentor package.`
- In prose summaries, keep the companion name as code: Install or use `outsystems-mentor-implementation` for the full deterministic Mentor package.
- Do not create a replacement Studio-native pseudocode package inside `outsystems-plan-to-mentor`.

Degraded paste mode acceptable:

- Write `docs/superpowers/plans/{plan-stem}-mentor-output.md`.
- Begin the file with this exact notice:

```text
DEGRADED OUTPUT: outsystems-mentor-implementation was not available. This file is a 10-section Mentor spec for paste mode only. It does not include Studio-native pseudocode packages and does not include Data Model Pseudocode, Server Action Pseudocode, Client Action Pseudocode, Screen/UI Pseudocode, Navigation Pseudocode, or Verification Pseudocode. Install or use outsystems-mentor-implementation for the full deterministic Mentor package.
```

- Use only the 10-section Mentor spec format from `references/mentor-spec-guardrails.md`.
- Do not send degraded output through OutSystems MCP.
- Do not label degraded output as Studio-native pseudocode.
- Do not include sections named `Manual Setup Gate`, `Session Readiness Matrix`, `Studio-Native Pseudocode`, `Data Model Pseudocode`, `Server Action Pseudocode`, `Client Action Pseudocode`, `Screen/UI Pseudocode`, `Navigation Pseudocode`, `Verification Pseudocode`, or `Mentor Executable Sessions` in degraded output.
