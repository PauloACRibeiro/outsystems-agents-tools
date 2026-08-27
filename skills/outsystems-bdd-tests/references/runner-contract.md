# BDD Framework API (ODC) — the runner contract

The REST surface this skill calls, measured against a live tenant rather than
read from a documentation page. Labels as in `component-contract.md`:
**MEASURED** means a command was run; **DOC-PAGE** means published documentation.

## The two Forge components

| Component | ID |
|---|---|
| `BDD Framework (ODC)` | 15745 |
| `BDD Framework API (ODC)` | 15746 |

This contract needs **both**. Installing only `BDD Framework (ODC)` gives
browser-run suites and no REST runner, which is the single most likely reason a
colleague sees a 404 here.

`BDDFrameworkTestRunLib`, where execution happens, is an External Logic (C#)
library and therefore unreadable by design.

## The endpoint

MEASURED — the deployed component's own OpenAPI document, fetched from the
tenant, HTTP 200, parsed; independently re-verified by Codex.

```
GET https://<runtime-host>/BDDFrameworkAPI/rest/TestTrigger/BDDTestRunner/{TestESpace}/{TestSuiteScreen}
Authorization: Bearer <token>
```

| Path parameter | Means |
|---|---|
| `TestESpace` | the **module** holding the tests, e.g. `ElasticSearchConnectorTests` |
| `TestSuiteScreen` | the suite **screen**, e.g. `Suite_Records` |

**Runtime host, not the portal host.** `<tenant>.outsystems.dev` returns 404 for
this path; the runtime is `<tenant>-<env>.outsystems.app`. That 404 reads exactly
like "no such endpoint" and cost a full round to diagnose.

The swagger document is readable without authentication at
`/BDDFrameworkAPI/rest/TestTrigger/swagger.json`, which is what `preflight` uses
to tell "component missing" apart from "token rejected".

## The run is synchronous

MEASURED: the surface is one path, `GET` only, with a single `200` whose body is
the complete `SuiteExecutionResult`. There is no run id, no status endpoint and
**nothing to poll**. The optional `Timeout` header is the server-side bound and
replaces any client-side polling timeout entirely.

## The three optional parameters are HEADERS

MEASURED. `ExecuteTags`, `SkipTags` and `Timeout` are HTTP header parameters and
not query parameters. Sent as a query string the runner does not look at them,
and the suite runs **unfiltered while appearing to filter** — a silent
wrong-scope pass rather than a visible error.

| Header | Value |
|---|---|
| `ExecuteTags` | comma-separated tags to include |
| `SkipTags` | comma-separated tags to exclude |
| `Timeout` | server-side bound in milliseconds |

**The response proves whether the filter was honoured.** Each returned
`TestScenarioResult` carries its own `Tags`, so a client should match every
returned scenario against what was asked for instead of trusting the header.
Cheap, and it turns an invisible wrong-scope pass into a loud one.

## The response schema

A 200 body is a `SuiteExecutionResult`:

| Field | Notes |
|---|---|
| `SuiteScreen` | the full suite URL — **carries the bearer token in clear text** |
| `IsSuccess` | computed, not reported; see below |
| `SuccessfulScenarios` | omitted when zero |
| `FailedScenarios` | omitted when zero |
| `SkippedScenarios` | omitted when zero |
| `ErrorMessage` | omitted when empty |
| `TestScenarioResults` | list of per-scenario results |

Each `TestScenarioResult` carries `ScenarioId`, `Description`, `IsSuccess`,
`IsSkipped`, `FailureReport` and `Tags`.

## `IsSuccess` is computed, not reported

MEASURED from the API's `CreateResponse`:

```
IsSuccess = (countSuccess > 0 or countSkipped > 0) and countFailed = 0
```

Two consequences, and the second is the dangerous one:

- A **zero-scenario** suite already returns `IsSuccess: false`, because both
  counts are zero. The API fails closed here on its own and needs no guard.
- An **all-skipped** suite returns `IsSuccess: true`, because a positive skip
  count with no failures satisfies the expression. **This is the real
  false-green**: a run that executed nothing is indistinguishable from one that
  passed, unless `SuccessfulScenarios > 0` is required as well.

**`IsSuccess` must never be the gate on its own.** The field that looks like the
verdict is exactly the field that cannot tell "everything passed" from "nothing
ran", and a test stage that reports success because it measured nothing is worse
than no test stage.

## The three traps in a real green response

MEASURED 2026-08-23, the first authenticated success, verbatim except the token:

```json
{ "SuiteScreen": "https://<host>/ElasticSearchConnectorTests/Suite_Records?AuthToken=<REDACTED>",
  "IsSuccess": true, "SuccessfulScenarios": 1,
  "TestScenarioResults": [ { "ScenarioId": "ES-001", "IsSuccess": true,
      "FailureReport": "\r\nGiven\r\n… [Passed] \r\n\r\nWhen\r\n… [Passed] \r\n" } ] }
```

1. **`SuiteScreen` echoes the bearer token in clear text.** Redact it on ingest
   rather than at display time, so no later code path — rendering, JSON output,
   logging, an exception message — can reach the raw value. Otherwise every run
   leaks the shared secret into a terminal, a CI log and a report.
2. **Zero-valued fields are omitted, not zero-filled.** `FailedScenarios`,
   `SkippedScenarios` and `ErrorMessage` are all absent above. Subscripting
   raises, `.get()` yields `None`, and `None > 0` is a `TypeError`, so every
   count needs a default of zero. The all-skipped guard depends on this, since
   `SuccessfulScenarios` is itself absent on such a run.
3. **`FailureReport` is populated on a pass**, carrying `[Passed]` markers. It is
   a step log, not a failure-only field, and reading a non-empty value as failure
   calls a green run red.

## The exit table

| exit | condition, in the response's own terms |
|---|---|
| `0` | `TestScenarioResults` non-empty **and** `FailedScenarios == 0` **and** `IsSuccess: true` **and** `SuccessfulScenarios > 0` |
| `1` | `FailedScenarios > 0` |
| `2` | `TestScenarioResults` empty, or all three counters zero |
| `2` | `IsSuccess: false` with `FailedScenarios == 0` — the suite says it failed and cannot say which scenario did |
| `2` | `IsSuccess: true` with `FailedScenarios > 0` — the mirror contradiction |
| `2` | `SuccessfulScenarios == 0` with `SkippedScenarios > 0` — every scenario was skipped |
| `2` | rejected token, unreachable host, unparseable body, or `ErrorMessage` set |

**The only path to green is a parsed 200, at least one scenario, `IsSuccess:
true`, and `SuccessfulScenarios > 0`.** Everything else is red or inconclusive,
and both exit non-zero so the skill can gate CI.

A verdict field that disagrees with the counters means the run cannot be trusted
in **either** direction. Picking the optimistic reading of a self-contradictory
response is how a green gate stops meaning anything.

## Error shapes

All MEASURED 2026-08-23.

- **The OpenAPI declares no security scheme** — `security` and
  `securityDefinitions` are both null — although the token *is* enforced. A
  client generated from that spec omits the header and the rejection reads as a
  broken endpoint. Add the `Authorization` header yourself.
- **A rejected token returns a genuine `401`** carrying an RFC 9110 problem
  document: `errors`, `type`, `title`, `status`, `traceId`, and **no `IsSuccess`
  field**. Branch on status first and parse as a `SuiteExecutionResult` only on
  200; parsing the problem document as a result would read as a failed run
  rather than an unusable response.
- **A `401` cannot confirm the target exists.** Controlled comparison: real
  names, a bogus screen and a bogus module all return 401 identically, while a
  bogus *operation* returns 404. Authentication is evaluated before path
  parameters resolve, so `preflight` must not report the target found on a 401.
- **A `401` is exit 2, not exit 1.** It is an unusable response, not a test
  failure.
- **An unresolvable suite name with a valid token returns `200`** with an
  `ErrorMessage` such as `Could not find tests in the screen 'X' of eSpace 'Y'`.
  The name-resolution failure surfaces in the body, not the status.
- **Non-200 statuses are deliberate**, set by the component via
  `Response_SetStatusCode`. Print status and body, report inconclusive, exit
  non-zero — but describe it as a response, not as a broken endpoint.

## The token

The token is a shared secret gating the suite screen. It comes from an
environment variable (`ODC_BDD_AUTH_TOKEN`), never from a repo file, and is
never echoed. It must match the `AuthToken` the suite screen passes to
`LayoutBase`.
