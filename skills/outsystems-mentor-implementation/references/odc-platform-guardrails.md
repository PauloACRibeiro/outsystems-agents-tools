# ODC Platform Guardrails

Use this OMI-owned reference when a prompt or pseudocode block touches
platform-level risk: architecture layering, public services, security-sensitive
server calls, query performance, timers/background processing, or public API
contracts.

This reference is read-only prompt discipline. It does not authorize
`app_create`, does not authorize `mentor_start`, does not authorize
`publish_start`, and does not authorize deploy, rollback, cleanup, or tenant
mutation. It does not replace current official docs, `outsystems-tech-content`,
or ODC Portal impact analysis.

Ground this guidance in current OutSystems public documentation before making
product-contract claims. Use `outsystems-tech-content` when available for
current Studio syntax, function signatures, widget rules, TrueChange messages,
and implementation-level authority.

This reference does not require any sibling architecture skill and does not
require a graph, HTML report, script, client-specific cache path, fixed filename,
or fixed JSON shape.

## Entry Routing

For platform guardrail-sensitive requests involving architecture layering,
public services, server trust, anonymous or registered access, query
performance, timers, background processing, async retry, imports, bulk work, or
public API contract changes, open [references/source-map.md](source-map.md)
and [references/odc-platform-guardrails.md](odc-platform-guardrails.md)
before producing output. Apply the Architecture Layering Gate, Security
Server-Trust Gate, Performance Query Pre-Mortem, Timer / Async Idempotency Gate,
or Public API Contract Gate as applicable.

## Architecture Layering Gate

Use this gate before OMI suggests reusable services, entities, public actions,
shared libraries, or cross-app dependencies.

Check:

- producer/consumer layer fit: the producer should belong below the consumer in
  the intended architecture direction.
- lifecycle independence: avoid references that couple applications or teams
  unnecessarily.
- one clear owner: do not place shared public services in an application with
  unclear or mixed ownership.
- sponsor or line-of-business boundary: isolate different sponsors or lines of
  business when their change pace differs.
- service exposure intent: Orchestration and End-user areas should not become
  generic service providers.
- foundation isolation: Foundation assets should not depend on business-specific
  Core assets.
- cycles: stop if the proposed dependency creates or reinforces a cycle.

Treat Orchestration, End-user, Foundation, and Core as application-composition
heuristics from public layering guidance, not as exact ODC runtime artifact
types.

Fallback behavior:

- If layer fit is unknown, add an `Unknowns And Fallback Behavior` item instead
  of emitting a confident dependency instruction.
- If the change touches a shared producer, also apply the existing Shared
  Producer Compatibility Gate in `tenant-context-guardrails.md`.
- If architecture-style or existing-app structure evidence is supplied, reduce it
  into OMI-owned evidence first. Do not require the producing tool, graph, report,
  cache path, or fixed data shape.
- If the supplied structure evidence is tenant-backed or names an existing app,
  run the Tenant Context Packet and Target App Resolution Gate in
  `tenant-context-guardrails.md` first, then reduce the result into OMI-owned
  evidence.

## Security Server-Trust Gate

Use this gate when OMI writes role-sensitive UI, anonymous or registered access,
client actions calling server actions, exposed REST, consumed REST with
credentials, or any operation that reads or mutates sensitive data.

Check:

- server-side authorization: sensitive reads and writes need validation in
  server-side logic.
- do not trust hidden or disabled UI controls: visibility and enabled state are
  user experience hints, not authorization.
- do not trust client-passed identity: derive user identity on the server side
  for server-side authorization and data filters.
- anonymous or registered access: state when a screen, REST endpoint, or action
  is public, authenticated, or custom-role restricted.
- input validation: validate externally supplied IDs, filters, status
  transitions, and ownership on the server.
- output minimization: do not expose sensitive system/user data unless the role
  and use case justify it.
- REST security: exposed REST endpoints need authentication and
  transport/security assumptions stated when relevant.

Fallback behavior:

- If explicit role evidence is missing, use the Role/Security Evidence Gate in
  `tenant-context-guardrails.md`.
- If server-side authorization cannot be specified, stop and ask for the policy
  instead of relying on UI-only restrictions.

## Performance Query Pre-Mortem

Use this gate when OMI writes Aggregates, SQL, list screens, dashboards, loops
over data, bulk operations, exports, imports, or data-heavy Server Actions.

Check:

- Max Records or pagination: every list or search query should state the expected
  limit.
- Aggregate or SQL inside `For Each`: do not emit this pattern without a
  pre-mortem and a reason it cannot be refactored.
- fetch only the fields needed: prefer structures or narrowed outputs for
  large/wide records when passing data through actions.
- query count: prefer a single joined query over sequences of dependent queries
  when that reduces round trips without hiding important business logic.
- index candidates for filters and joins: list candidate entity attributes used
  in frequent filters, joins, or sorts; do not claim an index must exist without
  current evidence.
- bulk writes: use set-based SQL only when the operation is truly bulk-oriented
  and the validation/transaction boundary is explicit.
- linked/external data: avoid cross-server joins when the data source boundary is
  known.

Fallback behavior:

- If expected volume is unknown, add `Volume/performance unknown` to
  `Unknowns And Fallback Behavior`.
- If performance is not the main risk, keep the pre-mortem short and do not force
  premature optimization.

## Timer / Async Idempotency Gate

Use this gate when OMI writes Timers, wake actions, background processing,
imports, long-running calls, retry loops, queue/status/polling flows, or async
cleanup.

Check:

- idempotency key or progress marker: repeated execution must not duplicate work
  or corrupt state.
- checkpoint: record where processing can safely resume.
- partial commit strategy: describe when partial commits are acceptable and what
  data is protected by each commit.
- safe retry behavior: define what happens after timeout, interruption, or
  scheduler retry.
- wake/polling behavior: for long work, define whether the flow wakes a timer,
  queues work, or exposes status for polling.
- batch size: state how many records/items are processed per run when volume is
  material.
- error isolation: record failed items separately when one bad record should not
  block the entire batch.

Fallback behavior:

- If idempotency cannot be proven, stop and ask for the durable progress model.
- If live execution is involved, use `live-mentor-campaign-guidance.md` before
  any Mentor, publish, deploy, rollback, cleanup, or tenant action.

## Public API Contract Gate

Use this gate when OMI creates or changes a public action, Service Action,
exposed REST method, consumed REST integration, shared producer API, event
contract, or reusable library boundary.

Check:

- input and output contract: name parameters, required/optional behavior, data
  types, and null/empty behavior.
- public descriptions: public elements and parameters need meaningful
  descriptions when they are part of a reusable contract.
- transaction behavior: state whether the public action commits, aborts, or
  relies on caller transaction scope.
- error semantics: define expected exceptions, error outputs, and retry-safe
  responses.
- compatibility: prefer additive changes, wrappers, or versioned actions when
  existing consumers may break.
- consumer impact: list known consumers or mark them unknown; route broad
  shared-producer changes through the Shared Producer Compatibility Gate.
- security: combine with the Security Server-Trust Gate for exposed REST or
  sensitive reusable actions.

Fallback behavior:

- If consumer impact is unknown, do not emit a confident breaking-change prompt.
- If transaction behavior is unknown, require clarification before making a
  public reusable action paste-ready.

## Unknowns And Fallback Behavior

Use these exact labels in OMI output when the gate cannot be satisfied:

- `Layer fit unknown`: architecture layer, owner, sponsor, or consumer direction
  is not verified.
- `Server-trust policy unknown`: the authorization, identity, or validation rule
  is missing.
- `Volume/performance unknown`: expected record count, page size, or query
  frequency is missing.
- `Idempotency model unknown`: no durable progress marker or safe retry behavior
  is defined.
- `Public contract impact unknown`: public consumers, transaction behavior, or
  compatibility strategy is missing.

When any of these labels materially affects safety, return a prompt/spec with an
explicit unknown rather than a paste-ready Mentor Studio instruction.
