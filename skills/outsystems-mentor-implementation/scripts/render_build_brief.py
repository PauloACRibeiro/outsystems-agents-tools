#!/usr/bin/env python3
"""Render an enriched blueprint into per-screen build-facts briefs.

Deterministic form of the derivable half of the Visual-Source UI Prompt Packet
(``references/odc-visual-source-ui-discipline.md``). That section is twelve
numbered instructions telling the model to derive the packet in prose before
every emission; items 1, 4, 7 and 9 are recoverable from the blueprint by
computation, so re-deriving them by reading is work repeated once per screen
with a fresh chance of a different answer each time.

What it buys is **derived facts in a uniform shape**, not id resolution - the
blueprint is name-based and no internal id exists to leak. Concretely:

* the entity-touch closure per screen - an entity reached only through
  ``data_source.joins`` or a content ``binds`` is as much a producer for that
  screen as one named in ``screens[].entities``, and reading finds it only if
  the reader looks in all three places every time;
* the typed attribute projection scoped to exactly those entities, so DATA FLOW
  is written against declared types rather than remembered ones;
* the per-screen build classification, delegated to
  ``blueprint_intake_plan.build_intake_plan`` rather than judged again here;
* one section list that does not vary with the data, so two screens' briefs are
  diffable and an absent producer is visible as ``(none)`` rather than as a
  section nobody wrote.

**Facts only.** Component-selection heuristics, the four-part section contract,
the state plan, polish acceptance and the gotcha review stay authored - they are
judgement, and a renderer that guessed them would be inventing requirements. App
chrome is deliberately not rendered here either: it is owned by Chrome Batch
Discipline and gated by ``scripts/check_chrome_coverage.py``, and a second
emitter for it would be exactly the two-owners drift this script exists to
remove.

The renderer refuses to emit anything for a blueprint the intake plan says is
owed back to its producer. Rendering it would launder a return-to-producer
condition into a build instruction.

Usage:
    python3 render_build_brief.py <blueprint.json> [--screen NAME]
                                  [--inventory <screen-inventory.json>]
"""

import argparse
import sys
from pathlib import Path

from blueprint_intake_plan import build_intake_plan
from json_file_io import JSONFileError, read_json_file

NONE = "(none)"

AUTHORED = [
    "component-selection heuristics, the four-part section contract "
    "(VISUAL LAYOUT / DATA FLOW / FUNCTIONAL BEHAVIOR / PRESENTATION ORDER),",
    "the state plan, polish acceptance, and the gotcha review.",
    "See references/odc-visual-source-ui-discipline.md - this brief is the "
    "derivable half only.",
    "App chrome is not rendered here: it is owned by Chrome Batch Discipline "
    "and gated by",
    "scripts/check_chrome_coverage.py.",
]


class BlueprintNotRenderable(Exception):
    """The intake plan owes this blueprint back to its producer."""


def _text(value):
    return value.strip() if isinstance(value, str) and value.strip() else None


def _dict(value):
    return value if isinstance(value, dict) else {}


def _list(value):
    return value if isinstance(value, list) else []


def _walk(regions, prefix):
    for index, region in enumerate(regions, start=1):
        if not isinstance(region, dict):
            continue
        number = f"{prefix}{index}"
        yield number, region, region.get("column")
        if region.get("type") == "group":
            yield from _walk(_list(region.get("items")), f"{number}.")


def walk_regions(screen):
    """Yield ``(number, region, column)`` for every declared region.

    Groups keep their place in the ordering and their children are numbered
    beneath them, so the printed tree matches the declared tree. ``column`` is
    the child's adaptive-block placeholder, absent on a top-level region.

    The walk recurses rather than stopping at one level. The schema expects
    group ``items`` to be leaf sections, so a nested group is out of contract -
    but dropping it silently would remove a declared region from a brief whose
    whole claim is that it inventories them, which is the worse failure.
    """
    yield from _walk(_list(screen.get("main_content")), "")


def touched_entities(screen):
    """Entity names this screen binds, by any of the three declared routes."""
    names = []
    seen = set()

    def add(value):
        name = _text(value)
        if name and name not in seen:
            seen.add(name)
            names.append(name)

    for name in _list(screen.get("entities")):
        add(name)

    def scan_content(items):
        for item in _list(items):
            if isinstance(item, dict):
                add(_dict(item.get("binds")).get("entity"))

    for _number, region, _column in walk_regions(screen):
        source = _dict(region.get("data_source"))
        add(source.get("entity"))
        for join in _list(source.get("joins")):
            add(join)
        scan_content(region.get("content"))
    for popup in _list(screen.get("popups")):
        if isinstance(popup, dict):
            scan_content(popup.get("content"))
    return names


def _entity_index(blueprint):
    index = {}
    for entity in _list(blueprint.get("entities")):
        if isinstance(entity, dict):
            name = _text(entity.get("name"))
            if name:
                index[name] = entity
    return index


def _attribute_line(attribute):
    if not isinstance(attribute, dict):
        return f"      {attribute}"
    name = _text(attribute.get("name")) or "?"
    data_type = _text(attribute.get("data_type")) or "(no data_type declared)"
    roles = []
    if attribute.get("is_primary_key") is True:
        roles.append("primary key")
    if attribute.get("is_foreign_key") is True:
        roles.append("foreign key")
    line = f"      {name}: {data_type}"
    if roles:
        line += f" ({', '.join(roles)})"
    enum_values = [v for v in _list(attribute.get("enum_values")) if _text(str(v))]
    if enum_values:
        line += f" [static entity seed: {', '.join(str(v) for v in enum_values)}]"
    return line


def static_entity_targets(blueprint):
    """Static entities declared by a foreign key rather than by an entry.

    ``entities[]`` is not the only declaration site. A foreign-key attribute
    typed ``<Target> Identifier`` and carrying a non-empty ``enum_values`` list
    declares ``<Target>`` as a Static Entity seeded with those values - rules 3
    and 4 of the Typed Create-Only Entities Sub-Schema in
    ``references/odc-visual-source-ui-discipline.md``'s companion reference.
    Reading only ``entities[]`` reports the canonical shipped asset's
    ``WorkItemStatus`` as undeclared, which would send a correct blueprint back
    to its producer.

    Returns ``{target: (seed values, owning attribute)}`` in discovery order.
    """
    suffix = " Identifier"
    targets = {}
    for entity in _list(blueprint.get("entities")):
        if not isinstance(entity, dict):
            continue
        owner = _text(entity.get("name")) or "?"
        for attribute in _list(entity.get("attributes")):
            if not isinstance(attribute, dict):
                continue
            if attribute.get("is_foreign_key") is not True:
                continue
            values = [str(v) for v in _list(attribute.get("enum_values")) if str(v).strip()]
            data_type = _text(attribute.get("data_type")) or ""
            if not values or not data_type.endswith(suffix):
                continue
            target = data_type[: -len(suffix)].strip()
            if target and target not in targets:
                targets[target] = (values, f"{owner}.{_text(attribute.get('name'))}")
    return targets


def _entity_lines(blueprint, screen, plan):
    declared = _entity_index(blueprint)
    static = static_entity_targets(blueprint)
    verified = {v.get("name") for v in plan["verifications"] if v.get("kind") == "entity"}
    touched = touched_entities(screen)
    ordered = [n for n in declared if n in touched]
    ordered += [n for n in static if n in touched and n not in declared]
    ordered += [n for n in touched if n not in declared and n not in static]

    lines = []
    for name in ordered:
        entity = declared.get(name)
        if entity is None and name in static:
            values, owner = static[name]
            lines.append(
                f"  - {name} [create static entity - declared by {owner} "
                "enum_values, not by an entities[] entry]"
            )
            lines.append(f"      records: {', '.join(values)}")
            continue
        if entity is None:
            lines.append(
                f"  - {name} [NOT DECLARED in entities[] - a screen names it, "
                "nothing declares it; return to producer rather than inventing "
                "a shape]"
            )
            continue
        status = "verify in target app" if name in verified else "create"
        lines.append(f"  - {name} [{status}]")
        attributes = _list(entity.get("attributes"))
        if not attributes:
            lines.append("      (no attributes declared)")
        for attribute in attributes:
            lines.append(_attribute_line(attribute))
    return lines or [f"  {NONE}"]


def _content_line(item):
    if isinstance(item, str):
        return _text(item)
    if not isinstance(item, dict):
        return None
    parts = []
    element = _text(item.get("element"))
    label = _text(item.get("label"))
    parts.append(element or label or "(unnamed content item)")
    if element and label:
        parts.append(f'label "{label}"')
    data = _text(item.get("data"))
    if data:
        parts.append(f"data: {data}")
    binds = _dict(item.get("binds"))
    entity, attribute = _text(binds.get("entity")), _text(binds.get("attribute"))
    if entity:
        parts.append(f"binds: {entity}.{attribute}" if attribute else f"binds: {entity}")
    action = _text(item.get("action"))
    if action:
        parts.append(f"action: {action}")
    return " | ".join(parts)


def _region_lines(screen):
    lines = []
    for number, region, column in walk_regions(screen):
        indent = "  " + "  " * number.count(".")
        head = [f"{indent}{number}. {_text(region.get('name')) or '(unnamed region)'}"]
        identifier = _text(region.get("id"))
        if identifier:
            head.append(f"[id {identifier}]")
        if column is not None:
            head.append(f"column {column}")
        if region.get("type") == "group":
            head.append(f"group columns={_text(region.get('columns')) or '(undeclared)'}")
        block = _text(_dict(region.get("outsystems_hints")).get("block"))
        if block:
            head.append(f"block={block}")
        reuse = _text(_dict(region.get("reuse")).get("block"))
        if reuse:
            head.append(f"reuse={reuse}")
        if region.get("custom_block_needed"):
            head.append("custom block needed")
        extended = _text(_dict(region.get("outsystems_hints")).get("extended_class"))
        if extended:
            head.append(f"class={extended}")
        lines.append(" ".join(head))

        body = indent + "     "
        source = _dict(region.get("data_source"))
        if source:
            facts = [f"entity {_text(source.get('entity')) or '(undeclared)'}"]
            joins = [_text(j) for j in _list(source.get("joins")) if _text(j)]
            if joins:
                facts.append(f"joins {', '.join(joins)}")
            for key in ("filter", "sort"):
                value = _text(source.get(key))
                if value:
                    facts.append(f'{key} "{value}"')
            if source.get("max_records") is not None:
                facts.append(f"max_records {source['max_records']}")
            lines.append(f"{body}data: {'; '.join(facts)}")
        for item in _list(region.get("content")):
            rendered = _content_line(item)
            if rendered:
                lines.append(f"{body}content: {rendered}")
        conditional = _text(region.get("conditional_rendering"))
        if conditional:
            lines.append(f"{body}conditional: {conditional}")
    return lines or [f"  {NONE}"]


def _action_lines(screen_name, plan):
    lines = []
    for modification in plan["modifications"]:
        if modification.get("screen") == screen_name:
            lines.append(
                f"  - place existing block {modification.get('block')} in region "
                f"\"{modification.get('region')}\" (verify it exists before binding; "
                "do not create it)"
            )
    for custom in plan["creations"]["custom_blocks"]:
        if custom.get("screen") == screen_name:
            lines.append(
                f"  - create custom block for region \"{custom.get('region')}\""
            )
    return lines or [f"  {NONE}"]


def _navigation_lines(screen_name, inventory):
    if inventory is None:
        return [
            "  (no inventory supplied - pass --inventory <screen-inventory.json> "
            "to render navigation; the blueprint does not carry it)"
        ]
    known = {
        _text(s.get("name"))
        for s in _list(inventory.get("screens"))
        if isinstance(s, dict)
    }
    if screen_name not in known:
        return [f'  (screen "{screen_name}" is not in the supplied inventory)']
    lines = []
    for edge in _list(inventory.get("navigation")):
        if not isinstance(edge, dict):
            continue
        trigger = _text(edge.get("trigger")) or "(no trigger declared)"
        payload = _text(edge.get("payload"))
        carrying = f" carrying {payload}" if payload else ""
        if _text(edge.get("from")) == screen_name:
            lines.append(f"  - out: -> {_text(edge.get('to'))} on {trigger}{carrying}")
        elif _text(edge.get("to")) == screen_name:
            lines.append(f"  - in:  <- {_text(edge.get('from'))} on {trigger}{carrying}")
    return lines or [f"  {NONE}"]


def _permissions_summary(screen):
    permissions = _dict(screen.get("permissions"))
    if not permissions:
        return NONE
    parts = []
    authentication = _text(permissions.get("authentication"))
    if authentication:
        parts.append(authentication)
    roles = _dict(permissions.get("roles"))
    if roles:
        parts.append(
            "roles " + ", ".join(f"{k}={v}" for k, v in sorted(roles.items()))
        )
    return "; ".join(parts) or NONE


def _screens_by_name(blueprint):
    return {
        _text(s.get("name")): s
        for s in _list(blueprint.get("screens"))
        if isinstance(s, dict) and _text(s.get("name"))
    }


def _require_renderable(blueprint):
    plan = build_intake_plan(blueprint)
    if plan["errors"]:
        raise BlueprintNotRenderable(
            "blueprint is owed back to its producer; no brief rendered:\n"
            + "\n".join(f"  - {e}" for e in plan["errors"])
        )
    return plan


def render_screen_brief(blueprint, screen_name, inventory=None, plan=None):
    """Render one screen's build-facts brief, or raise if it cannot be rendered."""
    if plan is None:
        plan = _require_renderable(blueprint)
    screens = _screens_by_name(blueprint)
    if screen_name not in screens:
        known = ", ".join(screens) or "(none)"
        raise KeyError(f"no screen named {screen_name!r} in this blueprint. Known: {known}")
    screen = screens[screen_name]
    context = _dict(blueprint.get("target_context"))

    lines = [
        f"BUILD BRIEF: {screen_name}",
        f"app: {_text(blueprint.get('name')) or NONE}",
        f"target mode: {_text(context.get('target_mode')) or NONE}",
        f"screen type: {_text(screen.get('type')) or NONE}",
        f"template: {_text(screen.get('template')) or NONE}",
        f"title: {_text(screen.get('title')) or NONE}",
        f"subtitle: {_text(screen.get('subtitle')) or NONE}",
        f"purpose: {_text(screen.get('description')) or NONE}",
        f"permissions: {_permissions_summary(screen)}",
        "",
        "entities this screen touches:",
    ]
    lines += _entity_lines(blueprint, screen, plan)
    lines += ["", "regions in order:"]
    lines += _region_lines(screen)
    # Named for what it covers: a bare "build actions" heading reading "(none)"
    # on a greenfield screen invites the reading that the screen needs no work,
    # when every element on it is a create carried by the entity flags above.
    lines += ["", "build actions for this screen (existing-asset placements and custom blocks):"]
    lines += _action_lines(screen_name, plan)
    lines += ["", "popups:"]
    popups = [
        f"  - {_text(p.get('name')) or '(unnamed popup)'}"
        + (f" (trigger: {_text(p.get('trigger'))})" if _text(p.get("trigger")) else "")
        for p in _list(screen.get("popups"))
        if isinstance(p, dict)
    ]
    lines += popups or [f"  {NONE}"]
    lines += ["", "navigation (from screen inventory):"]
    lines += _navigation_lines(screen_name, inventory)
    lines += ["", "these stay authored - the renderer emits facts only:"]
    lines += [f"  {line}" for line in AUTHORED]
    return "\n".join(lines) + "\n"


def render_all(blueprint, inventory=None):
    """Render every declared screen, in declared order."""
    plan = _require_renderable(blueprint)
    briefs = [
        render_screen_brief(blueprint, name, inventory=inventory, plan=plan)
        for name in _screens_by_name(blueprint)
    ]
    return "\n".join(briefs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("blueprint", type=Path, help="enriched blueprint JSON")
    parser.add_argument("--screen", help="render only this screen")
    parser.add_argument(
        "--inventory",
        type=Path,
        help="screen-inventory JSON supplying navigation edges",
    )
    args = parser.parse_args(argv)

    try:
        blueprint = read_json_file(args.blueprint)
        inventory = read_json_file(args.inventory) if args.inventory else None
    except JSONFileError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    try:
        if args.screen:
            output = render_screen_brief(blueprint, args.screen, inventory=inventory)
        else:
            output = render_all(blueprint, inventory=inventory)
            if not output.strip():
                # Printing nothing and exiting 0 would report success for a
                # blueprint that produced no brief at all.
                print(
                    f"{args.blueprint}: no screens declared; nothing to render",
                    file=sys.stderr,
                )
                return 2
    except BlueprintNotRenderable as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except KeyError as exc:
        print(str(exc).strip('"'), file=sys.stderr)
        return 2

    print(output, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
