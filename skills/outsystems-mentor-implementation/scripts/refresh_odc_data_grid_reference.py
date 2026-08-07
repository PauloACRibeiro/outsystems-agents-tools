#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_REPO_URL = "https://github.com/OutSystems/docs-odc.git"
CANONICAL_SCP_REPO_URL = "git@github.com:OutSystems/docs-odc.git"
DEFAULT_BRANCH = "main"
REMOTE_LOOKUP_TIMEOUT_SECONDS = 15
CLONE_TIMEOUT_SECONDS = 30
MAX_GIT_DETAIL_CHARS = 500
MAX_SOURCE_DISPLAY_CHARS = 200
MAX_SOURCE_ERROR_CHARS = 1000
SOURCE_BASE_URL = "https://github.com/OutSystems/docs-odc/blob/main"
PRIMARY_REFERENCE = Path("src/eap/reference/data-grid-ref.md")
LOCAL_REFERENCE_ROOT = Path("knowledge/outsystems/public/odc/reference")


def candidate_files(source_root):
    source_root = Path(source_root)
    primary = source_root / PRIMARY_REFERENCE
    if primary.is_file():
        return [primary]

    reference_root = source_root / "src" / "eap" / "reference"
    if reference_root.is_dir():
        matches = sorted(
            path
            for path in reference_root.rglob("*.md")
            if "data-grid" in path.name.lower() or "data_grid" in path.name.lower()
        )
        if matches:
            return matches

    knowledge_root = source_root / LOCAL_REFERENCE_ROOT
    if knowledge_root.is_dir():
        return sorted(
            path
            for path in knowledge_root.rglob("*.md")
            if "data" in path.name.lower() and "grid" in path.name.lower()
        )

    return []


def source_url_for(relative):
    if relative.as_posix().startswith("src/eap/"):
        return f"{SOURCE_BASE_URL}/{relative.as_posix()}"
    return ""


def read_source(source_root):
    files = candidate_files(source_root)
    if not files:
        raise ValueError(f"No Data Grid reference Markdown found under {source_root}")
    path = files[0]
    return path, path.read_text(encoding="utf-8")


def normalize(text):
    return re.sub(r"\s+", " ", text.strip())


def extract_dependency_requirements(text):
    requirements = []
    for paragraph in re.split(r"\n\s*\n", text):
        clean = normalize(paragraph)
        lowered = clean.lower()
        if clean and ("dependency" in lowered or "manage dependencies" in lowered):
            requirements.append(clean)
    return requirements[:4]


def extract_headings(text):
    headings = []
    for match in re.finditer(r"^#{2,4}\s+(.+?)\s*$", text, re.MULTILINE):
        heading = clean_heading(match.group(1))
        if heading and heading.lower() not in {"properties", "events", "inputs", "summary"}:
            headings.append(heading)
    return sorted(set(headings))


def clean_heading(raw_heading):
    heading = re.sub(r"\s+\{\s*#[^}]+\}\s*$", "", raw_heading)
    return re.sub(r"`|\*", "", heading).strip()


def extract_table_first_column(text, heading_names):
    wanted = {item.lower() for item in heading_names}
    values = set()
    current_heading = ""
    for line in text.splitlines():
        heading = re.match(r"^#{2,4}\s+(.+?)\s*$", line)
        if heading:
            current_heading = clean_heading(heading.group(1)).lower()
            continue
        if not line.startswith("|"):
            continue
        if not any(name in current_heading for name in wanted):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        value = cells[0]
        if value.lower() in {"property", "event", "action", "method", "name"} or set(value) <= {"-", ":"}:
            continue
        values.add(value.split("(")[0].strip())
    return sorted(values)


def extract_events(text):
    return sorted(set(re.findall(r"\bOn[A-Z][A-Za-z0-9]+", text)))


def extract_heading_section(text, heading_name):
    match = re.search(rf"^##\s+{re.escape(heading_name)}\b.*$", text, re.IGNORECASE | re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def extract_actions_or_methods(text):
    values = set(extract_table_first_column(text, ["actions", "methods", "client actions"]))
    for section_name in ["Actions", "Client Actions"]:
        section = extract_heading_section(text, section_name)
        for heading in re.findall(r"^#{3,4}\s+([A-Z][A-Za-z0-9_]*)\s*(?:\{\s*#[^}]+\})?\s*$", section, re.MULTILINE):
            values.add(heading)
    for link in re.findall(r"\[([A-Z][A-Za-z0-9_]*)\]\(<#Action_[^)]+>\)", text):
        values.add(link)
    for link in re.findall(r"\[([A-Z][A-Za-z0-9_]*)\]\(<#Client_[^)]+>\)", text):
        values.add(link)
    for token in re.findall(r"`([A-Z][A-Za-z0-9]+)`", text):
        lowered = token.lower()
        if any(keyword in lowered for keyword in ["action", "change", "save", "grid", "row", "line"]):
            values.add(token)
    return sorted(values)


def extract_properties(text):
    values = set(extract_table_first_column(text, ["properties", "inputs"]))
    for name in re.findall(r"(?m)^([A-Z][A-Za-z0-9_]*)\s*\n:\s+Type:", text):
        values.add(name)
    return sorted(values)


def setup_guidance(dependency_requirements):
    if dependency_requirements:
        return {
            "known_setup_sequence": [
                "Use the documented dependency requirements extracted from the selected source.",
                "Create or confirm data producers before placing grid consumer UI.",
                "Use exact documented actions or methods when wiring changed-row save behavior.",
            ],
            "mentor_prompt_guidance": "Use extracted Data Grid dependency facts and producer data/actions before emitting consumer grid prompts.",
        }
    guardrail = "Manual preflight guardrail: confirm the Data Grid dependency is available before consumer UI prompts; exact dependency setup was not found in the selected source."
    return {
        "known_setup_sequence": [guardrail],
        "mentor_prompt_guidance": guardrail,
    }


def evidence_statuses(dependency_requirements):
    if dependency_requirements:
        return {
            "evidence_status": "Current official",
            "dependency_setup_evidence_status": "Current official",
        }
    return {
        "evidence_status": "Current official for documented Data Grid facts",
        "dependency_setup_evidence_status": "Manual preflight gap",
    }


def build_reference(source_root):
    source_root = Path(source_root)
    markdown_path, text = read_source(source_root)
    relative = markdown_path.relative_to(source_root)
    dependency_requirements = extract_dependency_requirements(text)
    core_concepts = extract_headings(text)
    documented_properties = extract_properties(text)
    documented_events = extract_events(text)
    documented_actions_or_methods = extract_actions_or_methods(text)
    missing = []
    if not dependency_requirements:
        missing.append("Dependency requirement not found in source")
    if not documented_properties:
        missing.append("Documented properties not found in source")
    if not documented_events:
        missing.append("Documented events not found in source")
    if not documented_actions_or_methods:
        missing.append("Documented actions or methods not found in source")

    guidance = setup_guidance(dependency_requirements)
    statuses = evidence_statuses(dependency_requirements)
    reference = {
        "component": "ODC Data Grid",
        "source_family": "official_outsystems_docs_odc",
        "source_url": source_url_for(relative),
        "doc_path": relative.as_posix(),
        "dependency_requirements": dependency_requirements,
        "supported_targets": ["reactive web apps"],
        "core_concepts": core_concepts,
        "documented_properties": documented_properties,
        "documented_events": documented_events,
        "documented_actions_or_methods": documented_actions_or_methods,
        "known_setup_sequence": guidance["known_setup_sequence"],
        "mentor_prompt_guidance": guidance["mentor_prompt_guidance"],
        "missing_facts": missing,
        **statuses,
    }
    return reference, []


def write_reference(reference, warnings, output_path, generated_at_utc=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at_utc = generated_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "generated_at_utc": generated_at_utc,
        "warnings": sorted(warnings),
        **reference,
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
        raise ValueError(f"authoritative remote lookup timed out after {REMOTE_LOOKUP_TIMEOUT_SECONDS}s") from exc
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
            f"{DEFAULT_BRANCH} at origin/{DEFAULT_BRANCH} with a clean working tree. "
            "No clone fallback is used for explicit --source."
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
    parser = argparse.ArgumentParser(description="Refresh the ODC Data Grid reference for outsystems-mentor-implementation.")
    parser.add_argument("--source", help="Path to a local OutSystems/docs-odc checkout.")
    parser.add_argument("--output", required=True, help="Output JSON reference path.")
    args = parser.parse_args()

    cloned = None
    try:
        if args.source:
            source_root = validate_explicit_source(args.source)["top_level"]
        else:
            cloned = clone_repo(DEFAULT_REPO_URL)
            source_root = Path(cloned.name)

        try:
            reference, warnings = build_reference(source_root)
        except ValueError as exc:
            if args.source:
                raise SystemExit(
                    f"{bounded_git_detail(exc)}. Explicit --source must point to a valid OutSystems/docs-odc checkout; "
                    "no clone fallback is used for explicit --source."
                ) from exc
            raise SystemExit(bounded_git_detail(exc)) from exc
        write_reference(reference, warnings, args.output)
        print(f"component={reference['component']}")
        print(f"properties={len(reference['documented_properties'])}")
        print(f"events={len(reference['documented_events'])}")
        print(f"actions_or_methods={len(reference['documented_actions_or_methods'])}")
        print(f"missing_facts={len(reference['missing_facts'])}")
        print(f"warnings={len(warnings)}")
    finally:
        if cloned:
            cloned.cleanup()


if __name__ == "__main__":
    main()
