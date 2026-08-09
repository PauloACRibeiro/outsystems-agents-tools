#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PATTERN_ROOT = Path("src/eap/building-apps/ui/patterns")
DEFAULT_REPO_URL = "https://github.com/OutSystems/docs-odc.git"
SOURCE_BASE_URL = "https://github.com/OutSystems/docs-odc/blob/main"
FAMILIES = {"adaptive", "content", "interaction", "navigation", "numbers", "utilities"}


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data = {}
    current_key = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip().strip('"')
            data[current_key] = value if value else []
    return data, body


def first_heading(body, fallback):
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    if match:
        return re.sub(r"`|\*", "", match.group(1)).strip()
    return fallback.stem.replace("-", " ").title()


def first_paragraph(body):
    lines = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!") or line.startswith("<"):
            if lines:
                break
            continue
        if line.startswith("|") or line.startswith("1.") or line.startswith("- "):
            if lines:
                break
            continue
        lines.append(re.sub(r"\s+", " ", line))
    return " ".join(lines)


def parse_properties(body):
    mandatory = []
    optional = []
    section_match = re.search(r"^## Properties\s*\n(?P<section>.*?)(?=^##\s+|\Z)", body, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if not section_match:
        return mandatory, optional
    for table_match in re.finditer(r"(?P<table>(?:^\|.*\n?)+)", section_match.group("section"), re.MULTILINE):
        for line in table_match.group("table").splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2 or cells[0].lower() == "property" or set(cells[0]) <= {"-", ":"}:
                continue
            prop_name = cells[0].split("(")[0].strip()
            if "mandatory" in cells[0].lower():
                mandatory.append(prop_name)
            elif "optional" in cells[0].lower():
                optional.append(prop_name)
    return sorted(set(mandatory)), sorted(set(optional))


def extract_events(body):
    non_events = {"OnPhone", "OnTablet", "OnDesktop"}
    events = set()
    for event in re.findall(r"\bOn[A-Z][A-Za-z0-9]+", body):
        if event not in non_events:
            events.add(event)
    return sorted(events)


def extract_placeholders(body):
    placeholders = set()
    for match in re.findall(r"\b([A-Z][A-Za-z0-9]*Content)\b", body):
        placeholders.add(match)
    if "placeholder" in body.lower():
        placeholders.add("Pattern placeholders described in source")
    return sorted(placeholders)


def extract_notes(body, keywords):
    notes = []
    for paragraph in re.split(r"\n\s*\n", body):
        clean = re.sub(r"\s+", " ", paragraph.strip())
        if not clean:
            continue
        if clean.startswith(("#", "|", "![")):
            continue
        lowered = clean.lower()
        if any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in keywords):
            notes.append(clean)
    return notes[:4]


def extract_compatibility_notes(body):
    notes = []
    compatibility_patterns = [
        r"\bcompatib(?:le|ility)\b",
        r"\bincompatib(?:le|ility)\b",
        r"\b(?:applies|apply)\s+to\b",
        r"\bnote\s*:",
        r"\bavoid\s+using\b.*\balone\b",
        r"\bdo\s+not\s+use\b.*\balone\b",
    ]
    for paragraph in re.split(r"\n\s*\n", body):
        clean = re.sub(r"\s+", " ", paragraph.strip())
        if not clean:
            continue
        if clean.startswith(("#", "|", "![", "- ")):
            continue
        if re.match(r"^\d+\.", clean):
            continue
        if "in this example" in clean.lower():
            continue
        if any(re.search(pattern, clean, re.IGNORECASE) for pattern in compatibility_patterns):
            notes.append(clean)
    return notes[:4]


def family_for(path):
    try:
        family = path.relative_to(PATTERN_ROOT).parts[0]
    except ValueError:
        family = path.parts[-2] if len(path.parts) > 1 else "unknown"
    return family if family in FAMILIES else "unknown"


def catalog_entry(source_root, markdown_path):
    relative = markdown_path.relative_to(source_root)
    text = markdown_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    title = first_heading(body, markdown_path)
    purpose = frontmatter.get("summary") or first_paragraph(body)
    mandatory, optional = parse_properties(body)
    events = extract_events(body)
    placeholders = extract_placeholders(body)
    compatibility = extract_compatibility_notes(body)
    security = extract_notes(body, ["sanitize", "security", "safe", "html", "script", "injection"])
    applies_to = frontmatter.get("app_type", "")
    if isinstance(applies_to, str):
        applies_to = [item.strip() for item in applies_to.split(",") if item.strip()]
    entry = {
        "name": title,
        "family": family_for(relative),
        "doc_path": str(relative),
        "source_url": f"{SOURCE_BASE_URL}/{relative.as_posix()}",
        "purpose": purpose,
        "applies_to": applies_to,
        "mandatory_properties": mandatory,
        "important_optional_properties": optional,
        "events": events,
        "placeholders": placeholders,
        "data_binding_shape": infer_data_binding_shape(body),
        "compatibility_notes": compatibility,
        "security_or_sanitization_notes": security,
        "mentor_prompt_fragment": f"Use the {title} pattern and configure its documented properties before wiring events.",
        "evidence_status": "Current official",
    }
    warnings = []
    if not mandatory and not optional:
        warnings.append(f"{relative}: missing properties table")
    if not title:
        warnings.append(f"{relative}: missing title")
    return entry, warnings


def infer_data_binding_shape(body):
    lowered = body.lower()
    shapes = []
    if "aggregate" in lowered or "fetch data" in lowered:
        shapes.append("usually binds to an Aggregate or Data Action result")
    if "source" in lowered and "list" in lowered:
        shapes.append("list source binding is documented")
    if "optionslist" in lowered:
        shapes.append("requires an options list structure")
    if "value" in lowered and "label" in lowered:
        shapes.append("requires value and label bindings")
    return shapes


def iter_pattern_files(source_root):
    root = source_root / PATTERN_ROOT
    return sorted(path for path in root.rglob("*.md") if path.name != "intro.md")


def build_catalog(source_root):
    source_root = Path(source_root)
    entries = []
    warnings = []
    for markdown_path in iter_pattern_files(source_root):
        entry, entry_warnings = catalog_entry(source_root, markdown_path)
        entries.append(entry)
        warnings.extend(entry_warnings)
    entries.sort(key=lambda item: (item["family"], item["name"]))
    return entries, warnings


def ensure_expected_family_coverage(entries):
    families = Counter(entry["family"] for entry in entries)
    missing = sorted(family for family in FAMILIES if families[family] == 0)
    if missing:
        raise ValueError(f"Missing expected pattern families: {', '.join(missing)}")


def write_catalog(entries, warnings, output_path, generated_at_utc=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    families = dict(sorted(Counter(entry["family"] for entry in entries).items()))
    generated_at_utc = generated_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "generated_at_utc": generated_at_utc,
        "source_family": "official_outsystems_docs_odc",
        "source_pattern_root": str(PATTERN_ROOT),
        "summary": {
            "pattern_count": len(entries),
            "families": families,
            "warning_count": len(warnings),
        },
        "warnings": sorted(warnings),
        "patterns": entries,
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clone_repo(repo_url):
    tmp = tempfile.TemporaryDirectory()
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, tmp.name],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return tmp


def find_local_source():
    env_path = os.environ.get("OUTSYSTEMS_DOCS_ODC_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(
        [
            Path.cwd() / "projects" / "docs-odc",
            Path.cwd() / "docs-odc",
            Path.home() / "Documents" / "Workspace" / "projects" / "docs-odc",
        ]
    )
    for candidate in candidates:
        if (candidate / PATTERN_ROOT).is_dir():
            return candidate
    return None


def main():
    parser = argparse.ArgumentParser(description="Refresh the ODC UI pattern catalog for outsystems-mentor-implementation.")
    parser.add_argument("--source", help="Path to a local OutSystems/docs-odc checkout.")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL, help="Git repository to clone when --source is omitted.")
    parser.add_argument("--output", required=True, help="Output JSON catalog path.")
    args = parser.parse_args()

    cloned = None
    if args.source:
        source_root = Path(args.source)
    else:
        source_root = find_local_source()
        if source_root is None:
            if not shutil.which("git"):
                raise SystemExit("git is required when --source is omitted and no local docs-odc checkout is found")
            cloned = clone_repo(args.repo_url)
            source_root = Path(cloned.name)

    entries, warnings = build_catalog(source_root)
    if not entries:
        raise SystemExit(f"No pattern Markdown files found under {source_root / PATTERN_ROOT}")
    try:
        ensure_expected_family_coverage(entries)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    write_catalog(entries, warnings, args.output)
    print(f"patterns={len(entries)}")
    for family, count in sorted(Counter(entry["family"] for entry in entries).items()):
        print(f"{family}={count}")
    print(f"warnings={len(warnings)}")
    if cloned:
        cloned.cleanup()


if __name__ == "__main__":
    main()
