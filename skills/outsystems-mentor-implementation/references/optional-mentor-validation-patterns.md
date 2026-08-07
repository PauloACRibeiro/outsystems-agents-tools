# Optional Mentor Validation Patterns

Use this reference when Paulo asks for optional post-OMI validation, an
app-level audit after approved Mentor execution, a post-Mentor report, a
publish handoff without publish approval, or an AI model migration review
after OMI output. It owns optional post-OMI validation checklists, the
deployment-preview gate, report hygiene, publish-handoff review, and AI model
migration review without making Mentor Co-pilot a runtime dependency;
deployment preview evidence remains optional, and OMI does not require or
invoke `outsystems-deploy-preview`.

## Boundary

OMI does not require `outsystems-mentor-copilot`. This is an optional companion
pattern, not a runtime dependency.

Do not call `outsystems-mentor-copilot` from OMI. Do not require its scripts,
cache layout, task IDs, or report renderer. Do not make the sibling skill part
of the OMI execution path.

Route live MCP validation need decisions through `live-execution-intake.md`
before any optional tenant-backed validation, Mentor run, publish handoff,
deploy-adjacent evidence request, or current tenant/tool behavior claim. Static
docs, tests, and Claude review are first; live MCP is optional, evidence-driven,
read-only first, and approval-gated.

When optional validation depends on current target suitability, degraded visual
evidence, rollback-unavailable handling, or exact safe rollback proof, open
`references/live-target-evidence-matrix.md` before app-level validation or
publish/deploy-adjacent guidance. Use the matrix boundaries before making
readiness claims, and keep missing proof as `Unverified gap` instead of
inferring from nearby target evidence.

No automatic `mentor_start`. No automatic `publish_start`. No implicit publish.
Any live Mentor action, publish, deploy, rollback, app creation, promotion, or
tenant mutation still requires explicit current approval for the target and
action.

## When To Use

Use this after OMI output when the user wants a validation checklist, review
prompt, or audit framing around a generated plan, paste-ready prompt, or
Studio-native pseudocode.

Use this after approved Mentor execution when the user wants app-level review
before deciding whether to publish or preserve the Mentor session.

Do not use this to replace OMI's source-map routing, evidence status contract,
hardening guide, visual-source enriched blueprint, Prompt Coverage Audit, or
Post-Mentor Preservation Decision Gate.

## Optional Validation Menu

- Quality review: look for anti-patterns, unclear names, duplication, oversized
  actions, and complexity hotspots.
- Security review: check role boundaries, anonymous access, exposed endpoints,
  hardcoded secrets, sensitive logs, and SQL/input risks.
- Performance review: check N+1 query patterns, oversized aggregates, unbounded
  lists, heavy screens, and client/server boundary mistakes.
- Accessibility review: check labels, alt text, keyboard flow, heading order,
  contrast, and visible focus behavior.
- Test scaffold review: propose happy path, edge cases, and error cases for the
  changed Server Actions or client flows.
- Documentation gap review: identify entities, actions, screens, blocks, or
  decisions that need concise descriptions.
- Refactor review: identify split candidates, repeated logic, naming drift, or
  reusable block extraction candidates.
- Demo data review: check whether demo data is realistic, fictional,
  referentially coherent, and includes useful edge cases.
- Demo readiness review: check broken screens, embarrassing empty states,
  visible console or runtime errors, and high-impact polish gaps.
- AI model migration review: identify affected AIModelConnection references,
  affected actions and agents, expected behavior differences, prompt
  adjustments, and a testing checklist before publishing. Keep this as review
  guidance; do not execute the migration, call Mentor, or mutate a tenant
  unless Paulo gives explicit current approval for the target and action.
- Authenticated runtime smoke check: read-only browser inspection of approved
  routes with approved credentials/session context, secret-safe handling, role
  expectations, settled URL, visible state, and console/runtime summary.
- Security/performance execution plan: produces commands, target boundaries,
  expected evidence, and pass/fail criteria; it is not executed evidence until
  the named test actually runs.

## Production-Grade Lifecycle Advisory

Use this when a user asks whether an OMI result is ready to promote, release,
rollback, package, or operate outside a Development-only validation envelope.

This is a read-only advisory route by default. It does not deploy, promote,
rollback, package, create a PR, push, download source, upload external
libraries, publish external libraries, or mutate Test or Production.

Required evidence before a confident lifecycle claim:

- Current source app, revision, build, deployment key, and runtime URL when
  relevant.
- Target environment identity for any Test or Production promotion question.
- ODC Portal impact analysis for blockers and warnings.
- rollback rehearsal plan or current `rollback-unavailable` classification.
- package, PR, release, source download, external-library upload boundaries when those actions are in scope.
- Explicit current approval before any tenant-changing or repository-changing
  action.

If any item is missing, answer with `read-only advisory` and name the missing
proof. Do not present advisory evidence as executed promotion or rollback
evidence.

## Deployment Preview Gate

Use this when Paulo asks for a deploy preview, safe-to-promote check,
promotion readiness, or publish/deploy-adjacent readiness after OMI output or
after approved Mentor execution. For prompt-only OMI output or unpublished
Mentor changes, use the preview as current-state baseline only; it must not be
described as safe to promote for a pending change. When asked for a yes/no
promotion verdict, answer with the advisory readiness shape instead; a verdict
requires ODC Portal impact analysis evidence and explicit current approval.

This is a read-only deployment preview for tenant state. OMI owns this gate and
does not require or invoke `outsystems-deploy-preview`. A deployment preview
report from another workflow can be used as optional external evidence when it
is already available, but OMI does not require sibling skill scripts, cache
layout, HTML templates, runtime files, or installation. Do not copy sibling
cache paths into OMI artifacts.

Use a read-only deploy preview as advisory tenant evidence only; local preview
reports may still be written as artifacts. If the target environment revision
is ahead of the source revision, stop and mark the guidance `concerning`; do
not treat a deploy-preview result as final deploy approval or as a replacement
for ODC Portal impact analysis. For prompt-only OMI output or unpublished
Mentor changes, treat the preview as current-state baseline only; do not
describe the pending change as safe to promote until published source revision
evidence proves the change exists in the source environment.

Boundary:

- The gate does not deploy.
- The gate does not publish.
- The gate does not call rollback, cleanup, promotion, or tenant mutation tools.
- The gate does not replace ODC Portal impact analysis.
- ODC Portal impact analysis remains the deployment decision point for warnings
  and blockers.

Required preview evidence:

- app display name and canonical app key
- target environment name and key
- source revision and source revision date
- target environment revision and deployment date, or `fresh deploy` when the
  app is not deployed in the target environment
- published source revision evidence when the preview is meant to evaluate a
  live change rather than only the current tenant baseline
- preview fetched-at timestamp
- preview HTML path when a local preview HTML report is generated
- classification and risk level
- revision gap when both source and target revisions are known

## Artifact Reconciliation Gate

After a live campaign row or campaign closeout, compare queue, state,
readiness, and feedback artifacts before summarizing the result.

Check for stale contradiction patterns:

- Queue says a row is `done` but feedback top-level `Status:` still says
  `blocked`, `pending`, or `blocked-evidence`.
- State/readiness says a completed row is still the next actionable row.
- A completed row keeps old text such as "stopped before publish" even later
  evidence proves a terminal retry.
- A read-only terminal row is summarized as pending because no Mentor edit
  happened.
- `rollback-unavailable` is treated as incomplete even though rollback was not
  safely proven and the approved boundary says not to call rollback.

If a contradiction is found, propose a local-only artifact fix, patch only the
summary/status text needed to align with the final evidence, and rerun queue
validation plus campaign consistency checks.

## Deployment Preview Response Shape

When producing deployment preview guidance, include these sections. The shape
ends with the standard `### Evidence Status` section required by the Output
Shape Matrix — exactly one OMI evidence label, typically `Unverified gap` when
live tenant evidence is missing, placed before `### Unknowns And Fallback
Behavior` per the response contract.

### Deployment Preview Evidence

- App: record app display name and canonical app key.
- Source: record source environment, source revision, source revision date, and
  published source revision evidence when evaluating a live change.
- Target: record target environment, target revision and deployment date, or
  `fresh deploy` when the app is absent from the target.
- Freshness: record fetched-at timestamp and whether the source revision changed
  after the preview.
- Artifact: record preview HTML path only when a local preview HTML report
  already exists or is generated by an explicitly approved non-OMI workflow.

### Readiness Boundary

- Classification: record `noop`, `fresh deploy`, `update`, or `concerning`.
- Risk: record none, low risk, medium risk, high risk, or concerning.
- Revision gap: record the numeric source-minus-target gap when both revisions
  are known.
- Advisory statement: state that OMI readiness wording is advisory and does not
  replace ODC Portal impact analysis.

### ODC Portal Decision Boundary

- Record whether ODC Portal impact-analysis status is pending, clear,
  warning-only, or blocked.
- Record ODC Portal warnings and blockers separately.
- Treat blockers as overriding OMI readiness wording.

### Evidence Status

- Record exactly one main OMI evidence label, typically `Unverified gap` when
  live deploy-preview or ODC Portal evidence is missing or unrefreshed.

### Unknowns And Fallback Behavior

- Record missing revision evidence, stale preview evidence, unavailable ODC
  Portal analysis, ambiguous target environment, missing published source
  revision evidence, and unresolved dependency checks.
- Include fallback behavior for each unresolved evidence gap that keeps the
  guidance advisory only.

Freshness:

- Accept preview evidence only when freshness is younger than 10 minutes and the
  source revision is unchanged.
- If the preview is older than 10 minutes, or the source revision changed,
  refresh the preview before making any readiness claim.
- If the preview cannot be refreshed, use `Unknowns And Fallback Behavior` and
  label the deployment guidance advisory only.
- Before any safe-to-promote or promotion-readiness claim for a live change,
  require published source revision evidence that the change exists in the
  source environment.

Stop or warning conditions:

- If OMI has only produced prompt text, or if a Mentor change has not been
  published to the source environment, label the preview current-state baseline
  only and do not use it as readiness evidence for the pending change.
- `noop`: target already matches the source revision; no promotion is needed;
  must not be described as safe-to-promote for a pending change.
- `fresh deploy`: no target revision exists; first deployment to the target
  environment.
- `target-ahead`: target environment revision is ahead of source revision;
  concerning; stop.
- `stale`: preview older than 10 minutes or source revision changed; refresh.
- `1 <= revision gap <= 5`: low risk when ODC Portal impact analysis is clear
  and the source revision evidence includes the approved change.
- `6 <= revision gap <= 50`: medium risk; add an `Optional Constraints`
  warning for broader accumulated change surface and broader smoke testing.
- `revision gap > 50`: high risk; add an `Optional Constraints` warning for
  staged promotion review, stronger smoke testing, and ODC Portal
  impact-analysis review.
- These thresholds are an OMI-owned heuristic, not final ODC approval.
- If the target environment revision is ahead of the source revision, mark the
  result `concerning`, stop confident deployment guidance, and ask Paulo to
  confirm the intended baseline.
- If the preview is a `fresh deploy`, call out that this is a first deployment,
  not a normal update, and require stronger route, dependency, role, and smoke
  checks before promotion.
- If revision evidence is missing, do not infer the gap from prompt-only work;
  keep the classification advisory and list the missing evidence under
  `Unknowns And Fallback Behavior`.
- If ODC Portal later reports blockers, those blockers override OMI readiness
  wording.

## Report Shape

When producing a report artifact, use a project-local report path chosen for
the task and include:

1. Prompt used
2. Terminal Mentor result or app-level review result
3. Verification performed
4. Open gaps and manual checks
5. Publish decision

Do not use client-private cache paths as report destinations. Do not use
sibling skill cache paths as report destinations. Keep reports in a
project-local artifact location that can be reviewed without depending on
Claude-specific or Codex-specific cache state.

The report may surface a publish handoff, but it must not publish. If the user
has not already approved publish to a specific environment in the current
request, stop at the handoff and ask for explicit current approval.

## Session Continuation Notes

If an approved Mentor run returns continuation information, record only the
minimum safe operational context needed for the next approved action. Never
print or persist credentials, bearer tokens, OAuth codes, refresh tokens, ID
tokens, or Mentor session tokens in colleague-facing artifacts.

## Output Guidance

For prompt-only work, emit a bounded validation checklist or review prompt.

For AI model migration review, emit a bounded review of affected
AIModelConnection usage, behavior differences, prompt adjustments, testing
before publishing, and publish handoff risks. Do not execute the migration from
this optional validation path.

For AI model migration review that affects agents or model calls, include an
Agent Guardrail Coverage Audit after the migration review checklist. Do not
execute the migration, do not configure guardrails, and do not mutate a tenant
from this optional validation path.

For approved live work, combine this reference with
`references/live-mentor-campaign-guidance.md` and
`references/odc-mentor-hardening.md`. This reference does not authorize the
live action by itself.
