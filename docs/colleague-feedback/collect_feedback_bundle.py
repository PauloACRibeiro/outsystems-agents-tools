#!/usr/bin/env python3
"""Bundle a colleague's sprint-loop feedback into one .tgz they can email.

Collects, when present: their filled-in FEEDBACK.md, the pack's
``PACKAGE-MANIFEST.json`` from the docs folder (THE version and digest record
-- skill frontmatter carries no version field), the YAML frontmatter of each
installed ``outsystems-*`` skill (identity stamp: name and description --
never the skill body; identical copies across roots are collected once), any
``*receipt*.json`` files those skills left behind, and a short generated
environment.txt (OS, Python version, which skills roots exist).

Every text file is redacted before it enters the archive: the user's home
directory becomes ``~``, GUID-shaped ids become ``<redacted-guid>``, and
``*.outsystems.dev`` / ``*.outsystems.app`` hostnames become ``<redacted-host>``.

There is NO telemetry, NO network access and NO server in this script. It never
opens an outbound connection -- it only reads local files and writes one local
archive. Use --dry-run to see exactly what would be collected before writing.
Python 3.9+, standard library only.
"""

import argparse
import platform
import re
import sys
import tarfile
import time
from io import BytesIO
from pathlib import Path

DEFAULT_SKILLS_ROOTS = ["~/.claude/skills", "~/.agents/skills"]
DEFAULT_DOCS_ROOT = "~/outsystems-sprint-loop"
SKILL_PREFIX = "outsystems-"
ARCHIVE_PREFIX = "outsystems-sprint-loop-feedback"

# Built from character classes on purpose -- no literal example id in this file.
HEX = "[0-9a-fA-F]"
GUID_RE = re.compile(r"\b{h}{{8}}-(?:{h}{{4}}-){{3}}{h}{{12}}\b".format(h=HEX))
HOST_RE = re.compile(r"[\w-]+\.outsystems\.(?:dev|app)")

NOTES = []


def note(message):
    """Record a non-fatal problem; printed at the end, never raised."""
    NOTES.append(message)


def redact(text, counts):
    """Apply the three redaction rules, tallying hits per rule."""
    home = str(Path.home())
    if home and home != "/" and home in text:
        counts["home-path"] += text.count(home)
        text = text.replace(home, "~")
    text, hits = GUID_RE.subn("<redacted-guid>", text)
    counts["guid"] += hits
    text, hits = HOST_RE.subn("<redacted-host>", text)
    counts["outsystems-host"] += hits
    return text


def read_text(path):
    """Read a text file, or return None and leave a note."""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        note("skipped {} ({})".format(path.name, exc.strerror or exc))
        return None


def frontmatter(text):
    """Return the YAML frontmatter block, fences included, or None."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[: index + 1]) + "\n"
    return None


def root_label(root, used):
    """Short readable folder name for a skills root inside the archive."""
    base = root.parent.name.lstrip(".") or "root"
    label, suffix = base, 2
    while label in used:
        label, suffix = "{}-{}".format(base, suffix), suffix + 1
    used.add(label)
    return label


def build_environment(roots, counts):
    lines = [
        "platform: {}".format(platform.platform()),
        "python_version: {}".format(platform.python_version()),
        "sys_version: {}".format(" ".join(sys.version.split())),
        "skills_roots:",
    ]
    for root in roots:
        state = "exists" if root.is_dir() else "missing"
        lines.append("  - {} ({})".format(root, state))
    return redact("\n".join(lines) + "\n", counts)


def collect(args, roots, counts):
    """Return a list of (arcname, text) pairs, all already redacted."""
    items = []

    if args.feedback:
        path = Path(args.feedback).expanduser()
        if path.is_file():
            text = read_text(path)
            if text is not None:
                items.append(("FEEDBACK.md", redact(text, counts)))
        else:
            note("feedback file not found: {}".format(args.feedback))

    manifest = Path(args.docs_root).expanduser() / "PACKAGE-MANIFEST.json"
    if manifest.is_file():
        text = read_text(manifest)
        if text is not None:
            items.append(("PACKAGE-MANIFEST.json", redact(text, counts)))
    else:
        note("pack manifest not found: {} (no version info in this bundle)".format(manifest))

    used_labels = set()
    seen = {}
    for root in roots:
        label = root_label(root, used_labels)
        if not root.is_dir():
            note("skills root not found: {}".format(root))
            continue
        for skill in sorted(p for p in root.iterdir() if p.is_dir()):
            if not skill.name.startswith(SKILL_PREFIX):
                continue
            base = "installed-skills/{}/{}".format(label, skill.name)
            skill_md = skill / "SKILL.md"
            if skill_md.is_file():
                text = read_text(skill_md)
                block = frontmatter(text) if text is not None else None
                if block is None:
                    note("no frontmatter in {}/SKILL.md".format(skill.name))
                elif seen.get((skill.name, "frontmatter")) == block:
                    # identical copy in an earlier root: one copy is enough,
                    # and environment.txt already records that both roots exist
                    note("{}: frontmatter identical to the copy already collected".format(base))
                else:
                    seen[(skill.name, "frontmatter")] = block
                    items.append((base + "/SKILL.frontmatter.md", redact(block, counts)))
            for receipt in sorted(skill.rglob("*receipt*.json")):
                text = read_text(receipt)
                if text is None:
                    continue
                if seen.get((skill.name, receipt.name)) == text:
                    note("{}/{}: identical to the copy already collected".format(base, receipt.name))
                    continue
                seen[(skill.name, receipt.name)] = text
                items.append((base + "/" + receipt.name, redact(text, counts)))

    items.append(("environment.txt", build_environment(roots, counts)))
    return items


def write_archive(archive_path, stem, items):
    now = int(time.time())
    with tarfile.open(archive_path, "w:gz") as tar:
        top = tarfile.TarInfo(stem)
        top.type, top.mode, top.mtime = tarfile.DIRTYPE, 0o755, now
        tar.addfile(top)
        for arcname, text in items:
            data = text.encode("utf-8")
            info = tarfile.TarInfo("{}/{}".format(stem, arcname))
            info.size, info.mode, info.mtime = len(data), 0o644, now
            tar.addfile(info, BytesIO(data))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out-dir", default=".", help="where to write the .tgz (default: here)")
    parser.add_argument("--feedback", help="path to your filled-in FEEDBACK.md")
    parser.add_argument("--skills-root", action="append", dest="skills_roots",
                        help="a skills directory to scan; repeatable (default: {})".format(
                            " and ".join(DEFAULT_SKILLS_ROOTS)))
    parser.add_argument("--docs-root", default=DEFAULT_DOCS_ROOT,
                        help="pack docs folder holding PACKAGE-MANIFEST.json (default: {})".format(
                            DEFAULT_DOCS_ROOT))
    parser.add_argument("--dry-run", action="store_true",
                        help="list the files and per-rule redaction counts, write nothing")
    args = parser.parse_args()

    roots = [Path(r).expanduser() for r in (args.skills_roots or DEFAULT_SKILLS_ROOTS)]
    counts = {"home-path": 0, "guid": 0, "outsystems-host": 0}
    items = collect(args, roots, counts)

    stem = "{}-{}".format(ARCHIVE_PREFIX, time.strftime("%Y%m%d-%H%M%S", time.gmtime()))
    out_dir = Path(args.out_dir).expanduser()
    archive_path = out_dir / (stem + ".tgz")
    total = sum(len(text.encode("utf-8")) for _, text in items)

    for arcname, text in items:
        print("{}/{}  ({} bytes)".format(stem, arcname, len(text.encode("utf-8"))))

    if args.dry_run:
        print("\nDRY RUN - nothing written. Would be: {}".format(archive_path))
        size_line = "content bytes: {}".format(total)
    else:
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            write_archive(archive_path, stem, items)
        except OSError as exc:
            print("ERROR: could not write archive: {}".format(exc), file=sys.stderr)
            return 1
        print("\nArchive: {}".format(archive_path))
        size_line = "archive bytes: {}".format(archive_path.stat().st_size)

    print("Files: {}\n{}".format(len(items), size_line))
    print("Redacted: {} home path(s), {} GUID(s), {} OutSystems hostname(s)".format(
        counts["home-path"], counts["guid"], counts["outsystems-host"]))
    for message in NOTES:
        print("Note: {}".format(message))
    return 0


if __name__ == "__main__":
    sys.exit(main())
