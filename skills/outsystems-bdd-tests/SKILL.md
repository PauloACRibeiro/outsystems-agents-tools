---
name: outsystems-bdd-tests
description: Generate a BDDFramework test module through ODC Mentor and execute its suites over the BDD Framework API, reporting trustworthy per-scenario pass/fail. Use when the user asks to "run the BDD tests", "execute the test suite", "did the tests pass", "generate BDD tests for this app", "add a testing phase", or wants real pass/fail from an OutSystems app rather than test scaffolding. The sprint loop's testing phase, between publish and grading.
---

The sprint loop had no testing phase: it ran idea → plan → design → review →
build → publish → grade, and nothing in it ever executed the app's own logic and
reported pass or fail. This skill is that phase.

Two halves, usable independently:

- **Generate** — compose a Mentor prompt that builds an `<AppName>Tests` module.
- **Execute** — call the BDD Framework API's runner and report per-scenario
  results with a trustworthy exit code.

Everything the skill asserts about the components was measured against their own
OMLs and against a live tenant. The two reference files carry that evidence:
`outsystems-bdd-tests/references/component-contract.md` for what a test module
must look like, and `outsystems-bdd-tests/references/runner-contract.md` for the
REST contract. Read the relevant one before improvising.

## Prerequisites

Two Forge components, both installed by a human — **Mentor cannot install them
and neither can this skill**:

| Component | ID | Needed for |
|---|---|---|
| `BDD Framework (ODC)` | 15745 | building the test module at all |
| `BDD Framework API (ODC)` | 15746 | the REST runner this skill calls |

Installing only the first gives browser-run suites and no REST runner. That is
the most likely reason `preflight` reports the runner missing.

`Template_BDD Framework` 0.1.7 is optional — a clonable skeleton whose
conventions this skill follows but does not require.

Also required:

- The suite screen's `AuthToken` input must match the token you pass. It is a
  shared secret gating the screen.
- **The token comes from `ODC_BDD_AUTH_TOKEN`**, never from a repo file, and is
  never echoed. `--auth-token` exists for a caller that already holds it.
- Library settings configured per consuming app, as the components require.

Start every session with:

```bash
python3 scripts/odc_bdd_tests.py --hostname <tenant>-<env>.outsystems.app preflight
```

It fetches the swagger, checks the token is present, and names the exact
component and Forge URL if the runner is absent — instead of a 404 that reads
as a broken skill. **Use the runtime host**: `<tenant>.outsystems.dev` returns
404 for this path.

`preflight` deliberately does **not** claim your module and suite names resolve.
A 401 rejects a bad name and a bad token identically, because authentication is
evaluated before the path parameters do, so only a real run can confirm the
target.

## Phase 1 — Generate

```bash
python3 scripts/odc_bdd_tests.py generate \
  --app RoomBooking --flow TestFlow --count 5 \
  --scope "the booking service actions"
```

### Deciding which scenarios, not just how many

`--count` asks for a number and lets Mentor choose the scenarios. What it
chooses are the ones easiest to think of — the happy path, three times — and
nothing records the ones it did not. Decide them first instead, in a scenario
plan, and pass it:

```bash
python3 scripts/odc_bdd_tests.py generate \
  --app RoomBooking --flow TestFlow --plan plan.json \
  --scope "the booking service actions"
```

The plan enumerates each scenario by id, title and assertions, so the prompt
asks for those and no others. `--count` is ignored when a plan is given. The
schema, the validation rules and a worked example are in
`outsystems-bdd-tests/references/scenario-plan.md`.

Plan against these six categories, and treat one with no scenario as a gap:

| Category | What belongs here |
|---|---|
| `happy-path` | the flow works for the role it is meant for |
| `validation` | bad input is rejected, and the way the spec says |
| `boundary` | the exact threshold — at it, one under, one over |
| `role-forbidden` | an action the caller's role must not be able to perform |
| `volume` | many rows, long lists, repeated calls |
| `regression` | added after a specific defect, and named for it |

`generate --plan` prints a `COVERAGE GAP` line naming every category the plan
does not cover. It computes that against the six above, never against the
categories the plan happens to use — a check over what is present cannot report
the category nobody wrote anything for, which is the largest gap it could have
reported.

Scenarios sit in three buckets — `mustHave`, `niceToHave`, `optional` — and
carry a `P0`–`P3` priority. **The bucket is the delivery decision and the
priority orders the work inside it**; a plan carrying only one of them has
answered half the question. Every scenario also carries the requirement ids it
covers, and an empty list is a signal rather than an omission: that scenario is
defensive coverage — a smoke, an audit confirmation — not something anyone
asked for.

**A requirement with nothing implementing it still gets a scenario**, marked
`gap: true`. It asserts the intended behaviour and fails until someone builds
it, and the composed prompt says so. Never write it as a skip: an all-skipped
suite reports `IsSuccess: true` (see *Reading the result*), so a skipped gap
scenario reports success for work nobody has done. A plan with gaps therefore
exits 1 by design; `--baseline` keeps the known failures from burying a new one.

This prints a paste-ready Mentor prompt composed from
`outsystems-bdd-tests/references/component-contract.md`. The script composes; it
does not drive Mentor — it is stdlib-only and cannot call an MCP tool, and the
gated part should stay gated.

**Resolve or create the target flow first, and pass it with `--flow`.** A
template-cloned ODC app has no `MainFlow`; it has `BusinessValuePerceptionTags`,
`Common` and `ScreenTemplates`. `--flow` is required precisely so nobody assumes
a flow that does not exist.

Then, mirroring the delivery gate in `outsystems-plan-to-mentor`:

1. Where the OutSystems MCP is available, pass the prompt to `mentor_start` and
   **approve each edit**.
2. Where it is not, hand the prompt to whoever drives Mentor. Colleagues without
   the plugin are not stranded.

### The publish is the commit

**A Mentor turn writes into the session, and `publish_start` takes the OML from
that session.** There is no separate save. So after a Mentor turn, four things
all look like "nothing happened" and all four are correct behaviour:
`change_applied: true` means applied to the *session*, no app revision appears,
ODC Studio shows nothing, and the Context Service shows nothing.

**Publish before concluding anything.** Then check the publish's own
`no_changes_detected` before believing it landed.

**Two publish outcomes are not failures to retry** (upstream plugin 0.16.0). If
`publish_start` *refuses* the session, the refusal names the reason and the fix,
and the remedy is another Mentor turn that finishes the test module — never a
second publish; a `succeeded` turn carrying `turn_error` is the usual cause, and
it is not a finished task. If `publish_status` reaches `failed` carrying
`indeterminate: true`, the server lost sight of the publish and it may still be
building: re-poll with the `publication_key` in the payload, or verify with
`env_app`. Re-publishing there is what wedges an app — and a wedged app means no
test module to run at all.

**And check the tip revision BEFORE publishing.** Record the tip revision from
`app_revisions` when the Mentor session starts — that baseline is what the
pre-publish check compares against. A publish deploys the session's full OML
snapshot — last-writer-wins, no merge (vendor-confirmed 2026-08-24). If
`app_revisions` shows the tip moved past that baseline — Studio, a colleague,
another agent — publishing now silently erases those revisions. Don't publish
from a stale session: start a fresh `app_key` session (it reads the new tip as
its base) and replay the prompt. `fresh_context` does not rebase.

### Then run the readback gate

Mentor's closing summary is a claim; the tenant is the fact. After the publish,
put the element names Mentor listed in one file and the names the tenant reports
(via `context_screens` or ODC Studio) in another:

```bash
python3 scripts/odc_bdd_tests.py verify --expect claimed.txt --observed actual.txt
```

Exit 0 means every claimed element is present. Exit 2 names the gaps.

**Run it after the publish, never instead of one.** Run before, it reports every
element missing, and that reading is wrong — it is the reading this estate took
once before the cause was understood. An empty `--expect` file is treated as a
gap, not a pass: having nothing to check against must never read as verified.

## Phase 2 — Execute

```bash
export ODC_BDD_AUTH_TOKEN=...
python3 scripts/odc_bdd_tests.py --hostname <tenant>-<env>.outsystems.app \
  run --module RoomBookingTests --suite Suite_Bookings
```

The run is **synchronous**: one GET, one 200, the complete result in the body.
There is no run id, no status endpoint and nothing to poll.

Useful flags:

| Flag | Does |
|---|---|
| `--tags` / `--skip-tags` | sent as the `ExecuteTags` / `SkipTags` **headers** |
| `--timeout-ms` | the `Timeout` header, a server-side bound |
| `--dry-run` | print the request, call nothing |
| `--out <file>` | save the raw result |
| `--json` | machine-readable output |
| `--baseline <file>` | fail on any scenario that passed there and does not pass now |

`run` verifies the tag filter actually took effect by matching every returned
scenario's tags against what you asked for. A filter the server ignored
otherwise looks identical to one it applied.

`report --out <file>` re-renders a saved result and makes no tenant call.
`list` explains where to find suite screens — the API exposes one operation and
no catalogue, so there is nothing to enumerate.

`--baseline` can only make a verdict worse, never better. A clean comparison
cannot turn an inconclusive run green.

## Reading the result

| exit | means |
|---|---|
| `0` | pass — a parsed 200, at least one scenario, `IsSuccess: true`, **and** `SuccessfulScenarios > 0` |
| `1` | real failure — at least one scenario failed, or a baseline regression |
| `2` | inconclusive — trust nothing about this run |

**`IsSuccess` is never the gate on its own.** The API computes it as
`(countSuccess > 0 or countSkipped > 0) and countFailed = 0`, so an **all-skipped
suite reports `IsSuccess: true`**. The field that looks like the verdict is
exactly the field that cannot tell "everything passed" from "nothing ran". A
test stage that reports success because it measured nothing is worse than no
test stage, because it launders absence into evidence.

Exit 2 also covers: a rejected token (a 401 is inconclusive, not a failure), an
unreachable host, an unparseable body, a non-empty `ErrorMessage`, and a
response that contradicts itself in either direction.

Two things that look like failures and are not: `FailureReport` is populated on
a **pass**, carrying `[Passed]` markers — it is a step log. And zero-valued
counters are **omitted** from the response, not zero-filled.

The full exit table and the measured error shapes are in
`outsystems-bdd-tests/references/runner-contract.md`.

### Blocked is not not-done

When the sprint loop's run log records this phase, two negative verdicts
stay distinct:

- **Not done** — a path exists and the attempt failed: exit 1 (scenarios
  failed), or an exit 2 whose output shows a call reached the wire — a
  401, an unparseable body, a response that contradicts itself. Fix and
  re-run.
- **Blocked** — no path exists: the exit-2 output names a missing
  prerequisite instead of a wire response — `preflight`'s
  runner-not-reachable lines naming the component to install, or the
  no-token refusal (`run` refuses the same way before touching the wire),
  with nobody present to supply what is missing.

Exit 2 alone decides nothing here — `preflight` and a token-less `run`
exit 2 on precisely the no-path cases. What the output names decides.

Never mark the phase blocked from memory or a prior session's preflight.
Components get installed and tokens get set between sessions, so only a
fresh preflight can establish that no path exists now. Blocked is run-log
vocabulary, not a runner exit — the exit table stays 0/1/2.

And if you cannot find something — the module, the suite, the runner path —
that is a finding, reported with the response you observed (the 401, the
404, preflight's named component), never a license to skip the phase or to
mark it blocked from recall. A 401 rejects a bad name and a bad token
identically, so recall cannot even tell you which of the two you have.

## When NOT to use this skill

| You want | Use instead |
|---|---|
| UI quality scored from a live runtime URL | `outsystems-runtime-ui-audit` |
| Visual or UI-implementation quality judged from the model | not this skill — it never looks at presentation |
| Confirmation that a screen *renders* for a signed-in user | not this skill — it executes logic, it does not load screens |
| Test *scaffolding* for a human to finish | not this skill — the point here is an executed pass/fail |

This skill does not install Forge components, does not run browser journeys, and
makes no tenant mutation beyond the Mentor edits the loop already gates.

## Tests

```bash
python3 -m unittest discover -s skills/outsystems-bdd-tests/tests -v
```

The `-s` flag is required: `outsystems-bdd-tests` is not a valid Python
identifier, so bare discovery from the repo root finds nothing and reports it as
an empty suite. Every test runs offline against fixtures; none touches a tenant.
