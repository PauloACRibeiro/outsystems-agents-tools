#!/usr/bin/env python3
"""Compute one handoff verdict with named clauses, by invoking the checkers.

Before this script, the go/no-go for "may this plan go to Mentor" was prose
spread across three sites that did not agree with each other:

  * `SKILL.md` step 9 required only `coverage verdict: READY`.
  * `references/coverage-review-prompt.md` required that *and* an
    `outcome verdict: READY`.
  * `SKILL.md` step 14 required a third combination -- the coverage matrix
    written plus the handoff scanner passing -- and `SKILL.md` never named
    `check_outcome_coverage.py` anywhere in the file.

All three readings were faithful, so which checks ran depended on which file the
run happened to be reading. Each checker already failed closed on its own; what
nothing did was record that all of them ran. A skipped step left no trace.

This script is that trace. It is deliberately thin:

    It INVOKES the checkers. It never restates what they check.

TWO PROPERTIES CARRY THE WHOLE THING, AND BOTH ARE EASY TO LOSE IN A REFACTOR.

1. THE VERDICT COMES FROM EXIT CODES, NEVER FROM THE CHECKERS' PROSE.
   Reading `coverage verdict: READY` out of stdout would make this gate break
   the moment a checker rewords its output -- and a checker's output is being
   reworded on a sibling branch right now. stdout and stderr are captured as
   evidence and printed verbatim; nothing parses them for the answer.

2. THERE IS NO SKIPPED CLAUSE. ONLY PASS AND FAIL.
   Every way a clause can fail to produce an answer -- input not supplied on the
   command line, input file missing, checker script absent, checker crashed,
   checker hung -- is a FAIL with a named reason. An aggregator that reports
   READY because a clause never ran is worse than the three separate exits it
   replaces, and this estate has shipped that defect before.

   The visible cost, stated rather than discovered: `check_outcome_coverage.py`
   needs a design file, so a run that does not pass `--design` gets
   `outcome-coverage: FAIL (input-not-supplied)`. That is intended. The
   alternative is an auto-accept, which turns an unsatisfied rule into a
   permanent pass.

3. A WAIVER IS THE ONLY EXIT, AND IT COSTS A RECORDED REASON. (v2, L6.)
   Property 2 has a real operational cost: a run that cannot supply `--design`
   fails `outcome-coverage` forever. The honest way past that is not a skip
   state and not an auto-accept -- it is a waiver that names its clause and
   records why, through the same mechanism as everything else.

   `--waivers handoff-waivers.json` moves a FAILING clause to `WAIVED`.
   Everything about that is deliberately hostile to casual use:

     * WAIVED is its own state. It is never folded into PASS, in the verdict
       or in the rendering, and the clause keeps the evidence of its original
       failure alongside the recorded reason.
     * A waiver with no reason, a blank reason, an undefined clause name, an
       unrecognised key, or a duplicate clause is REFUSED -- and a refusal is
       itself a gate failure, not merely an absence of waivers.
     * ONE bad entry voids the WHOLE file. Dropping only the invalid entry
       would let a file its author demonstrably got wrong still move the
       verdict. A partially-trusted waiver file is the fail-open this states
       exists to prevent, one level up from the clause table.
     * A waiver on a clause that PASSED is inert, never an override, and is
       reported as unused so it cannot rot in the file unnoticed.
     * An ABSENT waiver file means "no waivers", never an error. Absence can
       only ever make the gate stricter, so it is safe in the one direction
       that matters; a typo'd path yields NOT READY, not a false READY.

THE VERSION CONTRACT.

  * `CLAUSE_NAMES` is the canonical, stable clause vocabulary and the waiver
    vocabulary. A waiver naming anything outside it is refused. Renaming a
    member silently invalidates every stored waiver, so it is pinned by a test.
  * `V1_STATES` is FROZEN. It names version one's domain and is kept as the
    historical record; v2 does not grow it. `V2_STATES` is the current domain
    and `PASSING_STATES` is the subset that permits READY.
  * `compute_verdict()` is the single place the states become one answer:
    READY iff every defined clause is present and PASS-or-WAIVED, and no
    waiver error was recorded. Nothing about how clauses are PRODUCED changed
    in v2; waivers are applied as a separate pass over the finished list.
  * `gate_version` is 2, so a consumer can tell a v1 report (two states) from
    a v2 report (three) without guessing.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent

GATE_VERSION = 2

# The clause vocabulary. Stable: L6 validates waivers against it.
CLAUSE_NAMES: tuple[str, ...] = (
    "requirement-coverage",
    "outcome-coverage",
    "handoff-scan",
)

# FROZEN. v1's domain, kept as the historical record so a v1 report stays
# interpretable; v2 does NOT grow this tuple -- the name would become a lie.
V1_STATES: tuple[str, ...] = ("PASS", "FAIL")

# The current domain. There is deliberately still no SKIP.
V2_STATES: tuple[str, ...] = ("PASS", "FAIL", "WAIVED")

# The states that permit READY. WAIVED passes the gate; it is never PASS.
PASSING_STATES: tuple[str, ...] = ("PASS", "WAIVED")

# The only keys a waiver entry may carry. Anything else is a refusal rather
# than a shrug: `resaon` would otherwise become a silently reasonless waiver.
WAIVER_KEYS: tuple[str, ...] = ("clause", "reason")

# Separates the human report from the machine block on stdout.
JSON_MARKER = "--- handoff gate (machine-readable) ---\n"

# Generous: these are small scanners over one file each. A checker still
# running after this has hung, and a hung clause is a failing clause.
DEFAULT_TIMEOUT = 120.0


@dataclass
class ClauseResult:
    """One named clause and the evidence behind its state."""

    name: str
    state: str
    reason: str | None = None
    command: list[str] = field(default_factory=list)
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    # v2. Set only when a waiver moved this clause to WAIVED; `reason` keeps
    # holding why the clause FAILED, so waiving records an excuse rather than
    # erasing the finding.
    waiver_reason: str | None = None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "state": self.state,
            "reason": self.reason,
            "command": self.command,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "waiver_reason": self.waiver_reason,
        }


def run_clause(
    name: str,
    script: Path,
    args: list[str],
    timeout: float = DEFAULT_TIMEOUT,
) -> ClauseResult:
    """Invoke one checker and turn its exit code into a clause state.

    `sys.executable`, not `python3`: `python3` is not a command on Windows
    PowerShell, which the skill's own reference file states twice, and this
    estate ships to Windows.
    """
    command = [sys.executable, str(script), *args]

    if not script.is_file():
        return ClauseResult(
            name=name,
            state="FAIL",
            reason="checker-missing",
            command=command,
            stderr=f"checker script not found: {script}",
        )

    try:
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return ClauseResult(
            name=name,
            state="FAIL",
            reason="checker-timeout",
            command=command,
            stderr=f"checker did not finish within {timeout:g}s",
        )
    except OSError as exc:  # unreadable, not executable, no interpreter
        return ClauseResult(
            name=name,
            state="FAIL",
            reason="checker-unrunnable",
            command=command,
            stderr=str(exc),
        )

    # The exit code is the answer. The output is only evidence.
    passed = completed.returncode == 0
    return ClauseResult(
        name=name,
        state="PASS" if passed else "FAIL",
        reason=None if passed else "checker-reported-failure",
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def not_supplied(name: str, missing: str) -> ClauseResult:
    """A clause whose input never arrived. A failure, never an absence."""
    return ClauseResult(
        name=name,
        state="FAIL",
        reason="input-not-supplied",
        stderr=(
            f"{missing} was not supplied, so this clause could not be evaluated. "
            "An unevaluated clause fails."
        ),
    )


def load_waivers(path: Path | None) -> tuple[dict[str, str], list[str]]:
    """Read the waiver file. Returns (clause -> recorded reason, errors).

    Any error voids the WHOLE file: the returned mapping is empty and the
    errors are non-empty. Dropping only the invalid entry would let a file its
    author demonstrably got wrong still move the verdict, which is the same
    partial-trust fail-open the clause table refuses one level down.

    An absent file is "no waivers", never an error. Absence can only make the
    gate stricter, so a typo'd path yields NOT READY rather than a false READY.
    """
    if path is None or not path.is_file():
        return {}, []

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {}, [f"{path}: the waiver file could not be parsed ({exc})"]

    if not isinstance(raw, dict):
        return {}, [f"{path}: the waiver file must be a JSON object"]

    entries = raw.get("waivers")
    if entries is None:
        return {}, [f"{path}: the waiver file has no 'waivers' key"]
    if not isinstance(entries, list):
        return {}, [f"{path}: 'waivers' must be a list"]

    errors: list[str] = []
    waivers: dict[str, str] = {}

    for index, entry in enumerate(entries, start=1):
        label = f"waiver {index}"

        if not isinstance(entry, dict):
            errors.append(f"{label}: each waiver must be a JSON object")
            continue

        unknown = sorted(set(entry) - set(WAIVER_KEYS))
        if unknown:
            errors.append(
                f"{label}: unrecognised key(s) {', '.join(repr(k) for k in unknown)}; "
                f"a waiver carries exactly {' and '.join(WAIVER_KEYS)}"
            )
            continue

        clause = entry.get("clause")
        if clause not in CLAUSE_NAMES:
            errors.append(
                f"{label}: names an undefined clause {clause!r}; "
                f"the clause vocabulary is {', '.join(CLAUSE_NAMES)}"
            )
            continue

        reason = entry.get("reason")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(
                f"{label} ({clause}): no recorded reason. A waiver without a reason "
                f"is an auto-accept, which turns an unsatisfied rule into a "
                f"permanent pass."
            )
            continue

        if clause in waivers:
            errors.append(
                f"{label}: {clause} is waived more than once, so there is no single "
                f"recorded reason for it"
            )
            continue

        waivers[clause] = reason.strip()

    if errors:
        # Whole-file refusal: nothing from a rejected file is trusted.
        return {}, errors
    return waivers, []


def apply_waivers(
    clauses: list[ClauseResult], waivers: dict[str, str]
) -> tuple[list[str], list[str]]:
    """Move FAILING clauses named by a waiver to WAIVED, in place.

    A waiver never overrides a PASS -- it only ever excuses a failure. One that
    names a clause which passed is inert and comes back in `unused`, so a stale
    waiver cannot sit in the file unnoticed.

    Returns (applied clause names, unused clause names).
    """
    by_name = {clause.name: clause for clause in clauses}
    applied: list[str] = []
    unused: list[str] = []

    for name, reason in waivers.items():
        clause = by_name.get(name)
        if clause is not None and clause.state == "FAIL":
            clause.state = "WAIVED"
            clause.waiver_reason = reason
            applied.append(name)
        else:
            unused.append(name)

    return applied, unused


def compute_verdict(
    clauses: list[ClauseResult], waiver_errors: list[str] | tuple[str, ...] = ()
) -> str:
    """READY iff every defined clause is present and PASS-or-WAIVED, and no
    waiver was refused.

    Presence is checked, not assumed. An aggregator that folds an empty or short
    clause list into READY by vacuous truth is the fail-open this script exists
    to prevent.

    A refused waiver denies READY on its own, even when every clause passes: a
    broken waiver file must not be indistinguishable from no waiver file. The
    membership test is against PASSING_STATES rather than `!= "FAIL"`, so an
    unrecognised state is still NOT READY.
    """
    if waiver_errors:
        return "NOT READY"
    by_name = {clause.name: clause for clause in clauses}
    for name in CLAUSE_NAMES:
        clause = by_name.get(name)
        if clause is None or clause.state not in PASSING_STATES:
            return "NOT READY"
    return "READY"


def build_clauses(args: argparse.Namespace) -> list[ClauseResult]:
    coverage_args = [str(args.source), str(args.plan)]
    if args.blueprint is not None:
        coverage_args += ["--blueprint", str(args.blueprint)]
    if args.inventory is not None:
        coverage_args += ["--inventory", str(args.inventory)]
    # The design file reaches TWO clauses. `outcome-coverage` reads its result
    # declarations; the coverage checker reads its input declarations for the
    # contract-reachability note. Forwarding it cannot change this clause's
    # state -- that note never fails -- so the gate's own contract is unmoved.
    if args.design is not None:
        coverage_args += ["--design", str(args.design)]
    # Unconditional, and it belongs here rather than behind a gate flag of its
    # own. A design ref the coverage checker cannot resolve is a check that did
    # not run, which is rule 2 above; a --strict the operator has to remember
    # is the same fail-open with an extra step. The exit from the resulting
    # FAIL is the one this gate already has: supply the artifact, write the
    # design cell as an explicit `none`, or waive the clause with a recorded
    # reason. Adding no flag also keeps GATE_VERSION honest -- the gate's own
    # surface is unchanged.
    coverage_args.append("--strict")

    clauses = [
        run_clause(
            "requirement-coverage",
            SCRIPT_DIR / "check_requirement_coverage.py",
            coverage_args,
        )
    ]

    if args.design is None:
        clauses.append(not_supplied("outcome-coverage", "--design"))
    else:
        clauses.append(
            run_clause(
                "outcome-coverage",
                SCRIPT_DIR / "check_outcome_coverage.py",
                [str(args.design), str(args.plan)],
            )
        )

    scan_args = [str(args.plan)]
    if args.original_plan is not None:
        # The scanner's own --source is the plan the patch was made from, which
        # is NOT this gate's --source (the requirement inventory). Passing the
        # wrong one would compare a plan against a PRD and report every heading
        # as dropped, so the gate keeps the two names apart deliberately.
        scan_args += ["--source", str(args.original_plan)]

    clauses.append(
        run_clause(
            "handoff-scan",
            SCRIPT_DIR / "check_plan_handoff.py",
            scan_args,
        )
    )
    return clauses


def render(
    clauses: list[ClauseResult],
    verdict: str,
    waiver_errors: list[str] | tuple[str, ...] = (),
    unused: list[str] | tuple[str, ...] = (),
) -> str:
    """Print the clause table, the waiver record and the verdict.

    `clause.state` is printed VERBATIM, never through a two-valued "is this
    passing?" helper. That helper is the one place a WAIVED clause could read
    as PASS to a human while the machine block stayed honest, so it does not
    exist here; if one is ever added it must be three-valued.
    """
    width = max(len(name) for name in CLAUSE_NAMES)
    lines = ["handoff gate clauses:"]
    for clause in clauses:
        notes = [note for note in (clause.reason,) if note]
        if clause.waiver_reason:
            notes.append(f"waived: {clause.waiver_reason}")
        suffix = f" ({'; '.join(notes)})" if notes else ""
        lines.append(f"- {clause.name.ljust(width)}  {clause.state}{suffix}")

    if waiver_errors:
        lines.append("")
        lines.append("waiver file REFUSED -- no waiver was applied from it:")
        lines.extend(f"- {error}" for error in waiver_errors)

    if unused:
        lines.append("")
        lines.append("unused waivers (their clause did not fail):")
        lines.extend(f"- {name}" for name in unused)

    lines.append("")
    lines.append("clause evidence (each checker's own output, verbatim):")
    for clause in clauses:
        lines.append("")
        lines.append(f"[{clause.name}]")
        body = (clause.stdout + clause.stderr).rstrip("\n")
        lines.extend(body.splitlines() if body else ["(no output)"])

    lines.append("")
    lines.append(f"handoff verdict: {verdict}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run every handoff checker and compute one verdict."
    )
    parser.add_argument(
        "--source",
        "--requirement-source",
        type=Path,
        required=True,
        help=(
            "Requirement inventory or ID-carrying PRD. `--requirement-source` is "
            "an alias for this same flag, spelling out the role: the handoff "
            "SCANNER also takes a --source and it means a different thing, so "
            "the two are easy to swap by hand. See --scan-source."
        ),
    )
    parser.add_argument(
        "--plan",
        type=Path,
        required=True,
        help="Patched plan file that will be sent to Mentor conversion",
    )
    parser.add_argument(
        "--design",
        type=Path,
        default=None,
        help=(
            "Design file declaring action results. Omitting it FAILS the "
            "outcome-coverage clause; it does not skip it."
        ),
    )
    parser.add_argument(
        "--blueprint",
        type=Path,
        default=None,
        help="enriched blueprint.json, passed through to the coverage checker",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=None,
        help="screen-inventory.json, passed through to the coverage checker",
    )
    parser.add_argument(
        "--original-plan",
        "--scan-source",
        type=Path,
        default=None,
        help=(
            "The plan the patch was made from. Forwarded to the handoff scanner "
            "as ITS --source, enabling the structural non-regression check. NOT "
            "the same as this gate's --source, which is the requirement "
            "inventory. `--scan-source` is an alias for this same flag, named "
            "for where the value is forwarded rather than for what it is."
        ),
    )
    parser.add_argument(
        "--waivers",
        type=Path,
        default=None,
        help=(
            "handoff-waivers.json: whole-clause waivers, each naming its clause "
            "and recording why. A waiver moves a FAILING clause to WAIVED, which "
            "is never PASS. Any invalid waiver refuses the whole file and denies "
            "READY; a file that is not there simply means no waivers."
        ),
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Also write the machine block to this file",
    )
    args = parser.parse_args(argv)

    waivers, waiver_errors = load_waivers(args.waivers)
    clauses = build_clauses(args)
    applied, unused = apply_waivers(clauses, waivers)
    verdict = compute_verdict(clauses, waiver_errors)

    payload = {
        "gate_version": GATE_VERSION,
        "verdict": verdict,
        "clauses": [clause.as_dict() for clause in clauses],
        "waivers": {
            "applied": applied,
            "unused": unused,
            "errors": list(waiver_errors),
        },
    }

    sys.stdout.write(render(clauses, verdict, waiver_errors, unused))
    sys.stdout.write(JSON_MARKER)
    sys.stdout.write(json.dumps(payload, indent=2))
    sys.stdout.write("\n")

    if args.json is not None:
        args.json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return 0 if verdict == "READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
