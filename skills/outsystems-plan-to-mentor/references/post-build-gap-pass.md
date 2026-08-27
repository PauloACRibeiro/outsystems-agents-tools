# Post-Build Gap Pass

A pattern note, not a stage this skill runs. The coverage gate in
`references/coverage-review-prompt.md` audits the *plan* against the spec and
converges before Mentor conversion. Nothing after it audits the *built app*
against the same spec. This note records the shape a post-build pass takes and
the two classification rules that make it worth running, so a run that wants
one has something to follow. Do not build it as tooling here — there is no
script, no artifact contract, and no checker behind this note.

## Why the gap is real for this loop

Every signal the loop already collects — validation, requirement coverage,
element enumeration, `change_applied`, retry count, publish status — describes
whether the right *shapes* exist. The coverage prompt says as much for server
action outcomes. The same blind spot covers the whole build, and one of our own
patterns walks straight into it: `outsystems-mentor-implementation` deliberately
prefers a publishable stub over a complete-but-broken implementation
(`odc-mentor-hardening.md`, `## Stub-First`). So a plan can converge READY, a
build can publish clean, and a requirement can still be represented by an empty
flow that nothing downstream contradicts.

## The staging

Requirement → gap → patch → validate → report. Each stage reads the previous
stage's output and the spec, never a summary of them:

1. **Requirement** — the inventory the coverage gate already built. Reuse those
   IDs; do not renumber for the post-build pass.
2. **Gap** — read the built app and mark each ID Covered / Partial / Missing
   against what is actually there.
3. **Patch** — the work items that close the Partial and Missing rows.
4. **Validate** — re-read the app after the patch turns, against the same
   inventory. A patch reported as applied is not a patch observed as present.
5. **Report** — one consolidated view across every pass the run took.

**Read the app through `context_*` and `app_refs`.** The workspace rule is that
OML stays server-side; a post-build pass inspects the live model and never
serializes an `.oml` to diff it. That constrains what the pass can see — screen
context carries no widget detail — so a gap the tenant surface cannot resolve is
recorded as unresolved, not guessed at.

## Rule 1 — classify on the logic present, not on the annotation

An element counts as unimplemented only when its logic holds nothing beyond the
entry node, the exit node, and a reminder or placeholder comment. State it as an
"if and only if", because it fails in both directions:

- A TODO comment sitting alongside real logic does **not** make the element a
  stub. Classifying on the comment reports work as missing that was done, and
  the patch stage then rewrites it.
- An element the plan cites, with a name that matches, and no logic in it, **is**
  a gap. Citation is not implementation.

Whatever produced the classification — a model reading the app, or a person —
this rule is what the reading gets audited against.

## Rule 2 — split build status before consolidating, on its own axis

A run that takes more than one build pass needs a per-item final status, and the
only honest one is the status from the item's *latest* pass. That requires
knowing which statuses end an item and which invite a retry:

- **Settled** — the item is resolved for this run and is not carried forward,
  whether it succeeded or failed.
- **Carried forward** — the item is partial, a placeholder, or applied with a
  warning, and stays open to a later pass.

Without the split, a consolidated report counts a partial from pass 1 the same
way it counts a success from pass 3, and the run's summary line reads better
than the run went.

**This is a second axis, not a second spelling of the disposition vocabulary.**
Keep the two apart:

- The coverage gate's `## Requirement Dispositions` vocabulary — `built`,
  `deferred`, `out-of-scope`, `accepted-risk` — is a **scope** decision the user
  owns, and `check_requirement_coverage.py` treats the latter three as
  **terminal**: a dispositioned requirement leaves the numerator and the
  denominator both. A post-build pass reads that table to learn what it should
  *not* expect to find in the app, and never re-decides it.
- Settled versus carried forward is a **build-status** reading over the in-scope
  items only, and it is the pass's own judgement, not the user's.

So do not describe a build item as `deferred`: on the scope axis that word is
terminal and means the user cut it, while a carried-forward item is one the run
still intends to finish. Borrowing the word would invert its meaning against a
rule the checker enforces.

## Evidence rule

A gap row names the element it read and the reading that produced the verdict,
and carries the requirement text verbatim. A row that states a verdict without
naming what was read is a judgement, and the pass records it as one.

## Provenance

Derived from the staging of an internal OutSystems gap-analysis pipeline
(read 2026-08-26; see
`docs/adoption/legacy-requirement-gaps-adoption.md`). Only the staging and the
two classification rules were taken. That pipeline patches a serialized OML on
disk, which this loop declines; none of its platform assertions were adopted.
