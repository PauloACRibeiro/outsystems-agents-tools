#!/usr/bin/env python3
"""Scan patched OutSystems plans for generic execution handoff language."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FORBIDDEN_PATTERNS: tuple[tuple[str, str], ...] = (
    ("superpowers:subagent-driven-development", "generic subagent execution skill"),
    ("superpowers:executing-plans", "generic inline execution skill"),
    ("Subagent-Driven", "generic subagent execution option"),
    ("Inline Execution", "generic inline execution option"),
    ("Two execution options", "generic Superpowers execution handoff"),
    ("REQUIRED SUB-SKILL", "generic required execution sub-skill header"),
)

SUMMARY_ONLY_PATTERNS: tuple[str, ...] = (
    "All content is in",
    "patches applied in place",
)

# Section names forbidden in capability-level plans. Matched case-insensitively,
# and only on markdown heading lines so that prose references to downstream
# conversion stay legal.
ELEMENT_RECIPE_HEADINGS: tuple[str, ...] = (
    "ODC Element Map",
    "ODC Elements",
    "Business Logic",
    "Screen Aggregates",
    "Studio-Native Pseudocode",
    "Data Model Pseudocode",
    "Server Action Pseudocode",
    "Client Action Pseudocode",
    "Screen And UI Pseudocode",
    "Screen/UI Pseudocode",
    "Navigation Pseudocode",
    "Verification Pseudocode",
)

# An ODC entity auto-generates entity actions named with these prefixes plus
# the entity's own name. A custom server action given the same name collides
# with one: the first live colleague run (2026-08-09) lost `CreateBooking`
# beside entity `Booking` to a session that reported change_applied with two
# retries and zero errors and created nothing. The same prompt under the name
# `BookRoom` landed first time.
COLLISION_PREFIXES = ("Create", "Update", "Delete", "Get")
COLLISION_NAME_RE = re.compile(r"\b(" + "|".join(COLLISION_PREFIXES) + r")([A-Z][A-Za-z0-9]*)\b")
ENTITY_LINE_RE = re.compile(r"\bentit(?:y|ies)\b", re.IGNORECASE)
PASCAL_TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9]*\b")


def declared_entities(text: str) -> set[str]:
    """Names the plan itself calls entities.

    Deliberately precise rather than exhaustive: only the whole remainder of a
    prefixed name is ever tested against this set, so a plan that never uses
    the word "entity" yields no findings instead of false ones.
    """
    names: set[str] = set()
    for line in text.splitlines():
        if ENTITY_LINE_RE.search(line):
            names.update(PASCAL_TOKEN_RE.findall(line))
    return names


def scan_text(text: str) -> list[tuple[int, str, str, str]]:
    findings: list[tuple[int, str, str, str]] = []
    entities = declared_entities(text)
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in COLLISION_NAME_RE.finditer(line):
            entity = match.group(2)
            if entity not in entities:
                continue
            findings.append(
                (
                    line_no,
                    match.group(0),
                    f"collides with the auto-generated entity action of `{entity}`; "
                    "rename the planned action to a verb phrase",
                    line.strip(),
                )
            )
        for pattern, reason in FORBIDDEN_PATTERNS:
            if pattern in line:
                findings.append((line_no, pattern, reason, line.strip()))
        for pattern in SUMMARY_ONLY_PATTERNS:
            if pattern in line:
                findings.append(
                    (
                        line_no,
                        pattern,
                        "summary-only patched artifact; write the full patched plan here",
                        line.strip(),
                    )
                )
        if line.lstrip().startswith("#"):
            lowered = line.lower()
            for pattern in ELEMENT_RECIPE_HEADINGS:
                if pattern.lower() in lowered:
                    findings.append(
                        (
                            line_no,
                            pattern,
                            "ODC element recipe section; keep the plan at capability level",
                            line.strip(),
                        )
                    )
    return findings


def scan_path(path: Path) -> list[tuple[int, str, str, str]]:
    return scan_text(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Patched plan file to scan")
    args = parser.parse_args(argv)

    if not args.plan.is_file():
        print(f"plan file not found: {args.plan}", file=sys.stderr)
        return 2

    findings = scan_path(args.plan)
    if not findings:
        print(f"handoff scan OK: {args.plan}")
        return 0

    print(f"forbidden generic execution handoff found in {args.plan}:")
    for line_no, pattern, reason, line in findings:
        print(f"- line {line_no}: {pattern} ({reason})")
        print(f"  {line}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
