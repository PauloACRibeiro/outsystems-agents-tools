#!/usr/bin/env python3
"""Validate an outsystems-ui-design enriched blueprint against the OMI contract.

Schema: schemas/enriched-blueprint.schema.json (projection of OMI's
odc-visual-source-enriched-blueprint.md). Stdlib only.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "enriched-blueprint.schema.json"

# TARGET PRODUCT: OutSystems Developer Cloud (ODC). See SKILL.md "Target product".
#
# The five layout blocks ODC ships in an app's own `Layouts` flow. Grounded in
# the ODC Themes doc (success.outsystems.com .../user_interface/themes/) and
# confirmed against the Layouts flow of a template-created ODC app (2026-08-10):
#   LayoutTopMenu     menu across the top; the block a new empty screen gets
#   LayoutSideMenu    menu in a left sidebar, top bar baked in
#   LayoutBlank       "a layout that doesn't contain the Menu"
#   LayoutBase        landing-page layout, Header + MainContent, "already has a
#                     Menu on the top"
#   LayoutBaseSection section container the docs describe as living *inside*
#                     LayoutBase rather than at the screen root; accepted here
#                     because it is a real element of the Layouts flow, but it
#                     carries no chrome of its own
# NOTE: `Layout_Top_Menu` (underscored) is NOT an ODC spelling. It appeared in a
# docs page and in the 2026-08-09 run dossier; the Layouts flow disproves it.
LAYOUT_BLOCKS = (
    "LayoutSideMenu", "LayoutTopMenu", "LayoutBlank", "LayoutBase", "LayoutBaseSection",
)

# Layouts that own a menu region, so a blueprint choosing one is expected to
# carry its menu content. LayoutBase qualifies on the Themes doc's wording
# ("already has a Menu on the top"); LayoutBaseSection does not - it is a
# content section nested in a layout that already made the chrome decision.
# Shared with outsystems-screen-inventory's MENU_BEARING (drift-tested).
MENU_BEARING_LAYOUTS = ("LayoutSideMenu", "LayoutTopMenu", "LayoutBase")

# Widgets/blocks whose presence means the region repeats over a row set, so it
# needs a data producer. `List` and `TableRecords` are both ODC built-in widgets
# with a repeating placeholder (`content` and `row` respectively) - verified
# against references/built-in-widgets.md, generated from OutSystems'
# runtime-widgets-js. `ListRecords` is deliberately absent: it is O11
# Traditional-Web only and is handled as a detector below.
REPEAT_MARKERS = ("List", "TableRecords", "Table", "Gallery", "Carousel", "AccordionList")

# Product-boundary detectors (maintainer decision, 2026-08-10): shipped surfaces
# speak ODC only, and O11-only names survive as *detectors* - naming one in a
# blueprint is an error whose message teaches the ODC replacement.
#
# Every entry must be grounded before it is added: the name must be documented
# as O11-only AND absent from references/built-in-widgets.md (the generated ODC
# runtime contract). Names that exist in both products (`TableRecords`,
# `Dropdown`, `ListItem`, `ListItemAction`) are NOT detectors - see SKILL.md.
O11_ONLY_BLOCKS = {
    # "List Records Widget ... Applies only to Traditional Web Apps" (O11 docs);
    # absent from the ODC runtime widget inventory.
    "ListRecords": "List (or TableRecords for a tabular layout)",
}
_O11_ONLY_RE = re.compile(r"\b(" + "|".join(O11_ONLY_BLOCKS) + r")\b")
# One register, as of 2026-09-01. `outsystems-mentor-implementation` is the
# semantic authority for this vocabulary - this schema is its projection, and on
# conflict the projection is what changes - and OMI's contract states the ODC
# literal DataType string, never a camelCase spelling. Two structural facts
# agree: the relationship form `<Target> Identifier` cannot be spelled in
# camelCase at all, and the length-bearing form is `Text(200)` in every one of
# its occurrences. See docs/adoption/data-type-register-unification.md.
ODC_BASIC_TYPES = (
    "Binary Data", "Boolean", "Currency", "Date", "Date Time", "Decimal",
    "Email", "Integer", "Long Integer", "Phone Number", "Text", "Time",
)

# The producer spellings this skill's own fixtures used to write. Retained ONLY
# so a legacy value is diagnosed by name, with the string to write instead,
# rather than reported as an unknown type.
LEGACY_CAMEL_REGISTER = {
    "binaryData": "Binary Data", "boolean": "Boolean", "currency": "Currency",
    "date": "Date", "dateTime": "Date Time", "decimal": "Decimal",
    "email": "Email", "integer": "Integer", "longInteger": "Long Integer",
    "phoneNumber": "Phone Number", "text": "Text", "time": "Time",
}

# All three are spellings of an ordinary auto-number primary key, and OMI's rule
# for one is the literal `Long Integer`. This mapping is deliberately NOT a case
# split: `longIntegerIdentifier` must never become `Long Integer Identifier`,
# which is in RESERVED_IDENTIFIER_TYPES below and fails every publish.
LEGACY_IDENTIFIER_TOKENS = {
    "integerIdentifier": "Long Integer",
    "longIntegerIdentifier": "Long Integer",
    "platformDefaultIdentifier": "Long Integer",
}

# A ProgressBar bound to a non-numeric attribute is the warning this drives.
NUMERIC_TYPES = {"Integer", "Long Integer", "Decimal", "Currency"}

# Shaped like the relationship form and fatal at publish. `Integer Identifier`
# and `Text Identifier` match the schema's `<Target> Identifier` pattern, so the
# pattern alone waves them through; `Identifier` and `Long Integer Identifier`
# are listed too so the rule reads as one rule rather than two halves. All four
# validate cleanly and then fail every publish with OS-RDBS-GEN-40002, masked as
# OS-DPL-50203 through the MCP path (SKILL.md, "Typed data model").
RESERVED_IDENTIFIER_TYPES = (
    "Identifier", "Integer Identifier", "Long Integer Identifier",
    "Text Identifier",
)

_TEXT_LENGTH_RE = re.compile(r"^Text\([1-9][0-9]*\)$")
_LEGACY_TEXT_LENGTH_RE = re.compile(r"^text\([1-9][0-9]*\)$")
_RELATIONSHIP_TYPE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]* Identifier$")


def canonical_data_type(value):
    """The canonical spelling of `value`, or None if it is outside the closed
    vocabulary.

    Register-aware by design: a legacy spelling canonicalises to the same string
    as the ODC literal it spells, so two blueprints that declare the same type
    in different registers compare equal rather than reading as a conflicting
    declaration of the same attribute.
    """
    if not isinstance(value, str):
        return None
    value = value.strip()
    if value in RESERVED_IDENTIFIER_TYPES:
        return None
    if value in ODC_BASIC_TYPES:
        return value
    if value in LEGACY_CAMEL_REGISTER:
        return LEGACY_CAMEL_REGISTER[value]
    if value in LEGACY_IDENTIFIER_TOKENS:
        return LEGACY_IDENTIFIER_TOKENS[value]
    if _TEXT_LENGTH_RE.match(value):
        return value
    if _LEGACY_TEXT_LENGTH_RE.match(value):
        return "T" + value[1:]
    if _RELATIONSHIP_TYPE_RE.match(value):
        return value
    return None
_NUMERIC_WIDGET_RE = re.compile(r"\b(ProgressBar|Counter)\b")
# (?!\s*=) - F-E: don't match HTML property syntax like "AdvancedHtml Tag=p".
_STATUS_WIDGET_RE = re.compile(r"\b(Tag|Badge)\b(?!\s*=)")

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "number": (int, float),
    "integer": int,
    "null": type(None),
}


def _expected_types(expected):
    """A schema `type` is either one name or a union list of them."""
    names = expected if isinstance(expected, list) else [expected]
    types = ()
    for name in names:
        entry = _TYPES[name]
        types += entry if isinstance(entry, tuple) else (entry,)
    return types


# --- placeholder ban (L12) --------------------------------------------------
#
# A blueprint whose entity name is `TBD` satisfies every shape rule in the
# contract and hands the downstream Mentor conversion a literal entity called
# TBD. Markers are rejected in a NAMED field set - the fields whose value
# becomes a model element, a binding, or a name acted on downstream - and
# deliberately NOT in the free-prose channels, where "TODO: confirm with the
# client" is a legitimate note. See placeholder_fields() for the set and for
# what it excludes.
#
# DUPLICATED verbatim in the sibling validator (outsystems-screen-inventory's
# validate_screen_inventory.py / outsystems-ui-design's validate_blueprint.py):
# no cross-skill Python import exists and the packs do not ship one. The drift
# gate is test_marker_list_matches_the_* in both suites.
PLACEHOLDER_MARKERS = ("TODO", "TBD", "FIXME", "PLACEHOLDER")
BARE_PLACEHOLDER_VALUES = ("...", "…")
# `<fill in>` / `[FILL-IN: colour]` / `{fill_in}`. Bracketed only: the bare
# phrase "users fill in the form" is ordinary prose in a behaviour field.
FILL_IN_PATTERN = r"[<\[{]\s*fill[ _-]?in[^>\]}]{0,24}[>\]}]"

_MARKER_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    + "|".join(re.escape(m) for m in PLACEHOLDER_MARKERS)
    + r")(?![A-Za-z0-9])",
    re.IGNORECASE,
)
_FILL_IN_RE = re.compile(FILL_IN_PATTERN, re.IGNORECASE)


class Finding(str):
    """A warning that carries its own handoff severity.

    Graduation, in one type: `graduating=True` means advisory while the author
    is still working, and blocking once they run `--handoff`. It is a `str`
    subclass on purpose - every consumer formats warnings as `f"WARNING: {w}"`
    and both suites compare them against plain strings, so the report stays
    byte-identical for anyone who never passes the flag.

    `graduating` is required, never defaulted: a warning added later has to
    decide, rather than inheriting "advisory" by saying nothing. The AST drift
    gate refuses a bare `warnings.append("...")` for the same reason.

    A warning graduates only if it is unconditionally author-fixable - there is
    always an action that clears it and clearing it is always right. Anything
    that can be a legitimate final state stays advisory, because neither
    validator has a waiver channel to clear it with.

    DUPLICATED verbatim in the sibling validator (outsystems-screen-inventory's
    validate_screen_inventory.py / outsystems-ui-design's validate_blueprint.py):
    no cross-skill Python import exists and the packs do not ship one. The drift
    gate is test_every_warning_classifies_itself in both suites.
    """

    def __new__(cls, text, graduating):
        finding = super().__new__(cls, text)
        finding.graduating = graduating
        return finding


def graduating_findings(warnings):
    """The subset that blocks at handoff - emission order, text verbatim."""
    return [w for w in warnings if getattr(w, "graduating", False)]


def advisory_findings(warnings):
    """The complement: what still prints as a plain WARNING at handoff."""
    return [w for w in warnings if not getattr(w, "graduating", False)]



def placeholder_in(text):
    """The placeholder marker in `text`, or None. Case-insensitive."""
    if not isinstance(text, str):
        return None
    if text.strip() in BARE_PLACEHOLDER_VALUES:
        return text.strip()
    match = _FILL_IN_RE.search(text) or _MARKER_RE.search(text)
    return match.group(0) if match else None


def _pf(path, value):
    """Yield (path, text) for a string field or a list-of-strings field."""
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            if isinstance(item, str):
                yield f"{path}[{index}]", item


def _regions(screen):
    """Every region on a screen, groups flattened, with its path."""
    for i, region in enumerate(_as_list(screen.get("main_content"))):
        if not isinstance(region, dict):
            continue
        base = f"main_content[{i}]"
        yield base, region
        if region.get("type") == "group":
            for j, item in enumerate(_as_list(region.get("items"))):
                if isinstance(item, dict):
                    yield f"{base}.items[{j}]", item


def placeholder_fields(bp):
    """The NAMED field set the placeholder ban covers.

    EXCLUDED on purpose: `evidence_boundary.*` and `target_context.review_notes`
    (the channels for recording what is not yet settled), `acceptance_checklist`
    (advisory human-facing prose by its own schema description), and
    `design_system.*` (free-form visual rules). A deferral note belongs there.

    INCLUDED since 2026-08-30: `screens[].render_gate[].label` and `.selector`.
    That key is gate-bearing by construction - a label names a row a downstream
    gate emits and a selector is executed against a live DOM - so it belongs
    with the named fields, not with the prose. Its `contains`/`equals`/`reason`
    stay out: those are literals about the UI, and a screen that renders the
    word "TBD" must stay assertable.
    """
    if not isinstance(bp, dict):
        return
    for key in ("name", "description", "primary_color"):
        yield from _pf(key, bp.get(key))

    tc = bp.get("target_context")
    if isinstance(tc, dict):
        for key in ("readable_app_name", "canonical_app_key", "existing_assets",
                    "target_surfaces"):
            yield from _pf(f"target_context.{key}", tc.get(key))

    chrome = bp.get("app_chrome")
    if isinstance(chrome, dict):
        for key in ("layout_block", "app_title"):
            yield from _pf(f"app_chrome.{key}", chrome.get(key))
        for i, entry in enumerate(_as_list(chrome.get("menu"))):
            if isinstance(entry, dict):
                yield from _pf(f"app_chrome.menu[{i}].label", entry.get("label"))

    for i, block in enumerate(_as_list(bp.get("blocks"))):
        if isinstance(block, dict):
            for key in ("name", "description"):
                yield from _pf(f"blocks[{i}].{key}", block.get(key))

    for i, entity in enumerate(_as_list(bp.get("entities"))):
        if not isinstance(entity, dict):
            continue
        for key in ("name", "type", "records"):
            yield from _pf(f"entities[{i}].{key}", entity.get(key))
        for j, attr in enumerate(_as_list(entity.get("attributes"))):
            if isinstance(attr, dict):
                for key in ("name", "data_type", "enum_values"):
                    yield from _pf(f"entities[{i}].attributes[{j}].{key}", attr.get(key))

    for i, screen in enumerate(_as_list(bp.get("screens"))):
        if not isinstance(screen, dict):
            continue
        for key in ("name", "display_name", "type", "description"):
            yield from _pf(f"screens[{i}].{key}", screen.get(key))
        # A render-gate label names a row and a selector is executed, so both
        # are gate-bearing in the strictest sense. `contains`/`equals`/`reason`
        # are NOT: they are literals copied from the UI or a statement about
        # it, and a screen that legitimately renders the word "TBD" must stay
        # assertable. The marker regex is also English-only by construction, so
        # scoping it here is the honest reach - it is not a defence against
        # placeholder CONTENT, which is what a `text` assertion is for.
        for j, entry in enumerate(_as_list(screen.get("render_gate"))):
            if isinstance(entry, dict):
                for key in ("label", "selector"):
                    yield from _pf(f"screens[{i}].render_gate[{j}].{key}", entry.get(key))
        for rpath, region in _regions(screen):
            for key in ("name", "id", "description", "content"):
                yield from _pf(f"screens[{i}].{rpath}.{key}", region.get(key))
            hints = region.get("outsystems_hints")
            if isinstance(hints, dict):
                yield from _pf(f"screens[{i}].{rpath}.outsystems_hints.block",
                               hints.get("block"))
            reuse = region.get("reuse")
            if isinstance(reuse, dict):
                yield from _pf(f"screens[{i}].{rpath}.reuse.block", reuse.get("block"))

    for i, icon in enumerate(_as_list(bp.get("icon_mapping"))):
        if isinstance(icon, dict):
            for key in ("role", "outsystems_icon"):
                yield from _pf(f"icon_mapping[{i}].{key}", icon.get(key))

    for i, role in enumerate(_as_list(bp.get("roles"))):
        if isinstance(role, dict):
            for key in ("name", "description"):
                yield from _pf(f"roles[{i}].{key}", role.get(key))


def _check_placeholders(bp, errors):
    """Fail-closed: an unresolved marker in a gate-bearing field is an error."""
    for path, text in placeholder_fields(bp):
        marker = placeholder_in(text)
        if marker:
            errors.append(
                f"{path}: active placeholder {marker!r} - a gate-bearing field "
                "must carry the real value, not a marker to resolve later"
            )


def _schema_branch_errors(node, schema, path):
    """A branch's own errors, collected without polluting the caller's list -
    `oneOf` needs to try a branch and discard it when another one matches."""
    found = []
    _check_schema(node, schema, path, found)
    return found


def _check_schema(node, schema, path, errors):
    # `oneOf` is the one combinator this projection uses (data_type: a closed
    # basic-type enum, OR a length-bearing Text, OR the relationship form). It
    # is checked before `type`, because the branches carry their own.
    if "oneOf" in schema:
        if any(not _schema_branch_errors(node, branch, path)
               for branch in schema["oneOf"]):
            return
        errors.append(
            f"{path}: value {node!r} matches none of the {len(schema['oneOf'])} "
            "permitted forms - see the field's schema description")
        return
    expected = schema.get("type")
    if expected and not isinstance(node, _expected_types(expected)):
        errors.append(f"{path}: expected {expected}, got {type(node).__name__}")
        return
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: value {node!r} not in {schema['enum']}")
    if "pattern" in schema:
        if not isinstance(node, str) or not re.search(schema["pattern"], node):
            errors.append(f"{path}: value {node!r} does not match "
                          f"{schema['pattern']!r}")
    if isinstance(node, dict):
        for req in schema.get("required", []):
            if req not in node:
                errors.append(f"{path}: missing required key '{req}'")
        for key, sub in schema.get("properties", {}).items():
            if key in node:
                _check_schema(node[key], sub, f"{path}.{key}", errors)
    if isinstance(node, list) and "items" in schema:
        for i, item in enumerate(node):
            _check_schema(item, schema["items"], f"{path}[{i}]", errors)


def _as_list(value):
    """Malformed input reports its own error from the schema check; here it must
    not crash. `.get(key, [])` is not enough: a key present and null returns
    None."""
    return value if isinstance(value, list) else []


def _as_dict(value):
    """The same for the object-valued sections. `.get(key, {})` and
    `(x.get(key) or {})` both still break on a key holding a NON-dict - `7` and
    `"x"` reach `.get` and raise - and the warning walkers read `app_chrome`,
    `target_context` and `outsystems_hints` before anything has checked them."""
    return value if isinstance(value, dict) else {}


def _hint_block(region):
    """The catalog block this region maps to, or None when it names none.

    `outsystems_hints` and its `block` are both UNTYPED: under `main_content[]`
    the schema types only `reuse` and `items`, so `_check_schema` clears a
    region holding `7` there and the early return in `collect_errors` never
    fires. Every walker below then reads the hint as if it had been checked.

    A non-string block reads as ABSENT rather than as a node to skip, and that
    is the load-bearing half. Skipping it would trade a traceback for a silent
    pass - the region would clear the Block Mapping Gate while mapping to
    nothing. Absent instead keeps the gate reporting it, which is what an
    unreadable hint deserves: a block is a NAME, and `7` is not one.
    """
    block = _as_dict(region.get("outsystems_hints")).get("block")
    return block if isinstance(block, str) else None


def _nominated_source(node):
    """`data_source.entity` as written, or None. `node` may be None: the group
    of an ungrouped region.

    Untyped for the same reason as the block hint, so this is the read every
    walker wants when it only formats the value into a message - it keeps the
    message naming what the author actually wrote.
    """
    return _as_dict(_as_dict(node).get("data_source")).get("entity")


def _source_entity(node):
    """The same value when it is a NAME, for the walkers that use it as one.

    `_datasource_entities` puts this in a set that is later `sorted()`, so a
    non-string is not merely unusable here - a list raises `unhashable type`
    and an int raises inside `sorted` against the strings beside it, in both
    cases before any finding is recorded. A value that is not a name is not
    an entity, so it drops out rather than propagating.
    """
    entity = _nominated_source(node)
    return entity if isinstance(entity, str) else None


_ELEMENT_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def _check_screen_name_is_element_name(bp, errors):
    """`screens[].name` is the ODC element name, never the human title.

    Every downstream consumer resolves a screen by matching this string against
    the built model's `Name` EXACTLY - outsystems-mentor-implementation's
    `recompute_assertions.py` (`_screen_id`), and the render-gate spec this
    validator emits, which carries the same string into `screens[].name` of the
    gate's own contract. Measured 2026-09-02 on restaurant-app-v3 rev 7:
    6 of 7 screens came back SCREEN_MISSING from a build that contained all
    seven, because the blueprints held display names ("A4 Print Preview") and
    the model holds element names (`A4PrintPreview`).

    The repair is here rather than in the matcher on Codex's recommendation
    (AH-2026-09-02-006): fuzzy matching would resolve `A4 Print Preview` and
    `A4PrintPreview` to the same screen and hide a genuine collision between
    two screens whose element names differ only by the characters it ignores.

    Runs AHEAD of the schema check, which short-circuits, for the same reason
    the identifier checks above do: the schema refuses the value with "does not
    match the pattern", which names the defect and not the repair. This says
    which field the title belongs in.
    """
    for i, screen in enumerate(_as_list(_as_dict(bp).get("screens"))):
        if not isinstance(screen, dict):
            continue
        name = screen.get("name")
        if not isinstance(name, str) or _ELEMENT_NAME_RE.match(name):
            continue
        suggested = re.sub(r"[^A-Za-z0-9_]", "", name)
        hint = (f" (element name: {suggested!r})"
                if _ELEMENT_NAME_RE.match(suggested) else "")
        errors.append(
            f"screens[{i}].name {name!r} is not an ODC element name - letters, "
            "digits and underscore only, first character a letter"
            f"{hint}. Downstream consumers match this string against the built "
            "model's screen Name exactly, so a display name here reports the "
            "screen as missing from a build that contains it. Put the human "
            "title in screens[].display_name"
        )


def _check_reserved_identifier_types(bp, errors):
    """The four `Identifier`-shaped strings that pass every gate and fail at
    publish. Two of them (`Integer Identifier`, `Text Identifier`) have exactly
    the shape of a legitimate `<Target> Identifier`, so the schema's pattern
    cannot tell them apart from a real relationship type - only a name can.

    Scoped to entity ATTRIBUTES, which is the path the rule was measured on: an
    `Identifier`-suffixed type on an action parameter publishes normally.

    Defensive on every node, because this runs BEFORE `_check_schema` and so
    sees unvalidated input (AH-2026-08-27-019, Codex). Note `.get(key, [])`
    returns None for a key that is PRESENT and null - the default only covers an
    absent key - so each list is type-checked rather than defaulted. Skip what
    cannot be read; never stop reading.
    """
    if not isinstance(bp, dict):
        return
    for entity in _as_list(bp.get("entities")):
        if not isinstance(entity, dict):
            continue
        for attribute in _as_list(entity.get("attributes")):
            if not isinstance(attribute, dict):
                continue
            value = attribute.get("data_type")
            if not isinstance(value, str) or value.strip() not in RESERVED_IDENTIFIER_TYPES:
                continue
            errors.append(
                f"entity '{entity.get('name', '?')}' attribute "
                f"'{attribute.get('name', '?')}': data_type {value.strip()!r} "
                "validates cleanly and then fails every publish "
                "(OS-RDBS-GEN-40002, masked as OS-DPL-50203). An ordinary "
                "auto-number primary key is the literal 'Long Integer'; a "
                "relationship is '<TargetEntity> Identifier'. A genuine 64-bit "
                "key requirement is a Mentor/publish-path limitation to raise "
                "in evidence_boundary.review_notes, never silently narrowed"
            )


def _iter_attributes(bp):
    """Every (entity, attribute) pair, defensively. Runs on UNVALIDATED input:
    skip what cannot be read, never stop reading."""
    if not isinstance(bp, dict):
        return
    for entity in _as_list(bp.get("entities")):
        if not isinstance(entity, dict):
            continue
        for attribute in _as_list(entity.get("attributes")):
            if isinstance(attribute, dict):
                yield entity, attribute


def _check_data_type_register(bp, errors):
    """One register. Ahead of the schema check for the same reason the reserved
    strings are: the schema now refuses a legacy spelling, and left downstream
    the reader would be told the string matches none of the permitted forms
    rather than which string to write instead.

    The identifier tokens are handled by _check_primary_key_data_type, which
    owns the whole class and gives it the primary-key diagnosis it needs.
    """
    for entity, attribute in _iter_attributes(bp):
        value = attribute.get("data_type")
        if not isinstance(value, str):
            continue
        value = value.strip()
        if value in LEGACY_IDENTIFIER_TOKENS:
            continue
        canonical = LEGACY_CAMEL_REGISTER.get(value)
        if canonical is None and _LEGACY_TEXT_LENGTH_RE.match(value):
            canonical = "T" + value[1:]
        if canonical is None:
            continue
        errors.append(
            f"entity '{entity.get('name', '?')}' attribute "
            f"'{attribute.get('name', '?')}': data_type {value!r} is the legacy "
            f"camelCase register - write {canonical!r}. The vocabulary carries "
            "one register, the ODC literal names, because that is what "
            "outsystems-mentor-implementation states and what is rendered "
            "verbatim into the Mentor prompt"
        )


PRIMARY_KEY_TYPE = "Long Integer"


def _check_primary_key_data_type(bp, errors):
    """A primary key is the literal `Long Integer`.

    Stated by OMI's contract and by SKILL.md, and enforced before this change by
    a single test asserting one string was absent from one fixture - which is
    exactly why `integerIdentifier`, the same forbidden class, sat unnoticed in
    OMI's own canonical asset. It is now a predicate over every attribute of
    every blueprint.

    The rule is stated for "an ordinary auto-number primary key", and the
    blueprint carries no auto-number flag, so it cannot narrow itself to that
    case. It does not need to. A static entity's key is the other case, and
    OMI's rule 6 gives it the same shape - an `Id` with `IsAutoNumber = No` and
    an explicit non-null integer, with the display value in a SEPARATE `Label`
    attribute - so a Text primary key is not the natural-key escape it looks
    like, it is a static entity modelled wrongly. Measured 2026-09-01: all 31
    primary keys in the live set are `Long Integer`, static and transaction
    alike, so the estate already writes one rule.

    A design that genuinely needs otherwise says so in
    `evidence_boundary.review_notes`, which is the same escape hatch the 64-bit
    key rule already uses - never a silently different type.
    """
    for entity, attribute in _iter_attributes(bp):
        value = attribute.get("data_type")
        if not isinstance(value, str):
            continue
        value = value.strip()
        where = (f"entity '{entity.get('name', '?')}' attribute "
                 f"'{attribute.get('name', '?')}'")
        if value in LEGACY_IDENTIFIER_TOKENS:
            errors.append(
                f"{where}: data_type {value!r} is a legacy spelling of an "
                f"auto-number primary key - write {PRIMARY_KEY_TYPE!r}. It is "
                "not a case variant of a permitted string: 'Long Integer "
                "Identifier' validates cleanly and then fails every publish "
                "(OS-RDBS-GEN-40002, masked as OS-DPL-50203)"
            )
        elif not attribute.get("is_primary_key"):
            continue
        elif _RELATIONSHIP_TYPE_RE.match(value):
            errors.append(
                f"{where}: data_type {value!r} is the relationship form, which "
                f"belongs on a foreign key. A primary key is the literal "
                f"{PRIMARY_KEY_TYPE!r}; an Identifier-suffixed type on a "
                "primary key fails at publish (OS-RDBS-GEN-40002, masked as "
                "OS-DPL-50203)"
            )
        elif value != PRIMARY_KEY_TYPE:
            errors.append(
                f"{where}: data_type {value!r} on a primary key - a primary key "
                f"is the literal {PRIMARY_KEY_TYPE!r}. An ordinary auto-number "
                "key is stated that way by OMI's contract, and a static "
                "entity's key is an `Id` with IsAutoNumber = No and an explicit "
                "integer, with the display value in a separate `Label` "
                "attribute - so a Text key is a static entity modelled wrongly, "
                "not a natural key. If this design genuinely needs another key "
                "type, say so in evidence_boundary.review_notes as a "
                "Mentor/publish-path limitation, never silently"
            )


def _check_single_layout(bp, errors):
    layout = bp.get("app_chrome", {}).get("layout_block")
    if layout not in LAYOUT_BLOCKS:
        errors.append(
            f"app_chrome.layout_block: {layout!r} must be exactly one of "
            f"{list(LAYOUT_BLOCKS)} - one layout block per screen, no combinations"
        )


def _check_region_shapes(bp, errors):
    """Guard against malformed region shapes before other invariants assume dicts."""
    for screen in bp.get("screens", []):
        screen_name = screen.get("name", "?")
        for region in screen.get("main_content", []):
            if not isinstance(region, dict):
                errors.append(
                    f"screen '{screen_name}': main_content item is not an object - "
                    "every region must be a JSON object"
                )
                continue
            if region.get("type") == "group":
                group_name = region.get("name", "?")
                for i, item in enumerate(region.get("items", [])):
                    if not isinstance(item, dict):
                        errors.append(
                            f"screen '{screen_name}' group '{group_name}': items[{i}] "
                            "is not an object - every region must be a JSON object"
                        )
                    elif item.get("type") == "group":
                        errors.append(
                            f"screen '{screen_name}' group '{group_name}': nested groups "
                            "are not part of the OMI contract - flatten to one group level"
                        )


def _leaf_regions(screen, with_group=False):
    # Reached from the WARNING walkers too, which run on input the schema check
    # has not cleared (see `_as_list`): skip what cannot be read, never stop
    # reading.
    if not isinstance(screen, dict):
        return
    for region in _as_list(screen.get("main_content")):
        if not isinstance(region, dict):
            continue
        if region.get("type") == "group":
            for item in _as_list(region.get("items")):
                if not isinstance(item, dict) or item.get("type") == "group":
                    continue
                yield (item, region, screen.get("name", "?")) if with_group \
                    else (item, screen.get("name", "?"))
        else:
            yield (region, None, screen.get("name", "?")) if with_group \
                else (region, screen.get("name", "?"))


def _reused_block(region):
    """The app-local block this region binds to, or None.

    Phase 1 trial F-02: `target_context.existing_assets` announces THAT the app
    has assets; `reuse` is what binds a region to one, so OMI is told what not
    to build instead of inferring it.
    """
    reuse = region.get("reuse")
    if not isinstance(reuse, dict):
        return None
    block = reuse.get("block")
    return block.strip() if isinstance(block, str) and block.strip() else None


def _existing_app_mode(bp):
    return bp.get("target_context", {}).get("target_mode") == "existing-app"


def _check_region_mapping(bp, errors):
    for screen in bp.get("screens", []):
        for region, screen_name in _leaf_regions(screen):
            block = _hint_block(region)
            if "reuse" in region:
                # Bound to an existing app block - that IS the mapping. A
                # malformed binding is reported once, by the reuse check.
                continue
            if not block and not region.get("custom_block_needed"):
                label = region.get("name") or region.get("id") or "?"
                errors.append(
                    f"screen '{screen_name}' region '{label}': no outsystems_hints.block "
                    "and not flagged custom_block_needed - every region must map to a "
                    "named OutSystems UI block or be explicitly flagged"
                )


_CONTAINER_RE = re.compile(r"\bContainer\b")


def _iter_strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _iter_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _iter_strings(value)


def _check_no_container(bp, errors):
    for screen in bp.get("screens", []):
        for region, screen_name in _leaf_regions(screen):
            probe = {
                "block": _hint_block(region) or "",
                "content": region.get("content", []),
            }
            for text in _iter_strings(probe):
                if _CONTAINER_RE.search(text):
                    label = region.get("name") or region.get("id") or "?"
                    errors.append(
                        f"screen '{screen_name}' region '{label}': 'Container' in "
                        f"{text!r} - no Container nodes in the skeleton; use "
                        "Columns*/Card family blocks"
                    )
                    break


_PAGINATION_WITH_REPEAT_RE = re.compile(
    r"\bPagination\b.*\b(" + "|".join(REPEAT_MARKERS) + r")\b|"
    r"\b(" + "|".join(REPEAT_MARKERS) + r")\b.*\bPagination\b"
)


_PLUS_JOINED_RE = re.compile(r"\bplus\b", re.IGNORECASE)
_BARE_BLOCK_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")


def _check_block_name_granularity(bp, errors):
    """Catch a block string standing in for several distinct widgets/regions.

    NOTE: `_check_block_name_bare` now requires every `block` value to be a
    single bare token, so any comma, space, or prose qualifier already fails
    that stricter gate. This granularity check remains as a more descriptive
    secondary signal (its message names the collapsing mistake specifically),
    and it still catches the semicolon / 2+ commas / Pagination-with-repeat
    shapes. Likewise, this skill's own evidence (Run A, Run B) always keeps
    Pagination as a sibling of its repeated-content block
    (TableRecords/Table/Gallery/...), never nested in the same block string -
    "Card with TableRecords and Pagination" is the same collapsing mistake
    even with only one "and" and no comma.

    'plus' is banned outright. It is a conjunction that joins two distinct
    block names ("Columns3 plus MetricCard web block") and never appears in a
    legitimate property qualifier - so unlike "and", it can be rejected with
    no false positives. Phase 3 GAP-3: this exact string shipped in the golden
    fixture, slipping past both the gate's wording and this check, while being
    the reference example operators copy from.
    """
    for screen in bp.get("screens", []):
        for region, screen_name in _leaf_regions(screen):
            block = _hint_block(region)
            if not block:
                continue
            if (
                ";" in block
                or block.count(",") >= 2
                or _PLUS_JOINED_RE.search(block)
                or _PAGINATION_WITH_REPEAT_RE.search(block)
            ):
                label = region.get("name") or region.get("id") or "?"
                errors.append(
                    f"screen '{screen_name}' region '{label}': outsystems_hints.block "
                    f"{block!r} looks like several widgets collapsed into one region - "
                    "split into sibling regions or a group's items[], one bare block "
                    "name per region"
                )


def _check_block_name_bare(bp, errors):
    """Reject block hints containing spaces or non-alphanumeric characters.

    A bare block name is a single token with no whitespace. Examples of valid
    names: Columns3, ColumnsMediumRight, Card, MetricCard. Examples of invalid
    names: "Card with UsePadding True" (prose), "Columns3 plus Card" (joined),
    "Card, Form" (comma-separated). Qualifiers belong in the section fields,
    not in the block name itself.
    """
    for screen in bp.get("screens", []):
        for region, sname in _leaf_regions(screen):
            block = _hint_block(region)
            if block and not _BARE_BLOCK_RE.match(block):
                label = region.get("name") or region.get("id") or "?"
                errors.append(
                    f"screen '{sname}' region '{label}': outsystems_hints.block "
                    f"{block!r} is not a bare block name - use a single catalog token "
                    "like 'Columns3' or 'ColumnsMediumRight'; put qualifiers in the "
                    "section fields, not the block name"
                )


# OMI's reference doc (odc-visual-source-ui-discipline.md) is explicit: "Use a
# bare Phosphor icon name for OutSystems UI Icon widgets, not `ph-*` or
# `ph ph-*` class syntax." OMI's own EXAMPLE ASSET violates this ("icon-home"),
# and this skill's golden fixture copied the error - so both conventions were
# in circulation and the schema (a bare string) waved both through.
# Phase 3 GAP-6: a wrong icon convention validated green and would have reached
# OMI unpatched. The schema is unchanged; this is a skill-side gate, like the
# Container and block-granularity checks above.
_ICON_CLASS_SYNTAX_RE = re.compile(r"^\s*(icon-|ph-|ph\s+ph-|fa-|fas\s|far\s)", re.IGNORECASE)


def _check_icon_convention(bp, errors):
    for i, entry in enumerate(bp.get("icon_mapping", [])):
        if not isinstance(entry, dict):
            continue
        icon = entry.get("outsystems_icon")
        if not isinstance(icon, str) or not icon.strip():
            continue
        if _ICON_CLASS_SYNTAX_RE.match(icon):
            role = entry.get("role", "?")
            errors.append(
                f"icon_mapping[{i}] (role {role!r}): outsystems_icon {icon!r} is CSS "
                "class syntax, not an icon name - OMI requires a bare Phosphor icon "
                "name (e.g. 'house', 'gear', 'magnifying-glass'), never 'icon-*', "
                "'ph-*' or 'ph ph-*'"
            )


_REPEAT_RE = re.compile(r"\b(" + "|".join(REPEAT_MARKERS) + r")\b")


def _check_product_vocabulary(bp, errors):
    """Hard gate: no O11-only widget name may reach an ODC build.

    The 2026-08-09 live run's most expensive failure mode was the builder
    faithfully constructing what the plan asked for, where the plan asked for
    the wrong product's widget. Validation passed, the build was wrong. This
    gate closes that: an O11-only name is an error, and the message names the
    ODC replacement so the fix is mechanical rather than a research task.

    Scanned in the same two places `_check_repeat_producer` scans - the block
    hint and the region's content descriptors - because that is where a widget
    name actually reaches OMI.
    """
    for screen in bp.get("screens", []):
        for region, screen_name in _leaf_regions(screen):
            texts = list(_iter_strings({
                "block": _hint_block(region) or "",
                "content": region.get("content", []),
            }))
            seen = []
            for text in texts:
                for match in _O11_ONLY_RE.findall(text):
                    if match not in seen:
                        seen.append(match)
            label = region.get("name") or region.get("id") or "?"
            for name in seen:
                errors.append(
                    f"screen '{screen_name}' region '{label}': {name!r} is an "
                    f"OutSystems 11 widget name and does not exist in ODC - use "
                    f"{O11_ONLY_BLOCKS[name]} instead"
                )


# The bare built-in `Dropdown` widget only. The word boundary already excludes
# `DropdownSearch` / `DropdownTags` / `DropdownServerSide_*`, which are blocks
# taking a single `OptionsList` and so have nothing to leave unstated.
_BARE_DROPDOWN_RE = re.compile(r"\bDropdown\b")


def _check_dropdown_option_expressions(bp, errors):
    """Hard gate 6, second half: a record-backed `Dropdown` must name the
    attribute its option labels come from.

    ODC's Dropdown needs four co-dependent expressions - `List`, `Labels`,
    `Values` and a type-matched `Variable` - and each one left unresolved
    surfaces as its own `Invalid Expression`. Naming the source entity settles
    `List` and `Values` (the value is the entity's identifier); only the label
    attribute is still unstated, so that is what this gate requires.

    Scope note: a Dropdown with no `data_source.entity` at all is the *first*
    half of gate 6 (option source missing). That stays prose-enforced - the
    static-option-list form is disclosed in free text, and no reliable
    mechanical read of it exists.
    """
    for screen in bp.get("screens", []):
        for region, group, screen_name in _leaf_regions(screen, with_group=True):
            entity = _nominated_source(region) or _nominated_source(group)
            if not entity:
                continue
            for item in _as_list(region.get("content")):
                if not isinstance(item, dict):
                    continue
                if not _BARE_DROPDOWN_RE.search(str(item.get("element", ""))):
                    continue
                if _as_dict(item.get("binds")).get("attribute"):
                    continue
                label = region.get("name") or region.get("id") or "?"
                errors.append(
                    f"screen '{screen_name}' region '{label}': Dropdown over "
                    f"{entity!r} names its option source but not its option "
                    "label - set binds.attribute to the attribute shown per "
                    "option. Dropdown needs List, Labels, Values and a "
                    "type-matched Variable; each one left unstated becomes its "
                    "own 'Invalid Expression'. Use DropdownSearch with an "
                    "OptionsList if a single option input suits better."
                )


def _check_repeat_producer(bp, errors):
    for screen in bp.get("screens", []):
        for region, group, screen_name in _leaf_regions(screen, with_group=True):
            texts = list(_iter_strings({
                "block": _hint_block(region) or "",
                "content": region.get("content", []),
            }))
            if not any(_REPEAT_RE.search(t) for t in texts):
                continue
            entity = _nominated_source(region) or _nominated_source(group)
            label = region.get("name") or region.get("id") or "?"
            if not entity:
                errors.append(
                    f"screen '{screen_name}' region '{label}': repeated content "
                    "(List/TableRecords/Table/Gallery/...) without a data producer - "
                    "set data_source.entity on the region or its group"
                )
            # A value that is not a name cannot be a DECLARED name, and is
            # reported as one rather than skipped - the author nominated a
            # producer, and naming what they wrote is the useful half. The
            # isinstance test is also what stops `in` raising on a list.
            elif not isinstance(entity, str) or entity not in _declared_entities(bp):
                errors.append(
                    f"screen '{screen_name}' region '{label}': data_source.entity "
                    f"{entity!r} is not a declared entity"
                )


def _declared_entities(bp):
    """entity name -> {attribute name -> attribute object}.

    Also read by the warning path on UNVALIDATED input. Names are restricted to
    strings rather than taken as-is: the schema requires `name` on both levels
    and types it `string`, so nothing post-schema changes, and a name holding a
    list would otherwise raise `unhashable type` as a dict key.
    """
    out = {}
    if not isinstance(bp, dict):
        return out
    for ent in _as_list(bp.get("entities")):
        if not isinstance(ent, dict):
            continue
        attrs = {}
        for a in _as_list(ent.get("attributes")):
            if isinstance(a, dict) and isinstance(a.get("name"), str):
                attrs[a["name"]] = a
        name = ent.get("name")
        out[name if isinstance(name, str) else None] = attrs
    return out


def _iter_binds(bp):
    """Yield (screen_name, element, binds) for every content item carrying binds.

    `element` is normalised to a string because both warning walkers match it
    with a regex; the schema types it `string`, so no post-schema text moves.
    """
    if not isinstance(bp, dict):
        return
    for screen in _as_list(bp.get("screens")):
        if not isinstance(screen, dict):
            continue
        sname = screen.get("name", "?")
        for region, _sn in _leaf_regions(screen):
            for item in _as_list(region.get("content")):
                if isinstance(item, dict) and isinstance(item.get("binds"), dict):
                    element = item.get("element", "")
                    yield sname, element if isinstance(element, str) else "", item["binds"]


def _check_binding_existence(bp, errors):
    declared = _declared_entities(bp)
    for sname, _element, binds in _iter_binds(bp):
        ent = binds.get("entity")
        attr = binds.get("attribute")
        # `binds` is untyped, and both names are dict KEYS below - a list raises
        # `unhashable type` before either error is recorded. A non-string name
        # is not a declared name, so it falls to the same error rather than
        # being skipped: the reader still learns which binding is wrong.
        if not isinstance(ent, str) or ent not in declared:
            errors.append(
                f"screen '{sname}': binds.entity {ent!r} is not a declared entity"
            )
        elif not isinstance(attr, str) or attr not in declared[ent]:
            errors.append(
                f"screen '{sname}': binds.attribute {attr!r} does not exist on entity "
                f"{ent!r} (declared: {sorted(declared[ent])})"
            )


def _check_binding_type_fit(bp, warnings):
    declared = _declared_entities(bp)
    for sname, element, binds in _iter_binds(bp):
        # Both are dict KEYS below, and the schema types them `string`; an
        # unvalidated blueprint can put a list there and raise `unhashable
        # type` before any finding is recorded.
        if not (isinstance(binds.get("entity"), str)
                and isinstance(binds.get("attribute"), str)):
            continue
        attr = declared.get(binds.get("entity"), {}).get(binds.get("attribute"))
        if not attr:
            continue  # existence gate already errors
        if _NUMERIC_WIDGET_RE.search(element) and attr.get("data_type") not in NUMERIC_TYPES:
            warnings.append(Finding(
                f"screen '{sname}': {element} binds to "
                f"{binds['entity']}.{binds['attribute']} (data_type "
                f"{attr.get('data_type')!r}), which is not numeric - a "
                "ProgressBar/Counter expects a numeric attribute",
                # Decided by a widget-NAME regex, and a Text attribute holding a
                # number is a modelling choice rather than a contract breach.
                graduating=False,
            ))
        if _STATUS_WIDGET_RE.search(element) and not (
            attr.get("is_foreign_key") and attr.get("enum_values")
        ):
            warnings.append(Finding(
                f"screen '{sname}': {element} binds to "
                f"{binds['entity']}.{binds['attribute']}, which is not backed by a "
                "static entity - a status Tag/Badge expects a static-entity-backed "
                "attribute",
                # Same name-regex heuristic: a Badge showing a count is a
                # legitimate final state, so this advises rather than blocks.
                graduating=False,
            ))


_ASSERTION_WIDGETS = {"links": "Link", "buttons": "Button", "inputs": "Input"}


def _derive_counts(screen):
    counts = {k: 0 for k in _ASSERTION_WIDGETS}
    for region, _sn in _leaf_regions(screen):
        for item in _as_list(region.get("content")):
            if not isinstance(item, dict):
                continue
            element = item.get("element", "")
            # `element` is untyped too, and these are regex operands.
            if not isinstance(element, str):
                continue
            for key, word in _ASSERTION_WIDGETS.items():
                if re.search(rf"\b{word}\b", element):
                    counts[key] += 1
    return counts


# Q3b (approved 2026-08-30): the two region classes that shipped MISSING on
# restaurant-app-v2 (2026-08-28/29) - the filter tabs and the empty states - did
# so undetected because the screens declared no `assertions`, leaving OMI's
# post-publish recompute with no contract to check. A screen declaring either
# class must therefore declare assertions; they stop being optional for exactly
# the regions that went missing.
#
# The trigger is the region's declared BLOCK token, never its prose: the region
# names on that app were Portuguese ("Filtro por seccao"), and a keyword rule in
# one language is not a rule. This is a separate mechanism from the counts and
# does not touch `_ASSERTION_WIDGETS`.
_ASSERTION_REQUIRED_BLOCKS = {"Tabs", "ButtonGroup", "BlankSlate", "EmptyState"}


def _assertion_forcing_blocks(screen):
    found = []
    for region, _sn in _leaf_regions(screen):
        # `or {}` covers a MISSING key, not one holding a non-dict, and both
        # are untyped under `main_content[]` (see `_hint_block`).
        hints = _as_dict(region.get("outsystems_hints"))
        reuse = _as_dict(region.get("reuse"))
        # `reuse` first - the SHARED precedence with OMI's region diff
        # (check_control_wiring.py). Reading the hint first let a region
        # carrying both be matched there as Tabs while evading this control
        # (Codex correction 1, AH-2026-08-30-007 round 1).
        block = reuse.get("block") or hints.get("block")
        if not isinstance(block, str):
            continue
        token = block.split("/")[-1].strip()
        if token in _ASSERTION_REQUIRED_BLOCKS:
            found.append((region.get("name", region.get("id", "?")), token))
    return found


def _check_assertions_required_for_filter_and_empty_state(bp, errors):
    for screen in bp.get("screens", []):
        if not isinstance(screen, dict):
            continue
        forcing = _assertion_forcing_blocks(screen)
        if not forcing:
            continue
        assertions = screen.get("assertions")
        if isinstance(assertions, dict) and assertions:
            continue
        sname = screen.get("name", "?")
        named = ", ".join(f"'{n}' ({b})" for n, b in forcing)
        errors.append(
            f"screen '{sname}': region(s) {named} declare a filter or "
            "empty-state block, so this screen's `assertions` are REQUIRED, not "
            "optional - without them OMI's post-publish recompute reports "
            "'no screen declares assertions - nothing was checked', which is how "
            "two screens shipped with these exact regions missing "
            "(restaurant-app-v2, 2026-08-28)"
        )


def _check_assertion_parity(bp, errors):
    for screen in bp.get("screens", []):
        assertions = screen.get("assertions")
        if not isinstance(assertions, dict):
            continue
        derived = _derive_counts(screen)
        sname = screen.get("name", "?")
        for key, claimed in assertions.items():
            if key not in _ASSERTION_WIDGETS:
                errors.append(
                    f"screen '{sname}': assertions.{key} is not a supported "
                    f"assertion ({', '.join(sorted(_ASSERTION_WIDGETS))}) - an "
                    "unknown key would sail through here and then fail as "
                    "UNSUPPORTED at the step-7 recompute; the vocabulary is "
                    "shared and enforced on both ends"
                )
            elif claimed != derived[key]:
                errors.append(
                    f"screen '{sname}': assertions.{key} claims {claimed} but "
                    f"main_content has {derived[key]} - a self-reported count must "
                    "match main_content (main_content is the source of truth)"
                )


def _check_enum_on_non_fk(bp, errors):
    for ent in bp.get("entities", []):
        if not isinstance(ent, dict):
            continue
        ename = ent.get("name", "?")
        for a in ent.get("attributes", []):
            if not isinstance(a, dict):
                continue
            if a.get("enum_values") and not a.get("is_foreign_key"):
                errors.append(
                    f"entity '{ename}' attribute '{a.get('name')}' carries enum_values "
                    "but is_foreign_key is false - enum_values is only valid on a "
                    "foreign-key attribute (it defines the referenced Static Entity's "
                    "records)"
                )


def _existing_entities(bp):
    """Entity names flagged `exists: true` - already in the target app.

    String names only. Both callers `sorted()` this set, and a set mixing None
    with strings raises before either can report anything; the schema types
    `name` `string`, so no post-schema name is dropped.
    """
    return {e.get("name") for e in _as_list(_as_dict(bp).get("entities"))
            if isinstance(e, dict) and e.get("exists") is True
            and isinstance(e.get("name"), str)}


def _check_existing_asset_channel(bp, errors):
    """F-02/F-05: the existing-asset bindings are only coherent on an existing app.

    A region that reuses an app-local block, or an entity flagged as already
    existing, contradicts a greenfield/shell-first target: there is no app yet
    for the asset to exist in.
    """
    mode = bp.get("target_context", {}).get("target_mode")
    for screen in bp.get("screens", []):
        for region, sname in _leaf_regions(screen):
            if "reuse" not in region:
                continue
            label = region.get("name") or region.get("id") or "?"
            block = _reused_block(region)
            if not block:
                errors.append(
                    f"screen '{sname}' region '{label}': reuse is declared without a "
                    "usable reuse.block name - name the existing app block (it may be "
                    "flow-qualified, e.g. 'MainFlow/RecentQueriesPanel')"
                )
            elif not _existing_app_mode(bp):
                errors.append(
                    f"screen '{sname}' region '{label}': reuse.block {block!r} binds an "
                    f"app block that already exists, but target_mode is {mode!r} - the "
                    "existing-asset channel is valid only under 'existing-app'"
                )
            elif _hint_block(region) or region.get("custom_block_needed"):
                errors.append(
                    f"screen '{sname}' region '{label}': reuse.block {block!r} coexists "
                    "with outsystems_hints.block or custom_block_needed - reuse satisfies "
                    "the mapping on its own; a region binds to an existing block OR "
                    "describes one to build, never both"
                )
    if not _existing_app_mode(bp):
        for name in sorted(n for n in _existing_entities(bp) if n):
            errors.append(
                f"entity '{name}' is flagged exists: true, but target_mode is {mode!r} "
                "- the existing-asset channel is valid only under 'existing-app'"
            )


def _check_create_attribute_channel(bp, errors):
    """F1 (AH-2026-09-02-003 designtomodel-disposition proposal 3.1): an attribute
    of an `exists: true` entity may carry `create: true` to say it is to be ADDED
    to the existing entity. `create` on an entity without `exists: true` is an
    error - a created entity creates all of its attributes already."""
    existing = _existing_entities(bp)
    for ent in _as_list(_as_dict(bp).get("entities")):
        if not isinstance(ent, dict):
            continue
        ename = ent.get("name")
        if ename in existing:
            continue
        for a in _as_list(ent.get("attributes")):
            if isinstance(a, dict) and a.get("create") is True:
                errors.append(
                    f"entity '{ename}' attribute '{a.get('name')}' carries "
                    "create: true, but the entity is not flagged exists: true "
                    "- create is only valid on an attribute of an existing "
                    "entity (a created entity creates all of its attributes "
                    "already)"
                )


def _check_existing_asset_announcement(bp, warnings):
    """Advisory: a bound asset should also be announced in existing_assets, so
    the target boundary stays readable without walking every region."""
    declared = _as_list(_as_dict(_as_dict(bp).get("target_context")).get("existing_assets"))
    known = set()
    for entry in declared:
        if isinstance(entry, str) and entry.strip():
            text = entry.strip()
            known.add(text)
            known.add(text.rsplit("/", 1)[-1])
            # Greenfield trial G-06: an annotated entry ("QueryHistory
            # (entity) - EXISTS; ...") names its asset in its leading token;
            # exact-string matching forced a bare-name duplicate sibling.
            # Match the word-bounded leading name - and only that, so a name
            # mentioned mid-annotation about another asset does not count.
            lead = re.match(
                r"[A-Za-z_][A-Za-z0-9_]*(?:/[A-Za-z_][A-Za-z0-9_]*)*", text)
            if lead:
                known.add(lead.group(0))
                known.add(lead.group(0).rsplit("/", 1)[-1])
    bound = []
    for screen in _as_list(_as_dict(bp).get("screens")):
        for region, _sn in _leaf_regions(screen):
            block = _reused_block(region)
            if block:
                bound.append(("reused block", block))
    bound.extend(("existing entity", n)
                 for n in sorted(n for n in _existing_entities(bp) if n))
    for kind, name in bound:
        if name not in known and name.rsplit("/", 1)[-1] not in known:
            warnings.append(Finding(
                f"{kind} {name!r} is bound in the blueprint but not named in "
                "target_context.existing_assets - announce it there too",
                # Blocks at handoff: plain set membership over names the
                # blueprint already carries, and naming the asset always clears
                # it. The target boundary is what OMI reads on intake.
                graduating=True,
            ))


def _datasource_entities(bp):
    names = set()
    for screen in bp.get("screens", []):
        for region, group, _sn in _leaf_regions(screen, with_group=True):
            for holder in (region, group):
                ent = _source_entity(holder)
                if ent:
                    names.add(ent)
    return names


def _fk_enum_targets(bp):
    """Entity names that some FK attribute (with enum_values) points at, via
    a '<Target> Identifier' data_type - the only contract-valid record seed."""
    targets = set()
    for ent in bp.get("entities", []):
        if not isinstance(ent, dict):
            continue
        for a in ent.get("attributes", []):
            if isinstance(a, dict) and a.get("is_foreign_key") and a.get("enum_values"):
                dt = a.get("data_type") or ""
                if dt.endswith(" Identifier"):
                    targets.add(dt[: -len(" Identifier")])
    return targets


def _records_targets(bp):
    """Entity names declared with a non-empty design-time `records` list -
    the standalone-static record intake (F-A Option A, OMI rule 6)."""
    return {e.get("name") for e in bp.get("entities", [])
            if isinstance(e, dict) and isinstance(e.get("records"), list)
            and e.get("records")}


def _check_records_on_non_static(bp, errors):
    """F-B3: `records` are design-time rows and only mean something on a
    static entity - on any other entity type they are a contract error."""
    for ent in bp.get("entities", []):
        if not isinstance(ent, dict) or "records" not in ent:
            continue
        etype = str(ent.get("type") or "")
        if "static" not in etype.lower():
            errors.append(
                f"entity '{ent.get('name', '?')}' declares records but its type is "
                f"{etype!r} - records are design-time rows and only valid on a "
                "static entity (a normal entity is runtime-populated)"
            )


def _fk_enum_seed_lists(bp):
    """(target_entity, via, ordered_list) for every FK attribute carrying
    non-empty enum_values onto a '<Target> Identifier' data_type."""
    out = []
    for ent in bp.get("entities", []):
        if not isinstance(ent, dict):
            continue
        for a in ent.get("attributes", []):
            if isinstance(a, dict) and a.get("is_foreign_key") and a.get("enum_values"):
                dt = a.get("data_type") or ""
                if dt.endswith(" Identifier"):
                    out.append((dt[: -len(" Identifier")],
                                f"{ent.get('name', '?')}.{a.get('name', '?')}",
                                list(a["enum_values"])))
    return out


def _check_dual_seed_mismatch(bp, errors):
    """OMI rule 6 alignment: when a static entity declares records AND an
    incoming FK's enum_values seeds it, identical ordered lists seed once;
    differing lists are a contradictory dual seed OMI stops on."""
    recs = {e.get("name"): list(e["records"]) for e in bp.get("entities", [])
            if isinstance(e, dict) and isinstance(e.get("records"), list)
            and e.get("records")}
    for target, via, lst in _fk_enum_seed_lists(bp):
        if target in recs and recs[target] != lst:
            errors.append(
                f"entity '{target}' declares records {recs[target]} but incoming "
                f"foreign key '{via}' carries enum_values {lst} - contradictory "
                "dual seed; OMI seeds once only when the ordered lists are "
                "identical (make them match or drop one seed)"
            )


# `<X> Identifier` types the platform supplies rather than the app declaring
# them. `User Identifier` is listed outright in the Mentor Web data type
# reference and ODC wires the relationship to its own `User` entity from the
# type alone (docs-odc building-apps/data/modeling/relationship/
# relationship-one-to-one.md); `Role Identifier` is the same shape (docs-odc
# reference/built-in-functions/roles.md). ODC's workflow system entities are
# deliberately absent: the platform publishes no `<X> Identifier` type for them,
# and an app that binds one adds it as a public element - which belongs in
# entities[] flagged exists: true, a route this check already accepts.
PLATFORM_IDENTIFIER_TARGETS = frozenset({"User", "Role"})


def declared_entity_names(bp):
    """Entity names this blueprint's entities[] declares, whatever their type.

    Public because multi-path mode unions it across the design directory: N
    per-screen blueprints are one app, and OMI merges their entity sets into one
    data model on intake.
    """
    return {e.get("name") for e in bp.get("entities", []) if isinstance(e, dict)}


def _check_fk_target_declared(bp, errors, extra_declared=None):
    """Producer-side half of OMI's Typed Create-Only rule 5: "When `enum_values`
    is `null`, require the target to be another declared create-only entity."

    OMI's sub-schema closes with "Do not invent a missing target entity ... stop
    prompt emission and return the blueprint for correction", and mandates a
    matching producer-side gate for a sub-schema contradiction before producer
    and consumer count as aligned - the same pairing the dual-seed rule has.
    Until this check existed a foreign key typed '<Target> Identifier' whose
    target appeared in no entities[] entry and was seeded by no enum_values
    validated clean, and OMI's build brief then instructed Mentor to create the
    relationship to an entity nothing in the pipeline asks to be created.

    extra_declared (multi-path only): entity names a SIBLING blueprint of the
    same design directory declares, so the guard does not false-error on a
    legitimate cross-blueprint projection - the same allowance F-B2 makes for a
    seed that lives in a sibling.

    `target_context.existing_assets` is deliberately NOT a declaration route: it
    announces THAT the app has assets, while the declared, explicit way to bind
    one is an entities[] entry flagged `exists: true`. Prose-matching it would
    also re-open the false negative the announcement check had to solve - 'User'
    is a substring of the routinely announced 'UserProfile'.
    """
    declared = declared_entity_names(bp) | set(extra_declared or ())
    seeded = {t.strip() for t in _fk_enum_targets(bp)}
    for ent in bp.get("entities", []):
        if not isinstance(ent, dict):
            continue
        for a in ent.get("attributes", []) or []:
            if not isinstance(a, dict) or not a.get("is_foreign_key"):
                continue
            dt = (a.get("data_type") or "").strip()
            if not dt.endswith(" Identifier"):
                continue
            target = dt[: -len(" Identifier")].strip()
            if not target or target in declared or target in seeded \
                    or target in PLATFORM_IDENTIFIER_TARGETS:
                continue
            errors.append(
                f"entity '{ent.get('name', '?')}' attribute '{a.get('name', '?')}' "
                f"is a foreign key to '{target}' via data_type {dt!r}, but "
                f"'{target}' is declared nowhere - declare it in entities[] (flag "
                "exists: true if it already exists in the target app), or seed it "
                "as a static entity by putting its records in this attribute's "
                "enum_values; OMI must not invent a missing target entity"
            )


def _check_static_datasource_unpopulated(bp, errors, extra_targets=None):
    types = {e.get("name"): (e.get("type") or "") for e in bp.get("entities", [])
             if isinstance(e, dict)}
    used = _datasource_entities(bp)
    # A static entity is populable if THIS blueprint seeds it - via an incoming
    # FK+enum or its own declared records - or (multi-path mode) if a SIBLING
    # blueprint does; extra_targets carries the union of the other blueprints'
    # seed targets (FK-enum + declared records).
    # An entity flagged `exists: true` is already populated in the target app -
    # demanding a seed path would force the producer to re-declare rows it has.
    seeded = (_fk_enum_targets(bp) | _records_targets(bp) | _existing_entities(bp)
              | (extra_targets or set()))
    for name in sorted(used):
        if "static" in str(types.get(name, "")).lower() and name not in seeded:
            errors.append(
                f"entity '{name}' (static) is used as a data_source but has no "
                "populable record path - it declares no records and no incoming "
                "foreign key with enum_values seeds it; OMI cannot populate it "
                "(declare its rows in the entity's records array, or seed it via "
                "an incoming FK+enum_values, or model it as a normal entity)"
            )


def _check_repeat_prose_columns(bp, warnings):
    for screen in _as_list(_as_dict(bp).get("screens")):
        if not isinstance(screen, dict):
            continue
        sname = screen.get("name", "?")
        for region, group, _sn in _leaf_regions(screen, with_group=True):
            own = _as_dict(region.get("data_source"))
            grp = _as_dict(_as_dict(group).get("data_source"))
            entity = own.get("entity") or grp.get("entity")
            if not entity:
                continue
            for item in _as_list(region.get("content")):
                if not isinstance(item, dict):
                    continue
                element = item.get("element", "")
                if not isinstance(element, str):
                    continue
                if _REPEAT_RE.search(element) and not isinstance(item.get("binds"), dict):
                    label = region.get("name") or region.get("id") or "?"
                    warnings.append(Finding(
                        f"screen '{sname}' region '{label}': repeat widget "
                        f"'{element}' over '{entity}' has no structured binds - its "
                        f"columns are prose-only and cannot be verified against "
                        f"'{entity}'s attributes",
                        # Blocks at handoff, which is what SKILL.md already
                        # says of it: "worth fixing before handoff". Adding
                        # binds always clears it.
                        graduating=True,
                    ))


# --- render-gate assertions -------------------------------------------------
#
# The measured failure (restaurant-app-v2, 2026-08-28): the blueprint's loudest
# disclosure - the dispatch screen must show the payload each channel will
# actually receive, BR-SC-006 "show exactly what each channel will receive" -
# shipped unmet, with the channel cards rendering placeholder descriptions. It
# had been written down twice, in review_notes and in acceptance_checklist, and
# neither channel carries authority: the checklist says so in its own schema
# description. A disclosure that reads like coverage and discharges nothing is
# worse than silence, because it stops anyone looking.
#
# Everything below is keyed on STRUCTURE and on requirement-id tokens, never on
# a phrase. The blueprint that motivated this is written in European
# Portuguese ("Os quatro canais mostram... o payload exato que receberiam
# (BR-SC-006)."), so an English-wording trigger would have fired on nothing.

# `[render-gate: <label>]` or `[no-runtime-claim]`, exactly.
_RG_MARKER_RE = re.compile(r"\[render-gate:\s*([^\]]+?)\s*\]")
_RG_NO_CLAIM_RE = re.compile(r"\[no-runtime-claim\]")
# Anything that was TRYING to be one of the two. A near-miss must never be
# quieter than a miss: `[render gate: X]` is invisible prose otherwise, and the
# author believes they wrote a link.
#
# Both patterns are deliberately narrow, because the words themselves are
# ordinary. A review note reading "the render gate never clicks" is correct
# prose and must not be a contract error, so only two shapes count: something
# BRACKETED that was reaching for a marker, and a line that OPENS with the
# token, which is an assertion written where prose goes.
_RG_MALFORMED_MARKER_RE = re.compile(
    r"\[[^\]]*(?:render[\s\-_]?gate|no[\s\-_]?runtime[\s\-_]?claim)[^\]]*\]",
    re.IGNORECASE)
_RG_PROSE_ASSERTION_RE = re.compile(r"^\s*[-*]?\s*render[\s\-_]?gate\b", re.IGNORECASE)

# A requirement id as the PRD assigns them: LETTER segments and a 2-4 digit
# tail. This rule blocks at handoff, so a false positive is expensive - and
# plenty of ordinary prose has the shape. Two extra conditions do the work of a
# deny-list, without a list to maintain:
#   - every letter segment is letters ONLY, so `A4-PDF-300` is not an id;
#   - the id has TWO letter segments (BR-SC-006) or a zero-padded tail
#     (UC-005, C-016, BR-001), so `AH-2026`, `SLA-99` and `ISO-8601` are not.
# A 5-digit tail is excluded by the pattern, which is what keeps the ODC error
# codes (`OS-CLRT-00000`) out. KNOWN MISS, stated: an unpadded single-segment id
# such as `US-9` is not detected - the workspace's PRDs zero-pad, and widening
# the rule to catch it would readmit every version and ratio in the prose.
_REQ_ID_RE = re.compile(r"\b([A-Z]{1,6})((?:-[A-Z]{1,6}){0,2})-(\d{2,4})\b")


def _is_requirement_id(match):
    _first, middle, tail = match.groups()
    return bool(middle) or tail.startswith("0")

# The three channels a disclosure is written to. `grounding_notes` is in the
# list because SKILL.md routes the EXTRAPOLATED disclosure there - the screen
# whose runtime behaviour is least evidenced is exactly the one that must not
# be exempt.
DISCLOSURE_CHANNELS = (
    ("evidence_boundary", "review_notes"),
    ("evidence_boundary", "grounding_notes"),
    ("target_context", "review_notes"),
)

_RG_ASSERTS = ("widget", "populated", "text", "known-unverified")
RENDER_GATE_MIN_REASON = 20


def _nfc(text):
    """NFC, so a name typed NFD and stored NFC is not two different names.

    macOS hands NFD strings out of filenames and some paste paths, and every
    join below is a raw `==`. Two visually identical names that do not compare
    equal produce a diagnosis pointing at nothing.
    """
    import unicodedata
    return unicodedata.normalize("NFC", text) if isinstance(text, str) else text


def _render_gate_entries(bp):
    """(screen_index, screen_name, entry_index, entry) for every declared entry."""
    for si, screen in enumerate(_as_list(_as_dict(bp).get("screens"))):
        if not isinstance(screen, dict):
            continue
        for ei, entry in enumerate(_as_list(screen.get("render_gate"))):
            if isinstance(entry, dict):
                yield si, screen.get("name", "?"), ei, entry


def _render_gate_labels(bp):
    return {_nfc(e.get("label")) for _si, _sn, _ei, e in _render_gate_entries(bp)
            if isinstance(e.get("label"), str)}


def _disclosure_lines(bp):
    """(path, text) for every disclosure line, in emission order."""
    for section, key in DISCLOSURE_CHANNELS:
        holder = _as_dict(bp).get(section)
        if not isinstance(holder, dict):
            continue
        for i, line in enumerate(_as_list(holder.get(key))):
            if isinstance(line, str):
                yield f"{section}.{key}[{i}]", line


def _declared_tokens(bp):
    """Every name the blueprint itself declares, for anchoring a stated gap.

    A length floor is the weakest content test there is, and weaker still in a
    language whose filler happens to be long. Requiring the reason to name
    something the blueprint declares forces it to be concrete, in any language.

    What the anchor buys, stated exactly: the reason names SOMETHING this
    blueprint declares. It cannot show that the thing named is the thing left
    uncovered - a reason mentioning an incidental entity clears it. The claim
    is worth making anyway, because it rejects the bare "not checkable here"
    that a length floor accepts, and a reviewer reads the rest.

    Region `id` is deliberately NOT a token, and nothing under three characters
    is: the shipped fixtures number their regions "1", "2", "2a", so admitting
    them would let any reason containing a digit clear the anchor - a check that
    passes on everything is not a check.
    """
    tokens = set()
    for screen in _as_list(bp.get("screens")):
        if not isinstance(screen, dict):
            continue
        if isinstance(screen.get("name"), str):
            tokens.add(_nfc(screen["name"]))
        for region, _g, _sn in _leaf_regions(screen, with_group=True):
            if isinstance(region.get("name"), str):
                tokens.add(_nfc(region["name"]))
        for region in _as_list(screen.get("main_content")):
            if isinstance(region, dict) and isinstance(region.get("name"), str):
                tokens.add(_nfc(region["name"]))
    for entity in _as_list(bp.get("entities")):
        if isinstance(entity, dict) and isinstance(entity.get("name"), str):
            tokens.add(_nfc(entity["name"]))
            for attr in _as_list(entity.get("attributes")):
                if isinstance(attr, dict) and isinstance(attr.get("name"), str):
                    tokens.add(_nfc(attr["name"]))
    for block in _as_list(bp.get("blocks")):
        if isinstance(block, dict) and isinstance(block.get("name"), str):
            tokens.add(_nfc(block["name"]))
    tokens |= cited_requirement_ids(bp)
    return {t for t in tokens if t and len(t) >= 3}


def cited_requirement_ids(bp):
    """Requirement ids the blueprint itself cites, from every prose channel."""
    found = set()
    sources = [line for _p, line in _disclosure_lines(bp)]
    sources += [s for s in _as_list(_as_dict(bp).get("acceptance_checklist"))
                if isinstance(s, str)]
    for line in sources:
        for match in _REQ_ID_RE.finditer(line):
            if _is_requirement_id(match):
                found.add(match.group(0))
    return found


def _check_render_gate_shape(bp, errors):
    """The assertion contract the schema cannot express: which companion field
    each `assert` needs, and which it must not carry."""
    seen = {}
    for _si, sname, ei, entry in _render_gate_entries(bp):
        at = f"screen '{sname}' render_gate[{ei}]"
        label = entry.get("label")
        if not isinstance(label, str) or not label.strip():
            errors.append(f"{at}: label must be a non-empty string - it names the gate row")
            continue
        key = _nfc(label)
        if key in seen:
            errors.append(
                f"{at}: duplicate label {label!r} (also on screen '{seen[key]}') - a "
                "disclosure references an assertion by this name alone, so a repeat "
                "makes the reference ambiguous")
        seen[key] = sname
        kind = entry.get("assert")
        if kind not in _RG_ASSERTS:
            errors.append(
                f"{at}: assert must be one of {', '.join(_RG_ASSERTS)}, not {kind!r}")
            continue
        selector = entry.get("selector")
        if kind == "known-unverified":
            for banned in ("selector", "contains", "equals"):
                if entry.get(banned) is not None:
                    errors.append(
                        f"{at}: a known-unverified entry declares that NO assertion is "
                        f"derivable, so it carries no {banned}")
            reason = entry.get("reason")
            if not isinstance(reason, str) or len(reason.strip()) < RENDER_GATE_MIN_REASON:
                errors.append(
                    f"{at}: known-unverified needs a reason of at least "
                    f"{RENDER_GATE_MIN_REASON} characters - a coverage hole is stated, "
                    "never abbreviated")
            else:
                # The entry's OWN screen is excluded: naming the screen you are
                # already on is free, and "not checkable on this screen" is
                # precisely the sentence the anchor exists to reject.
                anchors = _declared_tokens(bp) - {_nfc(sname)}
                if not any(tok and tok in _nfc(reason) for tok in anchors):
                    errors.append(
                        f"{at}: the reason names nothing this blueprint declares. State "
                        "which requirement id, region or entity is left uncovered - a "
                        "length floor accepts filler in any language, an anchor does not")
            _check_discharges_shape(bp, entry, kind, selector, at, errors)
            continue
        if entry.get("reason") is not None:
            errors.append(f"{at}: reason belongs to a known-unverified entry only")
        if not isinstance(selector, str):
            errors.append(
                f"{at}: {kind} needs a selector (an empty string is the honest "
                "'no confident selector' - the gate records that screenshot-only)")
        has_contains = entry.get("contains") is not None
        has_equals = entry.get("equals") is not None
        if kind == "text":
            if has_contains == has_equals:
                errors.append(
                    f"{at}: a text assertion needs exactly one of contains or equals - "
                    + ("both were given" if has_contains else "neither was given"))
            else:
                expected = entry.get("contains") if has_contains else entry.get("equals")
                if not isinstance(expected, str) or not expected.strip():
                    errors.append(
                        f"{at}: {'contains' if has_contains else 'equals'} must be a "
                        "non-empty string")
        elif has_contains or has_equals:
            errors.append(
                f"{at}: contains/equals belong to a text assertion - "
                f"{kind!r} asserts presence, not content")
        _check_discharges_shape(bp, entry, kind, selector, at, errors)


def _check_discharges_shape(bp, entry, kind, selector, at, errors):
    """What an entry is allowed to CLAIM it answers.

    Three constraints, each closing a measured way to make eleven requirements
    look answered by one trivially-true assertion (reproduced on the real
    restaurant-app-v2 dispatch blueprint: one `widget` on `body` carrying all
    eleven cited ids validated clean, with zero warnings).

    Stated limit, because a guarantee this rule does NOT provide is worse than
    a limit it admits: nothing here can judge whether a selector names the
    thing the requirement is about. These make the claim cheap to AUDIT - one
    id per element, one id per presence check, and no claim at all from an
    entry the gate will record `unasserted`. A reviewer still reads them.
    """
    names = _as_list(entry.get("discharges"))
    if not names:
        return
    for name in names:
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{at}: discharges entries must be non-empty requirement ids")
            continue
        if len(_REQ_ID_RE.findall(name)) > 1:
            errors.append(
                f"{at}: discharges entry {name!r} names more than one requirement - "
                "one id per element, so the claim can be read one line at a time")
    if kind != "known-unverified" and isinstance(selector, str) and not selector.strip():
        errors.append(
            f"{at}: an entry with an empty selector is recorded `unasserted` by the "
            "gate - screenshot-only - so it answers no requirement. Either name a "
            "selector or declare the gap with assert 'known-unverified'")
    if kind in ("widget", "populated") and len(names) > 1:
        errors.append(
            f"{at}: a {kind} assertion answers ONE question about ONE element, so it "
            f"discharges at most one requirement; this one claims {len(names)}. Split "
            "it, or say plainly what is uncovered with assert 'known-unverified'")


def _check_render_gate_near_miss(bp, errors):
    """A near-miss must never be quieter than a miss.

    `[render gate: X]` and `[Render-Gate: X]` are ordinary prose to every other
    rule here, so an author who wrote the link and mistyped it gets silence -
    the same failure shape this whole section exists to remove.
    """
    lines = list(_disclosure_lines(bp))
    lines += [(f"acceptance_checklist[{i}]", s)
              for i, s in enumerate(_as_list(bp.get("acceptance_checklist")))
              if isinstance(s, str)]
    labels = _render_gate_labels(bp)
    for path, line in lines:
        residue = _RG_NO_CLAIM_RE.sub("", _RG_MARKER_RE.sub("", line))
        if _RG_MALFORMED_MARKER_RE.search(residue):
            errors.append(
                f"{path}: carries something that reads as a render-gate marker but is "
                "not one. Write exactly '[render-gate: <label>]' or '[no-runtime-claim]' "
                f"- a mistyped marker is invisible to every check. Line: {line.strip()[:120]!r}")
        elif _RG_PROSE_ASSERTION_RE.search(residue):
            errors.append(
                f"{path}: opens with a render-gate token, so it reads as an assertion "
                "written into prose. Assertions live in screens[].render_gate, where a "
                "gate can execute them; prose carries only the '[render-gate: <label>]' "
                f"marker pointing at one. Line: {line.strip()[:120]!r}")
        for label in _RG_MARKER_RE.findall(line):
            if _nfc(label) not in labels:
                errors.append(
                    f"{path}: marker [render-gate: {label}] names no render_gate entry on "
                    "this blueprint - the link points at nothing")


def _check_render_gate_coverage(bp, warnings):
    """Advisory, never graduating: a screen with no assertion at all.

    Deliberately does NOT block at handoff. SKILL.md names a screen archetype
    with legitimately nothing to assert - an `instructional` screen, "a
    getting-started page, a launcher, a reference card. It explains rather than
    operates" - and blocking it would force the operator to invent a stated gap,
    which is the padding SKILL.md's "When a section is legitimately empty"
    exists to prevent. The rule that DOES block is the disclosure and
    requirement discharge below, because both are triggered by something the
    author themselves wrote.
    """
    bare = [s.get("name", "?") for s in _as_list(_as_dict(bp).get("screens"))
            if isinstance(s, dict) and not _as_list(s.get("render_gate"))]
    if not bare:
        return
    warnings.append(Finding(
        "screen(s) %s declare no render_gate assertion - nothing about what they "
        "must SHOW at runtime is checkable, so the render gate can only report "
        "them reached. If that is right (an instructional screen explains rather "
        "than operates), leave it; otherwise name the assertion, or declare the "
        "gap with assert 'known-unverified'"
        % ", ".join(repr(s) for s in bare),
        graduating=False,
    ))


def _check_disclosure_discharge(bp, warnings):
    """Graduating: every disclosure says where it is discharged.

    The structural slot, at the granularity of the failure. A disclosure line
    either names the assertion that covers it or says it makes no runtime claim
    - and one of the two is always the right answer, which is what lets this
    block at handoff without a waiver channel. A per-screen count cannot do this
    job: the v2 screen was not check-free, it was check-incomplete, and one
    trivial assertion would have cleared any floor.
    """
    unmarked = []
    for path, line in _disclosure_lines(bp):
        if _RG_MARKER_RE.search(line) or _RG_NO_CLAIM_RE.search(line):
            continue
        unmarked.append((path, line))
    if not unmarked:
        return
    warnings.append(Finding(
        "%d disclosure line(s) say where they are discharged and %d do not: %s. "
        "End each with '[render-gate: <label>]' naming the assertion that checks "
        "it, or '[no-runtime-claim]' if it asserts nothing observable on the "
        "rendered screen. A disclosure that reads like coverage and discharges "
        "nothing is the defect this rule exists to remove"
        % (sum(1 for _ in _disclosure_lines(bp)) - len(unmarked), len(unmarked),
           "; ".join(f"{p}: {t.strip()[:70]!r}" for p, t in unmarked[:4])
           + (" ..." if len(unmarked) > 4 else "")),
        graduating=True,
    ))


def _check_requirement_discharge(bp, warnings):
    """Graduating: every requirement id the blueprint cites is answered.

    Opt-in by the author's own citation - a blueprint that cites no ids gets no
    finding, so this can never force invented content. It fires on the specific
    v2 miss rather than on general absence: BR-SC-006 was cited in the checklist
    and answered by nothing.
    """
    cited = cited_requirement_ids(bp)
    if not cited:
        return
    answered = set()
    for _si, _sn, _ei, entry in _render_gate_entries(bp):
        haystack = " ".join(str(entry.get(k, "")) for k in ("label", "reason"))
        haystack += " " + " ".join(str(d) for d in _as_list(entry.get("discharges")))
        for req in cited:
            if req in haystack:
                answered.add(req)
    missing = sorted(cited - answered)
    if not missing:
        return
    warnings.append(Finding(
        "requirement id(s) %s are cited by this blueprint and answered by no "
        "render_gate entry. Name each in a `discharges` array on the assertion "
        "that checks it, or in the reason of a known-unverified entry saying why "
        "this screen cannot show it - a requirement the artifact claims to serve "
        "and nothing checks is how BR-SC-006 shipped unmet"
        % ", ".join(missing),
        graduating=True,
    ))


def render_gate_screens(bp):
    """Project the declared assertions into render-gate `screens[]` entries.

    The projection is MECHANICAL on purpose. A mapping table in a reference
    would leave the last hop - a human retyping an assertion into a check spec -
    as the one step that already failed once. What this cannot supply is `path`
    and `recordState`: neither is a design fact, both belong to the run. The
    gate rejects a screen missing either, loudly, so the omission cannot pass
    for a check.
    """
    out = []
    for screen in _as_list(bp.get("screens")):
        if not isinstance(screen, dict):
            continue
        entries = [e for e in _as_list(screen.get("render_gate")) if isinstance(e, dict)]
        if not entries:
            continue
        projected = {"name": screen.get("name")}
        families = {"widget": "expectWidgets", "populated": "expectPopulated"}
        for entry in entries:
            kind = entry.get("assert")
            if kind in families:
                projected.setdefault(families[kind], []).append(
                    {"label": entry.get("label"), "selector": entry.get("selector", "")})
            elif kind == "text":
                row = {"label": entry.get("label"), "selector": entry.get("selector", "")}
                row["contains" if entry.get("contains") is not None else "equals"] = (
                    entry.get("contains") if entry.get("contains") is not None
                    else entry.get("equals"))
                projected.setdefault("expectText", []).append(row)
            elif kind == "known-unverified":
                projected.setdefault("knownUnverified", []).append(
                    {"label": entry.get("label"), "reason": entry.get("reason")})
        out.append(projected)
    return out


def _check_acceptance_checklist_not_empty(bp, errors):
    """The one required section with no legitimate empty state.

    Adopted 2026-08-24 (UX-UI-Hub X-16). The field was previously unchecked, so
    a blueprint that produced no acceptance items validated clean - which is
    exactly how a section quietly stops being produced. Sections that ARE
    legitimately empty (blocks, entities, icon_mapping, roles) are listed in
    SKILL.md under "When a section is legitimately empty"; this is the
    counterpart that keeps that list from licensing over-omission.
    """
    if not bp.get("acceptance_checklist"):
        errors.append(
            "acceptance_checklist is empty. It is the one required section with "
            "no legitimate empty state - a screen with nothing worth checking is "
            "a screen with nothing worth building. See SKILL.md, 'When a section "
            "is legitimately empty'."
        )


def collect_errors(bp, extra_seed_targets=None, extra_declared=None):
    """Return a list of human-readable contract violations (empty = valid).

    extra_seed_targets (multi-path only): entity names seeded in a sibling
    blueprint - by an incoming FK+enum or by declared records - so F-B2 does
    not false-error on a static entity whose seed lives in another blueprint
    of the same app.

    extra_declared (multi-path only): entity names a sibling blueprint declares
    in its own entities[], for the foreign-key target check - a separate union,
    because a sibling DECLARING a static entity does not SEED it.
    """
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = []
    # Ahead of the schema check, which short-circuits: two of these four match
    # the relationship pattern and two do not, so leaving it downstream would
    # answer the same defect with a diagnosis in one half of the cases and a
    # generic "matches none of the permitted forms" in the other.
    _check_reserved_identifier_types(bp, errors)
    # Same reason: the schema's pattern refuses a display name with "does
    # not match", which names the defect and not the repair - and the
    # repair is a different field, not a different spelling of this one.
    _check_screen_name_is_element_name(bp, errors)
    # Same reason: the schema refuses a legacy spelling, so left downstream the
    # reader would be told the string matches none of the permitted forms rather
    # than which string to write instead. Both walk unvalidated input.
    _check_data_type_register(bp, errors)
    _check_primary_key_data_type(bp, errors)
    # Same reason, and now load-bearing: `data_type` is a closed vocabulary, so
    # a marker like "TBD" written there is rejected by the schema first and
    # would be reported as an unknown type rather than as the unresolved
    # placeholder it is. The walker is defensive on every node it touches.
    _check_placeholders(bp, errors)
    _check_schema(bp, schema, "$", errors)
    if errors:
        return errors
    _check_acceptance_checklist_not_empty(bp, errors)
    _check_region_shapes(bp, errors)
    _check_single_layout(bp, errors)
    _check_region_mapping(bp, errors)
    _check_block_name_granularity(bp, errors)
    _check_block_name_bare(bp, errors)
    _check_no_container(bp, errors)
    _check_product_vocabulary(bp, errors)
    _check_dropdown_option_expressions(bp, errors)
    _check_repeat_producer(bp, errors)
    _check_icon_convention(bp, errors)
    _check_binding_existence(bp, errors)
    _check_enum_on_non_fk(bp, errors)
    _check_existing_asset_channel(bp, errors)
    _check_create_attribute_channel(bp, errors)
    _check_records_on_non_static(bp, errors)
    _check_dual_seed_mismatch(bp, errors)
    _check_fk_target_declared(bp, errors, extra_declared)
    _check_static_datasource_unpopulated(bp, errors, extra_seed_targets)
    _check_assertion_parity(bp, errors)
    _check_assertions_required_for_filter_and_empty_state(bp, errors)
    _check_render_gate_shape(bp, errors)
    _check_render_gate_near_miss(bp, errors)
    return errors


def collect_warnings(bp):
    """Advisory findings that never affect the VALID/INVALID verdict.

    Runs on UNVALIDATED input, unlike the second half of `collect_errors`.
    `collect_errors` returns early when the schema check fails, so its later
    walkers only ever see a conforming blueprint; there is no such gate here -
    `_validate_one` calls this unconditionally, by design (see the note at that
    call site). Every walker below therefore obeys the same rule the pre-schema
    error checks do: skip what cannot be read, never stop reading. A validator
    that raises reports no findings at all, which is worse than a wrong one.
    """
    warnings = []
    _check_binding_type_fit(bp, warnings)
    _check_repeat_prose_columns(bp, warnings)
    _check_menu_chrome(bp, warnings)
    _check_existing_asset_announcement(bp, warnings)
    _check_buttongroup_onchange(bp, warnings)
    _check_render_gate_coverage(bp, warnings)
    _check_disclosure_discharge(bp, warnings)
    _check_requirement_discharge(bp, warnings)
    return warnings


def _check_buttongroup_onchange(bp, warnings):
    """Surface the unsettled `ButtonGroup.OnChange` observation at design time.

    A real build recorded the native `OnChange` never dispatching, and the OML
    of the failing revision showed the handler correctly wired - so no static
    check can tell a working ButtonGroup from a broken one. This fires where a
    human can still act on it: the moment a blueprint designs one.

    Advisory forever, never graduating. The observation is N=1, and a
    presentational ButtonGroup is a legitimate final state; blocking handoff on
    one unreproduced report would reject correct blueprints.
    """
    screens = []
    for screen in _as_list(_as_dict(bp).get("screens")):
        for region, sname in _leaf_regions(screen):
            block = _as_dict(region.get("outsystems_hints")).get("block")
            if block in ("ButtonGroup", "ButtonGroupItem") and sname not in screens:
                screens.append(sname)
    if not screens:
        return
    warnings.append(Finding(
        "screen(s) %s design a ButtonGroup: its native OnChange was observed "
        "not to dispatch on one real ODC build (search-engine-sandbox rev-261, "
        "2026-08) and the observation has never been reproduced or cleared. If "
        "the selection drives behaviour, either verify the handler fires or use "
        "Dropdown; if this build ships one, settle it - see the "
        "ButtonGroup.OnChange note in references/ui-reference.md for the "
        "three-widget sentinel check"
        % ", ".join(repr(s) for s in screens),
        # Never graduates: N=1, and a presentational ButtonGroup is a valid
        # final state, so this must not block a correct blueprint at handoff.
        graduating=False,
    ))


def _check_menu_chrome(bp, warnings):
    """Advisory (soak-1 G4): a menu-bearing layout should carry its menu content
    so OMI's Chrome Batch Discipline can review shared chrome - never an error,
    because chrome content may legitimately be absent from the wireframe."""
    chrome = _as_dict(_as_dict(bp).get("app_chrome"))
    if chrome.get("layout_block") in MENU_BEARING_LAYOUTS and not chrome.get("menu"):
        warnings.append(Finding(
            "app_chrome: layout %r has no 'menu' content - OMI reviews shared "
            "chrome from the blueprint; add app_chrome.menu ([{label, active}]) "
            "if the wireframe shows page links" % chrome.get("layout_block"),
            # Never blocks: chrome content may legitimately be absent from the
            # wireframe, as this check's own docstring says.
            graduating=False,
        ))


def _compare_key(data_type):
    """What two declarations of the same attribute are compared ON.

    The canonical spelling, so a type declared in the legacy register and the
    same type declared in the ODC literal register are one declaration rather
    than a conflict. A string outside the vocabulary has no canonical form and
    falls back to itself, so genuinely unknown types still compare literally
    instead of collapsing into one another.
    """
    return canonical_data_type(data_type) or data_type


def _entity_decls(bp, source):
    for e in bp.get("entities", []):
        if not isinstance(e, dict):
            continue
        pk_name = pk_type = pk_type_raw = None
        attrs = {}
        attrs_raw = {}
        for a in e.get("attributes", []):
            if not isinstance(a, dict) or "name" not in a:
                continue
            attrs[a["name"]] = (_compare_key(a.get("data_type")),
                                bool(a.get("is_foreign_key")))
            attrs_raw[a["name"]] = (a.get("data_type"),
                                    bool(a.get("is_foreign_key")))
            if a.get("is_primary_key"):
                pk_name = a["name"]
                pk_type = _compare_key(a.get("data_type"))
                pk_type_raw = a.get("data_type")
        records = e.get("records") if isinstance(e.get("records"), list) else None
        yield e.get("name"), {"source": source, "pk_name": pk_name,
                              "pk_type": pk_type, "pk_type_raw": pk_type_raw,
                              "attrs": attrs, "attrs_raw": attrs_raw,
                              "records": records}


def collect_cross_blueprint_errors(named_blueprints):
    """named_blueprints: list of (source_label, bp). Flag same-named entities
    declared with a conflicting shape across blueprints. Disjoint attribute
    subsets with the same PK are legitimate projections, not conflicts."""
    decls = defaultdict(list)
    for source, bp in named_blueprints:
        for name, decl in _entity_decls(bp, source):
            decls[name].append(decl)
    fk_seeds = defaultdict(list)  # target entity -> [(source, via, ordered_list)]
    for source, bp in named_blueprints:
        for target, via, lst in _fk_enum_seed_lists(bp):
            fk_seeds[target].append((source, via, lst))
    errors = []
    # Dual-seed mismatch across blueprints (OMI rule 6): one blueprint declares
    # a static's records, another seeds the same static via FK enum_values with
    # a differing ordered list. Same-source pairs are already caught per-file.
    for name, ds in decls.items():
        for d in ds:
            if not d.get("records"):
                continue
            for src, via, lst in fk_seeds.get(name, []):
                if src != d["source"] and lst != d["records"]:
                    errors.append(
                        f"entity '{name}' has a contradictory dual seed across "
                        f"blueprints: {d['source']} declares records "
                        f"{d['records']} vs {src} foreign key '{via}' enum_values "
                        f"{lst} - ordered lists must be identical (seeded once)"
                    )
    for name, ds in decls.items():
        if len(ds) < 2:
            continue

        # PK conflict: every distinct (pk_name, pk_type) pair seen, across ALL
        # declarations (not just vs the first one).
        pk_groups = defaultdict(list)
        for d in ds:
            # Grouped on the canonical form, reported as the file writes it -
            # the reader has to be able to find the string.
            pk_groups[(d["pk_name"], d["pk_type"])].append(
                (d["source"], d["pk_name"], d["pk_type_raw"]))
        if len(pk_groups) > 1:
            parts = [
                f"{src} (PK {pk_name}:{pk_type_raw})"
                for srcs in pk_groups.values()
                for src, pk_name, pk_type_raw in srcs
            ]
            errors.append(
                f"entity '{name}' has conflicting declarations across blueprints: "
                + " vs ".join(parts)
            )

        # Attribute conflict: for each attribute name declared by ANY of the
        # blueprints, every distinct (data_type, is_foreign_key) signature seen
        # among the declarations that declare it. Disjoint attribute subsets
        # (an attribute declared by only one blueprint) stay clean.
        attr_names = set()
        for d in ds:
            attr_names.update(d["attrs"])
        for attr in sorted(attr_names):
            sig_groups = defaultdict(list)
            for d in ds:
                if attr in d["attrs"]:
                    sig_groups[d["attrs"][attr]].append(
                        (d["source"], d["attrs_raw"][attr]))
            if len(sig_groups) > 1:
                parts = [
                    f"{src} {raw_sig}"
                    for srcs in sig_groups.values()
                    for src, raw_sig in srcs
                ]
                errors.append(
                    f"entity '{name}' attribute '{attr}' has conflicting types "
                    "across blueprints: " + " vs ".join(parts)
                )

        # Records conflict: every distinct non-empty declared records list seen
        # across the declarations that declare one. Declaring records in only
        # some blueprints is a legitimate projection, not a conflict.
        rec_groups = defaultdict(list)
        for d in ds:
            if d.get("records"):
                rec_groups[tuple(d["records"])].append(d["source"])
        if len(rec_groups) > 1:
            parts = [
                f"{src} (records {list(rec)})"
                for rec, srcs in rec_groups.items()
                for src in srcs
            ]
            errors.append(
                f"entity '{name}' has conflicting declared records across "
                "blueprints: " + " vs ".join(parts)
            )
    _collect_chrome_conflicts(named_blueprints, errors)
    return errors


def _collect_chrome_conflicts(named_blueprints, errors):
    """One app, one chrome. A multi-screen app is N design runs sharing one
    chrome decision made up front (chain ordering rule 3), and nothing checked
    that the N runs actually agreed - a screen could ship a different layout,
    a different app title, or a different sidebar and every per-file validation
    would still pass.

    `active` is deliberately excluded: each screen highlights its own menu
    entry, so comparing it would fail every correctly-built app.
    """
    for field in ("layout_block", "app_title"):
        groups = defaultdict(list)
        for source, bp in named_blueprints:
            value = bp.get("app_chrome", {}).get(field)
            if value is not None:
                groups[value].append(source)
        if len(groups) > 1:
            parts = [f"{src} ({field} {value!r})"
                     for value, srcs in groups.items() for src in srcs]
            errors.append(
                f"app_chrome.{field} differs across blueprints: "
                + " vs ".join(parts)
                + " - every screen in one app shares one chrome decision"
            )

    menus = {}
    for source, bp in named_blueprints:
        menu = bp.get("app_chrome", {}).get("menu")
        if isinstance(menu, list):
            menus[source] = tuple(e.get("label") for e in menu if isinstance(e, dict))
    if len(set(menus.values())) < 2:
        return
    base_source, base = next(iter(menus.items()))
    for source, labels in menus.items():
        if labels == base:
            continue
        if set(labels) == set(base):
            errors.append(
                f"app_chrome.menu order differs between {base_source} and "
                f"{source}: {list(base)} vs {list(labels)} - the same links in "
                "a different order is a different sidebar to the user"
            )
        else:
            only_one = sorted(x for x in set(base) ^ set(labels) if x is not None)
            errors.append(
                f"app_chrome.menu entries differ between {base_source} and "
                f"{source}: {only_one} appear(s) in only one - every screen "
                "shares one navigation"
            )


def collect_plan_agreement_errors(plan_text, named_blueprints):
    """Flag every entity a blueprint declares that the plan never names.

    The chain calls entity names the reconciliation boundary between its two
    routes, and until now the check was manual. It runs in one direction only:
    plan prose is free-form, so blueprint -> plan can be checked mechanically
    while plan -> blueprint cannot without guessing which capitalised words are
    entities. Matching is word-bounded, so `QueryHistoryArchive` in the plan
    does not satisfy an entity named `QueryHistory`.
    """
    errors = []
    for source, bp in named_blueprints:
        for entity in bp.get("entities", []):
            if not isinstance(entity, dict):
                continue
            name = entity.get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            if not re.search(rf"\b{re.escape(name)}\b", plan_text):
                errors.append(
                    f"{source}: entity '{name}' is declared in the blueprint but "
                    "never named in the plan - the two routes must agree at the "
                    "entity-name reconciliation boundary"
                )
    return errors


# --- Inventory agreement (the inventory -> blueprint tier boundary) -----------
#
# For a multi-screen app the screen inventory is the upstream artifact: it holds
# the one chrome decision, the authoritative screen list, and the assertion
# counts each screen's requirement asked for. Those facts reached the design run
# as prose (outsystems-screen-inventory's `format_brief`) and nothing checked
# that the blueprint it produced still carried them. `_collect_chrome_conflicts`
# comes closest, but it needs two blueprints to compare - so a one-screen design
# run had no chrome anchor at all.
#
# Direction is inventory -> blueprint only. A design run validates the screen it
# just built; the other N-1 inventory screens have simply not been designed yet,
# so an inventory screen with no blueprint is never a finding.


def _inventory_menu_for_screen(inv, screen_name):
    """The inventory's `{label, target}` menu in the blueprint's `{label, active}`
    shape: `target` never enters a blueprint, it becomes this screen's `active`.

    Duplicated on purpose from outsystems-screen-inventory's
    `blueprint_menu_for_screen` rather than imported - the two skills ship in
    different export packs and neither may depend on the other being installed.
    That suite's `test_menu_translation_matches_the_design_validator` is the
    drift gate.
    """
    chrome = inv.get("app_chrome")
    menu = chrome.get("menu") if isinstance(chrome, dict) else None
    return [
        {"label": e.get("label"), "active": e.get("target") == screen_name}
        for e in (menu if isinstance(menu, list) else [])
        if isinstance(e, dict)
    ]


def _inventory_screens(inv):
    return {
        s["name"]: s for s in (inv.get("screens") or [])
        if isinstance(s, dict) and isinstance(s.get("name"), str)
    }


def _blueprint_screen_names(bp):
    return [s.get("name") for s in bp.get("screens", []) if isinstance(s, dict)]


def _check_inventory_screen_names(inv_screens, source, bp, errors):
    for name in _blueprint_screen_names(bp):
        if name in inv_screens:
            continue
        known = ", ".join(sorted(inv_screens)) or "(none)"
        errors.append(
            f"{source}: screen {name!r} is not in the inventory - the inventory "
            "is the authoritative screen list, so a screen designed without an "
            "entry there has no recorded purpose, archetype or behaviour. "
            f"Inventory screens: {known}"
        )


def _check_inventory_chrome(inv, inv_screens, source, bp, errors):
    inv_chrome = inv.get("app_chrome") if isinstance(inv.get("app_chrome"), dict) else {}
    bp_chrome = bp.get("app_chrome") if isinstance(bp.get("app_chrome"), dict) else {}

    for field in ("layout_block", "app_title"):
        expected = inv_chrome.get(field)
        if expected is None:
            continue  # a half-built inventory fails its own validator, not this one
        actual = bp_chrome.get(field)
        if actual != expected:
            errors.append(
                f"{source}: app_chrome.{field} is {actual!r} but the inventory "
                f"decided {expected!r} - the chrome decision is made once for "
                "the whole app and copied into every blueprint"
            )

    if "menu" not in inv_chrome:
        return
    # `active` is per-screen while the menu is app-level, so it is only decidable
    # when the file carries exactly one screen. Labels are checked either way.
    named = [n for n in _blueprint_screen_names(bp) if n in inv_screens]
    anchor = named[0] if len(_blueprint_screen_names(bp)) == 1 and named else None
    expected = _inventory_menu_for_screen(inv, anchor)
    raw = bp_chrome.get("menu")
    actual = [e for e in raw if isinstance(e, dict)] if isinstance(raw, list) else []

    expected_labels = [e["label"] for e in expected]
    actual_labels = [e.get("label") for e in actual]
    if expected_labels != actual_labels:
        errors.append(
            f"{source}: app_chrome.menu carries {actual_labels} but the "
            f"inventory decided {expected_labels} - every screen in one app "
            "carries the same navigation, in the inventory's order"
        )
        return  # comparing `active` on a different menu would only add noise

    if anchor is None:
        return
    expected_on = [e["label"] for e in expected if e["active"]]
    actual_on = [e.get("label") for e in actual if e.get("active") is True]
    if expected_on != actual_on:
        errors.append(
            f"{source}: screen {anchor!r} marks {actual_on} as the active menu "
            f"entry, but the inventory's menu targets make it {expected_on} - "
            "`active` is derived from which entry targets this screen, never "
            "chosen per blueprint"
        )


def _check_inventory_assertions(inv_screens, source, bp, errors):
    """The inventory's counts come from the requirement and are carried through.

    This failure gets its own message on purpose. `_check_assertion_parity`
    already forces the blueprint's counts to equal its own `main_content`, so
    telling the operator to edit the number here would put them between two
    rules that cannot both be satisfied. The repair is upstream: either the
    design is missing something the requirement asked for, or the inventory's
    count was wrong.
    """
    for screen in bp.get("screens", []):
        if not isinstance(screen, dict):
            continue
        inv_screen = inv_screens.get(screen.get("name"))
        if inv_screen is None:
            continue
        declared = inv_screen.get("assertions")
        if not isinstance(declared, dict):
            continue
        carried = screen.get("assertions")
        carried = carried if isinstance(carried, dict) else {}
        for key, count in sorted(declared.items()):
            # The inventory's own validator owns its vocabulary; re-reporting an
            # unsupported key here would fail two artifacts for one typo.
            if key not in _ASSERTION_WIDGETS:
                continue
            if carried.get(key) == count:
                continue
            errors.append(
                f"{source}: screen {screen.get('name')!r} carries "
                f"assertions.{key} = {carried.get(key)!r}, but the inventory "
                f"declared {count} - the inventory's counts come from the "
                "requirement and are carried into the blueprint unchanged. Do "
                "not edit the number to agree: either the design is missing "
                f"{key} the requirement asked for (add them to the screen and "
                "re-derive), or the inventory's count was wrong (fix the "
                "inventory and re-run its validator)"
            )


# `opens` - the destination slot on a control. Optional and per control, so a
# blueprint authored before it existed is the same artifact it was; checked only
# here, because the inventory is the only artifact that knows which screen names
# are real.
#
# Measured on restaurant-app-v2 (2026-08-30): six screens were never built
# because no artifact named them. The inventory tier has since closed its half
# (outsystems-screen-inventory's R10, `record_actions`). The blueprint tier had
# NOWHERE to say it - every control that opened a screen described its
# destination in prose inside `data` ("Abre a configuracao do restaurante"), and
# prose is resolved against nothing. Two of those buttons were called inert for
# a day before the deployed screen list showed the destinations did not exist.
#
# Both rules below are mechanical and language-independent on purpose. The
# verb-reading the inventory does upstream is anchored on English openers, and
# the blueprints that paid for this rule are written in Portuguese: a prose
# reader would have found nothing on the very artifact that motivated it.
OPENS_INLINE = "inline"

# Mirrors outsystems-screen-inventory's RECORD_ACTION_INLINE / _OUT_OF_SCOPE.
# Duplicated rather than imported, for the same reason `_inventory_menu_for_screen`
# is: the two skills ship in different export packs and neither may depend on the
# other being installed.
_RECORD_ACTION_NON_DESTINATIONS = (OPENS_INLINE, "out-of-scope")


def _screen_opens(screen):
    """`(path, value)` for every control on a screen that declares `opens`.

    Walks leaf regions, so the per-row controls inside a group are covered -
    that is where the incident's "Editar" and "Configurar" buttons sat, not at
    the top of `main_content`.
    """
    for region, _sn in _leaf_regions(screen):
        rid = region.get("id", "?")
        for i, item in enumerate(_as_list(region.get("content"))):
            if isinstance(item, dict) and "opens" in item:
                yield f"region {rid!r} content[{i}]", item.get("opens")


def _check_inventory_opens(inv_screens, source, bp, errors):
    """N1: a named destination has to name a real screen.

    `inline` is accepted verbatim - the same third answer `record_actions`
    takes, meaning the action happens on this screen and there is no
    destination to resolve.
    """
    for screen in _as_list(bp.get("screens")):
        if not isinstance(screen, dict):
            continue
        name = screen.get("name")
        for where, target in _screen_opens(screen):
            if not isinstance(target, str) or not target.strip():
                errors.append(
                    f"{source}: screen {name!r} {where}: 'opens' must be a "
                    f"non-empty screen name, or {OPENS_INLINE!r} when the "
                    f"control acts on this screen - got {target!r}")
                continue
            target = target.strip()
            if target == OPENS_INLINE:
                continue
            if target == name:
                errors.append(
                    f"{source}: screen {name!r} {where}: 'opens' points at this "
                    f"screen itself - say {OPENS_INLINE!r} when the control "
                    "acts here rather than opening somewhere")
                continue
            if target not in inv_screens:
                known = ", ".join(sorted(inv_screens)) or "(none)"
                errors.append(
                    f"{source}: screen {name!r} {where}: 'opens' names "
                    f"{target!r}, which is not a screen in the inventory - a "
                    "control whose destination was never in the inventory is "
                    "still built, renders, and does nothing. Inventory "
                    f"screens: {known}")


def _check_inventory_record_action_doors(inv_screens, source, bp, errors):
    """N2: the inventory promised a door, so the blueprint has to draw it.

    N1 alone only catches a destination named WRONG. The blueprints that paid
    for this rule named no destination at all, so N1 would have passed them.
    This is the rule that fires on silence.

    Malformed `record_actions` entries are skipped rather than reported: their
    shape is the inventory validator's R10 to own, and one defect deserves one
    message.
    """
    for screen in _as_list(bp.get("screens")):
        if not isinstance(screen, dict):
            continue
        name = screen.get("name")
        inv_screen = inv_screens.get(name)
        if not isinstance(inv_screen, dict):
            continue  # reported by `_check_inventory_screen_names`
        drawn = {t.strip() for _w, t in _screen_opens(screen)
                 if isinstance(t, str)}
        for entry in _as_list(inv_screen.get("record_actions")):
            if not isinstance(entry, dict):
                continue
            action, resolves = entry.get("action"), entry.get("resolves_to")
            if not isinstance(action, str) or not isinstance(resolves, str):
                continue
            if resolves in _RECORD_ACTION_NON_DESTINATIONS:
                continue
            if resolves in drawn:
                continue
            errors.append(
                f"{source}: screen {name!r} has no control with "
                f"'opens': {resolves!r}, but the inventory resolves its "
                f"{action!r} record action to that screen - the door the "
                "inventory settled is missing from the design that has to "
                "draw it")


def collect_inventory_agreement_errors(inv, named_blueprints):
    """Flag every place a blueprint contradicts the inventory it was built from.

    Screen names, chrome and carried assertions are errors: the inventory is
    definitionally authoritative on all three. Entity bindings are advisory and
    live in `collect_inventory_agreement_warnings`.
    """
    errors = []
    if not isinstance(inv, dict):
        # Appended rather than returned as a literal, so the rule census can see
        # it: a finding that never goes through `errors.append` is not counted,
        # and an uncounted rule can be deleted with every test still green. This
        # one was uncounted until 2026-09-01.
        errors.append("inventory: top level must be a JSON object")
        return errors
    inv_screens = _inventory_screens(inv)
    for source, bp in named_blueprints:
        _check_inventory_screen_names(inv_screens, source, bp, errors)
        _check_inventory_chrome(inv, inv_screens, source, bp, errors)
        _check_inventory_assertions(inv_screens, source, bp, errors)
        _check_inventory_opens(inv_screens, source, bp, errors)
        _check_inventory_record_action_doors(inv_screens, source, bp, errors)
    return errors


def collect_inventory_agreement_warnings(inv, named_blueprints):
    """Advisory: an entity the inventory bound to a screen that the screen's
    blueprint never declares.

    Never an error. A legitimate design can surface an entity through a reused
    block or a foreign-key lookup without declaring it, so blocking here would
    fail correct work. `kind: "action"` bindings are not checked at all - a
    blueprint has no home for an action name, so any finding about one would be
    undischargeable.
    """
    if not isinstance(inv, dict):
        return []
    inv_screens = _inventory_screens(inv)
    warnings = []
    for source, bp in named_blueprints:
        declared = {
            e.get("name") for e in bp.get("entities", []) if isinstance(e, dict)
        }
        for name in _blueprint_screen_names(bp):
            inv_screen = inv_screens.get(name)
            if inv_screen is None:
                continue
            for binding in inv_screen.get("data_bindings") or []:
                if not isinstance(binding, dict) or binding.get("kind") != "entity":
                    continue
                bound = binding.get("name")
                if bound in declared:
                    continue
                warnings.append(Finding(
                    f"{source}: screen {name!r} does not declare entity "
                    f"{bound!r}, which the inventory lists as a data binding "
                    "for it - advisory only, since the screen may legitimately "
                    "reach that entity through a reused block or a foreign-key "
                    "lookup",
                    # Never blocks: the screen may reach the entity through a
                    # reused block or a foreign-key lookup, as the text says.
                    graduating=False,
                ))
    return warnings


def _expand_paths(raw_paths):
    out = []
    for rp in raw_paths:
        p = Path(rp)
        if p.is_dir():
            # Directory intake is restricted to canonical blueprint.json files:
            # a parent of per-screen directories (*/blueprint.json) or a single
            # screen directory (blueprint.json). A directory holding only
            # arbitrarily-named *.json is NOT intaken - it expands to nothing and
            # main() reports "no blueprint files found" (exit 2), so a misnamed
            # file is never silently validated, and per-file reports never collide.
            found = sorted(p.glob("*/blueprint.json")) or sorted(p.glob("blueprint.json"))
            out.extend(found)
        else:
            out.append(p)
    return out


def _validate_one(bp_path, report_path, extra_seed_targets=None,
                  extra_declared=None, handoff=False):
    """Existing single-file behaviour. Returns (exit_code, bp_or_None).

    extra_seed_targets and extra_declared are passed through to collect_errors
    for multi-path evaluation - the sibling seed union for F-B2, the sibling
    entity-name union for the foreign-key target check. Single-path callers omit
    both, so behaviour is unchanged.
    """
    try:
        bp = json.loads(bp_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report = f"INVALID: cannot parse {bp_path}: {exc}\n"
        try:
            report_path.write_text(report, encoding="utf-8")
        except OSError:
            pass
        sys.stdout.write(report)
        return 2, None
    errors = collect_errors(bp, extra_seed_targets=extra_seed_targets,
                            extra_declared=extra_declared)
    # Deliberately UNCONDITIONAL, decided rather than inherited. Skipping this
    # when `errors` is non-empty would be the cheap way to keep a malformed
    # blueprint out of the warning walkers, and it is the wrong one: the common
    # invalid blueprint is entirely readable - one missing `outsystems_hints`,
    # one undeclared bind - and its advisory findings are worth printing in the
    # same pass, which is what every INVALID report has always done. The
    # graduating subset below is computed from this list too, so a `--handoff`
    # run would lose its blocking findings the moment any contract error
    # appeared. Robustness against unreadable input belongs in the walkers, and
    # that is where `collect_errors` already put it.
    warnings = collect_warnings(bp)
    # Graduation. Two regimes over one finding set: while the design is being
    # drawn every warning advises, and at handoff the graduating subset blocks
    # instead. The finding text is identical either way - only the channel it
    # prints in, and the exit code, depend on the regime. A graduating warning
    # is never counted as a contract error: the blueprint still conforms.
    blocking = graduating_findings(warnings) if handoff else []
    advisory = advisory_findings(warnings) if handoff else warnings
    if errors:
        lines = [f"INVALID: {len(errors)} contract error(s)."] + [f"- {e}" for e in errors]
    else:
        lines = ["VALID: blueprint conforms to the OMI enriched-blueprint contract."]
    for w in advisory:
        lines.append(f"WARNING: {w}")
    if blocking:
        plural = "" if len(blocking) == 1 else "s"
        lines.append(
            f"HANDOFF BLOCKED: {len(blocking)} graduating warning{plural} - "
            "advisory while the design is being drawn, blocking here. "
            "Each is fixable in the blueprint; fix and re-validate")
        lines += [f"- {w}" for w in blocking]
    report = "\n".join(lines) + "\n"
    report_path.write_text(report, encoding="utf-8")
    sys.stdout.write(report)
    return (1 if (errors or blocking) else 0), bp


def _emit_plan_agreement(plan_path, loaded):
    """Print the plan-to-blueprint reconciliation. True means they disagree."""
    try:
        plan_text = Path(plan_path).read_text(encoding="utf-8")
    except OSError as exc:
        sys.stdout.write(f"PLAN AGREEMENT: cannot read plan {plan_path}: {exc}\n")
        return True
    errors = collect_plan_agreement_errors(plan_text, loaded)
    if errors:
        sys.stdout.write(f"PLAN AGREEMENT: {len(errors)} disagreement(s).\n")
        for e in errors:
            sys.stdout.write(f"- {e}\n")
        return True
    sys.stdout.write(
        f"PLAN AGREEMENT: every declared entity is named in {plan_path}.\n")
    return False


def _emit_inventory_agreement(inventory_path, loaded):
    """Print the inventory-to-blueprint reconciliation. True means they disagree.

    An unreadable inventory disagrees. The gate exists because the boundary was
    unchecked; a missing file silently restoring that state is the fail-open
    shape this chain keeps paying for.
    """
    try:
        inv = json.loads(Path(inventory_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        sys.stdout.write(
            f"INVENTORY AGREEMENT: cannot read inventory {inventory_path}: {exc}\n")
        return True
    errors = collect_inventory_agreement_errors(inv, loaded)
    if errors:
        sys.stdout.write(f"INVENTORY AGREEMENT: {len(errors)} disagreement(s).\n")
        for e in errors:
            sys.stdout.write(f"- {e}\n")
    else:
        sys.stdout.write(
            "INVENTORY AGREEMENT: screen names, chrome and carried assertions "
            f"match {inventory_path}.\n")
    for w in collect_inventory_agreement_warnings(inv, loaded):
        sys.stdout.write(f"INVENTORY AGREEMENT WARNING: {w}\n")
    return bool(errors)


def _cross_blueprint_unions(paths):
    """(seed targets, declared entity names) across every parseable blueprint.

    F-B2 and the foreign-key target check are hard ERRORS evaluated against
    this union, so a legitimate cross-blueprint projection - an entity declared
    in one blueprint and seeded from a sibling - is not false-flagged. Shared
    by every path that evaluates the contract, because a second path computing
    it differently applies a stricter contract than the verdict the operator
    was shown.
    """
    seeds = set()
    declared = set()
    for bp_path in paths:
        try:
            bp = json.loads(bp_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        seeds |= _fk_enum_targets(bp) | _records_targets(bp)
        declared |= declared_entity_names(bp)
    return seeds, declared


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+",
                        help="One or more blueprint.json paths, or a directory")
    parser.add_argument("--report",
                        help="Report path (single-path only; default: beside the blueprint)")
    parser.add_argument("--plan",
                        help="Implementation plan (markdown) to reconcile entity "
                             "names against - the chain's cross-route boundary")
    parser.add_argument("--inventory",
                        help="screen-inventory.json this design run was briefed "
                             "from - the tier boundary: screen names, chrome and "
                             "carried assertions must still agree with it")
    parser.add_argument("--emit-render-gate-spec", metavar="PATH",
                        help="Write the declared render_gate assertions as render-gate "
                             "screens[] entries, so the check spec is projected rather "
                             "than retyped. `path` and `recordState` belong to the run "
                             "and are added by the operator")
    parser.add_argument("--handoff", action="store_true",
                        help="Grade this run as a handoff rather than a draft: "
                             "the graduating warnings - the ones always fixable "
                             "by the author - block instead of advising. Without "
                             "it the report is unchanged, byte for byte")
    args = parser.parse_args(argv)

    paths = _expand_paths(args.paths)

    if not paths:
        sys.stdout.write(
            f"INVALID: no blueprint files found in: {' '.join(args.paths)}\n"
        )
        return 2

    # Emitted BEFORE the report and only from a blueprint that passes the
    # contract: projecting an executable spec out of a blueprint the validator
    # rejects would hand the gate assertions nobody has checked the shape of,
    # which is the silent-garbage path this whole feature exists to close.
    if args.emit_render_gate_spec:
        emit_seeds, emit_declared = _cross_blueprint_unions(paths)
        screens = []
        for bp_path in paths:
            try:
                bp = json.loads(bp_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                sys.stdout.write(f"INVALID: {bp_path}: {exc}\n")
                return 2
            # Evaluated on the SAME footing as the report below, unions and
            # all. Re-running collect_errors bare applied a stricter contract
            # than the validator's own verdict: a legitimate cross-blueprint
            # projection (entity declared in A, seeded from B) validated clean
            # in the report and was refused here, with a diagnosis that was
            # simply false - the blueprint was not broken.
            found = collect_errors(bp, extra_seed_targets=emit_seeds,
                                   extra_declared=emit_declared)
            if found:
                sys.stdout.write(
                    f"INVALID: {bp_path} carries {len(found)} contract error(s); no "
                    "render-gate spec projected. Fix the blueprint first - an "
                    "assertion set derived from a rejected blueprint is not evidence "
                    "of anything.\n")
                for error in found:
                    sys.stdout.write(f"- {error}\n")
                return 2
            screens.extend(render_gate_screens(bp))
        Path(args.emit_render_gate_spec).write_text(
            json.dumps({"screens": screens}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
        sys.stdout.write(
            f"RENDER-GATE SPEC: {len(screens)} screen(s) projected to "
            f"{args.emit_render_gate_spec}. Add `path` and `recordState` per record "
            "state before running the gate.\n")

    # Single-path: identical to the historical behaviour, including exit code 2.
    if len(paths) == 1:
        bp_path = paths[0]
        report_path = Path(args.report) if args.report else bp_path.with_name("validation-report.txt")
        code, bp = _validate_one(bp_path, report_path, handoff=args.handoff)
        if bp is not None:
            named = [(str(bp_path), bp)]
            # Single-path is where this matters most: the cross-blueprint chrome
            # pass needs two files, so until now one screen had no chrome anchor.
            if args.inventory and _emit_inventory_agreement(args.inventory, named):
                code = code or 1
            if args.plan and _emit_plan_agreement(args.plan, named):
                code = code or 1
        return code

    # Multi-path: per-file reports beside each, then the cross-blueprint pass.
    union_seed_targets, union_declared = _cross_blueprint_unions(paths)

    any_error = False
    loaded = []
    for bp_path in paths:
        report_path = bp_path.with_name("validation-report.txt")
        code, bp = _validate_one(bp_path, report_path,
                                 extra_seed_targets=union_seed_targets,
                                 extra_declared=union_declared,
                                 handoff=args.handoff)
        if code != 0:
            any_error = True
        if bp is not None:
            loaded.append((str(bp_path), bp))
    if len(loaded) >= 2:
        cross = collect_cross_blueprint_errors(loaded)
        if cross:
            any_error = True
            sys.stdout.write(f"CROSS-BLUEPRINT: {len(cross)} conflict(s).\n")
            for c in cross:
                sys.stdout.write(f"- {c}\n")
        else:
            sys.stdout.write("CROSS-BLUEPRINT: no conflicts.\n")
    if args.inventory and loaded and _emit_inventory_agreement(args.inventory, loaded):
        any_error = True
    if args.plan and loaded and _emit_plan_agreement(args.plan, loaded):
        any_error = True
    return 1 if any_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
