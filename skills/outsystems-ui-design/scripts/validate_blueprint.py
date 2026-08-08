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

LAYOUT_BLOCKS = ("LayoutSideMenu", "LayoutTopMenu", "LayoutBlank")
REPEAT_MARKERS = ("ListRecords", "TableRecords", "Table", "Gallery", "Carousel", "AccordionList")
NUMERIC_TYPES = {"integer", "longInteger", "decimal", "currency"}
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
}


def _check_schema(node, schema, path, errors):
    expected = schema.get("type")
    if expected and not isinstance(node, _TYPES[expected]):
        errors.append(f"{path}: expected {expected}, got {type(node).__name__}")
        return
    if "enum" in schema and node not in schema["enum"]:
        errors.append(f"{path}: value {node!r} not in {schema['enum']}")
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
    for region in screen.get("main_content", []):
        if not isinstance(region, dict):
            continue
        if region.get("type") == "group":
            for item in region.get("items", []):
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
            block = (region.get("outsystems_hints") or {}).get("block")
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
                "block": (region.get("outsystems_hints") or {}).get("block", ""),
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
            block = (region.get("outsystems_hints") or {}).get("block")
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
            block = (region.get("outsystems_hints") or {}).get("block")
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


def _check_repeat_producer(bp, errors):
    for screen in bp.get("screens", []):
        for region, group, screen_name in _leaf_regions(screen, with_group=True):
            texts = list(_iter_strings({
                "block": (region.get("outsystems_hints") or {}).get("block", ""),
                "content": region.get("content", []),
            }))
            if not any(_REPEAT_RE.search(t) for t in texts):
                continue
            own = (region.get("data_source") or {}).get("entity")
            inherited = ((group or {}).get("data_source") or {}).get("entity")
            entity = own or inherited
            label = region.get("name") or region.get("id") or "?"
            if not entity:
                errors.append(
                    f"screen '{screen_name}' region '{label}': repeated content "
                    "(ListRecords/Table/Gallery/...) without a data producer - set "
                    "data_source.entity on the region or its group"
                )
            elif entity not in _declared_entities(bp):
                errors.append(
                    f"screen '{screen_name}' region '{label}': data_source.entity "
                    f"{entity!r} is not a declared entity"
                )


def _declared_entities(bp):
    """entity name -> {attribute name -> attribute object}."""
    out = {}
    for ent in bp.get("entities", []):
        if not isinstance(ent, dict):
            continue
        attrs = {}
        for a in ent.get("attributes", []):
            if isinstance(a, dict) and "name" in a:
                attrs[a["name"]] = a
        out[ent.get("name")] = attrs
    return out


def _iter_binds(bp):
    """Yield (screen_name, element, binds) for every content item carrying binds."""
    for screen in bp.get("screens", []):
        sname = screen.get("name", "?")
        for region, _sn in _leaf_regions(screen):
            for item in region.get("content", []) or []:
                if isinstance(item, dict) and isinstance(item.get("binds"), dict):
                    yield sname, item.get("element", ""), item["binds"]


def _check_binding_existence(bp, errors):
    declared = _declared_entities(bp)
    for sname, _element, binds in _iter_binds(bp):
        ent = binds.get("entity")
        attr = binds.get("attribute")
        if ent not in declared:
            errors.append(
                f"screen '{sname}': binds.entity {ent!r} is not a declared entity"
            )
        elif attr not in declared[ent]:
            errors.append(
                f"screen '{sname}': binds.attribute {attr!r} does not exist on entity "
                f"{ent!r} (declared: {sorted(declared[ent])})"
            )


def _check_binding_type_fit(bp, warnings):
    declared = _declared_entities(bp)
    for sname, element, binds in _iter_binds(bp):
        attr = declared.get(binds.get("entity"), {}).get(binds.get("attribute"))
        if not attr:
            continue  # existence gate already errors
        if _NUMERIC_WIDGET_RE.search(element) and attr.get("data_type") not in NUMERIC_TYPES:
            warnings.append(
                f"screen '{sname}': {element} binds to "
                f"{binds['entity']}.{binds['attribute']} (data_type "
                f"{attr.get('data_type')!r}), which is not numeric - a "
                "ProgressBar/Counter expects a numeric attribute"
            )
        if _STATUS_WIDGET_RE.search(element) and not (
            attr.get("is_foreign_key") and attr.get("enum_values")
        ):
            warnings.append(
                f"screen '{sname}': {element} binds to "
                f"{binds['entity']}.{binds['attribute']}, which is not backed by a "
                "static entity - a status Tag/Badge expects a static-entity-backed "
                "attribute"
            )


_ASSERTION_WIDGETS = {"links": "Link", "buttons": "Button", "inputs": "Input"}


def _derive_counts(screen):
    counts = {k: 0 for k in _ASSERTION_WIDGETS}
    for region, _sn in _leaf_regions(screen):
        for item in region.get("content", []) or []:
            if not isinstance(item, dict):
                continue
            element = item.get("element", "")
            for key, word in _ASSERTION_WIDGETS.items():
                if re.search(rf"\b{word}\b", element):
                    counts[key] += 1
    return counts


def _check_assertion_parity(bp, errors):
    for screen in bp.get("screens", []):
        assertions = screen.get("assertions")
        if not isinstance(assertions, dict):
            continue
        derived = _derive_counts(screen)
        sname = screen.get("name", "?")
        for key, claimed in assertions.items():
            if key in derived and claimed != derived[key]:
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
    """Entity names flagged `exists: true` - already in the target app."""
    return {e.get("name") for e in bp.get("entities", [])
            if isinstance(e, dict) and e.get("exists") is True}


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
            elif (region.get("outsystems_hints") or {}).get("block") or \
                    region.get("custom_block_needed"):
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


def _check_existing_asset_announcement(bp, warnings):
    """Advisory: a bound asset should also be announced in existing_assets, so
    the target boundary stays readable without walking every region."""
    declared = bp.get("target_context", {}).get("existing_assets") or []
    known = set()
    for entry in declared:
        if isinstance(entry, str) and entry.strip():
            known.add(entry.strip())
            known.add(entry.strip().rsplit("/", 1)[-1])
    bound = []
    for screen in bp.get("screens", []):
        for region, _sn in _leaf_regions(screen):
            block = _reused_block(region)
            if block:
                bound.append(("reused block", block))
    bound.extend(("existing entity", n) for n in sorted(_existing_entities(bp)) if n)
    for kind, name in bound:
        if name not in known and name.rsplit("/", 1)[-1] not in known:
            warnings.append(
                f"{kind} {name!r} is bound in the blueprint but not named in "
                "target_context.existing_assets - announce it there too"
            )


def _datasource_entities(bp):
    names = set()
    for screen in bp.get("screens", []):
        for region, group, _sn in _leaf_regions(screen, with_group=True):
            for holder in (region, group):
                ent = (holder or {}).get("data_source", {}).get("entity") \
                    if isinstance((holder or {}).get("data_source"), dict) else None
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
    for screen in bp.get("screens", []):
        sname = screen.get("name", "?")
        for region, group, _sn in _leaf_regions(screen, with_group=True):
            own = region.get("data_source") if isinstance(region.get("data_source"), dict) else {}
            grp = (group or {}).get("data_source") if isinstance((group or {}).get("data_source"), dict) else {}
            entity = (own or {}).get("entity") or (grp or {}).get("entity")
            if not entity:
                continue
            for item in region.get("content", []) or []:
                if not isinstance(item, dict):
                    continue
                element = item.get("element", "")
                if _REPEAT_RE.search(element) and not isinstance(item.get("binds"), dict):
                    label = region.get("name") or region.get("id") or "?"
                    warnings.append(
                        f"screen '{sname}' region '{label}': repeat widget "
                        f"'{element}' over '{entity}' has no structured binds - its "
                        f"columns are prose-only and cannot be verified against "
                        f"'{entity}'s attributes"
                    )


def collect_errors(bp, extra_seed_targets=None):
    """Return a list of human-readable contract violations (empty = valid).

    extra_seed_targets (multi-path only): entity names seeded in a sibling
    blueprint - by an incoming FK+enum or by declared records - so F-B2 does
    not false-error on a static entity whose seed lives in another blueprint
    of the same app.
    """
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = []
    _check_schema(bp, schema, "$", errors)
    if errors:
        return errors
    _check_region_shapes(bp, errors)
    _check_single_layout(bp, errors)
    _check_region_mapping(bp, errors)
    _check_block_name_granularity(bp, errors)
    _check_block_name_bare(bp, errors)
    _check_no_container(bp, errors)
    _check_repeat_producer(bp, errors)
    _check_icon_convention(bp, errors)
    _check_binding_existence(bp, errors)
    _check_enum_on_non_fk(bp, errors)
    _check_existing_asset_channel(bp, errors)
    _check_records_on_non_static(bp, errors)
    _check_dual_seed_mismatch(bp, errors)
    _check_static_datasource_unpopulated(bp, errors, extra_seed_targets)
    _check_assertion_parity(bp, errors)
    return errors


def collect_warnings(bp):
    """Advisory findings that never affect the VALID/INVALID verdict."""
    warnings = []
    _check_binding_type_fit(bp, warnings)
    _check_repeat_prose_columns(bp, warnings)
    _check_menu_chrome(bp, warnings)
    _check_existing_asset_announcement(bp, warnings)
    return warnings


def _check_menu_chrome(bp, warnings):
    """Advisory (soak-1 G4): a menu-bearing layout should carry its menu content
    so OMI's Chrome Batch Discipline can review shared chrome - never an error,
    because chrome content may legitimately be absent from the wireframe."""
    chrome = bp.get("app_chrome", {})
    if chrome.get("layout_block") in ("LayoutSideMenu", "LayoutTopMenu") and not chrome.get("menu"):
        warnings.append(
            "app_chrome: layout %r has no 'menu' content - OMI reviews shared "
            "chrome from the blueprint; add app_chrome.menu ([{label, active}]) "
            "if the wireframe shows page links" % chrome.get("layout_block")
        )


def _entity_decls(bp, source):
    for e in bp.get("entities", []):
        if not isinstance(e, dict):
            continue
        pk_name = pk_type = None
        attrs = {}
        for a in e.get("attributes", []):
            if not isinstance(a, dict) or "name" not in a:
                continue
            attrs[a["name"]] = (a.get("data_type"), bool(a.get("is_foreign_key")))
            if a.get("is_primary_key"):
                pk_name, pk_type = a["name"], a.get("data_type")
        records = e.get("records") if isinstance(e.get("records"), list) else None
        yield e.get("name"), {"source": source, "pk_name": pk_name,
                              "pk_type": pk_type, "attrs": attrs,
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
            pk_groups[(d["pk_name"], d["pk_type"])].append(d["source"])
        if len(pk_groups) > 1:
            parts = [
                f"{src} (PK {pk_name}:{pk_type})"
                for (pk_name, pk_type), srcs in pk_groups.items()
                for src in srcs
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
                    sig_groups[d["attrs"][attr]].append(d["source"])
            if len(sig_groups) > 1:
                parts = [
                    f"{src} {sig}"
                    for sig, srcs in sig_groups.items()
                    for src in srcs
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
    return errors


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


def _validate_one(bp_path, report_path, extra_seed_targets=None):
    """Existing single-file behaviour. Returns (exit_code, bp_or_None).

    extra_seed_targets is passed through to collect_errors for multi-path
    F-B2 evaluation; single-path callers omit it, so behaviour is unchanged.
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
    errors = collect_errors(bp, extra_seed_targets=extra_seed_targets)
    warnings = collect_warnings(bp)
    if errors:
        lines = [f"INVALID: {len(errors)} contract error(s)."] + [f"- {e}" for e in errors]
    else:
        lines = ["VALID: blueprint conforms to the OMI enriched-blueprint contract."]
    for w in warnings:
        lines.append(f"WARNING: {w}")
    report = "\n".join(lines) + "\n"
    report_path.write_text(report, encoding="utf-8")
    sys.stdout.write(report)
    return (1 if errors else 0), bp


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+",
                        help="One or more blueprint.json paths, or a directory")
    parser.add_argument("--report",
                        help="Report path (single-path only; default: beside the blueprint)")
    args = parser.parse_args(argv)

    paths = _expand_paths(args.paths)

    if not paths:
        sys.stdout.write(
            f"INVALID: no blueprint files found in: {' '.join(args.paths)}\n"
        )
        return 2

    # Single-path: identical to the historical behaviour, including exit code 2.
    if len(paths) == 1:
        bp_path = paths[0]
        report_path = Path(args.report) if args.report else bp_path.with_name("validation-report.txt")
        code, _ = _validate_one(bp_path, report_path)
        return code

    # Multi-path: per-file reports beside each, then the cross-blueprint pass.
    # First compute the union of seed targets (incoming FK-enum + declared
    # records) across every parseable blueprint, so F-B2 does not false-warn on
    # a static entity whose seed lives in a sibling blueprint (a legitimate
    # cross-blueprint projection).
    union_seed_targets = set()
    for bp_path in paths:
        try:
            _bp = json.loads(bp_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        union_seed_targets |= _fk_enum_targets(_bp) | _records_targets(_bp)

    any_error = False
    loaded = []
    for bp_path in paths:
        report_path = bp_path.with_name("validation-report.txt")
        code, bp = _validate_one(bp_path, report_path,
                                 extra_seed_targets=union_seed_targets)
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
    return 1 if any_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
