#!/usr/bin/env python3
"""Run OutSystems BDDFramework suites over the BDD Framework API (ODC).

Stdlib only. See ../references/runner-contract.md for the measured contract.
"""
from __future__ import annotations

from typing import NamedTuple

import argparse
import json
import os
import pathlib
import re
import urllib.error
import urllib.request

# `SuiteScreen` echoes the full suite URL including ?AuthToken=<secret>
# (MEASURED 2026-08-23). Redaction happens at ingest so no later code path —
# rendering, JSON output, logging, an exception message — can reach the raw
# value.
_TOKEN_IN_URL = re.compile(r"((?:\?|&)authtoken=)[^&\s\"']*", re.IGNORECASE)


class ResultParseError(Exception):
    """The body was not a JSON object. Never treat it as a result."""


def redact_tokens(value):
    """Replace any AuthToken query value, anywhere in a nested structure."""
    if isinstance(value, str):
        return _TOKEN_IN_URL.sub(r"\1<REDACTED>", value)
    if isinstance(value, dict):
        return {k: redact_tokens(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_tokens(v) for v in value]
    return value


def parse_result(body: bytes) -> dict:
    """Parse a 200 body as a SuiteExecutionResult, redacted on the way in."""
    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ResultParseError(f"response body is not JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ResultParseError(
            f"response body is JSON but not an object (got {type(parsed).__name__})")
    return redact_tokens(parsed)


class Verdict(NamedTuple):
    exit_code: int      # 0 pass, 1 real failure, 2 inconclusive
    label: str          # "pass" | "fail" | "inconclusive"
    reason: str


def _count(payload: dict, name: str) -> int:
    """Counters are OMITTED when zero, never zero-filled (MEASURED).

    Subscripting raises and `.get()` yields None, which then raises on
    comparison. Every count in this module goes through here.
    """
    value = payload.get(name)
    try:
        return 0 if value is None else int(value)
    except (TypeError, ValueError):
        # A malformed counter is already exit 2 via _schema_type_error; the
        # renderer must not crash on the same payload it is reporting about.
        return 0


def _schema_type_error(payload: dict):
    """Name the first field whose TYPE contradicts the measured schema.

    Fail-closed, and the reason is measured: bool("false") is True and a dict
    is truthy, so without this check a response carrying IsSuccess: "false" or
    a dictionary-valued TestScenarioResults took the PASS row (found by Codex,
    AH-2026-08-24-007 round 2; reproduced before fixing). bool is excluded
    from the counter check explicitly because it is an int subclass.
    """
    success = payload.get("IsSuccess")
    if success is not None and not isinstance(success, bool):
        return f"IsSuccess is {type(success).__name__} {success!r}, not a boolean"
    results = payload.get("TestScenarioResults")
    if results is not None and not isinstance(results, list):
        return f"TestScenarioResults is {type(results).__name__}, not a list"
    for name in ("SuccessfulScenarios", "FailedScenarios", "SkippedScenarios"):
        value = payload.get(name)
        if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
            return f"{name} is {type(value).__name__} {value!r}, not an integer"
    return None


def classify_result(payload: dict) -> Verdict:
    """Map a parsed SuiteExecutionResult onto the spec's exit table.

    Order matters: the most specific contradictions are tested before the
    ordinary pass and fail rows, so a self-contradictory response can never
    fall through to an optimistic reading.
    """
    problem = _schema_type_error(payload)
    if problem:
        return Verdict(2, "inconclusive",
                       f"malformed response: {problem}; refusing to interpret it")
    results = payload.get("TestScenarioResults") or []
    passed = _count(payload, "SuccessfulScenarios")
    failed = _count(payload, "FailedScenarios")
    skipped = _count(payload, "SkippedScenarios")
    success = bool(payload.get("IsSuccess"))
    error = (payload.get("ErrorMessage") or "").strip()

    if error:
        return Verdict(2, "inconclusive", f"the runner returned ErrorMessage: {error}")
    if not results:
        return Verdict(2, "inconclusive", "the suite returned no scenarios at all")
    if passed == 0 and failed == 0 and skipped == 0:
        return Verdict(2, "inconclusive", "every counter is zero, so nothing was executed")
    if success and failed > 0:
        return Verdict(2, "inconclusive",
                       f"IsSuccess is true but {failed} scenario(s) failed")
    if not success and failed == 0:
        return Verdict(2, "inconclusive",
                       "IsSuccess is false but no scenario is reported failed, "
                       "so the suite cannot say what went wrong")
    if passed == 0 and skipped > 0:
        return Verdict(2, "inconclusive",
                       f"all {skipped} scenario(s) were skipped, so the suite "
                       "executed nothing while IsSuccess reads true")
    if failed > 0:
        return Verdict(1, "fail", f"{failed} of {len(results)} scenario(s) failed")
    if success and passed > 0:
        return Verdict(0, "pass", f"{passed} of {len(results)} scenario(s) passed")
    return Verdict(2, "inconclusive", "the response did not match any known-good shape")


RUNNER_PATH = "/BDDFrameworkAPI/rest/TestTrigger/BDDTestRunner"
SWAGGER_PATH = "/BDDFrameworkAPI/rest/TestTrigger/swagger.json"
API_COMPONENT = "BDD Framework API (ODC)"
API_COMPONENT_URL = "https://www.outsystems.com/forge/component-overview/15746/bdd-framework-api-odc"


class RunOutcome(NamedTuple):
    status: int
    payload: dict | None
    verdict: Verdict


def build_run_request(hostname, module, suite, token,
                      tags=None, skip_tags=None, timeout_ms=None):
    """One GET. Filters and the timeout are HEADERS, never query parameters.

    Sent as query parameters the runner does not look at them, and the suite
    runs unfiltered while appearing to filter.
    """
    url = f"https://{hostname}{RUNNER_PATH}/{module}/{suite}"
    request = urllib.request.Request(url, method="GET")
    # The OpenAPI declares no security scheme though the token IS enforced.
    request.add_header("Authorization", f"Bearer {token}")
    if tags:
        request.add_header("ExecuteTags", tags)
    if skip_tags:
        request.add_header("SkipTags", skip_tags)
    if timeout_ms is not None:
        request.add_header("Timeout", str(timeout_ms))
    return request


def interpret_response(status: int, body: bytes) -> RunOutcome:
    """Branch on status FIRST; parse as a result only on 200.

    A non-200 body is a different schema — the 401 is an RFC 9110 problem
    document with no IsSuccess field — so parsing it as a result would read as
    a failed run rather than as an unusable response.
    """
    if status != 200:
        detail = body.decode("utf-8", "replace").strip()[:400]
        note = (" A 401 here cannot confirm the target exists: authentication is "
                "evaluated before the path parameters resolve, so a bad module "
                "and a bad suite name reject identically."
                if status == 401 else "")
        return RunOutcome(status, None, Verdict(
            2, "inconclusive",
            f"the runner answered HTTP {status} rather than 200.{note} Body: {detail}"))
    try:
        payload = parse_result(body)
    except ResultParseError as exc:
        return RunOutcome(status, None, Verdict(
            2, "inconclusive", f"HTTP 200 but the body could not be read: {exc}"))
    return RunOutcome(status, payload, classify_result(payload))


def check_tag_filter(payload: dict, requested_tags):
    """Confirm the ExecuteTags header was honoured, using the returned data.

    Each TestScenarioResult carries its own Tags, so the response itself proves
    whether the filter took effect. Trusting the header instead would let a
    wrong-scope run pass silently.
    """
    if not requested_tags:
        return None
    asked = [t.strip() for t in requested_tags.split(",") if t.strip()]
    if not asked:
        return None
    # Compare casefolded, but report the spelling the caller actually typed:
    # echoing a lowercased list back makes the complaint hard to match against
    # the command that produced it.
    wanted = {t.casefold() for t in asked}
    offenders = []
    for scenario in payload.get("TestScenarioResults") or []:
        tags = {str(t).strip().casefold() for t in (scenario.get("Tags") or [])}
        if not tags & wanted:
            offenders.append(scenario.get("ScenarioId") or "<unnamed>")
    if not offenders:
        return None
    return (f"--tags asked for {', '.join(asked)} but "
            f"{len(offenders)} returned scenario(s) carry none of them "
            f"({', '.join(offenders)}). The server did not honour the filter, "
            "so this run covered a wider scope than requested.")


def default_fetch(request):
    """Perform the request. Returns (status, body) and never raises on HTTP."""
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return response.getcode(), response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except urllib.error.URLError as exc:
        return 0, str(exc.reason).encode()


def resolve_token(args):
    """--auth-token, else the environment. Never a file, never echoed."""
    return getattr(args, "auth_token", None) or os.environ.get("ODC_BDD_AUTH_TOKEN")


# Built rather than written literally: a bare triple backtick inside this
# file would terminate a Markdown fence when the code is quoted in docs.
_FENCE = "`" * 3


def render_report(payload: dict, verdict: Verdict) -> str:
    """Markdown. The payload is already redacted; nothing here re-reads a URL."""
    lines = [f"# BDD suite: {verdict.label.upper()}", "", verdict.reason, ""]
    lines.append(f"- passed: {_count(payload, 'SuccessfulScenarios')}")
    lines.append(f"- failed: {_count(payload, 'FailedScenarios')}")
    lines.append(f"- skipped: {_count(payload, 'SkippedScenarios')}")
    error = (payload.get("ErrorMessage") or "").strip()
    if error:
        lines.append(f"- **ErrorMessage:** {error}")
    lines.append("")
    for scenario in payload.get("TestScenarioResults") or []:
        if scenario.get("IsSkipped"):
            mark = "SKIPPED"
        elif scenario.get("IsSuccess"):
            mark = "PASS"
        else:
            mark = "FAIL"
        name = scenario.get("ScenarioId") or "<unnamed>"
        desc = scenario.get("Description") or ""
        lines.append(f"## {mark} — {name} {desc}".rstrip())
        report = (scenario.get("FailureReport") or "").strip()
        if report:
            # A step log, populated on a pass too. Shown as evidence, never
            # read as a failure signal.
            lines.append("")
            lines.append(_FENCE)
            lines.append(report)
            lines.append(_FENCE)
        lines.append("")
    return "\n".join(lines)


def passing_scenario_ids(payload):
    """ScenarioIds that genuinely passed: succeeded AND were not skipped."""
    ids = set()
    for scenario in payload.get("TestScenarioResults") or []:
        if scenario.get("IsSuccess") and not scenario.get("IsSkipped"):
            sid = str(scenario.get("ScenarioId", "")).strip()
            if sid:
                ids.add(sid)
    return ids


def baseline_regressions(baseline, current):
    """Scenarios that passed in the baseline and do not pass now.

    A scenario that has VANISHED counts, not just one that turned red: a
    deleted scenario is the quietest way for coverage to fall, and the
    counters cannot see it.
    """
    return sorted(passing_scenario_ids(baseline) - passing_scenario_ids(current))


def apply_baseline(verdict, baseline, current):
    """Escalate a verdict on regression. NEVER de-escalates.

    A baseline can only make a result worse. Letting a clean comparison soften
    an inconclusive verdict would turn --baseline into a way of laundering an
    all-skipped run into green - the exact failure the exit table exists to
    prevent.
    """
    if baseline is None:
        return verdict
    regressed = baseline_regressions(baseline, current)
    if not regressed:
        return verdict
    if verdict.exit_code == 0:
        noun = "scenario" if len(regressed) == 1 else "scenarios"
        return Verdict(1, "fail",
                       f"regression against the baseline: {len(regressed)} {noun} "
                       f"({', '.join(regressed)}) passed there and no longer pass")
    return verdict._replace(
        reason=verdict.reason + f" (also regressed: {', '.join(regressed)})")


def load_baseline(path):
    """Read a baseline result file. Unreadable is fatal, never ignored.

    A baseline that silently fails to load leaves the caller believing a
    regression check ran when none did.
    """
    if not path:
        return None
    return parse_result(pathlib.Path(path).read_bytes())


def cmd_preflight(args, fetch=default_fetch, echo=print) -> int:
    token = resolve_token(args)
    if not token:
        echo("FAIL: no token. Set ODC_BDD_AUTH_TOKEN, or pass --auth-token.")
        echo("      It must match the AuthToken protecting the suite screen.")
        return 2
    status, body = fetch(urllib.request.Request(
        f"https://{args.hostname}{SWAGGER_PATH}", method="GET"))
    if status == 200:
        echo(f"OK: {API_COMPONENT} is reachable on {args.hostname}.")
        echo("Note: this proves the component is installed, not that your module "
             "and suite names resolve — a 401 rejects a bad name and a bad token "
             "identically, so only a real run can confirm the target.")
        return 0
    echo(f"FAIL: the runner is not reachable on {args.hostname} (HTTP {status}).")
    echo(f"      Install '{API_COMPONENT}' from the Forge: {API_COMPONENT_URL}")
    echo("      Installing only 'BDDFramework' gives browser-run suites and no "
         "REST runner.")
    echo(f"      Check the host too: the runtime is <tenant>-<env>.outsystems.app, "
         f"not <tenant>.outsystems.dev, which 404s this path.")
    return 2


def cmd_run(args, fetch=default_fetch, echo=print) -> int:
    token = resolve_token(args)
    if not token:
        echo("FAIL: no token. Set ODC_BDD_AUTH_TOKEN, or pass --auth-token.")
        return 2
    request = build_run_request(
        args.hostname, args.module, args.suite, token,
        tags=args.tags, skip_tags=args.skip_tags, timeout_ms=args.timeout_ms)
    if args.dry_run:
        echo(f"DRY RUN: GET {request.full_url}")
        echo(f"         headers: {sorted(k for k in request.headers if k != 'Authorization')}"
             " (+ Authorization, not shown)")
        return 0
    status, body = fetch(request)
    outcome = interpret_response(status, body)
    if outcome.payload is not None:
        complaint = check_tag_filter(outcome.payload, args.tags)
        if complaint:
            echo(f"INCONCLUSIVE: {complaint}")
            _emit(args, outcome.payload, Verdict(2, "inconclusive", complaint), echo)
            return 2
    if outcome.payload is None:
        echo(f"{outcome.verdict.label.upper()}: {outcome.verdict.reason}")
        return outcome.verdict.exit_code
    try:
        baseline = load_baseline(getattr(args, "baseline", None))
    except (OSError, ResultParseError) as exc:
        echo(f"FAIL: --baseline could not be read: {exc}")
        return 2
    verdict = apply_baseline(outcome.verdict, baseline, outcome.payload)
    _emit(args, outcome.payload, verdict, echo)
    return verdict.exit_code


def _emit(args, payload, verdict, echo):
    if getattr(args, "out", None):
        pathlib.Path(args.out).write_text(json.dumps(payload, indent=2), "utf-8")
    if getattr(args, "json", False):
        echo(json.dumps({"exit_code": verdict.exit_code, "label": verdict.label,
                         "reason": verdict.reason, "result": payload}, indent=2))
    else:
        echo(render_report(payload, verdict))


def cmd_report(args, echo=print) -> int:
    if not getattr(args, "out", None):
        echo("FAIL: report needs --out naming a saved result file.")
        return 2
    try:
        payload = parse_result(pathlib.Path(args.out).read_bytes())
    except (OSError, ResultParseError) as exc:
        echo(f"FAIL: could not read {args.out}: {exc}")
        return 2
    verdict = classify_result(payload)
    try:
        baseline = load_baseline(getattr(args, "baseline", None))
    except (OSError, ResultParseError) as exc:
        echo(f"FAIL: --baseline could not be read: {exc}")
        return 2
    verdict = apply_baseline(verdict, baseline, payload)
    echo(render_report(payload, verdict))
    return verdict.exit_code


def cmd_list(args, fetch=default_fetch, echo=print) -> int:
    """Discovery is not available over this API.

    The runner exposes one operation and no catalogue, so there is nothing to
    enumerate. Saying so is more useful than a verb that silently returns
    nothing.
    """
    echo("The BDD Framework API exposes one operation and no discovery endpoint,")
    echo("so suite screens cannot be listed from it. Find them in ODC Studio, or")
    echo("via the OutSystems MCP: context_screens --app <YourAppTests>.")
    echo("Pass the app name to --module and the screen name to --suite.")
    return 0


BUCKETS = ("mustHave", "niceToHave", "optional")
CATEGORIES = ("happy-path", "validation", "boundary",
              "role-forbidden", "volume", "regression")
PRIORITIES = ("P0", "P1", "P2", "P3")


def load_scenario_plan(path):
    """Read and validate a scenario plan; return its scenarios in prompt order.

    Order is bucket first (mustHave, niceToHave, optional), then priority
    within the bucket. The bucket is the delivery decision and the priority
    orders the work inside it; neither is recoverable from the other, so both
    are required and both are honoured here.

    A plan with no scenarios raises. That mirrors `readback_gaps` treating an
    empty expectation list as a gap: having nothing to check against must never
    read as verified. See references/scenario-plan.md.
    """
    raw = json.loads(pathlib.Path(path).read_text("utf-8"))
    buckets = raw.get("scenarios")
    if not isinstance(buckets, dict):
        raise ValueError("plan has no `scenarios` object")
    unknown = [b for b in buckets if b not in BUCKETS]
    if unknown:
        raise ValueError(f"unknown bucket(s): {', '.join(sorted(unknown))}; "
                         f"expected {', '.join(BUCKETS)}")

    ordered, seen = [], set()
    for bucket in BUCKETS:
        entries = buckets.get(bucket) or []
        if not isinstance(entries, list):
            raise ValueError(f"bucket `{bucket}` is not a list")
        # Type-check BEFORE sorting. The sort key reads `priority` off every
        # entry, so a non-object entry raised AttributeError out of the lambda
        # and `generate --plan` printed a traceback instead of FAIL/exit 2 -
        # the per-entry guard below could never run. Codex caught it on
        # AH-2026-08-26-005 round 2.
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"bucket `{bucket}` holds a non-object entry")
        for entry in sorted(entries, key=lambda e: str(e.get("priority", ""))):
            _validate_scenario(entry, bucket, seen)
            seen.add(entry["id"])
            ordered.append(dict(entry, bucket=bucket))

    if not ordered:
        raise ValueError("plan lists no scenarios; refusing to compose a "
                         "prompt from an empty plan")
    return ordered


def _validate_scenario(entry, bucket, seen):
    """Reject a scenario the prompt would otherwise render as a plausible blank."""
    if not isinstance(entry, dict):
        raise ValueError(f"bucket `{bucket}` holds a non-object entry")
    ident = entry.get("id")
    if not ident:
        raise ValueError(f"a scenario in `{bucket}` has no `id`")
    if ident in seen:
        raise ValueError(f"duplicate scenario id: {ident}")
    if not entry.get("title"):
        raise ValueError(f"{ident} has no `title`")
    if entry.get("category") not in CATEGORIES:
        raise ValueError(f"{ident} has category {entry.get('category')!r}; "
                         f"expected one of {', '.join(CATEGORIES)}")
    if entry.get("priority") not in PRIORITIES:
        raise ValueError(f"{ident} has priority {entry.get('priority')!r}; "
                         f"expected one of {', '.join(PRIORITIES)}")
    asserts = entry.get("asserts")
    if not isinstance(asserts, list) or not [a for a in asserts if str(a).strip()]:
        raise ValueError(f"{ident} has no `asserts`; a scenario that asserts "
                         "nothing is not a test")
    # `requirements` and `gap` are required PRESENT, not required non-empty.
    # An omitted `requirements` is indistinguishable from a deliberate empty
    # one, and the empty one is a signal - defensive coverage nobody asked for.
    # An omitted `gap` silently defaults the scenario to "already built", which
    # is the one reading that makes a gap scenario disappear.
    if not isinstance(entry.get("requirements"), list):
        raise ValueError(f"{ident} has no `requirements` list; write [] to mean "
                         "'no requirement traceable', which is a signal, not an "
                         "omission")
    if not isinstance(entry.get("gap"), bool):
        raise ValueError(f"{ident} has `gap` {entry.get('gap')!r}; it must be "
                         "true or false, never absent - an absent gap flag "
                         "reads as already-built")


def missing_categories(scenarios):
    """Declared categories with no scenario — the coverage gaps.

    Computed against CATEGORIES, never against the categories the plan happens
    to use. A gap check over the observed set cannot report the category nobody
    wrote anything for, which is the largest gap it could have reported.
    """
    present = {s.get("category") for s in scenarios}
    return [c for c in CATEGORIES if c not in present]


def render_plan_section(scenarios) -> str:
    """The enumerated scenario block that replaces `Produce {count} scenarios`."""
    lines = [f"Produce exactly {len(scenarios)} scenarios, these and no others:",
             ""]
    for s in scenarios:
        reqs = [r for r in s.get("requirements", []) if str(r).strip()]
        head = f"{s['id']} [{s['bucket']} / {s['category']} / {s['priority']}]"
        if s.get("gap"):
            head += " GAP - the behaviour does not exist yet"
        lines.append(f"- {head}: {s['title']}")
        for assertion in s["asserts"]:
            lines.append(f"    Then: {assertion}")
        if reqs:
            lines.append(f"    Covers: {', '.join(reqs)}")
    gaps = [s for s in scenarios if s.get("gap")]
    if gaps:
        # Hard-wrapped to match the rest of the prompt. The two load-bearing
        # phrases are kept whole on their own lines so a substring check on
        # either does not break the next time this is reflowed.
        lines += [
            "",
            "A scenario marked GAP names behaviour that does not exist yet. It must",
            "assert the intended outcome and is EXPECTED TO FAIL",
            "until that behaviour is built. Never write it as a skipped or empty",
            "scenario: an all-skipped suite reports IsSuccess true, so a skipped",
            "scenario reports success for something nobody built.",
        ]
    return "\n".join(lines)


def compose_mentor_prompt(app, flow, scope, count, contract_path, plan=None) -> str:
    """Build the paste-ready Mentor prompt for a test module.

    The flow name is a REQUIRED argument, never a default: a template-cloned
    ODC app has no MainFlow (it has BusinessValuePerceptionTags, Common and
    ScreenTemplates), so a prompt that names one sends Mentor after a flow that
    does not exist. Resolve or create it first.

    With *plan*, the scenarios are enumerated from it and `count` is ignored -
    the plan decided how many there are, and a count that contradicts it would
    be a second, disagreeing answer to the same question.
    """
    contract = pathlib.Path(contract_path).read_text("utf-8")
    if "NotifyRunStepLogic" not in contract:
        raise ValueError(
            f"{contract_path} does not carry the measured element names; "
            "refusing to compose a prompt from an unrecognised contract")
    demand = (render_plan_section(plan) if plan
              else f"Produce {count} scenarios.")
    return f"""Build one BDD test suite in this application, testing {scope}.

Create a UI flow named {flow} if it does not exist, and build everything inside
it. Nothing you generate belongs in ScreenTemplates, which is a template source
only. Name the test module {app}Tests.

{demand}

For each scenario, create a web block in {flow} holding a
single BDDScenario, and FILL its named placeholders rather than replacing them:
ScenarioIdentifier, ScenarioDescription, TagsPlaceholder, SetupPlaceholder,
GivenPlaceholder, WhenPlaceholder, ThenPlaceholder, TeardownPlaceholder.

Put a BDDStep in the Given, When and Then placeholders and a SetupOrTeardown in
the setup and teardown placeholders. Wire every step through its mandatory
NotifyRunStepLogic block event. BDDStep has no input parameters and no
Destination property, so do not attempt to bind one, and there is no element
called SetupOrTeardownStep. Never leave a StepDescription empty.

Name the handlers a_Setup, b_Given, c_When, d_Then and e_Teardown, so
alphabetical order matches execution order. Give c_When, and only c_When, an
AllExceptions handler calling AssertFail with the exception message, so an
unexpected exception is a failed scenario rather than a crashed run.

Enumerate the exposed Service Actions in scope from inspection of the
application, not from prose. Do not report the suite complete until, for every
one of them: it has a dependency in the test module; a handler action calls that
exact Service Action; a BDDStep reaches that handler; and that BDDStep has a
non-empty StepDescription naming the behaviour. A dependency proxy with no wired
executable path is not coverage, and an empty step description is not a test.

Build the suite screen in {flow} on the LayoutBase block, give it a Text input
parameter named AuthToken, and pass that to LayoutBase's mandatory AuthToken
argument. Add the scenario blocks to it. Do NOT place a FinalResult on the
screen: LayoutBase already contains one, and a second makes the REST test runner
answer "Could not find tests in the screen". FinalResult must still be reachable
as a dependency of the test module, because LayoutBase renders it - a reference
the module needs, not a widget you place. A module missing that dependency does
not fail fast: the runner drives the screen and waits out
DefaultExecutionTimeout, shipped at 180000 ms.

Use only these assertions: Assert, AssertTrue, AssertFalse, AssertValue,
AssertFail. Do not use StepPhase or ApplicationTitle, which are not public. A
BDDStep may not be iterated by a ListRecords inside a BDDScenario, and a
data-driven scenario may not share a screen with a simple one.

Build everything through ODC Mentor against the app on the tenant: the model
stays server-side, and you must never download, export or edit an OML file
locally.

When you are done, list the exact name of every element you created and the flow
each one is in."""


def cmd_generate(args, echo=print) -> int:
    contract = (pathlib.Path(__file__).resolve().parent.parent
                / "references" / "component-contract.md")
    plan = None
    try:
        if getattr(args, "plan", None):
            plan = load_scenario_plan(args.plan)
        echo(compose_mentor_prompt(args.app, args.flow, args.scope,
                                   args.count, contract, plan=plan))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        echo(f"FAIL: {exc}")
        return 2
    if plan:
        gaps = missing_categories(plan)
        if gaps:
            echo("")
            echo("COVERAGE GAP - no scenario in: " + ", ".join(gaps))
    echo("")
    echo("Pass this to mentor_prompt on a loaded session, approving each edit.")
    echo("Then PUBLISH with mentor_publish - the")
    echo("publish is the commit, and Mentor's work is not in the app until it")
    echo("lands. Then run `verify` before trusting the summary.")
    return 0


def readback_gaps(expected, observed):
    """Elements Mentor claimed that the tenant does not report.

    An empty expectation list is itself a gap: it means the caller has nothing
    to check against, and "nothing to check" must never read as "verified".
    """
    wanted = [e.strip() for e in expected if e and e.strip()]
    if not wanted:
        return ["<no expected elements given>"]
    have = {o.strip() for o in observed if o and o.strip()}
    return sorted(name for name in wanted if name not in have)


def cmd_verify(args, echo=print) -> int:
    """Readback gate. Run it AFTER the publish, never instead of one.

    A Mentor turn lives in the session until published, so the tenant cannot
    report its elements before then. Run before the publish, this gate reports
    every element missing and that reading is wrong. Run after, it is the only
    check that settles whether the publish carried what the turn claimed.
    """
    try:
        expected = pathlib.Path(args.expect).read_text("utf-8").splitlines()
        observed = pathlib.Path(args.observed).read_text("utf-8").splitlines()
    except OSError as exc:
        echo(f"FAIL: {exc}")
        return 2
    gaps = readback_gaps(expected, observed)
    if not gaps:
        echo(f"OK: all {len([e for e in expected if e.strip()])} claimed element(s) "
             "are present on the tenant.")
        return 0
    echo("FAIL: Mentor claimed these and the tenant does not report them:")
    for name in gaps:
        echo(f"  - {name}")
    echo("")
    echo("If you have not published since the Mentor turn, publish first: the")
    echo("publish is the commit, and edits stay in the session until it lands.")
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odc_bdd_tests.py",
        description="Run OutSystems BDDFramework suites over the BDD Framework "
                    "API (ODC). The runner is synchronous: one GET returns the "
                    "complete result, so there is nothing to poll.")
    parser.add_argument("--hostname",
                        help="Runtime host, e.g. <tenant>-<env>.outsystems.app "
                             "(NOT the portal host, which 404s this path)")
    parser.add_argument("--auth-token",
                        help="Bearer token. Prefer the ODC_BDD_AUTH_TOKEN "
                             "environment variable; it is a shared secret.")
    parser.add_argument("--json", action="store_true",
                        help="Emit machine-readable JSON")
    # The spec lists --baseline among the globals without defining its
    # semantics. DECLARED here, IMPLEMENTED in Task 10 - which is the whole
    # point: a review found this flag parsing and comparing nothing. Do not
    # consider this task done on the strength of the parser accepting it.
    parser.add_argument("--baseline",
                        help="Earlier result JSON; exit 1 on any scenario that "
                             "passed there and does not pass now")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("preflight", help="Check the runner is installed and the token is set")
    sub.add_parser("list", help="Explain how to find suite screens (the API has no catalogue)")

    rp = sub.add_parser("run", help="Execute a suite and report per scenario")
    rp.add_argument("--module", required=True, help="TestESpace — the module holding the tests")
    rp.add_argument("--suite", required=True, help="TestSuiteScreen — the suite screen")
    rp.add_argument("--tags", help="ExecuteTags header: comma-separated tags to include")
    rp.add_argument("--skip-tags", help="SkipTags header: comma-separated tags to exclude")
    rp.add_argument("--timeout-ms", type=int,
                    help="Timeout header in milliseconds (server-side bound)")
    rp.add_argument("--dry-run", action="store_true", help="Print the request, call nothing")
    rp.add_argument("--out", help="Write the raw result JSON here")

    pp = sub.add_parser("report", help="Render a saved result; makes no tenant call")
    pp.add_argument("--out", required=True, help="Result file written by `run --out`")

    gp = sub.add_parser("generate", help="Compose the Mentor prompt for a test module")
    gp.add_argument("--app", required=True, help="App under test; the module is named <App>Tests")
    gp.add_argument("--flow", required=True,
                    help="UI flow to build into. RESOLVE IT FIRST - a template-cloned "
                         "ODC app has no MainFlow, and assuming one costs a whole run.")
    gp.add_argument("--scope", default="the application's most critical exposed Service Actions")
    gp.add_argument("--count", type=int, default=5,
                    help="How many scenarios. Ignored when --plan is given.")
    gp.add_argument("--plan",
                    help="Scenario plan JSON: which scenarios, not just how many. "
                         "See references/scenario-plan.md")

    vp = sub.add_parser("verify", help="Readback gate: did the published module gain what Mentor claimed?")
    vp.add_argument("--expect", required=True, help="File of element names Mentor said it created, one per line")
    vp.add_argument("--observed", required=True, help="File of element names the tenant reports, one per line")

    # `generate` and `verify` are NOT registered here. Each is added by the
    # task that defines its cmd_* function - Task 8 and Task 9 - so no
    # committed state ever exposes a verb that dispatches to an undefined
    # name. See the ordering note below.
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "preflight":
        return cmd_preflight(args)
    if args.command == "list":
        return cmd_list(args)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "report":
        return cmd_report(args)
    if args.command == "generate":
        return cmd_generate(args)
    if args.command == "verify":
        return cmd_verify(args)
    # Tasks 8 and 9 each append their own dispatch line here.
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
