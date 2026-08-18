#!/usr/bin/env python3
"""Compute app-chrome coverage as a set difference over declared chrome elements.

The blueprint (or screen inventory) declares `app_chrome`; the emitted Mentor
prompts either carry a CHROME BATCH block naming each element or they do not.
Coverage is mechanical: uncovered = declared - carried. The verdict is computed,
never hand-authored. This is the visual track's equivalent of
`outsystems-plan-to-mentor`'s requirement coverage review, and it exists for the
same reason: the artifact that feeds the build can silently lose something the
artifact upstream of it got right.

INPUT CONTRACT: pass the EMITTED PROMPT PACKAGE, not the run document that
contains it. A run journal narrates what happened, and narration names the same
elements an instruction does.

WHY THIS EXISTS (V84, LoanDesk, 2026-08-12). An app deployed with no navigation
menu at all: `ManageItems` was reachable by no route in the app, URL only. The
menu was never lost upstream -- `screen-inventory.json` declared it, all six
per-screen `blueprint.json` files carried it, and the cross-blueprint report
passed them. The emitted prompts transcribed `app_chrome.layout_block` as each
screen's `Layout: LayoutTopMenu` and dropped `app_chrome.menu`. Every gate in
the chain compared a different pair -- blueprint vs schema, blueprint vs
blueprint, plan vs PRD, deployed model vs expected delta -- and none compared
blueprint chrome vs emitted prompts, which is the one comparison that catches
this.

=============================================================================
EVIDENCE IS A CANONICAL BLOCK. THIS CHECKER DOES NOT READ ENGLISH.
=============================================================================

    CHROME BATCH: Menu block (the TopMenu layout's navigation web block)
      menu link: "Catalogue" -> Catalogue
      menu link: "My loans" -> MyLoans
      menu link: "Manage items" -> ManageItems
      app title: "LoanDesk"
      user info: "User profile summary"

A label counts as carried when a `CHROME BATCH:` block names it in a directive
of the matching kind. Labels are compared whole, after case and punctuation
normalisation -- never as substrings. A `menu link` directive additionally
requires a destination that is real, singular and correct: `<screen>`, `TODO
later` and `ScreenName` are the template rather than an answer; one label gets
exactly one destination across the package, so a correct directive cannot
launder an incorrect one beside it; and when the chrome source declares a target
(`screen-inventory.json` carries `menu[].target`) the destination must match it.
Two sources declaring different targets for one label fail here rather than
being deferred. Nothing else is evidence.

A declared target also RESOLVES the case where a real screen is named like a
template -- `Pending Approvals`, `Unknown Items`, `Decide Later`. Nothing inside
such a string says whether it is an answer or the shape of one, so the source
decides: a destination matching the target its own entry declares is accepted,
and the identical string with no declared target behind it is still refused.
Structural rejections are exempt from this and always refused, because no screen
can be called `<screen>` or `...` (Codex round 6, 2026-08-12).

WHY, AND IT IS NOT A PREFERENCE. Three rounds of adversarial review (Codex,
2026-08-12) each broke a version that tried to recognise instructions in prose:

  round 1  anchored on chrome vocabulary. `App chrome: Catalogue, My loans,
           Manage items` and `The navigation menu should preserve ...` passed;
           `In Common UI Flow, edit Menu and add links ...` and `Configure the
           top navigation with links ...` failed.
  round 2  required a base-form action token. `The navigation menu will add
           links ...` and `The navigation menu instructions include links ...`
           still passed; the imperative `Link ... from the Menu block to their
           screens` still failed.
  round 3  required the verb to open its clause. `The navigation menu will
           FIRST add links ...` and `... will add links AND include ...` passed
           through the lead-in and conjunction cases; `You must add menu links
           ...` and `Must add menu links ...` were refused for using obligation
           rather than imperative modality. Separately, `Update navigation for
           Loan entries, My loans and Manage items` passed because `entries`
           sat inside a declared LABEL and was counted as the destination.

Each round closed its own probes and the next round found more, which is the
signature of approximating a natural language rather than defining a form. The
ruling that ended it (Codex, round 3): "Prefer a canonical machine-readable
instruction block over progressively approximating English grammar." Since this
skill AUTHORS the prompts, the canonical block costs an emission rule and buys a
gate with no grammar surface to probe.

The trade is deliberate and it is not free: a prompt package that wires the
Menu block in perfectly good prose now reports NOT READY. That includes the two
shapes round 1 required be accepted -- they are regression-tested as NOT READY
now, under round 3's later ruling. Emitting the block is the fix, and Chrome
Batch Discipline carries that emission rule.

THE BLIND SPOTS, STATED SO NOBODY READS `READY` AS MEANING MORE THAN IT DOES.

1. This checker's universe is what the blueprint DECLARES. It answers "did every
   chrome element you designed reach a prompt?", never "did you design the
   chrome this app needed?". A blueprint with no `app_chrome` has nothing to
   gate and exits 2 rather than passing.
2. It reads prompts, not a built app. A CHROME BATCH block is evidence the
   instruction was emitted, not that Mentor executed it. The enumeration gate
   and the post-publish assertion recompute cover what was built; neither can
   see an instruction that was never written.
3. Of the Chrome Batch Discipline list, four kinds are gated: menu entries, app
   title, user-info chrome, and the layout block. Declared search bars, theme
   toggles, notification badges and global command buttons are NOT gated --
   their blueprint form is free prose. They stay a disclosed blind spot until
   the blueprint schema makes them mechanically comparable.
4. There is NO platform-default exemption. An earlier version exempted user-info
   chrome that a menu-bearing layout was assumed to supply; Codex showed the
   inference was lexical rather than semantic (`Login history shortcut` and
   `Sign out control` were both exempted, while ODC Screens proves only that
   `LayoutTopMenu`'s `Header` contains sign-in logic). Every declared element is
   now scored. If the blueprint schema ever carries an exact marker for
   layout-supplied chrome, this is where it would be honoured -- inference is
   not a substitute for one.

There is deliberately no deferral bypass. Chrome Batch Discipline allows an
implementation route to defer chrome, recorded in the prompt packet -- but a
flag that turns this gate off would reintroduce exactly the failure it exists to
catch, since the LoanDesk run believed it had handled chrome too. If chrome is
genuinely deferred, do not gate the blueprint that declares it.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MENU = "menu"
APP_TITLE = "app title"
USER_INFO = "user info"
LAYOUT_BLOCK = "layout block"

CANONICAL_BLOCK = """CHROME BATCH: Menu block (the TopMenu layout's navigation web block)
  menu link: "<label>" -> <screen>
  app title: "<label>"
  user info: "<label>\""""

# Opens a canonical block. Everything contiguous below it that parses as a
# directive belongs to it.
_BATCH_HEADER = re.compile(r"^\s*chrome batch\s*:", re.IGNORECASE)

# One directive. The kind is a fixed keyword, the label is a whole field, and
# the destination is a separate field -- so no part of a label can ever be read
# as evidence for another part of the same line.
_DIRECTIVE = re.compile(
    r"^\s*(?P<kind>menu link|menu entry|app title|user info|layout)\s*:\s*(?P<body>\S.*)$",
    re.IGNORECASE,
)

_DIRECTIVE_KINDS = {
    "menu link": MENU,
    "menu entry": MENU,
    "app title": APP_TITLE,
    "user info": USER_INFO,
    "layout": LAYOUT_BLOCK,
}

_DESTINATION = re.compile(r"->|→|=>")

# A destination that names the shape of an answer instead of giving one.
#
# Three rules, all closed sets rather than open heuristics -- open heuristics are
# what four review rounds kept defeating. Round 4 caught `<screen>`, `TODO` and
# `TBD`; round 5 caught the expanded forms `TODO later`, `TBD - decide` and
# `ScreenName`, which an exact-match list cannot see.
#
# Closed sets bound the false NEGATIVES; they do not bound the false positives,
# and round 6 measured one on merged main -- `_PLACEHOLDER_LEAD` matches a
# LEADING TOKEN, so it refused the real screen `Pending Approvals`. Widening the
# lists is safe; every word added here also removes a legal screen name, so a
# word earns its place only if no screen would sensibly start with it.
_BRACKETED = re.compile(r"[<>{}\[\]]")
_PLACEHOLDER_LEAD = re.compile(
    r"^(?:todo|tbd|tbc|fixme|xxx|wip|pending|unknown|decide|later|placeholder"
    r"|n/?a|none|null|na)\b",
    re.IGNORECASE,
)
_PUNCTUATION_ONLY = re.compile(r"^[\W_]+$")
# Destinations that name the KIND of thing wanted rather than an instance.
_GENERIC_DESTINATIONS = {
    "screen", "screens", "page", "pages", "target", "targets", "destination",
    "destinations", "name", "label", "value", "example", "sample",
    "screenname", "pagename", "targetscreen", "targetpage", "targetname",
    "yourscreen", "myscreen", "somescreen", "thescreen", "anyscreen",
    "examplescreen", "samplescreen", "screenhere", "insertscreen",
}


def _is_placeholder(text: str, declared_target: str | None = None) -> bool:
    """Does this destination name the shape of an answer instead of giving one?

    Two kinds of rule, and only one of them can be overruled.

    STRUCTURAL -- empty, bracketed, punctuation-only. No ODC screen can be named
    `<screen>` or `...`, so no blueprint can make one real. Not vouchable.

    LEXICAL -- the leading-word list and the generic-noun set. `Pending
    Approvals` is a placeholder-shaped string AND an entirely ordinary screen,
    and nothing inside the string tells you which. The chrome source is the
    authority: when it declares that exact target for this entry, the lexical
    rules stand down. `declared_target` carries the squashed declared target for
    the label on THIS directive, or None when the source declares none -- and a
    source that declares none has nothing to vouch with, so the same literal
    string stays refused there (Codex round 6, 2026-08-12).
    """
    stripped = text.strip()
    if not stripped:
        return True
    if _BRACKETED.search(stripped):
        return True
    if _PUNCTUATION_ONLY.match(stripped):
        return True
    squashed = _squash(stripped)
    if squashed and squashed == declared_target:
        return False
    if _PLACEHOLDER_LEAD.match(stripped):
        return True
    return squashed in _GENERIC_DESTINATIONS

# `Screen: Catalogue   Roles: (anonymous)   Layout: LayoutTopMenu` -- the exact
# key-value form the prompts already use to assign a layout. Structured, not
# prose: a keyword, a colon, and the block name.
_LAYOUT_ASSIGNMENT = re.compile(r"\blayout\s*:\s*(?P<block>[A-Za-z0-9_]+)", re.IGNORECASE)

# Header chrome that names the signed-in user. The rest of the header (search,
# theme toggle, badges) is a disclosed blind spot.
_USER_INFO_ELEMENT = re.compile(
    r"\b(?:user|profile|account|avatar|identity|sign[\s-]?(?:in|out)|log(?:in|out))\b",
    re.IGNORECASE,
)


def _squash(text: str) -> str:
    """Alphanumerics only, so a label survives the spelling the prompt uses:
    `My loans` in the blueprint, `MyLoans` in the directive."""
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def _unquote(text: str) -> str:
    text = text.strip()
    for pair in ('""', "''", "``", "“”", "‘’"):
        if len(text) >= 2 and text[0] == pair[0] and text[-1] == pair[1]:
            return text[1:-1].strip()
    return text


def carried_labels(
    text: str, declared_targets: dict[str, str] | None = None
) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    """Parse CHROME BATCH directives.

    Returns `(labels_by_kind, menu_destinations_by_label)`, both squashed. A
    menu label appears in the first only when it also has a real destination in
    the second, so a directive that names an entry without wiring it -- or wires
    it to a placeholder -- contributes nothing.

    `declared_targets` maps squashed menu label to squashed declared target, and
    is what lets a real screen called `Pending Approvals` through a rule written
    to catch `pending`. It only ever makes the parse MORE accepting, and only
    for a destination that matches the target its own source declared -- see
    `_is_placeholder`.

    A directive outside a block is ignored: the block header is what makes the
    batch deliberate, and it is the producer-first shape Chrome Batch Discipline
    already requires.
    """
    declared_targets = declared_targets or {}
    found: dict[str, set[str]] = {}
    destinations: dict[str, set[str]] = {}
    in_block = False
    for line in text.splitlines():
        if _BATCH_HEADER.match(line):
            in_block = True
            continue
        if not in_block:
            continue
        if not line.strip():
            continue
        match = _DIRECTIVE.match(line)
        if match is None:
            in_block = False
            continue
        kind = _DIRECTIVE_KINDS[match.group("kind").lower()]
        body = match.group("body")
        if kind == MENU:
            # A menu directive must say where the link goes, and must say it
            # for real: `-> <screen>` is the template, not an answer.
            split = _DESTINATION.search(body)
            if split is None:
                continue
            target = _unquote(body[split.end():])
            body = body[: split.start()]
            label = _squash(_unquote(body))
            if _is_placeholder(target, declared_targets.get(label)):
                continue
            destinations.setdefault(label, set()).add(_squash(target))
        found.setdefault(kind, set()).add(_squash(_unquote(body)))
    return found, destinations


def assigned_layouts(text: str) -> set[str]:
    return {
        _squash(m.group("block")) for m in _LAYOUT_ASSIGNMENT.finditer(text)
    }


def _label_of(entry: object) -> str | None:
    if isinstance(entry, str):
        return entry.strip() or None
    if isinstance(entry, dict):
        label = entry.get("label")
        if isinstance(label, str) and label.strip():
            return label.strip()
    return None


def _target_of(entry: object) -> str | None:
    """The screen a menu entry declares it points at, when it declares one."""
    if isinstance(entry, dict):
        for key in ("target", "screen", "destination"):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def chrome_elements(chrome: dict) -> list[tuple[str, str, str | None]]:
    """Declared chrome as `(kind, label, declared_target)` triples.

    The target is the screen a menu entry says it points at --
    `screen-inventory.json` carries these (`My loans` -> `My Loans`) and the
    per-screen blueprints do not. An earlier version dropped them, reasoning
    that a screen name appears throughout a prompt package and so is not
    evidence. That was true of the prose matcher and stopped being true when the
    directive gained a typed destination field: Codex round 4 (2026-08-12) drove
    a fully wrong permutation of the three targets straight through the gate.
    """
    found: list[tuple[str, str, str | None]] = []

    def add(kind: str, value: object, target: str | None = None) -> None:
        if isinstance(value, str) and value.strip():
            found.append((kind, value.strip(), target))

    add(LAYOUT_BLOCK, chrome.get("layout_block"))
    add(APP_TITLE, chrome.get("app_title"))

    sidebar = chrome.get("sidebar") if isinstance(chrome.get("sidebar"), dict) else {}
    add(APP_TITLE, sidebar.get("app_title"))
    logo = sidebar.get("logo") if isinstance(sidebar.get("logo"), dict) else {}
    add(APP_TITLE, logo.get("text"))

    for entry in chrome.get("menu") or []:
        add(MENU, _label_of(entry), _target_of(entry))
    for group in sidebar.get("nav_groups") or []:
        if not isinstance(group, dict):
            continue
        for item in group.get("items") or []:
            add(MENU, _label_of(item), _target_of(item))

    header = chrome.get("header") if isinstance(chrome.get("header"), dict) else {}
    for item in header.get("content") or []:
        element = item.get("element") if isinstance(item, dict) else item
        if isinstance(element, str) and _USER_INFO_ELEMENT.search(element):
            add(USER_INFO, element)

    return found


def _json_sources(path: Path) -> list[Path]:
    if path.is_dir():
        return sorted(path.rglob("*.json"))
    return [path]


def collect_chrome(
    path: Path,
) -> tuple[
    list[tuple[str, str, str | None, Path]], dict[tuple[str, str], str], list[str]
]:
    """Union the chrome declared across every source, deduplicated.

    A repeated element UPGRADES rather than being dropped: the per-screen
    blueprints declare menu labels with no target and `screen-inventory.json`
    declares the same labels with one, and the blueprints sort first. Taking
    strictly the first sighting would therefore discard every declared target on
    a real design directory.

    Two sources declaring DIFFERENT non-empty targets for one label is recorded
    as a CONFLICT and fails, rather than being settled by file order. An earlier
    version deferred that to the cross-blueprint report; Codex round 5
    (2026-08-12) showed the deferral was empty — inventory targets never enter
    the blueprints, so that pass compares only blueprint label order and can
    never see the disagreement. Choosing by sort order let a prompt matching
    whichever target happened to sort first report READY.
    """
    declared: list[tuple[str, str, str | None, Path]] = []
    index: dict[tuple[str, str], int] = {}
    conflicts: dict[tuple[str, str], str] = {}
    errors: list[str] = []
    for source in _json_sources(path):
        try:
            data = json.loads(source.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"cannot read {source}: {exc}")
            continue
        chrome = data.get("app_chrome") if isinstance(data, dict) else None
        if not isinstance(chrome, dict):
            continue
        for kind, label, target in chrome_elements(chrome):
            key = (kind, _squash(label))
            if key not in index:
                index[key] = len(declared)
                declared.append((kind, label, target, source))
                continue
            existing = declared[index[key]]
            if not target:
                continue
            if existing[2] is None:
                declared[index[key]] = (existing[0], existing[1], target, existing[3])
            elif _squash(existing[2]) != _squash(target):
                conflicts[key] = (
                    f'"{existing[2]}" ({existing[3]}) vs "{target}" ({source})'
                )
    return declared, conflicts, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "chrome_source",
        type=Path,
        help="Blueprint or screen-inventory JSON declaring app_chrome, "
        "or a directory of them",
    )
    parser.add_argument(
        "prompts",
        type=Path,
        nargs="+",
        help="Emitted Mentor prompt file(s) — the prompt package, not the run "
        "document that quotes it",
    )
    args = parser.parse_args(argv)

    if not args.chrome_source.exists():
        print(f"file not found: {args.chrome_source}", file=sys.stderr)
        return 2
    for path in args.prompts:
        if not path.is_file():
            print(f"file not found: {path}", file=sys.stderr)
            return 2

    declared, conflicts, errors = collect_chrome(args.chrome_source)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 2
    if not declared:
        print(
            f"no app_chrome found in {args.chrome_source}; "
            "pass the blueprint or screen inventory that declares the chrome",
            file=sys.stderr,
        )
        return 2

    # What each menu entry's own source says it points at, keyed and valued the
    # way directives are compared. This is the only thing that can vouch for a
    # destination the lexical placeholder rules would otherwise refuse.
    declared_targets = {
        _squash(label): _squash(target)
        for kind, label, target, _ in declared
        if kind == MENU and target
    }

    carried: dict[str, set[str]] = {}
    menu_destinations: dict[str, set[str]] = {}
    layouts: set[str] = set()
    for path in args.prompts:
        text = path.read_text(encoding="utf-8")
        labels, destinations = carried_labels(text, declared_targets)
        for kind, values in labels.items():
            carried.setdefault(kind, set()).update(values)
        for label, values in destinations.items():
            menu_destinations.setdefault(label, set()).update(values)
        layouts |= assigned_layouts(text)

    uncovered: list[tuple[str, str, str, Path]] = []
    for kind, label, target, source in declared:
        key = (kind, _squash(label))
        if key in conflicts:
            uncovered.append(
                (kind, label, f"sources declare conflicting targets: {conflicts[key]}",
                 source)
            )
            continue
        pool = layouts | carried.get(LAYOUT_BLOCK, set()) if kind == LAYOUT_BLOCK \
            else carried.get(kind, set())
        if _squash(label) not in pool:
            uncovered.append((kind, label, "no directive names it", source))
            continue
        if kind != MENU:
            continue
        wired = menu_destinations.get(_squash(label), set())
        # One label, one destination. A package that wires the same entry to two
        # different screens has not decided, and unioning them let a correct
        # directive launder an incorrect one (Codex round 5, 2026-08-12).
        if len(wired) > 1:
            uncovered.append(
                (kind, label,
                 f"wired to {len(wired)} conflicting destinations: "
                 f"{', '.join(sorted(wired))}", source)
            )
            continue
        # The inventory said where this entry points. A directive that wires it
        # somewhere else is not coverage, it is a wrong menu.
        if target and _squash(target) not in wired:
            got = ", ".join(sorted(wired)) or "nothing"
            uncovered.append(
                (kind, label, f'declared target "{target}", wired to {got}', source)
            )

    total = len(declared)
    covered = total - len(uncovered)
    print(
        f"chrome coverage: {covered}/{total} declared chrome elements "
        f"named by a CHROME BATCH directive"
    )

    if uncovered:
        print("uncovered (declared by the blueprint chrome, not carried by a directive):")
        for kind, label, reason, source in uncovered:
            print(f"- {kind} \"{label}\" — {reason} ({source})")

        print("\nChrome is carried by a canonical producer batch, never by prose:")
        for line in CANONICAL_BLOCK.splitlines():
            print(f"  {line}")

        print("chrome verdict: NOT READY")
        return 1

    # The verdict carries its own scope: prose scope does not survive being
    # quoted, and a bare "READY" reads as "the app has a working menu".
    print(
        f"chrome verdict: READY ({covered}/{total} declared chrome elements named "
        "by a CHROME BATCH directive -- does not check that the blueprint declared "
        "the chrome the app needed, nor that Mentor built it)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
