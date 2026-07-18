#!/usr/bin/env python3
"""Enforce that the generated skills tree matches its EXPORT-MANIFEST.json.

The `skills/` tree in this repo is generated output, exported one-way from the
canonical source repositories; it must never be hand-edited here. Every export
writes `skills/EXPORT-MANIFEST.json` recording the sha256 of each generated
file. This check recomputes those hashes and fails if any generated file was
modified, deleted, or added out of band — i.e. it blocks hand-edits of the
generated tree. It is fully self-contained (no access to the source repos is
required), so it runs as-is in this public repository's CI.

To legitimately change generated content, re-run the exporter in the source
repo and commit the refreshed tree + manifest; never edit files under
`skills/<name>/` directly here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

MANIFEST_REL = "skills/EXPORT-MANIFEST.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def managed_subtrees(listed_paths: list[str]) -> list[str]:
    """The `skills/<name>` roots the manifest owns (two-component skill roots)."""
    roots: set[str] = set()
    for rel in listed_paths:
        parts = PurePosixPath(rel).parts
        if len(parts) >= 3:
            roots.add(PurePosixPath(parts[0], parts[1]).as_posix())
    return sorted(roots)


def verify(repo_root: Path) -> list[str]:
    repo_root = Path(repo_root)
    manifest_path = repo_root / MANIFEST_REL
    if not manifest_path.is_file():
        return [f"missing {MANIFEST_REL} (no export provenance to verify against)"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        return [f"unreadable {MANIFEST_REL}: {exc}"]

    problems: list[str] = []
    listed: dict[str, str] = {}
    for entry in manifest.get("files", []):
        rel = entry["path"]
        listed[rel] = entry["sha256"]
        target = repo_root / rel
        if not target.is_file():
            problems.append(f"missing: {rel} (listed in manifest but absent)")
        elif _sha256(target) != entry["sha256"]:
            problems.append(f"modified: {rel} (hand-edited; hash != manifest)")

    # Any file under a managed subtree that the manifest does not list is an
    # out-of-band addition. Repo-authored siblings under skills/ (README.md,
    # .gitkeep, the manifest itself) live outside every skills/<name> root and
    # are therefore ignored.
    for sub in managed_subtrees(list(listed)):
        for path in sorted((repo_root / sub).rglob("*")):
            if path.is_file():
                rel = path.relative_to(repo_root).as_posix()
                if rel not in listed:
                    problems.append(f"untracked: {rel} (present but not in manifest)")

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "repo_root", nargs="?", default=".", help="Repository root (default: cwd)"
    )
    args = parser.parse_args(argv)

    problems = verify(Path(args.repo_root))
    if problems:
        print("Export integrity check FAILED — the generated skills/ tree was edited out of band:")
        for problem in problems:
            print(f"  - {problem}")
        print(
            "\nDo not hand-edit files under skills/<name>/. Re-run the exporter in the "
            "source repo and commit the refreshed tree + EXPORT-MANIFEST.json."
        )
        return 1
    print("Export integrity check passed: generated skills/ tree matches EXPORT-MANIFEST.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
