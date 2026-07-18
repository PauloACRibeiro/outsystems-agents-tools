#!/usr/bin/env python3
"""Scan patched OutSystems plans for generic execution handoff language."""

from __future__ import annotations

import argparse
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


def scan_text(text: str) -> list[tuple[int, str, str, str]]:
    findings: list[tuple[int, str, str, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
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
