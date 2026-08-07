# Structured Intent Mode

Use this guide when OMI needs structured intent as default internal
normalization, or when the user asks for structured intent, Architect Mode,
pseudocode mode, deterministic Mentor plans, or a demo that compares ambiguous
PRD input with a Mentor-ready structured plan.

This is a proposed capability. It is not a current Mentor Web or Mentor Studio API
unless the user provides a real API contract in the active task. Current
official Mentor Web behavior remains prompt or requirement-document input,
blueprint review, generation, and refinement. Phrase outputs accordingly.
Do not imply Mentor has a private structured-intent API unless the active task
provides one.

## Source Grounding

Use the available public knowledge-provider role (see
`references/knowledge-provider-contract.md` for the role→tool binding table)
first for product behavior and Mentor workflow grounding.
`workspace-knowledge-cc` and `outsystems-public-knowledge` expose the same
public retrieval role. Only when neither alias is available, use local clones
of `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` as an
explicitly degraded, source-backed fallback; treat `outsystems-ui` as
implementation nuance only, and do not rely on model memory alone. Use the
separate, VPN-gated `outsystems-tech-content` provider for implementation facts:
function signatures, widget constraints, and TrueChange messages. If it is
unavailable, stop and ask whether to proceed with degraded quality after
suggesting VPN reconnection and a fresh session.

When broad `outsystems-tech-content` queries return weak or empty results, retry
with exact implementation phrases before declaring a gap:

- `If function conditional expression`
- `CurrDateTime GetUserId`
- `CreateOrUpdate entity action save record`
- `validate form before save button run server action create or update`
- `static entity identifier Entities.Status.Record`
- `TrueChange invalid entity identifier mandatory data type`
- `Required Property Value event handler must be set`

For built-in function and TrueChange queries, use `content_source='model'` to target
`model-functions` and `model-truechange`. Do not add `version='odc'` to
model-reference queries unless results prove it helps — built-in functions are
platform-generic. No `collection` parameter exists on `search_outsystems_content`.
If a `content_source='model'` query returns no results, run `get_status` (the
working health probe — a bare `check_health` call is rejected with "Invalid
request parameters") and retry without `content_source` before declaring a
source gap. The empty filtered
result does not prove `model-functions` or `model-truechange` has no relevant
coverage; surface the implementation-authority gap in the evidence breakdown
when broader fallback evidence is all you have.

## Default Internal Normalization

Structured intent is default internal normalization for every complex source
plan, long pseudocode request, multi-block Mentor prompt, design-source
conversion, and existing-app work. It is an internal normalization artifact
unless the user asks to see it.

Use the Plan Conversion Manifest for coverage whenever the source is a complex
source plan, design source, or multi-block output. Preserve the existing
dependency order from the manifest: dependency inventory, data model, platform
configuration, external integration, runtime orchestration, server actions, and
UI blocks.

Keep the determinism QA anchors below even when the normalized structured intent
stays hidden. The visible answer can be pseudocode, Mentor Studio prompts,
review-only notes, or route guidance, but the internal normalized structure must
still preserve dependency order, explicit producers before consumers, evidence
labels, and unresolved gaps.

## When To Show It

Show the structured-intent artifact only when the user asks for it or when a
demo/review task needs the intermediate form visible. Visible uses include:

- proving that an ambiguous PRD can produce variable Mentor outputs;
- converting a PRD into a deterministic, Studio-native plan;
- preparing an Open Day or strategy demo about Mentor determinism;
- creating a Mentor-ready structured-intent packet with explicit evidence.

For ordinary one-action pseudocode, keep structured intent internal unless the
user asks for determinism, PRD ambiguity, or Architect Mode framing.

## Complex Source Plan Preflight

For any complex source plan, large feature request, design-source conversion, or
multi-block pseudocode output, open `prompt-narrowing-preflight.md` before this
guide emits or internally normalizes structured intent. Build the Plan Conversion
Manifest, preserve the source plan as the control artifact, and use block
decomposition, not plan shrinking.

The structured plan should then follow the dependency-ordered blocks from the
manifest and keep a coverage audit visible enough to prove that every source
requirement is still represented. Do not collapse long plans into a shorter
prompt by deleting coverage; narrow only to the next paste-safe block.

## Output Contract

Return these sections in order:

### Ambiguous PRD

Keep this short. Preserve the business intent and the ambiguity that could lead
to different blueprints. Do not improve the PRD silently.

### Variability Checklist

List the places Mentor could reasonably infer different implementations:
entity split, roles, static values, screen structure, validation, scoring logic,
default filters, and save behavior.

### Structured Studio-Native Plan

Emit Mentor-ready structured intent in the paste-safe order from `SKILL.md`:

1. Dependency inventory
2. Data model blocks
3. Platform configuration blocks
4. External integration blocks
5. Runtime orchestration blocks
6. Server action blocks
7. Consumer/UI blocks

Use Studio-native terms such as Entity, Static Entity, Role, Server Action,
Screen, Form, Button, Aggregate, Data Action, Assign, If, Run Server Action,
Refresh Data, and OnClick.

### Determinism QA

Check every applicable anchor before finalizing:

- Roles are declared before screen visibility or access rules use them.
- Static Entities are declared before values are used.
- Core Entity attributes, identifiers, mandatory fields, and relationships are
  explicit.
- Server Action inputs, outputs, validation, assignments, and persistence are
  explicit.
- Button OnClick is wired; create a placeholder action if the final action does
  not exist yet.
- Form.Valid is checked before save logic runs.
- Refresh Data is present after successful writes when the screen must update.
- Status fields use static entity identifiers or named substitutions; use no text literal statuses unless the model states the attribute is Text.
- CreateOrUpdate output-name guardrail: do not assert an exact
  `<CreateOrUpdate>.Id` output name unless verified. Emit a substitution note
  when the active ODC action output name is unknown.
- UI widget evidence caveat: for Form, Input, Button, Table, Dropdown,
  Checkbox, or Text Area facts backed only by support catalogs or O11 candidate
  evidence, mark the exact property wiring for ODC Studio review.

### Evidence Status

Still emit exactly one label from the main skill's `Evidence Status` list.
Choose the weakest materially used evidence class.

### Evidence Breakdown

Add this section when evidence is mixed. Keep it short:

- Product behavior: Mentor Web prompt/document input and blueprint review.
- Implementation facts: `content_source='model'` for model-functions/model-truechange; omit content_source for widget-library-rules and outsystems-ui-api.
- UI caveats: standard-widget or O11-supported candidate gaps.
- Assumptions: any unverified app-specific names or active model substitutions.

## Deterministic Plan Rules

- Prefer named dependencies over prose: `Role SalesManager`, `Static Entity
  LeadStatus`, `Server Action SaveLeadAndComputePriority`, `Button BtnSaveLead`.
- Convert business states into Static Entities unless the PRD explicitly says
  the status is free text.
- Convert scoring or priority rules into exact `If(...)`, comparison, or Assign
  expressions after verifying built-in functions.
- Put producers before consumers. If a screen calls a Server Action, define the
  Server Action first.
- Keep UI blocks reviewable. Do not overclaim exact widget properties when the
  catalog says `Unverified gap`, `Course/example-backed`, or
  `O11-supported ODC candidate`.
- If the app target is not stated in a demo context, assume an ODC Web app for
  Mentor Web generation and state the assumption. Ask only when choosing the
  wrong target would materially change the output.

## Demo Package Pattern

For demos, prefer this lightweight packet:

1. `current-flow-ambiguous-prd.md`
2. `expected-variability-checklist.md`
3. `structured-pseudocode-plan.md`
4. `live-demo-script.md`
5. `source-notes.md`

The demo should prove the claim without implying that Mentor currently accepts a
private structured-intent API.
