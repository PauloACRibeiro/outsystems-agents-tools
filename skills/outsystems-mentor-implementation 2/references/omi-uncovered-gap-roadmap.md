# OMI Uncovered Gap Roadmap

Use this reference when a request asks what OMI has not yet proven, when a user asks for production-grade confidence, or when an implementation path touches lifecycle or runtime capabilities that OMI1 through OMI4 did not execute end to end.

This roadmap does not authorize tenant mutation. It turns uncovered areas into explicit evidence gates, read-only advisory routes, or `Unverified gap` outcomes.

## Core Rule

Do not infer production-grade readiness from OMI campaign coverage. OMI may provide controlled internal sharing guidance, read-only review prompts, and bounded Development evidence, but unsupported areas require explicit current approval and fresh proof before action.

If the required evidence is missing, say `Unverified gap`, name the missing proof, and keep the answer review-only or advisory. Do not infer hidden Studio internals, runtime behavior, Test/Production safety, rollback support, external-library lifecycle safety, or authenticated behavior from nearby evidence.

## Gap Families

### Promotion and environment lifecycle

OMI has not proven a complete Test or Production promotion path. Promotion readiness requires current source revision proof, target environment identity, ODC Portal impact analysis, blocker/warning review, rollback posture, and explicit current approval.

Default response shape: read-only advisory. Do not mutate Test or Production until explicit current approval and fresh proof exist.

### Rollback rehearsal

OMI has not proven successful rollback rehearsal. Rollback readiness requires current app, environment, revision, build, deployment, deployment history, rollback tool support, preservation or intentional removal of evidence markers, and explicit current approval.

When safe rollback support is not proven, use `rollback-unavailable` instead of inventing a recovery path.

### Application lifecycle and release packaging

OMI has not broadly proven app creation, app deletion, destructive cleanup, package creation, PR creation, push/release workflows, source download, or external-library upload/publish. These are lifecycle actions, not normal prompt output.

Default boundary: do not deploy, promote, rollback, delete, clean up, package, push, upload, publish external libraries, or download source without explicit current approval naming the exact target and action.

### Authenticated runtime journeys

OMI has not proven broad role-specific or authenticated-only runtime journeys. Runtime inspection of login-protected routes requires approved credentials/session context, approved routes, secret-safe browser handling, role expectations, settled final URL, visible state, console/runtime summary, and explicit exclusions for login-only, no-default-entry, blank, Common-only, and route-mismatched outcomes.

Default response shape: review-only or degraded visual evidence unless the authenticated route is safely inspected.

### Complex refactors and non-trivial live logic

OMI has not proven broad refactors such as multi-screen transactional workflows, entity migrations, large dependency rewiring, shared producer behavior changes, or high-risk data changes. Use split proof/edit, blast-radius evidence, dependency evidence, rollback posture, and explicit stop conditions.

Default response shape: plan, proof-only inspection, or `Unverified gap`; do not run speculative Mentor edits.

Planned closure: OMI5 campaign prep at `docs/superpowers/plans/2026-07-04-omi5-datagrid-refactor-live-campaign.md` (repo-level; prep only, execution needs explicit current approval).

### Data Grid wiring and persistence

OMI has not proven full Data Grid setup, dependency wiring, changed-row persistence, save actions, validation behavior, or concurrent edit behavior. OMI4 proved a narrow event-message edit, not full Data Grid implementation.

Required proof includes Data Grid dependency, grid block, data source, fetch boundary, save boundary, validation behavior, event handlers, and runtime persistence evidence when claiming working behavior.

Planned closure: OMI5 campaign prep at `docs/superpowers/plans/2026-07-04-omi5-datagrid-refactor-live-campaign.md` (repo-level; prep only, execution needs explicit current approval).

### Workflow, event, timer, and async depth

OMI has not proven full workflow lifecycle, event producer/consumer behavior, timer execution under load, retry/wake behavior, idempotency under concurrency, or distributed transaction behavior. Do not trigger timers, execute indexing, publish workflows, or mutate async state unless explicitly approved.

### Agent, A2A, MCP tool, evaluation, and mobile runtime depth

OMI has not proven actual agent execution, Portal guardrail configuration, A2A messaging, imported MCP tool execution, model migration, evaluation dataset runs, mobile device execution, offline/sync behavior, or native capability testing.

Default response shape: current docs plus target proof for asset identity; no runtime claim unless the runtime or evaluation was actually executed and recorded.

### External Logic and external-library lifecycle

OMI has not proven external-library build, upload, publish, source download, versioning, binary compatibility, dependency blast-radius testing, or rollback with real external binaries. Existing call-site proof is not equivalent to library lifecycle proof.

Default response shape: route to an approved external-library/custom-code workflow when available; otherwise keep OMI output advisory unless that lifecycle is explicitly approved.

### Performance, load, resilience, and security execution

OMI review prompts are not executed load tests, security probes, concurrency tests, chaos tests, or resilience drills. Claim execution only when the named test or tool was actually run and evidence was recorded.

Default response shape: checklist, test plan, or review prompt with `Unverified gap` for unexecuted runtime claims.

### MCP blind spots and Studio visual escalation

OMI has not solved MCP/context blindness for hidden Studio branches, widget internals, action nodes, or model APIs. Use Studio visual proof or runtime proof as bounded evidence for visible details. Do not infer hidden branches or unrelated nodes.

If Mentor repeats unsupported model introspection or cannot identify the exact edit point, stop with no change.

### Colleague portability boundary

OMI is suitable for controlled internal sharing when local tests and reusable docs pass, but it is not automatically a public, environment-independent package. If a colleague lacks required internal documentation, MCP access, local mirrors, or tenant permissions, label the route degraded or blocked.

## Output Contract

For uncovered-gap questions, answer in this order:

1. `Covered by OMI1-4`
2. `Still Unproven`
3. `Required Evidence Before Action`
4. `Allowed Output Now`

Use `Unverified gap` for any production-grade, runtime, lifecycle, or security claim that lacks current evidence.
