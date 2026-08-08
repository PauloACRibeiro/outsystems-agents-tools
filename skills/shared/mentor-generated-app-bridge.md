# Mentor Generated App Bridge

## Purpose

Use this shared reference when a Mentor Web App Generator app already exists in
an ODC tenant and the user wants an agent to inspect the generated result,
decide the fastest next move, and prepare a clean handoff to either Mentor Web
refinement or Mentor Studio / ODC Studio surgical improvement.

This bridge is shared by:

- `mentor-app-generator`, for Post-Generation Review Mode.
- `outsystems-mentor-implementation`, for Generated App Snapshot Intake Mode.

The bridge optimizes speed first and quality second. The default answer should
be the fastest responsible path from the generated app state:

- regenerate in Mentor Web;
- continue surgically with `outsystems-mentor-implementation`;
- inspect manually before deciding.

## Artifact Location

Write post-generation artifacts beside the original Mentor Web packet. Use
`docs/mentor-app-generator/{app-slug}/post-generation/` as the default output
convention unless the user asks for a different location:

```text
docs/mentor-app-generator/{app-slug}/post-generation/
```

Default artifacts:

```text
docs/mentor-app-generator/{app-slug}/post-generation/app-snapshot.yaml
docs/mentor-app-generator/{app-slug}/post-generation/generated-app-review.md
```

Optional artifacts:

```text
docs/mentor-app-generator/{app-slug}/post-generation/regeneration-prompts.md
docs/mentor-app-generator/{app-slug}/post-generation/studio-handoff.md
```

## Read-Only MCP Evidence Workflow

Use OutSystems MCP as read-only evidence by default.

Before using MCP, identify the local source packet and target generated app.
If the generated app name or asset key is not obvious from the request or
packet, ask the user one concise question for the generated app name or asset key.

1. Use `app_list` with a narrow app name search when the asset key is unknown.
2. Use `app_info` to confirm app name, asset key, type, revision, and revision
   timestamp.
3. Use `app_refs` to capture dependency producers.
4. Use `context_entities` scoped to the app with `owned_only=true`.
5. Use `context_roles` scoped to the app with `owned_only=true`.
6. Use `context_screens` scoped to the app with `owned_only=true`.
7. Use `context_actions` scoped to the app with `owned_only=true`.
8. Use `context_structures` scoped to the app when the tool is available.
9. Use `context_themes` scoped to the app when the tool is available.
10. Use `context_search` only for narrow follow-up questions against the same
    app.

For every paged MCP list call, pass an explicit `limit` and `offset`. Page each
`app_list` or `context_*` result until the returned page is smaller than the
requested limit, or until the tool output explicitly proves there are no more
rows. Do not treat a default first page as complete evidence.

Record pagination completeness for each paged tool in
`mcp_evidence.completeness` with:

- `limit`
- `offsets_checked`
- `returned_count`
- `is_complete`

If a tool result is partial, truncated, interrupted, or only sampled, record that
in `mcp_evidence.missing_capabilities`, mark the affected architecture facts as
partial or unknown, and prefer `manual_review_required` when the missing rows
could change the regenerate-vs-Studio decision.

Do not use tenant-changing tools unless the user explicitly approves a separate
action. This includes `publish_start`, `deploy_start`, `extlib_upload`, and
`mentor_start`. If those tools are needed, stop and ask for approval before
running them.

Record every tool actually used in `mcp_evidence.tools_used`. Record missing
tool coverage and incomplete pagination in `mcp_evidence.missing_capabilities`.

## Snapshot Contract

`app-snapshot.yaml` is the canonical structured artifact. YAML is the primary
format because it is readable, diffable, and easy to edit during review.

Required top-level shape:

```yaml
snapshot_version: 1
app:
  slug:
  name:
  asset_key:
  type:
  revision:
  revision_datetime:
  inspected_at:
  source_packet_path:

mcp_evidence:
  tools_used:
  missing_capabilities:
  completeness:
    context_entities:
      limit:
      offsets_checked:
      returned_count:
      is_complete:
  tenant_changing_actions_used: false

generated_from:
  requirement_document:
  blueprint_prompts:
  known_manual_changes:

architecture:
  references:
  roles:
  entities:
  static_entities:
  relationships:
  screens:
  actions:
  structures:
  themes:

assessment:
  inferred_app_intent:
  observed_strengths:
  structural_gaps:
  functional_gaps:
  security_gaps:
  ui_ux_gaps:
  integration_gaps:
  inferred_items:
  unknowns:

decision:
  recommendation: regenerate_in_mentor_web | continue_in_mentor_studio | manual_review_required
  rationale:
  priority:
  next_skill: mentor-app-generator | outsystems-mentor-implementation | none
```

Allowed `decision.recommendation` values:

- `regenerate_in_mentor_web`
- `continue_in_mentor_studio`
- `manual_review_required`

Allowed `decision.next_skill` values:

- `mentor-app-generator`
- `outsystems-mentor-implementation`
- `none`

## Generated App Review Contract

`generated-app-review.md` is the human review artifact. Keep it concise and
decision-oriented.

Required sections:

1. `Executive Recommendation`
2. `Rationale`
3. `Observed App Shape`
4. `Requirement Fit`
5. `Correction Backlog`
6. `Next Prompt Pack`
7. `Evidence Boundary`

When no source requirement packet exists, the review must also include an
`Inferred App Intent` section. This section belongs inside
`generated-app-review.md`; do not create a separate `inferred-requirements.md` artifact.
It must state that no original local Mentor requirement packet was
available and every inferred claim must be bounded by observed MCP evidence,
local artifacts, or explicitly marked unknowns.

Under `Correction Backlog`, use these categories:

- Regenerate blockers
- Studio surgical fixes
- Manual verification needed
- Defer or nice-to-have

For `regenerate_in_mentor_web`, write Mentor Web refinement prompts to
`regeneration-prompts.md`.

For `continue_in_mentor_studio`, write a concise Studio context packet to
`studio-handoff.md`.

For `manual_review_required`, list the exact screenshots, Studio inspection, or
runtime behavior the user should collect before deciding.

## Decision Gate

Recommend `regenerate_in_mentor_web` when the generated app has a
blueprint-level structural problem:

- core entities are missing or materially mis-modeled;
- relationship direction or ownership is wrong enough to affect most screens;
- roles or access boundaries are structurally wrong;
- navigation or screens do not match the intended app;
- lifecycle stateflows are missing or wrong for the central domain object;
- existing ODC or Data Fabric dependencies were generated as local entities;
- fixing the issue surgically would require broad cross-cutting Studio work.

Recommend `continue_in_mentor_studio` when:

- the domain model is close enough;
- roles and navigation are close enough;
- problems are localized to validation, actions, UI details, integrations,
  hardening, naming, dashboard calculations, or edge-case behavior;
- targeted ODC Studio work is faster than another generation run.

Recommend `manual_review_required` when:

- MCP did not expose enough facts to distinguish structural failure from a
  surgical gap;
- the generated app cannot be confidently matched to the source packet;
- screenshots, Studio inspection, or runtime behavior are needed before a
  responsible decision.

## Cross-Skill Handoff Contract

When `decision.recommendation` is `continue_in_mentor_studio`, create
`studio-handoff.md` with:

- source app name, asset key, revision, and snapshot path;
- selected surgical fixes in priority order;
- observed producers: references, entities, roles, screens, actions,
  structures, and themes;
- inferred items and unknowns that `outsystems-mentor-implementation` must not overclaim;
- explicit warning to avoid exact widgets, local variables, event order, or
  bindings unless evidence exposes them.

When `decision.recommendation` is `regenerate_in_mentor_web`, create
`regeneration-prompts.md` with short Mentor Web prompts grouped by:

- data model corrections;
- relationship corrections;
- role and permission corrections;
- screen pattern corrections;
- stateflow corrections;
- theme or settings corrections;
- integration or data-source corrections.

## Evidence Boundary

Separate every important fact into one of three classes:

- Observed: directly present in MCP output or the local source packet.
- Inferred: a reasonable interpretation from observed app shape.
- Unknown: not exposed by MCP or local artifacts.

Do not infer exact widgets, widget IDs, local variables, screen aggregates, data
actions, bindings, CSS class usage per widget, or event order from MCP context
summaries. If exact UI structure is required, ask the user for screenshots, Studio
inspection notes, or approval for deeper read-only MCP inspection. Do not
request raw OML or source exports.

## Implementation Validation

After editing skills or this reference, run:

Before relying on post-generation artifacts, validate the snapshot/review pair
with the generated-app artifact validator.

```bash
python3 skills/mentor-app-generator/scripts/validate_generated_app_artifacts.py --snapshot skills/mentor-app-generator/fixtures/generated-app-snapshot-example.yaml --review skills/mentor-app-generator/fixtures/generated-app-review-expected.md
python3 skills/mentor-app-generator/tests/test_generated_app_bridge.py -v
rg --hidden --no-ignore -n "Post-Generation Review Mode|mentor-generated-app-bridge" skills/mentor-app-generator
rg --hidden --no-ignore -n "Generated App Snapshot Intake Mode|mentor-generated-app-bridge" skills/outsystems-mentor-implementation
rg --hidden --no-ignore -n "tenant-changing actions used|read-only" skills/shared/mentor-generated-app-bridge.md
git diff --check -- docs/superpowers/agent-handoff.md docs/superpowers/plans/2026-05-23-mentor-generated-app-bridge.md
python3 projects/workspace-agent-tools/scripts/agent_handoff_health.py --workspace-root .
```

On Windows PowerShell, use `python` instead of `python3` — `python3` is not a
command there.
