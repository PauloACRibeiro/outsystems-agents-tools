#!/usr/bin/env python3
"""Compute requirement coverage as a set difference over stable IDs.

The source file (PRD or the coverage review's Requirement Inventory) defines
the requirement ID universe; the plan file references IDs. Coverage is
mechanical: uncovered = defined - referenced, dangling = referenced - defined.
The verdict is computed, never hand-authored.

When the plan carries a ``## Traceability`` table (| Story | Requirements |
Design |), the checker additionally computes the story join: every defined
US- story must own exactly one well-formed row, every row's story is defined,
every defined requirement appears in at least one row's Requirements cell,
and every row carries a design reference (``blueprint:<Screen>`` /
``inventory:<Screen>``, or an explicit ``none``). The table region is excised
from the inline-citation scan, so a table-only mention never satisfies the
inline coverage gate. Plans without the table (pre-traceability format) keep
the exact citation-only behavior — US- tokens excluded — with a note.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# BR- business rule, UC- use case, C- acceptance criterion. Plain form is
# PREFIX-NNN; an optional uppercase scope infix (BR-VISIT-001) is allowed.
# Canonical grammar: PREFIX-NNN with dash-separated scope infixes (UC-A-001).
# The fused scope form (UC-A01, C-A17) is also accepted since 2026-08-09: the
# admin-area build's PRD used it and scored 0/N coverage on a complete plan
# because this pattern could not see its IDs at all (AB-02).
# Recommended scope infixes namespace rules per surface: BR-DM- data model,
# BR-SC- screens, BR-SEC- security/roles, BR-INT- integrations, BR-WF-
# workflows (adopted 2026-08-13 from the upstream BR-BP-/BR-SP- pattern).
ID_PATTERN = re.compile(r"\b(?:BR|UC|C)-(?:(?:[A-Z][A-Z0-9]*-)*\d{3}|[A-Z]+\d{2,3})\b")

# US- user stories are unpadded (US-1), matching the upstream convention.
# Stories participate only when the plan carries a Traceability table; a
# legacy no-table plan keeps the exact pre-traceability ID universe so its
# verdict cannot change. T-nnn task stamps are deliberately never matched:
# they are plan-internal and must not read as dangling references.
STORY_PATTERN = re.compile(r"\bUS-\d{1,3}\b")

# A design cell is comma-separated items, each an artifact ref into one of
# the loop's design artifacts (keyed by screens[].name, which may contain
# spaces) — or the whole cell is an explicit "none" (a story composed from
# tokens). An item's screen name is everything after the colon, verbatim.
DESIGN_ITEM_PATTERN = re.compile(r"(blueprint|inventory):\s*(\S.*)")
DESIGN_NONE = {"none", "-", "--", "—", "–"}

TRACEABILITY_HEADING = re.compile(r"^#{2,3}\s+Traceability\s*$", re.MULTILINE)


def extract_traceability_table(plan_text: str):
    """Locate and parse the plan's ## Traceability table.

    Returns (rows, malformed, table_span) where rows is a list of parsed row
    dicts, malformed is a list of raw lines that look like rows but do not
    parse, and table_span is the (start, end) character span of the table
    block so it can be excised from the inline-citation scan. Returns
    (None, [], None) when the plan has no Traceability section.
    """
    match = TRACEABILITY_HEADING.search(plan_text)
    if not match:
        return None, [], None

    rows: list[dict] = []
    malformed: list[str] = []
    offset = match.end()
    table_start = None
    table_end = offset
    started = False
    for line in plan_text[offset:].splitlines(keepends=True):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if started:
                break
            offset += len(line)
            table_end = offset
            continue
        if not stripped.startswith("|"):
            break
        if table_start is None:
            table_start = offset
        started = True
        offset += len(line)
        table_end = offset
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and (
            cells[0].lower() == "story" or set(cells[0]) <= {"-", ":", " "}
        ):
            continue
        if len(cells) != 3:
            malformed.append(stripped)
            continue
        rows.append(
            {"story": cells[0], "requirements": cells[1], "design": cells[2]}
        )

    span = (match.start(), table_end) if table_start is not None else (
        match.start(),
        table_end,
    )
    return rows, malformed, span


def load_screen_names(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        screen.get("name", "")
        for screen in data.get("screens", [])
        if isinstance(screen, dict)
    }


def parse_design_cell(cell: str) -> tuple[list[tuple[str, str]] | None, str | None]:
    """Return (refs, error). refs is [] for an explicit none-cell."""
    if cell.lower() in DESIGN_NONE:
        return [], None
    items = [item.strip() for item in cell.split(",")]
    if not any(items):
        return None, "empty design cell"
    refs: list[tuple[str, str]] = []
    for item in items:
        if not item:
            continue
        m = DESIGN_ITEM_PATTERN.fullmatch(item)
        if not m:
            return None, f"unparseable design item '{item}'"
        refs.append((m.group(1), m.group(2).strip()))
    return refs, None


def check_traceability(
    rows: list[dict],
    malformed: list[str],
    defined_stories: set[str],
    defined_requirements: set[str],
    artifacts: dict[str, Path | None],
) -> tuple[list[str], set[str]]:
    """Return (failures, mapped_requirements)."""
    failures: list[str] = []
    for line in malformed:
        failures.append(f"malformed traceability row: {line}")

    seen_stories: set[str] = set()
    mapped_requirements: set[str] = set()
    screen_names_cache: dict[str, set[str]] = {}
    for n, row in enumerate(rows, 1):
        story_cell = row["story"].strip().strip("`")
        if not STORY_PATTERN.fullmatch(story_cell):
            failures.append(
                f"traceability row {n}: story cell '{row['story']}' is not a "
                "single US-n id (one story per row)"
            )
            continue
        if story_cell in seen_stories:
            failures.append(
                f"traceability row {n}: duplicate story row for {story_cell}"
            )
            continue
        seen_stories.add(story_cell)
        if story_cell not in defined_stories:
            failures.append(
                f"story {story_cell} in traceability row {n} is not defined "
                "in the source"
            )

        row_requirements = set(ID_PATTERN.findall(row["requirements"]))
        if not row_requirements:
            failures.append(
                f"traceability row {n} ({story_cell}): Requirements cell "
                "cites no requirement IDs"
            )
        # The table is excised from the inline-citation scan, so an ID that
        # appears only in a row can never surface as dangling there — reject
        # it here or it fails open (Codex re-review, AH-2026-08-13-001).
        for req_id in sorted(row_requirements - defined_requirements):
            failures.append(
                f"traceability row {n} ({story_cell}): {req_id} is not "
                "defined in the source"
            )
        mapped_requirements |= row_requirements & defined_requirements

        refs, error = parse_design_cell(row["design"])
        if error is not None or refs is None:
            failures.append(
                f"traceability row {n} ({story_cell}): {error or 'no design reference'} "
                "(use blueprint:<Screen>, inventory:<Screen>, or an explicit 'none')"
            )
            continue
        for kind, screen in refs:
            artifact = artifacts.get(kind)
            if artifact is None:
                continue
            key = str(artifact)
            if key not in screen_names_cache:
                screen_names_cache[key] = load_screen_names(artifact)
            if screen not in screen_names_cache[key]:
                failures.append(
                    f"traceability row {n}: {kind}:{screen} names no screen "
                    f"in {artifact} (screens[].name)"
                )

    for story in sorted(defined_stories - seen_stories):
        failures.append(f"story {story} is defined but has no traceability row")
    unmapped = sorted(defined_requirements - mapped_requirements)
    if unmapped:
        failures.append("unmapped (defined in source, in no traceability row):")
        failures.extend(f"- {req_id}" for req_id in unmapped)
    return failures, mapped_requirements


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source",
        type=Path,
        help="File defining the requirement IDs (PRD or requirement inventory)",
    )
    parser.add_argument("plan", type=Path, help="Plan file to check for ID references")
    parser.add_argument(
        "--blueprint",
        type=Path,
        default=None,
        help="enriched blueprint.json to resolve blueprint:<Screen> refs against",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=None,
        help="screen-inventory.json to resolve inventory:<Screen> refs against",
    )
    args = parser.parse_args(argv)

    paths = [args.source, args.plan]
    paths += [p for p in (args.blueprint, args.inventory) if p is not None]
    for path in paths:
        if not path.is_file():
            print(f"file not found: {path}", file=sys.stderr)
            return 2

    plan_text = args.plan.read_text(encoding="utf-8")
    source_text = args.source.read_text(encoding="utf-8")

    rows, malformed, table_span = extract_traceability_table(plan_text)
    has_table = rows is not None

    # The ID universe depends on the plan format: a legacy no-table plan
    # keeps the exact pre-traceability universe (no US- stories), so its
    # verdict cannot change. The table block never counts as inline citation.
    inline_text = plan_text
    if table_span is not None:
        inline_text = plan_text[: table_span[0]] + plan_text[table_span[1] :]

    defined_requirements = set(ID_PATTERN.findall(source_text))
    referenced = set(ID_PATTERN.findall(inline_text))
    defined_stories: set[str] = set()
    if has_table:
        defined_stories = set(STORY_PATTERN.findall(source_text))

    defined = defined_requirements | defined_stories
    if not defined:
        print(
            f"no requirement IDs found in {args.source}; "
            "write the Requirement Inventory first",
            file=sys.stderr,
        )
        return 2

    uncovered = sorted(defined_requirements - referenced)
    dangling = sorted(referenced - defined_requirements)
    covered = len(defined_requirements) - len(uncovered)

    print(
        f"requirement coverage: {covered}/{len(defined_requirements)} "
        "defined IDs referenced by the plan"
    )
    if uncovered:
        print("uncovered (defined in source, never referenced in plan):")
        for req_id in uncovered:
            print(f"- {req_id}")
    if dangling:
        print("dangling (referenced in plan, never defined in source):")
        for req_id in dangling:
            print(f"- {req_id}")

    trace_failures: list[str] = []
    if not has_table:
        print(
            "note: no Traceability table found (pre-traceability plan format); "
            "story-to-requirement mapping not checked"
        )
    else:
        trace_failures, mapped = check_traceability(
            rows,
            malformed,
            defined_stories,
            defined_requirements,
            {"blueprint": args.blueprint, "inventory": args.inventory},
        )
        print(
            f"traceability: {len(mapped & defined_requirements)}/"
            f"{len(defined_requirements)} requirements mapped to stories "
            f"across {len(rows)} rows"
        )
        for line in trace_failures:
            print(line)

    if uncovered or dangling or trace_failures:
        print("coverage verdict: NOT READY")
        return 1

    print(
        f"coverage verdict: READY ({covered}/{len(defined_requirements)} "
        "covered, 0 dangling)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
