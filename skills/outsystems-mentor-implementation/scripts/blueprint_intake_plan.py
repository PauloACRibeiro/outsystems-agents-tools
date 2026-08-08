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
            plan["verifications"].append(
                {"kind": "entity", "name": name,
                 "verify": "entity and declared attributes exist in the target app"}
            )
        else:
            plan["creations"]["entities"].append(name)

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
