#!/usr/bin/env python3
"""Generate references/built-in-widgets.md from runtime-widgets-js sources.

Parses the machine-generated widget property interfaces in
OutSystems/runtime-widgets-js ``src/Generated/*.Generated.ts`` — the actual
runtime contract for the ~30 built-in platform widgets — and emits a markdown
inventory. The inventory is GENERATED, never hand-edited: re-run this script
against a fresh download to refresh it (procedure in
``maintenance/refresh-checklist.md``).

Python 3.7+ stdlib only. Deterministic: same inputs → byte-identical output
(commit/date are passed in, never read from the clock).

Usage:
    python3 scripts/generate_builtin_widgets.py \
        --source <dir with *.Generated.ts> \
        --out references/built-in-widgets.md \
        --commit <source repo commit sha> --date YYYY-MM-DD
"""

import argparse
import re
import sys
from pathlib import Path

# Interface noise that is not part of the design-relevant contract.
SKIP_SUFFIX = "_dataFetchStatus"          # fetch-state twins of data-bound props
SKIP_NAMES = {"placeholders", "expandedInWebEditor"}  # structural/editor-internal

ENUM_RE = re.compile(r"export\s+const\s+enum\s+(\w+)\s*\{([^}]*)\}", re.S)
ALIAS_RE = re.compile(r"export\s+type\s+(\w+)\s*=\s*([^;]+);", re.S)
IFACE_RE = re.compile(
    r"export\s+interface\s+(\w+)\s*(?:extends\s+[\w.]+(?:<[^>]*>)?\s*)?\{", re.S
)


def pascal(name):
    return name[:1].upper() + name[1:] if name else name


def body_of(text, open_brace_idx):
    """Return the brace-balanced body starting after ``{`` at open_brace_idx."""
    depth = 0
    for i in range(open_brace_idx, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace_idx + 1:i]
    raise ValueError("unbalanced braces")


def split_members(body):
    """Split an interface body into ``name: type`` statements, respecting
    nesting so function types like ``(x: string) => void`` stay whole."""
    # NOTE: angle brackets are deliberately not depth-tracked — `=>` would
    # miscount, and generic type arguments never contain `;` in these files.
    members, buf, depth = [], [], 0
    for ch in body:
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        if ch == ";" and depth == 0:
            stmt = "".join(buf).strip()
            if stmt:
                members.append(stmt)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        members.append(tail)
    out = []
    for stmt in members:
        name, _, typ = stmt.partition(":")
        name = name.strip()
        optional = name.endswith("?")
        if optional:
            name = name[:-1].strip()
        out.append((name, " ".join(typ.split()), optional))
    return out


def clean_type(typ):
    typ = typ.replace("DataTypes.", "")
    typ = re.sub(r"\s*\|\s*(undefined|null)\b", "", typ).strip()
    if typ.startswith("(") and typ.endswith(")") and "=>" in typ:
        inner = typ[1:-1].strip()
        if inner.count("(") == inner.count(")"):
            typ = inner
    return typ


def parse_widget(path):
    text = path.read_text(encoding="utf-8")
    widget = path.name.replace(".Generated.ts", "")

    enums = []
    for m in ENUM_RE.finditer(text):
        members = [
            v.split("=")[0].strip()
            for v in m.group(2).split(",")
            if v.strip()
        ]
        enums.append((m.group(1), members))

    aliases = []
    for m in ALIAS_RE.finditer(text):
        aliases.append((m.group(1), " ".join(m.group(2).split())))

    placeholders, props, events = [], [], []
    for m in IFACE_RE.finditer(text):
        iface = m.group(1)
        body = body_of(text, text.index("{", m.start()))
        members = split_members(body)
        if iface == "I%sPlaceholders" % widget:
            for name, typ, _ in members:
                repeats = "Iterator" in typ
                placeholders.append((name, repeats))
        elif iface == "I%sProperties" % widget:
            for name, typ, optional in members:
                if name.endswith(SKIP_SUFFIX) or name in SKIP_NAMES:
                    continue
                typ = clean_type(typ)
                # events are on<Event> handler props; other function-typed
                # props (Dropdown labels/values mappers) stay properties
                is_event = (
                    "=>" in typ
                    and name.startswith("on")
                    and len(name) > 2 and name[2].isupper()
                )
                if is_event:
                    events.append((name, typ, optional))
                else:
                    props.append((name, typ, optional))
    return {
        "widget": widget, "enums": enums, "aliases": aliases,
        "placeholders": placeholders, "props": props, "events": events,
    }


def render(widgets, commit, date):
    lines = [
        "---",
        "name: builtin-widgets-inventory",
        "description: Generated inventory of the built-in platform widget "
        "runtime contracts — every property, event, enum, and placeholder of "
        "the ~30 native widgets (Button, Input, Dropdown, TableRecords, "
        "AdvancedHtml, …), in FULL PATH form. Use to verify a built-in "
        "widget's exact property names when writing content[] descriptors or "
        "checking a mapping against the runtime contract.",
        "---",
        "",
        "# Built-in Platform Widgets — Generated Runtime Contract Inventory",
        "",
        "> **Harvested from:** `OutSystems/runtime-widgets-js` (internal "
        "OutSystems repo, no published license — keep this bundle private) "
        "`src/Generated/*.Generated.ts` @ `%s` (%s)." % (commit, date),
        "> **GENERATED FILE — never hand-edit.** Regenerate with "
        "`scripts/generate_builtin_widgets.py` (procedure in "
        "`maintenance/refresh-checklist.md`). On disagreement with "
        "`outsystems-frontend-skills` prose, `OutSystems/outsystems-ui` is "
        "the tiebreaker.",
        "",
        "These are the **native platform widgets** (the \"built-in, not "
        "blocks\" set in `ui-reference.md`), as their machine-generated "
        "runtime property interfaces define them. Names are presented in "
        "FULL PATH PascalCase form (`Button.Enabled`) to match model-side "
        "naming; the runtime interfaces themselves spell properties "
        "camelCase (`enabled`). Fetch-status twins and editor-internal "
        "fields are omitted. `(repeats)` marks an iterator placeholder — "
        "its content renders once per source row.",
        "",
    ]
    for w in widgets:
        name = w["widget"]
        lines.append("## %s" % name)
        lines.append("")
        if not (w["props"] or w["events"] or w["placeholders"] or w["enums"]):
            lines.append("No own properties beyond the base widget contract.")
            lines.append("")
            continue
        if w["props"]:
            lines.append("| Property | Runtime type |")
            lines.append("|---|---|")
            for p, typ, optional in w["props"]:
                opt = " *(optional)*" if optional else ""
                lines.append("| `%s.%s` | `%s`%s |" % (name, pascal(p), typ, opt))
            lines.append("")
        if w["events"]:
            lines.append("| Event | Handler signature |")
            lines.append("|---|---|")
            for p, typ, optional in w["events"]:
                opt = " *(optional)*" if optional else ""
                lines.append("| `%s.%s` | `%s`%s |" % (name, pascal(p), typ, opt))
            lines.append("")
        if w["placeholders"]:
            slots = ", ".join(
                "`%s`%s" % (p, " (repeats)" if rep else "")
                for p, rep in w["placeholders"]
            )
            lines.append("Placeholders: %s" % slots)
            lines.append("")
        for ename, members in w["enums"]:
            lines.append("Enum `%s`: %s" % (ename, ", ".join("`%s`" % v for v in members)))
            lines.append("")
        for aname, expr in w["aliases"]:
            lines.append("Type `%s` = `%s`" % (aname, expr))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True, help="dir containing *.Generated.ts")
    ap.add_argument("--out", required=True, help="output markdown path")
    ap.add_argument("--commit", required=True, help="source repo commit sha")
    ap.add_argument("--date", required=True, help="harvest date YYYY-MM-DD")
    args = ap.parse_args(argv)

    src = Path(args.source)
    files = sorted(src.glob("*.Generated.ts"))
    if not files:
        print("no *.Generated.ts files in %s" % src, file=sys.stderr)
        return 2
    widgets = [parse_widget(f) for f in files]
    Path(args.out).write_text(render(widgets, args.commit, args.date), encoding="utf-8")
    print("wrote %s (%d widgets)" % (args.out, len(widgets)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
