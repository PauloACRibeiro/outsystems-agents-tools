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
- Name, verbatim, every entity the screen inventory declares. Entity names
  flow inventory -> plan (`outsystems-screen-inventory` R8), and
  `validate_blueprint.py --plan` reconciles the design route against the plan
  route by matching those names in the plan text on word boundaries: an
  entity the plan never spells, or spells differently, fails reconciliation.
  Naming them is the whole obligation -- attribute shapes stay downstream
  with `outsystems-mentor-implementation`, as the forbidden content below
  says. New action names are not covered: the inventory abstains on those by
  design, and the plan names them.
- Include a `## Traceability` table (`| Story | Requirements | Design |`):
  one row per `US-n` user story, citing the requirement IDs the story
  delivers and its design artifact ref (`blueprint:<ScreenName>` /
  `inventory:<ScreenName>` from the loop's design artifacts, or an explicit
  `none`). The coverage checker fails any defined requirement that appears
  in no row. Every `US-n` a row cites must already be **defined in the
  source** -- its `## Requirement Inventory` table -- because the checker
  computes the story join against the source's story set and fails a row
  whose story the source never defines. Do not invent story IDs in the plan;
  add them to the source first.
- State scope boundaries and deliberately excluded concepts explicitly, and
  cite the ID of every deferred or excluded requirement with its disposition
  -- the coverage checker treats an uncited ID as uncovered.
- Prefer a `## Requirement Dispositions` table (`| ID | Disposition | Reason |`)
  over prose for those exclusions. The vocabulary is closed -- `built`,
  `deferred`, `out-of-scope`, `accepted-risk` -- and each terminal disposition
  needs a reason. A dispositioned requirement leaves both the numerator and the
  denominator, so the verdict says how much of the in-scope set was built
  instead of counting a deferral as coverage. Citing the ID in prose still
  works; it just cannot tell twelve built from three built and nine deferred.
- Do not plan a capability no requirement asks for. Name the requirement ID a
  section serves before writing it; if you cannot name one, it is a proposal,
  not scope -- put it under scope boundaries marked `(proposed)` with the
  reason, for the user to accept or cut. The coverage checker cannot catch
  this: it computes a set difference over cited IDs, so an uncited section
  passes.
- Keep verification at acceptance-criteria level: what observable behavior
  proves each capability works, not which tool checks it.
- **Where the capabilities imply server actions, the source spec declares each
  action's result values and the plan carries a verification matrix over them.**
  One obligation, split across the two artifacts, and the handoff gate's
  `outcome-coverage` clause is a set difference between the halves.
  - In the **source spec** — never in the plan — write one section per action in
    the grammar `scripts/check_outcome_coverage.py` parses: a backticked action
    name as a heading at `###`, then one sentence ending in a period with every
    value backticked, ``Result is one of `Success`, `MemberNotFound`.``
    (`outsystems-sprint-init` — not part of the colleague sprint-loop pack —
    scaffolds that section into `docs/specs/TEMPLATE.md`, so a scaffolded run
    already has the shape; write it by hand otherwise.) Beside those
    declarations, put the marker `<!-- outcome-coverage: success-rows-required -->`
    — every NEW spec carries it; it opts the checker into requiring success
    rows (below), and omitting it keeps the pre-rule semantics for artifacts
    that predate the rule. Where an action changes a status or state, the spec
    also declares a **transition table** (`| from-state | action | to-state |`);
    state names are capability vocabulary, not element design.
  - In the **plan**, give every **non-success** value at least one `V<N>`
    verification row that reaches it by executing the action. The row grammar is
    machine-checkable and defined in `references/coverage-review-prompt.md` —
    in particular the rule that the observed result counts only after a `->`,
    and that a row denying an outcome does not exercise it.
  - **Pair every guard with the thing it protects** (restaurant-app-v2,
    2026-08-27: every guard was tested, no row reached the state the guards
    protect, and the app shipped with its main happy path hard-blocked while
    every gate said READY):
    - Every refusal/guard row pairs with at least one **success-path row** that
      reaches the state the guard protects. Per action, write a row that names
      the action and observes a success value after the `->`
      (``V7  C-007  `Enrol` an eligible user on an open course -> `Success`.``);
      with the spec marker present, the checker fails the verdict without one.
    - Every row of the spec's transition table gets a V-row reaching its
      to-state.
    - The app's **default configuration** is the first happy-path case — the
      first success row runs the configuration the app ships with, before any
      special setup.
    - Absence checks (no prices, no PII) pair with a **presence** check of the
      legitimate content; an empty page passes every absence check.
  - Declaring result values is capability intent: it says which outcomes the
    business rules distinguish, which is the same kind of statement as a
    business rule. It is not element design and does not breach the boundary
    below — the action's inputs, outputs, data shapes and logic steps all stay
    downstream with `outsystems-mentor-implementation`.
- Record open decisions the user still owns, with what each decision blocks.
- Record platform support as a **tri-state**, never a boolean: `supported`,
  `not-supported`, `unknown`. A boolean has nowhere to put "nobody checked",
  so an unchecked capability reads as unsupported and quietly becomes a scope
  cut nobody decided. `unknown` is the honest third value, and it is the one
  that routes a capability to the coverage gate's Platform Feasibility rows.
- **Sequence data work parents-first.** Where the plan orders work that creates
  business concepts, seeds reference data, or loads data, state the order as a
  dependency order: reference data and lookups first, then the concepts nothing
  points out of, then the concepts that reference them, deepest last. The
  reason is not tidiness -- a record that references a parent cannot be written
  before that parent exists, so a plan whose sections happen to run
  child-first describes work that cannot be done in that order. Name the
  ordering constraint; leave the entities and their attributes to the source
  spec.
- **Where data moves incrementally, the checkpoint is an acceptance criterion.**
  A plan calling for a recurring load, sync, or catch-up states three things as
  observable behaviour: that the checkpoint advances only after a run's data is
  validated, written and recorded; that the checkpoint records the run's
  **start** time, so anything changed while the run was in flight is picked up
  next time rather than skipped; and that incoming records are matched to
  existing ones by the source system's own key. Without the first, one failed
  run loses data permanently and silently; without the second, the loss is
  intermittent and much harder to see.
- **Omission is not prohibition.** Where support was read off an enumeration --
  a catalog, a tool's list of what it can do, a reference table -- an absent
  row means *not observed*, never *not permitted*. Enumerations are shallow:
  a contract can live a layer deeper than the introspection reaches, so the
  thing being missing from the list is a fact about the list. Write `unknown`
  with what was checked, not `not-supported`. Only a source that *forbids* the
  capability supports `not-supported`.

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
