# Mentor Implementation Invocation

Invoke `outsystems-mentor-implementation` only after the coverage review is written and the patched plan passes `scripts/check_plan_handoff.py`.

Use the invocation payload template in
[prompt-templates/mentor-implementation-invocation-payload.md](prompt-templates/mentor-implementation-invocation-payload.md).
Its fields, one per line: `Invocation mode: outsystems-plan-to-mentor` (fixed),
`Delivery mode: paste-prompts | outsystems-mcp` (pick one), `Source PRD:`,
`Patched plan:`, `Output file:`,
`Target app state: new-app | template-scaffold | existing-app` (pick one),
`Target app inventory:`, and
`Mentor spec guardrails:` (fixed — the guardrails travel inlined in the
payload's own `Mentor spec guardrails (inline)` section, emitted verbatim in
the same message). Do not send a path here: a path relative to this skill does
not resolve inside `outsystems-mentor-implementation`, which is where the
payload is read.

When applying this template to another plan, replace the file paths with the actual project-local source, patched plan, output, and inventory paths. `Target app state:` is required. `Target app inventory:` is required whenever the target app state is not `new-app`; it names the scaffold inventory source (app map file, Studio observation notes, or OutSystems MCP context output).

The invoked skill must:

- Treat the patched plan as the implementation source.
- Fail closed on target state: if `Target app state:` is missing or invalid, or the state is not `new-app` and `Target app inventory:` is missing, stop and ask before generating any output.
- Do not assume a greenfield target. When `Target app state:` is `template-scaffold` or `existing-app`, inventory the existing scaffold before generating sessions, using the target app inventory plus live observation when available, and fold pre-existing elements into the package as modifications rather than creations.
- Against that scaffold inventory, classify each Mentor session as create or modify in the required `Create Or Modify` column of the `Session Readiness Matrix`.
- Apply the relevant 10-section Mentor spec format and anti-failure guardrails carried inline in the payload.
- Preserve OutSystems implementation authority and evidence rules.
- Produce Studio-native, deterministic Mentor content. The 10-section Mentor spec is a summary layer; it does not replace the detailed pseudocode package.
- Include `Manual Setup Gate`, `Session Readiness Matrix`, `Studio-Native Pseudocode`, and `Mentor Executable Sessions`.
- In `Studio-Native Pseudocode`, include `Data Model Pseudocode`, role, server action, client action, screen/UI, navigation, and verification pseudocode for every capability covered by the patched plan.
- In the verification pseudocode, include a runtime smoke stage distinct from the acceptance cases, and surface test-app creation as an approval-gated manual prerequisite in the `Manual Setup Gate` when the smoke stage needs a generated test app.
- Write every Mentor session as a reconcile (ensure the element exists with the specified shape, update to match when present, never a bare create), with an expected element delta and a `Traps` list per session, and include a build-log table template in the package.
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
- Begin the file with the DEGRADED OUTPUT notice in
  [prompt-templates/degraded-output-notice.md](prompt-templates/degraded-output-notice.md),
  emitted verbatim (no placeholders).
- Use only the 10-section Mentor spec format from `references/mentor-spec-guardrails.md`.
- Do not send degraded output through OutSystems MCP.
- Do not label degraded output as Studio-native pseudocode.
- Do not include sections named `Manual Setup Gate`, `Session Readiness Matrix`, `Studio-Native Pseudocode`, `Data Model Pseudocode`, `Server Action Pseudocode`, `Client Action Pseudocode`, `Screen/UI Pseudocode`, `Navigation Pseudocode`, `Verification Pseudocode`, or `Mentor Executable Sessions` in degraded output.
