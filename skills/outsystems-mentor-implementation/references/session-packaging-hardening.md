# Session Packaging Hardening

> ODC error codes: see `../../shared/reference/odc-error-registry.md` for the canonical index of every code named below.

How to package Mentor Executable Sessions so that execution survives the
failure modes observed in supervised paste runs: duplicated submissions,
silent derived-value slips, unwarned naming traps, oversized blocks, and
capability-unverified model connections. Applies to every mode that emits
Mentor sessions, and is required by the plan-to-mentor Output Contract.

## Model Capability Preflight

Entity `Public` flags are not the only referenceability check. Before
packaging any design that depends on structured output, action calling, or
a context-size assumption, verify the **actual model id** configured behind
each AI connection against current provider documentation — the connection
name proves nothing about capability. Read the connection's **usage quota**
in the same pass: a daily token limit smaller than one request fails the
next test run and masquerades as the previous fix not working.

Session-observed (single tenant; reverify on the target): a connection
whose model lacked `response_format: json_schema` support compiled and
published cleanly, then failed on the first agent call with
`OS-BERT-62000` / BadRequest naming `response_format`; correcting the
connection's model id and quota took effect without republishing the app.
These facts stay session-observed until reverified; package the capability
check as a Manual Setup Gate row next to the entity visibility checks.

## Reconcile Phrasing

Write every session as a reconcile, never a bare create:

- "Ensure Server Action `ResolvePerformer` exists with the following shape;
  if it already exists, update it to match exactly."
- Not: "Create Server Action `ResolvePerformer` with…" — a duplicated
  submission of a creating prompt can produce duplicate elements; reconcile
  wording reduces that damage if a duplicate ever happens.

Reconcile phrasing is packaging risk reduction, not an execution guarantee.
It does not authorize resubmission or unattended retries, and it does not
waive post-abort inspection of the app state. The execution protocol's
guards stand unchanged: a prompt is never resubmitted merely because the
panel looks stuck, and interrupted state is undefined until inspected.

## Traps

Each session carries a `Traps` list naming the mistakes Mentor is most
likely to make in that session's scope, harvested from the scaffold
inventory and the source spec while the package is generated:

- **Source-spelling preservation** — when the data model carries misspelled
  attribute names (`Nacionality`, `MissingBankInfomation`), say explicitly
  that the source spelling must be preserved and mapped, not corrected.
- **Similarly-named element disambiguation** — when two reachable elements
  share a name shape (`TRACK_INVALID_REASON` vs an unrelated
  `INVALID_REASON`), name the correct one and the wrong one.
- **Join-type assertions** — when a join must stay outer (or a filter must
  not collapse it to inner), state the join type and the filter placement
  as an explicit acceptance line.
- **Function-semantics traps** — when a filter or assignment relies on a
  built-in function's return convention (zero-based positions, `-1`
  not-found sentinels), state the exact comparison in the prompt:
  containment is `Index(...) >= 0`, because ODC `Index` is zero-based and
  returns `-1` when absent, so `> 0` silently drops position-0 matches.
  Expressions ported from an existing app carry this trap unflagged —
  ported code gets the same grounding as new code.
- **Product-vocabulary trap** — for an ODC target, name the forbidden widget
  and its replacement explicitly; naming only the widget you want is not
  enough. Verified O11-only name: `ListRecords` — use `List`, or
  `TableRecords` for a tabular layout. Mentor substitutes silently, with no
  validation error and no disclosure, so prohibition by name is the only
  guard. Measured on the first live colleague sprint-loop run (2026-08-09):
  re-running one screen session at full scope with the wrong name forbidden
  took `internal_retry_count` from 12 to 0, correctly authored, zero errors.
  Forbid only names verified O11-only against the generated built-in-widget
  reference. A name appearing in OutSystems 11 documentation is not evidence
  it is wrong for ODC — most widgets exist in both products, and
  TableRecords, ListItem and ListItemAction are ODC built-ins. Forbidding one
  of those would ban a widget that is valid on the target.

Warned traps hold; unwarned ones become defects. Trap generation is part of
packaging, not left to execution-time diligence.

## Session Sizing

- One action, plus its verdict/rollup logic, per session.
- Split search logic from verdict assembly into separate sessions when both
  are substantial.
- Flag any session whose scope predicts a long Mentor run (multiple action
  calls, orchestration plus assembly in one block). Long runs are where
  duplicate submissions and lost-focus mistakes happen; prefer two short
  sessions over one long one.

## Expected Element Delta

Each session names its expected element delta as a list, not prose:

```text
Expected element delta:
- create: ResolvePerformer (Server Action)
- modify: AgentFlow (add ExtractIntent call)
```

The execution loop verifies this list against the app's element tree — the
element tree is the authority. Treat Mentor's change summary as reporting
what it was asked to do, not everything it did: in a session-observed run
(single tenant), a reference session added entities by
FK dependency closure that never appeared in the summary. Neither the omission nor the
closure is documented categorical platform behavior; the checking rule that
follows from it is unconditional anyway — diff the tree, expect possible
unrequested dependency-closure extras, and record any found, because they
widen the consumed producer surface and the app's blast radius if a
producer changes. Mentor's summary is still worth reading line by line —
wrong-source logic slips sit there in plain sight — but tree state decides.

Declare an expected warning delta alongside the element delta when a
session wires references: TrueChange unused-element warnings clearing on
exactly the elements a new structure or action references is a cheap
corroborating signal. A cleared warning shows only that the element is
no longer considered unused — it does not prove the intended consumer
uses the intended producer — so it never replaces direct
tree and logic inspection as the authority. A lookalike invented type
leaves the original unused and pushes the count up (session-observed; the
warning semantics come from the TrueChange unused-element warning
reference).

The delta is the packaging-time expectation, not runtime truth. After any
abort or interrupted run, inspect the app and reclassify each pending
session's entries as create, modify, or already-conformant before an
authorized retry — a static `create:` entry is wrong when the interrupted
run already created the element.

## Build-Log Table Template

The package includes a pre-formatted build-log table for the executor to
fill, one row per session: emit the table skeleton in
[prompt-templates/build-log-table.md](prompt-templates/build-log-table.md)
verbatim (header row `| Session | Time | Outcome | Notes |`; its sample
`S1` row carries the full outcome vocabulary), one row per session.

Outcome vocabulary is fixed. Only `first-try`, `re-prompted`, and
`hand-fixed` count toward the run tally and the three-consecutive-hand-fixed
abandon criterion; `blocked`, `aborted`, `skipped`, and `already-conformant`
record sessions that did not execute to completion (or needed no change) so
the tally stays truthful.

## Derived-Value Bindings

Every derived local names its exact source in the pseudocode:

- `MatchCount` = length of `Matches` — not `GetPerformerCastings.Count`.
- A count bound to a different aggregate than the list it describes
  compiles cleanly, passes TrueChange, and is wrong only on the branch
  where the two diverge. The binding line in the prompt is what lets the
  executor verify Mentor's summary against intent.

## Bounded Literals

Declare Setting defaults with the `Default Value:` label using one of two
forms, and no other:

- **Inline** — the remainder of the label's line, surrounding whitespace
  trimmed. Wrap the value in a backtick code span to preserve exact
  characters, including boundary whitespace.
- **Fenced** — an empty label whose next non-blank line opens a fence
  (backtick or tilde, three or more delimiters); the literal is the fence
  body verbatim. An empty label followed by anything else, or a fence that
  never closes, is a malformed declaration and fails the lint.

Labels inside fenced blocks are content, never declarations. ODC caps a
Setting default at 2,000 characters; `response_contract_lint.py` measures
every declared default and fails the package above the cap, so the overflow
is caught at packaging time instead of at paste time.

## Runtime Smoke Ladder

Compiling clean proves shape, not behavior. Package the runtime checks in
`Verification Pseudocode` as an ordered ladder, cheapest rung first:

1. **Refusal probe** — one question whose correct answer is a refusal
   (an entity that does not exist). Zero data dependencies, yet it
   exercises the full pipeline end to end and the no-invention discipline
   under the exact conditions where a model is most tempted to improvise.
2. **Single known-entity probe** — one real name or identifier. Cheap, and
   it runs the resolution path against real data before curated cases
   exist; a single probe of this kind has surfaced multiple defects.
3. **Curated known-outcome cases** — one per verdict class; the only rung
   that proves the queries return correct data.

Test-surface caveat: a generated test app may expose only part of the
structured response (a single mapped field). Absence in that UI is
not absence in the response — verify the full structure through
logs or the debugger before reporting a field as missing or broken.
