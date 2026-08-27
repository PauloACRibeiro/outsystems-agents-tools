# The scenario plan — schema and categories

`generate` will compose a prompt for N scenarios without being told which N.
That is the right default for a first pass and the wrong one for a suite anybody
depends on: the scenarios that get written are the ones that were easy to think
of, and nothing records the ones that were not.

A scenario plan is the artefact that decides them in advance. Pass it with
`--plan`, and the composed Mentor prompt enumerates each scenario by identifier,
title and assertions instead of asking for a count.

Adapted from the priority-bucket test plans in `OutSystems/OML2Test` and the
scenario taxonomy in `OutSystems/solutions-agents-eval`; the mining record is
`docs/adoption/solutions-agents-eval-disposition.md` (F9, F12, F13).

## Shape

JSON, and only JSON. Where a plan exists in two renderings — a table for people
and a structure for tools — they drift, and the drift is silent. Upstream's own
plan pair had already drifted at the moment it was read: its narrative smoke
list named a `niceToHave` validation test where the machine-readable list named
the P0 anonymous-access sweep. Render prose from the plan if you want prose; do
not maintain a second copy of it.

```json
{
  "app": "RoomBooking",
  "scenarios": {
    "mustHave": [
      {
        "id": "BDD-001",
        "title": "Booking a free slot succeeds",
        "category": "happy-path",
        "priority": "P0",
        "asserts": [
          "CreateBooking returns a non-zero BookingId",
          "The Booking row exists with the requested slot"
        ],
        "requirements": ["REQ-BOOK-CREATE"],
        "gap": false
      }
    ],
    "niceToHave": [],
    "optional": []
  }
}
```

| Field | Required | Meaning |
|---|---|---|
| `id` | yes | stable identifier, unique across all three buckets |
| `title` | yes | one line; becomes the scenario description Mentor writes |
| `category` | yes | one of the six below |
| `priority` | yes | `P0`–`P3`; orders scenarios **within** a bucket |
| `asserts` | yes, non-empty | what the Then step must establish, in behaviour terms |
| `requirements` | yes, may be empty | requirement IDs this scenario covers |
| `gap` | yes | `true` when the behaviour does not exist in the app yet |

The bucket and the priority are two different facts. **The bucket is the
delivery decision** — what ships in this suite. **The priority orders the work
inside it.** Neither is reconstructible from the other, which is why a plan that
carries only one of them is not a plan.

`requirements` is mandatory and may be empty, and empty is a signal rather than
an omission: a scenario with no requirement is there for defensive reasons — a
CRUD smoke, an audit confirmation — not to satisfy anything anyone asked for.
A reviewer who cannot tell those apart cannot tell an over-tested suite from a
well-covered one.

## The six categories

The upstream taxonomy has eight, two of which describe attacks on a language
model — prompt injection, jailbreaks, authority resistance. A BDD suite calls
Service Actions; there is no prompt to inject. Those two collapse into the
model-side behaviours that survive the translation:

| Category | What belongs here |
|---|---|
| `happy-path` | the flow works for the role it is meant for |
| `validation` | bad input is rejected, and rejected the way the spec says |
| `boundary` | the exact threshold — at the limit, one under, one over |
| `role-forbidden` | an action the caller's role must not be able to perform |
| `volume` | many rows, long lists, repeated calls |
| `regression` | added after a specific defect, and named for it |

**A category with no scenario is a coverage gap, and the gap is reported from
this list, not from what the plan happens to contain.** That ordering matters.
Upstream's coverage tool computes gaps only across categories that already have
at least one test, so the one category nobody wrote anything for produces no gap
line at all — the instrument is blind to the largest gap it could report. Gap
detection over a declared set cannot fail that way.

## Requirement coverage and gaps

When the plan is derived from a requirements document:

- **One scenario per requirement, minimum.**
- **The bucket follows the requirement's priority**, not what is convenient to
  test: must/P0 → `mustHave`, should/P1 → `niceToHave`, could/P2/unstated →
  `optional`. A scenario covering several requirements takes the highest.
- **A requirement with nothing implementing it still gets its scenario**, marked
  `gap: true`.

### A gap scenario asserts and fails. It never skips.

This is the rule the whole `gap` field exists for. A scenario for behaviour that
does not exist yet must assert the intended behaviour and **fail** until someone
builds it. Writing it as a skip, or leaving it out and noting it elsewhere, puts
the suite back in the state this skill refuses to call a pass: the runner reports
`IsSuccess: true` for an all-skipped suite, and a stage that reports success
because it measured nothing launders absence into evidence. A failing gap
scenario is a work item. A skipped one is a lie with a green tick.

Failing scenarios from a plan with gaps therefore mean exit 1 by design, and
`--baseline` is how you keep the known ones from drowning the new ones.

## Reverse traceability

The plan should also account for the other direction: exposed Service Actions
with **no** requirement covering them. Those belong in `optional` with an empty
`requirements` array, as audit confirmations. Enumerating them needs the app's
own inventory — `context_actions`, or `app_refs` — which this skill does not
read; do it while writing the plan, not while composing the prompt.

## Validation

`generate --plan` refuses a plan that is malformed rather than composing a
prompt from a partial reading of it: an unknown bucket or category, a missing or
empty `asserts`, a duplicate `id`, a bad `priority`, an absent or non-list
`requirements`, an absent or non-boolean `gap`, or **a plan with no scenarios at
all**. The last one is deliberate and matches `verify`'s treatment of an empty
expectation file: having nothing to check against must never read as verified.

The two field-presence refusals earn their place. `requirements: []` and an
absent `requirements` read identically to a person and mean opposite things —
one is a recorded decision that nothing asked for this scenario, the other is
someone who did not get to it. And an absent `gap` defaults the scenario to
already-built, which is exactly how a gap scenario stops being one. Both were
declared mandatory here before the validator enforced either; Codex caught the
gap on `AH-2026-08-26-005`. A rule written into a reference file is not a rule
until something refuses to proceed without it.
