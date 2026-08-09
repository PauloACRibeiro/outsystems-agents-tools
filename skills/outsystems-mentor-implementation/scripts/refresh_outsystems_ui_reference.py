#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO_URL = "https://github.com/OutSystems/outsystems-ui.git"
CANONICAL_SCP_REPO_URL = "git@github.com:OutSystems/outsystems-ui.git"
DEFAULT_BRANCH = "dev"
REMOTE_LOOKUP_TIMEOUT_SECONDS = 15
CLONE_TIMEOUT_SECONDS = 30
MAX_GIT_DETAIL_CHARS = 500
MAX_SOURCE_DISPLAY_CHARS = 200
MAX_SOURCE_ERROR_CHARS = 1000
SOURCE_REPO = "OutSystems/outsystems-ui"
CONTENT_ROOT = Path("src")
SCSS_ROOT = CONTENT_ROOT / "scss"
SCRIPTS_ROOT = CONTENT_ROOT / "scripts"


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end].strip("\n")
    body_start = text.find("\n", end + 4)
    body = text[body_start + 1 :] if body_start != -1 else ""
    data = {}
    current_key = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            values = data.setdefault(current_key, [])
            if isinstance(values, list):
                values.append(line[4:].strip().strip("\"'"))
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        current_key = key.strip()
        value = value.strip().strip("\"'")
        data[current_key] = value if value else []
    return data, body


def first_heading(body, fallback):
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    if match:
        return re.sub(r"`|\*", "", match.group(1)).strip()
    stem = fallback.stem
    stem = re.sub(r"Config$", "", stem)
    return stem.replace("-", " ").replace("_", " ").title()


def first_paragraph(body):
    lines = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", "|", "!", "<", "- ")):
            if lines:
                break
            continue
        if re.match(r"^\d+\.", line):
            if lines:
                break
            continue
        lines.append(re.sub(r"\s+", " ", line))
    return " ".join(lines)


def parse_properties(body):
    properties = []
    section_match = re.search(
        r"^##\s+Properties\s*\n(?P<section>.*?)(?=^##\s+|\Z)",
        body,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    if not section_match:
        return properties
    for table_match in re.finditer(r"(?P<table>(?:^\|.*\n?)+)", section_match.group("section"), re.MULTILINE):
        for line in table_match.group("table").splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2:
                continue
            if cells[0].lower() == "property" or set(cells[0]) <= {"-", ":"}:
                continue
            name = cells[0].split("(")[0].strip()
            default_value = cells[1].strip() if len(cells) >= 3 else ""
            properties.append(
                {
                    "name": name,
                    "default_value": default_value,
                    "description": cells[-1].strip(),
                }
            )
    unique = {item["name"]: item for item in properties if item["name"]}
    return [unique[name] for name in sorted(unique)]


def extract_ts_properties(text):
    properties = []
    for prop_type in re.findall(r"\bpublic\s+([A-Z][A-Za-z0-9_]*)\s*:\s*([^;]+);", text):
        name, type_name = prop_type
        properties.append(
            {
                "name": name,
                "default_value": "",
                "description": f"Implementation configuration property typed as {type_name.strip()}.",
            }
        )
    for key, default in re.findall(
        r"case\s+Enum\.Properties\.([A-Z][A-Za-z0-9_]*):.*?validate[A-Za-z]+\([^,]+,\s*([^)]+)\)",
        text,
        re.DOTALL,
    ):
        for item in properties:
            if item["name"] == key:
                item["default_value"] = default.strip()
                break
    unique = {item["name"]: item for item in properties if item["name"]}
    return [unique[name] for name in sorted(unique)]


def extract_events(body):
    non_events = {"OnPhone", "OnTablet", "OnDesktop"}
    return sorted(
        {
            event
            for event in re.findall(r"\bOn[A-Z][A-Za-z0-9]+", body)
            if event not in non_events
        }
    )


def extract_slots(body):
    slots = set()
    for match in re.findall(r"\b([A-Z][A-Za-z0-9]*(?:Content|Placeholder|Slot))\b", body):
        slots.add(match)
    if "placeholder" in body.lower():
        slots.add("Pattern placeholders described in source")
    return sorted(slots)


def extract_notes(body, keywords):
    notes = []
    for paragraph in re.split(r"\n\s*\n", body):
        clean = re.sub(r"\s+", " ", paragraph.strip())
        if not clean or clean.startswith(("#", "|", "![", "- ")):
            continue
        lowered = clean.lower()
        if any(keyword in lowered for keyword in keywords):
            notes.append(clean)
    return notes[:4]


def normalize_gap_family(path):
    stem = path.stem.lstrip("_")
    generic_ts_stems = {
        "builder",
        "callbacks",
        "constants",
        "controller",
        "enum",
        "helper",
        "interface",
        "interfaces",
        "model",
        "parser",
        "provider",
        "service",
        "types",
        "utils",
        "utilities",
    }
    if path.suffix == ".ts" and stem.lower() in generic_ts_stems and path.parent.name:
        stem = path.parent.name
    stem = re.sub(r"-(deprecated|preview|odc|o11)$", "", stem, flags=re.IGNORECASE)
    stem = re.sub(r"API$", "", stem)
    stem = re.sub(r"(?<!^)(?=[A-Z])", "-", stem)
    normalized = re.sub(r"[^a-z0-9]+", "-", stem.lower()).strip("-")
    return normalized or "misc"


def collect_gap_markers(path):
    joined = "/".join(part.lower() for part in path.parts)
    markers = []
    if path.stem.endswith("API"):
        markers.append("api")
    if "deprecated" in joined:
        markers.append("deprecated")
    if "preview" in joined or "servicestudio" in joined:
        markers.append("preview")
    if re.search(r"(^|[-_/])odc($|[-_/])", joined):
        markers.append("odc")
    if re.search(r"(^|[-_/])o11($|[-_/])", joined):
        markers.append("o11")
    return markers


def summarize_gap_families(paths):
    families = {}
    for path in paths:
        family = normalize_gap_family(path)
        bucket = families.setdefault(
            family,
            {"family": family, "file_count": 0, "markers": set(), "sample_paths": []},
        )
        bucket["file_count"] += 1
        bucket["markers"].update(collect_gap_markers(path))
        bucket["sample_paths"].append(path.as_posix())
    return [
        {
            "family": family,
            "file_count": item["file_count"],
            "markers": sorted(item["markers"]),
            "sample_paths": sorted(item["sample_paths"])[:3],
        }
        for family, item in sorted(
            families.items(),
            key=lambda pair: (-pair[1]["file_count"], pair[0]),
        )
    ]


def analyze_gap_surface(source_root):
    source_root = Path(source_root)
    scss_paths = sorted(path.relative_to(source_root) for path in (source_root / SCSS_ROOT).rglob("*.scss"))
    ts_paths = sorted(
        path.relative_to(source_root)
        for path in (source_root / SCRIPTS_ROOT).rglob("*.ts")
        if not path.name.endswith("Config.ts")
    )
    return {
        "scss": {
            "file_count": len(scss_paths),
            "deprecated_file_count": sum(1 for path in scss_paths if "deprecated" in path.as_posix().lower()),
            "preview_file_count": sum(
                1
                for path in scss_paths
                if any(token in path.as_posix().lower() for token in ["preview", "servicestudio"])
            ),
            "platform_variants": {
                "odc": [path.as_posix() for path in scss_paths if "odc" in path.as_posix().lower()],
                "o11": [path.as_posix() for path in scss_paths if "o11" in path.as_posix().lower()],
            },
            "families": summarize_gap_families(scss_paths),
        },
        "ts": {
            "non_config_file_count": len(ts_paths),
            "api_file_count": sum(1 for path in ts_paths if path.stem.endswith("API")),
            "families": summarize_gap_families(ts_paths),
        },
    }


def git_value(source_root, args, fallback):
    try:
        result = subprocess.run(
            ["git", "-C", str(source_root), *args],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return fallback
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else fallback


def bounded_git_detail(value):
    detail = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(detail) > MAX_GIT_DETAIL_CHARS:
        return detail[:MAX_GIT_DETAIL_CHARS] + "..."
    return detail


def bounded_text(value, limit):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if len(text) <= limit else text[:limit] + "..."


def resolve_explicit_source(raw_source):
    try:
        return Path(raw_source).expanduser().resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        message = (
            f"Unable to resolve explicit --source '{bounded_text(raw_source, MAX_SOURCE_DISPLAY_CHARS)}': "
            f"{bounded_git_detail(exc)}. No clone fallback is used for explicit --source."
        )
        raise SystemExit(bounded_text(message, MAX_SOURCE_ERROR_CHARS)) from exc


def normalized_repo_identity(repo_url):
    if repo_url in {DEFAULT_REPO_URL, CANONICAL_SCP_REPO_URL}:
        return DEFAULT_REPO_URL
    return None


def valid_git_object_id(value):
    return bool(re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", value))


def isolated_git_environment():
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
        }
    )
    return env


class ClonedRepo:
    def __init__(self, temporary_directory, checkout_root):
        self._temporary_directory = temporary_directory
        self.name = str(checkout_root)

    def cleanup(self):
        self._temporary_directory.cleanup()


def required_git_value(source_root, args, requirement, allow_empty=False):
    command = ["git", "-C", str(source_root), *args]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f"{requirement} could not run Git: {bounded_git_detail(exc)}") from exc
    value = result.stdout.strip()
    if result.returncode != 0 or (not value and not allow_empty):
        detail = bounded_git_detail(result.stderr or result.stdout or f"Git exited with status {result.returncode}")
        raise ValueError(f"{requirement} failed: {detail}")
    return value


def required_origin_url(source_root):
    command = ["git", "-C", str(source_root), "config", "--local", "--null", "--get-all", "remote.origin.url"]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f"Git origin check could not run Git: {bounded_git_detail(exc)}") from exc
    raw = result.stdout
    values = raw[:-1].split("\0") if raw.endswith("\0") else []
    if result.returncode != 0 or len(values) != 1 or not values[0]:
        detail = bounded_git_detail(result.stderr or raw or f"Git exited with status {result.returncode}")
        raise ValueError(f"Git origin check requires exactly one nonempty remote.origin.url: {detail}")
    origin = values[0]
    if normalized_repo_identity(origin) is None:
        raise ValueError(f"Git origin mismatch; URL is not an exact allowlisted value: {bounded_git_detail(origin)}")
    return origin


def reject_hidden_index_flags(source_root):
    command = ["git", "-C", str(source_root), "ls-files", "-v", "-z"]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f"tracked index flags check could not run Git: {bounded_git_detail(exc)}") from exc
    if result.returncode != 0:
        detail = bounded_git_detail(result.stderr or result.stdout or f"Git exited with status {result.returncode}")
        raise ValueError(f"tracked index flags check failed: {detail}")
    suspicious = []
    for record in result.stdout.split("\0"):
        if not record:
            continue
        if len(record) < 3 or record[1] != " ":
            raise ValueError(f"tracked index flags check returned malformed output: {bounded_git_detail(record)}")
        status, path = record[0], record[2:]
        if status.islower() or status in {"S", "s"}:
            suspicious.append(f"{status} {path}")
    if suspicious:
        raise ValueError(f"tracked index flags detected: {bounded_git_detail(chr(10).join(suspicious))}")


def require_clean_checkout(source_root):
    reject_hidden_index_flags(source_root)
    command = [
        "git",
        "-c", "core.fileMode=false",
        "-c", "core.ignoreStat=false",
        "-c", "core.trustctime=true",
        "-c", "core.fsmonitor=false",
        "-C", str(source_root),
        "diff", "--quiet", "--no-ext-diff", "HEAD", "--",
    ]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f"tracked changes check could not run Git: {bounded_git_detail(exc)}") from exc
    if result.returncode == 1:
        raise ValueError("tracked changes detected by git diff --quiet HEAD --")
    if result.returncode != 0:
        detail = bounded_git_detail(result.stderr or result.stdout or f"Git exited with status {result.returncode}")
        raise ValueError(f"tracked changes check failed: {detail}")

    untracked = required_git_value(
        source_root,
        ["ls-files", "--others", "--exclude-standard"],
        "untracked files check",
        allow_empty=True,
    )
    if untracked:
        raise ValueError(f"untracked files detected: {bounded_git_detail(untracked)}")
    ignored = required_git_value(
        source_root,
        ["ls-files", "--others", "--ignored", "--exclude-standard"],
        "ignored untracked files check",
        allow_empty=True,
    )
    if ignored:
        raise ValueError(f"ignored untracked files detected: {bounded_git_detail(ignored)}")


def authoritative_remote_head():
    remote_ref = f"refs/heads/{DEFAULT_BRANCH}"
    command = ["git", "ls-remote", "--exit-code", DEFAULT_REPO_URL, remote_ref]
    env = isolated_git_environment()
    try:
        with tempfile.TemporaryDirectory() as lookup_root:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=REMOTE_LOOKUP_TIMEOUT_SECONDS,
                env=env,
                cwd=lookup_root,
            )
    except subprocess.TimeoutExpired as exc:
        raise ValueError(
            f"authoritative remote lookup timed out after {REMOTE_LOOKUP_TIMEOUT_SECONDS}s"
        ) from exc
    except OSError as exc:
        raise ValueError(f"authoritative remote lookup could not run Git: {bounded_git_detail(exc)}") from exc
    if result.returncode != 0:
        detail = bounded_git_detail(result.stderr or result.stdout or f"Git exited with status {result.returncode}")
        raise ValueError(f"authoritative remote lookup failed: {detail}")
    fields = result.stdout.strip().split()
    if len(fields) != 2 or fields[1] != remote_ref or not valid_git_object_id(fields[0]):
        raise ValueError(f"authoritative remote lookup returned an invalid response: {bounded_git_detail(result.stdout)}")
    return fields[0]


def validate_explicit_source(source_root):
    source_root = resolve_explicit_source(source_root)
    no_fallback = "No clone fallback is used for explicit --source."
    try:
        top_level = required_git_value(source_root, ["rev-parse", "--show-toplevel"], "Git top-level checkout check")
        if Path(top_level).resolve() != source_root:
            raise ValueError(f"Git top-level checkout mismatch: expected {source_root}, got {Path(top_level).resolve()}")
        origin = required_origin_url(source_root)
        if normalized_repo_identity(origin) != normalized_repo_identity(DEFAULT_REPO_URL):
            raise ValueError(f"Git origin mismatch: expected {DEFAULT_REPO_URL}, got {bounded_git_detail(origin)}")
        branch = required_git_value(source_root, ["branch", "--show-current"], "Git branch check")
        if branch != DEFAULT_BRANCH:
            raise ValueError(f"Git branch mismatch: expected {DEFAULT_BRANCH}, got {bounded_git_detail(branch)}")
        head = required_git_value(source_root, ["rev-parse", "--verify", "HEAD^{commit}"], "valid HEAD commit check")
        if not valid_git_object_id(head):
            raise ValueError(f"valid HEAD commit check returned an invalid object id: {bounded_git_detail(head)}")
        remote_ref = f"refs/remotes/origin/{DEFAULT_BRANCH}"
        remote_head = required_git_value(
            source_root,
            ["rev-parse", "--verify", f"{remote_ref}^{{commit}}"],
            f"origin/{DEFAULT_BRANCH} remote-tracking ref check",
        )
        if not valid_git_object_id(remote_head):
            raise ValueError(f"origin/{DEFAULT_BRANCH} remote-tracking ref returned an invalid object id")
        if head != remote_head:
            raise ValueError(
                f"HEAD mismatch: local HEAD {head} must equal origin/{DEFAULT_BRANCH} {remote_head}"
            )
        require_clean_checkout(source_root)
        authoritative_head = authoritative_remote_head()
        if head != authoritative_head:
            raise ValueError(
                f"authoritative remote HEAD mismatch: local HEAD {head} must equal "
                f"{DEFAULT_REPO_URL} {DEFAULT_BRANCH} {authoritative_head}"
            )
    except ValueError as exc:
        message = (
            f"Invalid explicit --source '{bounded_text(source_root, MAX_SOURCE_DISPLAY_CHARS)}': "
            f"{bounded_git_detail(exc)}. Use the top-level {DEFAULT_REPO_URL} checkout on branch "
            f"{DEFAULT_BRANCH} at origin/{DEFAULT_BRANCH} with a clean working tree. {no_fallback}"
        )
        raise SystemExit(bounded_text(message, MAX_SOURCE_ERROR_CHARS)) from exc
    return {
        "top_level": source_root,
        "origin": origin,
        "branch": branch,
        "head": head,
        "remote_head": remote_head,
        "authoritative_head": authoritative_head,
    }


def source_url(commit, relative_path):
    return f"https://github.com/{SOURCE_REPO}/blob/{commit}/{relative_path.as_posix()}"


def source_alias(branch, relative_path):
    return f"https://github.com/{SOURCE_REPO}/blob/{branch}/{relative_path.as_posix()}"


def markdown_reference_entry(source_root, path, commit, branch):
    relative = path.relative_to(source_root)
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, body = parse_frontmatter(text)
    properties = parse_properties(body)
    events = extract_events(body)
    slots = extract_slots(body)
    compatibility = extract_notes(body, ["compatib", "dependency", "requires", "do not", "avoid", "note"])
    return implementation_entry(
        relative=relative,
        name=first_heading(body, path),
        purpose=frontmatter.get("summary") or first_paragraph(body),
        properties=properties,
        events=events,
        slots=slots,
        compatibility=compatibility,
        commit=commit,
        branch=branch,
    )


def ts_reference_entry(source_root, path, commit, branch):
    relative = path.relative_to(source_root)
    text = path.read_text(encoding="utf-8", errors="replace")
    properties = extract_ts_properties(text)
    compatibility = extract_notes(text, ["compatib", "dependency", "requires", "do not", "avoid", "note"])
    return implementation_entry(
        relative=relative,
        name=first_heading("", path),
        purpose="Implementation configuration source.",
        properties=properties,
        events=extract_events(text),
        slots=extract_slots(text),
        compatibility=compatibility,
        commit=commit,
        branch=branch,
    )


def implementation_entry(relative, name, purpose, properties, events, slots, compatibility, commit, branch):
    warnings = []
    if not any([properties, events, slots, compatibility]):
        warnings.append(f"{relative}: no implementation nuance fields extracted")
    return (
        {
            "name": name,
            "doc_path": relative.as_posix(),
            "source_url": source_url(commit, relative),
            "source_aliases": [source_alias(branch, relative)],
            "purpose": purpose,
            "properties": properties,
            "events": events,
            "slots": slots,
            "compatibility_notes": compatibility,
            "evidence_status": "Implementation nuance only",
            "mentor_prompt_guidance": (
                "Use this source-backed note only after current docs and generated catalogs; "
                "do not label mirror-only facts Current official or Catalog-backed official."
            ),
        },
        warnings,
    )


def iter_reference_files(source_root):
    root = Path(source_root) / CONTENT_ROOT
    if not root.exists():
        return []
    markdown = [path for path in root.rglob("*.md") if path.is_file()]
    ts_configs = [path for path in root.rglob("*Config.ts") if path.is_file()]
    return sorted(markdown + ts_configs)


def build_reference(source_root, required_names=()):
    source_root = Path(source_root)
    commit = git_value(source_root, ["rev-parse", "HEAD"], "unknown")
    branch = git_value(source_root, ["branch", "--show-current"], DEFAULT_BRANCH)
    remote = git_value(source_root, ["remote", "get-url", "origin"], DEFAULT_REPO_URL)
    commit_timestamp = git_value(source_root, ["show", "-s", "--format=%cI", "HEAD"], "unknown")
    metadata = {
        "source_commit": commit,
        "source_branch": branch,
        "source_remote": remote,
        "source_commit_timestamp": commit_timestamp,
        "gap_analysis": analyze_gap_surface(source_root),
    }
    entries = []
    warnings = []
    for path in iter_reference_files(source_root):
        if path.suffix == ".md":
            entry, entry_warnings = markdown_reference_entry(source_root, path, commit, branch)
        else:
            entry, entry_warnings = ts_reference_entry(source_root, path, commit, branch)
        entries.append(entry)
        warnings.extend(entry_warnings)
    entries.sort(key=lambda item: (item["name"], item["doc_path"]))

    missing_required = []
    normalized_names = {entry["name"].lower(): entry for entry in entries}
    for required in required_names:
        entry = normalized_names.get(required.lower())
        if not entry or not any([entry["properties"], entry["events"], entry["slots"], entry["compatibility_notes"]]):
            missing_required.append(required)
    if missing_required:
        raise ValueError(
            "Missing required implementation nuance for: "
            + ", ".join(sorted(missing_required))
        )
    return entries, sorted(warnings), metadata


def write_reference(entries, warnings, metadata, output_path, generated_at_utc=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at_utc = generated_at_utc or metadata.get("source_commit_timestamp") or "unknown"
    branch = metadata["source_branch"]
    payload = {
        "generated_at_utc": generated_at_utc,
        "source_family": "official_repo_mirror",
        "source_quality": "outsystems_public_implementation_evidence",
        "source_repo": SOURCE_REPO,
        "source_commit": metadata["source_commit"],
        "source_branch": branch,
        "source_remote": metadata["source_remote"],
        "source_content_root": CONTENT_ROOT.as_posix(),
        "branch_aliases": sorted({branch, DEFAULT_BRANCH}),
        "summary": {
            "reference_count": len(entries),
            "warning_count": len(warnings),
            "entries_with_properties": sum(1 for item in entries if item["properties"]),
            "entries_with_events": sum(1 for item in entries if item["events"]),
            "top_level_paths": dict(
                sorted(Counter(item["doc_path"].split("/")[1] for item in entries if "/" in item["doc_path"]).items())
            ),
        },
        "gap_analysis": metadata.get("gap_analysis", {}),
        "warnings": warnings,
        "references": entries,
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clone_repo(repo_url):
    parent = tempfile.TemporaryDirectory()
    clone = ClonedRepo(parent, Path(parent.name) / "checkout")
    command = ["git", "clone", "--depth", "1", "--branch", DEFAULT_BRANCH, repo_url, clone.name]
    env = isolated_git_environment()
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=CLONE_TIMEOUT_SECONDS,
            env=env,
            cwd=parent.name,
        )
        head_result = subprocess.run(
            ["git", "-C", clone.name, "rev-parse", "--verify", "HEAD^{commit}"],
            check=False,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=CLONE_TIMEOUT_SECONDS,
            env=env,
            cwd=parent.name,
        )
        head = head_result.stdout.strip()
        if head_result.returncode != 0:
            detail = bounded_git_detail(
                head_result.stderr or head_result.stdout or f"Git exited with status {head_result.returncode}"
            )
            raise ValueError(f"cloned HEAD verification failed: {detail}")
        if not valid_git_object_id(head):
            raise ValueError(f"cloned HEAD verification returned an invalid object id: {bounded_git_detail(head)}")
        authoritative_head = authoritative_remote_head()
        if head != authoritative_head:
            raise ValueError(
                f"cloned HEAD {head} does not match authoritative remote {DEFAULT_REPO_URL} "
                f"branch {DEFAULT_BRANCH} at {authoritative_head}"
            )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as exc:
        detail = bounded_git_detail(getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or exc)
        clone.cleanup()
        raise SystemExit(
            f"Unable to clone approved public source {repo_url} on branch {DEFAULT_BRANCH}: {detail}. "
            "Confirm Git is installed and the repository is reachable, then retry."
        ) from exc
    return clone


def main():
    parser = argparse.ArgumentParser(description="Refresh the OutSystems UI implementation reference.")
    parser.add_argument("--source", help="Path to a local OutSystems/outsystems-ui checkout.")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).resolve().parents[1] / "references" / "outsystems-ui-implementation-reference.json"),
    )
    parser.add_argument("--require", action="append", default=[], help="Component name that must produce implementation nuance.")
    args = parser.parse_args()

    temp = None
    if args.source:
        source = validate_explicit_source(args.source)["top_level"]
    else:
        temp = clone_repo(DEFAULT_REPO_URL)
        source = Path(temp.name)
    try:
        try:
            entries, warnings, metadata = build_reference(source, required_names=args.require)
            if not entries:
                raise ValueError(f"No reference files found under {source / CONTENT_ROOT}")
        except ValueError as exc:
            source_hint = " Explicit --source does not fall back to cloning." if args.source else ""
            raise SystemExit(f"Unable to refresh OutSystems UI reference: {bounded_git_detail(exc)}.{source_hint}") from exc
        write_reference(entries, warnings, metadata, args.output)
        print(f"Wrote {len(entries)} OutSystems UI implementation references to {args.output}")
        if warnings:
            print(f"Warnings: {len(warnings)}")
    finally:
        if temp is not None:
            temp.cleanup()


if __name__ == "__main__":
    main()
