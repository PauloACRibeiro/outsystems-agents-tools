#!/usr/bin/env python3
"""Compute requirement coverage as a set difference over stable IDs.

The source file (PRD or the coverage review's Requirement Inventory) defines
the requirement ID universe; the plan file references IDs. Coverage is
mechanical: uncovered = defined - referenced, dangling = referenced - defined.
The verdict is computed, never hand-authored.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# BR- business rule, UC- use case, C- acceptance criterion. Plain form is
# PREFIX-NNN; an optional uppercase scope infix (BR-VISIT-001) is allowed.
ID_PATTERN = re.compile(r"\b(?:BR|UC|C)-(?:[A-Z][A-Z0-9]*-)*\d{3}\b")


def extract_ids(text: str) -> set[str]:
    return set(ID_PATTERN.findall(text))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        type=Path,
        help="File defining the requirement IDs (PRD or requirement inventory)",
    )
    parser.add_argument("plan", type=Path, help="Plan file to check for ID references")
    args = parser.parse_args(argv)

    for path in (args.source, args.plan):
        if not path.is_file():
            print(f"file not found: {path}", file=sys.stderr)
            return 2

    defined = extract_ids(args.source.read_text(encoding="utf-8"))
    referenced = extract_ids(args.plan.read_text(encoding="utf-8"))

    if not defined:
        print(
            f"no requirement IDs found in {args.source}; "
            "write the Requirement Inventory first",
            file=sys.stderr,
        )
        return 2

    uncovered = sorted(defined - referenced)
    dangling = sorted(referenced - defined)
    covered = len(defined) - len(uncovered)

    print(f"requirement coverage: {covered}/{len(defined)} defined IDs referenced by the plan")
    if uncovered:
        print("uncovered (defined in source, never referenced in plan):")
        for req_id in uncovered:
            print(f"- {req_id}")
    if dangling:
        print("dangling (referenced in plan, never defined in source):")
        for req_id in dangling:
            print(f"- {req_id}")

    if uncovered or dangling:
        print("coverage verdict: NOT READY")
        return 1

    print(f"coverage verdict: READY ({covered}/{len(defined)} covered, 0 dangling)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
