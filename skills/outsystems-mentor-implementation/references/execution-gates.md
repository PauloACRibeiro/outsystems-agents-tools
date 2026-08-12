---
name: omi-execution-gates
description: The three runtime gates that cover what build-time signals cannot see — execute an action before building on it, render a screen as a principal who can reach it, and never close a fix on the model's report. Use during any live build or fix iteration.
---

# Execution gates

> **Why these exist.** Every other gate in this skill — digest, enumeration,
> assertion recompute — is a **build-time** signal. Each describes whether the
> right *shapes* exist. None can observe whether the logic inside those shapes
> does its job. In the second live run an action passed all of them and could
> never create a record.
>
> Derived by execution from a live two-day build-and-grade run, 2026-08-10/11,
> in which an app was built end to end and then partly broken by a fix accepted
> on the model's report. Each gate below carries the specific observation that
> produced it.

## 1. Execution gate — per server action, before anything is built on it

**After an action's approved publish, execute it** against the verification rows
the plan declares for it, **before building any screen that calls it.**

**What this catches.** `Enrol` passed blueprint validation, coverage review
38/38, cross-blueprint check, plan agreement, enumeration with the exact
specified signature, `change_applied: true`, `internal_retry_count: 1`, and a
clean publish. It could never create an enrolment **for any course**: the create
step held an empty record literal `{}` and its outgoing connector pointed at the
`AlreadyEnrolled` assign instead of `Success`. A codegen defect, not prompt
ambiguity — all four `If` conditions were verbatim correct.

**The load-bearing point is ordering, not cleverness.** One happy-path call at
the moment the action was built would have found it, because the empty literal
breaks *every* path including the successful one. Instead it was found after
five screens had been built on a dead action. The tests existed and were
correct; they ran at the end.

**Refusal-branch coverage is enforced separately and mechanically** by
`check_outcome_coverage.py` in `outsystems-plan-to-mentor`: every non-success
result the design declares must have a verification row that reaches it. That
checker proves the tests were *written*; this gate is what makes them *run in
time*.

## 2. Render gate — per screen

**A screen is not verified until it has been rendered by a principal who can
reach it.** Role-gated screens are verified signed in, or they are not verified.
**Reading the deployed artifact is not a substitute.**

**What this catches.** `CourseEdit`'s date fields were verified from the
compiled JS chunk — a deliberate choice, since the screen is admin-gated and
could not be loaded anonymously. Every structural claim was true: real
`DatePicker` pattern blocks, correct bindings, `TimeFormat` present, zero
`type="date"`. On an **existing** record the fields rendered **blank and
un-typeable**, and the calendar opened on today rather than the record's own
date — so an administrator checking a date could overwrite a value never shown
to them. The defect lived in what the control did with existing data *on load*,
which no artifact read can reach.

**Where displayed values derive from a fetch, render more than once** — or
remove the timing dependence by construction, which is the better fix. A single
green observation cannot distinguish *correct* from *correct this time*: one
revision was verified by loading it in a browser and looked right, while
carrying the same race that made the next revision visibly wrong. It was lucky,
not correct.

**Sizing note.** For the app this came from, the authenticated surface was
**half the application**, and it is where the defects were. A verification pass
that stops at the anonymous surface grades the easy half.

### The tooling cannot satisfy this gate for you

`outsystems-runtime-ui-audit` **does not log in** — auth-gated runtimes are
explicitly out of its scope, and it is right to stop rather than score a login
page as if it were the app. The colleague guide says the same: the URL it audits
must work without login.

**So for a role-gated screen there is no automated route to this gate**, and
saying "the audit passed" does not discharge it. Two consequences, both learned
the hard way:

- **A clean audit of the anonymous surface is not evidence about the gated one.**
  It is evidence about a different half of the app.
- **An unauthenticated harness is not a substitute either.** A role-gated server
  action invoked without a user context answers *"Not authorised."* — an HTTP
  200 that a sweep can easily record as a correct refusal. Measured 2026-08-12.

**What discharges the gate for a gated screen** is a human or an authenticated
browser session opening the screen **as a principal holding the role**, on an
**existing** record as well as a new one, and reporting what rendered. Record it
as a manual verification row with the principal named. If nobody does that, the
screen is **unverified** — write that word rather than a tier.

## 3. Remedy gate — per fix

**A fix is not closed on the model's report that it was applied.** Hold a remedy
to the same standard of evidence as its diagnosis: if you can say how you
measured the cause, you must be able to say how you measured the cure.
`change_applied: true` with zero retries does not answer the second question.

**What this catches.** Twice in one afternoon the diagnosis was established
empirically — measured in the DOM, reproduced across three screens — and the
remedy was accepted on the model's report. The diagnosis was right both times.
The remedy was wrong both times, and once took three live screens off the air
with `OS-CLRT-60500 [View] TypeError: Cannot read properties of undefined
(reading 'render')`.

That asymmetry is the failure mode: rigour on the cause, credulity on the cure.

### Check recovery before you need it

**`deploy_rollback` requires prior Deploy operations.** An app changed only
through `publish_start` — which publishes an AVS revision directly into the dev
environment — has none, so `deploy_list` returns zero rows and **there is
nothing to roll back to.** Structural, not transient.

Read `deploy_list` **before** treating rollback as a fallback. Where it is
empty, plan on this basis:

- The only recovery is a forward Mentor turn: a full cycle, the same risk as any
  other change, and observably slower than the change it undoes.
- **"Cancel and retry" is not a recovery plan either.** `mentor_cancel` has been
  observed stuck in `cancelling` past the documented SIGKILL window, and
  `max_turn_time` does not enforce termination — runs have sailed past their
  bounds.
- Two wedge signatures exist and neither is visible from `status` alone: a run
  emitting *stalled* events (identical event ids), and one emitting *no* events
  at all.

**So a published change may be irreversible within the session that made it** —
which is precisely why rendering before publishing is the primary protection
here rather than a refinement of it.

## 3b. The digest gate is per publish, never across a session

**A `modelDigest` can return to a value it held before.** Measured on
TrainingHub: three apply-then-revert pairs — revisions **15 = 17, 18 = 20,
30 = 32** — so **32 distinct digests across 35 revisions**. A digest is a
content hash, not a unique revision id.

**The consequence for the gate.** A before/after comparison that spans a revert
reports `DIGEST: unchanged` while **two deploys actually landed**. Baseline
therefore belongs **immediately before each approved publish**, not once per
iteration — which is how the gate was originally written, and was wrong for
exactly this case.

**And the digest cannot carry the gate alone.** Revisions 3, 6 and 8 each
*minted a revision with a distinct digest after a failed deployment*: rev 3 took
seven attempts, revs 6 and 8 three each, every attempt terminal-with-error. The
digest moved every time. So:

| Signal | Answers |
|---|---|
| `modelDigest` | **the model changed** |
| terminal deploy state | **the deployment succeeded** |

Neither substitutes for the other, and a publish is only verified when both
agree.

**Match the terminal state exactly.** `env_deploy_history` reports **two**
terminal states — `Finished` and `FinishedWithError` — and a prefix or substring
test matches both. Measured on one environment page: **76 `Finished`, 24
`FinishedWithError`**; on TrainingHub, `== "Finished"` returns **30 rows** while
`startsWith("Finished")` returns **43**. A loose match **swallows 13 failed
deployments and reports them as landed.** Failures return in seconds, successes
take ~30s, so speed is a hint but not a test.

> **Provenance.** Measured 2026-08-11 by an independent verification session
> against the run's app and a second control app, after it asked whether our
> digest gate had this hazard. It did.

## 4. Mid-run loop triage — one `details: true` poll at 5–6 minutes

**A stuck turn is invisible to the normal polling cadence until it is too late.**
`internal_retry_count` — the field that says definitively that a turn is looping
— appears **only in the terminal `result`/`error` object. By the time a
status-only poll can see it, the turn has finished and its whole budget is
spent.**

So at the **5–6 minute mark**, do **one** `details: true` poll with a small
`events_limit` (~10–15) and read the `tool_begin`/`tool_end` payloads:

| Healthy | Looping |
|---|---|
| New Aggregates, nodes and assigns being built one after another — including across a legitimate "delete and rebuild this action" self-correction | The **same action name** with a **near-identical broken expression** recurring across consecutive `tool_begin` events |

**This is a spot-check, not a polling mode.** One poll, then straight back to
status-only. Making it habitual is exactly the token cost the polling-behaviour
discipline exists to avoid.

**A timed-out turn discards its work.** The platform's own error text says
*"Do not create a new app or discard work already applied."* **That is
aspirational, not a guarantee.** Mentor edits an in-memory OML working copy that
is checkpointed only on `status: succeeded`; a hard timeout kills the turn before
any checkpoint, so a resumed session reloads the last good state. On any
`"Agent turn timed out"` result, **ask Mentor to report what currently exists in
the model** rather than building on the assumption partial work survived.

**Turn size is the lever, not the timeout value.** Raising `max_turn_time` does
not reliably help — a scoped-down turn still hangs if it contains a single
operation Mentor can loop on. Split ambitious work into single-concern turns
sized to finish well inside 15–20 minutes, passing the session forward and
telling Mentor explicitly what already exists and not to recreate it.

> **Provenance.** This section is field evidence from another team's ODC build
> work (two production-shaped builds, 2026-08-07 → 08-10).
> **It was not measured by us.** Adopted because it is a read-only diagnostic
> whose only cost is one extra poll. Our own corroboration is negative and partial: two Mentor
> sessions wedged on one objective on 2026-08-11, one repeating identical event
> ids for 15 minutes and one emitting nothing for 20, and in both cases we could
> see *that* they were stuck and nothing about *why*.
