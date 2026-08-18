#!/usr/bin/env python3
"""Compute execution-outcome coverage as a set difference over action results.

The design file declares, per server action, the result values it can return
("Result is one of `Success`, `CourseFull`, ..."). The plan's verification
matrix declares which of those an execution test actually reaches. Coverage is
mechanical: unexercised = declared refusals - reached.

Why this exists (v39, from the TrainingHub run): every build-time signal the
loop relies on -- validation, coverage, enumeration, `change_applied`, retry
count, publish status -- describes whether the right *shapes* exist. None can
observe whether the logic inside them does its job. An action was, by every one
of those measures, correct, and did nothing at all.

This checker closes the smaller half of that gap: it proves every refusal the
design promises is exercised by something. It cannot prove the tests were run,
only that they were written -- ordering is the loop's job (R3), not a parser's.

Only NON-SUCCESS outcomes are required. A success path is exercised by any
happy-path test; a refusal branch is reached only on purpose.

THE BLIND SPOT, STATED SO NOBODY READS `READY` AS MEANING MORE THAN IT DOES.
This checker's entire universe is what the design *declares*. It answers "is
every refusal you wrote down tested?" -- never "did you write down every refusal
you needed?". An action that declares no not-found outcome contributes zero to
the total and the run still reports READY.

That is not hypothetical. V78: ODC's generated `Delete<Entity>` does not raise on
a missing row, it returns silently, so `RemoveCourse(999999)` reports `Success`
for a course that never existed. It declares no not-found result, so there is
nothing here to be unexercised, and this checker passes it. Its sibling defect
V71/V77 -- reads that *do* raise -- is equally invisible for the same reason.

**A check derived from the artifact it is checking cannot find an omission in
that artifact.** Finding the missing declaration needs a different instrument:
call every action with an id that does not exist and see what comes back. Static
scanning is structurally blind to it, including grepping for `NullIdentifier()`,
which finds the dead guards and never the absent one.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# "Result is one of `A`, `B`, `C`." -- the phrasing the design skill emits.
# Tolerates "Results are one of", a colon, and line wrapping inside the list.
_DECLARATION = re.compile(
    r"Results?\s+(?:is|are)\s+one\s+of\s*:?\s*(?P<values>[^.]+)\.",
    re.IGNORECASE | re.DOTALL,
)

# The action heading that a declaration belongs to: "### `Enrol(...) -> ...`"
_HEADING = re.compile(r"^#{2,4}\s+`(?P<name>[A-Za-z_][A-Za-z0-9_]*)", re.MULTILINE)

_BACKTICKED = re.compile(r"`([A-Za-z_][A-Za-z0-9_]*)`")

# Outcomes that need no dedicated refusal test.
_SUCCESS_VALUES = {"success", "ok", "created", "updated", "deleted"}


def _declared(text: str) -> dict[str, set[str]]:
    """Map action name -> declared non-success result values."""
    headings = [(m.start(), m.group("name")) for m in _HEADING.finditer(text)]
    out: dict[str, set[str]] = {}
    for match in _DECLARATION.finditer(text):
        owner = None
        for pos, name in headings:
            if pos < match.start():
                owner = name
            else:
                break
        if owner is None:
            continue
        values = {
            v for v in _BACKTICKED.findall(match.group("values"))
            if v.lower() not in _SUCCESS_VALUES
        }
        if values:
            out.setdefault(owner, set()).update(values)
    return out


# A verification row: "V6  C-005  User B calls ... -> "NotOwner"." Continuations
# are indented under it.
_V_ROW = re.compile(r"^V\d+\b")


def verification_scope(text: str) -> str:
    """Return only the verification-matrix rows, not the whole plan.

    This scoping is the whole point of the checker, and getting it wrong makes
    it useless in the most dangerous way: the plan also contains the *Mentor
    prompts*, which name every outcome because they instruct the build to
    return them. Scanning the whole plan therefore reports every outcome as
    exercised and passes a plan whose verification matrix tests none of them --
    a check that always says READY. Measured on the TrainingHub run: whole-plan
    scan says 7/7, matrix-only scan says 3/7, and the truth is 3/7.
    """
    rows: list[str] = []
    capturing = False
    for line in text.splitlines():
        if _V_ROW.match(line):
            capturing = True
            rows.append(line)
        elif capturing and (line.startswith((" ", "\t")) and line.strip()):
            rows.append(line)
        else:
            capturing = False
    return "\n".join(rows)


# An observed result is introduced by "->". Everything before it is the setup:
# who calls what, with which inputs. Everything after it is what came back.
_OBSERVED_SEGMENT = re.compile(r"->\s*([^>]*)")

# A segment that denies an outcome is not evidence the outcome was reached.
# Word-bounded, so it does not fire inside an identifier: "NotOwner" has no
# boundary after "Not" and is left alone.
_DENIAL = re.compile(r"\b(?:not|never|no|none|without|neither|nor|unless)\b", re.IGNORECASE)


def _reached(text: str) -> set[str]:
    """Outcomes the matrix says were OBSERVED -- not merely mentioned.

    Mentioning an outcome is not exercising it. Before this was anchored, every
    identifier anywhere in a verification row counted, so a row written to deny
    an outcome scored the same as one that reached it:

        V2  C-002  Confirm the happy path never returns `NotFound`.

    reported `2/2 exercised, verdict READY, exit 0` -- a false green in a gate
    verdict, on exactly the failure the gate exists to catch. Found by an
    adversarial pre-cut review (2026-08-12) and reproduced before being accepted.

    Two rules, both derived from how real matrices are written:

    1. Only the text AFTER a `->` counts. That is the convention the artifacts
       already use -- `-> REFUSED "CourseFull"`, `-> "AlreadyEnrolled"` -- and it
       separates the observed result from the setup that produced it.
    2. A segment that DENIES an outcome is discarded. "-> never returns X"
       observes the absence of X, which is the opposite of exercising it.

    Deliberately conservative: a genuinely-exercised outcome written without a
    `->` reads as unexercised, and the run says NOT READY. That direction costs
    a plan edit; the other direction ships an untested refusal branch.
    """
    found: set[str] = set()
    for line in verification_scope(text).splitlines():
        for segment in _OBSERVED_SEGMENT.findall(line):
            # A denial only discards outcomes it actually governs -- the ones that
            # come AFTER it. "-> never returns `NotFound`" denies the outcome and is
            # dropped; "-> `LoanNotFound`, a refusal and NOT an error" names the
            # outcome first and then emphasises what it is not, which is ordinary
            # matrix prose. Discarding the whole segment on any negation cost two
            # true rows the first time this ran for real (2026-08-12) -- and a check
            # that punishes natural phrasing gets worked around rather than obeyed.
            denial = _DENIAL.search(segment)
            scope = segment[: denial.start()] if denial else segment
            found.update(_BACKTICKED.findall(scope))
            found.update(re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', scope))
            # Bare identifiers appear unquoted in matrix prose ("-> succeeds, CourseFull").
            found.update(re.findall(r"\b([A-Z][A-Za-z0-9]*[a-z][A-Za-z0-9]*)\b", scope))
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("design", type=Path, help="Design file declaring action results")
    parser.add_argument("plan", type=Path, help="Plan file carrying the verification matrix")
    args = parser.parse_args(argv)

    for path in (args.design, args.plan):
        if not path.is_file():
            print(f"file not found: {path}", file=sys.stderr)
            return 2

    declared = _declared(args.design.read_text(encoding="utf-8"))
    if not declared:
        print(
            f"no action result declarations found in {args.design}; "
            'expected the form: Result is one of `Success`, `Refusal`, ...',
            file=sys.stderr,
        )
        return 2

    reached = _reached(args.plan.read_text(encoding="utf-8"))

    total = sum(len(v) for v in declared.values())
    unexercised: list[tuple[str, str]] = []
    for action in sorted(declared):
        for value in sorted(declared[action]):
            if value not in reached:
                unexercised.append((action, value))

    covered = total - len(unexercised)
    print(
        f"outcome coverage: {covered}/{total} declared refusal outcomes "
        f"exercised across {len(declared)} action(s)"
    )
    if unexercised:
        print("unexercised (declared by the design, no verification row reaches it):")
        for action, value in unexercised:
            print(f"- {action}.{value}")

    if unexercised:
        print("outcome verdict: NOT READY")
        return 1

    # The verdict carries its own scope. Prose scope does not survive being
    # quoted, and "READY" quoted bare reads as "the refusals are covered".
    print(
        f"outcome verdict: READY ({covered}/{total} DECLARED refusals exercised; "
        f"does not check whether the design declared every refusal it needed -- see V78)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
