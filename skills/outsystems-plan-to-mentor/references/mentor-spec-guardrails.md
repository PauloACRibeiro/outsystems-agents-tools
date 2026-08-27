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

10. **Do NOT call a generated entity action from a screen or client action.**
    `Create<E>`, `CreateOrUpdate<E>`, `Update<E>` and `Delete<E>` are
    server-side; calling one from the client raises `Security Warning . You're
    exposing a database operation in the client side. Validate the data in a
    Server Action before changing the database.` Route every write through a
    Server Action that validates before it writes — a pass-through wrapper
    silences the warning without earning it. See
    `outsystems-mentor-implementation` `odc-platform-guardrails.md`, Security
    Server-Trust Gate.

## Guardrail 7 override for modification plans

For existing-app modifications, replace guardrail 7 with:

```text
7. **Do NOT create seed data or BootstrapData actions** unless Section 4
explicitly requests it. This is a modification to an existing app - seeding is
out of scope unless stated.
```

## Known Platform Bounds

Bounds worth designing around, split by authority.

### Confirmed by current official ODC docs

1. **A Setting default value is capped at 2,000 characters** (roughly 300
   words) and is rejected outright above that. Any system prompt of real
   substance will not fit; plan a different home up front — an entity row, a
   Resource, or runtime assignment — instead of trimming at build time.
2. **The ODC "Test agent" flow can create a generated test app in the
   tenant** (see Runtime Verification below for the approval consequence).

### Session-observed only

Observed live on a single tenant; require current documentation or a fresh
bounded observation of the target before treating them as load-bearing
platform facts:

3. **The ODC agentic template shipped `LoadMemory` with no Timestamp sort and
   `Max. Records` 50.** Check it first in any agentic app: unsorted, memory
   loads in unspecified order; sorted ascending, a conversation past the
   record cap deterministically drops recent turns while keeping old ones.
   Review `Max. Records` explicitly on every memory or list read path rather
   than accepting aggregate defaults silently; record the accepted bound and
   its failure mode when keeping it.
4. **Changing an agent's Response type broke consumer service actions.**
   Check every consumer of the public entry point when the response contract
   changes, and update it in the same session.
5. **Memory persistence needed a valid `AIMessage` assembled from a
   structured answer.** When a call returns structured output, the flow must
   build the assistant message explicitly before storing memory, or
   persistence breaks silently.

## Runtime Verification

Compiling clean does not prove the pipeline executes. TrueChange and a clean
publish prove shape, not behavior: a wrong identifier flowing between stages,
an empty serialization, or an inverted filter all survive compilation.

- Acceptance criteria (Section 9) must include a runtime smoke stage distinct
  from the data-correctness acceptance cases: run one end-to-end request and
  confirm the pipeline executes without runtime errors before judging answer
  quality.
- The ODC "Test agent" flow creates a new app in the tenant. That is tenant
  mutation beyond the app being built: surface it in Section 10 as an
  approval-gated manual prerequisite up front, not as a surprise at the end
  of the build.

## Review Additions

Before final Mentor-ready output, check:

- RBAC: every screen has an explicit role assignment.
- Scope: ambiguous features are out of scope until confirmed.
- CSS: each new class is either theme-level or screen-local, not both.
- Blocks: similar block names remain distinct.
- Connectors: connector calls are preserved unless explicitly requested.
- Batching: batch groups are homogeneous and explain why. Size them down as the target app grows — above a length threshold Mentor swaps the app summary its coding agent sees for a simplified, shorter version (verified in the coding agent's private source, `current_asset/summary.py`; see `outsystems-mentor-implementation` execution-gates §4), so on a large app it is working from a reduced view of the model and is not told so. Name every element the batch touches explicitly; never refer to one by position or as "the screen we just added".
- Functions: any Section 5 action specified as a Function declares **exactly
  one** output parameter — two raises `Only One Output Parameter Allowed`, zero
  raises `Output parameter required`, and neither publishes. A Data Action is
  the separate case: at least one output, not exactly one.
- Load-time data: no Section 5 screen spec fetches server data from
  `OnInitialize` or another render-blocking handler — that raises a Performance
  Warning directing the fetch to an Aggregate or Data Action. `OnInitialize`
  remains the right home for the variable assigns those queries read.
- Warning baseline: post-Mentor warning deltas are measurable when a baseline is available.
