# OutSystems Mentor Implementation — Source Map

## Handbook paths (repo-relative inside this portable skill)

- **Language-elements handbook** (exact syntax, element reference, coverage matrix):
  `references/odc-studio-language-elements.md`

- **Implementation-context guide** (architecture, placement, security, deployment, troubleshooting):
  `references/odc-studio-implementation-context.md`

- **Source manifest** (evidence coverage and auditability — open only for gap or source-audit questions):
  `references/odc-pseudocode-source-manifest.md`

- **Mentor Capability And Constraint Matrix** (current OutSystems documentation
  route owner for Mentor Web, Mentor Studio, known limitations, capability, and
  constraint claims):
  `references/mentor-capability-constraint-matrix.md`

- **Prompt Narrowing Preflight** (source owner for complex source-plan block
  decomposition, not plan shrinking; Plan Conversion Manifest;
  dependency-ordered blocks; coverage audit):
  `references/prompt-narrowing-preflight.md`

- **Route Mode Classifier** (source owner for OMI route-mode selection,
  stop/ask conditions, fallback behavior, no tenant mutation boundaries, and
  structured intent normalization):
  `references/omi-route-mode-classifier.md`

- **Retrieval Query Bundles** (source owner for retrieval recipes, evidence
  authority classes, fallback behavior, stop conditions, and expected file
  owners):
  `references/retrieval-query-bundles.md`

- **Live Execution Intake** (global source owner for optional live OutSystems
  MCP validation decisions, read-only resolution pass, direct MCP tool
  preference, degraded manual evidence boundaries, approval gates, sanitized
  evidence, and stop conditions):
  `references/live-execution-intake.md`

- **Live Target Evidence Matrix** (OMI3-derived target suitability, REST/API,
  Data Grid, agentic/integration, visual, screenshot-backed Studio evidence,
  no-default-entry, and rollback-unavailable gates):
  `references/live-target-evidence-matrix.md`

- **OMI Uncovered Gap Roadmap** (post-OMI4 uncovered production-grade,
  lifecycle, runtime, portability, and MCP-blind-spot boundaries):
  `references/omi-uncovered-gap-roadmap.md`

- **Evidence Status owner** (label definitions, source→label decision table,
  dry-run/fixture, `outsystems-ui`, and Forge-bridge rules):
  `references/omi-evidence-status.md`

- **UI generation guide**:
  `references/odc-ui-generation.md`

- **Visual-source UI discipline guide**:
  `references/odc-visual-source-ui-discipline.md`

- **Visual-source enriched blueprint guide**:
  `references/odc-visual-source-enriched-blueprint.md`

- **UI framework-selection guide**:
  `references/odc-ui-framework-selection.md`

- **UI prompt inventory**:
  `references/odc-ui-prompt-inventory.md`

- **Realistic UI acceptance coverage map**:
  `references/odc-ui-acceptance-coverage-map.md`

- **Generated ODC UI pattern catalog** (per pattern: names, properties, events,
  placeholders, compatibility and security notes, plus `client_actions` — the
  actions the official docs name for driving that pattern from an action flow.
  Also carries a top-level `accessibility_client_actions` block: the six
  framework-global actions under **Logic > OutSystemsUI > Accessibility**, which
  belong to no single pattern. Regenerate with
  `scripts/refresh_odc_ui_catalog.py --output <path>`, never by hand):
  `references/odc-ui-pattern-catalog.json`

- **Generated OutSystems UI implementation reference**:
  `references/outsystems-ui-implementation-reference.json`

- **Generated ODC Studio widget/block catalog**:
  `references/odc-studio-widget-catalog.json`

- **Generated O11 Designing Screens support catalog**:
  `references/o11-designing-screens-widget-catalog.json`

- **Generated ODC Data Grid reference catalog**:
  `references/odc-data-grid-reference.json`

- **Curated UI prompt recipes**:
  `references/odc-ui-prompt-recipes.md`

- **Real-app UI observed evidence**:
  `references/odc-ui-real-app-evidence.md`

- **Mentor hardening guide**:
  `references/odc-mentor-hardening.md`

- **ODC platform guardrails**:
  `references/odc-platform-guardrails.md`

- **Live Mentor campaign guidance**:
  `references/live-mentor-campaign-guidance.md`

- **Tenant context guardrails**:
  `references/tenant-context-guardrails.md`

- **Optional Mentor validation patterns**:
  `references/optional-mentor-validation-patterns.md`

- **Structured intent mode guide**:
  `references/structured-intent-mode.md`

- **App-shell first scaffold guide**:
  `references/odc-app-shell-first-scaffold.md`

- **Polish gate** (source owner for per-screen visual finish checks after the
  render gate: type hierarchy, brand-colour restraint, spacing, content
  realism, active state, heading semantics):
  `references/execution-gates.md` §2b

## Route by question type

| Question type | Open first |
|---|---|
| "What element do I use for X?" | Language-elements handbook → `## 3. ODC Studio Visual Elements` |
| "Where does this logic go?" | Implementation-context guide → `## 2. Architecture And Placement Rules` |
| "How do I design a Server Action / Data Action / Aggregate?" | Implementation-context guide → `## 3. Build And Design Guidance` |
| "How do I consume or expose a REST API?" | `references/live-target-evidence-matrix.md` first when the answer targets an existing app or claims current REST proof; otherwise Implementation-context guide -> `## 4. Integration And External Systems Guidance`; use `references/odc-platform-guardrails.md` for public API contract changes |
| "Architecture Layering Gate, Security Server-Trust Gate, User Reference Authoring Gate, Not-Found Guard Gate, Performance Query Pre-Mortem, Timer / Async Idempotency Gate, Public API Contract Gate, Deploy-Time Error Code Gate, Library Release Visibility Gate, layering, public services, anonymous access, server trust, query performance, Aggregate or SQL inside For Each, timers, background processing, imports, async retry, bulk work, API contract changes, **referencing the platform `User` entity — user ownership, 'my <records>', created-by/assigned-to, per-user filtering, or a foreign key to a user**, or **an action taking a record id that may not exist — update, cancel, delete, detail, 'not found', a row that was already removed, or a 500 on a missing row**" | `references/odc-platform-guardrails.md` first, then the affected implementation guide; use it as read-only prompt discipline, keep live Mentor/publish/deploy/tenant mutation behind explicit approval, and do not require any sibling architecture skill, graph report, cache path, script, fixed filename, or fixed JSON shape |
| "What are the transaction / commit rules?" | Language-elements handbook → `## 6. Execution And Transaction Semantics` |
| "Is this element supported / current / archived?" | Language-elements handbook → `## 8. Coverage Matrix And Verification Gaps` |
| "What system actions or built-in functions exist?" | Language-elements handbook → `## 4. OutSystems Language Catalog` |
| "App-shell first scaffold, blank app shell, first scaffold against a verified app key, bootstrap first entities/roles/screens into an existing or newly created shell, product-template shell, ODC manual empty shell, default template, Continue in ODC Studio, custom app template, Template_<app_name>, blank shell, template-incomplete shell, built-in application templates, missing Common UI flow, template-backed app_create, blank-shell opt-out, clonedFromTemplateKey, or create a new application correctly" | For visual-source first scaffold work, open `references/odc-visual-source-enriched-blueprint.md` first, then `references/odc-app-shell-first-scaffold.md` so the shell guide can consume that artifact for approval, product-template shell classification, ODC manual empty shell, ODC custom app template, and built-in application templates context, and boundary handling, then `references/odc-visual-source-ui-discipline.md`, then `references/odc-ui-framework-selection.md`, then `references/odc-ui-prompt-inventory.md`, then `references/odc-ui-generation.md`. For non-visual scaffold asks, start at `references/odc-app-shell-first-scaffold.md`, then `references/odc-mentor-hardening.md`, then the specific implementation guide for the affected elements. |
| "iterative shell-first rerun, repeat first scaffold against the same app, reuse app key, or delta prompt for existing shell" | `references/odc-app-shell-first-scaffold.md` first, then `references/odc-ui-generation.md` or the affected implementation guide; reuse the verified canonical app key, do not call `app_create` again unless explicitly approved, and keep publish behind the Post-Mentor Preservation Decision Gate |
| "Mentor Web new app generation, requirement document, blueprint refinement, no-shell app generation, or create app from scratch without a verified shell" | `references/mentor-capability-constraint-matrix.md` first, then `references/agentic-routing.md` for Mentor Web guidance; for "create app from scratch" also offer the shell-first route in `references/odc-app-shell-first-scaffold.md`, where an approved `app_create` mints a template-backed shell; either way, do not emit a Mentor Studio first-scaffold prompt until an app shell and verified app key exist |
| "route mode, output mode, classify OMI request, choose pseudocode versus Mentor prompt versus live validation, or decide whether this is review-only" | `references/omi-route-mode-classifier.md` first; use the Route Mode Classifier to choose `mode: studio-native-pseudocode`, `mode: mentor-studio-prompt`, `mode: mentor-web-orientation`, `mode: visual-source-ui`, `mode: existing-app-grounding`, `mode: live-validation`, or `mode: review-only`; apply structured intent normalization internally for complex work and do not mutate a tenant from classification |
| "full implementation plan artifact, coverage review, saved plan, Mentor-ready spec, approval gate, or plan-to-Mentor workflow" | Use `outsystems-plan-to-mentor`; do not produce a partial Studio pseudocode answer from this skill |
| "coverage-reviewed patched plan, plan-to-Mentor gate, Invocation mode: outsystems-plan-to-mentor" | Use `outsystems-plan-to-mentor` for the coverage gate; when this skill is already invoked with `Invocation mode: outsystems-plan-to-mentor`, open `references/prompt-narrowing-preflight.md`, build the Plan Conversion Manifest, use block decomposition, not plan shrinking, convert into dependency-ordered blocks, and run the coverage audit before Mentor-ready output; do not rerun the upstream coverage review |
| "complex source plan, long source plan, large feature request, design-source conversion, multi-block pseudocode output, plan-aware prompt sizing, or prompt narrowing for complex plans" | `references/prompt-narrowing-preflight.md` first; build a Plan Conversion Manifest, use block decomposition, not plan shrinking, preserve the source plan as the control artifact, split into dependency-ordered blocks, run the coverage audit, and emit one paste-safe Mentor prompt per block unless explicitly review-only |
| "Security, permissions, CSP, secrets" | Implementation-context guide → `## 5. Security And Enterprise Constraints` |
| "Debugging, testing, deployment order" | Implementation-context guide → `## 6. Debugging, Testing, Deployment, And Troubleshooting Guidance` |
| "Workflow publish, workflow revision messages, workflow merge conflicts" | Implementation-context guide → `## 6. Debugging, Testing, Deployment, And Troubleshooting Guidance` |
| "Timers, private gateway, SSO, REST config" | `references/live-target-evidence-matrix.md` first when the answer claims current target proof for timers, events, workflows, External Logic, or REST configuration; otherwise Implementation-context guide -> `## 7. Platform Management And Operational Implications` |
| "event proof, workflow proof, timer proof, current event asset, current workflow asset, current timer action, or current async asset proof" | `references/live-target-evidence-matrix.md` first when the answer targets an existing app or claims current event, workflow, timer, or async asset proof; then the affected implementation guide; if exact proof is missing, label `Unverified gap` and do not infer from nearby app evidence |
| "AI models, agents, agentic app, structured output, guardrails" | `references/live-target-evidence-matrix.md` first when the answer targets an existing app or claims current AI model, agentic, External Logic, timer, event, or workflow proof; then `references/agentic-routing.md`, then implementation-context guide -> `## 8. AI And Agentic Implementation Guidance` |
| "Agent Guardrail Coverage Audit, prompt attack/PII/harmful content, OS-ABRS-FM-40005, guardrail evaluation dataset" | `references/agentic-routing.md` first, then implementation-context guide -> `## 8. AI And Agentic Implementation Guidance`; include the audit only for AI/agentic output that materially changes safety risk |
| "Mentor Studio, Mentor Web, AI-assisted app generation, prompts, known limitations" | `references/mentor-capability-constraint-matrix.md` first, then `references/agentic-routing.md`, then implementation-context guide → `## 8. AI And Agentic Implementation Guidance`; keep claims grounded in current OutSystems documentation and do not promote generated, dry-run, fixture-only, or screenshot-only evidence |
| "retrieval refresh, retrieval source gap, degraded retrieval check, current evidence query, tool-order question, widget catalog refresh, TrueChange/platform errors, security and roles, performance and queries, timers/events, or agentic and guardrails retrieval" | `references/retrieval-query-bundles.md` first; use Retrieval Query Bundles for exact search intent, preferred tool order, authority class, fallback behavior, stop condition, and expected OMI file owner; if the selected bundle cannot ground the claim, stop rather than speculate |
| "live validation, optional OutSystems MCP validation, Live MCP validation, current tenant/tool behavior, read-only MCP evidence, direct OutSystems MCP tools, manual MCP-over-HTTP evidence, app_info, env_app, or decide whether live validation is needed" | `references/live-execution-intake.md` first, then `references/live-target-evidence-matrix.md` when the unresolved claim is target suitability or current target proof; run static docs, tests, and Claude review first, then a read-only resolution pass only when needed; use direct OutSystems MCP tools first, keep manual MCP-over-HTTP as degraded read-only evidence only, store sanitized evidence only, and require explicit current approval for `mentor_create_asset`, `mentor_prompt`, `mentor_publish` (pre-2026-09: `mentor_start` / `publish_start`), `deploy_start`, rollback, `app_create`, external-library upload, publish, deploy, or tenant mutation |
| "OMI1 live preflight, same-execution-context MCP, same execution context, live campaign MCP preflight, auth_status before live row, Computer Use / Claude fallback preflight, fresh evidence, or historical evidence is context only" | `references/live-execution-intake.md` first for the same-execution-context OutSystems MCP preflight and fresh-evidence boundary, then `references/live-mentor-campaign-guidance.md` for bounded Computer Use / Claude fallback readiness and `blocked-automation` behavior; keep durable queue/evidence artifacts in whatever review process owns the campaign |
| "OMI4 applied quality, proof/edit split, publish advisory, live row terminal status, or artifact reconciliation" | `references/live-execution-intake.md` first for the proof/edit split, publish advisory, broad metadata retry, runtime browser proof, and artifact reconciliation boundaries, then `references/omi-evidence-status.md` for live row terminal status taxonomy, then `references/optional-mentor-validation-patterns.md` for advisory validation and queue/state/readiness/feedback reconciliation |
| "OMI uncovered gaps, production-grade guarantee, not covered by OMI1/OMI2/OMI3/OMI4, promotion rehearsal, authenticated runtime journey, external-library lifecycle, complex refactor, Data Grid wiring, agent/mobile runtime execution, package/release, rollback rehearsal, MCP blind spot, or colleague portability limit" | `references/omi-uncovered-gap-roadmap.md` first; then open the narrower source owner for the affected area. Keep unproven capabilities as `Unverified gap`, read-only advisory, or explicit approval-gated work. |
| "target suitability, evidence matrix, OMI3 lessons, exposed REST proof, consumed REST binding proof, producer/API binding proof, Data Grid target proof, screenshot-backed Studio evidence, degraded visual evidence, no-default-entry proof, rollback-unavailable, or exact safe rollback proof" | `references/live-target-evidence-matrix.md` first; use it before confident Mentor Studio prompts or implementation-grade pseudocode when the answer depends on current target facts; if exact proof is missing, label `Unverified gap`, ask for the missing contract or target proof, and do not infer from generic dependencies, Service Actions, entity references, or runtime-adjacent evidence |
| "Studio visual proof, hidden screen/action layers, Data Grid event proof, External Logic call-site proof, timer branch proof, Agent asset proof, or MobileApplication proof" | `references/live-target-evidence-matrix.md` first; use it for Studio visual proof, Studio-proven hidden screen/action layers, Data Grid event handler evidence, External Logic call-site proof, timer branch proof, Agent asset proof, MobileApplication proof, asset-type boundaries, and runtime route exclusions |
| "publish-validator classifier, OS-APPS-40028 classification, RadioGroup or ButtonGroup duplicate children" | `references/odc-mentor-hardening.md` first; keep direct OML cache/chunk repair guidance out of OMI prompt output unless the user explicitly asks for direct OML pipeline analysis |
| "tenant inventory, tenant context guardrails, Tenant Context Packet, Existing App Structure Evidence, existing app target resolution, cached tenant evidence, app overview artifact, app documentation artifact, app architecture summary artifact, every-app scope expansion, tenant-backed dependency inventory, optional reverse dependency evidence, shared producer impact, shared producer blast radius, named element confidence, change mode matrix, shared producer compatibility, role/security evidence, or decide which existing app this belongs in" | `references/tenant-context-guardrails.md` first; use tenant context and existing app structure evidence as read-only target/dependency evidence only, tag named existing elements by confidence source, keep modes separate, require exact app identity and freshness before confident app-targeted prompts, ask before per-app deep dives, tenant-wide scans, or Mentor work across many apps, use shared producer impact as a scope brake, require a selected compatibility strategy before broad shared-producer behavior changes, do not infer role assignments, and do not infer exact Studio internals |
| "Run a live Mentor campaign, test against a real OutSystems target, use a dedicated fixture, add a reversible marker, publish, perform visual inspection, rollback, cleanup, or use Claude as a bounded authenticated MCP execution route" | `references/live-execution-intake.md` first, then `references/live-target-evidence-matrix.md`, then `references/live-mentor-campaign-guidance.md`, then `references/odc-mentor-hardening.md` for the exact Mentor prompt; keep queue, approval, review, and evidence control in whatever review process owns the campaign; no live Mentor, publish, deploy, rollback, cleanup, or tenant mutation by default |
| "This application does not contain a default entry, no-default-entry repair, default start screen, runtime URL has no default screen, MainFlow user screen default, default-entry bootstrap, minimal MainFlow > Home default-entry bootstrap, create-screen step for default entry, or approved fixture Home bootstrap" | `references/live-execution-intake.md` first for read-only app/context/revision evidence, then `references/live-target-evidence-matrix.md`, then `references/live-mentor-campaign-guidance.md` for empty-app versus non-empty app classification, MainFlow user-screen requirement, Common authentication-screen exclusion, default-screen repair boundaries, and the minimal approved `MainFlow > Home` bootstrap route, then `references/odc-mentor-hardening.md` only if the user approves a narrow Mentor prompt; do not mutate the tenant, create a screen, mark a screen default, publish, or combine the repair with marker/access work by default |
| "optional post-OMI validation, app-level audit after approved Mentor execution, post-Mentor report, validation menu, or publish handoff without publish approval" | `references/live-execution-intake.md` first when live MCP validation need or current tenant/tool evidence is in question, then `references/live-target-evidence-matrix.md` when current target suitability, degraded visual evidence, or rollback readiness is in question, then `references/optional-mentor-validation-patterns.md`; for already approved tenant-backed Mentor validation also open `references/live-mentor-campaign-guidance.md` and `references/odc-mentor-hardening.md`; do not treat `outsystems-mentor-copilot` as an OMI runtime dependency and do not publish or deploy by default |
| "deploy preview, safe to promote, promotion readiness, publish/deploy-adjacent readiness, what happens if I push/deploy this app to an environment, or deployment risk after OMI output" | `references/optional-mentor-validation-patterns.md` first for the OMI-owned read-only Deployment Preview Gate; route to `references/live-execution-intake.md` first if current tenant/tool validation beyond supplied read-only preview evidence is needed, then `references/live-target-evidence-matrix.md` for rollback readiness, exact safe rollback proof, degraded visual evidence, or current target suitability claims; if tied to approved live Mentor or publish work, also open `references/live-mentor-campaign-guidance.md`; use deployment preview evidence only when already available or explicitly supplied; OMI does not require, invoke, or route through `outsystems-deploy-preview`; prompt-only or unpublished changes are current-state baseline only, and safe-to-promote wording requires published source revision evidence; the gate does not deploy or replace ODC Portal impact analysis |
| "quality/security/performance/accessibility/test/docs/refactor/demo readiness/AI model migration review after OMI output" | `references/optional-mentor-validation-patterns.md` first; produce a bounded checklist or review prompt, not a tenant-changing action, unless the user explicitly approves tenant-backed Mentor execution |
| "Structured intent, Architect Mode, pseudocode mode, deterministic Mentor plan, PRD ambiguity demo, or current PRD flow versus structured plan demo" | `references/structured-intent-mode.md` first, then `references/odc-mentor-hardening.md`, then the specific implementation guide for the affected elements |
| "Generated App Snapshot Intake Mode, generated app snapshot, app-snapshot.yaml, studio-handoff.md, continue from generated app review, surgical fixes from Mentor Web generated app" | `../../shared/mentor-generated-app-bridge.md` first, then `references/source-map.md` for the affected implementation area |
| "A2A, Agent-to-Agent, external agents, SendMessage, agent card" | `references/agentic-routing.md` first, then implementation-context guide → `## 8. AI And Agentic Implementation Guidance` |
| "MCP servers, prebuilt connectors, external tools, unsupported MCP structures" | `references/agentic-routing.md` first, then implementation-context guide → `## 8. AI And Agentic Implementation Guidance` |
| "Agent evaluations, datasets, test conversations, evaluation criteria" | `references/agentic-routing.md` first, then implementation-context guide → `## 8. AI And Agentic Implementation Guidance` |
| "Exception handling, Raise Exception, Exception Handler, error flows" | Implementation-context guide → `## 3. Build And Design Guidance` (exception subsection) |
| "Screen lifecycle, On Initialize, On Ready, OnParameterChanged, On Destroy" | Language-elements handbook → `## 3. ODC Studio Visual Elements` (lifecycle subsection) |
| "Mobile UI, OutSystems UI versus Mobile UI, UI framework selection, mobile app UI generation, Phosphor icons, shared UI library, Mobile Library, Input OTP CSP, Mobile UI CSP, or OutSystems UI to Mobile UI migration" | `references/odc-ui-framework-selection.md` first; continue to `references/odc-ui-generation.md` only when generation is supported or catalog-backed guidance/review applies |
| "OutSystems UI ODC Forge documentation, Using Mobile and Reactive Patterns, or ODC/O11 OutSystems UI pattern documentation bridge" | `references/odc-ui-framework-selection.md` first, then `references/odc-ui-prompt-inventory.md` and `references/odc-ui-generation.md`; treat the Forge-to-O11 documentation link as current official routing evidence for OutSystems UI pattern docs, not as Mobile UI equivalence or repo-only source-code product-contract authority |
| "Figma, screenshot, HTML mockup, source HTML/CSS, screen mockup, written UI brief, visual-source UI prompt, or design-source UI discipline" | `references/odc-visual-source-enriched-blueprint.md` first. If the target is a verified blank shell, a first-scaffold shell, or a shell-creation path pending explicit approval, continue to `references/odc-app-shell-first-scaffold.md` so the shell guide can consume that artifact for approval and boundary handling, then `references/odc-visual-source-ui-discipline.md`, then `references/odc-ui-framework-selection.md`, then `references/odc-ui-prompt-inventory.md`, then `references/odc-ui-generation.md`. Otherwise continue directly to `references/odc-visual-source-ui-discipline.md`, then `references/odc-ui-framework-selection.md`, then `references/odc-ui-prompt-inventory.md`, then `references/odc-ui-generation.md`; build or validate the enriched blueprint before deriving the Visual-Source UI Prompt Packet and `### Mentor Studio Prompt`; treat the prompt packet as blueprint-derived preparation or summary, not a required extra visible output section; do not treat this route as Mentor Web no-shell app generation |
| "Create/modify a Screen, Web Block, standard widget, or UI pattern in Mentor Studio" | `references/odc-ui-framework-selection.md` first, then `references/odc-ui-prompt-inventory.md`; continue to `references/odc-ui-generation.md` only when generation is supported or catalog-backed guidance/review applies, then `references/odc-ui-prompt-recipes.md` only for supported paste-ready generation, then `references/odc-ui-pattern-catalog.json` for exact pattern facts |
| "Describe an uncommon ODC UI pattern for Mentor Studio" | `references/odc-ui-framework-selection.md` first, then `references/odc-ui-prompt-inventory.md`, then `references/odc-ui-generation.md` only when generation is supported or catalog-backed guidance/review applies, then `references/odc-ui-pattern-catalog.json`; label output `Catalog-backed official` unless a curated recipe exists |
| "Which realistic UI acceptance fixture should be added next, or what live-signature coverage is still weak?" | `references/odc-ui-acceptance-coverage-map.md` first, then `references/odc-ui-generation.md` and the existing `tests/fixtures/ui_prompts/web_acceptance_*.md` files |
| "Record a live Mentor execution miss, refine a realistic UI fixture from Mentor output, or decide whether a concrete miss should become coverage" | `references/odc-ui-generation.md` first → `## Live Execution Intake Checklist`, then `references/odc-ui-acceptance-coverage-map.md`; capture the concrete miss and add one narrow failing acceptance test before changing fixtures |
| "Need source-backed implementation evidence for an OutSystems UI pattern, dependency, event, placeholder, property, style family, deprecated/preview marker, or ODC/O11 variant not covered by current docs/catalog" | `references/odc-ui-framework-selection.md` first, then `references/odc-ui-prompt-inventory.md`, then `references/odc-ui-generation.md`, then `references/outsystems-ui-implementation-reference.json`; consult its top-level `gap_analysis` before drilling into individual entries when the question is about family discovery, SCSS coverage, non-`*Config.ts` TypeScript/API surface, deprecated/preview markers, or ODC/O11 implementation variants; keep output `OutSystems-public implementation evidence` when repo-only facts materially affect the answer and state they are not current ODC product-contract authority unless current ODC docs, Forge routing/version evidence, or tenant observations confirm the exposed behavior |
| "Generate UI prompts with producer-first order" | `references/odc-ui-framework-selection.md` first, then `references/odc-ui-prompt-inventory.md`; continue to `references/odc-ui-generation.md` only when generation is supported or catalog-backed guidance/review applies; use prompt blocks for supported paste-ready generation only; for supported web output use `### Mentor Studio Prompt` → `### Prompt Coverage Audit` → `### Studio-Native UI Spec` → `### Evidence Status` |
| "Standard widget, basic Form, Button, Input, Table, List, or Web Block UI prompt" | `references/odc-ui-framework-selection.md` first, then `references/odc-ui-prompt-inventory.md`, then `references/odc-studio-widget-catalog.json`, then `references/o11-designing-screens-widget-catalog.json` only when the widget entry has `o11_candidate_support`; use `references/odc-ui-generation.md` only after inventory selection; supported web output order is `### Mentor Studio Prompt` → `### Prompt Coverage Audit` → `### Studio-Native UI Spec` → `### Evidence Status` |
| "Data Grid, editable grid, advanced grid, changed rows, grid save action, or dependency-sensitive grid UI prompt" | `references/live-target-evidence-matrix.md` first when the answer targets an existing app or claims current Data Grid proof; otherwise start with `references/odc-ui-framework-selection.md`, then `references/odc-ui-prompt-inventory.md`, then `references/odc-data-grid-reference.json`; use `references/odc-ui-generation.md` after dependency and producer checks for generic/new prompts, and require route and visual proof only for existing-app or current Data Grid proof claims |
| "Real app UI evidence, compare generated UI pseudocode to an existing ODC app, benchmark a UI prompt against a tenant app, mine a tenant app for UI prompt examples, or decide whether an observed app pattern should become a recipe" | `references/odc-ui-generation.md` first, then `references/tenant-context-guardrails.md` when target app identity comes from tenant inventory or cached tenant evidence, then `references/odc-ui-real-app-evidence.md`; use a Tenant Context Packet for target identity and freshness, use `Real-App Pseudocode Comparison Mode` for comparison output, use `Recipe-Candidate Triage` for recipe decisions, require `Extra Evidence Trigger` checks before promotion, keep real app evidence example-backed, and do not infer exact widget trees from MCP context summaries |
| "Mentor hardening, known fragile generation patterns, TrueChange pre-mortem checklist, plan corrections, or Mentor Studio reliability issues" | `references/odc-mentor-hardening.md` first, then the specific guide for the affected element |
| "Mentor invented, dropped, renamed or widened something the spec pinned — extra or missing roles, RBAC scope drift, a changed attribute type or length, or an element built outside the stated scope" | `references/odc-mentor-hardening.md` → `### Preserve RBAC Scope Exactly As Specified`, `### Preserve Exact Attribute Types From Spec And Source`, and `### Enforce Out-of-Scope Contract as a Blocking Boundary`; state the pinned value from the spec and re-check after the fix turn, because a fix turn is not assumed comprehensive |
| "Did the thing I just built actually run? — verifying an action does its job, verifying a screen for a signed-in user, closing a fix, or deciding whether a publish landed" | `references/execution-gates.md`; build-time signals (`change_applied`, enumeration, digest, assertion recompute) describe whether the right shapes exist and cannot see whether the logic works |
| "It renders but it does nothing, the button is dead, the style had no effect, the caption shows raw `If(...)`, the badge and the row disagree — which probe tells these apart" | `references/execution-gates.md` §6, the failure-shapes catalog: twelve shapes measured on one app that all passed validation with `error_count: 0`, each with the probe that discriminates it (network log, computed style, DOM presence, `db_query`, rendered-content baseline, and — for shape 11 — naming the UI element that can make a guarded branch's condition true). Structured fields and runtime probes were right every time; Mentor's prose was wrong three times, so read the fields and treat the narrative as a hypothesis |
| "Mentor reported success but nothing changed, a silent no-op, an element created then reported missing, a generic or vague Mentor error, or why did this turn go wrong after the fact" | `references/odc-mentor-hardening.md` → `### The Host Execution Model — Why A Successful Turn Can Change Nothing` for the mechanics, then `references/execution-gates.md` §5c for the triage ordering; read the model back before reading the run's own account of itself, and label an unobserved cause a hypothesis |
| "ModelAPI question — what interface is a screen/entity/flow node, is this property settable, how do I create a child element, how do I wire a flow, how do I bind an argument, what does applyModelApiCode-shaped code actually address, or which namespace goes in imports" | `references/odc-modelapi-code-application-surface.md` — the curated ModelAPI code-application surface, from the platform's own generated API reference; it is authority for the API surface only (what exists, what is settable, what a call takes) and never for runtime behaviour. For how that code is applied and why a successful turn can change nothing, `references/odc-mentor-hardening.md` → `### The Host Execution Model — Why A Successful Turn Can Change Nothing`; for element semantics and platform rules, Language-elements handbook and `references/odc-platform-guardrails.md` |
| "Forbidden Mentor introspection patterns, split proof/edit retries, or protected contract prompts" | `references/odc-mentor-hardening.md` first for Forbidden Mentor introspection patterns, split proof/edit retries, and protected contract prompts; use it before asking Mentor to prove or edit fragile targets |
| "Write ODC SQL for INSERT, RETURNING, deterministic first-N rows, SQL node parameters, or output structures" | `references/odc-mentor-hardening.md` first, then Language-elements handbook → `### SQL` |
| "Data writes, create/update/delete entity actions, INSERT/UPDATE/DELETE SQL, or status-changing writes" | `references/odc-mentor-hardening.md` first, then Implementation-context guide → data modeling subsection |
| "JSON Deserialize, Deserialize<StructureName>, parsed response access, or response structure parsing" | `references/odc-mentor-hardening.md` first, then Language-elements handbook for element syntax |
| "Status values, static entity values, enum values, or Identifier-backed statuses" | `references/odc-mentor-hardening.md` first, then Implementation-context guide → data modeling subsection |
| "External logic, external libraries, SDK, custom code, .NET extension" | `references/live-target-evidence-matrix.md` first when the answer targets an existing app or claims current External Logic/ExternalLibrary proof; then Implementation-context guide -> `## 4. Integration And External Systems Guidance` (external logic subsection) |
| "Data modeling, entity, relationship, foreign key, one-to-many, index" | Implementation-context guide → `## 3. Build And Design Guidance` (data modeling subsection). **If the relationship is to a user** — ownership, "my <records>", created-by, assigned-to, per-user filtering — open `references/odc-platform-guardrails.md` → `## User Reference Authoring Gate` **first**: the platform `User` entity is not modelled like an ordinary parent entity, and the data modeling subsection does not cover it |
| "Evidence coverage, source gap, unverified element" | Source manifest |
| "O11 to ODC migration, refactoring O11 code for ODC" | Implementation-context guide → `## 2. Architecture And Placement Rules` (migration boundary section) |
| "The build said success and the screen does not show it — which layout does this app actually render, a search bar or top-bar control added to the layout block never appeared, a dropdown is clipped by the header, or the control is there and clicking it does nothing" | `references/odc-visual-source-ui-discipline.md` → `## Default Layout Replacement Review` to read the layout the app renders before emitting chrome, then `## Chrome Batch Discipline` for the unconditional-destination rule; then `references/odc-mentor-hardening.md` → `### Block Chrome Must Be Real Block Content, Not Placeholder Default Content`, `### A Dropdown Inside A Slim Fixed Header Clips Unless It Escapes The Bar`, and `## Ask What The Event Points At, Not What The Action Does`. These are the cases where every build-time signal reports success and the screen still does not change, so do not read a clean turn as evidence |
| "Clicking a row sets some values and clears others, the add after the click does nothing, or a handler reads the clicked row from `List.Current`" | `references/odc-mentor-hardening.md` → `` ## Pass The Clicked Row As Arguments, Not As `.Current` `` — ask which event the handler is bound to first, then pass the row's values as input arguments; the runtime half is `references/execution-gates.md` §6 shape 12 |
| "A branch that is complete and correct but never fires, or an aggregate nothing consumes" | `references/execution-gates.md` §6 shape 11 — for every guarded branch, name the UI element that makes the condition true; if none exists the branch is dead-but-live, and the aggregate feeding it should be deleted rather than left fetching for nobody |
| "A styling fix that changed nothing, or which theme classes actually resolve in this app" | `references/odc-mentor-hardening.md` → `### Style Only With Classes Verified Present In This App's Theme` for what to emit, and `references/execution-gates.md` → `### Measured computed style, not class presence` for the per-app audit and the per-fix measurement; the measured known-bad list is there |
| "Is this verification verdict actually current — a message or count read off a screen I have not reloaded, or a warning count that jumped on a turn that should not have grown it" | `references/execution-gates.md` §1b for the post-reload rule (feedback messages and list counts persist across probes) and §5d for the per-turn WARNING-count diff |

## Architecture guidance source families

Use the handbooks first, then the available public-provider role:
`workspace-knowledge-cc` and `outsystems-public-knowledge` expose the same
public retrieval role. Only when neither alias is available, use local clones
of `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` as an
explicitly degraded, source-backed fallback; do not rely on model memory alone.
Use internal architecture evidence only when the separate, VPN-gated
`outsystems-tech-content` capability is available.

| Source family | When |
|---|---|
| [references/odc-platform-guardrails.md](odc-platform-guardrails.md) | When the question involves layering, public services, anonymous access, server trust, query performance, timers, background processing, imports, async retry, bulk work, API contract changes, referencing the platform `User` entity (user ownership, created-by/assigned-to, per-user filtering), an action taking a record id that may not exist (update, cancel, delete, detail, not-found refusals), or the Architecture Layering Gate, Security Server-Trust Gate, User Reference Authoring Gate, Not-Found Guard Gate, Performance Query Pre-Mortem, Timer / Async Idempotency Gate, Public API Contract Gate, Deploy-Time Error Code Gate, or Library Release Visibility Gate |
| Architecture Design | App vs Library vs Service design |
| Integration Patterns | Cross-app integration pattern selection |
| Sharing Data Patterns | Entity ownership and data sharing design |
| Distributed Transactions | Saga patterns and distributed transaction design |
| Library Reusability Patterns | When to extract a Library vs Service Action |
| ODC Adoption Workshop Day 2 - 01 Event Driven Architecture | Event-driven placement decisions |
| ODC Adoption Workshop Day 3 - 03 Distributed Transactions | Saga/compensation pattern pseudocode |
| Agent guardrails | Guardrail configuration in agentic apps |
| ODC-Agentic development in the SDLC | Agentic SDLC and architecture overview |
| ODC-AI development in Mentor Studio | Mentor Studio authoring workflow |
| ODC-Known limitations | Mentor Studio and Mentor Web constraints |
| ODC-Agent-to-agent communication in ODC | A2A concepts and architecture |
| ODC-Adding external agents in the ODC portal using A2A | A2A connection and `SendMessage` usage |

## Default response contract

Unless the user asks for another format, answer in this order:
1. `Placement`
2. `Studio-Native Pseudocode`
3. `Evidence Status`
4. Optional constraints only when they materially change correctness

For supported web UI paste-ready generation, route through `references/odc-ui-generation.md` and use this explicit order:
1. `### Mentor Studio Prompt`
2. `### Prompt Coverage Audit`
3. `### Studio-Native UI Spec`
4. `### Evidence Status`

For supported web UI generation that also materially changes AI/agentic safety risk, keep the UI generation order and insert the guardrail audit after the UI spec:
1. `### Mentor Studio Prompt`
2. `### Prompt Coverage Audit`
3. `### Studio-Native UI Spec`
4. `### Agent Guardrail Coverage Audit`
5. `### Evidence Status`

For non-ready Mobile UI and Mobile UI guardrail routes, use the guardrail order from
`odc-ui-framework-selection.md` / `odc-ui-generation.md` and do not emit `### Mentor Studio Prompt`.

For `Evidence Status`, use exactly one of:
- `Current official`
- `Catalog-backed official`
- `O11-supported ODC candidate`
- `Mixed official+archived`
- `Course/example-backed`
- `OutSystems-public implementation evidence`
- `Unverified gap`

Dry-run evidence and fixture-only evidence are not standalone Evidence Status
labels; use `Unverified gap` for product-contract claims that rely only on
dry-run output or local fixtures; upgrade only when separately grounded by
current official docs, catalog facts, course/example material,
implementation-reference evidence, or tenant observation.

Do not load the full source manifest just to emit `Evidence Status`. Use it only when the evidence class is unclear or the user asks for source coverage.

For Mentor Web, Mentor Studio, capability, constraint, and known-limitations
claims, route to `references/mentor-capability-constraint-matrix.md` as the
Mentor Capability And Constraint Matrix source owner. Keep runtime docs thin:
do not copy the matrix details here, and do not promote generated, dry-run,
fixture-only, or screenshot-only evidence.

Before choosing a visible response contract, route through
`references/omi-route-mode-classifier.md` as the Route Mode Classifier source
owner. Keep runtime docs thin: classify the request, apply structured intent
normalization for complex work, then open only the mode-specific guides needed
for the selected output.

## Retrieval stack for pseudocode and Mentor prompts

Use `references/retrieval-query-bundles.md` as the Retrieval Query Bundles
source owner before emitting ODC pseudocode or Mentor Studio prompts. It owns
the detailed recipes for Mentor capability refresh, widget catalog refresh,
data binding and producer review, TrueChange and platform errors, security and
roles, performance and queries, timers/events, agentic and guardrails work, and
degraded retrieval behavior.

The thin default is:

1. The available public knowledge-provider role (see
   `references/knowledge-provider-contract.md` for the role→tool binding table):
   The maintainer may bind `workspace-knowledge-cc`; a colleague may bind
   `outsystems-public-knowledge`. Both expose the same public retrieval role,
   and provider availability determines the mode.
2. If neither provider is available, use local clones of `docs-howtos`,
   `docs-odc`, `docs-product`, and `outsystems-ui` as an explicitly degraded,
   source-backed fallback; do not rely on model memory alone.
3. `outsystems-tech-content` — separate, VPN-gated implementation authority for
   exact syntax and constraints. The public component does not supply its
   restricted function, widget, or TrueChange authority.
4. Current public/official docs and mirrored authority files already routed in this skill

Keep the technical-content tool details in the bundle owner: `check_health`,
`explain_filters`, `list_collections`, `include_full_content`, `page_url`,
`visibility`, unpublished reference boundaries, and the rule to not pass
collection names as a `collection` argument. If a `content_source='model'`
query returns no results, run `get_status` (it reports indexed collections and
chunk counts; `check_health` takes no arguments and reports liveness only) and
retry without `content_source`; the empty filtered result does not prove `model-functions` or
`model-truechange` has no relevant coverage. If the selected bundle cannot
ground exact signatures, widget rules, TrueChange errors, live Mentor behavior,
security roles, or tenant-specific facts, stop rather than speculate.

Fallback notes:

- `outsystems-tech-content` is the quality gate for implementation authority. If it is unavailable but a public provider is callable, run `provider: public-grounded` per SKILL.md's preflight and `references/knowledge-provider-contract.md`: continue with public-docs authority, state the narrower grounding, and fail closed on TrueChange error text, internal/courseware evidence, and widget rules beyond the generated catalogs. Only when no provider at all is available, stop and ask whether to proceed with degraded quality after suggesting VPN reconnection and a fresh session.
- `docs-howtos`, `docs-odc`, and `docs-product` can provide explicitly degraded
  product grounding when neither public-provider alias is available and a
  colleague has cloned or can directly access them.
- `outsystems-ui` can fill OutSystems-public implementation evidence gaps. Do not use it as current ODC product-contract authority or to upgrade evidence beyond the main skill's evidence rules unless current ODC docs, Forge routing/version evidence, or tenant observations confirm the exposed behavior.

For structured-intent or deterministic-plan work, use the retry ladder in
`references/structured-intent-mode.md` before treating an empty broad
implementation search as a source gap.

## Process Artifacts (not runtime routing targets)

These files are review queues, cross-agent campaign records, and reviewer
prompts. They are process history for skill maintenance and live under
`maintenance/`, outside the runtime `references/` surface.
Do not open these while answering an implementation question; no runtime
route points here.
Open them only for capability-review, campaign, or audit work that names them.

- `maintenance/omi-deterministic-quality-cross-agent-review-queue.md`
- `maintenance/omi-deterministic-quality-vnext-review-queue.md`
- `maintenance/omi-deterministic-quality-follow-up-review-queue.md`
- `maintenance/outsystems-mentor-implementation-capability-review-queue.md`
- `maintenance/odc-ui-pattern-coverage-queue.md`
- `maintenance/odc-data-bound-widget-producer-review.md`
- `maintenance/claude-data-grid-reference-review-prompt.md`
- `maintenance/claude-additional-testing-prompt.md`
- `maintenance/claude-rename-review-prompt.md`
- `maintenance/claude-deep-audit-prompt.md`
- `maintenance/claude-data-grid-boundary-testing-prompt.md`
- `maintenance/claude-compatibility-review-prompt.md`
- `maintenance/claude-capability-review-prompts/` (directory)

When capability-review, campaign, or audit work explicitly names one of these
artifacts, use these routes (moved verbatim from the runtime route table):

| Review-work ask | Open first |
|---|---|
| "Ask Claude to test this skill, review Codex/Claude compatibility, or write cross-agent feedback for Codex" | `maintenance/claude-compatibility-review-prompt.md` |
| "Ask Claude to do additional regression testing after compatibility review, stress-test multiple outsystems-mentor-implementation routes, or write deeper cross-agent feedback for Codex" | `maintenance/claude-additional-testing-prompt.md` |
| "Ask Claude to deep-audit remaining blocked checks, Data Grid reference behavior, Inventory Action Sheet evidence boundaries, or model-source fallback after additional regression testing" | `maintenance/claude-deep-audit-prompt.md` |
| "Ask Claude to test Data Grid evidence-boundary polish, review the editable Data Grid fixture, or decide whether a schema-level Data Grid follow-up is still needed" | `maintenance/claude-data-grid-boundary-testing-prompt.md` |
| "Ask Claude to test Data Grid reference evidence-status split, review `odc-data-grid-reference.json`, or confirm the JSON-level dependency setup boundary after Codex follow-up" | `maintenance/claude-data-grid-reference-review-prompt.md` |
| "Ask Claude to review the rename from mentor-studio-code to outsystems-mentor-implementation, validate slug migration, or check legacy alias boundaries" | `maintenance/claude-rename-review-prompt.md` |
| "Run publication-readiness review, capability review loop, Codex-Claude review loop, or full Claude feedback cycle for this skill" | `maintenance/outsystems-mentor-implementation-capability-review-queue.md` first, then the matching prompt under `maintenance/claude-capability-review-prompts/`; process one queue row at a time; Do not publish, deploy, run live Mentor tenant actions, or mutate an OutSystems tenant unless the user explicitly approves the live validation gate |
| "Review data-bound widgets, source-like bindings, producer-first UI guidance, or whether Table/List/Dropdown/Carousel/Gallery/Data Grid/Lightbox Image/Video need producer review" | `maintenance/odc-data-bound-widget-producer-review.md` first, then `maintenance/outsystems-mentor-implementation-capability-review-queue.md` row `MSC-010` and `maintenance/claude-capability-review-prompts/producer-binding-ui-widgets-review.md`; keep the review file-first unless the user explicitly approves live Studio or tenant checks |
