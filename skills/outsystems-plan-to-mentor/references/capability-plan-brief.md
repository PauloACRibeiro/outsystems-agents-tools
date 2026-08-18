# Capability Plan Brief

Give this brief to the plan generator before the first saved plan is written.
It applies to any plan generator: `superpowers:writing-plans`, a spec-driven
workflow, or a hand-written plan. A generic planner naturally produces
element-level detail; the plan-to-Mentor coverage gate then rejects that detail
and forces a wholesale rewrite. Handing this brief over first prevents the
rewrite.

## What the first saved plan is

The first saved plan must be a business/capability implementation plan, not an
ODC Studio element recipe. Studio-native conversion happens downstream:
`outsystems-plan-to-mentor` owns the coverage gate, and
`outsystems-mentor-implementation` produces the element map and pseudocode.

## Required shape

- Use capability headings such as users and goals, workflows, business rules,
  acceptance criteria, dependencies, open decisions, and scope boundaries.
- Cite the source's stable requirement IDs (`BR-` business rules — namespaced
  per surface for multi-surface plans, e.g. `BR-DM-`/`BR-SC-` —, `UC-` use
  cases, `C-` acceptance criteria, `US-` user stories; see
  `references/requirement-id-conventions.md`) inline in the section that
  addresses each requirement. If the source PRD carries no IDs yet, the
  coverage gate will assign them in pass 1; a plan that already cites them
  converges faster.
- Include a `## Traceability` table (`| Story | Requirements | Design |`):
  one row per `US-n` user story, citing the requirement IDs the story
  delivers and its design artifact ref (`blueprint:<ScreenName>` /
  `inventory:<ScreenName>` from the loop's design artifacts, or an explicit
  `none`). The coverage checker fails any defined requirement that appears
  in no row.
- State scope boundaries and deliberately excluded concepts explicitly, and
  cite the ID of every deferred or excluded requirement with its disposition
  -- the coverage checker treats an uncited ID as uncovered.
- Keep verification at acceptance-criteria level: what observable behavior
  proves each capability works, not which tool checks it.
- Record open decisions the user still owns, with what each decision blocks.

## Forbidden content

- Do not create sections named `ODC Element Map`, `ODC Elements`,
  `Business Logic`, or `Screen Aggregates`.
- Do not list entity attributes, server action inputs, client actions,
  aggregates, screen widgets, role folders, TrueChange checks, publish checks,
  or browser checks.
- Do not include Studio-native pseudocode of any kind. Element-level detail
  belongs to `outsystems-mentor-implementation`; if the plan seems to need an
  ODC element map to feel complete, stop at capability intent and leave the
  element map to the downstream conversion.
- Do not add a generic Superpowers execution header, and do not copy
  scanner-forbidden token strings into the plan, even inside negative wording.
  Refer to them only as generic execution skills.

## Required handoff header

Start the saved plan with this OutSystems-specific handoff header, adapting
only the paths:

```text
> Handoff: Coverage review: `outsystems-plan-to-mentor`. Mentor conversion: `outsystems-mentor-implementation`. This plan describes capability intent only; the Studio-native element map is produced downstream.
```

## Where element detail goes instead

Element-level knowledge discovered while planning (entity relationships, join
expectations, naming traps, platform observations) belongs in the source spec
or PRD, where the coverage gate and the downstream conversion both read it. The
plan cites the spec; it does not restate the elements.
