---
name: omi-execution-gates
description: The three runtime gates that cover what build-time signals cannot see — execute an action before building on it, render a screen as a principal who can reach it, and never close a fix on the model's report. Use during any live build or fix iteration.
---

# Execution gates

> Mentor operation cadence: see `../../shared/reference/mentor-operations-registry.md` for the canonical index.

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

**So for a role-gated screen the audit is not a route to this gate**, and
saying "the audit passed" does not discharge it. Two consequences, both learned
the hard way:

- **A clean audit of the anonymous surface is not evidence about the gated one.**
  It is evidence about a different half of the app.
- **An unauthenticated harness is not a substitute either.** A role-gated server
  action invoked without a user context answers *"Not authorised."* — an HTTP
  200 that a sweep can easily record as a correct refusal. Measured 2026-08-12.

**What discharges the gate for a gated screen** is a human or an authenticated
browser session opening the screen **as a principal holding the role**, on an
**existing** record as well as a new one, and reporting what rendered. The
automated route is `outsystems-render-gate`: the operator bootstraps a test
principal's session once, the run derives a check spec per screen, and the gate
emits verification rows (naming that principal, with screenshots) for exactly
this discharge — where it cannot run, record it as a manual verification row
with the principal named instead. If nobody does either, the screen is
**unverified** — write that word rather than a tier.

**Only a clean run discharges it.** A run that returns **exit 4 does not
discharge this gate**: exit 4 means `unasserted` rows — nothing failed, but
nothing checked those rows either, and a gap is not a pass. Each such row needs
the recorded **human screenshot verdict** written as a manual verification row
naming the principal, per that skill's Result semantics, before the phase
proceeds. A completed run is not by itself the evidence; its exit code is.

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

**Three publish mechanics, recorded here because the runbook alone
demonstrably fails to carry them:**

- **`publish_start` rejects a `message` over 500 characters** — a hard
  validation error: the call never fires. Keep the drafted message under ~480
  for headroom and trim to load-bearing nouns (entity/screen/action names plus
  the one-line why) rather than restating Mentor's summary. Rediscovered the
  hard way twice on 2026-08-11; until then the limit lived only in the runbook.
- **The `operation_id` a gateway `publish_start` returns is not the key the
  log tools take.** `publish_logs` and `deploy_messages` both return HTTP 404
  for it. For the per-line error trail, find the app's record in
  `env_deploy_history` and use that record's key as the `operation_key`. The
  bridge works in flight — the row is at the top of the window — but the
  history is a 100-row unpaged window (V73), so retrospectively the row may
  already be gone, and an empty result is not "never deployed".
- **Revision notes attach on publish, not on promotion.** A deployment
  operation carries no comment field of its own; the publish `message` is the
  only place a note is written, and promoting moves an existing revision, so
  the note set at publish is the one that travels to the target environment.
  When a `commit -m`-style comment is asked for on a promotion, point at the
  publish that created the revision rather than reporting it as unsupported.
  (Upstream 0.13.1, verified verbatim, rev.17 P1 re-diff 2026-08-13.)
- **`context_*` reads lag a successful publish by ~20–90s** (external field
  measurement, two builds; worst after a phase touching several screens' role
  lists at once), and `context_search` has been observed to catch up faster
  than the paginated listings. Terminal state and digest are the immediate
  signals; content enumeration is the delayed one — see the enumeration gate's
  wait rule in SKILL.md before reading a miss as a failed phase.

> **Provenance.** The `operation_id` bridge and the `context_*` lag figures
> are field evidence from the same external ODC build work as §4 — **not
> measured by us.** The 500-character limit and the window caveat are our own.

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
telling Mentor explicitly what already exists and not to recreate it. One shape
deserves pre-flight counting rather than triage: a single Server Action asked
to originate several grouped-Aggregate list outputs (the "get all the dashboard
data" shape) has crashed a turn outright on the same external evidence,
discarding all of its work — same remedy at a coarser grain, one small action
per list, decided before the turn is fired (see the hardening guide's
turn-shaping entry).

> **Provenance.** This section is field evidence from another team's ODC build
> work (two production-shaped builds, 2026-08-07 → 08-10).
> **It was not measured by us.** Adopted because it is a read-only diagnostic
> whose only cost is one extra poll. Our own corroboration is negative and partial: two Mentor
> sessions wedged on one objective on 2026-08-11, one repeating identical event
> ids for 15 minutes and one emitting nothing for 20, and in both cases we could
> see *that* they were stuck and nothing about *why*.

## 4b. Cancel calibration and token hygiene

External field evidence: an internal OutSystems project (adopted 2026-08-14); field-observed over the Mentor MCP, not in official docs.

RECONCILIATION — three existing OMI rules stay binding; this section calibrates the *voluntary* cancel decision underneath them: (1) `max_turn_time` must still be passed explicitly on every `mentor_start` (SKILL.md driving contract) — but as a *requested* ceiling, not an enforced terminal bound: §3 records runs sailing past it, so never treat the ceiling as a guarantee that the turn will terminate; (2) the §4 `details: true` poll at 5–6 minutes is diagnostic — it is never by itself a reason to cancel; (3) §3's warning that `mentor_cancel` can wedge in `cancelling` stands — cancel is a last resort, not a recovery plan.

- **A slow Mentor turn is not a wedged one.** Heavy structural turns legitimately run **8–12 minutes with silent stretches** (~7 quiet minutes is normal). Healthy small turns on this estate go terminal in 1–5 minutes — both profiles are real; judge against the turn's size.
- **Give a heavy turn ~12–14 minutes before considering `mentor_cancel`** — and cancel only if you also intend to split the work smaller. A cancel that re-runs the same oversized prompt buys nothing.
- **Cancel economics:** a cancel costs >3 minutes to settle, a cancelled turn commits **nothing** (failed/cancelled turns never advance OML), and a cancel against an already-succeeded run is a **no-op you will misread as a wedge** — re-poll the `runId` before concluding anything from a cancel.
- **Hang tell:** a `nextCursor` unchanged for ~7–10 minutes is the cursor-side signature of the §4 wedge classes (stalled event ids / no events). One `details: true` poll to confirm, then apply the cancel calibration above.
- **Copy `mentor_session_token` verbatim — never retype it.** One mistyped character returns `signature_invalid`, which reads exactly like token expiry and sends you down the wrong recovery path.
- **Cancelled-run token recovery — payload token first, last-successful as fallback, established sessions only.** On a failed or cancelled run the terminal `error` payload carries the same `mentor_session_id` plus a freshly minted `mentor_session_token`; resume an established session — one that has already reached at least one successful turn — with those credentials, per the SKILL.md driving contract (verified against upstream 0.13.x). Keep your last SUCCESSFUL token as the fallback for exactly one case: that established session's freshly minted token is rejected as `signature_invalid`. That rejection has two causes — a hand-transcribed character (see the verbatim rule above) and a payload token the server will not accept — so re-check transcription before concluding the minted token is bad. **This fallback does not apply to a bare first-turn `app_key` init failure**: that error carries no token at all, and by definition no turn in this session has ever succeeded, so no last-successful token can exist to fall back to — SKILL.md routes that case to starting fresh, not to any token fallback. The external source for this section states the last-successful rule unconditionally but names no server version; this estate's version-anchored measurement takes precedence, and the unconditional form is narrowed to the established-session `signature_invalid` case only.

## 5. Summary admissions — the confession is in the fine print, never the headline

**A turn summary's follow-up notes and caveats are required reading, not
optional colour — especially for anything RBAC-shaped.** Mentor has been
observed to self-report a real spec gap in its own summary — a role's data
scoping passing an empty region list — while the same turn reported
**zero validation errors** and a complete-sounding feature list. A skim that
stops at "zero errors" misses exactly this kind of admission.

This is "the friendly surface lies toward success" (V76) read from the other
side. The summary is **untrustworthy for success claims** — the enumeration
gate exists because one described five parts of an action that was never
created — and **load-bearing for failure admissions.** Its admissions are
findings: anything the summary flags as a scoping gap, a manual step, or a
"needs a follow-up turn" note is either fixed before the phase closes or
carried explicitly as an open item — never silently rolled forward into the
build report as if resolved.

> **Provenance.** The self-reported RBAC gap is field evidence from the same
> external ODC build work as §4 — **not measured by us.** Our own runs supply
> the success-direction half (2026-08-09 enumeration incident, V76).

### 5b. Derive the checklist from the spec, never from the builder's summary

§5 governs how to *read* a summary. This is the separate rule about where the
verification checklist **comes from**: when scoring or verifying a build, derive
the checklist by reading the spec, plan, or blueprint files directly. The
builder's own summary of what it built **must not** set the checklist — a
builder summarizing its own work is precisely the bias a fresh verification pass
exists to remove, and a checklist derived from it can only ever confirm what the
builder already believes it did. Anything the spec required but the summary never
mentions is exactly the item this ordering is designed to catch.

Corollary for verdicts: where some criteria were checked and others could not be
driven at all, the result is PARTIAL, never rounded up to PASS. "Unverifiable"
and "verified" are different findings.

> **Provenance.** External field evidence from an internal OutSystems project
> @ 3524310 (adopted 2026-08-14, round 2); field-observed in that project's own
> verification agent, not in official docs, and **not measured by us.**
