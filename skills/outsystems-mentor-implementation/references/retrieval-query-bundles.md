# Retrieval Query Bundles

Use this source owner when `outsystems-mentor-implementation` needs fresh
OutSystems evidence before writing Studio-native pseudocode, Mentor Studio
prompts, or review guidance. Runtime guides should route here instead of
duplicating detailed retrieval recipes.

Where a recipe below says "the knowledge-provider," resolve `grounding_search`
through the role→tool binding table in
`references/knowledge-provider-contract.md`. For public grounding,
`workspace-knowledge-cc` and `outsystems-public-knowledge` expose the same
public retrieval role; use whichever provider is available. If neither is
available, the four approved local repositories are an explicitly degraded
fallback and require source-backed search and reads rather than model memory.

`outsystems-tech-content` is named directly everywhere below. It remains a
separate, VPN-gated, non-substitutable gate for internal notes, courseware,
archives, workshops, and implementation authority; it is not part of the
public-only knowledge-provider contract. If it is unavailable, keep dependent
claims `Unverified or blocked`.

Bundle aliases used by runtime docs and tests: widget catalog refresh, security
and roles, performance and queries, agentic and guardrails.

## Public-provider query shaping

This applies to `search_outsystems_public` in either binding, and matters most
in `provider: public-grounded` mode, where it is the only retrieval available.

The retriever is lexical, not semantic. Its query builder ANDs every
non-stopword token, so a long sentence becomes a conjunction that must match
every word in one document; when it misses, the fallback is a bag-of-words OR
over the same tokens plus adjacent bigrams, then a final re-sort by score.

Measured on 2026-08-07 rather than assumed, and confirmed against the real OPK
four-repo corpus (2633 documents) — short and long queries fail differently,
and neither dominates. On the clean OPK corpus the gap is narrower than on a
wider index: long intent sentences retrieve well there, so treat them as a
legitimate second pass rather than a degraded phrasing.

- **Short is better for precision on a known target.** "Mentor Studio
  capabilities" put the target doc at #1-2; the bundle's full intent sentence
  pushed it out of the top 5 entirely. "Data Grid widget" returned two ODC Data
  Grid docs where the long sentence returned none.
- **Long is better for recall.** On the TrueChange bundle the long intent
  sentence surfaced `docs-odc/src/error/aisa/mentor-studio-errors.md` at #1
  (score 41) — a real ODC error catalog that the short query missed completely.
- **A long query still returns relevant hits**, not nothing. The OR fallback
  plus score re-sort keeps results topical; the cost is diluted ranking, not an
  empty result set.

Shape queries accordingly:

- **Start short, then broaden.** Open with three to six content words for the
  specific fact you need. If the top hits are thin, generic, or only
  incidentally on-topic, re-run with the bundle's fuller `Exact search intent`
  phrasing as a recall pass — it reaches adjacent docs a narrow query cannot.
  Treat the two as complementary passes, not right-and-wrong phrasings.
- Use the docs' own vocabulary: product nouns as OutSystems spells them
  (`Data Action`, `Service Action`, `Aggregate`, `Timer`, `Trigger Event`).
  Two-word product terms are exactly what the bigram fallback handles best.
- Keep one concept per query in the short pass. Run several narrow queries and
  merge rather than asking one broad question.
- Pass `platform='odc'` unless the question is deliberately about O11. This is
  load-bearing, not a nicety: **two thirds of the public corpus is O11**
  (measured on the real four-repo corpus — 1780 of 2633 documents; `docs-product`
  is an O11 corpus), so the filter removes most of the index before ranking.
  Without it, the O11 `docs-product` built-in-functions page outranks the ODC
  one for "Index text function". Caveat, now quantified: the filter excludes
  documents tagged `o11` but not the few with empty platform metadata — **8 of
  2633, about 0.3%** — so it narrows the field very sharply without being a
  hard guarantee. Spot-check a hit's platform when a claim rests on it; you do
  not need to check every hit.
  **That measurement is corpus-specific, and the two provider bindings do not
  share a corpus.** It was taken on the packaged public component's four-repo
  index, which is what a colleague installs. A maintainer binding pointed at a
  full workspace indexes far more than those four repos — courseware and
  archived material included — and much of that carries no platform tag, so
  `platform='odc'` filters far less of it away: an ODC-phrased query there has
  been observed returning five O11 documents out of five. The tool name and
  call signature are interchangeable between bindings; **the corpus behind them
  is not**, and neither is this number. Re-measure before trusting it on a
  binding other than the packaged component.
- Relative score is a usable signal. On this corpus, well-covered topics score
  roughly 25-70 while incidental keyword matches score under about 12. A top
  hit far below the others' range usually means the corpus does not really
  cover the fact, not that the phrasing was wrong.
- An empty or weak result from a short, well-spelled query is weak evidence of
  a corpus gap. Broaden per the two-pass rule and try the term's documented
  synonym before calling it a gap, and say which queries were run when you do.

Do not run live tenant mutation tools from these bundles. Tenant evidence is
read-only unless the user gives exact current approval for a separate live action.

## Authority Classes

- `Current official`: current OutSystems docs, official source mirrors, or
  current tool/tenant observations that directly expose the fact.
- `approved internal`: approved internal OutSystems documentation or courseware
  returned only through VPN-gated `outsystems-tech-content`.
- `tenant-observed`: read-only observation from tenant context, Studio state, or
  MCP context tools; use only for the specific observed tenant/app/screen.
- `OutSystems-public implementation evidence`: public implementation-reference
  facts, such as `OutSystems/outsystems-ui`, that support review notes but are
  not current ODC product-contract authority by themselves.
- `degraded check`: a bounded retrieval run where a preferred source is
  unavailable; document the gap and stop rather than speculate when the missing
  source controls correctness.

## Mentor Studio capability refresh

- Exact search intent: refresh current Mentor Studio capabilities, open asset
  types, known limitations, and stop conditions before claiming what Studio can
  edit.
- Preferred tool order: the knowledge-provider's `grounding_search` with
  `scope="public"` first, then VPN-gated `outsystems-tech-content` for approved
  internal Mentor notes and implementation-authority details.
- Authority class: `Current official` for public docs and official mirrors;
  `approved internal` for internal Mentor capability notes; `tenant-observed`
  only for a specific read-only app/tool observation.
- Fallback behavior: if neither public-provider alias is available, use
  `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` only as a
  source-backed `degraded check`; if `outsystems-tech-content` is unavailable,
  keep internal Mentor and implementation-level claims `Unverified or blocked`.
- Stop condition: if current docs or approved internal evidence do not confirm
  the capability, stop rather than speculate and keep the claim `Unverified gap`.
- Tie-breaker: when the knowledge-provider and `outsystems-tech-content`
  disagree on a Mentor scope or capability fact, prefer the source with the
  more recent indexed, published, or last-updated timestamp and record both
  dates in the Evidence Status note.
- Expected OMI file owner: `references/mentor-capability-constraint-matrix.md`.

## Mentor Web capability refresh

- Exact search intent: refresh Mentor Web new-app generation, requirement
  document, blueprint, mobile app, and no-shell generation boundaries.
- Preferred tool order: the knowledge-provider's `grounding_search` with
  `scope="public"`, then VPN-gated `outsystems-tech-content` for approved
  internal Mentor notes and exact implementation boundaries that affect
  generated app follow-up.
- Authority class: `Current official` for current docs; `approved internal` for
  approved internal Mentor material; generated app snapshots are not authority.
- Fallback behavior: if VPN-gated `outsystems-tech-content` is unavailable or
  only generated, dry-run, or screenshot evidence exists, use the latter as
  example context only and keep internal claims `Unverified or blocked`.
- Stop condition: if the source does not distinguish Mentor Web from Mentor
  Studio, stop rather than speculate and route through the capability matrix.
- Tie-breaker: when the knowledge-provider and `outsystems-tech-content`
  disagree on a Mentor Web scope or capability fact, prefer the source with the
  more recent indexed, published, or last-updated timestamp and record both
  dates in the Evidence Status note.
- Expected OMI file owner: `references/mentor-capability-constraint-matrix.md`.

## Prompts and decomposition refresh

- Exact search intent: confirm prompt sizing, decomposition, structured intent,
  and block-level delivery guidance for complex source plans.
- Preferred tool order: current local OMI references first
  (`prompt-narrowing-preflight.md`, `structured-intent-mode.md`,
  `omi-route-mode-classifier.md`), then the knowledge-provider and
  `outsystems-tech-content` only when platform behavior or Mentor capability
  claims need external grounding.
- Authority class: local OMI references own deterministic workflow rules;
  the public knowledge-provider supplies `Current official` facts and VPN-gated
  `outsystems-tech-content` alone supplies `approved internal` product facts.
- Fallback behavior: if external retrieval is degraded, continue with local
  workflow discipline but do not add new product-contract claims.
- Stop condition: if decomposition would drop source-plan requirements, stop
  rather than speculate and return to the Plan Conversion Manifest.
- Expected OMI file owner: `references/prompt-narrowing-preflight.md`.

## Widget catalog refresh

- Exact search intent: refresh standard widget, OutSystems UI pattern, Data
  Grid, producer-bound widget, dropdown label, Table/List boundary, and
  pagination evidence before promoting a widget or pattern status.
- Preferred tool order: generated catalogs first
  (`odc-studio-widget-catalog.json`, `odc-ui-pattern-catalog.json`,
  `odc-data-grid-reference.json`), the knowledge-provider's `grounding_search`
  (`scope="public"`) second, `outsystems-tech-content` all-source search for
  widget-library rules and UI pattern APIs third, then public implementation
  references such as `outsystems-ui-implementation-reference.json`.
- Authority class: `Current official` for current public docs or current
  tenant/tool observation; VPN-gated `outsystems-tech-content` alone supplies
  `approved internal` docs. `Catalog-backed official` applies to generated
  official catalog facts; `OutSystems-public implementation evidence` applies
  to repo-only implementation details; `tenant-observed` applies to read-only
  app facts.
- Fallback behavior: keep `Unverified gap` visible when only contextual,
  O11-support, repo-only, generated, dry-run, or fixture evidence exists.
- Stop condition: new widget promotion requires focused tests and source
  references; without both, stop rather than speculate.
- Expected OMI file owner: `references/odc-ui-generation.md`,
  `maintenance/odc-ui-pattern-coverage-queue.md`, and the generated catalog
  artifact that owns the affected widget or pattern.

## Data binding and producer review

- Exact search intent: confirm source-like inputs, producer-first order,
  aggregates/data actions/list variables, option-list mapping, media URLs, and
  reusable producer dependencies before consumer UI emission.
- Preferred tool order: local producer-review reference first
  (`odc-data-bound-widget-producer-review.md`), then generated catalogs, the
  knowledge-provider's `grounding_search` (`scope="public"`) for binding
  concepts, and `outsystems-tech-content` for exact widget/API constraints.
- Authority class: `Current official` for current docs or current tenant/tool
  observation of named producers; `tenant-observed` for app-specific producer
  identity; `Unverified gap` for unconfirmed producer names.
- Fallback behavior: emit `Unknowns And Fallback Behavior` and ask for producer
  evidence when a source-like input would otherwise be empty.
- Stop condition: do not emit the consumer widget until the producer is named
  and the evidence label is explicit.
- Expected OMI file owner: `maintenance/odc-data-bound-widget-producer-review.md`
  and `references/odc-ui-generation.md`.

## TrueChange and platform errors

- Exact search intent: refresh TrueChange errors, warnings, platform validation
  behavior, unsupported nodes, empty required properties, and fragile Mentor
  Studio generation patterns.
- Preferred tool order: `outsystems-tech-content` with model-oriented search
  first for TrueChange and platform errors, broader `outsystems-tech-content`
  retry if model-filtered results are weak, the knowledge-provider's
  `grounding_search` (`scope="public"`) second, then local hardening
  references.
- Authority class: `Current official` or `approved internal` when returned by
  docs/approved sources; `degraded check` when technical content is unreachable.
- Fallback behavior: run health/filter checks when the technical-content endpoint
  is visible but weak; if unavailable, state degraded quality and do not invent
  exact error text.
- `provider: public-grounded` behavior: fail closed on TrueChange, but know
  what the corpus does carry. Measured 2026-08-07: the public corpus mentions
  TrueChange only incidentally (top hits score 7.7-10.5, all passing
  references), so TrueChange validation error codes and exact error text are
  NOT retrievable in this mode — name the gap, keep the claim `Unverified gap`,
  and do not substitute a plausible-looking message. What IS public is the
  Mentor and platform *service* error catalogs under `docs-odc` `src/error/`
  (`aisa/` Mentor Studio, `aica/` Mentor Web, `ctxs/` context service) — the
  `OS-AISA-*` family this skill's Mentor invocation discipline already cites,
  including `OS-AISA-40001`. Ground those from public docs and label them
  normally; keep them distinct from TrueChange validation errors, which they do
  not cover.
- Stop condition: if the error behavior affects correctness and no authoritative
  source confirms it, stop rather than speculate.
- Expected OMI file owner: `references/odc-mentor-hardening.md`.

## Security and roles

- Exact search intent: refresh role checks, anonymous/registered access,
  server-trust boundaries, public service exposure, CSP/secrets handling, and
  role-specific UI or Server Action guidance.
- Preferred tool order: the knowledge-provider's `grounding_search` with
  `scope="public"`, then VPN-gated `outsystems-tech-content` for approved
  internal security/courseware and implementation details, then tenant context
  only when a specific app's roles are observed read-only.
- Authority class: `Current official` for current docs; `approved internal` for
  approved security guidance; `tenant-observed` for a named app's read-only role
  inventory.
- Fallback behavior: if VPN-gated `outsystems-tech-content` is unavailable, keep
  internal security/course claims `Unverified or blocked`; if app-specific role
  assignments are not observed, keep them unknown and do not infer role
  membership from names.
- Stop condition: stop rather than speculate when authorization behavior affects
  data exposure or tenant mutation safety.
- Expected OMI file owner: `references/odc-platform-guardrails.md` and
  `references/tenant-context-guardrails.md` for app-specific evidence.

## Performance and queries

- Exact search intent: refresh Aggregate/SQL placement, query pre-mortem,
  indexing, pagination, N+1/loop query risks, bulk work, and data-fetch
  performance guardrails.
- Preferred tool order: the knowledge-provider's `grounding_search` with
  `scope="public"`, then VPN-gated `outsystems-tech-content` for approved
  internal performance/courseware and exact SQL/function details, then local
  platform guardrails.
- Authority class: `Current official` for current docs; `approved internal` for
  approved training/courseware; `degraded check` if implementation-authority
  search cannot run.
- Fallback behavior: if VPN-gated `outsystems-tech-content` is unavailable, keep
  internal performance/course claims `Unverified or blocked` and keep public
  guidance architectural and conservative when exact SQL or built-in function
  details are not confirmed.
- Stop condition: if exact syntax, transaction behavior, or data volume behavior
  controls the answer and retrieval is degraded, stop rather than speculate.
- Expected OMI file owner: `references/odc-platform-guardrails.md`.

## Timers, async, and events

- Exact search intent: refresh timers, event publishing/handling, idempotency,
  retries, background processing, imports, and distributed workflow boundaries.
- Preferred tool order: the knowledge-provider's `grounding_search` with
  `scope="public"`, then VPN-gated `outsystems-tech-content` for approved
  internal architecture/courseware and exact element and API details, then
  local platform guardrails.
- Authority class: `Current official` for current docs; `approved internal` for
  approved architecture material; `tenant-observed` only for app-specific
  read-only timer/event inventory.
- Fallback behavior: if VPN-gated `outsystems-tech-content` is unavailable, keep
  internal architecture/course claims `Unverified or blocked`; provide public
  placement guidance only when exact element syntax is unavailable and mark
  exact names or behaviors `Unverified gap`.
- Stop condition: stop rather than speculate if retry/idempotency behavior could
  duplicate writes or hide failed integration work.
- Expected OMI file owner: `references/odc-platform-guardrails.md` and the
  implementation-context guide section for the affected element.

## Agentic apps, AI model calls, guardrails, and evaluations

- Exact search intent: refresh agentic apps, AI model calls, `CallAgentV2`,
  `SendMessage`, A2A, guardrail configuration, evaluation datasets, and safety
  audit output requirements.
- Preferred tool order: the knowledge-provider's `grounding_search` with
  `scope="public"`, then VPN-gated `outsystems-tech-content` for approved
  internal agentic notes and exact element/API details, then local
  `agentic-routing.md`.
- Authority class: `Current official` for current docs; `approved internal` for
  approved internal agentic guidance; `tenant-observed` for a named app's
  read-only agent/model inventory.
- Fallback behavior: if VPN-gated `outsystems-tech-content` is unavailable, keep
  internal agentic claims `Unverified or blocked`; if guardrail or model-call
  specifics are not authoritative, output an Agent Guardrail Coverage Audit
  with explicit unknowns rather than a confident implementation recipe.
- Stop condition: for agentic and guardrails work, stop rather than speculate
  when safety, PII, harmful-content, or external-agent behavior is unclear.
- Expected OMI file owner: `references/agentic-routing.md`.

## outsystems-tech-content Call Conventions

Use `content_source='model'` to target `model-functions` and
`model-truechange` when the selected bundle needs built-in function syntax or
TrueChange/platform errors. For widget catalog refresh, widget nesting rules,
or UI pattern APIs, omit `content_source` unless the bundle says otherwise.
There is no `collection` parameter. Use `version`, `content_source`,
`authority_level`, and `owner` filters instead. Leave `visibility` unset by
default: the server derives a per-deployment visibility envelope, and omitting
the argument searches every tier that deployment allows, while naming one tier
narrows to it and drops the rest. Name a tier only to deliberately exclude the
others. `explain_filters` may state that omitting `visibility` short-circuits
to an empty result; measured against the live server 2026-08-31, omitting it
returns results blended across the served tiers, and the server's own
zero-result message tells the caller to drop the argument. Trust the measured
behavior over that sentence. When `outsystems-tech-content` discovery tools are
present, use `check_health`, `explain_filters`, `list_collections`, and
`include_full_content` according to the bundle. Do not pass collection names as
a `collection` argument. Cite `page_url` when present; when `page_url` is
missing, treat the hit as unpublished reference material and keep that boundary
explicit.

If a `content_source='model'` query returns no results, run `get_status` (it
reports the indexed collections and their chunk counts, so it separates a thin
collection from a bad filter; `check_health` takes no arguments and reports
liveness only) and retry without `content_source` before declaring a source
gap. An empty
model-filtered result does not prove `model-functions` or `model-truechange` has no relevant coverage; surface the implementation-authority gap in the final
Evidence Status or degraded-quality note.

A reachable provider can still return nothing for an instrument reason. Before
declaring any source gap, check whether the call passed `visibility`: a value
outside the deployment's envelope returns a zero-result message naming the
tiers actually served and telling the caller to drop the argument. That is an
instrument artifact, not missing coverage. Retry with `visibility` unset
before recording the gap.

For degraded checks that control exact signatures, widget rules, TrueChange
errors, live Mentor behavior, security roles, or tenant-specific facts,
stop rather than speculate.

## Degraded retrieval behavior

- Exact search intent: decide whether a retrieval gap blocks output, permits a
  conservative review-only answer, or requires the user to approve degraded quality.
- Preferred tool order: check the selected bundle's preferred tools first, then
  run available health/filter/discovery checks for the missing source. Do not
  mix direct docs or local mirrors into the normal provider-available order.
- Authority class: `degraded check` until the missing preferred source is
  restored or the claim is narrowed to evidence that was actually retrieved.
- Fallback behavior: when neither `workspace-knowledge-cc` nor
  `outsystems-public-knowledge` supplies the public retrieval role, use
  `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` only as an
  explicitly degraded, source-backed fallback; do not rely on model memory
  alone. For any other missing source, say which source was unavailable, which
  route-specific fallback was used, and which claims remain `Unverified gap`.
- Stop condition: stop rather than speculate whenever a missing source controls
  exact signatures, widget rules, TrueChange/platform errors, live Mentor
  behavior, security/role behavior, or tenant-specific facts.
- Expected OMI file owner: this file plus the route-specific reference that
  owns the affected output.
