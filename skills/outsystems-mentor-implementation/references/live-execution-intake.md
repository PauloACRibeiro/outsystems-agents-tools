# Live Execution Intake

Use this reference as the global OMI source owner for deciding whether a
deterministic-quality claim needs live OutSystems MCP validation. It governs the
need decision, read-only evidence pass, explicit approval gates, degraded manual
fallbacks, and safe evidence capture before any live tenant action is even
considered.

## Entry Ownership

This file is the single entry point for live execution questions. Open
`live-target-evidence-matrix.md` only for target suitability proof and
`live-mentor-campaign-guidance.md` only for campaign mechanics, when a
section of this file routes you there.

## Decision Rule

Static docs, tests, and Claude review are first. Live OutSystems MCP validation
is needed only when a deterministic-quality claim depends on current
tenant/tool behavior that docs and tests cannot prove.

If the change is documentation-only, tests prove the local contract, current
OutSystems docs prove the product-contract claim, and Claude review finds no
tenant-behavior gap, do not create a live-validation decision artifact. Record
`Live MCP validation not needed` in the execution notes with the static
evidence instead.

Boundary phrase: no publish or deploy by default. Live validation is evidence
collection and does not authorize Mentor execution, app creation,
external-library upload, publish, deploy, rollback, promotion, cleanup, or any
other tenant mutation.

## Read-Only Resolution Pass

Start every possible live validation route with a read-only resolution pass.
Use direct OutSystems MCP tools first when they are available, and collect only
facts needed to resolve the remaining claim.

Read-only resolution can collect:

- `app_info` for current app identity, readable app name, canonical app key, and
  app-level metadata.
- `env_app` for environment identity, deployed app presence, runtime URL when
  relevant, and current environment app facts.
- Revision/build facts needed to distinguish current-state baseline from a
  published change.
- Dependency lookup facts needed to confirm existing producer, consumer,
  library, or connector identity.
- Tenant-observed warnings/errors only when the remaining deterministic-quality
  claim depends on those warnings/errors.

The read-only resolution pass must not write files that contain secrets, must
not call tenant-changing tools, and must not transform a read-only lookup into
approval for a later action.

Fresh-app context-indexing lag: Context Service tools (`context_screens`,
`context_actions`, `context_entities`) may not expose owned rows for a freshly
created or just-published app (tenant-observed, OMI2 fixture campaign,
2026-06-24). Treat a zero-row context result for a just-created target as
possible indexing lag, not proof of absence: perform one bounded re-check
after a short wait, or route the remaining claim through the approved
visual/runtime proof path. Label evidence collected under this condition as
degraded until a later context read or independent proof confirms it.

### Broad Metadata Noise Policy

Broad reference or dependency calls such as `app_refs` are supporting evidence
unless the row explicitly depends on dependency/reference proof.

On broad metadata errors such as CloudFront HTTP 504 or Context Service HTTP
500:

1. Retry once after a short pause.
2. If the retry also fails, record `degraded supporting evidence`.
3. Switch to narrower row-specific proof such as `env_app`, `app_info`,
   `app_revisions`, `context_screens`, `context_actions`, `context_entities`,
   `context_roles`, focused `context_search`, Studio visual proof, or runtime
   proof.
4. Continue only if mandatory row-specific proof is available through another
   approved non-secret source.

Do not keep repeating broad metadata calls after the bounded retry. Do not mark
a row blocked solely because broad metadata failed unless the missing
dependency/reference proof is row-critical and cannot be proven another
approved way. The bounded rule is: retry once, then degrade.

## Live Campaign Execution Context Preflight

For a live Mentor campaign row, direct tool availability must be proven in the
same execution context that will run the live row; configuration alone is not
enough: a local MCP registration, cached login, or another agent surface does
not prove that the row runner can call the needed OutSystems tenant tools.

Before any live campaign row uses tenant facts or runs a tenant-changing action,
record fresh evidence that:

- `auth_status` is callable in the row runner and returns `logged_in true`.
- The authenticated tenant matches the intended tenant for the approved row.
- The row runner exposes the minimum live-campaign tool set needed for the
  approved scope.
- The target app/environment identity was resolved in the same runner before
  the row proceeded.

Minimum live-campaign tool set for broad OMI live execution:

- App facts: `app_info`, `app_refs`, `app_revisions`.
- Context facts: `context_screens`, `context_actions`, `context_entities`,
  `context_roles`.
- Environment facts: `env_list`, `env_app`.
- Mentor execution (session-based, measured 2026-09-02): `mentor_start_session`,
  `mentor_load_asset` / `mentor_create_asset`, `mentor_prompt`,
  `mentor_get_run`, `mentor_cancel_prompt`, `mentor_close_session`. The
  pre-2026-09 `mentor_start` / `mentor_cancel` are no longer exposed.
- Publish execution: `mentor_publish`, `publish_status`, `publish_logs`. The
  gateway `publish_start` is no longer exposed; pass `mentor_publish`'s
  returned `publicationKey` to `publish_status` as `publish_key`.
- Deploy observation: `deploy_status`, `deploy_messages`.
- Rollback execution, only for explicitly approved rollback rows:
  `deploy_rollback`.

If a row needs only a narrower read-only subset, document the subset and why the
missing tools are outside that row's approved scope. If the approved row needs a
missing tool, do not start the live campaign row; mark it
`blocked-tool-unavailable` or ask the user for a different approved execution
route.

When the runner is Codex CLI or Codex Desktop, acceptable preflight evidence can
include `codex mcp get outsystems`, `codex mcp list`, and a fresh session where
the relevant `mcp__outsystems__*` tools are visible and `auth_status` succeeds.
The decisive proof is still the callable tool surface in the same execution
context that will run the row.

If a local CLI login refresh succeeds but the current Codex or Claude runner
still returns OAuth authorization required, treat the row as `blocked-auth` in
that runner. Do not start Mentor, publish, or continue a tenant-changing row
until `auth_status` succeeds in the same execution context that will run the
row.

Those are two separate token caches, and knowing that changes the plan rather
than only the verdict. A command-line tenant login keeps its own token store and
authenticates through a browser, so no agent can perform it, and a healthy
runner authorization says nothing about whether that login is current. When a
row will need an OML or `.opc` snapshot, decide it before the run starts and
fold that login into the same pause that collects the runner's authorization:
one interruption for the person at the keyboard rather than two, several minutes
apart, with the run stalled in between. A snapshot discovered to be needed after
the run is a second pause the plan could have spent once.

Historical evidence is context only. It can explain why a row exists or what
previously happened, but it does not prove the current app identity, current
environment, current revision, current build, current deployment, runtime route,
or current tool availability for a new or resumed live row. Recheck and record
fresh evidence before current-proof claims.

## Execution Evidence Contract

For live or publish-adjacent OMI work, quality comes from a fixed evidence
sequence, not from larger Mentor prompts.

Use this sequence for fragile targets and for any row that may mutate a
Development app:

1. Fresh read-only target proof in the same execution context.
2. Row-specific proof for the exact screen, action, entity, REST method, agent,
   timer, mobile asset, runtime route, or hidden Studio layer.
3. Proof-only inspection when the exact target is not already proven. A
   proof-only step must not edit, save, publish, deploy, trigger timers, call
   external integrations, or mutate data.
4. Edit only after the exact target is proven. Keep the edit prompt narrow and
   name protected surfaces. This is the `edit only after the exact target is
   proven` gate.
5. For non-publish rows, stop after clean edit validation: `attempted_change=true`,
   `change_applied=true`, validation has `0` errors, target proof still
   matches, and no unrelated mutations or contradictory completion signals are
   present.
6. If publish is explicitly approved and required, publish only after clean
   terminal evidence and then collect post-publish proof from `env_app`,
   revision/build/deployment facts, row-specific context, Studio visual proof,
   or runtime browser proof.
7. Artifact reconciliation across queue, state, readiness, and feedback so a
   completed row is not still described as pending. A non-publish row may be
   terminal after edit validation plus artifact reconciliation.

During artifact reconciliation, remove any stale contradiction between the
queue, state, readiness, and feedback before treating the row as terminal.

If any step produces contradictory evidence, missing auth, malformed validation
output, unsupported inspection behavior, target mismatch, or secret-bearing
output, stop before the next step and record `blocked-evidence`,
`blocked-auth`, `blocked-tool-unavailable`, or the narrowest accurate terminal
status.

## Live MCP Need Decision Matrix

| Decision | Use when | Outcome |
| --- | --- | --- |
| live validation is needed when | The remaining claim depends on current app identity, environment identity, Mentor tool behavior, generated change summaries, revision/build state, dependency lookup, or tenant-observed warnings/errors that docs, tests, and review cannot prove. | Prepare the smallest read-only MCP evidence plan first. If the plan needs any mutation, stop at the approval gate. |
| live validation is not needed when | The change is documentation-only, tests prove the local contract, current OutSystems docs prove the product-contract claim, and Claude review finds no tenant-behavior gap. | Do not create a live-validation decision artifact. Report the static evidence and keep live MCP out of scope. |

When the matrix points to live validation, prefer current official docs and local
tests for any part of the claim they can prove. Use live MCP only for the
current tenant/tool fact that remains unresolved.

## Target Suitability Cross-Check

When the unresolved live-validation claim is whether a current target app
contains enough proof for REST/API behavior, producer/consumer binding, Data
Grid, agentic assets, External Logic, timer, event, workflow, runtime visual
proof, screenshot-backed Studio proof, no-default-entry repair, or rollback
readiness, open `references/live-target-evidence-matrix.md` before confident
output.

Read-only live validation resolves only the unresolved current target fact. The
matrix determines whether the evidence is enough for confident output, enough
only for degraded or screenshot-backed evidence, or missing and therefore an
`Unverified gap`. Do not upgrade generic dependencies, Service Actions, entity
references, or nearby runtime evidence into exact Studio internals.

## Explicit Approval Gates

Every tenant-changing action requires explicit current approval naming the
exact target and exact action. Approval must identify the readable target name,
canonical target key when known, environment when relevant, and the action to
run.

- `mentor_prompt requires explicit current approval`.
- `mentor_create_asset requires explicit current approval`.
- `mentor_publish requires explicit current approval`.
  (An approval row written before 2026-09 against the retired names reads as
  a gate on the session-surface tool it maps to: the old prompt-start name maps
  to `mentor_prompt`, the old publish-start name to `mentor_publish`.)
- `deploy_start requires explicit current approval`.
- `rollback requires explicit current approval`.
- `app_create requires explicit current approval`.
- External-library upload requires explicit current approval.
- Any cleanup, promotion, configuration write, dependency mutation, or other
  tenant mutation requires explicit current approval.

If approval is missing, ambiguous, stale, or names the wrong target, stop with
`blocked-approval-required`. Do not infer approval from a plan, a previous
conversation, a test request, or a broad request to validate quality.

## Direct MCP Tool Preference

Use direct OutSystems MCP tools first for live evidence whenever they are
available in the current session. Direct tool calls are preferred because the
tool name, parameters, return shape, and error boundary are auditable without
persisting credentials.

Read-only direct MCP evidence can include `app_info`, `env_app`, context lookup,
dependency lookup, app/environment identity, revision/build facts, and
tenant-observed warnings/errors. Keep the evidence narrow and tied to the
unresolved deterministic-quality claim.

## Degraded Manual MCP-Over-HTTP Evidence

manual MCP-over-HTTP is degraded read-only evidence and degraded read-only
diagnostics. Use it only when direct OutSystems MCP tools are unavailable and
the user has explicitly accepted the degraded path for a read-only evidence
question.

The manual path must remain read-only. You must not use manual MCP-over-HTTP for
`mentor_prompt`, `mentor_create_asset`, `mentor_publish` (or the pre-2026-09
`mentor_start` / `publish_start`), `deploy_start`, rollback, `app_create`,
external-library upload, cleanup, promotion, dependency mutation, or any other
tenant mutation.

Do not put bearer tokens, OAuth codes, refresh tokens, ID tokens, session
tokens, raw authorization headers, cookie headers, or generated request headers
in artifacts, notes, prompts, test fixtures, logs, commits, or review files.
There must be no token or header material in artifacts.

## In-Memory Mentor Validation

When Mentor validation is explicitly approved, keep run-sensitive data
in-memory unless a sanitized artifact is required for review. A Mentor run may
produce generated change summaries, status events, or errors that help validate
the unresolved claim, but those outputs do not authorize publish, deploy,
rollback, or follow-up mutation.

Record only sanitized evidence needed for the claim: target app/environment,
approved action, fetched-at timestamp, terminal status, bounded summary,
redacted warnings/errors, and the next manual decision. Do not persist tokens,
headers, cookies, raw session payloads, or unrelated app content.

## Publish, Deploy, Rollback, And App Creation Boundary

Boundary phrase: no publish or deploy by default. OMI may prepare handoff
guidance, readiness notes, or read-only evidence, but it must not call
`mentor_publish` (or the pre-2026-09 `publish_start`), `deploy_start`,
rollback, `app_create`, external-library upload, or any other tenant-changing tool unless explicit current approval
names the exact target and action.

Publish/deploy-adjacent evidence is advisory unless the approved workflow also
proves the published source revision and target environment state. A read-only
preview or app lookup does not replace ODC Portal impact analysis and does not
become deployment approval.

Post-OMI4 uncovered lifecycle actions remain approval-gated even when earlier
campaign rows succeeded in Development. Test or Production promotion,
successful rollback rehearsal, app creation, app deletion, destructive cleanup,
package/PR/release work, source download, external-library upload, and
external-library publish require fresh proof, exact target naming, and explicit
current approval. Without that proof, classify the answer as `read-only
advisory`, `rollback-unavailable`, `blocked-approval-required`, or
`Unverified gap`.

### Publish Advisory Contract

**`Unverified gap` (2026-09-02): `no_changes_detected=true` can no longer be
returned.** On the session surface `publish_status` returns `{key,
applicationKey, applicationRevision, outcome, status}` and nothing else
(measured), so the publish never reports that it landed nothing. The advisory contract below is
therefore **unconditional**: treat EVERY publish as a publish advisory, and
never use the publish operation alone as proof that behavior landed. Where the
flag used to select which rows needed independent proof, the digest gate
(`app_info`'s `modelDigest` before and after) now answers the landed-or-not
question, and it was always the stronger signal — `no_changes_detected` was a
self-report with recorded false negatives.

Any publish row can be terminal only when independent post-publish proof
supports the expected result, such as:

- `env_app` revision/build/deployment facts that match the approved target;
- context proof for the expected element or preserved contract;
- Mentor terminal and bounded detail proof for hidden internals that context
  cannot expose;
- Studio visual proof for the exact hidden branch or node;
- runtime browser proof for the inspected route or event behavior.

If post-publish proof does not show the expected result — or the digest is
unchanged across the publish — stop and classify the row as blocked or not
deployed. Keep the
phrase `publish advisory` attached to the result so later summaries do not
overclaim a clean deployed-change proof.

## Sanitized Evidence Requirements

Store sanitized evidence only. Sanitized evidence may include:

- Tool name and read-only operation name.
- Fetched-at timestamp.
- App display name and canonical app key.
- Environment name and environment key.
- Revision/build identifiers and dates.
- Dependency names and keys.
- Bounded generated change summary or redacted warning/error text.
- Static docs, tests, or Claude review references used to avoid live validation.

Do not store token/header material, raw request payloads, full response dumps
containing secrets, OAuth/session material, cookies, private cache paths, or
unrelated tenant data. Keep evidence scoped to the unresolved claim.

## Stop Conditions

Treat these as stop conditions:

- The request needs live validation but lacks exact current approval for a
  tenant-changing action.
- The target app, environment, or action is ambiguous.
- Direct tools are unavailable and the only fallback would require recording or
  exposing token/header material.
- Static docs, tests, or Claude review conflict with the proposed live claim.
- The remaining product-contract claim depends on live Mentor behavior, exact
  widget signatures, TrueChange behavior, or tenant-specific facts that cannot
  be proven with the available read-only evidence.
- The proposed artifact would include secrets, headers, OAuth/session material,
  or broad tenant data unrelated to the claim.
- A publish, deploy, rollback, app creation, external-library upload, cleanup,
  promotion, or other mutation is requested without exact current approval.

When a stop condition fires, report the unresolved gap, the missing approval or
evidence, and the smallest safe next action. Use `blocked-approval-required`
when approval is the blocker.
