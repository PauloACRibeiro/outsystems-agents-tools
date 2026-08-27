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

A design ref is only resolved when its artifact is on the command line. Until
2026-08-20 a ref whose artifact was absent was skipped in silence and the run
still printed READY, so ``blueprint:AnyStringAtAll`` passed unexamined — a
check is never *skipped* when its input is missing. Unresolved refs are now
named, counted, and told which flag would resolve them; ``--strict`` makes
them a failure. The default stays a note so existing runs keep their verdict,
but ``check_handoff_gate.py`` always passes ``--strict``: the gate is where
READY is decided, its own doctrine is that no clause is ever skipped, and its
sanctioned exit from a failing clause is a recorded waiver, not silence.

Uncovered IDs are described with the kind and text from the source's
``## Requirement Inventory`` table when it has one, because a bare ``BR-004``
names the token that is missing rather than the obligation. That lookup is
presentation only: it never moves a count or a verdict, and a source with no
inventory table falls silently back to bare IDs.

When the plan carries a ``## Requirement Dispositions`` table (| ID |
Disposition | Reason |), coverage splits into built and dispositioned. A
requirement with a terminal disposition (deferred / out-of-scope /
accepted-risk, each carrying a reason) leaves both the numerator and the
denominator — neither gap nor win — and the reported rate is over the in-scope
denominator. This is not a correction of a defect: citing a deferred ID in the
plan's scope boundaries is the discharge path
``references/requirement-id-conventions.md`` designs, and it works as
specified. What it cannot do is tell twelve built from three built and nine
deferred, because both print the same ``12/12 READY``. The table recovers that
distinction. Plans without the table keep the exact prior behavior.
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

# The source's definition site. Read for presentation only: a bare uncovered
# ID names the token that is missing, not the obligation, and the reviewer has
# to go and look it up. `references/requirement-id-conventions.md` fixes the
# shape as | ID | Type | Requirement |, so the lookup is already available.
INVENTORY_HEADING = re.compile(
    r"^#{2,3}\s+Requirement Inventory\s*$", re.MULTILINE
)

# The disposition table is located by its exact heading, never by a general
# region mechanism: heading-name matching over arbitrary sections is the
# brittleness that got the uncited-section checker rejected.
DISPOSITIONS_HEADING = re.compile(
    r"^#{2,3}\s+Requirement Dispositions\s*$", re.MULTILINE
)

# Closed vocabulary. `built` is the default state every uncited requirement is
# already in, so a `built` row changes nothing: the ID stays in the denominator
# and still needs its inline citation. The terminal three each end the
# requirement's life in this build and each require a reason.
DISPOSITION_BUILT = "built"
TERMINAL_DISPOSITIONS = ("deferred", "out-of-scope", "accepted-risk")
DISPOSITIONS = (DISPOSITION_BUILT,) + TERMINAL_DISPOSITIONS


def _extract_table(plan_text: str, heading, header_cell: str, width: int):
    """Locate a named section's markdown table.

    Returns (rows, malformed, span) where rows is a list of cell lists,
    malformed holds raw lines that look like rows but do not carry ``width``
    cells, and span is the (start, end) character span of the heading-and-table
    block so it can be excised from the inline-citation scan. Returns
    (None, [], None) when the section is absent.

    The scan stops at the first non-table line, a heading included. Two named
    tables can sit in one plan, so a heading with no table beneath it must not
    run on and adopt the next section's table as its own.
    """
    match = heading.search(plan_text)
    if not match:
        return None, [], None

    rows: list[list[str]] = []
    malformed: list[str] = []
    offset = match.end()
    table_end = offset
    started = False
    for line in plan_text[offset:].splitlines(keepends=True):
        stripped = line.strip()
        if not stripped:
            if started:
                break
            offset += len(line)
            table_end = offset
            continue
        if not stripped.startswith("|"):
            break
        started = True
        offset += len(line)
        table_end = offset
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and (
            cells[0].lower() == header_cell or set(cells[0]) <= {"-", ":", " "}
        ):
            continue
        if len(cells) != width:
            malformed.append(stripped)
            continue
        rows.append(cells)

    return rows, malformed, (match.start(), table_end)


def extract_traceability_table(plan_text: str):
    """Locate and parse the plan's ## Traceability table.

    Returns (rows, malformed, table_span) where rows is a list of parsed row
    dicts. Returns (None, [], None) when the plan has no Traceability section.
    """
    rows, malformed, span = _extract_table(plan_text, TRACEABILITY_HEADING, "story", 3)
    if rows is None:
        return None, [], None
    parsed = [
        {"story": cells[0], "requirements": cells[1], "design": cells[2]}
        for cells in rows
    ]
    return parsed, malformed, span


def extract_disposition_table(plan_text: str):
    """Locate and parse the plan's ## Requirement Dispositions table.

    Returns (rows, malformed, table_span) in the same shape as
    ``extract_traceability_table``, or (None, [], None) when absent.
    """
    rows, malformed, span = _extract_table(plan_text, DISPOSITIONS_HEADING, "id", 3)
    if rows is None:
        return None, [], None
    parsed = [
        {"id": cells[0], "disposition": cells[1], "reason": cells[2]}
        for cells in rows
    ]
    return parsed, malformed, span


def load_requirement_details(source_text: str) -> dict[str, tuple[str, str]]:
    """Map requirement ID -> (type, text) from the source's Requirement
    Inventory table, for describing uncovered IDs.

    Presentation only, so every failure mode here is silence. A source with no
    inventory table -- an ID-carrying PRD, a heading-style list -- yields an
    empty map and the uncovered list stays bare IDs, exactly as before. A
    malformed or empty-celled row is skipped rather than reported: the source
    is not this checker's artifact to validate, and reporting on it would turn
    a formatting slip in somebody else's PRD into a coverage failure.
    """
    rows, _malformed, _span = _extract_table(
        source_text, INVENTORY_HEADING, "id", 3
    )
    if not rows:
        return {}

    details: dict[str, tuple[str, str]] = {}
    for cells in rows:
        req_id = cells[0].strip().strip("`")
        kind = cells[1].strip().strip("`")
        text = cells[2].strip().strip("`")
        if not ID_PATTERN.fullmatch(req_id) or not kind or not text:
            continue
        # First row wins: the conventions forbid duplicate rows, and silently
        # preferring the last one would hide a source that carries two.
        details.setdefault(req_id, (kind, text))
    return details


def describe_requirement(
    req_id: str, details: dict[str, tuple[str, str]]
) -> str:
    """Render one uncovered ID, with its kind and text when the source has
    them and as the bare ID when it does not."""
    entry = details.get(req_id)
    if entry is None:
        return f"- {req_id}"
    kind, text = entry
    return f"- {req_id} ({kind}) {text}"


def check_dispositions(
    rows: list[dict],
    malformed: list[str],
    defined_requirements: set[str],
) -> tuple[list[str], dict[str, str]]:
    """Return (failures, dispositioned) where dispositioned maps a defined
    requirement ID to its terminal disposition."""
    failures: list[str] = []
    for line in malformed:
        failures.append(f"malformed disposition row: {line}")

    seen: set[str] = set()
    dispositioned: dict[str, str] = {}
    for n, row in enumerate(rows, 1):
        req_id = row["id"].strip().strip("`")
        if not ID_PATTERN.fullmatch(req_id):
            failures.append(
                f"disposition row {n}: ID cell '{row['id']}' is not a single "
                "requirement id (one requirement per row)"
            )
            continue
        if req_id in seen:
            failures.append(
                f"disposition row {n}: duplicate disposition row for {req_id}"
            )
            continue
        seen.add(req_id)
        # The table is excised from the inline-citation scan, so an ID that
        # appears only here can never surface as dangling there — reject it
        # here or it fails open, exactly as the traceability rows do.
        if req_id not in defined_requirements:
            failures.append(
                f"disposition row {n}: {req_id} is not defined in the source"
            )
            continue

        disposition = row["disposition"].strip().strip("`").lower()
        if disposition not in DISPOSITIONS:
            failures.append(
                f"disposition row {n} ({req_id}): '{row['disposition']}' is not "
                f"a disposition (use {', '.join(DISPOSITIONS)})"
            )
            continue
        if disposition == DISPOSITION_BUILT:
            continue
        if not row["reason"].strip().strip("`"):
            failures.append(
                f"disposition row {n} ({req_id}): {disposition} requires a "
                "reason (a terminal disposition is a decision, not a silence)"
            )
            continue
        dispositioned[req_id] = disposition

    return failures, dispositioned


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
    dispositioned: dict[str, str] | None = None,
    strict: bool = False,
) -> tuple[list[str], set[str], list[str], list[str]]:
    """Return (failures, mapped_requirements, unresolved, dispositioned_only).

    ``dispositioned`` maps a defined requirement ID to its terminal
    disposition word, so a row can be described with the decision and not just
    the token.

    ``unresolved`` holds one rendered line per design ref whose artifact was
    not supplied on the command line. Under ``strict`` those lines are
    failures; otherwise the caller prints them as a note. Either way they are
    now visible -- a check whose input is missing must never be silently
    skipped, which is what ``artifacts.get(kind)`` returning None used to do
    while the run still printed READY.

    ``dispositioned_only`` holds one rendered line per row whose whole
    Requirements cell is dispositioned: the row looks like live work and
    carries none. It is never a failure and ``strict`` never escalates it --
    see the note-versus-failure reasoning at the printing site in ``main``.
    """
    failures: list[str] = []
    unresolved: list[str] = []
    dispositioned_only: list[str] = []
    # One derivation per function, matching ``main``'s. A dispositioned
    # requirement has no story delivering it, so it is not unmapped -- it is
    # out of this build by decision.
    dispositioned = dispositioned or {}
    in_scope = defined_requirements - set(dispositioned)
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

        # Case B: the row cites requirements, and every one of them that is
        # defined at all has been dispositioned out of this build. The counts
        # are already right; what is wrong is that the row reads as live work.
        # A row citing only IDs that are undefined is a different defect and is
        # already reported as one above, so it is excluded here rather than
        # given a second finding.
        if (
            row_requirements
            and not row_requirements & in_scope
            and row_requirements & set(dispositioned)
        ):
            named = ", ".join(
                f"{req_id} ({dispositioned[req_id]})"
                for req_id in sorted(row_requirements & set(dispositioned))
            )
            dispositioned_only.append(
                f"- traceability row {n} ({story_cell}): {named}"
            )

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
                unresolved.append(
                    f"- traceability row {n} ({story_cell}): {kind}:{screen} "
                    f"(pass --{kind} to resolve it)"
                )
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
    unmapped = sorted(in_scope - mapped_requirements)
    if unmapped:
        failures.append("unmapped (defined in source, in no traceability row):")
        failures.extend(f"- {req_id}" for req_id in unmapped)

    if unresolved and strict:
        failures.append(unresolved_header(len(unresolved), strict=True))
        failures.extend(unresolved)
        unresolved = []
    return failures, mapped_requirements, unresolved, dispositioned_only


def dispositioned_only_header(count: int) -> str:
    """Header for the rows that deliver nothing in scope.

    There is no ``strict`` counterpart on purpose. ``check_handoff_gate.py``
    always passes ``--strict``, so escalating this would fail every plan
    carrying a fully-dispositioned story -- and the author has no permitted
    fix: `requirement-id-conventions.md` requires that every defined story own
    a row AND that the row cite at least one requirement ID, so the row can
    neither be dropped nor emptied.
    """
    if count == 1:
        return (
            "note: 1 story delivers no in-scope requirement (every requirement "
            "it cites is dispositioned):"
        )
    return (
        f"note: {count} stories deliver no in-scope requirement (every "
        "requirement each cites is dispositioned):"
    )


def unresolved_header(count: int, strict: bool) -> str:
    """One wording for both routes, so a reader who has seen the note
    recognises the failure."""
    noun = "design ref" if count == 1 else "design refs"
    if strict:
        return (
            f"{count} {noun} unverified: the design artifact was not supplied "
            "(--strict)"
        )
    return (
        f"note: {count} {noun} unverified (the design artifact was not "
        "supplied; --strict makes this a failure):"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # The two operands are same-typed markdown files, so a caller who
    # guesses `--source X --plan Y` is guessing the safer spelling. Both
    # forms are accepted; a mixed call is rejected rather than guessed at,
    # since it cannot say which file fills which slot.
    parser.add_argument(
        "source",
        type=Path,
        nargs="?",
        help="File defining the requirement IDs (PRD or requirement inventory)",
    )
    parser.add_argument(
        "plan", type=Path, nargs="?", help="Plan file to check for ID references"
    )
    parser.add_argument(
        "--source",
        dest="source_flag",
        type=Path,
        default=None,
        help="Named form of the source operand (do not mix with positionals)",
    )
    parser.add_argument(
        "--plan",
        dest="plan_flag",
        type=Path,
        default=None,
        help="Named form of the plan operand (do not mix with positionals)",
    )
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
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "fail when a design ref cannot be resolved because its artifact "
            "was not supplied (default: report it as a note)"
        ),
    )
    args = parser.parse_args(argv)

    positional = [args.source, args.plan]
    flagged = [args.source_flag, args.plan_flag]
    if any(p is not None for p in positional) and any(f is not None for f in flagged):
        parser.error(
            "use either the positional form (source plan) or the named form "
            "(--source SOURCE --plan PLAN), not both"
        )
    if all(f is not None for f in flagged):
        args.source, args.plan = flagged
    if args.source is None or args.plan is None:
        parser.error(
            "both operands are required: source plan, or --source SOURCE --plan PLAN"
        )

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
    disposition_rows, disposition_malformed, disposition_span = (
        extract_disposition_table(plan_text)
    )
    has_dispositions = disposition_rows is not None

    # The ID universe depends on the plan format: a legacy no-table plan
    # keeps the exact pre-traceability universe (no US- stories), so its
    # verdict cannot change. Neither named table counts as inline citation.
    inline_text = plan_text
    for start, end in sorted(
        [s for s in (table_span, disposition_span) if s is not None], reverse=True
    ):
        inline_text = inline_text[:start] + inline_text[end:]

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

    disposition_failures: list[str] = []
    dispositioned: dict[str, str] = {}
    if has_dispositions:
        disposition_failures, dispositioned = check_dispositions(
            disposition_rows, disposition_malformed, defined_requirements
        )

    # A dispositioned requirement leaves the numerator and the denominator
    # both: neither gap nor win. Without a disposition table the in-scope set
    # is the whole defined set and every count below is the prior one.
    in_scope = defined_requirements - set(dispositioned)
    uncovered = sorted(in_scope - referenced)
    dangling = sorted(referenced - defined_requirements)
    covered = len(in_scope) - len(uncovered)

    if has_dispositions:
        if not in_scope:
            disposition_failures.append(
                "every defined requirement is dispositioned; the plan builds "
                "nothing"
            )
        print(
            f"requirement coverage: {covered}/{len(in_scope)} in-scope IDs "
            f"referenced by the plan ({len(defined_requirements)} defined - "
            f"{len(dispositioned)} dispositioned)"
        )
        counts = [
            f"{kind} {sum(1 for v in dispositioned.values() if v == kind)}"
            for kind in TERMINAL_DISPOSITIONS
            if any(v == kind for v in dispositioned.values())
        ]
        print(f"dispositions: {', '.join(counts) if counts else 'none'}")
        for line in disposition_failures:
            print(line)
    else:
        print(
            f"requirement coverage: {covered}/{len(defined_requirements)} "
            "defined IDs referenced by the plan"
        )
    if uncovered:
        details = load_requirement_details(source_text)
        print("uncovered (defined in source, never referenced in plan):")
        for req_id in uncovered:
            print(describe_requirement(req_id, details))
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
        trace_failures, mapped, unresolved, dispositioned_only = check_traceability(
            rows,
            malformed,
            defined_stories,
            defined_requirements,
            {"blueprint": args.blueprint, "inventory": args.inventory},
            dispositioned,
            args.strict,
        )
        scope_label = "in-scope requirements" if has_dispositions else "requirements"
        print(
            f"traceability: {len(mapped & in_scope)}/{len(in_scope)} "
            f"{scope_label} mapped to stories across {len(rows)} rows"
        )
        for line in trace_failures:
            print(line)
        # Non-strict only: under --strict these lines are already among the
        # failures above, and printing them twice would read as two findings.
        if unresolved:
            print(unresolved_header(len(unresolved), strict=False))
            for line in unresolved:
                print(line)
        # Always a note, never a failure, and `--strict` does not reach it.
        # The counts above are already right -- the requirement is out of both
        # numerator and denominator -- so what is left is that the row reads as
        # live work. Failing it would be a check with no compliant exit: the
        # story must own a row and the row must cite an ID, so the only doors
        # out would be rewriting the source, reversing a recorded disposition
        # to satisfy a checker, or waiving the clause.
        if dispositioned_only:
            print(dispositioned_only_header(len(dispositioned_only)))
            for line in dispositioned_only:
                print(line)

    if uncovered or dangling or trace_failures or disposition_failures:
        print("coverage verdict: NOT READY")
        return 1

    if has_dispositions:
        print(
            f"coverage verdict: READY ({covered}/{len(in_scope)} in-scope "
            f"covered, {len(dispositioned)} dispositioned, 0 dangling)"
        )
    else:
        print(
            f"coverage verdict: READY ({covered}/{len(defined_requirements)} "
            "covered, 0 dangling)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
