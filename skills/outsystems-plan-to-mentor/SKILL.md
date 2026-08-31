---
name: outsystems-plan-to-mentor
description: Review and patch saved OutSystems implementation plans before Mentor conversion. Use when the user has a plan from superpowers:writing-plans, an OutSystems spec-driven workflow, or a hand-written plan and needs PRD coverage review, a patched plan, Mentor-ready prompts, or optional OutSystems MCP delivery through outsystems-mentor-implementation. Also use before the first OutSystems implementation plan is written from an approved PRD, so the plan generator receives the capability-plan brief.
---

# OutSystems Plan To Mentor

Coverage-review any saved OutSystems implementation plan before Mentor conversion. The plan generator is interchangeable; this skill owns the post-plan gate.

This skill works for both Codex and Claude, writes a patched plan before Mentor conversion, and keeps durable artifacts in the active project.

## Routing Boundary

Use this skill when the user has a saved OutSystems plan and asks to review it for coverage, patch gaps, produce Mentor-ready prompts, or optionally send the prepared prompt through OutSystems MCP. Also use it in pre-plan mode when an approved PRD or original request exists but no saved plan does yet.

Do not use this skill to write the original PRD, create the first implementation plan, or produce low-level Studio pseudocode directly. Pre-plan mode hands the capability-plan brief to the selected plan generator; it never writes the plan itself. Delegate Studio-native conversion to `outsystems-mentor-implementation` after the patched plan is written.

## Modes

Route the request before applying the saved-plan input gate:

- Pre-plan mode: an approved PRD or original request exists but no saved plan does. Required input: the source PRD or original request only. Load `references/capability-plan-brief.md`, hand it to the selected plan generator, and stop until the plan is saved. The saved-plan input gate does not apply in pre-plan mode.
- Post-plan mode: a saved plan exists. Required inputs: the source PRD or original request plus the saved plan file. Run the workflow below.

After pre-plan mode, restart in post-plan mode with the new saved plan path.

Do not execute the plan with generic development skills. OutSystems Mentor delivery must go through this coverage gate and then `outsystems-mentor-implementation`.

Do not publish, deploy, rollback, promote, package, push, or create pull requests from this skill. Those actions require separate explicit approval outside the plan-to-Mentor gate.

## Inputs

In post-plan mode, require both inputs before proceeding:

- Source PRD or original request: conversation context or file path.
- Saved plan file: project-local path to the plan being reviewed.

If either input is missing, stop and ask for the missing source. If the plan targets a live app and the user may choose MCP mode, also collect the target app name or app key before MCP delivery.

Before invoking `outsystems-mentor-implementation`, collect the target app state: new-app, template-scaffold, or existing-app. For template-scaffold or existing-app targets, also collect a scaffold inventory source (app map file, Studio observation notes, or OutSystems MCP context output) and pass it in the invocation payload. Do not invoke the companion without a valid target app state; for non-new states, do not invoke without the scaffold inventory source.

If the saved plan file is missing, do not continue coverage review and do not suggest `write-and-review-plan`. Offer to create the saved plan with `superpowers:writing-plans` or another explicit plan generator. After the plan is written, restart this workflow from step 1 with the new saved plan path.

### Pre-Plan Brief

When no saved plan exists yet, or the user asks to prepare for writing the first OutSystems plan, load `references/capability-plan-brief.md` and hand `references/capability-plan-brief.md` to the plan generator before it writes the first saved plan. The brief carries the capability boundary and the required OutSystems-specific handoff header, so the coverage gate does not force a plan rewrite later.

### Missing Plan Generator Boundary

The first saved plan must be a business/capability implementation plan, not an ODC Studio element recipe. Do not adapt `superpowers:writing-plans` by mapping tasks directly to ODC elements.

Do not include Studio-native pseudocode, Server Action logic flows, entity attribute recipes, TrueChange steps, publish steps, or browser verification as the primary plan content. The first plan should describe capabilities, user workflows, acceptance criteria, scope boundaries, dependencies, and open decisions.

Do not create sections named `ODC Element Map`, `ODC Elements`, `Business Logic`, or `Screen Aggregates` in the first saved plan.

Do not list entity attributes, server action inputs, client actions, aggregates, screen widgets, role folders, TrueChange checks, publish checks, or browser checks in the first saved plan.

Use capability headings such as users and goals, workflows, business rules, acceptance criteria, dependencies, open decisions, and scope boundaries.

If the first plan seems to need an ODC element map to feel complete, stop at capability intent and let `outsystems-mentor-implementation` create the Studio-native element map later.

Leave Data Model Pseudocode, Server Action Pseudocode, Client Action Pseudocode, Screen And UI Pseudocode, Navigation Pseudocode, and Verification Pseudocode to `outsystems-mentor-implementation`.

The first saved plan must not include a generic Superpowers execution header. Do not copy scanner-forbidden token strings into the generated plan, even inside negative wording.

Refer to those forbidden strings only as generic execution skills in generated plan text.

Use an OutSystems-specific handoff header that points to `outsystems-plan-to-mentor` for coverage review and `outsystems-mentor-implementation` for Mentor conversion.

## Workflow

1. Read the saved plan and the source PRD or original request.
2. Load `references/coverage-review-prompt.md` and `references/requirement-id-conventions.md`.
3. Establish the Requirement Inventory: use the source's stable requirement IDs when it carries them, otherwise assign `BR-`/`UC-`/`C-`/`US-` IDs per the conventions (namespace business rules per surface for multi-surface plans, e.g. `BR-DM-`/`BR-SC-`/`BR-SEC-`) and record the inventory at the top of the coverage review artifact. Then audit the plan against the source of truth using the required ID-keyed coverage matrix. Extract the plan's platform-capability claims and audit them as platform feasibility rows in the same pass.
4. If coverage ambiguity would change requirements, stop and ask before patching.
5. Write the coverage review to `docs/superpowers/plans/{plan-stem}-coverage-review.md`.
6. Write a minimally patched plan to `docs/superpowers/plans/{plan-stem}-patched.md`. The patched plan cites each requirement ID inline where it is addressed, carries a `## Requirement Dispositions` table (`| ID | Disposition | Reason |`) for every requirement it does not build — closed vocabulary `built`/`deferred`/`out-of-scope`/`accepted-risk`, each terminal disposition with a reason — and carries the `## Traceability` table (`| Story | Requirements | Design |`) per the requirement ID conventions. A pre-traceability plan under review is accepted with the checker's note; the patched plan this skill writes always includes the table. The patched plan artifact must be a complete executable plan, not a change summary or wrapper. Copy the full patched plan content into `docs/superpowers/plans/{plan-stem}-patched.md`. Do not patch only the original plan in place and leave `-patched.md` as a short summary. Preserve every heading the original plan carries, verbatim, including its H1 title: the structural non-regression check at step 7 compares heading text level-insensitively and reads the title as a heading like any other, so renaming `# Booking Plan` to `# Booking Plan (patched)` registers as a dropped section and fails the scan. Append a `## Change Summary` section rather than renaming anything — the patched plan is identified by its filename, never by its title, and added headings are never reported. Before writing the patched file, rewrite any generic Superpowers execution header to the OutSystems-specific handoff header.
7. In every pass, run `scripts/check_handoff_gate.py`: `--source` the requirement inventory (or ID-carrying PRD), `--plan` the same full patched plan file that will be sent to `outsystems-mentor-implementation`, `--design` the design file declaring action results, `--blueprint`/`--inventory` when the run's design artifacts (enriched blueprint.json, screen-inventory.json) are on disk, so traceability design refs resolve against real `screens[].name` values, and `--original-plan <plan the patch was made from>` whenever that file is on disk — the gate forwards it to the handoff scanner as `--source <original plan>`, which is why the two names differ: this gate's own `--source` is the requirement inventory. It enables the scanner's structural non-regression check (headings present in the original and absent from the patched file — it catches a silently summarised patched artifact that the two-phrase summary guard cannot see; additions are never reported, and headings the scanner itself orders removed are exempt). The gate invokes `scripts/check_requirement_coverage.py`, `scripts/check_outcome_coverage.py` and `scripts/check_plan_handoff.py` as subprocesses and computes one verdict over named clauses; it replaces none of them. Copy its full output verbatim into the review artifact. The clause table, the coverage numbers and the coverage verdict are computed, never hand-authored. When the plan carries a `## Requirement Dispositions` table, the coverage rate is over the in-scope set (defined minus dispositioned); the `requirement-coverage` clause carries the checker's own in-scope and dispositioned counts verbatim in its captured output, and they are reported as printed — a READY verdict over the in-scope set says nothing about what was dispositioned out of it. No clause is ever skipped: an input you do not supply fails its clause with `input-not-supplied`, so supply the missing artifact rather than dropping the flag — dropping it cannot reach READY. The same rule reaches inside the coverage clause, where it used to stop at the gate's own arguments: the gate always runs `check_requirement_coverage.py` with `--strict`, so an unresolved design ref — a `blueprint:`/`inventory:` ref in a Traceability row whose artifact you did not pass — fails the requirement-coverage clause instead of going silently unchecked while the run prints READY. Fix it by supplying `--blueprint`/`--inventory`, or by writing that story's design cell as an explicit `none`; run the checker directly without `--strict` if you want the unresolved refs listed as a note rather than a failure. `--inventory` also buys the closure check: every destination reachable from a screen the plan builds must itself be built by the plan, or the run fails with an **unbuilt destination** naming the control, its screen and the screen it opens. Read what it is and is not: on the two apps that paid for this rule the create and edit edges were never written at all, so this check would have stayed silent and its sibling in `outsystems-screen-inventory` — which is where the *offer* is closed — is the load-bearing half. This one nets a strictly different failure, an inventory that DID name the destination against a plan with no item for it, and it arms itself only once the inventory declares one. Fix a finding by adding the plan item, or settle it upstream — an action declared `inline` or `out-of-scope` names no destination and is not checked, the second being the recorded statement that the control is not built at all. `--design` now reaches two clauses: `outcome-coverage` reads its result declarations, and the coverage checker reads its `Inputs are ...` sentences for the **contract reachability** note — every input an action declares must be named where the plan or the inventory says a user supplies it (`screens[].accepts`, `navigation[].payload`, `screens[].key_interactions`), or carry `(internal)` for a value no interface can supply, or `(waived: <reason>)` for one this build deliberately does not offer. It is a note with no `--strict` form and it cannot move a clause: it matches on the name, which is evidence of naming rather than of a control, and the sentence is opt-in while the gate always passes `--strict`, so a blocking form would punish the spec that declares its inputs and reward the one that declares nothing. Read it as the question "where does this value come from?", answered in the spec — on restaurant-app-v2, where `OpenMenuForDate` was date-parameterised and the only control ever built was "Criar ementa de hoje", the true answer was "always today" and nobody wrote it. A design declaring no inputs prints nothing. One traceability finding is deliberately a note with no `--strict` form: a story whose whole Requirements cell is dispositioned delivers nothing in this build, and the checker names the row and each ID's disposition word so the table cannot read as live work — but it never fails, because that story must own a row and the row must cite an ID, so there is no compliant shape to fail the author toward. Read it as a scope signal to carry into the review, not a defect to patch out of the plan. The only exit from a failing clause is a waiver: `--waivers handoff-waivers.json` (schema at `schemas/handoff-waivers.schema.json`) moves one named clause to `WAIVED`, and every waiver carries a recorded reason that the gate prints. `WAIVED` is not `PASS` — the clause keeps the evidence of its own failure beside the reason it was excused. A waiver with no recorded reason, or naming a clause outside the vocabulary, or otherwise malformed, refuses the whole waiver file and denies READY; one bad entry voids the good ones with it. A waiver file that is not there simply means no waivers, which can only make the gate stricter.
8. Run at least two coverage passes before delivery mode. Pass 2 audits the patched plan against the same source of truth, writes `docs/superpowers/plans/{plan-stem}-coverage-review-v2.md`, and patches the plan again if any row is Missing, Partial without accepted platform/runtime uncertainty, unsupported by evidence, or invalid for ODC/Mentor implementation, or if the gate reports NOT READY.
9. Repeat the coverage loop until convergence or max 3 passes. Convergence means the gate reports `handoff verdict: READY` — every clause PASS, or `WAIVED` with a recorded reason: no uncovered IDs, no dangling references, every declared refusal outcome reached by a verification row, and no forbidden generic handoff language — plus no Missing rows, no Partial except explicitly accepted platform/runtime uncertainty, no Infeasible or Unverified platform feasibility rows, and all top gaps closed or documented as accepted runtime risk. If a third pass is needed, write `docs/superpowers/plans/{plan-stem}-coverage-review-final.md`.
10. Write each coverage pass to a versioned review artifact and show the final `Coverage Audit -- Patched Plan vs Spec` table plus the gate's clause table and verdict before asking how to deliver.
11. If the `handoff-scan` clause fails on a forbidden generic handoff, an ODC element recipe section, or a planned action name that collides with an entity's auto-generated action, patch the plan again and rerun the gate. A colliding name is renamed to a verb phrase (`BookRoom`, not `CreateBooking` beside entity `Booking`); the platform gives no error for the collision, it silently declines to create the action.
12. Load `references/delivery-modes.md`.
13. Do not ask the delivery mode question until the gate reports `handoff verdict: READY`.
14. Ask the delivery mode question exactly once:

```text
1 - Create prompts ready to paste sequentially in Mentor in ODC Studio
2 - Send to Mentor using the OutSystems MCP
```

15. Load `references/mentor-spec-guardrails.md`.
16. Load `references/mentor-implementation-invocation.md`. Compose the payload's `Excluded scope:` field before invoking the companion: every excluded candidate in the run's `screen-inventory.json` when one is on disk, plus every terminally dispositioned requirement ID in the patched plan, each carried with its disposition word from the closed vocabulary (`deferred`, `out-of-scope`, `accepted-risk`). Send the literal `none recorded` when there is nothing to exclude. The field is a do-not-build list: it reaches Section 8 of the Mentor spec and nothing on it gets built.
17. Companion Availability Gate: Before invoking `outsystems-mentor-implementation`, determine whether `outsystems-mentor-implementation` is available in the active agent's skill catalog or local skill roots.
18. Prefer the full companion flow whenever `outsystems-mentor-implementation` is available. If `outsystems-mentor-implementation` is available, use the full companion flow. Invoke `outsystems-mentor-implementation` with that same full patched plan path, source PRD or request, selected delivery mode, output file path, and relevant Mentor spec guardrails.
19. Require `outsystems-mentor-implementation` to write the Mentor-ready output file before any MCP send.
20. If `outsystems-mentor-implementation` is not available, ask the missing-companion fallback choice exactly once, separate from the delivery mode question:

```text
1 - Stop after the patched plan and install or use outsystems-mentor-implementation for the full deterministic Mentor package
2 - Write a DEGRADED OUTPUT paste-mode 10-section Mentor spec
```

21. If the user chooses option 1, stop after the patched plan. Report the patched plan path and explain that the full flow requires installing or using `outsystems-mentor-implementation`. State: Install or use `outsystems-mentor-implementation` for the full deterministic Mentor package.
22. If the user chooses option 2, write `docs/superpowers/plans/{plan-stem}-mentor-output.md` as a DEGRADED OUTPUT using only the 10-section Mentor spec format from `references/mentor-spec-guardrails.md`. This is a degraded paste-mode Mentor spec.
23. Degraded paste-mode Mentor spec output must be paste mode only. Do not send degraded output through OutSystems MCP, and do not label degraded output as Studio-native pseudocode.
24. At the top of degraded output, emit the DEGRADED OUTPUT notice in `references/prompt-templates/degraded-output-notice.md` verbatim (no placeholders).

## Artifact Rules

Use project-local artifacts:

- Coverage review: `docs/superpowers/plans/{plan-stem}-coverage-review.md`
- Coverage review v2: `docs/superpowers/plans/{plan-stem}-coverage-review-v2.md`
- Final coverage review, when needed: `docs/superpowers/plans/{plan-stem}-coverage-review-final.md`
- Patched plan: `docs/superpowers/plans/{plan-stem}-patched.md`
- Mentor output: `docs/superpowers/plans/{plan-stem}-mentor-output.md`
- MCP result, when used: `docs/superpowers/reviews/{plan-stem}-mentor-result.json`

The patched plan file is the source of truth for downstream Mentor conversion.
It must contain the full final plan text after all coverage patches. A separate
change-summary section may be included inside the full file, but a summary-only
artifact is invalid.

Do not write to Claude-private cache/config, Codex-private config, plugin caches, or agent-private runtime folders.
## When an artifact is not produced

Adopted 2026-08-24 from the `OutSystems/-UX-UI-Hub` mining pass (X-16/X-17).
The list above already marked two artifacts conditional — "when needed", "when
used" — without ever saying what the condition was. An omission marker nobody
can evaluate is worse than none: it reads as discretionary. Each condition is
drawn from the workflow above, not invented here.

- **Coverage review v2 is not conditional.** Step 8 requires at least two
  passes, so it is always written. It sits in the same list as the conditional
  artifacts and is not one of them.
- **Final coverage review** — written only when a third pass actually runs,
  i.e. the gate did not report `handoff verdict: READY` after pass 2. Step 9
  caps the loop at three passes, so this artifact exists for at most one pass.
  Converging on pass 2 and writing no final review is the normal good case.
- **MCP result** — written only when the user chose delivery mode 2 at step 14
  *and* the OutSystems MCP tools were actually available in the active agent.
  Paste mode produces none, and its absence is not a gap to explain away.
- **Mentor output** — **not produced at all** when the user takes fallback
  option 1 at step 21 (stop after the patched plan and install or use
  `outsystems-mentor-implementation`). That is a **legitimate terminal
  outcome**, not a failure and not a degraded run: report the patched plan path,
  say why the flow stopped, and stop. Do not substitute a degraded paste-mode
  spec the user did not ask for.

**The patched plan is never optional.** It is the source of truth for
downstream Mentor conversion, and a run that produced no patched plan produced
nothing. A list of what may be absent, without a statement of what may not,
licenses over-omission.

## A recorded outcome is not evidence the artifact exists

Adopted 2026-08-26 from the `OutSystems/shapers-workspace` mining pass (T2). Their
prerequisite gate reads a recorded lifecycle state *and* globs the directory that
state describes, then treats a mismatch as a finding rather than trusting either
side.

The rule above says which artifacts may legitimately be absent. It does not cover
the case where a **record and the disk disagree** — a plan whose step is ticked
done, or a prior run's report claiming a coverage review, while the named file is
not there. Both directions are drift, and both are reported, never silently
resolved:

- **Record says produced, file is absent.** The claim is unsupported. Say so
  naming the path that is missing, and re-run the step that writes it. Do not
  amend the record to match the disk — the skill that owns the step owns its
  state.
- **File is present, record does not mention it.** There is on-disk work the
  record does not reflect. Say so; do not consume the file as though it had been
  produced by this run, and do not overwrite it before the user has seen that it
  exists.

Cross-check every artifact path a run is about to report, not just the one it
happened to write last. `check_handoff_gate.py` already refuses to skip a clause —
this is the same discipline one layer out: a clause discharged against a file
nobody looked for is a skipped clause wearing a PASS.


## Compatibility

Keep the canonical workflow compatible with both Codex and Claude:

- Use plain skill and capability names in durable instructions.
- Keep Codex-only tool discovery notes out of the core workflow.
- Keep Claude-only tool names and cache paths out of the core workflow.
- Treat OutSystems MCP delivery as conditional on tools being available in the active agent.
- If MCP mode is selected but tools are unavailable, say so explicitly and fall back to paste mode unless the user chooses to stop.

## Final Response

Report:

- The computed clause table and `handoff verdict:` line from `scripts/check_handoff_gate.py`, copied verbatim, including each clause's captured checker output: the covered/in-scope counts, the defined and dispositioned counts when the plan carries a Requirement Dispositions table, plus the uncovered and dangling lists (both empty at convergence).
- Every `WAIVED` clause with the recorded reason that excused it, so a waived handoff is never reported as a clean one.
- Final `Coverage Audit -- Patched Plan vs Spec` table.
- Top gaps closed.
- Coverage review paths.
- Patched plan path.
- Mentor output path.
- Whether the Mentor output came from the full `outsystems-mentor-implementation` companion flow or degraded paste mode.
- If degraded paste mode was used, state that the output is a 10-section Mentor spec only and does not include Studio-native pseudocode packages.
- MCP result path when MCP mode was used.
- Remaining user decisions.
