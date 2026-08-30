#!/usr/bin/env python3
"""Check a captured OMI response transcript against an expected scorecard.

Deterministic checks only:
- required sections appear in the expected order
- Evidence Status section uses exactly one allowed label
- required phrases present, forbidden phrases absent

Exit 0 on pass, 1 on fail. --json prints a machine-readable report.
"""
import argparse
import json
import re
import sys
from pathlib import Path


def find_heading_position(text, heading):
    """Position of a heading matched as an exact full line, or -1 if absent."""
    match = re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE)
    return match.start() if match else -1


def find_section_positions(text, sections):
    positions = []
    for heading in sections:
        positions.append((heading, find_heading_position(text, heading)))
    return positions


def check(output_text, expected):
    failures = []

    positions = find_section_positions(output_text, expected["required_sections_in_order"])
    last = -1
    for heading, idx in positions:
        if idx == -1:
            failures.append({"check": "section_order", "detail": f"missing section {heading!r}"})
        elif idx < last:
            failures.append({"check": "section_order", "detail": f"section {heading!r} out of order"})
        else:
            last = idx

    if expected["allowed_evidence_labels"]:
        evidence_idx = find_heading_position(output_text, "### Evidence Status")
        evidence_block = output_text[evidence_idx:] if evidence_idx != -1 else ""
        next_heading = re.compile(r"^### ", re.MULTILINE).search(evidence_block, 1)
        if next_heading:
            evidence_block = evidence_block[: next_heading.start()]
        labels_found = [
            label for label in expected["allowed_evidence_labels"] if label in evidence_block
        ]
        # Longer labels can contain shorter ones as substrings; keep distinct matches
        # that are not substrings of another found label.
        distinct = [
            l for l in labels_found
            if not any(l != other and l in other for other in labels_found)
        ]
        if len(distinct) != 1:
            failures.append({
                "check": "evidence_label",
                "detail": f"expected exactly one allowed label, found {distinct!r}",
            })

    for phrase in expected.get("required_phrases", []):
        if phrase not in output_text:
            failures.append({"check": "required_phrase", "detail": f"missing {phrase!r}"})

    for phrase in expected.get("forbidden_phrases", []):
        # A forbidden phrase shaped like a heading (e.g. "### Studio-Native
        # Pseudocode") must be found as an ACTUAL heading line, not as a
        # raw substring - otherwise prose that names the heading only to
        # say it's absent ("no `### Placement` section here") would
        # false-fail. Non-heading forbidden phrases (tool names, claim
        # sentences) keep the plain substring check.
        if phrase.startswith("#"):
            found = find_heading_position(output_text, phrase) != -1
        else:
            found = phrase in output_text
        if found:
            failures.append({"check": "forbidden_phrase", "detail": f"found {phrase!r}"})

    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--expected", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    output_text = args.output.read_text(encoding="utf-8")
    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    failures = check(output_text, expected)
    verdict = "pass" if not failures else "fail"
    report = {"scenario": expected.get("scenario"), "verdict": verdict, "failures": failures}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['scenario']}: {verdict}")
        for f in failures:
            print(f"  - {f['check']}: {f['detail']}")
    return 0 if verdict == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
