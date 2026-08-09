#!/usr/bin/env python3
"""Install the OMI colleague pack into per-agent skill directories.

Colleague-machine installer for packs built by scripts/build_skill_package.py.
Installs plain directory COPIES (never symlinks) into:

  Claude Code : ~/.claude/skills/   (%USERPROFILE%\\.claude\\skills on Windows)
  Codex       : ~/.agents/skills/   (%USERPROFILE%\\.agents\\skills on Windows)

`~/.codex/skills/` is deliberately not a target: it is Codex's deprecated
legacy location. Discovery on both agents is a filesystem scan, so no config
registration is performed.

Guards: refuses to touch symlinked targets (the maintainer's live-link
mechanism, see docs/CANONICAL-LIVE-INSTALL-STRATEGY.md) and refuses to install
into any path inside a Workspace checkout (marker: workspace-manifest.yaml).

See packaging/README.md -> "Install (Phase 2)" for the mapping table.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

PACK_PREFIX = "omi-colleague-pack"
PACKAGE_MANIFEST_NAME = "PACKAGE-MANIFEST.json"
RECEIPT_NAME = ".omi-colleague-pack-receipt.json"
OMI_DIR_NAME = "outsystems-mentor-implementation"
SHARED_DIR_NAME = "shared"
WORKSPACE_MARKER = "workspace-manifest.yaml"
MAX_RECEIPT_BYTES = 1024 * 1024
MAX_COMPRESSED_ARCHIVE_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_MEMBERS = 4096
MAX_MEMBER_BYTES = 32 * 1024 * 1024
MAX_TOTAL_BYTES = 128 * 1024 * 1024
MAX_COMPRESSION_RATIO = 200
MAX_INSTALLED_FILE_BYTES = 32 * 1024 * 1024
TRANSACTION_STAGE_NAME = ".omi-colleague-pack-transaction-staging"
TRANSACTION_BACKUP_NAME = ".omi-colleague-pack-transaction-backup"

_VERSION_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:\.(\d+))?$")


class InstallError(Exception):
    """Refusal or failure with a colleague-actionable message."""


def parse_pack_version(version: str) -> tuple:
    match = _VERSION_RE.match(version)
    if not match:
        raise InstallError(
            f"unrecognized pack version {version!r} (expected YYYY-MM-DD or YYYY-MM-DD.N)"
        )
    return (match.group(1), int(match.group(2) or 0))


def pack_version_from_filename(pack_path: Path) -> str:
    name = Path(pack_path).name
    prefix = PACK_PREFIX + "-"
    suffix = ".tgz"
    if not (name.startswith(prefix) and name.endswith(suffix)):
        raise InstallError(f"not a {PACK_PREFIX} archive name: {name}")
    version = name[len(prefix):-len(suffix)]
    parse_pack_version(version)  # validates shape
    return version


def resolve_latest_pack(dist_dir: Path) -> Path:
    dist_dir = Path(dist_dir)
    candidates = []
    for path in dist_dir.glob(PACK_PREFIX + "-*.tgz"):
        try:
            candidates.append((parse_pack_version(pack_version_from_filename(path)), path))
        except InstallError:
            continue
    if not candidates:
        raise InstallError(f"no {PACK_PREFIX}-*.tgz found under {dist_dir}")
    return max(candidates)[1]


def _validate_member(member: tarfile.TarInfo, expected_top: str) -> None:
    name = member.name
    if name.startswith("/") or "\\" in name or (len(name) > 1 and name[1] == ":"):
        raise InstallError(f"absolute path in archive: {name}")
    parts = PurePosixPath(name).parts
    normalized = PurePosixPath(name).as_posix()
    if ".." in parts or any(part in {"", ".", ".."} for part in parts):
        raise InstallError(f"path traversal in archive: {name}")
    if normalized != name:
        raise InstallError(f"non-canonical normalized path in archive: {name}")
    if not parts or parts[0] != expected_top:
        raise InstallError(
            f"archive member outside expected top directory {expected_top}/: {name}"
        )
    if not member.isfile():
        raise InstallError(
            f"unsupported archive member type (directory/symlink/device/hardlink): {name}"
        )


def _verify_file_hashes(top: Path, manifest: dict) -> None:
    problems = []
    manifest_paths = set()
    entries = manifest.get("files")
    if type(entries) is not list or manifest.get("file_count") != len(entries):
        raise InstallError("package manifest file count is invalid")
    ordered_paths = []
    for entry in entries:
        if type(entry) is not dict or set(entry) != {"path", "sha256", "size"}:
            raise InstallError("package manifest file entry is invalid")
        rel = entry["path"]
        if not isinstance(rel, str):
            raise InstallError("manifest lists an unsafe path")
        rel_parts = PurePosixPath(rel).parts
        if (
            PurePosixPath(rel).is_absolute()
            or ".." in rel_parts
            or "\\" in rel
            or (len(rel) > 1 and rel[1] == ":")
            or PurePosixPath(rel).as_posix() != rel
        ):
            raise InstallError(f"manifest lists an unsafe path: {rel}")
        if rel in manifest_paths:
            raise InstallError(f"manifest lists a duplicate path: {rel}")
        manifest_paths.add(rel)
        ordered_paths.append(rel)
        path = top / rel
        if not path.is_file():
            problems.append(rel + " (missing)")
            continue
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != entry["sha256"] or len(payload) != entry["size"]:
            problems.append(rel + " (sha256 mismatch)")
    if ordered_paths != sorted(ordered_paths):
        raise InstallError("package manifest files are not sorted")
    if problems:
        raise InstallError(
            "pack integrity check failed:\n  " + "\n  ".join(problems)
        )
    # The loop above only confirms every MANIFEST-listed file exists on disk
    # with the right hash; it never confirms the reverse -- that nothing
    # extra was extracted. A tar member can pass _validate_member's
    # structural checks (right top dir, no traversal, file/dir only) while
    # never being declared in PACKAGE-MANIFEST.json, in which case it would
    # sail through with zero integrity verification. Reject any such file.
    extra = []
    for path in top.rglob("*"):
        if not path.is_file():
            continue
        rel = str(PurePosixPath(*path.relative_to(top).parts))
        if rel == PACKAGE_MANIFEST_NAME:
            continue
        if rel not in manifest_paths:
            extra.append(rel)
    if extra:
        raise InstallError(
            f"pack contains files not listed in {PACKAGE_MANIFEST_NAME}:\n  "
            + "\n  ".join(sorted(extra))
        )
    if "install.py" not in manifest_paths:
        raise InstallError("package manifest does not bind root install.py")


def read_pack_payload(payload: bytes, archive_name: str, workdir: Path) -> tuple:
    """Boundedly validate and extract one already-captured pack payload."""
    version = pack_version_from_filename(Path(archive_name))
    expected_top = f"{PACK_PREFIX}-{version}"
    if len(payload) > MAX_COMPRESSED_ARCHIVE_BYTES:
        raise InstallError("pack archive exceeds compressed size limit")
    try:
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as tar:
            seen: set[str] = set()
            total = 0
            for position, member in enumerate(tar, start=1):
                if position > MAX_ARCHIVE_MEMBERS:
                    raise InstallError("pack archive exceeds member count limit")
                _validate_member(member, expected_top)
                normalized = PurePosixPath(member.name).as_posix()
                if normalized in seen:
                    raise InstallError(
                        f"duplicate normalized archive member: {member.name}"
                    )
                seen.add(normalized)
                if member.size > MAX_MEMBER_BYTES:
                    raise InstallError("pack archive exceeds member size limit")
                total += member.size
                if total > MAX_TOTAL_BYTES:
                    raise InstallError("pack archive exceeds total size limit")
                if total / max(len(payload), 1) > MAX_COMPRESSION_RATIO:
                    raise InstallError("pack archive exceeds compression ratio limit")
                stream = tar.extractfile(member)
                if stream is None:
                    raise InstallError(f"archive member cannot be read: {member.name}")
                member_payload = stream.read(MAX_MEMBER_BYTES + 1)
                if len(member_payload) != member.size:
                    raise InstallError(f"archive member size drift: {member.name}")
                target = Path(workdir).joinpath(*PurePosixPath(member.name).parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(member_payload)
    except (tarfile.TarError, OSError) as exc:
        raise InstallError(
            f"pack file is corrupt or not a valid archive: {archive_name} ({exc})"
        ) from exc
    top = Path(workdir) / expected_top
    manifest_path = top / PACKAGE_MANIFEST_NAME
    if not manifest_path.is_file():
        raise InstallError(f"pack has no {PACKAGE_MANIFEST_NAME}: {archive_name}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError, OSError) as exc:
        raise InstallError(f"pack has an invalid {PACKAGE_MANIFEST_NAME}") from exc
    if type(manifest) is not dict:
        raise InstallError(f"pack has an invalid {PACKAGE_MANIFEST_NAME}")
    if manifest.get("pack_name") != PACK_PREFIX:
        raise InstallError(f"pack name does not match {PACK_PREFIX}")
    if manifest.get("version") != version:
        raise InstallError(
            f"pack filename says version {version} but {PACKAGE_MANIFEST_NAME} "
            f"says {manifest.get('version')!r}"
        )
    _verify_file_hashes(top, manifest)
    expected_fields = {
        "pack_name",
        "version",
        "build_date_utc",
        "source_commit",
        "file_count",
        "files",
    }
    if set(manifest) != expected_fields:
        raise InstallError("package manifest fields are invalid")
    if not isinstance(manifest.get("source_commit"), str) or re.fullmatch(
        r"[0-9a-f]{40}", manifest["source_commit"]
    ) is None:
        raise InstallError("package manifest source commit is invalid")
    if manifest.get("build_date_utc") != version.split(".", 1)[0]:
        raise InstallError("package manifest build date is invalid")
    canonical = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    if manifest_path.read_bytes() != canonical:
        raise InstallError("package manifest bytes are not canonical")
    return top, manifest


def capture_pack(pack_path: Path) -> tuple[bytes, str, str]:
    """Capture one exact bounded archive payload, digest, and filename version."""
    pack_path = Path(pack_path)
    version = pack_version_from_filename(pack_path)
    payload = _read_stable_regular_file(
        pack_path, "pack archive", MAX_COMPRESSED_ARCHIVE_BYTES
    )
    return payload, hashlib.sha256(payload).hexdigest(), version


def read_pack(pack_path: Path, workdir: Path) -> tuple:
    """Capture, validate, and extract a pack for direct library callers."""
    payload, _digest, _version = capture_pack(pack_path)
    return read_pack_payload(payload, Path(pack_path).name, workdir)


def default_roots() -> dict:
    """Documented per-agent skills roots. Copy targets, never ~/.codex/skills."""
    home = Path.home()
    return {
        "claude": home / ".claude" / "skills",
        "codex": home / ".agents" / "skills",
    }


def find_workspace_ancestor(path: Path):
    """Return the enclosing Workspace checkout root, or None."""
    path = Path(path)
    # Walk from the deepest existing ancestor so non-existent roots still resolve.
    probe = path
    while not probe.exists() and probe.parent != probe:
        probe = probe.parent
    probe = probe.resolve()
    for candidate in (probe,) + tuple(probe.parents):
        if (candidate / WORKSPACE_MARKER).is_file():
            return candidate
    return None


def _shared_rel_to_target(root: Path, rel: str) -> Path:
    parts = PurePosixPath(rel).parts
    if (
        PurePosixPath(rel).is_absolute()
        or ".." in parts
        or "\\" in rel
        or (len(rel) > 1 and rel[1] == ":")
    ):
        raise InstallError(f"unsafe shared file path: {rel}")
    return root.joinpath(*parts)


def _guard_owned_path(path: Path) -> None:
    """Reject unsafe symlinks and paths owned by another local user."""
    current_uid = os.getuid() if hasattr(os, "getuid") else None
    exact = path.absolute()
    for candidate in (exact, *exact.parents):
        try:
            status = candidate.lstat()
        except FileNotFoundError:
            continue
        except OSError as exc:
            raise InstallError(f"cannot inspect target path component {candidate}") from exc
        if stat.S_ISLNK(status.st_mode):
            if candidate == exact or current_uid is None or status.st_uid == current_uid:
                raise InstallError(
                    f"refusing target with symlinked path component: {candidate}"
                )
            try:
                parent_status = candidate.parent.lstat()
            except OSError as exc:
                raise InstallError(
                    f"cannot inspect symlink parent {candidate.parent}"
                ) from exc
            if parent_status.st_uid == current_uid:
                raise InstallError(
                    f"refusing target with symlinked path component: {candidate}"
                )
            continue
        if candidate == exact and current_uid is not None and status.st_uid != current_uid:
            raise InstallError(f"refusing unowned target path: {candidate}")


def _directory_identity(path: Path, label: str) -> tuple[int, int]:
    """Return one regular directory's device/inode identity without following links."""
    try:
        status = Path(path).lstat()
    except OSError as exc:
        raise InstallError(f"cannot inspect {label}: {path}") from exc
    if not stat.S_ISDIR(status.st_mode):
        raise InstallError(f"{label} is not a regular directory: {path}")
    return (status.st_dev, status.st_ino)


def _require_directory_identity(
    path: Path, expected: tuple[int, int], label: str
) -> None:
    actual = _directory_identity(path, label)
    if actual != expected:
        raise InstallError(f"{label} identity changed: {path}")


def _require_absent(path: Path, label: str) -> None:
    try:
        Path(path).lstat()
    except FileNotFoundError:
        return
    except OSError as exc:
        raise InstallError(f"cannot inspect {label}: {path}") from exc
    raise InstallError(f"{label} appeared unexpectedly: {path}")


def _is_absent(path: Path) -> bool:
    try:
        Path(path).lstat()
    except FileNotFoundError:
        return True
    except OSError as exc:
        raise InstallError(f"cannot inspect transaction path: {path}") from exc
    return False


def _remove_owned_directory(
    path: Path, expected: tuple[int, int], label: str
) -> None:
    if _is_absent(path):
        return
    _require_directory_identity(path, expected, label)
    try:
        _rmtree(path)
    except OSError as exc:
        raise InstallError(f"cannot remove {label}: {path}") from exc


def _remove_owned_file(path: Path, expected: tuple[int, int], label: str) -> None:
    if _is_absent(path):
        return
    _require_file_identity(path, expected, label)
    try:
        _clear_readonly_if_present(path)
        path.unlink()
    except OSError as exc:
        raise InstallError(f"cannot remove {label}: {path}") from exc


def _remove_owned_empty_directory(
    path: Path, expected: tuple[int, int], label: str
) -> None:
    if _is_absent(path):
        return
    _require_directory_identity(path, expected, label)
    try:
        path.rmdir()
    except PermissionError:
        try:
            os.chmod(path, stat.S_IWRITE)
            path.rmdir()
        except OSError as exc:
            raise InstallError(f"cannot remove empty {label}: {path}") from exc
    except OSError as exc:
        raise InstallError(f"cannot remove empty {label}: {path}") from exc


def _file_identity(path: Path, label: str) -> tuple[int, int]:
    try:
        status = Path(path).lstat()
    except OSError as exc:
        raise InstallError(f"cannot inspect {label}: {path}") from exc
    if stat.S_ISLNK(status.st_mode):
        raise InstallError(f"{label} is a symlink, not a regular file: {path}")
    if not stat.S_ISREG(status.st_mode):
        raise InstallError(f"{label} is not a regular file: {path}")
    return (status.st_dev, status.st_ino)


def _require_file_identity(
    path: Path, expected: tuple[int, int], label: str
) -> None:
    if _file_identity(path, label) != expected:
        raise InstallError(f"{label} identity changed: {path}")


def _managed_file_entry(
    path: Path, root: Path, scope: str, installed_path: str | None = None
) -> dict:
    payload = _read_stable_regular_file(
        path, f"managed {scope} file", MAX_INSTALLED_FILE_BYTES
    )
    return {
        "path": installed_path
        or PurePosixPath(*path.relative_to(root).parts).as_posix(),
        "scope": scope,
        "kind": "regular",
        "size": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def _omi_inventory_at(omi: Path) -> list[dict]:
    _directory_identity(omi, "installed OMI directory")
    entries = []

    def walk_error(exc: OSError) -> None:
        raise InstallError(f"cannot enumerate installed OMI directory: {exc}")

    for current, directories, files in os.walk(
        omi, topdown=True, followlinks=False, onerror=walk_error
    ):
        current_path = Path(current)
        for name in list(directories):
            _directory_identity(current_path / name, "managed OMI directory")
        for name in files:
            path = current_path / name
            if path == omi / RECEIPT_NAME:
                continue
            relative = PurePosixPath(*path.relative_to(omi).parts).as_posix()
            entries.append(
                _managed_file_entry(
                    path,
                    omi,
                    "omi",
                    f"{OMI_DIR_NAME}/{relative}",
                )
            )
    return sorted(entries, key=lambda entry: entry["path"])


def _omi_managed_inventory(root: Path) -> list[dict]:
    return _omi_inventory_at(root / OMI_DIR_NAME)


def _omi_directories_at(omi: Path) -> list[str]:
    _directory_identity(omi, "installed OMI directory")
    directories = []

    def walk_error(exc: OSError) -> None:
        raise InstallError(f"cannot enumerate installed OMI directory: {exc}")

    for current, names, _files in os.walk(
        omi, topdown=True, followlinks=False, onerror=walk_error
    ):
        current_path = Path(current)
        for name in names:
            path = current_path / name
            _directory_identity(path, "managed OMI directory")
            relative = PurePosixPath(*path.relative_to(omi).parts).as_posix()
            directories.append(f"{OMI_DIR_NAME}/{relative}")
    return sorted(directories)


def _expected_omi_directories(inventory: list[dict]) -> list[str]:
    directories = set()
    for entry in inventory:
        if entry["scope"] != "omi":
            continue
        parts = PurePosixPath(entry["path"]).parts
        for end in range(2, len(parts)):
            directories.add(PurePosixPath(*parts[:end]).as_posix())
    return sorted(directories)


def _verify_omi_directories(
    omi: Path, expected_inventory: list[dict], label: str
) -> None:
    if _omi_directories_at(omi) != _expected_omi_directories(expected_inventory):
        raise InstallError(f"{label} directory inventory drift")


def _build_inventory_from(
    omi: Path, shared_root: Path, shared_rels: list[str]
) -> list[dict]:
    entries = _omi_inventory_at(omi)
    for rel in shared_rels:
        entries.append(
            _managed_file_entry(
                _shared_rel_to_target(shared_root, rel),
                shared_root,
                "shared",
            )
        )
    return sorted(entries, key=lambda entry: entry["path"])


def _build_managed_inventory(root: Path, shared_rels: list[str]) -> list[dict]:
    return _build_inventory_from(root / OMI_DIR_NAME, root, shared_rels)


def _expected_installed_inventory(manifest: dict) -> list[dict]:
    """Translate immutable package-manifest entries to installed paths."""
    declared = manifest.get("files")
    if (
        type(declared) is not list
        or manifest.get("file_count") != len(declared)
    ):
        raise InstallError("package managed inventory is invalid")
    expected = []
    source_paths = []
    for item in declared:
        if type(item) is not dict or set(item) != {"path", "sha256", "size"}:
            raise InstallError("package managed inventory is invalid")
        source_path = item["path"]
        if not isinstance(source_path, str):
            raise InstallError("package managed inventory is invalid")
        source = PurePosixPath(source_path)
        if (
            source.is_absolute()
            or ".." in source.parts
            or "\\" in source_path
            or (len(source_path) > 1 and source_path[1] == ":")
            or source.as_posix() != source_path
        ):
            raise InstallError("package managed inventory path is invalid")
        if (
            type(item["size"]) is not int
            or item["size"] < 0
            or item["size"] > MAX_INSTALLED_FILE_BYTES
            or not isinstance(item["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", item["sha256"]) is None
        ):
            raise InstallError("package managed inventory entry is invalid")
        source_paths.append(source_path)
        if len(source.parts) < 3 or source.parts[0] != "skills":
            continue
        if source.parts[1] == OMI_DIR_NAME:
            scope = "omi"
        elif source.parts[1] == SHARED_DIR_NAME:
            scope = "shared"
        else:
            continue
        expected.append(
            {
                "path": PurePosixPath(*source.parts[1:]).as_posix(),
                "scope": scope,
                "kind": "regular",
                "size": item["size"],
                "sha256": item["sha256"],
            }
        )
    paths = [entry["path"] for entry in expected]
    if (
        source_paths != sorted(source_paths)
        or len(source_paths) != len(set(source_paths))
        or paths != sorted(paths)
        or len(paths) != len(set(paths))
        or not any(entry["scope"] == "omi" for entry in expected)
    ):
        raise InstallError("package managed inventory is not canonical")
    return expected


def _verify_managed_inventory(receipt: dict, root: Path) -> None:
    expected = receipt["managed_files"]
    expected_omi = [entry for entry in expected if entry["scope"] == "omi"]
    actual_omi = _omi_managed_inventory(root)
    if actual_omi != expected_omi:
        raise InstallError("managed OMI inventory drift")
    _verify_omi_directories(
        root / OMI_DIR_NAME, expected, "managed OMI"
    )
    for entry in expected:
        if entry["scope"] != "shared":
            continue
        actual = _managed_file_entry(root.joinpath(*PurePosixPath(entry["path"]).parts), root, "shared")
        if actual != entry:
            raise InstallError("managed shared inventory drift")


def _validate_receipt(receipt: object, root: Path, agent: str | None = None) -> dict:
    fields = {
        "pack_name",
        "version",
        "source_commit",
        "installed_utc",
        "pack_sha256",
        "agent",
        "skills_root",
        "managed_shared_files",
        "managed_files",
    }
    if type(receipt) is not dict or set(receipt) != fields:
        raise InstallError("managed receipt schema is invalid")
    try:
        parse_pack_version(receipt["version"])
    except (InstallError, TypeError) as exc:
        raise InstallError("managed receipt version is invalid") from exc
    expected_root = str(root.resolve(strict=False))
    if (
        receipt["pack_name"] != PACK_PREFIX
        or receipt["skills_root"] != expected_root
        or receipt["agent"] not in {"claude", "codex"}
        or (agent is not None and receipt["agent"] != agent)
        or not isinstance(receipt["source_commit"], str)
        or re.fullmatch(r"[0-9a-f]{40}", receipt["source_commit"]) is None
        or not isinstance(receipt["pack_sha256"], str)
        or re.fullmatch(r"[0-9a-f]{64}", receipt["pack_sha256"]) is None
        or not isinstance(receipt["installed_utc"], str)
        or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", receipt["installed_utc"])
        is None
    ):
        raise InstallError("managed receipt identity is invalid")
    shared = receipt["managed_shared_files"]
    if type(shared) is not list or any(not isinstance(rel, str) for rel in shared):
        raise InstallError("managed receipt shared-file inventory is invalid")
    if shared != sorted(shared) or len(shared) != len(set(shared)):
        raise InstallError("managed receipt shared-file inventory is invalid")
    for rel in shared:
        parts = PurePosixPath(rel).parts
        if len(parts) < 2 or parts[0] != SHARED_DIR_NAME:
            raise InstallError("managed receipt shared-file inventory is invalid")
        _shared_rel_to_target(root, rel)
    managed = receipt["managed_files"]
    if type(managed) is not list or managed != sorted(
        managed, key=lambda entry: entry.get("path", "") if type(entry) is dict else ""
    ):
        raise InstallError("managed file inventory is invalid")
    paths = []
    shared_paths = []
    for entry in managed:
        if type(entry) is not dict or set(entry) != {
            "path", "scope", "kind", "size", "sha256"
        }:
            raise InstallError("managed file inventory is invalid")
        rel = entry["path"]
        if not isinstance(rel, str):
            raise InstallError("managed file inventory is invalid")
        parts = PurePosixPath(rel).parts
        scope = entry["scope"]
        if (
            PurePosixPath(rel).is_absolute()
            or ".." in parts
            or "\\" in rel
            or PurePosixPath(rel).as_posix() != rel
            or entry["kind"] != "regular"
            or type(entry["size"]) is not int
            or entry["size"] < 0
            or entry["size"] > MAX_INSTALLED_FILE_BYTES
            or not isinstance(entry["sha256"], str)
            or re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]) is None
            or scope not in {"omi", "shared"}
            or (scope == "omi" and (not parts or parts[0] != OMI_DIR_NAME))
            or (scope == "shared" and (len(parts) < 2 or parts[0] != SHARED_DIR_NAME))
        ):
            raise InstallError("managed file inventory is invalid")
        paths.append(rel)
        if scope == "shared":
            shared_paths.append(rel)
    if len(paths) != len(set(paths)) or shared_paths != shared or not any(
        entry["scope"] == "omi" for entry in managed
    ):
        raise InstallError("managed file inventory is invalid")
    return receipt


def _read_stable_regular_file(path: Path, label: str, maximum: int) -> bytes:
    """Read one bounded regular file without following or swapping its path."""
    path = Path(path)
    try:
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise InstallError(f"{label} is not a regular file: {path}")
        if before.st_size > maximum:
            raise InstallError(f"{label} is larger than {maximum} bytes: {path}")
        # O_BINARY is essential on Windows: os.open without it reads in TEXT
        # mode and truncates a payload at the first 0x1A byte. A .tgz has many,
        # so the pack read short and tarfile raised EOFError ("Compressed file
        # ended before the end-of-stream marker"), failing the Windows OMI
        # install (product finding P8). O_BINARY is 0 on POSIX.
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
        descriptor = os.open(path, flags)
    except InstallError:
        raise
    except OSError as exc:
        raise InstallError(f"cannot securely open {label}: {path}") from exc

    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or not os.path.samestat(before, opened):
            raise InstallError(f"{label} identity changed before it was opened: {path}")
        payload = bytearray()
        while len(payload) <= maximum:
            chunk = os.read(descriptor, min(65536, maximum + 1 - len(payload)))
            if not chunk:
                break
            payload.extend(chunk)
        after_descriptor = os.fstat(descriptor)
        after_path = path.lstat()
        stable_fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns")
        if (
            len(payload) > maximum
            or not stat.S_ISREG(after_descriptor.st_mode)
            or not stat.S_ISREG(after_path.st_mode)
            or not os.path.samestat(opened, after_descriptor)
            or not os.path.samestat(after_descriptor, after_path)
            or any(
                getattr(opened, field) != getattr(after_descriptor, field)
                for field in stable_fields
            )
            or any(
                getattr(after_descriptor, field) != getattr(after_path, field)
                for field in stable_fields
            )
        ):
            raise InstallError(f"{label} changed while it was being read: {path}")
        return bytes(payload)
    except InstallError:
        raise
    except OSError as exc:
        raise InstallError(f"cannot securely read {label}: {path}") from exc
    finally:
        os.close(descriptor)


def _read_managed_receipt(
    receipt_path: Path, root: Path, agent: str | None = None
) -> dict:
    try:
        payload = _read_stable_regular_file(
            receipt_path, "managed receipt", MAX_RECEIPT_BYTES
        )
        receipt = json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise InstallError(
            f"managed receipt is corrupt/unparseable: {receipt_path}"
        ) from exc
    return _validate_receipt(receipt, root, agent)


def guard_root(root: Path, shared_rel_files: list) -> None:
    """Refuse symlinked targets and Workspace-checkout targets."""
    root = Path(root).expanduser()
    _guard_owned_path(root)
    workspace = find_workspace_ancestor(root)
    if workspace is not None:
        raise InstallError(
            f"refusing to install into {root}: it is inside the Workspace checkout "
            f"at {workspace}. This installer is for colleague machines; the "
            "Workspace uses symlink live-links "
            "(docs/CANONICAL-LIVE-INSTALL-STRATEGY.md)."
        )
    targets = [
        root / OMI_DIR_NAME,
        root / (OMI_DIR_NAME + ".installing-tmp"),
        root / TRANSACTION_STAGE_NAME,
        root / TRANSACTION_BACKUP_NAME,
        root / SHARED_DIR_NAME,
    ]
    targets += [_shared_rel_to_target(root, rel) for rel in shared_rel_files]
    for target in targets:
        _guard_owned_path(target)


def _rmtree(path: Path) -> None:
    """rmtree that clears the read-only bit first (needed on Windows)."""
    def _onerror(func, target, exc_info):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    shutil.rmtree(path, onerror=_onerror)


def _clear_readonly_if_present(path: Path) -> None:
    """Best-effort: clear the read-only bit before unlink/overwrite (Windows)."""
    try:
        if path.exists():
            os.chmod(path, stat.S_IWRITE)
    except OSError:
        pass


def _shared_rel_files(manifest: dict) -> list:
    """Manifest paths under skills/shared/, re-rooted at the skills root."""
    rels = []
    for entry in manifest.get("files", []):
        parts = PurePosixPath(entry["path"]).parts
        if len(parts) >= 3 and parts[0] == "skills" and parts[1] == SHARED_DIR_NAME:
            rels.append("/".join(parts[1:]))
    return sorted(rels)


def install_into_root(top: Path, manifest: dict, root: Path, agent: str,
                      pack_sha256: str, dry_run: bool = False) -> dict:
    """Install (or cleanly update) the pack under one skills root.

    Returns a summary dict: {"root", "version", "replaced_version"}.
    """
    root = Path(root).expanduser()
    omi_src = top / "skills" / OMI_DIR_NAME
    if not omi_src.is_dir():
        raise InstallError(
            f"pack is missing {OMI_DIR_NAME}/ under skills/: {omi_src}"
        )
    expected_inventory = _expected_installed_inventory(manifest)
    shared_rels = _shared_rel_files(manifest)
    expected_shared_rels = [
        entry["path"] for entry in expected_inventory if entry["scope"] == "shared"
    ]
    if shared_rels != expected_shared_rels:
        raise InstallError("package managed shared inventory drift")
    omi_target = root / OMI_DIR_NAME
    receipt_path = omi_target / RECEIPT_NAME
    tmp_target = root / (OMI_DIR_NAME + ".installing-tmp")
    transaction_stage = root / TRANSACTION_STAGE_NAME
    transaction_backup = root / TRANSACTION_BACKUP_NAME
    guard_root(root, shared_rels)

    for residue, label in (
        (tmp_target, "existing unowned staging target"),
        (transaction_stage, "transaction staging residue requiring recovery"),
        (transaction_backup, "transaction backup residue requiring recovery"),
    ):
        if not _is_absent(residue):
            raise InstallError(
                f"refusing {label} {residue}; preserve it and remove or rename it "
                "manually only after recovery is complete"
            )

    prior = None
    managed_omi_identity = None
    if not _is_absent(omi_target):
        managed_omi_identity = _directory_identity(
            omi_target, "managed OMI directory"
        )
        if _is_absent(receipt_path):
            raise InstallError(
                f"{omi_target} exists but has no {RECEIPT_NAME}, so it is "
                "not managed by this installer. Remove or rename it manually "
                "if you want the installer to take over."
            )
        prior = _read_managed_receipt(receipt_path, root, agent)
        guard_root(root, prior["managed_shared_files"])
        _verify_managed_inventory(prior, root)

    prior_shared = set(prior["managed_shared_files"]) if prior else set()
    guarded_shared_rels = sorted(set(shared_rels) | prior_shared)
    guard_root(root, guarded_shared_rels)
    prior_shared_identities = {}
    for rel in sorted(prior_shared):
        target = _shared_rel_to_target(root, rel)
        _guard_owned_path(target)
        prior_shared_identities[rel] = _file_identity(
            target, "managed shared file"
        )
    for rel in shared_rels:
        target = _shared_rel_to_target(root, rel)
        if rel not in prior_shared and not _is_absent(target):
            raise InstallError(
                f"refusing to overwrite existing unowned target {target}; "
                "it is not managed by this installer"
            )

    summary = {
        "root": str(root),
        "version": manifest["version"],
        "replaced_version": prior.get("version") if prior else None,
    }
    if dry_run:
        return summary

    guard_root(root, guarded_shared_rels)
    root_was_absent = _is_absent(root)
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise InstallError(f"cannot create skills root {root}") from exc

    staging_identity = None
    transaction_stage_identity = None
    backup_identity = None
    staged_shared_identities = {}
    activated_shared_identities = {}
    omi_activation_attempted = False
    rollback_errors = []
    created_directory_identities = {}
    if root_was_absent:
        created_directory_identities[root] = _directory_identity(
            root, "transaction-created skills root"
        )

    def ensure_transaction_parents(path: Path) -> None:
        missing = []
        candidate = path
        while candidate != root and _is_absent(candidate):
            missing.append(candidate)
            candidate = candidate.parent
        for directory in reversed(missing):
            directory.mkdir()
            created_directory_identities[directory] = _directory_identity(
                directory, "transaction-created parent directory"
            )

    def cleanup_owned(path: Path, identity, label: str) -> None:
        if identity is None:
            return
        try:
            _remove_owned_directory(path, identity, label)
        except InstallError as cleanup_error:
            rollback_errors.append(str(cleanup_error))

    def rollback() -> None:
        # Remove only transaction-created active paths whose identities still
        # match. Any foreign replacement is preserved and makes recovery manual.
        if (
            omi_activation_attempted
            and staging_identity is not None
            and not _is_absent(omi_target)
        ):
            try:
                _remove_owned_directory(
                    omi_target, staging_identity, "transaction-installed OMI directory"
                )
            except InstallError as rollback_error:
                rollback_errors.append(str(rollback_error))
        for rel, expected in activated_shared_identities.items():
            target = _shared_rel_to_target(root, rel)
            if not _is_absent(target):
                try:
                    _remove_owned_file(
                        target, expected, "transaction-installed shared file"
                    )
                except InstallError as rollback_error:
                    rollback_errors.append(str(rollback_error))

        if backup_identity is not None:
            backup_omi = transaction_backup / OMI_DIR_NAME
            if managed_omi_identity is not None and not _is_absent(backup_omi):
                try:
                    _require_directory_identity(
                        backup_omi, managed_omi_identity, "backed-up OMI directory"
                    )
                    _require_absent(omi_target, "OMI rollback target")
                    backup_omi.rename(omi_target)
                    _require_directory_identity(
                        omi_target, managed_omi_identity, "restored OMI directory"
                    )
                except (InstallError, OSError) as rollback_error:
                    rollback_errors.append(f"cannot restore prior OMI: {rollback_error}")
            for rel, expected in prior_shared_identities.items():
                backup_file = _shared_rel_to_target(transaction_backup, rel)
                if _is_absent(backup_file):
                    continue
                target = _shared_rel_to_target(root, rel)
                try:
                    _require_file_identity(
                        backup_file, expected, "backed-up shared file"
                    )
                    _require_absent(target, "shared rollback target")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    backup_file.rename(target)
                    _require_file_identity(
                        target, expected, "restored shared file"
                    )
                except (InstallError, OSError) as rollback_error:
                    rollback_errors.append(
                        f"cannot restore prior shared file {rel}: {rollback_error}"
                    )

        cleanup_owned(tmp_target, staging_identity, "installer staging directory")
        cleanup_owned(
            transaction_stage,
            transaction_stage_identity,
            "transaction staging directory",
        )
        if backup_identity is not None and not rollback_errors:
            cleanup_owned(
                transaction_backup, backup_identity, "transaction backup directory"
            )
        for directory, identity in sorted(
            created_directory_identities.items(),
            key=lambda item: len(item[0].parts),
            reverse=True,
        ):
            try:
                _remove_owned_empty_directory(
                    directory, identity, "transaction-created parent directory"
                )
            except InstallError as rollback_error:
                rollback_errors.append(str(rollback_error))

    try:
        tmp_target.mkdir()
        staging_identity = _directory_identity(
            tmp_target, "installer staging directory"
        )
        transaction_stage.mkdir()
        transaction_stage_identity = _directory_identity(
            transaction_stage, "transaction staging directory"
        )
        shutil.copytree(omi_src, tmp_target, dirs_exist_ok=True)
        _require_directory_identity(
            tmp_target, staging_identity, "installer staging directory"
        )
        if managed_omi_identity is not None:
            _require_directory_identity(
                omi_target, managed_omi_identity, "managed OMI directory"
            )
        for rel in shared_rels:
            source = _shared_rel_to_target(top / "skills", rel)
            staged = _shared_rel_to_target(transaction_stage, rel)
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, staged)
            staged_shared_identities[rel] = _file_identity(
                staged, "staged shared file"
            )
        staged_inventory = _build_inventory_from(
            tmp_target, transaction_stage, shared_rels
        )
        if staged_inventory != expected_inventory:
            raise InstallError("staged managed inventory drift from package manifest")
        _verify_omi_directories(
            tmp_target, expected_inventory, "staged OMI"
        )

        guard_root(root, guarded_shared_rels)
        _require_directory_identity(
            tmp_target, staging_identity, "installer staging directory"
        )
        transaction_backup.mkdir()
        backup_identity = _directory_identity(
            transaction_backup, "transaction backup directory"
        )

        if managed_omi_identity is not None:
            _require_directory_identity(
                omi_target, managed_omi_identity, "managed OMI directory"
            )
            omi_target.rename(transaction_backup / OMI_DIR_NAME)
            _require_directory_identity(
                transaction_backup / OMI_DIR_NAME,
                managed_omi_identity,
                "backed-up OMI directory",
            )
        else:
            _require_absent(omi_target, "unmanaged OMI target")

        for rel, expected in prior_shared_identities.items():
            target = _shared_rel_to_target(root, rel)
            _require_file_identity(target, expected, "managed shared file")
            backup_file = _shared_rel_to_target(transaction_backup, rel)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            target.rename(backup_file)
            _require_file_identity(backup_file, expected, "backed-up shared file")

        _require_absent(omi_target, "OMI replacement target")
        _require_directory_identity(
            tmp_target, staging_identity, "installer staging directory"
        )
        omi_activation_attempted = True
        tmp_target.rename(omi_target)
        _require_directory_identity(
            omi_target, staging_identity, "installed OMI directory"
        )

        for rel, expected in staged_shared_identities.items():
            guard_root(root, guarded_shared_rels)
            staged = _shared_rel_to_target(transaction_stage, rel)
            target = _shared_rel_to_target(root, rel)
            _require_file_identity(staged, expected, "staged shared file")
            _require_absent(target, "shared replacement target")
            ensure_transaction_parents(target.parent)
            activated_shared_identities[rel] = expected
            staged.rename(target)
            _require_file_identity(target, expected, "installed shared file")

        installed_inventory = _build_managed_inventory(root, shared_rels)
        if installed_inventory != expected_inventory:
            raise InstallError(
                "installed managed inventory drift from package manifest"
            )
        _verify_omi_directories(
            omi_target, expected_inventory, "installed OMI"
        )
        receipt = {
            "pack_name": manifest["pack_name"],
            "version": manifest["version"],
            "source_commit": manifest.get("source_commit"),
            "installed_utc": datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            ),
            "pack_sha256": pack_sha256,
            "agent": agent,
            "skills_root": str(root.resolve(strict=False)),
            "managed_shared_files": shared_rels,
            "managed_files": expected_inventory,
        }
        _require_directory_identity(
            omi_target, staging_identity, "installed OMI directory"
        )
        _require_absent(receipt_path, "managed receipt target")
        receipt_path.write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )
        validated_receipt = _read_managed_receipt(receipt_path, root, agent)
        if validated_receipt["managed_files"] != expected_inventory:
            raise InstallError("managed receipt inventory drift")
        _verify_managed_inventory(validated_receipt, root)
    except (InstallError, OSError) as exc:
        try:
            rollback()
        except (InstallError, OSError) as rollback_error:
            rollback_errors.append(str(rollback_error))
        if rollback_errors:
            raise InstallError(
                "transaction failed and rollback requires manual recovery; "
                f"preserved transaction residue under {root}: {exc}; "
                + "; ".join(rollback_errors)
            ) from exc
        raise InstallError(
            f"transaction failed; prior install restored: {exc}"
        ) from exc

    # Receipt and final-inventory validation above are the commit boundary.
    # Cleanup failures after this point must never roll back the valid active
    # installation or attempt to restore a possibly partially deleted backup.
    cleanup_errors = []
    for path, identity, label in (
        (
            transaction_stage,
            transaction_stage_identity,
            "transaction staging directory",
        ),
        (
            transaction_backup,
            backup_identity,
            "transaction backup directory",
        ),
    ):
        try:
            _remove_owned_directory(path, identity, label)
        except InstallError as cleanup_error:
            cleanup_errors.append(str(cleanup_error))
    if cleanup_errors:
        raise InstallError(
            "installation committed with a valid active inventory, but transaction "
            f"cleanup requires operator recovery under {root}; preserve and inspect "
            "the residue before removing it, then rerun --check: "
            + "; ".join(cleanup_errors)
        )
    return summary


def check_root(
    root: Path, latest_version: str, expected_pack_sha256: str | None = None
) -> tuple:
    """Classify one skills root vs the latest version.

    Returns (status, installed_version_or_None); status is one of
    "up-to-date", "outdated", "not-installed", "unmanaged", "live-link",
    "recovery-needed".
    """
    root = Path(root).expanduser()
    for residue in (
        root / (OMI_DIR_NAME + ".installing-tmp"),
        root / TRANSACTION_STAGE_NAME,
        root / TRANSACTION_BACKUP_NAME,
    ):
        try:
            residue.lstat()
        except FileNotFoundError:
            continue
        except OSError:
            return ("recovery-needed", None)
        return ("recovery-needed", None)
    omi_target = root / OMI_DIR_NAME
    if omi_target.is_symlink():
        return ("live-link", None)
    receipt_path = omi_target / RECEIPT_NAME
    try:
        receipt_path.lstat()
    except FileNotFoundError:
        if omi_target.exists():
            return ("unmanaged", None)
        return ("not-installed", None)
    except OSError:
        return ("unmanaged", None)
    try:
        receipt = _read_managed_receipt(receipt_path, root)
        _verify_managed_inventory(receipt, root)
    except InstallError:
        return ("unmanaged", None)
    installed = receipt.get("version", "")
    if (
        expected_pack_sha256 is not None
        and receipt.get("pack_sha256") != expected_pack_sha256
    ):
        return ("outdated", installed or None)
    try:
        if parse_pack_version(installed) >= parse_pack_version(latest_version):
            return ("up-to-date", installed)
    except InstallError:
        return ("unmanaged", None)
    return ("outdated", installed)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Install the OMI colleague pack into Claude Code and Codex "
            "skill directories (colleague machines only; copies, never symlinks)."
        )
    )
    parser.add_argument("--repo-root", type=Path, default=Path("."),
                        help="repo checkout containing dist/ (default: .)")
    parser.add_argument("--pack", type=Path, default=None,
                        help="explicit pack .tgz (overrides dist/ resolution)")
    parser.add_argument("--agent", choices=["claude", "codex", "both"],
                        default="both")
    parser.add_argument("--claude-root", type=Path, default=None,
                        help="override the Claude Code skills root")
    parser.add_argument("--codex-root", type=Path, default=None,
                        help="override the Codex skills root")
    parser.add_argument("--check", action="store_true",
                        help="report installed vs latest; make no changes")
    parser.add_argument("--dry-run", action="store_true",
                        help="print what would happen; make no changes")
    args = parser.parse_args(argv)

    roots = default_roots()
    overridden = set()
    if args.claude_root is not None:
        roots["claude"] = args.claude_root
        overridden.add("claude")
    if args.codex_root is not None:
        roots["codex"] = args.codex_root
        overridden.add("codex")
    selected = ["claude", "codex"] if args.agent == "both" else [args.agent]

    try:
        pack_path = args.pack if args.pack is not None else resolve_latest_pack(
            Path(args.repo_root) / "dist"
        )
        latest_version = pack_version_from_filename(pack_path)

        if args.check:
            pack_payload, pack_sha, captured_version = capture_pack(pack_path)
            if captured_version != latest_version:
                raise InstallError("pack archive version changed while capturing")
            with tempfile.TemporaryDirectory(prefix="omi-pack-check-") as work:
                read_pack_payload(pack_payload, Path(pack_path).name, Path(work))
            worst = 0
            for agent in selected:
                status, installed = check_root(
                    roots[agent], latest_version, expected_pack_sha256=pack_sha
                )
                detail = f"installed {installed}, latest {latest_version}" \
                    if installed else f"latest {latest_version}"
                print(f"[{agent}] {status} ({detail}) root={roots[agent]}")
                if status in (
                    "not-installed",
                    "unmanaged",
                    "outdated",
                    "recovery-needed",
                ):
                    worst = 2
            return worst

        defaults_in_use = [a for a in selected if a not in overridden]
        if defaults_in_use:
            workspace = find_workspace_ancestor(Path.cwd())
            if workspace is not None:
                raise InstallError(
                    "refusing to install to default skill roots from inside "
                    f"the Workspace checkout at {workspace}. This machine "
                    "uses symlink live-links; the installer is for "
                    "colleague machines. (Explicit --claude-root/"
                    "--codex-root scratch targets are allowed.)"
                )

        pack_payload, pack_sha, captured_version = capture_pack(pack_path)
        if captured_version != latest_version:
            raise InstallError("pack archive version changed while capturing")
        with tempfile.TemporaryDirectory(prefix="omi-pack-install-") as work:
            top, manifest = read_pack_payload(
                pack_payload, Path(pack_path).name, Path(work)
            )
            for agent in selected:
                summary = install_into_root(
                    top, manifest, roots[agent], agent=agent,
                    pack_sha256=pack_sha, dry_run=args.dry_run,
                )
                verb = "would install" if args.dry_run else "installed"
                replaced = summary["replaced_version"]
                suffix = f" (replacing {replaced})" if replaced else ""
                print(f"[{agent}] {verb} {manifest['pack_name']} "
                      f"{manifest['version']}{suffix} -> {summary['root']}")
        return 0
    except InstallError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
