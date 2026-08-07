#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


SCREEN_CREATE_RE = re.compile(
    r"create (?:a\s+)?(?:new\s+)?(?:minimal\s+)?Web Screen named ([A-Za-z][A-Za-z0-9_]*)",
    re.IGNORECASE,
)
NAVIGATE_RE = re.compile(
    r"(?:Navigate to|navigates to|navigate to)(?: the)? ([A-Za-z][A-Za-z0-9_]*) screen",
    re.IGNORECASE,
)
MARKDOWN_BATCH_RE = re.compile(r"^##\s+BATCH\s+([A-Za-z0-9]+)\b.*$", re.MULTILINE)
YAML_ID_RE = re.compile(r"^\s{2}- id:\s*(.+?)\s*$")
YAML_NAME_RE = re.compile(r"^\s{4}name:\s*(.+?)\s*$")
YAML_PROMPT_RE = re.compile(r"^\s{4}prompt:\s*\|\s*$")


def _clean(value):
    return value.strip().strip('"').strip("'")


def parse_markdown_batches(text):
    matches = list(MARKDOWN_BATCH_RE.finditer(text))
    batches = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        label = _clean(match.group(1))
        batches.append({"label": label, "name": "", "prompt": text[start:end]})
    return batches


def parse_yaml_batches(text):
    batches = []
    current = None
    in_prompt = False

    for line in text.splitlines():
        id_match = YAML_ID_RE.match(line)
        if id_match:
            if current:
                current["prompt"] = "\n".join(current["prompt_lines"])
                batches.append(current)
            current = {
                "label": _clean(id_match.group(1)),
                "name": "",
                "prompt_lines": [],
            }
            in_prompt = False
            continue

        if not current:
            continue

        name_match = YAML_NAME_RE.match(line)
        if name_match and not in_prompt:
            current["name"] = _clean(name_match.group(1))
            continue

        if YAML_PROMPT_RE.match(line):
            in_prompt = True
            continue

        if in_prompt:
            current["prompt_lines"].append(line[6:] if line.startswith("      ") else line)

    if current:
        current["prompt"] = "\n".join(current["prompt_lines"])
        batches.append(current)

    return batches


def parse_batches(path):
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return parse_yaml_batches(text)
    return parse_markdown_batches(text)


def screen_creations(batches, existing_screens):
    created = {name: -1 for name in existing_screens}
    for index, batch in enumerate(batches):
        for name in SCREEN_CREATE_RE.findall(batch["prompt"]):
            created.setdefault(name, index)
    return created


def navigation_errors(batches, existing_screens):
    created = screen_creations(batches, existing_screens)
    errors = []

    for index, batch in enumerate(batches):
        for target in NAVIGATE_RE.findall(batch["prompt"]):
            created_index = created.get(target)
            if created_index is None:
                errors.append(
                    f"batch {batch['label']} -> {target} has no matching screen creation"
                )
            elif created_index > index:
                target_batch = batches[created_index]["label"]
                errors.append(
                    f"batch {batch['label']} -> {target} created in batch {target_batch}"
                )

    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate that Mentor prompt batches create navigation target screens before wiring Navigate actions."
    )
    parser.add_argument("prompt_file", type=Path)
    parser.add_argument(
        "--existing-screen",
        action="append",
        default=[],
        help="Screen name that already exists before these batches run. Can be repeated.",
    )
    args = parser.parse_args(argv)

    try:
        batches = parse_batches(args.prompt_file)
    except OSError as exc:
        print(f"{args.prompt_file}: {exc}", file=sys.stderr)
        return 2

    if not batches:
        print(f"{args.prompt_file}: no prompt batches found", file=sys.stderr)
        return 2

    errors = navigation_errors(batches, set(args.existing_screen))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"navigation order valid: {len(batches)} batches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
