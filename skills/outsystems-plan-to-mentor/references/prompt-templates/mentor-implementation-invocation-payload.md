# Mentor implementation invocation payload (prompt template)

- version: 2 (2026-08-10 — the `Mentor spec guardrails:` field stopped naming a file and started carrying it. V23, first live colleague sprint-loop run 2026-08-09: the old value was a path relative to this skill, and the payload is read inside `outsystems-mentor-implementation`, where it resolves to nothing. Version 1 extracted this template unchanged from `references/mentor-implementation-invocation.md`; prompts-as-data, Enzyme adoption #3)
- owner: `outsystems-plan-to-mentor/references/mentor-implementation-invocation.md`
- placeholders: the file paths (`docs/superpowers/specs/approved-prd.md`, `docs/superpowers/plans/feature-patched.md`, `docs/superpowers/plans/feature-mentor-output.md`, `docs/app-map.md`) and the `|`-separated option lists on `Delivery mode:` and `Target app state:` — pick one option per line; `Invocation mode:` and `Mentor spec guardrails:` are fixed values

Everything from `## Template` down is emitted verbatim, in one message: the
field block first, then the guardrails section under it. Replace the sample
paths with the actual project-local paths and select one option per
`|`-separated field.

The guardrails section is part of the payload, not a pointer for the caller to
follow. Its content is copied verbatim from this skill's
`references/mentor-spec-guardrails.md`, which stays the owner; a test fails if
the two drift. Nothing below `## Template` may name a path relative to this
skill — the skill that reads the payload cannot resolve one.

## Template

```text
Invocation mode: outsystems-plan-to-mentor
Delivery mode: paste-prompts | outsystems-mcp
Source PRD: docs/superpowers/specs/approved-prd.md
Patched plan: docs/superpowers/plans/feature-patched.md
Output file: docs/superpowers/plans/feature-mentor-output.md
Target app state: new-app | template-scaffold | existing-app
Target app inventory: docs/app-map.md
Mentor spec guardrails: inlined below, under `Mentor spec guardrails (inline)`
```

## Mentor spec guardrails (inline)

Apply these to the Mentor-ready output. They are the anti-failure guardrails
the invocation contract names.

## 10-section Mentor spec format

1. **Overview** - purpose, change type (new or modify), target users, app shell key, and style direction.
2. **Roles** - role names, access rules, and anonymous access policy.
3. **Data model** - entities, attributes, and types. For modifications, say "No new entities - do NOT create any" when true.
4. **Screens + RBAC** - per-screen table with change type, heading text, batch group, and role assignment.
5. **Server actions + logic blocks** - new or modified server actions, service actions, aggregates, data actions, timers, events, REST methods, agentic flows, or workflow nodes. Use `outsystems-mentor-implementation` for Studio-native deterministic-intent blocks when logic details are needed.
6. **Integrations** - library references, consumed or exposed APIs, AI model connections, MCP connectors, and external prerequisites. For modifications, say "Do NOT add or remove library references" when true.
7. **UI/UX direction** - theme, CSS classes, layout patterns, responsive rules, and OutSystems UI guidance.
8. **Out of scope** - explicit exclusion list. Everything not confirmed stays here.
9. **Acceptance criteria** - machine-verifiable criteria matching the patched plan.
10. **Notes for Mentor** - disambiguation, naming conventions, known pitfalls, dependency order, and manual prerequisites.

## CRITICAL CONSTRAINTS

Append or adapt these guardrails in Mentor-ready prompts when relevant:

1. **Respect the role-per-screen assignments in Section 4 EXACTLY.**
   Do NOT default screens to anonymous/public access. If Section 4 says role =
   X, set the screen to require that role.

2. **Apply OutSystems UI to all screens.** Do NOT generate bare HTML layouts.
   Use OutSystems UI patterns where applicable.

3. **Use ODC terminology only.** Do NOT reference "Service Studio", "eSpace",
   or other OutSystems 11 concepts unless the source plan explicitly concerns
   O11 migration.

4. **Respect Section 8 absolutely.** If a feature is listed as out of scope,
   do NOT build it partially or speculatively.

5. **Do NOT call `eSpace.AddDependency(globalKey)` from
   `applyModelApiCode`.** If a referenced library is needed, surface that
   manual prerequisite in Section 10.

6. **Use the EXACT attribute types from Section 3.** Do NOT silently
   substitute `Integer` for `Long Integer` or infer different types.

7. **Implement seed data via a `BootstrapData` server action** only when the
   source request or patched plan calls for demo data. **Trigger it from a
   Timer with `Schedule = "WhenPublished"`** (`ScheduleConfiguration.WhenPublished
   = true`, fires automatically on every publish), **NOT from a screen's
   `OnInitialize`** — a screen-load trigger only fires when a real user opens
   that specific screen, so the database silently stays empty while the build
   looks complete. When converting an existing trigger, remove the old
   `OnInitialize` call in the same turn that adds the Timer — one trigger
   source. When the seed set spans 3+ entities or roughly 20+ records,
   pre-split it into one `Seed<EntityGroup>` sub-action per entity (or tight
   group), called in sequence from a thin `BootstrapData` coordinator that
   does only the idempotency check — a flat multi-entity seed flow has been
   observed failing mid-turn before self-correcting into exactly this split.
   The Timer itself goes through `outsystems-mentor-implementation`'s
   Timer / Async Idempotency Gate. (External field evidence, Arjan fork
   review 2026-08-12.)

8. **At the end, summarize** what was created or modified, what was skipped
   and why, and any manual steps the user must take.

9. **Respect producer-consumer order in Sections 4, 5, and 10.** Do NOT
   reference a server action, service action, screen, event, timer, agentic
   flow, or workflow node before its creation step in the same Mentor session.
   Cross-app library producers must be published or pre-existing before the
   consuming app uses them.

## Guardrail 7 override for modification plans

For existing-app modifications, replace guardrail 7 with:

```text
7. **Do NOT create seed data or BootstrapData actions** unless Section 4
explicitly requests it. This is a modification to an existing app - seeding is
out of scope unless stated.
```
