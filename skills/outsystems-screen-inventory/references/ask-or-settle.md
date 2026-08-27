# Ask or settle — the one criterion

Every gate in this skill that stops for a human — hard gate 2's candidate
dispositions, hard gate 3's chrome decision, hard gate 5's fusion approval —
used to carry its own idea of what was worth raising, each written for its own
situation. Per-site rules do not disagree loudly. They drift, and the artifact
ends up asking about whatever the last gate happened to emphasise. This file is
the whole rule; the gates point at it and do not restate it.

**Scope.** This is the criterion for the decisions *this artifact* takes.
`outsystems-plan-to-mentor` and `outsystems-mentor-implementation` keep their
own instructions: they ship in different manifests, and a pointer wave across
skills leaves a dangling link in every pack that ships one skill and not the
other. One skill, one statement — not one statement everywhere.

## Before the test: decompose

A bundled question cannot be answered and cannot be recorded. "Is the booking
area right?" holds a candidate disposition, a fusion and a menu decision at
once; whatever comes back settles none of them cleanly, and it will not fit
`open_decisions[]`, where one entry is one decision with 2–4 options. Split
until each piece is a single decision whose alternatives you can list.

Run the rest of this file on each piece separately. A compound question that
survives as a compound question has skipped the criterion, not passed it.

## The convergence test

For each decomposed piece, ask:

> **Would competent engineers at different organizations, given this same
> source, converge on the same answer?**

If yes, **settle it** and record why where this artifact already records
reasoning — the candidate's `rationale`, the screen's `behavior`, the binding's
`behavior_notes`. Convergence means the answer is in the source and you have not
read it out yet; asking is not diligence there, it is handing back work.

If no, the piece is a real question. It still has to clear the conjunction
below before it earns a place, because "not obvious" is a much larger set than
"worth the one gate you get".

## The specific-values trap

The test says *converge on the same value*, which makes it easy to run at the
wrong granularity — and run at the wrong granularity it fails on almost
everything, which turns the criterion into a machine that asks about all of it.
That failure looks like rigour and is indistinguishable in its effects from
having no criterion at all.

Run it **on the decision, not on the wording** that realises the decision.
Competent engineers converge on "this screen lists bookings and filters them"
and diverge on whether the filter button reads "Search" or "Apply". The first is
a decision this artifact takes; the second is copy, and copy is settled, not
asked.

The trap has a second face at the point of recording. Even a piece that
genuinely fails the test never becomes a request for a value: options carry
consequences, so the entry asks *which of these outcomes*, never *what should
this be*. A user handed a blank is being asked to do the work the skill exists
to do, and the answer that comes back is a guess wearing an approval.

## The three-part conjunction

A piece is worth raising only when **all three legs hold**. Any one failing
sends it back to be settled.

### Leg 1 — Not derivable

The source does not answer it and re-reading will not change that. Most first
questions fail here: the answer was in the requirements doc, one section away
from where the candidate was harvested. Re-read before you raise.

### Leg 2 — Consequence-bearing

Different answers change *this file*, and you can name the change: a screen that
appears or disappears, a menu entry gained or lost, an edge that carries a
payload or does not. If you cannot name what would differ, there is nothing to
decide — and there is nothing to write, because every option needs a
`consequence`. This is the leg that catches anxiety phrased as a question.

### Leg 3 — In scope

The decision is one of the five things this artifact decides:
`candidate-disposition`, `screen-fusion`, `chrome`, `navigation`, `binding`.
A block choice or a visual question belongs to `outsystems-ui-design`; an
attribute shape or a new action's name belongs to the capability plan. Raising
it here does not just waste the gate — it creates a second declaration site that
neither of them reads, so the answer is recorded in the one place it cannot be
acted on.

## What survives

A piece that clears all three legs goes into `open_decisions[]` — typed, with
its category and its 2–4 consequence-bearing options — whether the human is
present or not. Present, it is what hard gate 5 puts in front of them. Absent,
it is the deferral the autonomous-run disclosure demands (trial finding G-03),
and it marks the inventory PROPOSED, NOT APPROVED until someone takes it.

What it never becomes is a chat line or a guess. The criterion decides *whether*
a question is real; the slot decides *where* a real one lives. Neither is a
substitute for the other.
