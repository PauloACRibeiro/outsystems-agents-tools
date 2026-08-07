# Tenant Context Guardrails

Use this reference when OMI output uses tenant inventory, app list evidence,
cached tenant evidence, existing app target resolution, verified app-shell
identity, reusable asset discovery, tenant-backed dependency inventory,
existing app structure evidence, app overview artifact, app documentation
artifact, optional reverse dependency evidence, shared producer impact, shared
producer blast radius, or tenant-wide scope language before a Mentor Studio
prompt.

This reference is an evidence and scope discipline layer. It is not a tenant
execution skill, not a tenant architecture renderer, and not a replacement for
`outsystems-plan-to-mentor` coverage review.

Use a Tenant Context Packet or Existing App Structure Evidence packet only as
read-only target/dependency evidence for target identity, reusable asset names,
existing element names, dependency inventory, reverse dependency evidence,
scope control, and unknowns. It does not authorize tenant-changing actions, and
it does not prove exact Studio internals.

OMI does not call `outsystems-tenant-architecture` and does not require
tenant-architecture scripts, templates, cache files, or HTML output. Reuse only
the portable guardrail ideas after expressing them through the Tenant Context
Packet and OMI's own evidence contract.

## Tenant Evidence Preflight

Run this preflight when an OMI answer targets an existing app, verified app
shell, live Mentor campaign target, tenant-backed dependency inventory,
existing app structure evidence, app overview artifact, app documentation
artifact, optional reverse dependency evidence, shared producer impact, shared
producer blast radius, or a "which app should this go in?" placement decision.

The preflight result is the Tenant Context Packet. Stop at `Unknowns And
Fallback Behavior` when the target app name, canonical app key, environment,
and evidence freshness are not known well enough for a confident app-targeted
prompt.

## Tenant Context Packet

When tenant inventory is used, reduce it to this packet before generating OMI
output:

```text
Tenant Context Packet
- tenantId:
- environment:
- targetAppName:
- targetAppKey:
- targetAppType:
- evidenceSource: live | cached
- freshness:
- fetched_at:
- freshness_probe:
- reusableAssets:
- candidateIntegrations:
- candidateAgents:
- candidateLibraries:
- perAppDeepDiveNeeded: yes | no
- unknowns:
```

Keep the packet small. Use only fields needed for target identity,
dependency inventory, scope control, and unresolved questions.

## Worked Tenant Context Packet Examples

These examples are illustrative only. They are not live or cached tenant data.

Cached evidence example:

```text
Tenant evidence: cached, fetched_at=2026-06-29T20:10:00Z, freshness_probe=app_list(limit=1) total matched cached total

Tenant Context Packet
- tenantId: example-tenant
- environment: Development
- targetAppName: Example Service Portal
- targetAppKey: app-example-service-portal-dev
- targetAppType: WebApplication
- evidenceSource: cached
- freshness: acceptable for target identity only
- fetched_at: 2026-06-29T20:10:00Z
- freshness_probe: app_list(limit=1) total matched cached total
- reusableAssets:
  - Already exists (use existing): LowCodeLibrary ExampleSharedComponents
- candidateIntegrations:
  - Existing REST integration: ExampleRecordsApi
- candidateAgents:
  - Existing Agent: ExampleTriageAgent
- candidateLibraries:
  - ExampleSharedComponents
- perAppDeepDiveNeeded: no
- unknowns:
  - exact screen variables and widget tree still require app-specific evidence
```

Stale evidence example:

```text
Tenant evidence: stale, fetched_at=2026-06-28T09:00:00Z, freshness_probe=app_list(limit=1) total changed from cached total

Tenant Context Packet
- tenantId: example-tenant
- environment: Development
- targetAppName: Example Service Portal
- targetAppKey: app-example-service-portal-dev
- targetAppType: WebApplication
- evidenceSource: cached
- freshness: stale
- fetched_at: 2026-06-28T09:00:00Z
- freshness_probe: app_list(limit=1) total changed from cached total
- reusableAssets:
  - Unknown until tenant evidence is refreshed
- candidateIntegrations:
  - Unknown until tenant evidence is refreshed
- candidateAgents:
  - Unknown until tenant evidence is refreshed
- candidateLibraries:
  - Unknown until tenant evidence is refreshed
- perAppDeepDiveNeeded: yes
- unknowns:
  - target app identity must be refreshed before a confident app-targeted prompt
```

## Target App Resolution Gate

Before emitting a confident Mentor Studio prompt for an existing app or app
shell, verify the target app name, canonical app key, environment, and evidence
freshness. If multiple apps match, ask Paulo to choose the exact app. If the
evidence is stale, missing, or ambiguous, keep the prompt blocked and use
`Unknowns And Fallback Behavior`.

## Read-Only Boundary

Tenant Context Packet evidence is read-only discovery. It can improve target
selection and dependency naming, but it does not authorize `app_create`, does
not authorize `mentor_start`, does not authorize `publish_start`, and does not
authorize deploy, rollback, cleanup, or tenant mutation.

Any tenant-changing action still needs OMI's current explicit approval gate for
the readable target name, canonical id when known, environment, and exact
action.

## Change Mode Matrix

Keep OMI's operating mode explicit. Do not let evidence from one mode authorize
actions in another mode.

| Mode | Allowed work | Approval and artifact boundary |
|---|---|---|
| `prompt-only` | Produce Studio-native pseudocode, paste-ready prompts, audits, and unknowns. | No tenant-changing action. Evidence gaps stay in `Unknowns And Fallback Behavior`. |
| `read-only tenant discovery` | Use read-only inventory to build a Tenant Context Packet, dependency inventory, freshness labels, or advisory impact notes. | Does not authorize `app_create`, `mentor_start`, `publish_start`, deploy, rollback, cleanup, or tenant mutation. |
| `Mentor execution` | Send an approved prompt through Mentor for a named target. | Requires exact current approval for readable target name, canonical id when known, environment, action, and prompt. Record a project-local evidence artifact when the run matters for later decisions. |
| `publish/deploy handoff` | Prepare advisory readiness notes, deployment preview evidence, or publish handoff text. | Requires published source revision evidence before any safe-to-promote wording. ODC Portal impact analysis remains the decision boundary. |
| `tenant mutation` | Create apps, publish, deploy, rollback, cleanup, or change tenant configuration. | Requires exact current approval for the specific target and action. OMI must stop before mutation when approval is absent or ambiguous. |

When the user request moves between modes, restate the new mode and approval
boundary before acting. A Tenant Context Packet or reverse dependency summary is
never approval to change a tenant.

## Evidence Freshness Labels

Use one of these lines when tenant evidence materially affects output:

```text
Tenant evidence: live
Tenant evidence: cached, fetched_at=<timestamp>, freshness_probe=<probe>
Tenant evidence: stale, fetched_at=<timestamp>, freshness_probe=<probe>
```

In short, cached evidence can support asset identity and dependency inventory
when the freshness probe is acceptable for the request, but cached evidence must
not justify destructive or app-targeted execution by itself. Stale or missing
freshness evidence belongs in `Unknowns And Fallback Behavior` before any
confident Mentor Studio prompt.

## Scope Guard

For tenant-wide requests, produce tenant-only inventory first. In short, do not
auto-chain tenant -> every app -> Mentor. If the user asks for every app, all
apps, deep dives for the whole tenant, or implementation across many apps, ask
Paulo to select the exact apps or confirm the cost and scope before any per-app
deep dive or Mentor prompt work.

Use `perAppDeepDiveNeeded: yes` only as a routing signal. It is not approval to
inspect every app and it is not approval to mutate any app.

## Dependency Inventory Integration

Tenant-observed assets can be listed in OMI's dependency inventory as:

```text
Already exists (use existing): <asset type> <asset name> (<canonical id if available>)
```

Use this for asset identity only. Tenant architecture evidence can identify an
app, library, integration, agent, AI model connection, workflow, or other
tenant asset. It does not prove exact Studio internals such as screen
variables, widget tree, event order, local action names, aggregate names, data
action names, or button OnClick handlers.

For exact Studio internals, use `context_screens` or other app-specific
evidence required by the relevant OMI route. If the exact element cannot be
verified, use `Unknowns And Fallback Behavior`.

## Existing App Structure Evidence

Use this optional intake when Paulo supplies or approves read-only app
structure evidence before an app-targeted prompt. Examples include a reduced
app overview artifact, app documentation artifact, app architecture summary
artifact, architecture-style summary, or cached/live MCP context summary. Treat
the source as an implementation detail: OMI consumes the reduced facts, not the
producing tool, renderer, graph, report, cache path, or fixed data shape.

Reduce the evidence to this packet before using it:

```text
Existing App Structure Evidence
- appName:
- appKey:
- appType:
- revision:
- evidenceSource: live | cached | supplied-artifact
- freshness:
- fetched_at:
- freshness_probe:
- uiFlows:
- screens:
- actionsAndFunctions:
- entitiesAndStructures:
- roles:
- inheritedItems:
- dependencyHints:
- exactInternalsUnavailable:
- unknowns:
```

Optional source metadata fields are optional hints, not required schema:

```text
- sourceDescription:
- sourceRevisionDateTime:
- publicElements:
- staticEntitiesOrEnums:
- inheritedItemCount:
```

Copy these fields only when they are already present in a source artifact or
observed through read-only MCP context. Do not invent counts, public status,
enum/static-entity classification, or inherited/reference counts from naming
conventions.

Use one of these lines when existing app structure evidence materially affects
output:

```text
Existing app structure evidence: live
Existing app structure evidence: cached, fetched_at=<timestamp>, freshness_probe=<probe>
Existing app structure evidence: supplied-artifact, fetched_at=<timestamp>, freshness_probe=<probe>
Existing app structure evidence: stale, fetched_at=<timestamp>, freshness_probe=<probe>
```

Cached or supplied-artifact evidence may support orientation when its
freshness probe is acceptable for the request. Stale, missing, or ambiguous
evidence blocks confident app-targeted prompts naming current screens,
actions, entities, structures, roles, or dependencies. In that case, do not
emit a confident app-targeted prompt; move the gap to `Unknowns And Fallback
Behavior` and refresh with live MCP context before presenting current app
structure as confirmed.

### Search Engine Sandbox Reduced Example

In this repo's tests, the golden fixture for this compact example is
`tests/fixtures/existing_app_structure_evidence/search_engine_sandbox_reduced_packet.md`
from this skill root, or
`skills/outsystems-mentor-implementation/tests/fixtures/existing_app_structure_evidence/search_engine_sandbox_reduced_packet.md`
from the repo root.
Its curation note says the project-local evidence spec is provenance only and
is not a required source contract. The fixture path is test collateral, not an
OMI input requirement.

```text
Search Engine Sandbox Reduced Example

Existing App Structure Evidence
- appName: Search Engine Sandbox
- appKey: <example-app-key>
- appType: WebApplication
- revision: 241
- evidenceSource: live
- freshness: live MCP app and context snapshot fetched on 2026-06-30T16:10:27Z
- fetched_at: 2026-06-30T16:10:27Z
- freshness_probe: app_list, app_info, context_screens, context_actions, context_entities, context_structures, context_roles
- sourceDescription: Companion app for the Search Engine Connector Library; sends serialized DSL queries to a Search Engine endpoint and receives JSON responses.
- sourceRevisionDateTime: 2026-06-25T14:30:20.840175Z
- publicElements:
  - entity Allrecordings
- staticEntitiesOrEnums:
  - COUNTRY
  - QueryLists
  - ESMigrationBucketStatus
  - ESMigrationRunStatus
  - MigrationTemplate
- inheritedItemCount: unknown; inherited items were not exhaustively collected
- uiFlows: Common, MainFlow
- screens:
  - Common: Login, InvalidPermissions, RecoverPasswordReset, UserProfile, ChangePassword, RecoverPasswordRequest
  - MainFlow: Home, Setup, Reference, Search_Query, Search_Multiple, Search_Template, MigrationDashboard, MigrationProfiles, Index_GetList, Index_Create, Index_LoadData, Index_SetAlias, Avd_ReIndex, CRUD_Create, CRUD_Retrieve, CRUD_Update, CRUD_Delete, Adv_EmailSentLog, Adv_RealTimeIndexing, Adv_EscapeForJSON, Adv_TaskManagement, Adv_ChangeHistory, Adv_Dictionary
- actionsAndFunctions:
  - ServerAction InitTimerIndexBLRM
  - ServerAction SaveQueryToHistory
  - ServerAction FormatResultDetailsForDisplay
  - ServerAction SetRealTimeIndexingModeForMigration
  - ServerAction ExecuteKillSwitch
  - ServerAction StoreFunctionScore
  - ClientAction DoLogin
- entitiesAndStructures:
  - entity QueryHistory
  - entity Allrecordings
  - entity ESMigrationRun
  - entity ESMigrationBucket
  - entity ESMigrationProfile
  - structure SandboxElasticOperationResult
  - structure SandboxElasticBulkItemError
  - structure BulkIndexResult
- roles:
  - SearchEngineSandbox (<example-role-key>)
- inheritedItems:
  - Unknown; not exhaustively collected in this compact packet
- dependencyHints:
  - Search Engine Connector Library
  - Search Engine endpoint
  - Elasticsearch/ES query, index, template, alias, bulk load, migration, and task operations
  - ElasticSearchConnector.StoreFunctionScoreScript
- exactInternalsUnavailable:
  - widget trees
  - widget IDs
  - local variables
  - event order
  - aggregate names
  - Data Action internals
  - button handlers
  - per-screen role assignments
  - action behavior beyond names, descriptions, parameters, and action type
  - return value semantics and error paths
- unknowns:
  - Full inherited item inventory was not exhaustively collected.
  - Full action list was not expanded in this reduced packet.
  - Exact UI layout and interaction internals are not available from this packet.
  - No Mentor/publish/deploy/rollback/cleanup/tenant mutation is authorized by this packet.

Dependency inventory examples:
- Already exists (use existing): screen Search_Query
- Already exists (use existing): screen MigrationDashboard
- Already exists (use existing): entity QueryHistory
- Already exists (use existing): entity ESMigrationRun
- Already exists (use existing): structure SandboxElasticOperationResult
- Already exists (use existing): role SearchEngineSandbox (<example-role-key>)
```

For a prompt or handoff summary, the same app can be referenced compactly as:
Search Engine Sandbox, app key <example-app-key>,
revision: 241.

Use this packet as read-only orientation evidence for target grounding,
named-element confidence, dependency inventory, and unknowns. Observed screens,
actions, functions, entities, structures, roles, inherited items, and dependency
hints may be listed in OMI's dependency inventory as:

```text
Already exists (use existing): <asset type> <asset name> (<canonical id if available>)
```

This packet does not prove exact Studio internals, including widget trees,
widget IDs, local variables, event order, aggregate names, Data Action
internals, button OnClick handlers, role assignments, action behavior, return
values, or error paths. Exact internals require app-specific evidence such as
`context_screens` for named screen targeting.

This packet does not replace current official docs and
`outsystems-tech-content` for Studio syntax, function signatures, widget rules,
TrueChange messages, or product-contract claims.

Architecture-style summaries can improve target grounding, named-element
confidence, dependency inventory, library and AI model connection dependency
hints, and unknowns, but they remain read-only orientation evidence and this
evidence does not infer per-screen roles.

This is a generic OMI intake. It does not require a sibling architecture or
documentation skill, does not require a graph, HTML report, script,
client-specific cache path, fixed filename, or fixed JSON shape, and does not
require any sibling skill installed. Cache reuse must be expressed through the
evidence freshness fields rather than client-specific paths.

No per-screen role inference from screen lists, `isPublic`, app role names, or
overview tables. Keep roles as a flat observed list unless explicit role access
evidence is available.

## Named Element Confidence Gate

Use this gate when OMI output names an existing Screen, Action, Entity,
Aggregate, Data Action, Role, Web Block, dependency, library, integration,
agent, AI model connection, workflow, or shared component.

Tag each named element with one confidence source before using it in a
confident paste-ready instruction:

| Source | Meaning | Allowed use |
|---|---|---|
| `observed` | App-specific evidence exposes the exact element name, such as `context_screens`, approved live Mentor output, snapshot evidence, or another current app-specific source. | May be used in a confident paste-ready instruction. |
| `tenant-inventory` | Tenant evidence identifies the asset or dependency, but not exact Studio internals. | May support target identity, dependency inventory, and scope control only. |
| `official-docs` | Current OutSystems docs or implementation authority confirms a platform element, pattern, or API. | May support platform guidance, not app-specific element existence. |
| `inferred` | The name is derived from a label, convention, PRD, visual source, or generated assumption. | Keep as a review note or substitution note, not confirmed Studio structure. |
| `unverified` | The current evidence cannot confirm the element. | Move to `Unknowns And Fallback Behavior` before paste-ready output. |

Only `observed` app-specific names, or platform names backed by `official-docs`,
can appear as confident paste-ready references to existing Studio structure.
Tenant inventory can say an asset exists; it does not prove local variables,
screen actions, aggregates, data actions, widget IDs, role mappings, or exact
event wiring.

If any required existing element is `inferred` or `unverified`, do not emit a
confident paste-ready instruction for that element. Add a substitution note or
ask Paulo for current app-specific evidence.

## Optional Reverse Dependency Evidence

Use optional reverse dependency evidence only when OMI needs to answer "who
uses this shared asset?" before changing, reusing, or targeting a shared
library, agent, integration, connection, service, or component.

Keep this evidence reduced and client-neutral. OMI may consume a compact
summary with only these fields:

```text
- producer asset key
- producer asset name
- producer asset type
- evidenceSource: live | cached
- fetched_at
- freshness_probe
- consumers:
  - consumer asset key
  - consumer asset name
  - consumer asset type
  - used revision
  - revision gap
- coverage notes
```

Integrate the producer in OMI's dependency inventory as:

```text
Already exists (use existing): <asset type> <asset name> (<canonical id if available>)
```

Then summarize consumer count, stale references, failed or unanalyzed consumer
coverage, and unknown freshness in `Unknowns And Fallback Behavior` or
`Optional Constraints`.

Use reverse dependency evidence as a scope brake. If a shared producer has many
consumers, stale references, failed coverage, or unknown freshness, do not emit
a confident Mentor Studio prompt that changes producer behavior until Paulo
chooses the compatibility strategy, target consumers, or bounded app scope.

## Shared Producer Compatibility Gate

When optional reverse dependency evidence shows that a shared producer has many
consumers, stale references, failed coverage, unknown freshness, or a material
revision gap, require Paulo to choose a compatibility strategy before OMI emits
a confident Mentor Studio prompt that changes producer behavior.

Allowed compatibility strategies:

- `additive wrapper` - add a new wrapper action/block/output while preserving the
  existing producer contract.
- `versioned Service Action` - add or route through a versioned public action
  when consumers need staged adoption.
- `consumer migration` - name the target consumers and migration order before
  changing the producer contract.
- `bounded single-app scope` - avoid changing the producer and implement the
  behavior in one named consuming app.

If no compatibility strategy is selected, keep the producer change in `Unknowns
And Fallback Behavior`. OMI may still produce prompt-only consumer-local work
when the bounded app scope is clear.

In short, do not perform a tenant-wide scan unless Paulo explicitly confirms
scope and cost after the actual candidate count is known. Reuse generic
freshness, timeout, partial coverage, and large-payload discipline, but OMI
does not require a sibling skill, does not require an HTML report, and does
not require scripts, cache paths, or fixed JSON filenames.

Reverse dependency evidence identifies shared-asset blast-radius risk only. It
does not prove exact Studio internals such as screen variables, widget trees,
event order, local action names, aggregate names, data action names, or button
OnClick handlers. It also does not approve publish, deploy, promotion, or
safety to promote.

## Large Payload Discipline

In short, do not read full tenant or app inventory payloads into model context.
If a tool returns a large payload or saves output to disk, reduce to the packet
fields with a compact field whitelist or pass the path through a script/tool
that emits only the needed summary.

The compact field whitelist for tenant context is:

```text
asset key/id
asset name
asset type
environment key/name when available
modified or fetched timestamp when available
dependency or reusable asset names when already present in reduced evidence
```

## Client-Neutral Cache Discipline

OMI guidance must be Codex-safe and use client-neutral cache discipline. A
cache may be used only as an implementation detail of the current client or MCP
wrapper, and the output must label freshness through the Tenant Context Packet.

Environment cache reuse is allowed when the current client can prove freshness,
but it stays an optimization and not a product-contract claim.

Do not copy `~/.claude/cache`. Do not copy Claude Code harness auto-save
assumptions. Do not require AskUserQuestion. Express cache behavior as
client-neutral freshness evidence instead.

## MCP Quirk Guardrails

- `context_*` calls must use `limit <= 100`.
- The `context_*` lookups index by visibility, not ownership: app-scoped
  queries return owned rows plus rows inherited from referenced libraries
  (OutSystemsUI, Charts, etc.), and each row carries `isReferenced` and
  `producerAssetKey`/`producerAssetName`.
- `owned_only` defaults to `true` when `app` is set and `false` tenant-wide,
  so pass `owned_only: false` with `app` to keep inherited rows. In short: an
  existing-app inventory built with defaults silently omits inherited
  elements.
- `app_refs` can time out on large apps; avoid it unless the route truly needs
  dependency detail and the result can be cached or reduced.
- In short, do not run more than two `app_refs` calls in parallel.
- `deploy_impact` is not a hard readiness gate until current tool behavior is
  revalidated for the active tenant.
- `context_screens` does not expose per-screen role assignments. It may expose
  `isPublic`, but OMI must not infer Accessible by roles, and must not
  cross-product roles and screens. In short: do not infer Accessible by roles,
  and do not cross-product roles and screens.

## Role/Security Evidence Gate

Role and access-control claims require explicit role evidence. `context_screens`
may expose screen names and sometimes `isPublic`, but OMI must not infer role
assignments, screen access, action access, or data access from screen inventory
alone.

Use explicit role evidence such as a reviewed specification, app-specific role
inventory, verified Studio evidence, approved live Mentor evidence, or current
official OutSystems role guidance. If role evidence is absent, mark role
assignments as unknown and use `Unknowns And Fallback Behavior`.

Do not cross-product roles and screens. Do not convert `isPublic=false` into a
list of Accessible by roles. Do not claim that a screen, action, or data path is
role-protected unless the role mapping is explicitly observed or specified.

## Demo Warmup

For demo readiness and demo warmup, prewarm tenant inventory before the live
demo when tenant context will be shown or used for target selection. In short,
do not run a first-time tenant scan during a live demo unless Paulo accepts the
delay.

The warmed packet may make target selection faster, but it does not expand
approval for Mentor execution, publish, deploy, rollback, cleanup, or tenant
mutation.

## Optional Read-Only Smoke Test

Use this only when Paulo explicitly asks to validate current tenant context
behavior. Keep it read-only and stop before any Mentor or tenant-changing
operation.

Read-only tools only:

```text
1. auth_status
2. app_list with a narrow name search or a small page
3. app_info for the selected app only
```

The smoke-test output is a Tenant Context Packet plus an evidence label. It is
not a live Mentor campaign, not a publish readiness gate, and not proof of exact
Studio internals.

No Mentor, publish, deploy, rollback, cleanup, or tenant mutation is allowed in
this smoke test.
