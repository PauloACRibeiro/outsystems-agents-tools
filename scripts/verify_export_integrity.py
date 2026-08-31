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
    subtrees = managed_subtrees(list(listed))
    for sub in subtrees:
        for path in sorted((repo_root / sub).rglob("*")):
            if path.is_file():
                rel = path.relative_to(repo_root).as_posix()
                if rel not in listed:
                    problems.append(f"untracked: {rel} (present but not in manifest)")

    # A whole skills/<name> directory the manifest owns no file under is
    # invisible to the loop above, because the managed roots are derived from
    # the manifest rather than from disk. That is how a 66-file macOS
    # conflict-copy of a skill ("skills/<name> 2/") was committed with this
    # check passing, and it would have been published had the export commit
    # carrying it ever been pushed (2026-08-31). Every directory directly
    # under skills/ must be a root the manifest owns.
    owned_roots = {sub for sub in subtrees if sub.startswith("skills/")}
    skills_dir = repo_root / "skills"
    if skills_dir.is_dir():
        for path in sorted(skills_dir.iterdir()):
            if path.is_dir():
                rel = path.relative_to(repo_root).as_posix()
                if rel not in owned_roots:
                    problems.append(
                        f"unmanaged root: {rel}/ (directory under skills/ that the "
                        "manifest owns no file under)"
                    )

    return problems


def list_managed(repo_root: Path) -> list[str]:
    """Every path the manifest owns, for staging exactly the generated set."""
    manifest_path = Path(repo_root) / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return sorted({entry["path"] for entry in manifest.get("files", [])} | {MANIFEST_REL})


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "repo_root", nargs="?", default=".", help="Repository root (default: cwd)"
    )
    parser.add_argument(
        "--list-managed",
        action="store_true",
        help="print the manifest-owned paths and exit; pipe to git add instead of "
        "staging skills/ wholesale, which sweeps in unmanaged files",
    )
    parser.add_argument(
        "-z",
        "--null",
        action="store_true",
        help="with --list-managed, separate paths with NUL (for xargs -0)",
    )
    args = parser.parse_args(argv)

    if args.list_managed:
        sep = "\0" if args.null else "\n"
        sys.stdout.write(sep.join(list_managed(Path(args.repo_root))) + sep)
        return 0

    problems = verify(Path(args.repo_root))
    if problems:
        print("Export integrity check FAILED — the generated skills/ tree was edited out of band:")
        for problem in problems:
            print(f"  - {problem}")
        print(
            "\nDo not hand-edit files under skills/<name>/. Re-run the exporter in the "
            "source repo and commit the refreshed tree + EXPORT-MANIFEST.json.\n"
            "An 'unmanaged root' is usually not an edit at all but a stray directory "
            "next to the generated tree — a macOS conflict-copy such as "
            "'<name> 2/' — which must be deleted, not exported."
        )
        return 1
    print("Export integrity check passed: generated skills/ tree matches EXPORT-MANIFEST.json.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
