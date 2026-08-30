#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path


ALLOWED_STATUSES = {
    "pending",
    "prompt-ready",
    "claude-running",
    "feedback-ready",
    "codex-reviewing",
    "changes-needed",
    "pass",
    "accepted-risk",
    "blocked-claude-automation",
    "blocked-evidence",
    "needs-human-decision",
    "verified",
    "done",
}

TERMINAL_STATUSES = {
    "done",
    "accepted-risk",
    "blocked-claude-automation",
    "blocked-evidence",
}

REQUIRED_COLUMNS = [
    ("id", "ID"),
    ("capability_group", "Capability group"),
    ("status", "Status"),
    ("source_files", "Source files"),
    ("claude_prompt_path", "Claude prompt path"),
    ("expected_feedback_path", "Expected feedback path"),
    ("codex_decision", "Codex decision"),
    ("verification", "Verification"),
    ("commit", "Commit"),
    ("accepted_risk", "Accepted risk"),
    ("notes", "Notes"),
]

REQUIRED_FIELD_KEYS = [
    "source_files",
    "expected_feedback_path",
    "codex_decision",
    "verification",
    "commit",
    "accepted_risk",
    "notes",
]


def parse_cells(line: str):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def required_headers():
    return [label for _key, label in REQUIRED_COLUMNS]


def parse_rows(queue_path: Path):
    rows = []
    column_keys = [key for key, _label in REQUIRED_COLUMNS]
    expected_cell_count = len(REQUIRED_COLUMNS)
    header_seen = False

    for line_number, line in enumerate(
        queue_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if line.startswith("| ID |"):
            header_seen = True
            headers = parse_cells(line)
            if headers != required_headers():
                raise ValueError(
                    "header mismatch on line "
                    f"{line_number}: expected {required_headers()}, got {headers}"
                )
            continue

        if not line.startswith("| MSC-"):
            continue

        cells = parse_cells(line)
        if len(cells) != expected_cell_count:
            raise ValueError(
                f"line {line_number}: expected {expected_cell_count} cells, got {len(cells)}"
            )

        row = dict(zip(column_keys, cells))
        row["line_number"] = line_number
        rows.append(row)

    if not header_seen:
        raise ValueError("header mismatch: missing queue table header")

    return rows


def _is_missing(value: str) -> bool:
    return not value or value.strip() == ""


def validate_rows(rows):
    errors = []
    seen_ids = set()

    if not rows:
        return ["queue has no capability rows"]

    for row in rows:
        row_id = row["id"]
        status = row["status"]

        if row_id in seen_ids:
            errors.append(f"{row_id}: duplicate id")
        seen_ids.add(row_id)

        if status not in ALLOWED_STATUSES:
            errors.append(f"{row_id}: invalid status {status}")

        for key in REQUIRED_FIELD_KEYS:
            if _is_missing(row[key]):
                label = dict(REQUIRED_COLUMNS)[key]
                errors.append(f"{row_id}: missing {label}")

        if (
            row["capability_group"] != "Live Mentor Validation Gate"
            and status not in {"pending", "needs-human-decision"}
            and (
                _is_missing(row["claude_prompt_path"])
                or row["claude_prompt_path"].lower() == "none"
            )
        ):
            errors.append(f"{row_id}: reviewed row needs a Claude prompt path")

    return errors


def first_unresolved(rows):
    for row in rows:
        if row["status"] not in TERMINAL_STATUSES:
            return row
    return {}


def public_row(row):
    return {key: row[key] for key, _label in REQUIRED_COLUMNS if key in row}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate outsystems-mentor-implementation capability review queue."
    )
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("command", choices=["validate", "next", "assert-final"])
    args = parser.parse_args(argv)

    try:
        rows = parse_rows(args.queue)
    except OSError as exc:
        print(f"{args.queue}: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors = validate_rows(rows)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    if args.command == "validate":
        print(f"queue valid: {len(rows)} rows")
        return 0

    if args.command == "next":
        next_row = first_unresolved(rows)
        if not next_row:
            print("no unresolved rows", file=sys.stderr)
            return 3
        print(json.dumps(public_row(next_row), indent=2))
        return 0

    unresolved = [row["id"] for row in rows if row["status"] not in TERMINAL_STATUSES]
    if unresolved:
        print(f"unresolved rows: {', '.join(unresolved)}", file=sys.stderr)
        return 2

    print("final readiness queue state is terminal")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
