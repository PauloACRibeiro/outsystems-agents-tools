# Mentor Spec Guardrails

Use this reference when turning a coverage-reviewed patched plan into
Mentor-ready output. It preserves the useful Mentor prompt structure from the
retired personal planning flow without depending on that older skill.

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
   source request or patched plan calls for demo data.

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

## Review Additions

Before final Mentor-ready output, check:

- RBAC: every screen has an explicit role assignment.
- Scope: ambiguous features are out of scope until confirmed.
- CSS: each new class is either theme-level or screen-local, not both.
- Blocks: similar block names remain distinct.
- Connectors: connector calls are preserved unless explicitly requested.
- Batching: batch groups are homogeneous and explain why.
- Warning baseline: post-Mentor warning deltas are measurable when a baseline is available.
