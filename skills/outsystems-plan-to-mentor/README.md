# outsystems-plan-to-mentor

Use this skill after you already have an OutSystems implementation plan and
need to turn it into Mentor-ready work. It coverage-audits the plan against the
source PRD or original request, writes a minimally patched plan file, asks how
the result should be delivered, then routes the patched plan to
`outsystems-mentor-implementation`.

The skill works with Codex and Claude because the core workflow is plain
Markdown, uses project-local files, and treats MCP delivery as optional. It does
not depend on agent-private config, private caches, or a single plan generator.

## What It Is For

Use it when you have a saved OutSystems plan from any source and want a
reviewable gate before Mentor conversion:

- a plan from `superpowers:writing-plans`
- a spec-driven OutSystems workflow
- a hand-written plan
- a plan copied from another agent or conversation

Do not use it to write the first PRD or the first plan. Create or save the plan
first, then run this skill as the post-plan gate.

## Pre-Plan Brief

Hand the plan generator `references/capability-plan-brief.md` before the first
plan is written. The brief keeps the first plan at
capability level and injects the required OutSystems-specific handoff header,
so the coverage gate does not force a plan rewrite later.

## Missing Plan Behavior

If the source PRD exists but the saved plan file does not, stop before coverage
review. Do not suggest `write-and-review-plan`. Use `superpowers:writing-plans`
or another explicit plan generator to create the saved plan first, then rerun
`outsystems-plan-to-mentor` with the new plan path.

## Business Intent Plan Boundary

The missing-plan fallback should create a business/capability implementation
plan, not an ODC Studio element recipe. Do not map writing-plans tasks directly
to ODC elements.

The first plan should stay focused on capabilities, user workflows, acceptance
criteria, scope boundaries, dependencies, and open decisions. Studio-native
pseudocode belongs in `outsystems-mentor-implementation`, after
`outsystems-plan-to-mentor` has completed the coverage loop and patched plan.

Do not create ODC element inventory sections. Do not list entity attributes,
server action inputs, client actions, aggregates, or screen widgets. Use
capability headings such as users and goals, workflows, business rules,
acceptance criteria, dependencies, open decisions, and scope boundaries.

Do not include generic Superpowers execution headers. Do not copy
scanner-forbidden token strings into saved plan text, even inside negative
wording. Use an OutSystems-specific handoff header that sends the plan through
`outsystems-plan-to-mentor` first, then `outsystems-mentor-implementation`.

## Required Inputs

- Source PRD or original request: the source of truth for coverage review.
- Saved plan file: the implementation plan to audit and patch.
- Target app name or app key: only needed if you may choose OutSystems MCP
  delivery.

## Main Strategy

The strategy from the design session is to keep plan creation interchangeable
and make this skill own the review-to-Mentor handoff:

```text
PRD / original request
        |
any plan generator
(superpowers:writing-plans, spec-driven, hand-written, etc.)
        |
outsystems-plan-to-mentor
        |
bounded coverage loop + patched plan file
        |
delivery mode question
        |
outsystems-mentor-implementation
        |
Mentor-ready file
        |
paste manually OR send via OutSystems MCP
```

This keeps the workflow deterministic: the original plan is not treated as
Mentor-ready until it has been checked against the source request, patched, and
scanned for generic execution handoffs.

In short, the skill still produces a coverage audit + patched plan file; it now
does so through a bounded loop rather than a single review.

## Companion Availability

With `outsystems-mentor-implementation` available, this skill runs the full flow:

```text
coverage audit + patched plan
        |
outsystems-mentor-implementation
        |
full deterministic Mentor package
        |
Manual Setup Gate + Session Readiness Matrix + Studio-native pseudocode + Mentor executable sessions
```

Without `outsystems-mentor-implementation` available, this skill still provides value but has a smaller boundary:

- It can complete the coverage loop.
- It can write the full patched plan.
- It can stop and tell you to install or use `outsystems-mentor-implementation` for the full deterministic Mentor package.
- If degraded paste mode is acceptable, it can write a DEGRADED OUTPUT file using the 10-section Mentor spec format only.

The degraded paste-mode Mentor spec is paste mode only and does not include Studio-native pseudocode packages. It does not include Data Model Pseudocode, Server Action Pseudocode, Client Action Pseudocode, Screen/UI Pseudocode, Navigation Pseudocode, or Verification Pseudocode.

Install or use `outsystems-mentor-implementation` for the full deterministic Mentor package.

## Coverage Loop

The skill always runs at least two passes before delivery mode. Every
requirement in the source gets a stable ID (`BR-` business rule — namespaced
per surface for multi-surface plans, e.g. `BR-DM-`/`BR-SC-` —, `UC-` use
case, `C-` acceptance criterion, `US-` user story; see
`references/requirement-id-conventions.md`), and each pass writes a visible
matrix headed `Coverage Audit -- Patched Plan vs Spec`, one row per ID:

```markdown
| ID | Requirement | Status | Evidence | Patch / Risk |
|---|---|---|---|---|
```

Coverage itself is mechanical, not self-reported:
`scripts/check_requirement_coverage.py` computes the set difference between
the IDs the source defines and the IDs the plan cites inline, and its
`READY` / `NOT READY` verdict is computed, never hand-authored. New plans
also carry a `## Traceability` table (`| Story | Requirements | Design |`)
joining each `US-` story to the requirement IDs it delivers and to a design
artifact ref (`blueprint:<Screen>` / `inventory:<Screen>`, resolvable
against the artifacts via `--blueprint`/`--inventory`); the checker fails
any requirement mapped to no story, any story without exactly one
well-formed row, and any table-only citation (the table region never counts
as inline coverage). A pre-traceability plan without the table keeps the
citation-only contract, with a printed note. The matrix's Evidence column
stays the judgement layer on top: the checker proves every ID is cited, the
reviewer verifies each citation is honest.

A plan also carries a `## Requirement Dispositions` table
(`| ID | Disposition | Reason |`) for anything it does not build. The
vocabulary is closed — `built`, `deferred`, `out-of-scope`, `accepted-risk` —
and each terminal disposition needs a reason. A dispositioned requirement
leaves the numerator and the denominator both, so the checker reports
`covered/in-scope` with the defined and dispositioned counts beside it. The
older discharge — citing a deferred ID in the plan's scope boundaries — was
never wrong and still works; what it could not do was distinguish a plan that
builds twelve requirements from one that builds three and defers nine, since
both printed `12/12 READY`. A plan with no disposition table keeps the exact
prior verdict.

Given `--design`, the coverage checker also reads the design's
``Inputs are `A`, `B`.`` sentences and reports, as a **note**, every declared
action input that nothing accounts for — not named where the plan or the
screen inventory says a user supplies it, and carrying neither `(internal)`
nor `(waived: <reason>)`. It never moves the verdict, because it matches on
the name rather than on a declared token and because the sentence is opt-in:
a blocking form would let a spec that declares nothing keep READY while one
that declares its inputs can lose it. It exists because restaurant-app-v2
shipped `OpenMenuForDate` — date-parameterised, with duplicate-date handling —
behind a UI whose only control was "Criar ementa de hoje", so the product's
core carry-over claim was unreachable and every gate said READY.

The three checkers are not sequenced by hand. `scripts/check_handoff_gate.py`
invokes `check_requirement_coverage.py`, `check_outcome_coverage.py` and
`check_plan_handoff.py` as subprocesses and computes one `handoff verdict:`
over named clauses. Two properties matter. The verdict comes from each
checker's **exit code**, never from parsing its printed prose, so a checker
that rewords its output cannot silently change the gate's answer. And there is
no skipped clause: an input that is not supplied, a checker that is missing,
crashes, or hangs, each fails its clause with a named reason. A gate that
reported READY because a clause never ran would be worse than the three
separate exits it replaces. The gate adds no reporting of its own: each clause captures its checker's
output verbatim, so the coverage clause carries the `covered/in-scope` line
and the dispositioned counts exactly as the checker printed them.

The visible consequence, stated rather than discovered in a run: the outcome
checker needs a design file, so a run without `--design` gets
`outcome-coverage: FAIL (input-not-supplied)` and cannot reach READY. Supply
the design file; do not drop the flag.

When the design file genuinely does not exist, the honest way past that clause
is a waiver, not a dropped flag. `--waivers handoff-waivers.json` moves one
named clause to `WAIVED`; the file's shape is published as
`schemas/handoff-waivers.schema.json`. Every waiver names its clause and
records why, and both the reason and the clause's original failure evidence are
printed — `WAIVED` is a third state, never folded into `PASS`. The refusals are
deliberately blunt: a waiver with no recorded reason, an undefined clause name,
an unrecognised key or a duplicated clause refuses the **whole** file and
denies READY, because a file its author demonstrably got wrong should not move
the verdict at all. A waiver whose clause passed anyway is inert and reported
as unused, and a waiver file that is not there means no waivers — absence can
only ever make the gate stricter.

Pass 1 reviews the original plan and writes the first full patched plan. Pass 2
reviews the patched plan as if it came from someone else. A third pass is used
only when remaining Missing or Partial rows, weak evidence, or ODC/Mentor
precision issues still need closure. The delivery mode question comes after the
final matrix and the gate's `handoff verdict: READY`, not before.

The `-patched.md` artifact is the full patched plan, not a summary wrapper. If
the original plan is also edited in place, the full final content still needs to
be copied into `-patched.md` because the scanner and Mentor conversion use the
same `-patched.md` file.

## Outputs

By default the skill writes project-local artifacts:

- `docs/superpowers/plans/<plan-stem>-coverage-review.md`
- `docs/superpowers/plans/<plan-stem>-coverage-review-v2.md`
- `docs/superpowers/plans/<plan-stem>-coverage-review-final.md`, only when a
  third pass is needed
- `docs/superpowers/plans/<plan-stem>-patched.md`
- `docs/superpowers/plans/<plan-stem>-mentor-output.md`
- `docs/superpowers/reviews/<plan-stem>-mentor-result.json`, only when MCP
  delivery is used

The Mentor-ready file is always written before any optional MCP send.

## Codex Prompt

```text
$outsystems-plan-to-mentor

Source PRD or original request:
<path or pasted source>

Saved plan file:
<path to the plan>

Target app, if MCP delivery may be used:
<app name or app key, or "paste mode only">
```

## Claude Prompt

```text
Use the `outsystems-plan-to-mentor` skill.

Source PRD or original request:
<path or pasted source>

Saved plan file:
<path to the plan>

Target app, if MCP delivery may be used:
<app name or app key, or "paste mode only">
```

## Portability Notes

- Keep durable artifacts in the active project.
- Keep Codex adapter metadata isolated to `agents/openai.yaml`.
- Keep the core workflow free of Claude tool names and Codex tool names.
- Use paste mode when OutSystems MCP tools are unavailable.
- Do not publish, deploy, roll back, promote, package, push, or create pull
  requests from this skill without separate explicit approval.
