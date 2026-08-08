#!/usr/bin/env python3
"""Per-session telemetry + OMI-link report over polling-behavior session data.

Reads (a) each session directory under a polling-behavior cache's sessions/
folder directly, for per-session rows (runId, app, status, wall time, and
whether an omi-link.json correlation file exists for it), and (b) a Mode 3
digest JSON (produced by that skill's own `run.py summary` command) for
aggregate figures (sessionCount, succeededCount, trend) - passed through
verbatim, never recomputed here.

MIN_SESSIONS_REQUIRED mirrors the polling skill's own config default for
"minimum succeeded sessions before a signal can fire." The digest JSON does
not expose that value itself, so it is a documented local constant here, not
read live from another repo's config file.

Exit 0 on a successful report - this is a reporting tool, not a pass/fail
gate over the telemetry itself. Exit 2 on a usage/config error (missing or
malformed --digest file, missing --cache directory).
"""
import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from json_file_io import JSONFileError, read_json_file  # noqa: E402

# Mirrors the polling-behavior skill's config.json feedback.minSessionsRequired
# default (5). Not read live from that repo; update by hand if that default
# ever changes.
MIN_SESSIONS_REQUIRED = 5


def session_rows(sessions_dir):
    rows = []
    sessions_dir = Path(sessions_dir)
    if not sessions_dir.is_dir():
        return rows
    for session_dir in sorted(sessions_dir.iterdir()):
        if not session_dir.is_dir():
            continue
        meta_path = session_dir / "meta.json"
        if not meta_path.is_file():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        start = meta.get("startTime")
        end = meta.get("endTime")
        wall_seconds = (end - start) if (start is not None and end is not None) else None
        link_path = session_dir / "omi-link.json"
        linked_scenario = None
        if link_path.is_file():
            link = json.loads(link_path.read_text(encoding="utf-8"))
            linked_scenario = link.get("omi_scenario")
        rows.append({
            "runId": meta.get("runId", session_dir.name),
            "appName": meta.get("appName") or meta.get("appKey") or "unknown",
            "status": meta.get("status", "unknown"),
            "wallSeconds": wall_seconds,
            "linkedScenario": linked_scenario,
        })
    return rows


def build_report(digest, sessions_dir):
    rows = session_rows(sessions_dir)
    succeeded_count = digest.get("succeededCount", 0)
    return {
        "sessionCount": digest.get("sessionCount", 0),
        "succeededCount": succeeded_count,
        "failedCount": digest.get("failedCount", 0),
        "cancelledCount": digest.get("cancelledCount", 0),
        "trend": digest.get("trend"),
        "belowMinSessionsRequired": succeeded_count < MIN_SESSIONS_REQUIRED,
        "minSessionsRequired": MIN_SESSIONS_REQUIRED,
        "sessions": rows,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--digest", required=True, type=Path,
                        help="path to a Mode 3 'run.py summary' JSON output")
    parser.add_argument("--cache", required=True, type=Path,
                        help="path to the polling-behavior cache dir (contains sessions/)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    try:
        report = _build_report_from_args(args)
    except SystemExit as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['sessionCount']} sessions total "
              f"({report['succeededCount']} succeeded, {report['failedCount']} failed, "
              f"{report['cancelledCount']} cancelled)")
        if report["belowMinSessionsRequired"]:
            print(f"Below minSessionsRequired ({report['minSessionsRequired']}) - "
                  "no trend/signal claim should be made from this data yet.")
        for row in report["sessions"]:
            link_note = row["linkedScenario"] or "unlinked"
            print(f"  {row['runId']}  {row['appName']}  {row['status']}  "
                  f"{row['wallSeconds']}s  [{link_note}]")
    return 0


def _build_report_from_args(args):
    if not args.cache.is_dir():
        raise SystemExit(f"no such cache directory: {args.cache}")
    try:
        digest = read_json_file(args.digest)
    except JSONFileError as exc:
        raise SystemExit(f"cannot read --digest file: {exc}")
    return build_report(digest, args.cache / "sessions")


if __name__ == "__main__":
    sys.exit(main())
