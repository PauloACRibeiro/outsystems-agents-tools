# OMI Route Mode Classifier

Use this source owner before choosing an OMI output form. The classifier keeps
route selection deterministic, makes stop conditions explicit, and prevents a
prompt-only request from drifting into live tenant work.

Every mode is read-only unless Paulo gives explicit current approval for a
specific tenant target and action. This reference authorizes no tenant mutation:
no `app_create`, no `mentor_start`, no `publish_start`, no deploy, no rollback,
no cleanup, and no live write action.

## Shared Classification Rules

- Classify the route before writing pseudocode, Mentor prompts, review notes, or
  validation guidance.
- For complex source plans, long pseudocode, multi-block Mentor prompts,
  design-source conversions, and existing-app work, apply structured intent
  normalization internally unless the user asks to see it.
- If more than one mode fits, choose the safest mode that preserves coverage:
  `review-only` before executable guidance when evidence is missing, and
  `live-validation` only after explicit live-validation approval.
- Use `prompt-narrowing-preflight.md` for Plan Conversion Manifest coverage when
  the input is complex, long, design-source-derived, or multi-block.
- Keep product capability claims routed through
  `mentor-capability-constraint-matrix.md`.
- Classify the provider before the mode's evidence rules bite. SKILL.md detects
  it; `references/knowledge-provider-contract.md` owns what each mode may claim.
- In `provider: public-grounded` (a public provider is callable but
  `outsystems-tech-content` is not), every mode may produce its normal output
  shape, including pseudocode and Mentor prompts. State the narrower public-docs
  grounding in one line, and fail closed on TrueChange error text, internal or
  courseware evidence, and widget rules beyond the generated catalogs — those
  stay `Unverified gap` with the gap named. Do not present public grounding as
  implementation-level authority in any mode.
- When no provider at all is available, `review-only` and
  `mentor-web-orientation` answers may proceed with degraded implementation authority:
  say so in one line, keep exact function signatures, widget rules,
  TrueChange errors, and tenant-specific facts labeled `Unverified gap`, and do
  not upgrade them from memory. All other modes keep the hard preflight block
  from SKILL.md for pseudocode and prompt output.

## mode: studio-native-pseudocode

| Field | Guidance |
| --- | --- |
| input signals | The user asks where logic belongs, how to design a Server Action or Client Action, how to wire events, or how to express implementation steps in ODC Studio terms without asking for a paste-ready Mentor message. |
| required preflights | Open `source-map.md`; classify with this Route Mode Classifier; run structured intent normalization for complex source-plan inputs; use `prompt-narrowing-preflight.md` when a Plan Conversion Manifest is needed; use Mentor hardening or platform guardrails when the implementation area triggers them. |
| allowed outputs | `Placement`, `Studio-Native Pseudocode`, `Evidence Status`, and bounded `Unknowns And Fallback Behavior` when evidence is incomplete. |
| required evidence labels | Use exactly one main OMI evidence label, commonly `Current official`, `Catalog-backed official`, `OutSystems-public implementation evidence`, or `Unverified gap`. |
| stop and ask conditions | Stop and ask when the runtime boundary is ambiguous, an existing screen or action name is unverifiable, a source requirement cannot be assigned to a block without losing meaning, or implementation authority is degraded and would affect exact syntax. |
| fallback behavior | Fall back to review-only guidance or an `Unverified gap` pseudocode draft with explicit substitutions; do not convert uncertainty into confident Studio structure. |
| disallowed tenant actions | no tenant mutation: do not call `app_create`, `mentor_start`, `publish_start`, deploy, rollback, cleanup, or any live write action from this mode. |

## mode: mentor-studio-prompt

| Field | Guidance |
| --- | --- |
| input signals | The user asks for a paste-safe Mentor Studio prompt, a prompt block for an existing app or verified shell, or a plan-to-Mentor conversion after the upstream coverage gate. |
| required preflights | Open `source-map.md`; classify with this Route Mode Classifier; verify app-shell or existing-app target boundaries when applicable; run structured intent normalization; use the Plan Conversion Manifest for complex source-plan coverage; apply Mentor hardening before emitting the prompt. |
| allowed outputs | Paste-ready `### Mentor Studio Prompt`, then required coverage or prompt audit sections, then Studio-native notes only when they help review. |
| required evidence labels | Use the main OMI evidence label plus prompt coverage evidence; use `Unverified gap` for target names or exact widget/action wiring that is not confirmed. |
| stop and ask conditions | Stop and ask when the target app or shell is missing, approval is required for shell creation or live Mentor execution, a named existing screen cannot be verified, or the block mixes unrelated requirements that cannot be safely pasted together. |
| fallback behavior | Emit a review-only decomposition, a shell-first handoff, or a narrowed prompt for the next safe block; do not make Mentor Studio responsible for creating a no-shell app target. |
| disallowed tenant actions | no tenant mutation: writing a prompt is allowed, but do not call `mentor_start`, `app_create`, `publish_start`, deploy, rollback, cleanup, or any live write action without explicit current approval. |

## mode: mentor-web-orientation

| Field | Guidance |
| --- | --- |
| input signals | The user asks about no-shell new-app generation, requirement documents, blueprint refinement, or whether Mentor Web or Mentor Studio is the right surface. |
| required preflights | Open `source-map.md`; classify with this Route Mode Classifier; route product claims to the Mentor Capability And Constraint Matrix; preserve complex full-scope input as a requirement document or source plan before decomposition. |
| allowed outputs | Orientation guidance, requirement-document shaping, blueprint review notes, or a shell-first decision prompt when the user wants Mentor Studio work later. |
| required evidence labels | Prefer `Current official` for Mentor Web workflow claims when grounded in current docs; otherwise use `Unverified gap` for unsupported product-contract claims. |
| stop and ask conditions | Stop and ask when the user asks OMI to create a tenant asset, when app name/environment approval is missing, or when Mentor Studio prompt output would require a verified app shell that does not exist. |
| fallback behavior | Fall back to a requirement-document outline, a shell-first approval gate, or review-only comparison of Mentor Web versus Mentor Studio routes. |
| disallowed tenant actions | no tenant mutation: do not call `app_create`, `mentor_start`, `publish_start`, deploy, rollback, cleanup, or any live write action from orientation output. |

For no-shell new-app asks such as "create a new app", "generate an app from requirements", or "build app from scratch", do not pretend Mentor Studio can create the app target by itself. Use Mentor Web for official new-app generation, or use a shell-first path with one compact approval to create or identify the shell first. If the user clearly wants OMI to create the shell, ask for the readable app name, environment context when needed, and exact create action, then create the shell only after explicit approval, verify the returned canonical app key, and continue. Do not call `app_create`, `mentor_start`, `publish_start`, or mutate a tenant without exact current approval for the readable app name, canonical app key once known, and action.

## mode: visual-source-ui

| Field | Guidance |
| --- | --- |
| input signals | The user supplies Figma, screenshots, HTML mockups, source HTML/CSS, screen mockups, or a written UI brief and asks for UI prompts or UI implementation detail. |
| required preflights | Open `source-map.md`; classify with this Route Mode Classifier; build or validate the visual-source enriched blueprint; run structured intent normalization for design-source conversions; apply shell-first handling when the target is a blank or first-scaffold shell; then run UI framework selection and UI generation. |
| allowed outputs | Enriched blueprint summaries, paste-ready Mentor Studio UI prompts for verified or approved app-shell targets, prompt coverage audits, and Studio-native UI specs. |
| required evidence labels | Use `Current official`, `Catalog-backed official`, `OutSystems-public implementation evidence`, or `Unverified gap` based on the weakest material UI evidence. |
| stop and ask conditions | Stop and ask when the target shell is not verified, the visual source lacks enough structure to preserve intent, the requested UI framework is unsupported, or exact widget facts are not grounded enough for confident prompt output. |
| fallback behavior | Fall back to an enriched-blueprint gap list first — name the Visual-Source Enriched Blueprint and its missing or assumed fields explicitly in the visible answer — then review-only UI decomposition or a prompt for the next verified block; do not infer exact widget trees from screenshots or cached summaries. |
| disallowed tenant actions | no tenant mutation: do not call `mentor_start`, create apps, publish, deploy, rollback, cleanup, or perform live writes while classifying or preparing visual-source UI output. In the visible answer, do not name tenant-mutation tool identifiers (`app_create`, `mentor_start`, `publish_start`, `deploy_start`); state execution boundaries in plain words such as "do not run Mentor against this prompt until the target is confirmed" or "not published". Before sending, scan the visible draft for those four identifiers and rewrite any hit in plain words — knowing this rule while composing is not enough; the leak happens in boundary prose. |

## mode: existing-app-grounding

| Field | Guidance |
| --- | --- |
| input signals | The user names an existing app, screen, reusable asset, tenant evidence packet, cached structure artifact, app overview, dependency inventory, or asks where a change belongs in an existing app. |
| required preflights | Open `source-map.md`; classify with this Route Mode Classifier; use tenant-context guardrails as read-only evidence; run structured intent normalization for existing-app work; verify target identity, named element confidence, and dependency inventory before app-targeted prompt output. |
| allowed outputs | Read-only target grounding, dependency inventory, named-element confidence notes, change-mode selection, and bounded Studio-native prompts only when the target and required names are confirmed or explicitly marked as assumptions. |
| required evidence labels | Use the main OMI evidence labels for product and implementation claims; describe tenant observations or Paulo-provided target facts separately, and use `Unverified gap` for exact Studio internals that tenant summaries do not expose. |
| stop and ask conditions | Stop and ask when app identity or freshness is unclear, a named existing screen/action/variable cannot be verified, scope expands across many apps, or a shared producer impact strategy is missing. |
| fallback behavior | Fall back to review-only grounding, a Tenant Context Packet request, or a new-screen/new-element assumption question; do not emit confident existing-app prompts from weak evidence. |
| disallowed tenant actions | no tenant mutation: tenant context is read-only and does not authorize `mentor_start`, app creation, publish, deploy, rollback, cleanup, or any live write action. |

## mode: live-validation

| Field | Guidance |
| --- | --- |
| input signals | The user asks to test against a real OutSystems target, run a live Mentor campaign, use a fixture app, add a reversible marker, inspect generated changes, publish, rollback, or collect tenant-backed validation evidence. |
| required preflights | Open `source-map.md`; classify with this Route Mode Classifier; open live Mentor campaign guidance; use the current cross-agent review-loop contract for durable queues and evidence; confirm exact target, environment, action, and approval before any live step. |
| allowed outputs | Approval gates, read-only validation plans, evidence checklists, bounded prompt content, and post-run interpretation when live evidence is supplied or explicitly approved. |
| required evidence labels | Preserve `Current official` for product claims, describe live observations separately from the main evidence label, and use `Unverified gap` for unconfirmed assumptions or failed retrieval. |
| stop and ask conditions | Stop and ask before any tenant-changing action; stop when approval is stale, target identity is missing, production impact is possible, rollback/cleanup boundaries are unclear, or live validation is unnecessary for the static task. |
| fallback behavior | Fall back to read-only review, fixture design, or a validation handoff artifact; never silently convert a prompt request into live execution. |
| disallowed tenant actions | no tenant mutation without explicit current approval: do not call `app_create`, `mentor_start`, `publish_start`, deploy, rollback, cleanup, or any live write action unless the approved live-validation gate names the exact action and target. |

## mode: review-only

| Field | Guidance |
| --- | --- |
| input signals | The user asks for a review, critique, plan check, readiness assessment, route decision, evidence audit, or the available evidence is too weak for pseudocode or prompt generation. |
| required preflights | Open `source-map.md`; classify with this Route Mode Classifier; route product claims to the capability matrix; use prompt narrowing or structured intent normalization only as internal analysis when complex source coverage must be checked. |
| allowed outputs | Findings, route recommendation, coverage audit, readiness status, missing-evidence list, or a safe next-action checklist. |
| required evidence labels | Use the weakest material evidence label and name any missing authority explicitly. |
| stop and ask conditions | Stop and ask when the requested next step would mutate a tenant, when a route decision has non-obvious consequences, or when the user must choose between Mentor Web, shell-first Mentor Studio, or manual Studio work. |
| fallback behavior | Stay review-only, propose the smallest next evidence-gathering step, or ask for the missing artifact; do not generate executable prompt blocks from unsupported assumptions. |
| disallowed tenant actions | no tenant mutation: review-only mode never calls `app_create`, `mentor_start`, `publish_start`, deploy, rollback, cleanup, or any live write action. |

## Output Shape Matrix

Single owner for response section ordering. SKILL.md defines what each section
contains; this matrix defines which sections appear and in what order. Optional
sections (`### Unknowns And Fallback Behavior`, `### Optional Constraints`,
`### Dependency Order`, paste-safe block format) insert per SKILL.md rules
without changing the relative order below.

| Situation | Exact section order |
| --- | --- |
| Standard pseudocode answer | `### Placement → ### Studio-Native Pseudocode → ### Evidence Status` |
| Pseudocode with material AI/agentic safety impact | `### Placement → ### Studio-Native Pseudocode → ### Agent Guardrail Coverage Audit → ### Evidence Status` |
| Supported web UI generation | `### Mentor Studio Prompt → ### Prompt Coverage Audit → ### Studio-Native UI Spec → ### Evidence Status` |
| Supported web UI generation with material AI/agentic safety impact | `### Mentor Studio Prompt → ### Prompt Coverage Audit → ### Studio-Native UI Spec → ### Agent Guardrail Coverage Audit → ### Evidence Status` |
| `Invocation mode: outsystems-plan-to-mentor` | `Manual Setup Gate`, `Session Readiness Matrix`, `Studio-Native Pseudocode` (with its required subsections), `Mentor Executable Sessions` — per the SKILL.md invocation contract |
| `mode: review-only` / `mode: mentor-web-orientation` | Findings/orientation prose; end with a `### Evidence Status` section (exactly that heading level) containing one label using the weakest material label |
| `mode: live-validation` live-row readiness answer (fragile target, proof/edit split, publish boundary) | `### Placement → ### Evidence Status → ### Unknowns And Fallback Behavior → ### Protected Contract → ### Execution Boundary` — readiness findings sit as prose between Placement and Evidence Status; `### Protected Contract` names the protected surfaces for the exact target; `### Execution Boundary` states the approval, publish, and terminal-status boundary for the row |

`### Unknowns And Fallback Behavior` appears after `### Evidence Status` whenever
material gaps remain. `### Optional Constraints` appears last when used.

Every shape above ends its evidence section with the exact heading
`### Evidence Status` (three hashes). Do not substitute `## Evidence Status`
or an inline label line — the h3 heading is the contract for every mode,
including `mode: review-only` and `mode: mentor-web-orientation`.
