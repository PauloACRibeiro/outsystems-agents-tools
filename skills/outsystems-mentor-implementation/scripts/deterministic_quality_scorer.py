#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


STALE_SCOPE_PATTERNS = [
    "Mentor Studio constraints used as source guardrails: web apps only",
    "web apps only",
    "supports web apps only",
]
NUMERIC_SCORE_KEYS = [
    "coverage_score",
    "dependency_order_score",
    "evidence_status_score",
    "safety_gate_score",
    "stale_scope_claim_score",
]
LIVE_MCP_KEYS = [
    "live_mcp_decision",
    "live_mcp_future_start",
    "live_mcp_mutation_denial",
]


# Mentor tool names that denote a tenant mutation. The session-based surface
# (measured live 2026-09-02) replaced mentor_start/publish_start with
# mentor_create_asset / mentor_prompt / mentor_publish; the old names stay so
# drafts written against the pre-2026-09 surface still score.
SESSION_MENTOR_MUTATION_TOOL_NAMES = (
    "mentor_create_asset",
    "mentor_prompt",
    "mentor_publish",
)
MENTOR_MUTATION_TOOL_NAMES = ("mentor_start",) + SESSION_MENTOR_MUTATION_TOOL_NAMES

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


def parse_source_requirements(text: str) -> dict[str, str]:
    requirements = {}
    for line in text.splitlines():
        match = re.match(r"^\s*-\s+(REQ-\d{3})\s+(.+?)\.\s*$", line)
        if match:
            requirements[match.group(1)] = match.group(2)
    return requirements


def parse_expected_manifest(text: str) -> tuple[dict[str, set[str]], list[str]]:
    expected_by_block = {f"DQ-B{index:02d}": set() for index in range(1, 8)}
    for line in text.splitlines():
        if " -> " not in line or "REQ-" not in line:
            continue

        requirement_id_match = re.search(r"(REQ-\d{3})", line)
        if not requirement_id_match:
            continue

        requirement_id = requirement_id_match.group(1)
        for block_id in re.findall(r"block (DQ-B\d{2}) ", line):
            expected_by_block.setdefault(block_id, set()).add(requirement_id)

    dependency_order = re.findall(r"^\s*-\s+block (DQ-B\d{2}) ", text, re.MULTILINE)
    return expected_by_block, dependency_order


def parse_generated_output(text: str) -> tuple[list[str], dict[str, dict[str, object]]]:
    blocks = []
    ordered_ids = []
    for chunk in re.split(r"(?=^## block DQ-B\d{2} )", text, flags=re.MULTILINE):
        if not chunk.startswith("## block DQ-B"):
            continue
        blocks.append(chunk)

    parsed_blocks = {}
    for block in blocks:
        block_id_match = re.search(r"^## block (DQ-B\d{2}) ", block)
        if not block_id_match:
            continue

        block_id = block_id_match.group(1)
        ordered_ids.append(block_id)
        coverage_line = next(
            (
                line
                for line in block.splitlines()
                if line.startswith("Requirements covered:")
            ),
            "",
        )
        evidence_line = next(
            (
                line
                for line in block.splitlines()
                if line.startswith("Evidence Status:")
            ),
            "",
        )
        parsed_blocks[block_id] = {
            "coverage_ids": set(re.findall(r"REQ-\d{3}", coverage_line)),
            "coverage_line": coverage_line,
            "evidence_line": evidence_line,
            "raw": block,
        }

    return ordered_ids, parsed_blocks


def parse_scorecard(text: str) -> dict[str, str]:
    return {
        key: value.strip()
        for key, value in re.findall(r"^-\s+([a-z_]+):\s*(.+?)\s*$", text, re.MULTILINE)
    }


def build_report(
    source_plan_text: str,
    expected_manifest_text: str,
    generated_output_text: str,
    expected_scorecard_text: str,
) -> dict[str, object]:
    requirements = parse_source_requirements(source_plan_text)
    expected_by_block, dependency_order = parse_expected_manifest(expected_manifest_text)
    ordered_ids, generated_blocks = parse_generated_output(generated_output_text)
    expected_scorecard = parse_scorecard(expected_scorecard_text)

    errors = []

    for requirement_id, phrase in requirements.items():
        if requirement_id not in generated_output_text:
            errors.append(f"{requirement_id} missing from generated output context")

    generated_by_block = {
        block_id: generated_blocks.get(block_id, {}).get("coverage_ids", set())
        for block_id in expected_by_block
    }
    for block_id in expected_by_block:
        expected_coverage = expected_by_block[block_id]
        actual_coverage = generated_by_block.get(block_id, set())
        if expected_coverage != actual_coverage:
            missing = sorted(expected_coverage - actual_coverage)
            extra = sorted(actual_coverage - expected_coverage)
            if missing:
                errors.append(
                    f"{block_id} missing requirement coverage: {', '.join(missing)}"
                )
            if extra:
                errors.append(
                    f"{block_id} has unexpected requirement coverage: {', '.join(extra)}"
                )

    if ordered_ids != dependency_order:
        errors.append(
            "dependency order mismatch: expected "
            f"{dependency_order}, got {ordered_ids}"
        )

    missing_evidence_blocks = [
        block_id
        for block_id in dependency_order
        if not generated_blocks.get(block_id, {}).get("evidence_line")
    ]
    if missing_evidence_blocks:
        errors.append(
            "blocks missing Evidence Status: " + ", ".join(missing_evidence_blocks)
        )

    normalized_output = normalize(generated_output_text)
    normalized_scorecard = normalize(expected_scorecard_text)
    stale_matches = []
    for pattern in STALE_SCOPE_PATTERNS:
        normalized_pattern = normalize(pattern)
        if normalized_pattern in normalized_output or normalized_pattern in normalized_scorecard:
            stale_matches.append(pattern)
    if stale_matches:
        errors.append(
            "stale Mentor Studio scope wording present: " + ", ".join(stale_matches)
        )

    live_mcp_missing = []
    for key in LIVE_MCP_KEYS:
        if key not in expected_scorecard:
            live_mcp_missing.append(key)
    if live_mcp_missing:
        errors.append("scorecard missing live MCP keys: " + ", ".join(live_mcp_missing))

    safety_checks = [
        "read-only first" in normalize(generated_blocks.get("DQ-B07", {}).get("evidence_line", "")),
        "no publish" in normalize(generated_blocks.get("DQ-B07", {}).get("evidence_line", "")),
        "deploy" in normalize(generated_blocks.get("DQ-B07", {}).get("evidence_line", "")),
        "rollback" in normalize(generated_blocks.get("DQ-B07", {}).get("evidence_line", "")),
        "app_create" in normalize(generated_blocks.get("DQ-B07", {}).get("evidence_line", "")),
        any(
            name in normalize(generated_blocks.get("DQ-B07", {}).get("evidence_line", ""))
            for name in MENTOR_MUTATION_TOOL_NAMES
        ),
        "read-only first" in normalize(expected_scorecard.get("live_mcp_future_start", "")),
        "app_info" in normalize(expected_scorecard.get("live_mcp_future_start", "")),
        "env_app" in normalize(expected_scorecard.get("live_mcp_future_start", "")),
        "search/list calls" in normalize(expected_scorecard.get("live_mcp_future_start", "")),
        "not needed" in normalize(expected_scorecard.get("live_mcp_decision", "")),
        "unresolved" in normalize(expected_scorecard.get("live_mcp_decision", "")),
        (
            "no app_create, mentor_start, publish_start, deploy_start, rollback, or mutating tool"
            in normalize(expected_scorecard.get("live_mcp_mutation_denial", ""))
            or any(
                name in normalize(expected_scorecard.get("live_mcp_mutation_denial", ""))
                for name in SESSION_MENTOR_MUTATION_TOOL_NAMES
            )
        ),
    ]

    scores = {
        "coverage_score": "100" if expected_by_block == generated_by_block else "0",
        "dependency_order_score": "100" if ordered_ids == dependency_order else "0",
        "evidence_status_score": "100" if not missing_evidence_blocks else "0",
        "safety_gate_score": "100" if all(safety_checks) else "0",
        "stale_scope_claim_score": "100" if not stale_matches else "0",
    }

    score_mismatches = {}
    for key in NUMERIC_SCORE_KEYS:
        expected_value = expected_scorecard.get(key)
        actual_value = scores[key]
        if expected_value != actual_value:
            score_mismatches[key] = {
                "expected": expected_value,
                "actual": actual_value,
            }

    return {
        "matches_expected_scorecard": not score_mismatches and not errors,
        "scores": scores,
        "score_mismatches": score_mismatches,
        "errors": errors,
        "expected_dependency_order": dependency_order,
        "actual_dependency_order": ordered_ids,
    }


def print_text_report(report: dict[str, object]) -> None:
    print(
        "deterministic quality scorer: "
        + ("PASS" if report["matches_expected_scorecard"] else "FAIL")
    )
    for key, value in report["scores"].items():
        print(f"{key}: {value}")
    if report["score_mismatches"]:
        print("score mismatches:")
        for key, mismatch in report["score_mismatches"].items():
            print(
                f"- {key}: expected {mismatch['expected']}, got {mismatch['actual']}"
            )
    if report["errors"]:
        print("errors:")
        for error in report["errors"]:
            print(f"- {error}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Score generated OMI deterministic-quality output against the current manifest and scorecard."
    )
    parser.add_argument("--source-plan", type=Path, required=True)
    parser.add_argument("--expected-blocks", type=Path, required=True)
    parser.add_argument("--generated-output", type=Path, required=True)
    parser.add_argument("--expected-scorecard", type=Path, required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    try:
        report = build_report(
            read(args.source_plan),
            read(args.expected_blocks),
            read(args.generated_output),
            read(args.expected_scorecard),
        )
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_report(report)

    return 0 if report["matches_expected_scorecard"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
