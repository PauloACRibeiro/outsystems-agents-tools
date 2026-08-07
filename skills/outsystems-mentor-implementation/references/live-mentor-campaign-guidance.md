# Live Mentor Campaign Guidance

Use this reference when `outsystems-mentor-implementation` is being tested with
a real OutSystems target, or when a Mentor Studio prompt is meant to be run
against a live non-production app as part of a gated campaign.

This file does not authorize tenant-changing work. It records what OMI2 taught
the skill. Exact approval is still required before app creation, Mentor edits,
publish, deploy, rollback, cleanup, promotion, package, push, or PR.

When tenant inventory or cached tenant evidence is used to identify the target
app, open `references/tenant-context-guardrails.md` and record a Tenant Context
Packet. Use it for target identity only. It does not expand approval and does
not authorize tenant-changing actions beyond the exact live campaign gate.

## Evidence Boundary

The OMI2 campaign used a dedicated Development fixture app and proved the
workflow on that fixture. It does not prove arbitrary production safety.
Use `outsystems-cross-agent-review-loop` for the queue, reviewer prompts,
approval gates, and final readiness evidence; use this skill for the Mentor
prompt content and Studio-native scope control.

OutSystems documentation grounding used for these boundaries:

- `deployments-api-v1.json`: ODC exposes separate publish and deployment
  operation resources, statuses, messages, revision, build, and environment
  fields. Treat publish and deploy/rollback evidence as distinct until current
  tool output proves the relationship for the target app.
- `avoid-setting-screens-accessible-everyone.md`: setting a screen as
  accessible to Everyone makes it public; Authenticated Users is the safer
  default unless public access is explicitly intended.
- `server-call-screen-accessible-everyone.md`: server calls on screens
  accessible to Everyone are security-sensitive and need server-side
  validation and non-sensitive returned data.

For multi-capability campaigns, also use
`references/live-target-evidence-matrix.md`. A simple fixture can prove marker,
publish, and visual-control behavior, but REST/API contracts, direct consumed
REST bindings, Data Grid behavior, External Logic, agentic assets, timers,
events, and workflows need target-specific proof. Screenshot-backed Studio
evidence may close a specific gap only for the visible method, branch, screen,
or property shown in the sanitized artifact.

## Computer Use / Claude Fallback Preflight

Complete the Computer Use / Claude fallback preflight before relying on Claude
UI fallback.

Evidence-tool reliability caveat: ODC Studio may open with a blank or
disconnected canvas during Computer Use visual inspection (tenant-observed,
OMI4-009/OMI4-010, 2026-07-03). Detect this state before treating visual
evidence as blocked: if the canvas is blank, perform one bounded recovery
attempt (close and reopen the app in Studio, or refresh the Studio window),
then, if the canvas is still blank, record the row's visual route as
degraded-evidence with a sanitized screenshot instead of treating the whole
row as hard-blocked — alternate approved evidence routes (context reads,
runtime checks) may still close the row.

Before relying on Claude UI fallback, verify Computer Use availability and the
current authorization envelope. If Computer Use, browser tooling, or the Claude
UI route is unavailable after the approved recovery attempt, mark the campaign
row `blocked-automation` and preserve the prompt path, expected feedback path,
attempt count, blocked tool, and sanitized transcript or screenshot evidence.

Allowed bounded fallback operations are limited to:

- focus or open Claude, Claude Code, or the related approved app window;
- use Claude's supported UI for OutSystems MCP access when Codex MCP cannot run
  the approved row;
- paste campaign prompts from repo artifacts;
- scroll, read, or copy non-secret output needed for evidence summaries;
- accept login or browser permission prompts directly tied to approved
  OutSystems MCP or Claude access when no secret, token, callback URL, or private
  config is exposed.

Excluded fallback operations:

- do not delete data;
- do not install software, plugins, extensions, or certificates;
- do not change system settings;
- do not bypass browser safety warnings;
- do not solve CAPTCHAs;
- do not create accounts, keys, persistent access, or uploads;
- do not publish, deploy, roll back, promote, clean up, or mutate tenant state
  outside the exact approved row;
- do not transmit secrets, bearer tokens, OAuth callback URLs, refresh tokens,
  private logs, private config, or Mentor session tokens;
- do not edit Claude-private config, plugin cache, command files, OAuth callback
  storage, private MCP data, or Codex-private config.

## Fixture Preconditions

Use a Dedicated non-empty Development fixture for live capability testing.
An empty app is not a valid visual target because it may have no screen or no
default screen. Before running a reversible visible marker test, verify:

- tenant hostname, environment name/key, app display name/key
- current revision/build/deployment
- a default screen exists and the approved runtime URL resolves to that route
- baseline text is visible before adding the marker text
- the future marker is absent before the marker edit
- the fixture has no production, Test, or promotion scope in the approval

For browser-based baseline and post-publish inspection, either use an already
authenticated browser session or make only the inspected default route reachable
without credentials. If corrective access is needed, treat it as a separate
corrective access Mentor edit with separate exact approval.

Do not quietly set a real application screen to accessible to Everyone. For a
dedicated test fixture, it can be acceptable when the user explicitly approves it,
the page has no sensitive data, and any server calls are validated server-side.
For non-fixture apps, prefer Authenticated Users or a browser session that can
authenticate without exposing secrets.

## No-Default-Entry Repair

If visual inspection returns `This application does not contain a default
entry`, classify the target before accepting the result.

- Empty app path: accept this only when read-only context evidence proves no
  owned screens or actions exist and the user accepts the empty-app limitation.
- non-empty app with no default screen: treat this as a no-default-entry repair
  case, not as an accepted empty-app risk.
- Documentation grounding: OutSystems ODC UI flows docs state that the Default
  Screen is the index page in Web apps, that only one screen can be the Default
  Screen, and that Studio users navigate to the Screen, right-click it, and
  select Mark as Default Screen.
- Capability boundary: this skill may prepare a narrow Mentor/Studio prompt to
  mark an existing screen as Default Screen only when that screen is an
  existing MainFlow user screen and only after the target app, candidate screen,
  runtime URL, and current revision/build/deployment are verified.
- Do not mark Common authentication, permissions, profile, or password-recovery
  screens as the app default. Treat those as platform/template flow screens, not
  user-created entry screens for live marker or scaffold proof.
- If the app has only Common authentication/template screens and no user screen
  in `MainFlow`, the repair is blocked until a MainFlow user screen exists.
  Ask for a separate approved scaffold/create-screen step or a manual Studio
  screen before any default-screen repair or visual-marker retry.
- Require separate exact approval before running Mentor for a default start
  screen change; do not combine default-screen repair with marker edit,
  corrective access, role/security, or cleanup work unless the approval names
  both actions.
- Prefer an existing low-risk `MainFlow` screen such as `Home` only when
  read-only context proves it exists. If no obvious MainFlow user screen exists,
  ask the user to choose or create the screen instead of inventing one.
- After a terminal default-screen repair, publish only with exact current
  approval, then publish and re-inspect the approved runtime URL.
- Do not change access, roles/security, data model, dependencies,
  integrations, theme/layout, navigation, or business logic as part of this
  repair.

## Minimal MainFlow Home Default-Entry Bootstrap

Use the minimal MainFlow > Home default-entry bootstrap only when a live
fixture or intentionally empty shell needs runtime-entry proof and the user has
approved a separate scaffold/create-screen step. This is narrower than
a product scaffold: it creates the smallest user-facing route needed to prove
that the app can render a default entry.

Before preparing the prompt, verify:

- target tenant, environment, app display name, and app key
- current revision/build/deployment
- documentation grounding for Default Screen and screen creation behavior remains current in the existing OMI reference set; add or verify approved OutSystems public/internal documentation before adding any new product-behavior claim
- shell classification and whether the app is a fixture, intentionally empty
  shell, ODC manual empty shell, bare MCP-created shell, or template-incomplete
  shell
- no suitable `MainFlow` user screen already exists, or the user explicitly chose
  to create/replace the named empty fixture screen
- approved baseline text
- whether publish and browser reinspection are approved as part of the same
  envelope or must stop after the Mentor session

The Mentor/Studio prompt may request only this change:

- create a single user screen named `Home` in `MainFlow`
- place the approved baseline text visibly on that screen
- mark `Home` as the app's default screen using the Studio `Mark as Default
  Screen` behavior
- preserve any verified product-template assets that already exist
- stop if the app, environment, revision/build/deployment, or existing screen
  content no longer matches the approved envelope

This bootstrap does not recreate `Common`, authentication, profile,
password-recovery, `Layouts`, `Themes`, or `OutSystemsUI`, and it does not
prove product-template equivalence. It solves only the default-entry/runtime
fixture proof gap.

Do not change access, roles/security, data model, dependencies, integrations,
navigation, theme/layout, or business logic unless the approval names that
change. If anonymous browser proof is also required, handle it as a separate
corrective access approval or as an explicitly named action in the same
approval envelope.

After a terminal Mentor run, publish only the terminal Mentor session if exact
current approval names the app and Development environment. After publish,
record publish status/logs when available, recheck `env_app`, and perform
settled runtime reinspection of the approved URL. Passing evidence must show
the baseline text visible, final URL inside the approved route, no login-only,
no-default-entry, blank, Common-only, or route-mismatched state, and a console/
runtime summary.

## Mentor Edit Scope

A live reversible marker edit should be narrow enough to review by artifact and
visual evidence. The OMI2 marker was:

```text
OMI live probe 2026-06-23 RUN123
```

The Mentor prompt should say:

- target only the verified default screen and route
- add only the approved visible marker text
- keep baseline text visible
- do not change data model, roles/security, integrations, dependencies,
  navigation, external libraries, timers, server actions, client actions,
  business logic, or theme/layout beyond the marker placement
- stop if the target screen, app key, environment key, or current
  revision/build/deployment no longer match the approved envelope

If a corrective access edit is required first, keep it separate from the marker
edit. Do not mix access correction and marker behavior in one approval unless
the approval explicitly names both.

## Session And Token Hygiene

Publish only the same terminal Mentor session that produced the approved change.
If the transient Mentor session token is unavailable, stale, invalid, or would
need to be printed or stored, stop if the token is unavailable. Do not rerun
Mentor, substitute a no-op session, or create a fresh marker session without
fresh exact approval.

Never print or store bearer tokens, authorization headers, OAuth callback codes,
refresh tokens, ID tokens, or Mentor session tokens. In prompt and artifact
wording, say do not print or store token values. Artifact evidence should name
operation IDs, app keys, environment keys, revision/build/deployment, and
sanitized statuses only.

If direct Codex OutSystems tenant tools are unavailable but the user approves a
bounded execution route through Claude, use the Claude authenticated MCP route
only for the named operation set, such as `mentor_start` and `mentor_get_run`
for an in-memory edit. Do not touch Claude-private config, plugin cache,
command files, OAuth callback storage, or private MCP data.

## Publish Gate

Before publishing a Mentor session, recheck:

- tenant hostname
- app display name/key
- environment name/key
- current deployed revision/build/deployment
- approved source Mentor run/session
- allowed operation is publish to the named Development environment only

After publish, poll the publish operation until terminal, inspect publish
messages/logs when available, then recheck the deployed app. Record the final
revision/build/deployment and runtime URL. Do not treat a successful Mentor
edit as publish evidence.

## Promotion Preview Gate

Use this before a promotion handoff after approved Mentor execution and
Development publish evidence exists. This gate is advisory only and does not
authorize promotion.

Record:

- preview HTML path
- app display name/key
- source environment and target environment
- source revision and target revision, `noop`, or `fresh deploy`
- published source revision evidence that includes the approved change
- fetched-at timestamp with freshness younger than 10 minutes
- classification
- risk level
- revision gap
- whether ODC Portal impact analysis is still pending

Stop or warn:

- `noop`: if target already matches source, record that no promotion handoff is
  needed; do not describe it as safe-to-promote for a pending unpublished change.
- `target-ahead`: if the target environment revision is ahead of source, stop
  and ask the user to confirm the intended baseline.
- `fresh deploy`: warn that this is first deployment to the target environment.
- `1 <= revision gap <= 5`: record low risk when Portal impact analysis is clear.
- `6 <= revision gap <= 50`: record medium risk and require broader smoke-test
  coverage plus ODC Portal impact-analysis review.
- `revision gap > 50`: record high risk and require staged promotion discussion,
  stronger smoke testing, and ODC Portal impact-analysis review.
- `stale`: if freshness is older than 10 minutes or the source revision changed,
  refresh before any promotion-readiness statement.

No deploy, rollback, cleanup, promotion, or tenant mutation is authorized by
this gate.

## Visual Inspection Gate

Use a settled-state visual inspection, not just the first browser screenshot.
OMI2 produced blank initial screenshots before the page settled; that was valid
diagnostic evidence, but not the selected pass result.

The visual check should record:

- approved runtime URL and whether the final route stayed inside it
- screenshot path
- console/runtime errors and warnings
- baseline text visible
- marker text visible after publish, or absent after rollback/baseline
- login-like text absent when anonymous fixture access is expected
- no obvious broken layout
- if a reload or short wait was needed, record the initial state and the
  settled-state result separately

Stop if the browser redirects outside the approved route, requests credentials
or secrets, or needs any tenant-changing action to continue.

Treat login-only, no-default-entry, blank, Common-only, and route-mismatched
states as degraded evidence unless the campaign explicitly accepts that
limitation. Passing visual proof for a non-empty target must exclude those
states and record the settled final URL, viewport, screenshot/report path, and
console/runtime summary.

## Rollback And Cleanup Gate

Rollback-eligibility pre-population rule: a campaign row that plans to
exercise rollback must pre-populate the target with at least two independent
successful deployments before the rollback step. A freshly bootstrapped
fixture may not satisfy the platform's rollback-eligibility threshold even
after repeated Mentor publishes (tenant-observed, OMI2-009: two publishes,
`found 0` qualifying deployments).

Open backlog note (read-only investigation, no tenant session authorized by
this note): why a twice-published fixture reports zero qualifying
deployments — likely an ODC platform counting distinction between publish
and deploy operations. Resolve with read-only `deploy_list` /
`env_deploy_history` evidence during a future approved campaign, then update
this rule with the confirmed semantics.

Do not assume rollback is available. Recheck the current revision/build/
deployment first, then attempt rollback only after exact approval. If the tool
returns no operation key or reports rollback-unavailable, record the exact
reason, recheck the app state, and do not invent manual recovery.

If exact safe rollback support is not proven for the current
app/environment/revision/build/deployment, close the row or guidance as
`rollback-unavailable` rather than calling rollback. Do not call rollback when
it could remove an approved marker, default-screen repair, or other evidence
that the current campaign still needs to preserve.

The OMI2 rollback attempt returned rollback-unavailable because the platform
reported insufficient successful deployments for the asset, even though the app
had Mentor publish revisions. Treat that as a publish-versus-deploy evidence
boundary until the target's deployment history proves otherwise.

If rollback coverage matters, prepare the fixture before the marker test with
enough qualifying successful deployments for the rollback tool. If cleanup is
still desired after rollback-unavailable, request a separate approval for a
Mentor revert edit plus publish or for a manual cleanup path.

## Resumability

Each campaign row should leave enough artifact evidence to resume after Codex,
Claude, or Mentor token usage limits:

- prompt path
- feedback/evidence path
- target app and environment keys
- pre-action and post-action revision/build/deployment
- operation IDs and terminal statuses
- blocked/degraded reason when a step stops
- next exact approval needed

On resume, validate the queue and recheck the live app state before continuing.
Redo only the last inconsistent or unproven step; do not redo completed rows
with terminal evidence.

Historical evidence is context only. On resume or rerun, collect fresh evidence
for current app identity, current environment, current revision, current build,
current deployment, runtime route, and tool availability before treating a row as
current-proof. Do not use OMI1, OMI2, OMI3, or older campaign artifacts as proof
for a new target state unless the row explicitly revalidated the relevant fact.
