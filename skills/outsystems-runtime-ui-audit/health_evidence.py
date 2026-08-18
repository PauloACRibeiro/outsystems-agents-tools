#!/usr/bin/env python3
"""Render `odc app health --json` output as the report's runtime-health block.

P6 (dossier rev. 17): the block is telemetry evidence beside the 16-criterion
UI score, never part of it. Input is the AppHealthResponse JSON the internal
`odc` CLI emits (an internal OutSystems project, Analytics API v5). The
semantics this renderer enforces mechanically, so a report cannot misread them:

- an absent metric is the absence of a reading, never a zero;
- `noData.status == "undetermined"` renders as "no data" with the CLI's own
  reason — no app is ever listed as traffic-free off an unproven page;
- `appScore` is an Apdex-style latency score: the caveats print on every
  render, and a high score on thin traffic is flagged on the row itself.

Usage: health_evidence.py <app-health.json>   (or `-` for stdin)
Stdlib only; read-only; exits 2 on unusable input — including JSON that parses
but does not match the pinned response shape (fail closed on schema drift,
never a traceback and never a silently-accepted unknown state). Every
server-echoed string is markdown-escaped before it reaches the report.
"""

import json
import math
import re
import sys

LOW_TRAFFIC_REQUESTS = 100  # below this, flag appScore inline

# (json field, label, formatter) — every name the CLI's pinned
# APP_METRIC_ALLOW_LIST accepts, so no requested-and-echoed metric can be
# silently dropped from a row. Display order: score, volume, errors,
# latency percentiles, users, last error.
ROW_METRICS = (
    ("appScore", "appScore", lambda v: fmt_num(v)),
    ("requests", "requests", lambda v: fmt_num(v)),
    ("requestsPerSecond", "req/s", lambda v: fmt_num(v)),
    ("requestsPerMinute", "req/min", lambda v: fmt_num(v)),
    ("requestsPerHour", "req/h", lambda v: fmt_num(v)),
    ("requestsPerDay", "req/day", lambda v: fmt_num(v)),
    ("errors", "errors", lambda v: fmt_num(v)),
    ("errorsPerSecond", "err/s", lambda v: fmt_num(v)),
    ("errorsPerMinute", "err/min", lambda v: fmt_num(v)),
    ("errorsPerHour", "err/h", lambda v: fmt_num(v)),
    ("errorsPerDay", "err/day", lambda v: fmt_num(v)),
    ("errorPercent", "errors%", lambda v: f"{fmt_num(v)}%"),
    ("responseTimeP50", "P50", lambda v: f"{fmt_num(v)}ms"),
    ("responseTimeP75", "P75", lambda v: f"{fmt_num(v)}ms"),
    ("responseTimeP90", "P90", lambda v: f"{fmt_num(v)}ms"),
    ("responseTimeP95", "P95", lambda v: f"{fmt_num(v)}ms"),
    ("responseTimeP99", "P99", lambda v: f"{fmt_num(v)}ms"),
    ("responseTimeP100", "P100", lambda v: f"{fmt_num(v)}ms"),
    ("uniqueUsers", "users", lambda v: fmt_num(v)),
    ("authenticatedUsers", "auth users", lambda v: fmt_num(v)),
    ("anonymousUsers", "anon users", lambda v: fmt_num(v)),
    ("lastErrorOccurred", "last error", str),
)

# Metric names the CLI accepts (its APP_METRIC_ALLOW_LIST); a request echo
# outside this set is schema drift, not a rendering choice.
KNOWN_METRICS = frozenset(f for f, _, _ in ROW_METRICS)

CAVEATS = (
    "`appScore` is an Apdex-style LATENCY score (0-100), not a health verdict: "
    "it says nothing about failures, and an app with no traffic scores 100.",
    "An absent metric is the absence of a reading, never a zero.",
)


_MD_SPECIALS = re.compile(r"([\\`*_\[\]|])")


def sanitize(value):
    """Neutralize server-echoed text: one line, no live markdown or HTML."""
    flat = re.sub(r"\s+", " ", str(value)).strip()
    escaped = _MD_SPECIALS.sub(r"\\\1", flat)
    return escaped.replace("<", "&lt;").replace(">", "&gt;")


# Counter fields are i64 in the pinned clean schema (the CLI integralizes
# the trace-derived wire floats); everything else numeric stays f64.
COUNT_ROW_FIELDS = (
    "requests",
    "errors",
    "uniqueUsers",
    "authenticatedUsers",
    "anonymousUsers",
)
NUMERIC_ROW_FIELDS = tuple(
    f
    for f, _, _ in ROW_METRICS
    if f != "lastErrorOccurred" and f not in COUNT_ROW_FIELDS
)
STRING_ROW_FIELDS = ("applicationKey", "lastErrorOccurred")


def _is_num(v):
    return (
        isinstance(v, (int, float))
        and not isinstance(v, bool)
        and math.isfinite(v)
    )


U64_MAX = 2**64 - 1
U32_MAX = 2**32 - 1
I64_MAX = 2**63 - 1


def _is_uint(v, upper):
    return isinstance(v, int) and not isinstance(v, bool) and 0 <= v <= upper


def _opt_str(container, field):
    return container.get(field) is None or isinstance(container[field], str)


def _require_str(container, field, where):
    if not isinstance(container.get(field), str):
        raise ValueError(f"{where} {field} must be a string and is required")


def validate(data):
    """Raise ValueError on any departure from the pinned AppHealthResponse.

    Required response fields, u64/u32 counters as non-negative integers, and
    required nested UnresolvedApp/NoDataApp fields are all enforced; only the
    fields the Rust schema marks optional (row metrics, applicationKey,
    noData, metricsAdvisory) may be absent.
    """
    results = data.get("results")
    if not isinstance(results, list):
        raise ValueError("results must be a list and is required")
    for row in results:
        if not isinstance(row, dict):
            raise ValueError("each results row must be an object")
        _require_str(row, "applicationName", "row")
        for field in NUMERIC_ROW_FIELDS:
            if row.get(field) is not None and not _is_num(row[field]):
                raise ValueError(f"row field {field} must be a number")
        for field in COUNT_ROW_FIELDS:
            if row.get(field) is not None and not _is_uint(row[field], I64_MAX):
                raise ValueError(
                    f"row field {field} must be a non-negative i64 integer"
                )
        for field in STRING_ROW_FIELDS:
            if row.get(field) is not None and not isinstance(row[field], str):
                raise ValueError(f"row field {field} must be a string")
    metrics = data.get("metrics")
    if not isinstance(metrics, list) or not all(
        isinstance(m, str) for m in metrics
    ):
        raise ValueError("metrics must be a list of strings and is required")
    unknown = sorted(set(metrics) - KNOWN_METRICS)
    if unknown:
        raise ValueError(f"unknown metric names: {', '.join(unknown)}")
    for field in ("stageKey", "since", "to"):
        _require_str(data, field, "response")
    for field, upper, wire_type in (
        ("total", U64_MAX, "u64"),
        ("nextPageOffset", U32_MAX, "u32"),
    ):
        if not _is_uint(data.get(field), upper):
            raise ValueError(
                f"{field} must be a {wire_type} integer and is required"
            )
    resolved = data.get("resolvedApps")
    if not isinstance(resolved, list) or not all(
        isinstance(k, str) for k in resolved
    ):
        raise ValueError("resolvedApps must be a list of strings and is required")
    no_data = data.get("noData")
    if no_data is not None:
        if not isinstance(no_data, dict):
            raise ValueError("noData must be an object")
        status = no_data.get("status")
        if status == "determined":
            apps = no_data.get("apps")
            if not isinstance(apps, list) or not all(
                isinstance(a, dict) for a in apps
            ):
                raise ValueError("noData.apps must be a list of objects")
            for app in apps:
                for field in ("input", "applicationKey"):
                    _require_str(app, field, "noData app")
        elif status == "undetermined":
            if not isinstance(no_data.get("reason"), str):
                raise ValueError("undetermined noData must carry a string reason")
        else:
            raise ValueError(f"unknown noData.status: {status!r}")
    unresolved = data.get("unresolved")
    if not isinstance(unresolved, list) or not all(
        isinstance(u, dict) for u in unresolved
    ):
        raise ValueError("unresolved must be a list of objects and is required")
    for item in unresolved:
        for field in ("input", "reason"):
            _require_str(item, field, "unresolved")
    advisory = data.get("metricsAdvisory")
    if advisory is not None and not isinstance(advisory, str):
        raise ValueError("metricsAdvisory must be a string")


def fmt_num(v):
    if isinstance(v, float) and v == int(v):
        return str(int(v))
    return str(v)


def render_row(row, requested):
    name = row.get("applicationName") or row.get("applicationKey") or "(unnamed)"
    parts = []
    for field, label, fmt in ROW_METRICS:
        if field not in requested:
            continue
        value = row.get(field)
        if value is None:
            parts.append(f"{label}: no reading")
            continue
        rendered = f"{label}: {sanitize(fmt(value))}"
        if field == "appScore":
            requests = row.get("requests")
            if requests is not None and requests < LOW_TRAFFIC_REQUESTS:
                rendered += " (low traffic — score inflated, see caveats)"
        parts.append(rendered)
    return f"- **{sanitize(name)}** — " + " · ".join(parts)


def render(data):
    lines = [
        "## Runtime health (telemetry — does not affect the UI score)",
        "",
        f"Source: internal `odc app health` (Analytics API v5) · "
        f"stage `{sanitize(data.get('stageKey', '?'))}` · "
        f"window {sanitize(data.get('since', '?'))} → "
        f"{sanitize(data.get('to', '?'))}",
        "",
    ]

    requested = set(data.get("metrics", ()))
    results = data.get("results", [])
    if results:
        lines.extend(render_row(row, requested) for row in results)
    else:
        lines.append("- No app returned a health row in this window.")

    advisory = data.get("metricsAdvisory")
    if advisory:
        lines.extend(["", f"> {sanitize(advisory)}"])

    no_data = data.get("noData")
    if no_data is not None:
        status = no_data.get("status")
        if status == "undetermined":
            reason = sanitize(no_data.get("reason", "(no reason given)"))
            lines.extend(
                [
                    "",
                    f"No-traffic determination: **undetermined** — {reason}. "
                    "Render this as *no data*: no app's absence from the rows "
                    "above means anything.",
                ]
            )
        elif status == "determined":
            apps = no_data.get("apps", [])
            if apps:
                lines.append("")
                for app in apps:
                    label = app.get("input") or app.get("applicationKey", "?")
                    lines.append(
                        f"- **{sanitize(label)}** — no traffic in this "
                        "environment in the window (no reading; an absent row "
                        "is not a clean bill of health — this also covers an "
                        "app never deployed to this environment, and for a "
                        "UUID a key this tenant does not have)."
                    )

    unresolved = data.get("unresolved", [])
    if unresolved:
        lines.append("")
        for item in unresolved:
            lines.append(
                f"- Unresolved input **{sanitize(item.get('input', '?'))}**: "
                f"{sanitize(item.get('reason', 'no reason given'))} — the rows "
                "above cover fewer apps than were asked for."
            )

    lines.extend(["", "Caveats (always apply):"])
    lines.extend(f"- {caveat}" for caveat in CAVEATS)
    lines.append("")
    return "\n".join(lines)


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-2].strip(), file=sys.stderr)
        return 2
    try:
        raw = (
            sys.stdin.read()
            if argv[1] == "-"
            else open(argv[1], encoding="utf-8").read()
        )
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"unusable input: {exc}", file=sys.stderr)
        return 2
    if not isinstance(data, dict):
        print("unusable input: expected a JSON object", file=sys.stderr)
        return 2
    try:
        validate(data)
    except ValueError as exc:
        print(f"unusable input: {exc}", file=sys.stderr)
        return 2
    print(render(data))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
