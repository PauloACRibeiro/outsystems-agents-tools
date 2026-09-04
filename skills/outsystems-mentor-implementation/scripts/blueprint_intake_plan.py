#!/usr/bin/env python3
"""Classify an enriched blueprint into create / modify / verify build actions.

Executable form of the intake rule in
references/odc-visual-source-enriched-blueprint.md section Existing-Asset Reuse
Channel (Phase 1 trial F-02): reused and existing elements fold into
modification or verification steps, never creation steps. Run it as a
pre-flight before prompt emission; a non-empty ``errors`` list means the
blueprint must go back to the producer uncorrected - do not invent a
replacement and do not fall back to creating the asset.

Usage:
    python3 blueprint_intake_plan.py <blueprint.json>

Prints the plan as JSON and exits 1 when errors are present.
"""

import json
import sys


def _leaf_regions(screen):
    """Yield (region, screen_name) for direct regions and group children."""
    name = screen.get("name", "?")
    for region in screen.get("main_content", []):
        if not isinstance(region, dict):
            continue
        if region.get("type") == "group":
            for item in region.get("items", []):
                if isinstance(item, dict) and item.get("type") != "group":
                    yield item, name
        else:
            yield region, name


IDENTIFIER_SUFFIX = " Identifier"

# `<X> Identifier` types the platform supplies rather than the app declaring
# them, so an FK onto one has no entities[] entry to point at and never should.
# `User Identifier` is in the Mentor Web data type reference outright, and ODC
# wires the relationship to its own `User` entity from the type alone
# (docs-odc building-apps/data/modeling/relationship/relationship-one-to-one.md);
# `Role Identifier` is the same shape (docs-odc reference/built-in-functions/
# roles.md). ODC's workflow system entities are deliberately NOT here: the
# platform publishes no `<X> Identifier` type for them, and an app that binds
# one adds it as a public element - which belongs in entities[] flagged
# exists: true, a route this guard already accepts.
PLATFORM_IDENTIFIER_TARGETS = frozenset({"User", "Role"})


def _fk_enum_seeded_targets(bp):
    """Entity names a foreign key declares by carrying a non-empty enum_values.

    Rule 4 of the Typed Create-Only Entities Sub-Schema: `<Target> Identifier`
    plus a non-empty enum_values list declares `<Target>` as a Static Entity
    seeded with those values, so entities[] is not the only declaration site.
    """
    seeded = set()
    for entity in bp.get("entities", []):
        if not isinstance(entity, dict):
            continue
        for attribute in entity.get("attributes", []) or []:
            if not isinstance(attribute, dict):
                continue
            if not attribute.get("is_foreign_key") or not attribute.get("enum_values"):
                continue
            data_type = (attribute.get("data_type") or "").strip()
            if data_type.endswith(IDENTIFIER_SUFFIX):
                seeded.add(data_type[: -len(IDENTIFIER_SUFFIX)].strip())
    return seeded


def _fk_target_errors(bp):
    """Foreign keys whose target entity nothing in the blueprint declares.

    Rule 5 of the Typed Create-Only Entities Sub-Schema
    (references/odc-visual-source-enriched-blueprint.md): "When `enum_values` is
    `null`, require the target to be another declared create-only entity."
    The sub-schema closes with "Do not invent a missing target entity ... stop
    prompt emission and return the blueprint for correction" - and `errors` is
    that stop, because render_build_brief refuses a blueprint the plan owes back.

    Until this check existed the rule was prose only. The two neighbouring cases
    both failed loud - an entity a screen names but nothing declares is marked
    NOT DECLARED by the renderer, a static-entity target is resolved by its
    enum_values - so a plain foreign key was the one declaration route with
    neither resolution nor guard, and the brief told Mentor to create a
    relationship to an entity nothing asks to be created.
    """
    entities = [e for e in bp.get("entities", []) if isinstance(e, dict)]
    declared = {e.get("name") for e in entities}
    seeded = _fk_enum_seeded_targets(bp)
    errors = []
    for entity in entities:
        owner = entity.get("name", "?")
        for attribute in entity.get("attributes", []) or []:
            if not isinstance(attribute, dict):
                continue
            if attribute.get("is_foreign_key") is not True:
                continue
            data_type = (attribute.get("data_type") or "").strip()
            if not data_type.endswith(IDENTIFIER_SUFFIX):
                continue
            target = data_type[: -len(IDENTIFIER_SUFFIX)].strip()
            if not target or target in declared or target in seeded \
                    or target in PLATFORM_IDENTIFIER_TARGETS:
                continue
            errors.append(
                f"entity '{owner}' attribute '{attribute.get('name', '?')}' is a "
                f"foreign key to '{target}' via data_type {data_type!r}, but "
                f"'{target}' is declared nowhere - no entities[] entry (flag "
                "exists: true if it is already in the target app) and no "
                "enum_values seeding it as a static entity; do not invent a "
                "missing target entity - return to producer"
            )
    return errors


def _reused_block(region):
    reuse = region.get("reuse")
    if not isinstance(reuse, dict):
        return None
    block = reuse.get("block")
    return block.strip() if isinstance(block, str) and block.strip() else None


def build_intake_plan(bp):
    """Return the action plan the intake rule mandates for this blueprint.

    ``creations`` lists what the build creates, ``modifications`` what it
    places/binds on existing assets, ``verifications`` what it checks in the
    target app before relying on it. ``errors`` carries producer-correction
    conditions; when non-empty the plan must not be executed.
    """
    plan = {
        "creations": {"entities": [], "blocks": [], "custom_blocks": []},
        "modifications": [],
        "verifications": [],
        "errors": [],
    }
    existing_app = bp.get("target_context", {}).get("target_mode") == "existing-app"
    mode = bp.get("target_context", {}).get("target_mode")

    for entity in bp.get("entities", []):
        if not isinstance(entity, dict):
            continue
        name = entity.get("name", "?")
        if entity.get("exists") is True:
            if not existing_app:
                plan["errors"].append(
                    f"entity '{name}' is flagged exists: true under target_mode "
                    f"{mode!r} - return to producer"
                )
                continue
            attributes = entity.get("attributes", []) or []
            new_attributes = [
                a for a in attributes if isinstance(a, dict) and a.get("create") is True
            ]
            verify_names = [
                a.get("name", "?") for a in attributes
                if isinstance(a, dict) and a.get("create") is not True
            ]
            verification = {
                "kind": "entity", "name": name,
                "verify": "entity and declared attributes exist in the target app",
                "attributes": verify_names,
            }
            if new_attributes:
                verification["verify"] = (
                    "entity and declared attributes exist in the target app, "
                    "excluding the attributes below which are ADDED to it"
                )
            plan["verifications"].append(verification)
            for attribute in new_attributes:
                plan["modifications"].append(
                    {"kind": "add-attribute", "entity": name,
                     "attribute": attribute.get("name", "?"),
                     "data_type": attribute.get("data_type", "?")}
                )
        else:
            plan["creations"]["entities"].append(name)

    plan["errors"].extend(_fk_target_errors(bp))

    declared_blocks = [
        b.get("name", "?") for b in bp.get("blocks", []) if isinstance(b, dict)
    ]
    plan["creations"]["blocks"] = list(declared_blocks)

    for screen in bp.get("screens", []):
        for region, sname in _leaf_regions(screen):
            label = region.get("name") or region.get("id") or "?"
            block = _reused_block(region)
            if "reuse" in region and not block:
                plan["errors"].append(
                    f"screen '{sname}' region '{label}': reuse without a usable "
                    "reuse.block name - return to producer"
                )
                continue
            if block:
                if (region.get("outsystems_hints") or {}).get("block") or \
                        region.get("custom_block_needed"):
                    plan["errors"].append(
                        f"screen '{sname}' region '{label}': reuse.block {block!r} "
                        "coexists with outsystems_hints.block or custom_block_needed "
                        "- return to producer"
                    )
                    continue
                if not existing_app:
                    plan["errors"].append(
                        f"screen '{sname}' region '{label}': reuse.block {block!r} "
                        f"under target_mode {mode!r} - return to producer"
                    )
                    continue
                if block in declared_blocks or block.rsplit("/", 1)[-1] in declared_blocks:
                    plan["errors"].append(
                        f"reused block {block!r} also appears in blocks[] - that array "
                        "is the list of blocks this build CREATES; return to producer"
                    )
                    continue
                plan["modifications"].append(
                    {"kind": "place-and-bind", "screen": sname,
                     "region": label, "block": block}
                )
            elif region.get("custom_block_needed"):
                plan["creations"]["custom_blocks"].append(
                    {"screen": sname, "region": label}
                )

    return plan


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        bp = json.load(fh)
    plan = build_intake_plan(bp)
    print(json.dumps(plan, indent=2))
    return 1 if plan["errors"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
