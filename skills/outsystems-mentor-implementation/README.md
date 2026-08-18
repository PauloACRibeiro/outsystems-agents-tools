# outsystems-mentor-implementation

Portable skill for producing OutSystems Developer Cloud Studio-native
pseudocode, placement guidance, and paste-safe Mentor Studio prompt blocks for
existing implementation work or first scaffold work inside a verified app shell.

This README is for humans using the skill from this repo. The agent-facing
behavior lives in [SKILL.md](SKILL.md).

Legacy note: this skill was previously named `mentor-studio-code`. Treat that
old name as historical/provenance wording only, not an operational alias; the
canonical skill name for new prompts, packages, installs, and routing is
`outsystems-mentor-implementation`.

## Strategic purpose

The strategic goal is to make OutSystems work with coding agents feel closer to
traditional software development: structured intent, reviewable implementation
decisions, explicit unknowns, and more predictable execution.

Mentor Web and Mentor Studio still interpret prompts and requirement documents.
This skill does not turn Mentor into a deterministic compiler and does not bypass
human review. It adds a deterministic-intent layer before execution: entities,
roles, screens, actions, validations, data behavior, evidence status, and
unknowns are made explicit before a Mentor Studio prompt or Studio-native
pseudocode block is handed off for review.

For Strategic Goal explanation and supporting workflow artifact, see
[docs/outsystems-mentor-implementation-deterministic-intent-share.md](../../docs/outsystems-mentor-implementation-deterministic-intent-share.md).

## Mentor capability matrix

Product capability and constraint claims for Mentor Web, Mentor Studio, and
known limitations are owned by the
[Mentor Capability And Constraint Matrix](references/mentor-capability-constraint-matrix.md).
Use that file to check the current OutSystems documentation route before saying
what Mentor can create, refine, or modify.

Keep this README thin: do not copy the full matrix here, and do not promote
generated, dry-run, fixture-only, or screenshot-only evidence into
product-contract claims.

## Source-owner discipline

OMI keeps this README as a human summary. The canonical details live in source
owner references, so do not duplicate the canonical contract here.

- `references/mentor-capability-constraint-matrix.md` owns Mentor capability,
  constraint, known-limitation, and current OutSystems documentation claims.
- `references/prompt-narrowing-preflight.md` owns complex-plan decomposition,
  Plan Conversion Manifest, block sizing, and coverage-audit rules.
- `references/omi-route-mode-classifier.md` owns output-mode selection,
  stop/ask behavior, fallback behavior, and no-tenant-mutation classification.
- `references/retrieval-query-bundles.md` owns retrieval recipes, authority
  classes, degraded checks, and stop conditions.
- `references/live-execution-intake.md` owns optional live validation need
  decisions, read-only resolution, sanitized evidence, and approval gates.
- `references/live-target-evidence-matrix.md` owns OMI3-derived target
  suitability rules for REST/API proof, producer/consumer binding, Data Grid,
  agentic/integration assets, screenshot-backed Studio evidence, degraded
  visual exclusions, no-default-entry repairs, and safe rollback boundary
  decisions.
- `references/structured-intent-mode.md` owns structured-intent normalization
  and deterministic-plan retry behavior.
- `references/odc-pseudocode-source-manifest.md` owns generic source coverage
  and evidence-audit gaps.

`references/source-map.md` ends with a "Process Artifacts" split: review queues
and reviewer prompts listed there are maintenance history, not runtime routing
targets.

## OMI1 Live Preflight Hardening

OMI1 live preflight lessons are reusable skill behavior, not just campaign
history. Before a live campaign row runs, OMI requires same-execution-context
OutSystems MCP proof, `auth_status` tenant match, and fresh evidence for the
current app/environment/revision/build/deployment/runtime route relevant to the
row. Computer Use / Claude fallback preflight is required before relying on UI
fallback, and historical evidence is context only until the current row
revalidates the fact it needs.

## What this skill is for

Use this skill when you want an agent to:

- choose the correct ODC runtime boundary before writing logic
- express implementation steps in real ODC Studio terms
- generate paste-safe Mentor Studio prompts for supported web UI work
- ground pseudocode and prompt output in current OutSystems evidence

## Generated Output scorer

For deterministic-quality review work that already has a source plan, expected
block manifest, generated output sample, and expected scorecard, use
`scripts/deterministic_quality_scorer.py` before review handoff. It gives a
repeatable local check for coverage drift, dependency-order drift, missing
Evidence Status lines, stale Mentor Studio scope wording, and unsafe live-MCP
gate wording.

Repo-local example:

```bash
python3 skills/outsystems-mentor-implementation/scripts/deterministic_quality_scorer.py \
  --source-plan skills/outsystems-mentor-implementation/tests/fixtures/deterministic_quality/complex_source_plan.md \
  --expected-blocks skills/outsystems-mentor-implementation/tests/fixtures/deterministic_quality/complex_source_plan_expected_blocks.md \
  --generated-output skills/outsystems-mentor-implementation/tests/fixtures/deterministic_quality/generated_output_sample.md \
  --expected-scorecard skills/outsystems-mentor-implementation/tests/fixtures/deterministic_quality/generated_output_expected_score.md \
  --json
```

On Windows PowerShell, use `python` instead of `python3` and put the command on
one line — `\` does not continue a line there, and `python3` is not a command.

Use this scorer only when those four artifacts exist. It does not replace
current OutSystems documentation authority, human review, or approval gates for
live validation.

Do not use it for Mentor Web requirement packets, blueprint refinement, or
post-generation app review; those are outside this skill's colleague-sharing
scope. Do not use it as the owner of a full saved implementation plan, approval
workflow, or personal validation campaign; those are outside the colleague
quick-start scope.

App-shell first scaffold is part of this skill when the target is an empty or
newly created app shell with a verified app key. Since ODC MCP 0.14.0 a newly
created shell is normally not empty — `app_create` clones the kind's standard
application template by default — so the scaffold preserves `Common`, `Layouts`
and `Themes` rather than inventing them. This skill can prepare the
first-pass entities, roles, screens, relationships, and Mentor Studio prompts
for that shell. It does not replace Mentor Web, and it does not silently create
or publish an app. If the user prefers another specification workflow, use that
reviewed artifact as input. For changing an app that already has meaningful
structure, use a saved implementation plan plus this skill: "change this app
deliberately with a coding agent and Mentor, while preserving reviewability and
control."

## Tenant context and existing app evidence

When an existing app, verified app shell, or placement decision depends on
tenant inventory or cached tenant evidence, OMI uses a Tenant Context Packet
from `references/tenant-context-guardrails.md`.

Before a confident app-targeted prompt, verify the target app name, canonical
app key, environment, and evidence freshness. Cached or stale tenant evidence
must be labeled. Stale or ambiguous evidence belongs in `Unknowns And Fallback
Behavior`.

The packet can improve target identity, reusable asset names, dependency
inventory, scope control, and unknowns. It does not authorize Mentor execution,
publish, deploy, rollback, cleanup, or tenant mutation.

Existing app structure evidence can improve OMI when an existing app already
has an app overview, app documentation, or app architecture summary artifact.
Treat that artifact as read-only orientation evidence for target grounding,
named-element confidence, dependency inventory entries such as `Already exists
(use existing)`, library and AI model connection dependency hints, and
unknowns. It does not prove exact Studio internals, does not infer per-screen
roles, and does not replace current official docs or `outsystems-tech-content`
for implementation authority. OMI does not require a sibling architecture or
documentation skill and does not require a graph, HTML report, script,
client-specific cache path, fixed filename, or fixed JSON shape. This evidence
does not authorize Mentor execution, publish, deploy, rollback, cleanup, or
tenant mutation.

The Search Engine Sandbox reduced example at
`tests/fixtures/existing_app_structure_evidence/search_engine_sandbox_reduced_packet.md`
from this skill root, or
`skills/outsystems-mentor-implementation/tests/fixtures/existing_app_structure_evidence/search_engine_sandbox_reduced_packet.md`
from the repo root, is a portable example for this optional, read-only evidence
shape; it is not a required source contract.

Optional reverse dependency evidence can improve shared producer decisions when
a change touches a shared producer. Treat it as read-only evidence for consumer
count, stale references, failed coverage, and scope brake decisions. OMI does
not require a sibling skill, does not require an HTML report, and does not
require scripts, cache paths, or fixed JSON filenames. This evidence does not
authorize Mentor execution, publish, deploy, rollback, cleanup, or tenant
mutation.

## Live target evidence matrix

When a request depends on what a current tenant app really contains, use the
Live Target Evidence Matrix before confident output. The matrix keeps REST,
producer/consumer, Data Grid, agentic/integration, visual, screenshot-backed
Studio, and rollback claims tied to exact evidence.

If the exact target proof is missing, OMI should label the claim
`Unverified gap`, ask for the missing contract or target proof, and keep the
answer review-only or blocked instead of inferring from nearby dependencies,
Service Actions, entity references, screenshots, or runtime-adjacent evidence.

### What OMI3 changed

OMI3 showed that target suitability is now a first-class skill capability, not
only a campaign concern. A simple fixture can prove marker and publish control,
but REST/API, producer/consumer, Data Grid, agentic/integration, visual, and
rollback claims need evidence shaped for that capability.

The reusable rule is: when the current target proof is missing, use
`Unverified gap` and keep the answer review-only or blocked. Use
screenshot-backed Studio evidence only as bounded proof for the visible method,
branch, screen, or property. Treat degraded visual evidence and unavailable
rollback support as explicit outcomes, not as silent failures to explain away.

### What OMI4 changed

OMI4 converted applied live-campaign lessons into reusable applied quality
gates:

- Split proof from edit for fragile targets.
- Treat Studio visual proof as first-class bounded evidence for hidden layers.
- Block unsupported Mentor model-introspection patterns and stop with no change
  rather than speculating.
- Treat `no_changes_detected=true` as a publish advisory, not proof by itself.
- Retry broad metadata once, then switch to narrower row-specific proof.
- Use runtime browser proof when context proof is blind and the route is safe to
  inspect.
- Treat read-only completion as a valid high-quality result.
- Preserve asset-type boundaries for web apps, Agent assets, and mobile apps.
- Preserve exact REST, integration, timer, Data Grid, and External Logic
  contracts.
- Reconcile queue, state, readiness, and feedback artifacts before claiming
  campaign closeout.

### Confidence and escalation guardrails

OMI uses confidence and escalation guardrails when a request targets an existing
app, shared producer, role/security behavior, fragile Mentor generation
pattern, or platform-level design risk:

- Named Element Confidence Gate: named screens, actions, entities, roles,
  dependencies, and other elements must be observed or verified before they are
  used in confident paste-ready instructions.
- Change Mode Matrix: prompt-only output, read-only tenant discovery, Mentor
  execution, publish/deploy handoff, and tenant mutation each require their own
  explicit current approval boundary.
- Shared Producer Compatibility Gate: shared producer changes need a
  compatibility strategy before confident prompts when consumer impact is broad,
  stale, failed, or unknown.
- Role/Security Evidence Gate: OMI must not infer role assignments from screen
  inventory or `isPublic`; role/security claims need explicit evidence.
- TrueChange Pre-Mortem Checklist: fragile Mentor prompt areas get a final
  check for common TrueChange, binding, dependency, and navigation failures.
- Platform guardrail suite: architecture layering, server-trust security,
  references to the platform `User` entity, actions taking a record id that may
  not exist, query performance, timer/async idempotency, and public API
  contracts get read-only prompt discipline through the Architecture Layering
  Gate, Security Server-Trust Gate, User Reference Authoring Gate, Not-Found
  Guard Gate, Performance Query Pre-Mortem, Timer / Async Idempotency
  Gate, and Public API Contract Gate. This evidence does not authorize Mentor
  execution, publish, deploy, rollback, cleanup, or tenant mutation. It does not
  require any sibling architecture skill and does not require a graph, HTML
  report, script, client-specific cache path, fixed filename, or fixed JSON
  shape.

Use `references/odc-platform-guardrails.md` when a request touches layering,
public services, anonymous access, server trust, query performance, timers,
background processing, imports, async retry, bulk work, API contract changes,
any relationship to a user — ownership, "my &lt;records&gt;", created-by,
assigned-to, per-user filtering, or a foreign key to the platform `User` entity
— or an action taking a record id that may not exist, including a 500 on a
missing row, a delete reporting success for a row that never existed, or a
not-found refusal that never fires.
This suite complements current official docs and `outsystems-tech-content`; it
does not replace them for implementation authority.

## Deployment preview readiness handoff

Use OMI for a deployment preview readiness handoff when a colleague asks whether
an implementation block is ready for a safe-to-promote or promotion-readiness
discussion. OMI can organize current source/target revision evidence, freshness,
published-source proof, ODC Portal impact-analysis status, warnings, blockers,
unknowns, and fallback behavior.

This is an advisory handoff, not deployment approval. Prompt-only OMI output and
unpublished Mentor changes are current-state baseline only. They do not prove a
pending change is safe to promote.

OMI does not require `outsystems-deploy-preview`, does not invoke
`outsystems-deploy-preview`, and does not use sibling skill scripts, templates,
or cache paths. If a deployment preview report already exists, treat it as
optional external evidence and still preserve the ODC Portal impact analysis
boundary for warnings and blockers.

## Visual-source blueprint path

For Figma, screenshot, HTML mockup, and design-brief UI work, OMI owns a
portable enriched blueprint artifact at
`assets/visual-source-enriched-blueprint.json`.
This is the primary structured input for higher-fidelity UI prompting.
It stays portable across Codex and Claude without hidden local cache paths,
client-specific integration wording, or automatic tenant mutation.

## Related skills and surfaces

| Surface or skill | Relationship |
|---|---|
| Mentor Web | Separate prompt-to-app generation surface: prompts or requirement documents become a blueprint for review before generation. This README does not publish a colleague-ready Mentor Web skill dependency. |
| MCP `app_create` | The other origination route, in this skill's own hands: template-backed by default since ODC MCP 0.14.0 (Studio new-app-wizard parity), blank only on the `blank` opt-out. Needs explicit approval and the Shell Provenance Gate before any first-scaffold prompt. |
| Mentor Studio / ODC Studio | This skill prepares Studio-native implementation blocks and paste-safe prompts for existing implementation work or an app-shell first scaffold. Mentor still executes interpretively, so results must be reviewed in Studio. |
| Superpowers planning | Use the Superpowers `writing-plans` skill, available to both Claude and Codex, or an equivalent planning workflow to create a saved implementation plan before using this skill for Studio-native deterministic intent blocks. |
| App-shell first scaffold | OMI-owned mode for an empty or newly created shell after the app key is verified. Use any reviewed source artifact as input, and stop before shell creation or Mentor execution unless that exact action is approved. Since ODC MCP 0.14.0 an approved `app_create` mints a template-backed shell, so a no-shell ask can be served here end to end; keep prompt-to-app and requirement-document generation in Mentor Web. |
| Codex and Claude | Both agents should read the same canonical repo source and keep private config/cache/plugin data out of the shared skill. |

## Full implementation plan workflow for colleagues

For colleague use, do not depend on the maintainer's personal planning shortcuts. Use the
portable capability instead:

1. Write a saved implementation plan with the Superpowers `writing-plans` skill
   (`superpowers:writing-plans` in Codex, and the same Superpowers planning
   skill in Claude) or with an equivalent planning workflow.
2. Run the OutSystems coverage-review pass below against the original
   request/PRD and the saved plan.
3. Patch the plan with minimal changes until the coverage review is acceptable.
4. Use `outsystems-plan-to-mentor` for the coverage gate and
   `outsystems-mentor-implementation` only for Studio-native
   deterministic-intent blocks or paste-safe Mentor Studio prompt content.
5. Stop before any Mentor execution, publish, deploy, rollback, package, push,
   PR, promotion, or tenant mutation unless the user explicitly approves that
   exact action.

Reusable coverage-review prompt:

```text
Using the original request/PRD already in this conversation as the source of truth, audit the plan you just produced for coverage and alignment.

For each major requirement you can infer from the request:

* mark it Covered / Partial / Missing
* briefly cite where it's addressed in the plan (section name or a short quote). If you can't point to evidence, treat it as Partial or Missing.

Then:

1. Give a simple coverage score (0-100) and a 1-2 sentence rationale.
2. List the top gaps (missing, partially covered, or unclear assumptions), prioritized by impact.
3. Produce a patched version of the plan that closes those gaps with minimal changes, preserving the original structure where possible (add/adjust sections rather than rewriting everything).
```

## Colleague prerequisites

The user needs **one** knowledge provider, not a specific one — either provider
is enough to run the skill. The skill detects which one is present at preflight
and adjusts what it is willing to claim; nothing to configure.

- **`provider: implementation-authority`** — `outsystems-tech-content` is
  callable (`search_outsystems_content`). Full implementation-level authority:
  function signatures, TrueChange and platform errors, widget-library rules and
  UI pattern APIs. Employee-only, and the MCP itself sits behind the OutSystems
  VPN.
- **`provider: public-grounded`** — a public knowledge-provider role is callable
  (see `references/knowledge-provider-contract.md`): the maintainer may bind
  `workspace-knowledge-cc`; a colleague may bind `outsystems-public-knowledge`.
  Public OutSystems documentation only, no VPN, no employee account. The skill
  still produces pseudocode and Mentor Studio prompts, under a narrower and
  explicitly stated authority.
- Direct access to cloned/local `docs-howtos`, `docs-odc`, `docs-product`, and
  `outsystems-ui` matters only when neither provider is available.

Required behavior boundary:

- detect the provider from the callable tool set, preferring
  `outsystems-tech-content` when both are present
- in `provider: public-grounded`, say so in one line wherever the answer names
  its sources, never present public grounding as implementation-level
  authority, and fail closed — name the gap, keep the claim `Unverified gap` —
  on TrueChange error text, internal/courseware/archive/workshop evidence, and
  widget rules beyond the skill's generated catalogs
- only when neither provider is available: ask whether to proceed with degraded
  quality, and do not produce pseudocode or Mentor Studio prompts until a
  provider is confirmed or the user explicitly accepts the degraded-quality risk
- provider availability determines the mode, not the machine owner or alias;
  both aliases expose the same public retrieval role
- if neither provider is available, use `docs-howtos`, `docs-odc`,
  `docs-product`, and `outsystems-ui` as an explicitly degraded, source-backed
  fallback instead of treating model memory as evidence

Current sharing position:

- canonical Tier 1 skill in this repo
- portable for any colleague with a public-provider alias — no VPN required and
  no OutSystems employee account; `outsystems-tech-content` raises the ceiling
  rather than being the entry price
- the approved four-repository set remains an explicitly degraded fallback for
  when neither provider alias is available
- not a standalone offline skill without a provider or the source-backed
  approved four-repository fallback set

## Porting the retrieval stack to another machine

For public OutSystems grounding, use the available public knowledge-provider
role. The maintainer may bind it to `workspace-knowledge-cc`; a colleague may bind it to
`outsystems-public-knowledge`. Both expose the same public retrieval role.
Provider availability determines the mode, not the machine owner or alias.

For another machine, recreate the useful parts of that retrieval stack in this
order. Step 1 alone is a working setup:

1. **Install `outsystems-public-knowledge` for the public-provider role.** This
   is the baseline path and needs no VPN and no employee account. It supplies
   indexed access over the four approved public repositories and puts the skill
   in `provider: public-grounded`. It does not replace `outsystems-tech-content`
   and does not supply restricted function signatures, widget rules, or
   TrueChange authority.
2. **Add `outsystems-tech-content` as an optional upgrade when the colleague is
   an OutSystems employee.** This MCP is employee-only, uses a private
   OutSystems network endpoint, and requires VPN access. It is not needed to run
   the skill; it raises the ceiling to `provider: implementation-authority` and
   provides strong implementation coverage such as ODC documentation
   (`docs-next`), EAP docs, training, `model-functions`, `model-truechange`,
   `widget-library-rules`, `outsystems-ui-api`, Mobile UI component facts, and
   synthesized best-practice material. When it is present the skill prefers it
   automatically — there is nothing to switch.
3. **Keep the four public OutSystems source repos as the explicit degraded
   fallback.** If neither provider alias is available, clone or locate these
   repos for auditable, source-backed grounding:

   ```bash
   mkdir -p ~/outsystems-public-sources
   cd ~/outsystems-public-sources
   git clone https://github.com/OutSystems/docs-odc.git
   git clone https://github.com/OutSystems/docs-howtos.git
   git clone https://github.com/OutSystems/docs-product.git
   git clone https://github.com/OutSystems/outsystems-ui.git
   ```

4. **Make the cloned repos searchable by the agent.** Best quality is a local
   retrieval/search MCP or equivalent index over those repos. Minimum acceptable
   fallback is telling the agent the clone root and requiring source-backed
   `rg`/file reads before it emits ODC product or implementation claims. Do not
   rely on model memory alone.

The public knowledge-provider role and `outsystems-tech-content` are
complementary, not aliases or substitutes. The public role supplies repo-backed
product grounding. The VPN-gated technical-content provider supplies restricted
implementation-authority checks such as function signatures, TrueChange
messages, and widget constraints. It is only a partial substitute for
repo-backed public source search because it may not provide arbitrary local
cross-file inspection, colleague-specific repo branches, offline auditability,
or a public-only evidence boundary by default. When results include internal or
restricted visibility, do not paste that content into external or broadly
shareable artifacts.

Example setup prompt for a colleague to paste into Codex, Claude, or another
agent:

```text
Help me set up the OutSystems retrieval stack for the `outsystems-mentor-implementation` skill on this machine.

Context:
- One provider is enough to run the skill. The public provider needs no VPN and no OutSystems employee account.
- `outsystems-tech-content` is an optional upgrade: employee-only, reachable only on the OutSystems private network (the endpoint is published internally, deliberately not here), so it will not work without VPN access. Skip it if either of those does not apply to me.
- Do not edit another agent's private config/cache/plugin data unless I explicitly approve that exact file and change.

Tasks:
1. Check for the public-provider role under either `workspace-knowledge-cc` or `outsystems-public-knowledge`; use whichever is available. If neither is installed, set up `outsystems-public-knowledge` — this is the baseline path and the only step most machines need.
2. Verify the public provider with one harmless read-only `search_outsystems_public` query for ODC documentation, then `fetch_doc` on a returned `doc_id`.
3. Only if I am an OutSystems employee who can connect to the VPN: check whether the session exposes `outsystems-tech-content` tools such as `check_health`, `list_collections`, `explain_filters`, and `search_outsystems_content`. If they are missing and I want the upgrade, tell me to connect VPN and configure the MCP using this agent host's normal MCP setup flow with the internal endpoint from the employee setup note (deliberately not published here), then start a fresh agent session if this host only loads MCP tools at startup. Verify with `get_status` (a bare `check_health` call is rejected — "Invalid request parameters"), then `list_collections`, then one harmless read-only `search_outsystems_content` query.
4. If neither provider is available, clone or locate the public repos `OutSystems/docs-odc`, `OutSystems/docs-howtos`, `OutSystems/docs-product`, and `OutSystems/outsystems-ui`, and record their local root so the agent can use source-backed `rg`/file reads as an explicitly degraded fallback. Do not rely on model memory alone.
5. Explain clearly whether the machine has full-quality retrieval, degraded retrieval, or is blocked. Public-provider-only is a supported working setup, not a degraded one — report it as `provider: public-grounded`, not as a failure.
```

## Evidence boundaries and accepted risks

The current colleague-sharing position is controlled internal sharing, not a
blanket production guarantee.

- Campaign 1 proved broad readiness across routing, Studio-native pseudocode,
  hardening, UI prompt contracts, Data Grid references, generated-app snapshot
  intake, evidence rules, and an in-memory Mentor probe.
- Campaign 2 proved a bounded non-production live validation path for controlled
  internal sharing. Detailed campaign mechanics remain maintainer evidence, not
  colleague quick-start guidance.
- Fixture-only, dry-run, or generated-reference evidence must not be promoted to
  current product-contract authority without separate official docs, catalog
  facts, implementation-reference evidence, or tenant observation.
- Remaining future tests such as successful rollback rehearsal, non-trivial live
  Studio logic changes, Data Grid dependency wiring, authenticated-only visual
  inspection, generated-app snapshot intake, and plan-to-Mentor integration are
  useful follow-ups, but they are not blockers for controlled colleague sharing.

## Post-OMI4 uncovered gaps

OMI is ready for controlled internal sharing, not a blanket production
guarantee. The post-OMI4 uncovered gap roadmap keeps production-grade lifecycle
claims approval-gated and evidence-driven.

Use `references/omi-uncovered-gap-roadmap.md` when a request asks whether OMI
has proven promotion, rollback rehearsal, authenticated runtime journeys,
external-library lifecycle, mobile or agent runtime execution, complex
refactors, security/performance/load execution, MCP blind-spot coverage, or
colleague portability outside the controlled internal environment.

## Codex and Claude compatibility

Codex and Claude should use the same canonical skill source for this skill. The
shared contract is `SKILL.md`, this README, and the `references/` and `tests/`
in this directory.

Keep the shared skill agent-neutral:

- Do not put Claude-specific config, command files, cache paths, plugin data, or
  install-time behavior into the shared skill.
- Do not put Codex-specific config, session paths, plugin cache details, or
  private MCP setup into the shared skill.
- Keep Codex adapter metadata isolated to `agents/openai.yaml`.
- When a workflow differs by agent, describe the portable behavior in plain
  capability names, not agent-specific tool names.
- If compatibility needs a local install check, inspect the symlink or installed
  copy without editing private config, plugin cache, command files, or plugin
  data.
- Maintainer-only review prompts and evidence references remain in
  `references/` for improving this skill, but they are not colleague
  prerequisites and are not required for normal single-agent use.

## Expected evidence order

The skill expects the agent to retrieve OutSystems evidence in this order
before final output:

1. the available public-provider role (see
   `references/knowledge-provider-contract.md`), bound to either
   `workspace-knowledge-cc` or `outsystems-public-knowledge`
2. only when neither provider alias is available, direct access to
   `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` as an
   explicitly degraded, source-backed fallback
3. the separate, VPN-gated `outsystems-tech-content` implementation-authority
   provider
4. current public/official OutSystems docs already routed by the skill

Use `outsystems-ui` as OutSystems-public implementation evidence, not as
current ODC product-contract authority unless current ODC docs, Forge
routing/version evidence, or tenant observations confirm the exposed behavior.

Minimum `outsystems-tech-content` queries for implementation work:

These apply in `provider: implementation-authority` only. In
`provider: public-grounded` they are not reachable, and the four lookups below
split two ways: built-in function syntax and the widget/pattern facts already in
the skill's generated catalogs stay groundable from public documentation, while
TrueChange errors and widget-library rules beyond the catalogs fail closed as
`Unverified gap`.

- Built-in function syntax: `content_source='model'` targets `model-functions`
  (also public — the docs-odc mirror carries the full built-in function
  reference at `src/eap/reference/built-in-functions/`)
- TrueChange errors: `content_source='model'` targets `model-truechange`
- Widget nesting rules: omit `content_source` (reaches `widget-library-rules`)
- UI pattern APIs: omit `content_source` (reaches `outsystems-ui-api`)
- No `collection` parameter exists — scope with `version` (odc/o11),
  `content_source` (documentation/training/model/web), `authority_level`,
  or `owner`; omit all filters for broadest coverage

Use the MCP discovery helpers to keep this guidance current:

- `get_status`: verify the service before declaring a source gap after errors
  or unexpectedly weak search results (a bare `check_health` call is rejected
  with "Invalid request parameters")
- `explain_filters`: confirm valid `version`, `content_source`,
  `authority_level`, `owner`, and `visibility` values before choosing filters
- `list_collections`: discover available evidence families; Do not pass
  collection names as a `collection` argument to `search_outsystems_content`
- `include_full_content`: request only when exact wording or parameter tables
  are needed; cite `page_url` when present
- Missing `page_url` usually means unpublished reference material, so preserve
  that evidence boundary and do not treat internal/restricted `visibility`
  results as externally shareable content without saying so
- If a `content_source='model'` query returns no results, run `get_status`
  and retry without `content_source` before declaring a source gap. An empty
  model-filtered result does not prove `model-functions` or `model-truechange`
  has no relevant coverage; surface the implementation-authority gap in the
  final Evidence Status or degraded-quality note.

## What the agent needs from you

For the skill to work well, include these facts in your prompt when you know
them:

- whether the target is Mentor Studio or Studio-native pseudocode
- whether the work is UI, data, integration, workflow, or agentic
- the existing app, screen, action, entity, or block names when they already
  exist
- whether the request is allowed to pause for degraded-quality approval when no
  provider at all is available
- where fallback docs live if neither public-provider alias is available

If `outsystems-tech-content` is missing but a public provider is callable, the
skill continues in `provider: public-grounded`: it states the narrower
public-docs grounding and fails closed on the internal-only lookups rather than
pausing. It pauses and asks only when no provider at all is available. If
neither public-provider alias is available, switch to the four approved
official/source-mirror repositories as an explicitly degraded fallback instead
of improvising or using model memory.

## Quick-start prompts

### Deterministic intent from a PRD

```text
Use the `outsystems-mentor-implementation` skill in structured intent mode.

Source requirement:
<paste the PRD, user story, meeting notes, or requirement document>

Goal:
- Convert this into a reviewable Studio-native deterministic-intent plan.
- Include entities, static entities, roles, screens, actions, validations, data behavior, evidence status, unknowns, and fallback behavior.
- Do not run Mentor, publish, deploy, rollback, package, push, PR, or mutate any tenant.

Constraints:
- Use current OutSystems evidence only.
- If `outsystems-tech-content` is unavailable but a public provider is, continue in `provider: public-grounded`. Pause and ask whether to proceed with degraded quality only when no provider at all is available.
- Treat this as a proposed structured-intent workflow, not a current private Mentor API.
```

### Existing app Mentor Studio prompt

```text
Use the `outsystems-mentor-implementation` skill to prepare a paste-safe Mentor Studio prompt for this existing ODC Web app.

Target:
- App: <app name/key if known>
- Screen/action/entity/block: <target names if known>

Goal:
- <describe the exact implementation change>

Constraints:
- Verify the runtime boundary first.
- Use `references/source-map.md` and the Mentor hardening guidance for screen-targeting, data writes, JSON deserialize, status values, UI buttons, or dependency-sensitive prompt blocks.
- If target identity depends on tenant inventory or cached tenant evidence, include a Tenant Context Packet with target app name, canonical app key, environment, and evidence freshness.
- If an app overview, app documentation, or app architecture summary artifact is supplied, reduce it to Existing App Structure Evidence for target grounding, named-element confidence, dependency inventory, library and AI model connection dependency hints, and unknowns; do not treat it as exact Studio internals or as a dependency on any sibling architecture or documentation skill.
- Do not run Mentor or mutate the tenant. Output the prompt/spec only.
```

### Review-gated validation handoff

```text
Use the `outsystems-mentor-implementation` skill to prepare a reviewable validation handoff for this implementation block.

Goal:
- Summarize what should be reviewed before Mentor execution or manual Studio implementation.
- Include the target app/screen/action/entity names, expected behavior, evidence status, unknowns, and acceptance checks.

Boundaries:
- Do not run Mentor, publish, deploy, rollback, package, push, PR, promotion, or mutate any tenant.
- Keep the handoff usable by a single colleague using either Codex or Claude.
- Do not require a second coding agent or any personal maintainer-only review loop.
```

### Deployment preview readiness handoff

```text
Use the `outsystems-mentor-implementation` skill to prepare a deployment preview readiness handoff for the Inventory Portal app from Development to Test.

Goal:
- Summarize whether current tenant evidence supports a safe-to-promote discussion.
- Separate prompt-only or unpublished work from published source revision evidence.
- Include source revision, target revision, target environment, freshness, classification, revision gap, ODC Portal impact-analysis status, warnings, blockers, unknowns, and fallback behavior.

Boundaries:
- Do not run Mentor, publish, deploy, rollback, cleanup, promotion, or mutate any tenant.
- Do not require or invoke `outsystems-deploy-preview`.
- If an external deployment preview report is already available, treat it as optional advisory evidence only.
```

## Prompt template

Use this when you want a generic prompt that works for Codex, Claude, or
another agent that can read the skill:

```text
Use the `outsystems-mentor-implementation` skill for this ODC implementation task:

<describe the target app, screen, action, or logic block>

Goal:
- <describe the Studio-native output needed>

Constraints:
- Use current OutSystems evidence only.
- Use the available public-provider alias: `workspace-knowledge-cc` or `outsystems-public-knowledge`.
- If `outsystems-tech-content` is unavailable but a public provider is, continue in `provider: public-grounded`: state the narrower public-docs grounding and fail closed on TrueChange error text, internal/courseware evidence, and widget rules beyond the generated catalogs.
- If neither alias is available, use `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` as an explicitly degraded grounding fallback; do not rely on model memory alone.
- If no provider at all is available, ask whether to proceed with degraded quality instead of continuing silently, and do not continue in degraded mode unless I explicitly accept that risk.

Known context:
- Existing app/screen/action names: <if known>
- Runtime boundary hints: <if known>
- UI or integration constraints: <if known>

Before producing output:
1. Detect the provider: `search_outsystems_content` first, else `search_outsystems_public` (`workspace-knowledge-cc` or `outsystems-public-knowledge`).
2. If only the public provider is available, run `provider: public-grounded` — do not stop and do not ask me to connect VPN.
3. If neither is available, use source-backed reads from `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` as an explicitly degraded fallback, and ask whether I want to proceed with degraded quality.
4. Retrieve the minimum current OutSystems evidence needed for this task.

Final output should follow the skill's normal response contract.
```
