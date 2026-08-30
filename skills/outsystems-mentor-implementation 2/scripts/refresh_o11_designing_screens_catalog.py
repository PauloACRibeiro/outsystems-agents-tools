#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


DEFAULT_SOURCE_ROOT = Path("knowledge/outsystems/public/o11/product-docs/14 - Other Documentation/OutSystems Language")
DEFAULT_GENERATED_AT = "source-derived"
INTERFACE_ROOT_PART = "Interface"
TRADITIONAL_ROOT_PART = "_Traditional Web"
SECTION_NAMES = {
    "properties": {"properties", "attributes"},
    "events": {"events"},
    "runtime_properties": {"runtime properties", "runtime properties:"},
    "accessibility_notes": {
        "accessibility",
        "accessibility - wcag 2.2 aa compliance",
        "accessibility - wcag 2.1 aa compliance",
    },
}
FLATTENED_DESCRIPTION_STARTERS = (
    "Identifies",
    "Specifies",
    "Boolean",
    "Text literal",
    "Text",
    "Holds",
    "Screen action",
    "When",
    "Action",
    "JavaScript",
    "Transition",
    "Name of",
    "Value of",
    "Set to",
    "If",
    "List",
    "Record",
    "Expression",
    "Entity",
    "Local",
    "Source",
    "Destination",
    "Target",
    "URL",
    "HTML",
    "Default",
    "Defines",
    "Number",
    "Path",
    "Binary",
    "Image",
    "Placeholder",
)
FLATTENED_SKIP_NAMES = {
    "attributes",
    "default value",
    "description",
    "mandatory",
    "methods hierarchy",
    "observations",
    "read only",
    "runtime properties",
    "source content",
    "type",
}
SCALAR_VALUE_WORDS = {
    "binary data",
    "boolean",
    "date",
    "date time",
    "false",
    "integer",
    "long integer",
    "no",
    "text",
    "true",
    "yes",
}
EVENT_DESCRIPTION_FIRST_WORDS = {
    "Action",
    "By",
    "Event",
    "Handler",
    "JavaScript",
    "Screen",
    "Set",
    "Transition",
    "When",
}
ODC_TARGET_NAMES = {
    "Container",
    "Expression",
    "If",
    "Text",
    "Form",
    "Input",
    "Button",
    "Button Group",
    "Link",
    "Popover Menu",
    "List",
    "List Item",
    "Table",
    "Checkbox",
    "Radio Group",
    "Dropdown",
    "Label",
    "Text Area",
    "Switch",
    "Image",
    "Icon",
    "Upload",
    "Screen",
    "Block Widget",
    "Block",
}


def strip_frontmatter(text):
    return re.sub(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", "", text, flags=re.DOTALL)


def extract_frontmatter_value(text, key):
    match = re.search(rf'^{re.escape(key)}:\s*"?(.*?)"?\s*$', text, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def normalize_widget_name(title):
    name = re.sub(r"\s+", " ", title).strip()
    name = re.sub(r"\s+Widget$", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\s+Reference$", "", name, flags=re.IGNORECASE)
    return name


def slug_from_source_url(source_url, title):
    if source_url:
        return source_url.rstrip("/").rsplit("/", 1)[-1]
    normalized = normalize_widget_name(title).lower()
    return re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")


def source_family_for(page_family):
    if page_family == "traditional_web":
        return "official_outsystems_public_docs_o11_traditional_web"
    return "official_outsystems_public_docs_o11"


def page_family_for(path):
    parts = set(path.parts)
    if TRADITIONAL_ROOT_PART in parts:
        return "traditional_web"
    if INTERFACE_ROOT_PART in parts:
        return "interface"
    return "unknown"


def discover_markdown_files(source_root):
    source_root = Path(source_root)
    if source_root.name == "OutSystems Language" or (source_root / INTERFACE_ROOT_PART).exists():
        roots = [source_root / INTERFACE_ROOT_PART, source_root / TRADITIONAL_ROOT_PART]
    else:
        roots = [
            source_root / DEFAULT_SOURCE_ROOT / INTERFACE_ROOT_PART,
            source_root / DEFAULT_SOURCE_ROOT / TRADITIONAL_ROOT_PART,
        ]
    files = []
    for root in roots:
        if root.is_dir():
            files.extend(path for path in root.rglob("*.md") if path.is_file() and is_designing_screens_file(path))
    return sorted(files)


def is_designing_screens_file(path):
    text = path.read_text(encoding="utf-8")
    source_url = extract_frontmatter_value(text, "source_url").lower()
    if is_designing_screens_landing_page(path, text, source_url):
        return False
    if re.search(r"/designing_screens/[^/#?]+", source_url):
        return True
    return any(part.lower() == "designing screens" for part in path.parts) and path.stem.lower() != "designing screens"


def is_designing_screens_landing_page(path, text, source_url):
    normalized_url = source_url.split("#", 1)[0].split("?", 1)[0].rstrip("/")
    if normalized_url.endswith("/designing_screens"):
        return True
    title = extract_frontmatter_value(text, "title")
    if not title:
        heading = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
        title = heading.group(1).strip() if heading else path.stem
    return normalize_widget_name(title).lower() == "designing screens"


def heading_matches(text):
    return list(re.finditer(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$", text, re.MULTILINE))


def section_by_title(text, allowed_titles):
    matches = heading_matches(text)
    for index, match in enumerate(matches):
        title = match.group("title").strip().lower()
        if title not in allowed_titles:
            continue
        level = len(match.group("marks"))
        start = match.end()
        end = len(text)
        for next_match in matches[index + 1 :]:
            next_title = next_match.group("title").strip()
            if len(next_match.group("marks")) <= level and not is_pdf_page_heading(next_title):
                end = next_match.start()
                break
        return text[start:end].strip()
    return ""


def is_pdf_page_heading(title):
    return bool(re.fullmatch(r"page\s+\d+", title.strip(), flags=re.IGNORECASE))


def text_after_heading(text, heading_title):
    for match in heading_matches(text):
        if match.group("title").strip().lower() == heading_title.lower():
            return text[match.end() :].strip()
    return ""


def first_content_paragraph(text, title):
    body = strip_frontmatter(text)
    source_content = text_after_heading(body, "Source Content")
    search_body = source_content or body
    preferred = section_by_title(search_body, {normalize_widget_name(title).lower(), title.lower()})
    if not preferred:
        return ""
    paragraphs = []
    for raw in re.split(r"\n\s*\n", preferred):
        paragraph = re.sub(r"\s+", " ", raw.strip())
        if is_boilerplate_paragraph(paragraph):
            continue
        paragraphs.append(paragraph)
    return paragraphs[0] if paragraphs else ""


def is_boilerplate_paragraph(paragraph):
    if not paragraph or paragraph.startswith(("#", "|", "!", "<", ">", "- [")):
        return True
    lower = paragraph.lower()
    if lower.startswith(
        (
            "source content",
            "navigation",
            "methods hierarchy",
            "_no procedural sections detected",
            "applies ",
            "last updated",
            "success.outsystems.com",
        )
    ):
        return True
    return bool(
        re.fullmatch(r"\d+/\d+", paragraph)
        or re.fullmatch(r"\d{4}-\d{2}-\d{2}", paragraph)
        or re.fullmatch(r"[A-Z][a-z]+ \d{1,2}, \d{4}", paragraph)
    )


def extract_table_names(section):
    names = []
    for table_match in re.finditer(r"(?P<table>(?:^\|.*\n?)+)", section, re.MULTILINE):
        rows = [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in table_match.group("table").splitlines()
        ]
        if len(rows) > 1 and all(set(cell) <= {"-", ":"} for cell in rows[1]):
            rows = rows[2:]
        else:
            rows = rows[1:]
        for cells in rows:
            if not cells:
                continue
            value = cells[0].strip()
            if value and set(value) - {"-", ":"}:
                names.append(value)
    return sorted(dict.fromkeys(names))


def clean_flattened_lines(section):
    lines = []
    for raw_line in section.splitlines():
        line = re.sub(r"\s+", " ", raw_line.strip())
        if not line:
            continue
        if line.startswith(("#", "<", ">", "!", "|", "- [")):
            continue
        if is_boilerplate_paragraph(line):
            continue
        lowered = line.lower().strip('"')
        if lowered in FLATTENED_SKIP_NAMES or lowered in SCALAR_VALUE_WORDS:
            continue
        if all(word.lower() in SCALAR_VALUE_WORDS for word in line.split()):
            continue
        if re.fullmatch(r"\d+/\d+", line) or re.fullmatch(r"Page \d+", line, flags=re.IGNORECASE):
            continue
        if line.startswith(('"', "'", "“", "”")):
            continue
        lines.append(line)
    return lines


def flattened_name_from_line(line):
    first_word = line.split()[0].rstrip(".").lower()
    if first_word in SCALAR_VALUE_WORDS:
        return ""
    if re.fullmatch(r"[A-Z][A-Za-z0-9]*(?:[- ][A-Z][A-Za-z0-9]*){0,4}", line):
        return line
    starters = "|".join(re.escape(starter) for starter in FLATTENED_DESCRIPTION_STARTERS)
    starter_as_name = flattened_starter_as_name(line)
    if starter_as_name:
        return starter_as_name
    if any(line.startswith(f"{starter} ") for starter in FLATTENED_DESCRIPTION_STARTERS):
        return ""
    match = re.match(
        rf"^(?P<name>[A-Z][A-Za-z0-9]*(?:[- ][A-Za-z0-9]+){{0,4}})\s+(?=(?:{starters})\b)",
        line,
    )
    if match:
        return match.group("name").strip()
    return ""


def flattened_starter_as_name(line):
    for starter in sorted(FLATTENED_DESCRIPTION_STARTERS, key=len, reverse=True):
        prefix = f"{starter} "
        if not line.startswith(prefix):
            continue
        remainder = line[len(prefix) :].strip()
        if any(
            remainder == description_starter or remainder.startswith(f"{description_starter} ")
            for description_starter in FLATTENED_DESCRIPTION_STARTERS
        ):
            return starter
        return ""
    return ""


def extract_flattened_names(section):
    names = []
    for line in clean_flattened_lines(section):
        name = flattened_name_from_line(line)
        if name:
            names.append(name)
    return sorted(dict.fromkeys(names))


def extract_flattened_events(section):
    events = []
    for line in clean_flattened_lines(section):
        event = flattened_event_from_line(line)
        if event:
            events.append(event)
    return sorted(dict.fromkeys(events))


def flattened_event_from_line(line):
    words = []
    for token in line.split():
        word = token.strip(".,:;()[]")
        if not word:
            continue
        if words and len(words) > 1 and word in EVENT_DESCRIPTION_FIRST_WORDS:
            break
        if not re.fullmatch(r"[A-Z][A-Za-z0-9]+", word):
            break
        words.append(word)
        if len(words) >= 5:
            break
    if len(words) < 2 or words[0] != "On":
        return ""
    return " ".join(words)


def extract_section_names(text, names, section_kind=None):
    section = section_by_title(strip_frontmatter(text), names)
    if not section:
        return []
    table_names = extract_table_names(section)
    if table_names:
        return table_names
    if section_kind == "events":
        return extract_flattened_events(section)
    return extract_flattened_names(section)


def extract_accessibility_notes(text):
    body = strip_frontmatter(text)
    section = section_by_title(body, SECTION_NAMES["accessibility_notes"])
    if not section:
        return []
    notes = []
    for raw in re.split(r"\n\s*\n", section):
        paragraph = re.sub(r"\s+", " ", raw.strip())
        if paragraph and not paragraph.startswith(("#", "|", "!", "<")):
            notes.append(paragraph)
    return notes[:4]


def entry_for_file(path, source_root):
    text = path.read_text(encoding="utf-8")
    title = extract_frontmatter_value(text, "title")
    if not title:
        heading = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
        title = heading.group(1).strip() if heading else path.stem
    normalized = normalize_widget_name(title)
    source_url = extract_frontmatter_value(text, "source_url")
    page_family = page_family_for(path)
    properties = extract_section_names(text, SECTION_NAMES["properties"], section_kind="properties")
    events = extract_section_names(text, SECTION_NAMES["events"], section_kind="events")
    runtime_properties = extract_section_names(
        text, SECTION_NAMES["runtime_properties"], section_kind="runtime_properties"
    )
    accessibility_notes = extract_accessibility_notes(text)
    purpose = first_content_paragraph(text, title)
    missing = []
    if not purpose:
        missing.append("O11 purpose not found in source")
    if not properties:
        missing.append("O11 properties not found in source")
    if not events:
        missing.append("O11 events not found in source")
    if not runtime_properties:
        missing.append("O11 runtime properties not found in source")
    relative = path.relative_to(source_root) if path.is_relative_to(source_root) else path
    # doc_path is published provenance, so it is recorded relative to the
    # harvest root rather than to the workspace: the leading
    # knowledge/outsystems/... segments name a mirror that exists only on the
    # maintainer's machine and resolve for nobody who reads the catalog.
    doc_relative = (
        relative.relative_to(DEFAULT_SOURCE_ROOT)
        if relative.is_relative_to(DEFAULT_SOURCE_ROOT)
        else relative
    )
    support_status = "O11-supported ODC candidate" if normalized in ODC_TARGET_NAMES else "O11-only support"
    return {
        "title": title,
        "normalized_name": normalized,
        "slug": slug_from_source_url(source_url, title),
        "source_url": source_url,
        "source_family": source_family_for(page_family),
        "page_family": page_family,
        "doc_path": doc_relative.as_posix(),
        "purpose": purpose,
        "properties": properties,
        "events": events,
        "runtime_properties": runtime_properties,
        "accessibility_notes": accessibility_notes,
        "support_status": support_status,
        "missing_facts": missing,
        "parse_warnings": [],
    }


def build_catalog(source_root):
    source_root = Path(source_root)
    files = discover_markdown_files(source_root)
    if not files:
        raise ValueError(f"No O11 Designing Screens Markdown files found under {source_root}")
    entries = [entry_for_file(path, source_root) for path in files]
    entries.sort(key=lambda item: (item["normalized_name"].lower(), item["page_family"], item["doc_path"]))
    summary = {
        "entry_count": len(entries),
        "o11_supported_odc_candidate_count": sum(
            1 for item in entries if item["support_status"] == "O11-supported ODC candidate"
        ),
        "o11_only_support_count": sum(1 for item in entries if item["support_status"] == "O11-only support"),
    }
    return {
        "source_family": "official_outsystems_public_docs_o11",
        "source_roots": [
            INTERFACE_ROOT_PART,
            TRADITIONAL_ROOT_PART,
        ],
        "summary": summary,
        "entries": entries,
    }, []


def write_catalog(catalog, warnings, output_path, generated_at_utc=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at_utc = generated_at_utc or DEFAULT_GENERATED_AT
    payload = {
        "generated_at_utc": generated_at_utc,
        "warnings": sorted(warnings),
        **catalog,
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Refresh the O11 Designing Screens widget support catalog.")
    parser.add_argument("--source", default=".", help="Workspace root or OutSystems Language source root.")
    parser.add_argument("--output", required=True, help="Output JSON catalog path.")
    args = parser.parse_args()

    try:
        catalog, warnings = build_catalog(Path(args.source))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    write_catalog(catalog, warnings, args.output)
    print(f"entries={catalog['summary']['entry_count']}")
    print(f"o11_supported_odc_candidates={catalog['summary']['o11_supported_odc_candidate_count']}")
    print(f"o11_only_support={catalog['summary']['o11_only_support_count']}")
    print(f"warnings={len(warnings)}")


if __name__ == "__main__":
    main()
