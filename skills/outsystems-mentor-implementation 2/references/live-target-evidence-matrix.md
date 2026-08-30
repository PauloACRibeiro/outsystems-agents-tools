# Live Target Evidence Matrix

Use this reference when an `outsystems-mentor-implementation` answer depends on
current target suitability rather than only generic OutSystems documentation.
It converts OMI3 campaign lessons into reusable evidence gates before confident
Mentor Studio prompts, Studio-native pseudocode, live validation claims, visual
inspection claims, or rollback readiness claims.

This file does not authorize tenant-changing work. It is a read-only evidence
and response-shape source owner. Approval for `mentor_start`, `publish_start`,
`deploy_start`, rollback, `app_create`, cleanup, promotion, external-library
mutation, package, push, or PR remains outside this file.

## Core Rule

Do not infer implementation-grade behavior from nearby evidence. If the exact
target facts are missing, label the claim `Unverified gap`, ask for the missing
contract or target proof, and avoid a confident paste-ready Mentor Studio
prompt for that claim.

## Evidence Classes

| Evidence class | Use it for | Boundary |
|---|---|---|
| Current MCP/context evidence | App identity, revision, environment, references, screens, actions, entities, roles, and deployment facts exposed by direct tools. | It does not prove exact Studio widget trees, hidden action branches, or REST method internals unless those details are present in the returned facts. |
| Current official OutSystems documentation | Product-contract behavior, platform limits, REST, Data Grid, rollback, agentic, timer, event, workflow, and security claims. | It does not prove a named tenant app currently implements the documented feature. |
| Screenshot-backed Studio evidence | Visible Studio tree, visible method, visible branch, visible request/response member, visible property, or visible implementation flow. | It proves only the visible branch, visible method, visible screen, timestamp, and approved fixture scope. It is not a broad product-contract claim and does not prove hidden branches or every method. |
| Studio-proven hidden layer | Hidden Studio implementation details that are visible in a screenshot or live ODC Studio session but absent from MCP/context facts. | It is first-class bounded evidence for that exact visible node only; keep the result as visible proof only and do not turn it into a broad product-contract claim. |
| Runtime visual evidence | Settled browser route, visible page content, screenshot, URL, viewport, console/runtime summary, and degraded-state exclusions. | It proves only the inspected route, viewport/session, timestamp, and runtime state. It does not prove Studio internals. |
| Dependency-chain evidence | A target depends on a producer or library through one or more observed references. | It can support routing or accepted-risk wording, but it is not the same as direct method usage, direct ExternalLibrary usage, or direct REST binding proof. |

## Scenario Matrix

| Scenario | Required target proof before confident output | Not enough by itself | Response when missing |
|---|---|---|---|
| Exposed REST API or API-integrated logic | Exact exposed REST API name, method name, request/response structures, headers, auth behavior, timeout and retry assumptions, and error mapping. Current MCP/context evidence, official docs plus supplied API contract, or screenshot-backed Studio evidence can satisfy the row when bounded. | Public Service Actions, API-looking action names, generic REST docs, entity references, or `app_refs` alone. | Mark API placement, payload, headers, auth, timeout, retry, and error mapping as `Unverified gap`; ask for the API contract or Studio/context proof. |
| Consumed REST or producer/consumer API binding | Exact consumed REST API, base URL, OpenAPI/source contract when available, visible methods, method calls in implementation logic, producer identity, and consumer identity. | Producer dependency, public Service Actions, entity references, runtime degradation, or `app_refs` alone. Nearby facts are not enough; do not infer consumed REST binding from Service Actions or entity references. | Block or degrade producer/API binding proof; ask for direct binding evidence or a screenshot-backed Studio view of Logic > Integrations > REST. |
| Data Grid deep case | `OutSystemsDataGrid` dependency, named user-facing screen in `MainFlow`, runtime route that renders grid content, data source shape, refresh boundary, save boundary, validation behavior, and event boundaries. | Deep entities/actions, a generic table, a catalog route, or Data Grid docs alone. | Ask for a target with verified Data Grid dependency and visible grid route, or return review-only guidance with `Unverified gap` for grid internals. |
| Complex refactor or non-trivial live logic | Exact target elements, dependency graph or blast-radius evidence, data ownership, transaction boundary, rollback posture, test strategy, and proof/edit split. | A broad PRD, app name, generated summary, or nearby entity/action evidence. | Use `Unverified gap` or produce a plan/review-only output until the exact blast-radius evidence and approved target are available. |
| Data Grid wiring and persistence | Data Grid dependency, grid block, data source, fetch boundary, changed-row persistence, save action, validation behavior, event handler inputs, and runtime persistence proof when claiming working behavior. | A visible table, a Data Grid doc link, a narrow event-message edit, or data source evidence alone. | Keep output advisory or ask for exact grid wiring proof; do not claim persistence until save behavior is proven. |
| Workflow, event, timer, and async depth | Exact workflow/event/timer/async asset, event producer, event consumer, retry/wake behavior, idempotency boundary, commit/status behavior, and approved execution boundary. | A timer action name, generic async docs, or one idempotency guard. | Do not trigger timers, events, indexing, or background work unless approved. Use `Unverified gap` for unexecuted behavior. |
| External Logic and external-library lifecycle | Current External Logic call-site proof, external-library package identity, version, external-library upload and publish boundary, source download boundary, binary compatibility, dependency blast radius, and rollback posture. | Existing call-site proof, dependency reference, or generic custom-code docs alone. | Route lifecycle work to the external-library/custom-code workflow; keep OMI advisory unless upload, publish, or source download is explicitly approved. |
| Agentic, AI model, External Logic, timer, event, or workflow | Named-app claims require direct evidence of the current target asset type: agent context, AI model connection, `ExternalLibrary` reference, callable external logic action, timer action, event action, or workflow action. Current official docs may ground only generic product-contract behavior or pattern shape for the exact pattern. | App names, generic agentic docs, product documentation alone, indirect dependency-chain evidence, or integration-looking actions alone. Documentation does not prove a named target currently uses the asset. | If proof is missing, hand off or block the confident implementation path until direct target proof exists. Dependency-chain evidence may be recorded as such, but do not claim direct usage. |
| Studio-proven hidden layer | Use screenshot-backed or live ODC Studio visual proof when MCP context cannot expose the exact hidden layer. Accept only visible app identity, visible screen/action/API tree path, selected element, method/action name, parameter mappings, branch condition, Message expression, or implementation flow. Common OMI examples include a screen action, Data Grid event handler, External Logic call site, timer branch, consumed REST call node, and exposed REST implementation branch. | A dependency reference, action name search, generic docs, or a screenshot that does not show the selected tree path and visible node details. | Treat the visible proof as first-class bounded evidence for that exact hidden layer. State `visible proof only`; do not claim hidden branches, other methods, unrelated nodes, or broad product-contract behavior. |
| Agent or mobile asset type | Prove the current asset type before asserting runtime facts. For an Agent asset, use app/asset catalog proof plus `context_agents`, agent actions, model connection, or public agent service action proof. For a `MobileApplication`, use app catalog proof plus mobile screens/actions/entities and framework/dependency evidence. | Assuming a normal deployed web route, runtime URL, or deployment key for non-web assets. `env_apps` returning no deployed web-app row can be expected for an Agent asset or mobile asset and is not contrary proof by itself. | For Agent asset and `MobileApplication` targets, state `no runtime URL asserted` when the evidence proves no web runtime URL should be claimed. Use read-only completion when the row is about guardrail coverage or framework boundary and no mutation is needed. |
| Agent, A2A, MCP tool, evaluation, and mobile runtime depth | Exact asset type, model or agent connection, guardrail configuration evidence when claimed, A2A or MCP tool contract, evaluation dataset and run evidence when claimed, mobile framework, device/runtime target, offline/sync boundary, approved runtime/evaluation boundary, and secret-safe execution path. | Asset identity, guardrail docs, a mobile app catalog row, or generated prompt output alone. | Keep output as docs-grounded advisory or target-proof summary until runtime execution or evaluation evidence exists. Do not execute agent, mobile, MCP-tool, evaluation, Studio, or runtime proof collection unless explicitly approved. |
| MCP blind spot escalation | Exact hidden layer that MCP/context cannot expose, bounded Studio visual proof or runtime proof, selected element/path, visible node details, sanitized evidence, explicit exclusions, and explicit approval before Studio/runtime proof collection. | Broad context search, dependency references, action inventory, or Mentor speculation. | Escalate to approved Studio visual proof, approved runtime proof, or `Unverified gap`; do not infer hidden internals or collect active proof without approval. |
| Runtime visual inspection | Settled final URL, approved route, page title/body, screenshot, viewport, visible baseline/marker when relevant, console/runtime summary, and degraded-state exclusions. Runtime proof is strongest when context proof is blind but the row can be safely observed through a Development URL. Record the requested URL, final URL, visible content or event message, screenshot path, console summary, and explicit exclusions for login-only, no-default-entry, blank, Common-only, and route-mismatched states. | First paint only, login redirect, no-default-entry page, blank page, Common-only auth/profile/password-recovery flow, route mismatch, or uninspected console errors. | Record degraded evidence or block the visual claim. Do not pass visual proof until login-only, no-default-entry, blank, Common-only, and route-mismatched states are excluded. |
| Authenticated runtime journey | approved credentials/session context, approved Development route, expected role or permission state, role expectations, settled final URL, visible page state, browser console/runtime summary, secret-safe browser handling, and explicit exclusions for login-only, no-default-entry, blank, Common-only, route-mismatched, and wrong-role outcomes. | A runtime URL, a login page, a prior manual claim, unauthenticated screenshot, or successful publish alone. | Mark visual evidence degraded or use `Unverified gap`; do not claim authenticated behavior until the approved role-specific path is inspected without exposing secrets. |
| Performance, load, resilience, and security execution | Named tool or test command, approved target, test inputs, execution timestamp, sanitized result summary, and pass/fail criteria for a load test, security probe, concurrency test, resilience drill, or failover exercise. | A review checklist, Mentor summary, static analysis prompt, or architecture note. These are not executed evidence. | Label unexecuted runtime claims `Unverified gap` or `not executed evidence`; offer a test plan or checklist unless execution is separately approved. |
| No-default-entry repair | Verified non-empty target, current revision/build/deployment, separate exact approval, and either a verified existing `MainFlow` user screen for default-screen repair or an approved default-entry bootstrap that names the `MainFlow` screen, baseline text, default route, publish boundary, and reinspection boundary, and does not recreate Common/template assets. | Common authentication, invalid-permissions, profile, password-recovery screens, a target with no user screen and no approved bootstrap, claims that the bootstrap recreated Common/template assets, or claims product-template equivalence. | Block the repair until a `MainFlow` user screen exists or the user approves a separate screen creation/scaffold step. If approved, keep the bootstrap minimal and record that it solves runtime entry only, not product-template equivalence. |
| Screenshot-backed Studio supplement | Use local screenshot inspection with app/screen/action context, visible tree path, visible request/response members or method calls, and sanitized evidence report. | Screenshot text that does not show the relevant tree/method/flow, or screenshot-only evidence used for unrelated product-contract claims. | Accept only the bounded visible proof. State what is visible and what remains unproven, including hidden branches and other REST methods. |
| Publish advisory | Treat `no_changes_detected=true`, revision-only movement, or publish metadata without independent inspection as advisory evidence. | A successful publish operation, a revision number, or a clean-looking publish status without post-publish proof. | Record `publish advisory`; do not use it as proof by itself. Require post-publish proof or classify the row as blocked/not deployed when proof is absent. |
| Rollback rehearsal or rollback readiness | Current exact app/environment/revision/build/deployment, deployment history that proves a safe target, current rollback tool support, explicit approval, and evidence that rollback will preserve or intentionally revert the approved marker/repair state. | Rollback tool visibility, old deployment names, generic rollback docs, or a successful publish alone. | When exact safe rollback is not proven, use terminal `rollback-unavailable`; do not call rollback if it may remove approved evidence, if it cannot preserve evidence for an approved marker or repair, or if the operation key/support is uncertain. |

## Protected Contract Checklist

For REST, consumed REST, External Logic, Data Grid, timer, and integration
edits, list protected surfaces before any edit prompt. Use the Protected
contract checklist as a preservation boundary, not as permission to mutate
unproven surfaces.

REST and consumed REST protected surfaces:

- REST API name.
- method name.
- base URL.
- method URL.
- HTTP method.
- request parameters and types.
- request body type.
- response body type.
- response headers.
- authentication, including custom authentication and authentication callbacks.
- producer app.
- consumer app.
- existing mappings.
- unrelated methods and integrations.

Data Grid protected surfaces:

- Grid block name.
- Source block or dependency.
- Data source variable or data action.
- Fetch/refresh boundary.
- Save boundary.
- Validation boundary.
- Data Grid event handler name and inputs.
- Existing screen layout outside the approved edit.

Timer and background-flow protected surfaces:

- Timer or action name.
- Early guard location.
- No-work/idempotency timer branch.
- Existing valid-work path.
- External Logic call site or external connector calls.
- Commit/retry/status behavior.
- Entities and statuses used for progress tracking.

If a protected surface cannot be proven, either stop or mark it as an
`Unverified gap`; do not silently let Mentor rewrite it.

## Output Discipline

When target proof is present, include an `Evidence Status` or equivalent note
that names the proof type, freshness, and boundary.

When target proof is missing, use this shape:

```text
Evidence Status: Unverified gap
The current evidence does not prove <specific target fact>. I can provide
review-only guidance, but I should not emit a confident Mentor Studio prompt
for <specific behavior> until <specific missing proof> is supplied or verified.
```

When screenshot-backed Studio evidence is used, include:

- inspected artifact path
- visible app/screen/action context
- visible tree path or selected element
- exact visible members/methods/branches
- sanitized source boundary
- statement that hidden branches or other methods are not claimed

When visual runtime evidence is used, include:

- requested URL and final URL
- viewport
- screenshot/report path
- visible baseline/marker or target content
- console/runtime summary
- explicit result for login-only, no-default-entry, blank, Common-only, and
  route-mismatched exclusions

## No-Default-Entry Repair Boundaries

If browser/runtime inspection reports `This application does not contain a
default entry`, route it as a no-default-entry repair for the app's default
start screen; classify empty-app accepted risk separately from a non-empty app
that needs a verified Default Screen. A valid repair target must be a verified
MainFlow user screen, not a `Common` authentication, permission, profile, or
password-recovery screen. If no MainFlow user screen exists, use the `minimal
MainFlow > Home default-entry bootstrap` only after the user approves a separate
scaffold/create-screen step; otherwise block and ask for manual Studio screen
creation or explicit bootstrap approval.

## Reusable Documentation Hygiene

Keep reusable skill guidance generic. Campaign app names, tenant hostnames,
environment keys, app keys, screenshots, and row-specific proof belong in
campaign artifacts. This matrix may refer to OMI3 as provenance, but it must
not embed tenant-specific target names or identifiers.
