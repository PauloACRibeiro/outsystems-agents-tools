# Mentor implementation invocation payload (prompt template)

- version: 1 (2026-08-06 — extracted unchanged from `references/mentor-implementation-invocation.md`; prompts-as-data, Enzyme adoption #3)
- owner: `outsystems-plan-to-mentor/references/mentor-implementation-invocation.md`
- placeholders: the file paths (`docs/superpowers/specs/approved-prd.md`, `docs/superpowers/plans/feature-patched.md`, `docs/superpowers/plans/feature-mentor-output.md`, `docs/app-map.md`) and the `|`-separated option lists on `Delivery mode:` and `Target app state:` — pick one option per line; `Invocation mode:` and `Mentor spec guardrails:` are fixed values

Emit the payload below when invoking `outsystems-mentor-implementation`, replacing the sample paths with the actual project-local paths and selecting one option per `|`-separated field.

## Template

```text
Invocation mode: outsystems-plan-to-mentor
Delivery mode: paste-prompts | outsystems-mcp
Source PRD: docs/superpowers/specs/approved-prd.md
Patched plan: docs/superpowers/plans/feature-patched.md
Output file: docs/superpowers/plans/feature-mentor-output.md
Target app state: new-app | template-scaffold | existing-app
Target app inventory: docs/app-map.md
Mentor spec guardrails: references/mentor-spec-guardrails.md
```
