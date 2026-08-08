"""Shared JSON-file read+parse helper for this skill's scripts.

Enumerating the callers here rots: the catalog-refresh tooling that used it is
maintainer-only and does not ship in public distributions, so a named list goes
stale the moment a bundle withholds one of them.

Each caller decides what to do with a JSONFileError (raise SystemExit with
its own message, or record a per-item status) - this helper only owns the
read/parse/exception-wrapping step.
"""
import json


class JSONFileError(Exception):
    """Raised when a JSON file is missing, unreadable, or malformed."""


def read_json_file(path):
    """Read and parse *path* as JSON, raising JSONFileError on failure."""
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise JSONFileError(f"no such file: {path}") from exc
    except UnicodeDecodeError as exc:
        raise JSONFileError(f"malformed JSON in {path}: {exc}") from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise JSONFileError(f"malformed JSON in {path}: {exc}") from exc
