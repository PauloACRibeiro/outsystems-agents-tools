#!/usr/bin/env python3
"""Scan patched OutSystems plans for generic execution handoff language.

With ``--source <plan>`` the scan additionally checks structural
non-regression: headings present in the plan the patch was made from and
absent from the patched file. One-directional -- additions are the point of
a patch -- and exempt for headings this same scanner orders removed.
"""

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


# --- structural non-regression (optional --source) --------------------------
#
# `SUMMARY_ONLY_PATTERNS` above catches a patched plan that *narrates* dropping
# content. It cannot catch one that drops a section silently, which is the
# failure SKILL.md step 6 spends three sentences forbidding. Comparing heading
# structure against the source plan catches both.
#
# Requirement IDs are deliberately NOT compared. `check_requirement_coverage.py`
# already computes `uncovered = defined - referenced` over the patched plan
# against the PRD, and SKILL.md steps 8-9 make that blocking; the only IDs a
# source-plan comparison would add are ones the PRD does not define -- dangling
# refs a correct patch is supposed to remove. The structural non-regression
# suite pins this by asserting requirement IDs are never compared here.

HEADING_RE = re.compile(r"^ {0,3}#{1,6}\s+(.+?)\s*$")
FENCE_RE = re.compile(r"^ {0,3}(?:```|~~~)")


def plan_headings(text: str) -> dict[str, str]:
    """Normalized heading key -> the heading text as first written.

    Level-insensitive: a section demoted from ``##`` to ``###`` moved, it did
    not vanish. Fenced code blocks are skipped so a `# comment` in a shell
    example is never read as a section.
    """
    headings: dict[str, str] = {}
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if not match:
            continue
        title = match.group(1).rstrip("#").strip()
        if not title:
            continue
        headings.setdefault(" ".join(title.split()).casefold(), title)
    return headings


def scanner_mandates_removal(heading: str) -> bool:
    """True when this scanner itself orders the heading gone.

    Derived from the scanner's own tables rather than restated, so a new row in
    either one cannot leave a correct patch failing the non-regression check.
    """
    if any(pattern in heading for pattern, _ in FORBIDDEN_PATTERNS):
        return True
    lowered = heading.lower()
    return any(pattern.lower() in lowered for pattern in ELEMENT_RECIPE_HEADINGS)


def structural_regressions(source_text: str, patched_text: str) -> list[str]:
    """Headings lost between the source plan and the patched plan."""
    patched = plan_headings(patched_text)
    return [
        title
        for key, title in plan_headings(source_text).items()
        if key not in patched and not scanner_mandates_removal(title)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="Patched plan file to scan")
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Plan the patch was made from; enables the structural "
        "non-regression check (headings present there and absent here)",
    )
    args = parser.parse_args(argv)

    if not args.plan.is_file():
        print(f"plan file not found: {args.plan}", file=sys.stderr)
        return 2
    if args.source is not None and not args.source.is_file():
        print(f"source plan file not found: {args.source}", file=sys.stderr)
        return 2

    findings = scan_path(args.plan)
    lost: list[str] = []
    if args.source is not None:
        lost = structural_regressions(
            args.source.read_text(encoding="utf-8"),
            args.plan.read_text(encoding="utf-8"),
        )

    if findings:
        print(f"forbidden generic execution handoff found in {args.plan}:")
        for line_no, pattern, reason, line in findings:
            print(f"- line {line_no}: {pattern} ({reason})")
            print(f"  {line}")
    if lost:
        print(
            f"structural non-regression FAILED: {len(lost)} heading(s) in "
            f"{args.source} are absent from {args.plan}:"
        )
        for title in lost:
            print(f"- {title}")
        print(
            "  write the full patched plan, or -- if the section is genuinely "
            "retired -- say so in the coverage review before dropping it"
        )
    elif args.source is not None:
        print(f"structural non-regression OK: {args.plan} keeps every heading in {args.source}")

    if findings or lost:
        return 1
    print(f"handoff scan OK: {args.plan}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
