# Prompt Narrowing Preflight

Use this preflight before turning any complex source plan, large feature
request, design-source conversion, or multi-block pseudocode output into
Studio-native pseudocode or Mentor prompts.

This is block decomposition, not plan shrinking. The source plan remains the
control artifact, and narrowing is only a way to choose the next safe block of
work. Do not delete coverage, compress requirements into vague summaries, or
drop inconvenient source-plan items.

## Trigger

Run this preflight when any of these are true:

- The source is a complex implementation plan, PRD, requirement document,
  visual blueprint, design-source conversion, or large feature request.
- The output would need more than one dependency-sensitive pseudocode block.
- The output would create or modify multiple ODC element families.
- The output would need multiple paste-safe Mentor Studio prompts.
- A single prompt would mix unrelated goals or make verification unclear.

## Source Plan Control

Keep the original source plan intact and cite its location or provenance in the
output. If the source plan changes, record the revision before continuing.

Required rule: the source plan remains the control artifact. A narrowed block is
only a delivery slice. It is not permission to omit, rewrite, or re-prioritize
source-plan requirements without explicit review.

If any source requirement cannot be assigned to a block without losing meaning,
stop and ask for clarification before generating pseudocode or Mentor prompts.

## Plan Conversion Manifest

Build a Plan Conversion Manifest before generating pseudocode or Mentor prompts.
Emit it using the field skeleton in
[prompt-templates/plan-conversion-manifest.md](prompt-templates/plan-conversion-manifest.md),
filling every bracketed placeholder. At minimum it carries these fields:
`source_plan_path`, `source_plan_revision`, `coverage_map`
(`source_requirement` → `block_id`), `dependency_order`, and one `blocks`
entry per block with `block_id`, `block_goal`, `scope_in`, `scope_out`,
`evidence_required`, `unknowns`, and `acceptance_checks`.

The coverage_map must map every source requirement to a block_id. The manifest
is incomplete while any source requirement is unmapped. Final output must have
no omitted source-plan requirement.

## Dependency-Ordered Blocks

Split work into dependency-ordered blocks using the existing OMI emission order:

1. Dependency inventory
2. Data model
3. Platform configuration
4. External integration
5. Runtime orchestration
6. Server actions
7. UI blocks

Each block must name its prerequisites, producers, consumers, and verification
checks. Producer blocks must appear before consumer blocks. If two blocks are
cyclic or mutually dependent, stop and ask for the preferred dependency break
instead of inventing an order.

## Mentor Prompt Narrowing

Apply Mentor prompt narrowing only to one block at a time. For Mentor Studio
output, each block must be paste-safe and one requirement per Mentor prompt
unless the block is explicitly review-only.

Every paste-safe Mentor message must include:

- the target ODC element or block;
- prerequisites and existing items to reuse;
- exactly what to create or adjust;
- acceptance checks for that block;
- any unknowns or manual verification notes.

Do not merge multiple source requirements into one Mentor prompt when the
combined prompt becomes vague, dependency-unsafe, or hard to verify.

## Block Size Budget And Split Triggers

Use this Block Size Budget before writing a prompt or pseudocode block.

split triggers:

- The block mixes data model, server action, and UI work.
- The block touches more than one write target, such as an Entity and a Screen,
  or a Server Action and a Web Block.
- The block needs more than one paste-safe Mentor message.
- The block's acceptance_checks cannot be verified independently.
- The block contains multiple independent user-visible requirements.
- The block requires different evidence types, such as current docs plus
  tenant read-only evidence, and one part can proceed without the other.

If a split trigger fires, split the block and update the Plan Conversion
Manifest before writing output.

## Merge Rule

Merge only after coverage audit passes and only when merging does not create a
vague multi-requirement Mentor prompt. The coverage audit must prove that every
source requirement is mapped, every mapped block has acceptance_checks, and the
combined prompt still remains one requirement per Mentor prompt unless the
combined block is explicitly review-only.

Required rule: merge only after coverage audit passes.

## Stop Conditions

Stop and ask the user before output generation when:

- a source requirement cannot be assigned to a block without losing meaning;
- a block cannot be made paste-safe without assuming an unverified target;
- dependency order is cyclic or unclear;
- coverage audit finds an unmapped, partial, or conflicting source requirement;
- preserving coverage would require plan shrinking, source deletion, or hidden
  scope changes.
