#!/usr/bin/env python3
"""OMI regression harness - deterministic checker over saved generation-pass artifacts.

A harness run has two parts (see the golden-scenarios suite's own README,
part of this project's local operator test suite, not shipped in this pack):
(a) an agent-driven GENERATION PASS captures one output artifact per scenario
    into an outputs/<run-label>/<id>.md file;
(b) this script deterministically CHECKS every saved artifact against its
    scorecard (an expected/<id>.json file), the route-mode contract lint, and
    the global shape checks, then reports pass/fail per scenario.

The scorecard-free shape checks (placeholder scan, paste-safe Mentor-prompt
structure, Plan Conversion Manifest shape) live in response_contract_lint.py
now, not here - this script imports them so the live self-check SKILL.md
requires and this test harness never drift apart. This script only adds the
scorecard-driven arguments (min_coverage_entries, min_mentor_prompt_blocks,
requires_manifest gating) response_contract_lint.py's generic defaults don't
know about.

Report-don't-mutate: this script never edits artifacts, scorecards, or skill
content. Reports contain no timestamps, durations, or absolute paths - two
runs over the same artifacts must produce byte-identical reports.

The JSON report's optional top-level "telemetry" key holds a Phase 2
polling-digest snapshot when --telemetry-digest is passed; omitted
otherwise. The snapshot is embedded verbatim (never fetched live inside
run()), so determinism holds: the same artifacts + the same digest file
produce the same report.

Exit 0 = every checked scenario passes; 1 = at least one failure;
2 = usage/config error (missing run directory, unknown scenario id).
"""
import argparse
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from golden_scenario_check import check  # noqa: E402
from response_contract_lint import (  # noqa: E402
    lint, scan_placeholders, check_manifest, check_prompt_structure)
from json_file_io import JSONFileError, read_json_file  # noqa: E402

DEFAULT_SUITE = SCRIPTS.parent / "tests" / "golden_scenarios"

# lint() (response_contract_lint.py) now also runs the generic shape checks
# internally. This harness reports those same checks under their own
# dedicated layers below with scorecard-aware parameters (min_coverage_entries,
# min_mentor_prompt_blocks) that lint()'s generic defaults don't know about -
# so any of these check names produced by lint()'s "contract-lint" layer would
# just be reporting the same defect twice. Filtered out here, not in lint()
# itself, so the real self-check path (response_contract_lint.py run directly,
# with no scorecard) still reports them.
GENERIC_CHECK_NAMES = {
    "placeholder_text", "template_literal",
    "manifest_marker", "coverage_entries", "dependency_order",
    "paste_safe_contents", "merged_prompt", "prompt_block_count",
}


def tag(layer, failures):
    return [{"layer": layer, **f} for f in failures]


def check_artifact(text, scorecard):
    """All deterministic layers for one artifact; returns tagged failures."""
    failures = []
    failures += tag("scorecard", check(text, scorecard))
    contract_lint_failures = lint(text, scorecard.get("lint_mode", scorecard["mode"]))
    contract_lint_failures = [
        f for f in contract_lint_failures if f["check"] not in GENERIC_CHECK_NAMES]
    failures += tag("contract-lint", contract_lint_failures)
    failures += tag("placeholder", scan_placeholders(text))
    if scorecard.get("requires_manifest"):
        failures += tag("manifest", check_manifest(
            text, scorecard.get("min_coverage_entries", 2)))
    failures += tag("prompt-structure", check_prompt_structure(
        text, scorecard.get("min_mentor_prompt_blocks", 0)))
    return failures


def run(suite_dir, run_label, scenario_ids=None, telemetry_digest=None):
    suite_dir = Path(suite_dir)
    expected_dir = suite_dir / "expected"
    outputs_dir = suite_dir / "outputs" / run_label
    all_ids = sorted(p.stem for p in expected_dir.glob("*.json"))
    if scenario_ids is None:
        scenario_ids = all_ids
    else:
        unknown = sorted(set(scenario_ids) - set(all_ids))
        if unknown:
            raise SystemExit(f"unknown scenario id(s): {', '.join(unknown)}")
        scenario_ids = sorted(scenario_ids)

    scenarios = []
    for sid in scenario_ids:
        scorecard = json.loads(
            (expected_dir / f"{sid}.json").read_text(encoding="utf-8"))
        artifact = outputs_dir / f"{sid}.md"
        if not artifact.is_file():
            failures = [{
                "layer": "artifact", "check": "artifact_exists",
                "detail": f"missing output artifact outputs/{run_label}/{sid}.md",
            }]
        else:
            failures = check_artifact(
                artifact.read_text(encoding="utf-8"), scorecard)
        scenarios.append({
            "scenario": sid,
            "verdict": "pass" if not failures else "fail",
            "failures": failures,
        })

    passed = sum(1 for s in scenarios if s["verdict"] == "pass")
    report = {
        "run_label": run_label,
        "scenarios": scenarios,
        "summary": {
            "total": len(scenarios),
            "passed": passed,
            "failed": len(scenarios) - passed,
        },
    }
    if telemetry_digest is not None:
        report["telemetry"] = telemetry_digest
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-label", required=True)
    parser.add_argument("--scenario", action="append", dest="scenarios",
                        metavar="ID", help="check only this scenario (repeatable)")
    parser.add_argument("--suite-dir", type=Path, default=DEFAULT_SUITE,
                        help="override the golden_scenarios directory (tests)")
    parser.add_argument("--json", type=Path, metavar="PATH",
                        help="also write the JSON report to PATH")
    parser.add_argument("--telemetry-digest", type=Path, metavar="PATH",
                        help="path to a Mode 3 'run.py summary' JSON snapshot to embed "
                             "verbatim under the report's telemetry key (omitted by default)")
    args = parser.parse_args()

    outputs_dir = args.suite_dir / "outputs" / args.run_label
    if not outputs_dir.is_dir():
        print(f"error: no such run directory: {outputs_dir}", file=sys.stderr)
        return 2
    try:
        telemetry_digest = None
        if args.telemetry_digest:
            try:
                telemetry_digest = read_json_file(args.telemetry_digest)
            except JSONFileError as exc:
                raise SystemExit(f"cannot read --telemetry-digest file: {exc}")
        report = run(args.suite_dir, args.run_label, args.scenarios, telemetry_digest=telemetry_digest)
    except SystemExit as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for scenario in report["scenarios"]:
        print(f"{scenario['scenario']}: {scenario['verdict']}")
        for failure in scenario["failures"]:
            print(f"  - [{failure['layer']}] {failure['check']}: {failure['detail']}")
    s = report["summary"]
    print(f"{s['passed']}/{s['total']} scenarios pass ({s['failed']} failed)")
    if args.json:
        args.json.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if s["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
