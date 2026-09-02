# Coverage Review Prompt

Use this prompt after writing or receiving a saved OutSystems implementation
plan and before Mentor conversion. The coverage gate is a bounded convergence
loop: run at least two coverage passes. Even if pass 1 claims full coverage,
run pass 2, and stop after max 3 passes.

Load `references/requirement-id-conventions.md` first. The coverage number
and the coverage verdict come from `scripts/check_requirement_coverage.py`;
they are computed, never hand-authored.

This gate audits the plan against the spec and stops at conversion. Auditing
the *built* app back against the same spec is a separate pass this skill does
not run; `references/post-build-gap-pass.md` records its shape for a run that
wants one.

```text
Using the original request/PRD already in this conversation as the source of truth, audit the plan you just produced for coverage and alignment.

First, establish the Requirement Inventory. If the source already carries stable requirement IDs (BR- business rules, UC- use cases, C- acceptance criteria), use them unchanged. If it does not, assign IDs per the requirement ID conventions and write the `## Requirement Inventory` table at the top of the coverage review artifact. IDs stay stable across passes: later passes reuse the same inventory and may only append.

While writing the inventory, watch for a requirement that asserts two obligations. The checker scores whole ID tokens, so two obligations wearing one ID score as covered the moment the plan addresses either half. When you meet one, split it in pass 1: append the second obligation as a new ID and leave existing rows unchanged. Never renumber, and never invent a sub-ID (`BR-007.a`) — the checker cannot see one. Pass 1 is the only cheap moment, because from pass 2 on the plan already cites the IDs; a later pass records the compound in the matrix's Patch / Risk column instead of resplitting it.

For each requirement in the inventory:

* mark it **Covered / Partial / Missing**
* briefly cite *where* it is addressed in the plan (section name or a short quote). If you cannot point to evidence, treat it as **Partial** or **Missing**.

Write the coverage matrix in this exact shape, one row per inventory ID:

## Coverage Audit -- Patched Plan vs Spec

| ID | Requirement | Status | Evidence | Patch / Risk |
|---|---|---|---|---|

## Platform Feasibility

In the same pass, extract the plan's platform-capability claims: anything the plan assumes the platform can do, such as agent call configuration, structured output, action calling, AI model connections, integration patterns, timers, workflows, or offline behavior.

Add each claim as an extra matrix row (use `--` in the ID column) marked **Feasible / Infeasible / Unverified**:

* **Feasible** only with evidence from a current official OutSystems source retrieved this session: a public knowledge provider (`workspace-knowledge-cc` or `outsystems-public-knowledge` — either provider is acceptable; they expose the same public retrieval role), `outsystems-tech-content`, or live official docs. The companion constraint references from `outsystems-mentor-implementation` (start with its `agentic-routing.md` reference for agentic claims) may route to the official source, but a companion summary alone is not authority. If the official source cannot be retrieved, keep the row Unverified. When the evidence came from a public provider only — OMI's `provider: public-grounded` — the row is Feasible on public-docs authority; do not promote it to implementation-level authority, and keep it Unverified when it depends on exact TrueChange error text, internal/courseware material, or widget rules beyond OMI's generated catalogs, which a public provider cannot ground.
* **Infeasible** when the docs forbid the claimed configuration. Known example: action calling and structured output cannot be combined on the same agent call; a plan that assumes both on one call must be restructured before conversion.
* **Unverified** when no evidence was found either way. Say what was checked.

Do not declare convergence while any platform feasibility row is Infeasible or Unverified. An Infeasible row is an architecture decision for the user, not a silent patch; stop and present options. Feasibility checked here is cheap; the same discovery inside `outsystems-mentor-implementation` ripples back into spec and plan rework.

## Execution Outcome Coverage

Every build-time signal this loop relies on -- validation, coverage, enumeration, `change_applied`, retry count, publish status -- describes whether the right *shapes* exist. None of them can observe whether the logic inside those shapes does its job. A server action can pass every one of them and do nothing at all; that is a measured outcome, not a hypothetical.

So: **every non-success result value the design declares for a server action must have at least one verification row that reaches it by executing the action.** A refusal branch is reached only on purpose — and so, it turned out, is the success path: "any happy-path test reaches it" held until restaurant-app-v2 shipped with no happy-path test at all, which is why the success-path pairing rules below exist.

Write the verification matrix so each row is machine-checkable: one row per line beginning `V<N>`, naming the outcome it reaches, with indented continuation lines where a row wraps.

**Put the observed result after a `->`, and only there.** The checker counts an outcome as exercised only when it appears after the arrow, because that is the only part of a row that says what came back — everything before it is setup. `V4  C-004  Enrol with an id that does not exist -> "CourseNotFound".` counts; naming the outcome while describing the setup does not.

**A row that denies an outcome does not exercise it.** `-> never returns "CourseNotFound"` observes an absence, which is the opposite of reaching the branch, and the checker discards it. Write a row that reaches the refusal on purpose.

Both rules are deliberately conservative: an outcome genuinely exercised but written without an arrow reads as unexercised and the run says `NOT READY`. That costs a plan edit. The opposite error ships an untested refusal branch — which is how a row asserting two refusals were *never* returned once scored them as fully covered.

**Each refusal row must record the relevant state before and after the call, not the message the caller saw.** A refusal that returns the right value while writing a row is a defect no message-only assertion can see. State the evidence as the before/after reading, not as a screenshot of the refusal.

**Tests that verify the guard but never the thing the guard protects are the failure class the next four rules close.** Measured on restaurant-app-v2 (2026-08-27): every translation-failure row and the approval-refused row passed, while no row asserted that a menu with nothing to translate can reach `Traduzida` and be approved — so the app's DEFAULT single-language configuration shipped with its main happy path hard-blocked, and every gate said READY.

1. **Every refusal/guard row pairs with at least one success-path row that reaches the state the guard protects.** For each action with refusal rows, write a V-row that names the action and observes a success value after the `->`. A guard proven to refuse is worthless when the protected state is reachable by nothing.
2. **An action that changes a status or state declares a transition table** — `| from-state | action | to-state |` — in the design, **and every transition gets a V-row** reaching its to-state. An early-exit that skips a transition is exactly what a refusal-only matrix cannot see.
3. **The app's DEFAULT configuration is the first happy-path case.** Write the first success row against the configuration the app ships with, before any special setup. The v2 block lived precisely in the most common configuration, which no row ever ran.
4. **Absence checks pair with presence checks.** A row scanning for what must NOT appear (no prices, no PII) pairs with a row asserting the legitimate content IS present — an empty page passes every absence check.

The checker enforces rule 1 mechanically when the design opts in by carrying the marker `<!-- outcome-coverage: success-rows-required -->` (put it in the spec beside the result declarations; every NEW spec carries it). With the marker, each action that declares non-success results also needs a success row — one that names the action on a word boundary and observes a success value (`Success`, `Created`, ...) after the arrow, same denial scoping as refusals — and the checker prints `success coverage: k/n` and fails the verdict on any miss. Without the marker the checker keeps its pre-rule semantics, so plans written before this rule keep their verdicts. Rule 4 is also mechanical under the same marker: any design criterion or plan V-row naming a payload or projection with an absence assertion ("no price", "must not contain", "never emits", "omits") needs a paired presence row (a count, "one row per item", "contains"). Pairing is keyed by requirement ID first — the design row's `| ID |` cell and the ID a V-row cites right after `V<N>` — then by the action name the row mentions when it cites no ID, and last by a shared "payload" bucket when it has neither; that last bucket is a documented blind spot, since two unrelated ID-less, action-less payload rows can still cancel each other out in it. The checker prints `containment coverage: k/n`. Rules 2–3 remain review judgement, not machine-checked: audit them in this pass and record misses in the Patch / Risk column.

Run the checker and copy its full output verbatim into the review artifact:

```
python3 scripts/check_outcome_coverage.py <design-file> <plan-under-review>
```

(On Windows PowerShell, `python` -- `python3` is not a command there.) The numbers and the `outcome verdict:` line are computed, never hand-authored.

**Scope note, because getting it wrong makes the check useless in the most dangerous direction:** the checker reads only the `V<N>` verification rows, not the whole plan. A plan also carries the Mentor prompts, which name every outcome because they instruct the build to return them -- so a whole-plan scan reports full coverage for a plan whose matrix tests nothing, and can only ever say READY.

## Contract Reachability

An action's declared outcomes say what it can return. Its **inputs** say what a
caller must supply — and an input no interface can supply is a capability the
app does not have, however correctly the action is built.

Measured on restaurant-app-v2 (2026-08-30). The spec's contract for menu
creation was `OpenMenuForDate`, "opens the menu for a restaurant and date",
explicitly date-parameterised and with duplicate-date handling. The UI as
planned and as built offered one control, "Criar ementa de hoje". No date
input existed anywhere, so tomorrow's menu could not be created and the
product's core carry-over claim was untestable until an unplanned Mentor turn
added a date field. Every gate said READY: nothing compared action contracts
against UI affordances.

So, in the **source spec**, beside each action's result declaration, write one
sentence naming its inputs — same grammar as the result sentence, every name
backticked, the list stopping at the first period:

```text
#### `OpenMenuForDate`

Opens the menu for a restaurant and date, creating a draft when none exists.
Inputs are `RestaurantId` (internal), `MenuDate`.
Result is one of `Created`, `DuplicateDate`, `NoRestaurantInScope`.
```

Each input is accounted for in one of three ways. Either the **plan or the
screen inventory names it** where a user supplies it (`screens[].accepts` — the
route or query parameter —, `navigation[].payload`, or
`screens[].key_interactions`); or it carries `(internal)`, meaning no interface
can supply it by construction — a session binding, a constant; or it carries
`(waived: <reason>)`, meaning one could and this build does not offer one, on
purpose. A `waived` with no reason is refused, exactly as a terminal
disposition with no reason is.

The checker reports anything left over as a **note**, never a failure, and
`--strict` does not escalate it. Two reasons, and the second is the load-bearing
one. It matches on the name, which is evidence of naming and not of a control:
an affordance spelled in the product's own language (the v2 inventory carries
the payload as `menu date`, not `MenuDate`) reads as unaccounted-for. And the
`Inputs are` sentence is opt-in while the handoff gate always passes
`--strict`, so a blocking form would let a spec that declares nothing keep
READY while a spec that declares its inputs can lose it — honesty must not be
the expensive option.

Read the note as a question to answer in this pass, not as a formatting slip to
patch out. Record each finding in the matrix's Patch / Risk column, and answer
it in the spec: name the affordance that supplies the value, add the affordance
to the plan, or write down that nothing supplies it and why. On the incident
the true answer was "always today" — the sentence nobody in that run ever
wrote, and writing it is where the product gap becomes visible.

The check runs when the coverage checker is given `--design`; a design that
declares no inputs prints nothing, so artifacts written before this grammar
keep their output unchanged.

## Traceability Table

The plan must carry a `## Traceability` section in the shape the requirement
ID conventions define — one row per user story, joining the story to the
requirement IDs it delivers and to its design artifact:

| Story | Requirements | Design |
|---|---|---|

Design refs are `blueprint:<ScreenName>` / `inventory:<ScreenName>` (the
artifact's `screens[].name`), or an explicit `none`. When the run has the
design artifacts on disk, pass them to the checker
(`--blueprint <blueprint.json>` / `--inventory <screen-inventory.json>`) so
every ref is resolved against real screen names.

A pre-traceability plan (no table) is accepted with the checker's printed
note and citation-only coverage; do not retrofit a table into in-flight run
artifacts. Every NEW plan, and every patched plan this review writes, includes
the table.

## Requirement Dispositions Table

Every requirement the patched plan does not build goes in a
`## Requirement Dispositions` section, in the shape the requirement ID
conventions define:

| ID | Disposition | Reason |
|---|---|---|

The vocabulary is closed — `built`, `deferred`, `out-of-scope`,
`accepted-risk` — and each of the three terminal dispositions requires a
reason. A dispositioned requirement leaves the numerator and the denominator
both, so the checker reports `covered/in-scope` with the defined and
dispositioned counts beside it: the verdict then distinguishes a plan that
builds twelve requirements from one that builds three and defers nine.

This is a gain in signal, not a fix for a broken rule. Discharging a deferral
by citing its ID in the scope boundaries stays valid and the checker still
accepts it; a plan with no disposition table keeps the exact prior behaviour.
Write the table anyway whenever the plan defers anything, and do not
disposition a requirement to make a NOT READY verdict go away — a terminal
disposition is a scope decision the user owns, so raise it as one.

**Gate checklist for a changed spec or plan.** Before accepting any change:

- [ ] Every story has acceptance criteria.
- [ ] References BR-* and names the new ones — a change that introduces
  behavior introduces the IDs for it; existing IDs are cited, new ones are
  declared in the inventory in the same change.
- [ ] The Traceability table has a row for every story and maps every
  requirement.

## Plan Integrity Checks

Audit these in the same pass and record findings in the matrix's Patch / Risk column:

* Every plan section or step cites the requirement IDs it serves, inline where the work happens. A section that cites none is a proposal, not scope: either cite the requirement it serves, or move it under scope boundaries marked `(proposed)` with the reason it was added, for the user to accept or cut. Nothing is silently present -- the checker computes a set difference over cited IDs, so a section no requirement asked for is invisible to it and reaches READY untouched. This one is judgement, not machine-checked.
* References resolve: anything a step depends on is defined earlier in the plan or in the recorded existing scaffold, never assumed.
* Producers come before consumers in the plan's ordering.
* Everything the plan introduces is reachable from a user workflow; no orphaned deliverables.
* Deferred or out-of-scope requirements are carried in the `## Requirement Dispositions` table with a reason, or failing that cited by ID in the scope boundaries or accepted-risk section with their disposition; nothing is silently absent.
* No generic bucket sections ("Misc", "Utilities", "Other").

Then:

1. Run `python3 scripts/check_requirement_coverage.py <inventory-or-prd> <plan-under-review> --design <design-file>` (on Windows PowerShell, `python` — `python3` is not a command there) and copy its full output verbatim into the review artifact. `--design` adds the contract-reachability note above; add `--inventory <screen-inventory.json>` so the note can read the screen's affordances too. The coverage numbers, the uncovered and dangling lists, and the `coverage verdict:` line are computed, never hand-authored; do not restate them as your own estimate. The checker proves every ID is cited; the Evidence column stays the judgement check that each citation is honest.
2. List the **top gaps** (uncovered IDs, Partial rows, or unclear assumptions), prioritized by impact.
3. Produce a **patched version of the plan** that closes those gaps with **minimal changes**, preserving the original structure where possible (add/adjust sections rather than rewriting everything). The patched plan cites each requirement ID inline where it is addressed. The patched version must be the full plan text after edits. Do not write a summary-only patched artifact.

**The patched plan preserves every original heading verbatim, the H1 title included.** The handoff scanner's structural non-regression check compares heading text between the original plan and the patched one, level-insensitively, and it reads the document title as a heading like any other -- so renaming `# Booking Plan` to `# Booking Plan (patched)` registers as a dropped section and fails the scan. That is a correct catch: a renamed title is indistinguishable, to a text comparison, from a section that vanished. Record what the patch changed by appending a `## Change Summary` section rather than renaming anything. The patched plan is identified by its filename (`{plan-stem}-patched.md`), never by its title. Adding headings is always free; the check never reports additions.

Before writing the patched plan file, replace any generic Superpowers execution handoff. The patched plan should point to `outsystems-plan-to-mentor` and `outsystems-mentor-implementation`.

Do not copy scanner-forbidden token strings into generated or patched plan content, even inside negative wording. Refer to them only as generic execution skills.

Repeat against the patched plan until convergence or max 3 passes:

* pass 1: original plan -> `coverage-review.md` and patched plan.
* pass 2: patched plan -> `coverage-review-v2.md`; patch again if any row is Partial, Missing, unsupported by evidence, or has invalid ODC/Mentor implementation detail, or if the checker reports NOT READY.
* pass 3, only if needed: patched plan -> `coverage-review-final.md`; document any remaining accepted risk.

The scanner and Mentor invocation must use the same full patched plan file.

Convergence requires:

* `scripts/check_requirement_coverage.py` reports `coverage verdict: READY` on the patched plan -- no uncovered IDs, no dangling references, and no disposition-table failures. Uncovered is computed over the in-scope set when the plan carries a Requirement Dispositions table. An accepted-risk requirement converges by carrying a reasoned row in the Requirement Dispositions table, or by being cited in the plan's scope boundaries with its disposition -- not by being waived from the checker. Report the in-scope and dispositioned counts as the checker prints them; a READY verdict over three in-scope requirements is not a claim about the other nine.
* `scripts/check_outcome_coverage.py` reports `outcome verdict: READY` -- every declared refusal outcome is reached by a verification row, and, when the design carries the success-rows marker, every action's success path too. An outcome that is genuinely untestable converges by being cited in scope boundaries with its reason, not by being dropped from the design's declared results.
* no Missing rows.
* no Partial except explicitly accepted platform/runtime uncertainty.
* no Infeasible or Unverified platform feasibility rows.
* top gaps either closed in the patched plan or documented as accepted runtime risk.
* the final matrix and the checker's verdict output are ready to show in the assistant response before delivery mode.
```
