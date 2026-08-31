#!/usr/bin/env python3
"""Validate a screen-inventory.json against the screen-inventory contract.

The inventory is the shared artifact N per-screen `outsystems-ui-design` runs
read from: the screen list, each screen's behaviour, the one chrome decision,
and the cross-screen navigation. Its vocabulary is deliberately borrowed from
downstream so the loop closes:

- `app_chrome.layout_block` / `app_title` copy verbatim into every blueprint;
  the menu translates - the inventory records `{label, target}`, a blueprint
  records `{label, active}`, and `blueprint_menu_for_screen` performs that
  translation so OUD's cross-blueprint chrome pass (which compares the label
  sequence and ignores `active`) succeeds by construction.
- `assertions` accepts only the shared assertion vocabulary (links, buttons,
  inputs) that OUD's validator recomputes and OMI's `recompute_assertions.py`
  re-checks against the built model. Unknown keys are an error on all three.
- `archetype` is one of the 14 OUD screen archetypes.
- `candidates[].source_ref` cites requirement IDs in the grammar
  outsystems-plan-to-mentor owns, so the requirement->screen binding is
  recorded once here instead of being invented a second time in the capability
  plan's Traceability table.

Exit codes: 0 valid, 1 contract errors, 2 unreadable input.
"""
import json
import re
import sys
from pathlib import Path

# TARGET PRODUCT: OutSystems Developer Cloud (ODC).
# Shared verbatim with outsystems-ui-design's LAYOUT_BLOCKS /
# MENU_BEARING_LAYOUTS - see that file for the grounding, and
# test_layout_vocabulary_matches_the_design_validator for the drift gate that
# fails when these two lists stop agreeing.
LAYOUTS = (
    "LayoutSideMenu", "LayoutTopMenu", "LayoutBlank", "LayoutBase", "LayoutBaseSection",
)
MENU_BEARING = ("LayoutSideMenu", "LayoutTopMenu", "LayoutBase")

# The 14 screen archetypes outsystems-ui-design confirms at its Step 1. Keeping
# one vocabulary means the inventory's archetype IS the design run's Step 1
# answer rather than a second opinion the operator has to reconcile.
ARCHETYPES = (
    "calendar", "dashboard", "detail-view", "edit-form", "gallery-grid",
    "inbox-notifications", "instructional", "kanban", "list-table",
    "map-view", "master-detail", "settings", "timeline", "wizard",
)

# OPTIONAL refinement of archetype: the ODC block the screen's main collection
# is laid out in, named in outsystems-ui-design's block vocabulary
# (references/blocks-index.md), never the App Generator's spec-level pattern
# names. Declaring it takes the list-vs-gallery-vs-cards decision once for the
# whole app; leaving it absent is the normal answer on any screen that lays out
# no collection.
PRESENTATION_PATTERNS = (
    "TableRecords", "Gallery", "IList+Card", "MasterDetail", "Accordion",
)

# Shared with outsystems-ui-design's _ASSERTION_WIDGETS and OMI's
# recompute_assertions.py. Do not extend without changing all three.
ASSERTION_KEYS = ("links", "buttons", "inputs")

# --- record actions: where a list screen's create/edit/detail happens --------
#
# The gap this closes (2026-08-30): two apps shipped list screens whose "add"
# and per-row "edit" controls pointed at screens nobody had put in the
# inventory. The controls were built, rendered, and did nothing; a human found
# them by clicking. The first app lost four screens that way, the one before it
# two. Nothing upstream was wrong-shaped: `navigation` endpoints are already
# held to real screens, so a WRITTEN edge can never dangle. The edge was never
# written, and an absent edge is what no check could see.
#
# `archetype` values that lay out one row per record someone acts on. Narrower
# than "shows a collection" on purpose, and measured on three real inventories:
# `master-detail` is excluded because its editor is on the same screen by
# definition, and `dashboard` because it summarises rather than lists. Widening
# to the nine collection-ish archetypes fired on two worked-example screens
# that were correct - the accusing-correct-rows shape AH-2026-08-26-015 removed
# a warning for. Read-only use of the borrowed enum; nothing here extends it.
RECORD_LIST_ARCHETYPES = ("list-table", "gallery-grid")

# The record actions that need somewhere to happen. Bounded deliberately.
RECORD_ACTIONS = ("create", "edit", "detail")

# The archetypes each action legitimately opens. An outgoing edge into one of
# these discharges that action WHATEVER its trigger says, and the route is not
# optional: a trigger is prose describing a gesture ("select an item row", "the
# + button") and no bounded vocabulary covers gestures. Measured - demanding an
# `open`-shaped trigger for `detail` accused four inventories in this repo
# whose row-open was already correctly closed by a real edge to a real screen,
# which is the accusing-correct-rows shape AH-2026-08-26-015 deleted a warning
# for. Structural, so wording cannot defeat it and wording cannot satisfy it.
RECORD_ACTION_DESTINATIONS = {
    "create": ("edit-form", "wizard"),
    "edit": ("edit-form", "wizard"),
    "detail": ("detail-view",),
}

# The two resolutions that answer "where" without naming a screen.
RECORD_ACTION_INLINE = "inline"
RECORD_ACTION_OUT_OF_SCOPE = "out-of-scope"

# The verb that OPENS a key_interaction is the action it offers: interactions
# are authored as imperative phrases ("Create a dish in one of the five
# sections"), so the first word is the action. Narrative `behavior` prose is
# deliberately NOT read - scanning it matched "land on the run it created" and
# invented a create form that was never there, and on the evidence app it
# actively asserted the wrong answer ("Dishes are created, edited and retired
# here" on a screen whose build produced navigation controls). Portuguese sits
# beside English because that inventory described a Portuguese UI and the next
# one may be written in it.
RECORD_ACTION_OPENERS = (
    ("create", r"(create|add|new|register|criar|adicionar|novo|nova|registar)"),
    ("edit", r"(edit|update|change|rename|configure|editar|alterar|"
             r"atualizar|configurar)"),
    ("detail", r"(open|view|inspect|abrir|ver|consultar)"),
)

# The requirement-ID grammar. outsystems-plan-to-mentor OWNS it
# (scripts/check_requirement_coverage.py, ID_PATTERN); this is a deliberate
# duplicate rather than a shared module, because the two skills ship in
# different packs and no cross-skill Python import exists - sharing would buy
# a packaging dependency to deduplicate one line. Duplication is only safe
# with a gate, so test_requirement_id_pattern_matches_plan_to_mentors fails
# when the two copies diverge, and unlike the layout drift test it does NOT
# skip when the sibling skill is absent. Change both together.
REQUIREMENT_ID_PATTERN = re.compile(
    r"\b(?:BR|UC|C)-(?:(?:[A-Z][A-Z0-9]*-)*\d{3}|[A-Z]+\d{2,3})\b")

SOURCE_KINDS = ("requirements-doc", "existing-app-modernization")

# NO template-screen warning lives here, deliberately. A `requirements-doc`
# inventory says nothing about what its target shell is - `source.kind` splits
# greenfield from modernization, not Web from Mobile from an intentionally
# blank shell - so a name-keyed warning on Login/UserProfile fires on targets
# where the template screens do not exist and the row is correct. Codex
# required this removal on AH-2026-08-26-015 (2026-08-26) after it shipped as
# an advisory warning. Gating it needs a target-shell fact this artifact does
# not decide, and coining one here would fork a contract for a single warning.
# The baseline is guidance in SKILL.md until such a fact exists for its own
# reasons.
# `mapped` and `dissolved` are both in-scope: the capability IS built, either as
# its own screen or inside another one. The three below are the excluded-scope
# channel - the candidate is not in this build at all - and they are BORROWED
# VERBATIM from outsystems-plan-to-mentor's closed requirement-disposition
# vocabulary (TERMINAL_DISPOSITIONS in check_requirement_coverage.py), not
# invented here. One word, one meaning, so an excluded id keeps it when it
# travels to that skill's Requirement Dispositions table and on to Section 8 of
# the Mentor spec. Do not add a fourth without adding it there -
# test_excluded_dispositions_match_the_coverage_checker is the drift gate. Each
# needs a stated reason, which holds by construction: `rationale` is already
# required on every candidate.
EXCLUDED_DISPOSITIONS = ("deferred", "out-of-scope", "accepted-risk")
DISPOSITIONS = ("mapped", "dissolved") + EXCLUDED_DISPOSITIONS
BINDING_KINDS = ("entity", "action")

# An open decision is one this skill is entitled to leave undecided, so the
# taxonomy is exactly this skill's own scope and nothing wider: a decision
# about block choice, visual design or logic belongs to outsystems-ui-design or
# the capability plan, and recording it here would create a second declaration
# site those skills never read. Each category names a part of this artifact:
#   candidate-disposition  hard gate 2 - is this candidate a screen at all
#   screen-fusion          hard gate 5 - are these one screen or two
#   chrome                 hard gate 3 - the one layout/title/menu decision
#   navigation             R7 - does this edge exist and what does it carry
#   binding                R6/R8 - which entity or action a screen binds to
OPEN_DECISION_CATEGORIES = (
    "candidate-disposition", "screen-fusion", "chrome", "navigation", "binding",
)
DECISION_STATUSES = ("open", "resolved")

# Fewer than two options is not a decision; more than four is not one either -
# the point of the slot is a choice a reviewer can actually take in one pass.
MIN_OPTIONS, MAX_OPTIONS = 2, 4

TOP_LEVEL = ("schema_version", "app_name", "source", "app_chrome",
             "candidates", "screens", "navigation")


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


def placeholder_fields(inv):
    """The NAMED field set the placeholder ban covers.

    EXCLUDED on purpose: `source.grounding_notes` - the channel for recording
    what is not yet settled. A deferral note belongs there.
    """
    if not isinstance(inv, dict):
        return
    for key in ("app_name", "design_tokens_source"):
        yield from _pf(key, inv.get(key))

    source = inv.get("source")
    if isinstance(source, dict):
        yield from _pf("source.refs", source.get("refs"))

    chrome = inv.get("app_chrome")
    if isinstance(chrome, dict):
        for key in ("layout_block", "app_title"):
            yield from _pf(f"app_chrome.{key}", chrome.get(key))
        for i, entry in enumerate(chrome.get("menu", []) or []):
            if isinstance(entry, dict):
                for key in ("label", "target"):
                    yield from _pf(f"app_chrome.menu[{i}].{key}", entry.get(key))

    for i, cand in enumerate(inv.get("candidates", []) or []):
        if isinstance(cand, dict):
            for key in ("id", "source_ref", "rationale", "dissolved_into",
                        "resolves_to"):
                yield from _pf(f"candidates[{i}].{key}", cand.get(key))

    for i, screen in enumerate(inv.get("screens", []) or []):
        if not isinstance(screen, dict):
            continue
        for key in ("name", "purpose", "archetype", "behavior",
                    "key_interactions", "accepts"):
            yield from _pf(f"screens[{i}].{key}", screen.get(key))
        for j, binding in enumerate(screen.get("data_bindings", []) or []):
            if isinstance(binding, dict):
                for key in ("name", "usage", "behavior_notes"):
                    yield from _pf(f"screens[{i}].data_bindings[{j}].{key}",
                                   binding.get(key))

    for i, edge in enumerate(inv.get("navigation", []) or []):
        if isinstance(edge, dict):
            for key in ("from", "to", "trigger", "payload"):
                yield from _pf(f"navigation[{i}].{key}", edge.get(key))


def _check_placeholders(inv, errors):
    """Fail-closed: an unresolved marker in a gate-bearing field is an error."""
    for path, text in placeholder_fields(inv):
        marker = placeholder_in(text)
        if marker:
            errors.append(
                f"{path}: active placeholder {marker!r} - a gate-bearing field "
                "must carry the real value, not a marker to resolve later"
            )


ACCESS_CLASSIFICATIONS = (
    "preview_public", "public", "authenticated", "role", "unresolved",
)


def _check_access_classification(inv, errors):
    """The field is optional; once declared it is held to its own rules.

    `unresolved` blocks the build rather than defaulting to public, and a
    `role` screen must name the role, because the role's existence is a
    precondition for creating the screen and an unnamed role cannot be checked.
    """
    for name, screen in _screens_by_name(inv).items():
        access = screen.get("access_classification")
        if access is None:
            # An orphaned role name is the one case an absent classification
            # still has to answer for: it asserts a gate nothing declared, so
            # it reads as decided when nothing was.
            if _is_text(screen.get("access_role")):
                errors.append(
                    f"screen '{name}': access_role is set without an "
                    "access_classification - a role name only carries meaning "
                    "on a 'role' screen, and on its own it implies a gate the "
                    "inventory never declared")
            continue
        if access not in ACCESS_CLASSIFICATIONS:
            errors.append(
                f"screen '{name}': access_classification {access!r} is not one "
                f"of {', '.join(ACCESS_CLASSIFICATIONS)}")
            continue
        if access == "unresolved":
            errors.append(
                f"screen '{name}': access_classification is 'unresolved' - who "
                "the screen is for was never decided, so it must not be built. "
                "Resolve it with the user; the writer default is never the "
                "policy")
        if access == "role" and not _is_text(screen.get("access_role")):
            errors.append(
                f"screen '{name}': access_classification 'role' requires "
                "access_role naming the gating role - the role's existence is "
                "a precondition for creating the screen, and an unnamed role "
                "cannot be verified")
        if access != "role" and _is_text(screen.get("access_role")):
            errors.append(
                f"screen '{name}': access_role is set but "
                f"access_classification is {access!r} - a role name only "
                "carries meaning on a 'role' screen")


def _is_text(value):
    return isinstance(value, str) and value.strip() != ""


def _as_list(value):
    """Malformed input reports its own error elsewhere; here it must not crash."""
    return value if isinstance(value, list) else []


def _as_dict(value):
    return value if isinstance(value, dict) else {}


def _screens_by_name(inv):
    return {
        s["name"]: s for s in _as_list(inv.get("screens"))
        if isinstance(s, dict) and _is_text(s.get("name"))
    }


def _check_source(inv, errors):
    source = inv.get("source")
    if not isinstance(source, dict):
        errors.append("source: must be an object with 'kind' and 'refs'")
        return
    kind = source.get("kind")
    if kind not in SOURCE_KINDS:
        errors.append(
            f"source.kind: {kind!r} must be one of {', '.join(SOURCE_KINDS)}")
    refs = source.get("refs")
    if not isinstance(refs, list) or not refs or not all(_is_text(r) for r in refs):
        errors.append(
            "source.refs: at least one non-empty reference to the document(s) "
            "this inventory was derived from - an inventory with no traceable "
            "source cannot be audited against its requirements")


def _check_chrome(inv, screen_names, errors):
    """One app, one chrome. These are the fields OUD compares across blueprints."""
    chrome = inv.get("app_chrome")
    if not isinstance(chrome, dict):
        errors.append("app_chrome: must be an object")
        return
    layout = chrome.get("layout_block")
    if layout not in LAYOUTS:
        errors.append(
            f"app_chrome.layout_block: {layout!r} must be exactly one of "
            f"{', '.join(LAYOUTS)} - the chrome decision is made once for the "
            "whole app and copied into every blueprint")
    if not _is_text(chrome.get("app_title")):
        errors.append("app_chrome.app_title: required non-empty string")

    menu = chrome.get("menu", [])
    if not isinstance(menu, list):
        errors.append("app_chrome.menu: must be a list of {label, target}")
        return
    if layout in MENU_BEARING and not menu:
        errors.append(
            f"app_chrome.menu: layout {layout!r} carries a menu but none is "
            "declared - every screen's blueprint would then invent its own")
    if layout == "LayoutBlank" and menu:
        errors.append(
            "app_chrome.menu: LayoutBlank has no menu region; either declare a "
            "menu-bearing layout or drop the menu entries")
    seen = set()
    for i, entry in enumerate(menu):
        where = f"app_chrome.menu[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be an object with 'label' and 'target'")
            continue
        label = entry.get("label")
        if not _is_text(label):
            errors.append(f"{where}: 'label' required non-empty string")
        elif label in seen:
            errors.append(f"{where}: duplicate menu label {label!r}")
        else:
            seen.add(label)
        target = entry.get("target")
        if not _is_text(target):
            errors.append(f"{where}: 'target' required non-empty string")
        elif target not in screen_names:
            errors.append(
                f"{where}: target {target!r} is not a screen in this inventory - "
                "a menu entry that points nowhere ships as a dead link")


def _check_screens(inv, errors):
    """Returns the ordered screen-name list (may contain duplicates on error)."""
    screens = inv.get("screens")
    names = []
    if not isinstance(screens, list) or not screens:
        errors.append("screens: required non-empty list")
        return names
    seen = set()
    for i, screen in enumerate(screens):
        where = f"screens[{i}]"
        if not isinstance(screen, dict):
            errors.append(f"{where}: must be an object")
            continue
        name = screen.get("name")
        if not _is_text(name):
            errors.append(f"{where}: 'name' required non-empty string")
        else:
            where = f"screen '{name}'"
            if name in seen:
                errors.append(f"{where}: duplicate screen name")
            seen.add(name)
            names.append(name)
        if not _is_text(screen.get("purpose")):
            errors.append(f"{where}: 'purpose' required non-empty string")
        archetype = screen.get("archetype")
        if archetype not in ARCHETYPES:
            errors.append(
                f"{where}: archetype {archetype!r} is not one of the 14 "
                "outsystems-ui-design archetypes "
                f"({', '.join(ARCHETYPES)})")
        # Optional, and held to its enum once declared - the access_classification
        # posture. No partial-adoption warning to match it, though: an absent
        # access decision is a gap on every screen, while an absent presentation
        # pattern is the correct answer on every screen with no collection to lay
        # out, so the same warning here would accuse correct rows.
        pattern = screen.get("presentation_pattern")
        if pattern is not None and pattern not in PRESENTATION_PATTERNS:
            errors.append(
                f"{where}: presentation_pattern {pattern!r} is not one of "
                f"{', '.join(PRESENTATION_PATTERNS)} - this field names the ODC "
                "block outsystems-ui-design will build, in that skill's block "
                "vocabulary; omit it rather than approximate one")
        # F-11: names alone were not enough. An inventory entry that carries
        # only a name hands the design run a label and no contract.
        if not _is_text(screen.get("behavior")):
            errors.append(
                f"{where}: 'behavior' required - what the screen DOES, not what "
                "it is called (trial F-11: an inventory of names alone left "
                "block choices and interactions to be reconciled by hand)")
        interactions = screen.get("key_interactions")
        if (not isinstance(interactions, list) or not interactions
                or not all(_is_text(x) for x in interactions)):
            errors.append(
                f"{where}: 'key_interactions' required non-empty list of "
                "non-empty strings (trial F-11)")
        _check_bindings(screen, where, errors)
        _check_assertions(screen, where, errors)
        accepts = screen.get("accepts", [])
        if not isinstance(accepts, list) or not all(_is_text(x) for x in accepts):
            errors.append(f"{where}: 'accepts' must be a list of non-empty strings")
    return names


def _check_bindings(screen, where, errors):
    bindings = screen.get("data_bindings")
    if not isinstance(bindings, list):
        errors.append(f"{where}: 'data_bindings' required list (may be empty)")
        return
    for j, binding in enumerate(bindings):
        at = f"{where}: data_bindings[{j}]"
        if not isinstance(binding, dict):
            errors.append(f"{at}: must be an object")
            continue
        if not _is_text(binding.get("name")):
            errors.append(f"{at}: 'name' required non-empty string")
        kind = binding.get("kind")
        if kind not in BINDING_KINDS:
            errors.append(
                f"{at}: kind {kind!r} must be one of {', '.join(BINDING_KINDS)}")
        if not _is_text(binding.get("usage")):
            errors.append(f"{at}: 'usage' required non-empty string")
        introduced = binding.get("introduced_here")
        if introduced is not None and not isinstance(introduced, bool):
            errors.append(
                f"{at}: introduced_here must be a boolean - true means this "
                "inventory is where the name was born (greenfield trial G-05)")
        elif introduced is True and kind == "action":
            errors.append(
                f"{at}: introduced_here is for entities only - a new action's "
                "name is born in the capability plan, never here (the "
                "no-logic-design scope guard; method.md R8's greenfield "
                "asymmetry)")


def _check_assertions(screen, where, errors):
    assertions = screen.get("assertions")
    if assertions is None:
        return
    if not isinstance(assertions, dict):
        errors.append(f"{where}: 'assertions' must be an object")
        return
    for key, value in assertions.items():
        if key not in ASSERTION_KEYS:
            errors.append(
                f"{where}: assertions.{key} is not a supported assertion "
                f"({', '.join(ASSERTION_KEYS)}) - the vocabulary is shared with "
                "the design validator and the post-publish recompute, so a new "
                "key would be silently unchecked downstream")
        elif not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(
                f"{where}: assertions.{key} must be a non-negative integer, "
                f"got {value!r}")


def _check_candidates(inv, screen_names, errors, require_requirement_ids=False):
    """No candidate is silently dropped, and no screen appears from nowhere."""
    absorbed = {name: 0 for name in screen_names}
    candidates = inv.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        errors.append(
            "candidates: required non-empty list - every screen-worthy thing "
            "the source named must be accounted for, so nothing is dropped "
            "without a decision")
        return
    seen = set()
    for i, cand in enumerate(candidates):
        where = f"candidates[{i}]"
        if not isinstance(cand, dict):
            errors.append(f"{where}: must be an object")
            continue
        cid = cand.get("id")
        if not _is_text(cid):
            errors.append(f"{where}: 'id' required non-empty string")
        else:
            where = f"candidate '{cid}'"
            if cid in seen:
                errors.append(f"{where}: duplicate candidate id")
            seen.add(cid)
        source_ref = cand.get("source_ref")
        if not _is_text(source_ref):
            errors.append(
                f"{where}: 'source_ref' required - where in the source this "
                "candidate came from")
        elif (require_requirement_ids
                and not REQUIREMENT_ID_PATTERN.search(source_ref)):
            errors.append(
                f"{where}: source_ref {source_ref!r} cites no requirement ID - "
                "a candidate harvested from a requirements document must name "
                "at least one ID that document defines (BR-/UC-/C-, optionally "
                "with a scope infix), free prose as a trailing note: "
                "'BR-SC-002 - the room list section'. Without it the "
                "requirement-to-screen binding exists only as prose here and "
                "gets invented a second time in the capability plan's "
                "Traceability table, with nothing checking the two agree")
        if not _is_text(cand.get("rationale")):
            errors.append(f"{where}: 'rationale' required non-empty string")
        disposition = cand.get("disposition")
        if disposition not in DISPOSITIONS:
            errors.append(
                f"{where}: disposition {disposition!r} must be one of "
                f"{', '.join(DISPOSITIONS)}")
            continue
        resolves = cand.get("resolves_to", [])
        if disposition == "mapped":
            if (not isinstance(resolves, list) or not resolves
                    or not all(_is_text(x) for x in resolves)):
                errors.append(
                    f"{where}: a mapped candidate needs 'resolves_to' naming at "
                    "least one screen")
                continue
            for target in resolves:
                if target not in absorbed:
                    errors.append(
                        f"{where}: resolves_to {target!r} is not a screen in "
                        "this inventory")
                else:
                    absorbed[target] += 1
        elif disposition == "dissolved":
            if not _is_text(cand.get("dissolved_into")):
                errors.append(
                    f"{where}: a dissolved candidate needs 'dissolved_into' - "
                    "where the capability actually lives now (it was never a "
                    "destination, but it still has to exist somewhere)")
            if resolves:
                errors.append(
                    f"{where}: a dissolved candidate must not also resolve to a "
                    "screen; pick one disposition")
        else:
            if resolves:
                errors.append(
                    f"{where}: a {disposition} candidate must not resolve to a "
                    "screen; it is excluded from this build, so nothing here "
                    "implements it - pick one disposition")
            if cand.get("dissolved_into") is not None:
                errors.append(
                    f"{where}: a {disposition} candidate must not carry "
                    "'dissolved_into' - that field names where the capability "
                    f"lives in this build, which is 'dissolved'; "
                    f"'{disposition}' means it is not built at all")
    for name, count in absorbed.items():
        if count == 0:
            errors.append(
                f"screen '{name}': no candidate resolves to it - every screen "
                "must trace back to something the source asked for")


def _cited_requirement_ids(inv):
    """{requirement_id: [candidate ids citing it]} across every source_ref."""
    cited = {}
    for i, cand in enumerate(_as_list(inv.get("candidates"))):
        if not isinstance(cand, dict):
            continue
        ref = cand.get("source_ref")
        if not _is_text(ref):
            continue
        label = cand.get("id") if _is_text(cand.get("id")) else f"candidates[{i}]"
        for req_id in REQUIREMENT_ID_PATTERN.findall(ref):
            cited.setdefault(req_id, []).append(label)
    return cited


def _check_non_screen_requirements(inv, errors):
    """Shape of the optional non-screen disposition list; returns its IDs.

    A requirement can produce no screen and still be a real requirement (a
    hashing rule, a retention policy). Saying so explicitly is what lets the
    absorption check treat silence as the error it is.
    """
    declared = set()
    entries = inv.get("non_screen_requirements")
    if entries is None:
        return declared
    if not isinstance(entries, list):
        errors.append(
            "non_screen_requirements: must be a list of {id, reason} objects")
        return declared
    for i, entry in enumerate(entries):
        where = f"non_screen_requirements[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be an object with 'id' and 'reason'")
            continue
        if not _is_text(entry.get("reason")):
            errors.append(
                f"{where}: 'reason' required - why this requirement produces no "
                "screen. A bare exclusion list is indistinguishable from an "
                "oversight, which is the state this slot exists to remove")
        req_id = entry.get("id")
        if not _is_text(req_id):
            errors.append(f"{where}: 'id' required non-empty string")
            continue
        req_id = req_id.strip()
        if not REQUIREMENT_ID_PATTERN.fullmatch(req_id):
            errors.append(
                f"{where}: id {req_id!r} is not a requirement ID - use the "
                "grammar the source document and the capability plan share "
                "(BR-/UC-/C- with an optional scope infix, e.g. BR-SEC-004)")
        elif req_id in declared:
            errors.append(f"{where}: duplicate disposition for {req_id}")
        else:
            declared.add(req_id)
    return declared


def _check_provenance_conflicts(cited, declared, errors):
    """Cited and dispositioned are mutually exclusive, source or no source."""
    for req_id in sorted(set(cited) & declared):
        errors.append(
            f"{req_id}: both cited as candidate provenance (by "
            f"{', '.join(sorted(set(cited[req_id])))}) and dispositioned as "
            "producing no screen - it is one or the other")


def provenance_mode(inv, source_text, notes):
    """Decide whether the requirement-ID checks apply, and on what universe.

    Returns (require_ids, defined). `defined` is None when no source document
    was supplied; it is never empty, because a source that defines no IDs
    degrades the whole check to a note rather than failing every candidate -
    the same reading check_requirement_coverage.py gives an ID-less source
    (input this check cannot use, not a failed verdict).
    """
    kind = _as_dict(inv.get("source")).get("kind")
    if kind != "requirements-doc":
        notes.append(
            f"NOTE: requirement-ID provenance not checked: source.kind is {kind!r}, "
            "so candidates trace to an existing app's own screens and there is "
            "no requirement-ID grammar for them to cite")
        return False, None
    if source_text is None:
        return True, None
    defined = set(REQUIREMENT_ID_PATTERN.findall(source_text))
    if not defined:
        notes.append(
            "NOTE: requirement-ID provenance not checked: the --source document "
            "defines no requirement IDs, so no candidate can cite one. Give "
            "the source a Requirement Inventory first - see "
            "outsystems-plan-to-mentor references/requirement-id-conventions.md")
        return False, None
    return True, defined


def _check_absorption(cited, declared, defined, errors, notes):
    """Every requirement the source defines is absorbed or dispositioned."""
    unabsorbed = sorted(defined - set(cited) - declared)
    if unabsorbed:
        errors.append(
            "unabsorbed requirements - defined in the source, no candidate "
            "cites them and no non_screen_requirements entry disposes of "
            f"them: {', '.join(unabsorbed)}. Each is either a candidate's "
            "provenance or an explicit non-screen disposition with a reason; "
            "silence is the third state this check removes")
    for req_id in sorted(set(cited) - defined):
        errors.append(
            f"candidate provenance {req_id} (cited by "
            f"{', '.join(sorted(set(cited[req_id])))}) is not defined in the "
            "source document - a citation the source cannot confirm proves "
            "nothing")
    for req_id in sorted(declared - defined):
        errors.append(
            f"non_screen_requirements: {req_id} is not defined in the source "
            "document")
    absorbed = defined & set(cited)
    dispositioned = defined & declared
    notes.append(
        f"PROVENANCE: {len(absorbed) + len(dispositioned)}/{len(defined)} "
        f"source requirements accounted for ({len(absorbed)} on candidates, "
        f"{len(dispositioned)} dispositioned as producing no screen)")


def _check_navigation(inv, screens_by_name, errors):
    """Validates edges; returns the valid (from, to) pairs for the graph walk."""
    edges = []
    nav = inv.get("navigation")
    if not isinstance(nav, list):
        errors.append("navigation: required list (may be empty)")
        return edges
    for i, edge in enumerate(nav):
        where = f"navigation[{i}]"
        if not isinstance(edge, dict):
            errors.append(f"{where}: must be an object")
            continue
        src, dst = edge.get("from"), edge.get("to")
        for field, value in (("from", src), ("to", dst)):
            if not _is_text(value):
                errors.append(f"{where}: '{field}' required non-empty string")
            elif value not in screens_by_name:
                errors.append(
                    f"{where}: {field} {value!r} is not a screen in this inventory")
        if not _is_text(edge.get("trigger")):
            errors.append(
                f"{where}: 'trigger' required - what the user does to follow "
                "this edge")
        if _is_text(src) and src == dst:
            errors.append(f"{where}: an edge from a screen to itself is not navigation")
        if _is_text(dst) and dst in screens_by_name:
            if _is_text(src) and src in screens_by_name and src != dst:
                edges.append((src, dst))
            payload = edge.get("payload")
            if payload is not None:
                # Trial F-12: the plan asserted a hand-off and the receiving
                # screen had no input that could accept it. Nothing caught it
                # until packaging.
                if not _is_text(payload):
                    errors.append(f"{where}: 'payload' must be a non-empty string")
                elif payload not in _as_list(screens_by_name[dst].get("accepts")):
                    errors.append(
                        f"{where}: hands {payload!r} to screen {dst!r}, which does "
                        f"not list it in 'accepts' - the receiving end of a "
                        "hand-off must exist before the build assumes it")
    return edges


def _offered_record_actions(screen):
    """The record actions a screen's `key_interactions` open with, in order.

    Anchored at the start of each interaction because that is where the verb
    is; an unanchored scan reads "the run it created" as a create form.
    """
    offered = []
    for item in _as_list(screen.get("key_interactions")):
        if not _is_text(item):
            continue
        text = item.strip().lower()
        for action, verbs in RECORD_ACTION_OPENERS:
            if action in offered:
                continue
            if re.match(rf"^{verbs}\b", text):
                offered.append(action)
    return [a for a in RECORD_ACTIONS if a in offered]


def _record_actions_declared(screen):
    """`{action: resolves_to}` for the well-formed entries only.

    Malformed ones are reported by `_check_record_actions`; skipping them here
    keeps one defect to one message.
    """
    declared = {}
    for entry in _as_list(screen.get("record_actions")):
        if not isinstance(entry, dict):
            continue
        action, resolves = entry.get("action"), entry.get("resolves_to")
        if action in RECORD_ACTIONS and _is_text(resolves):
            declared.setdefault(action, resolves)
    return declared


def _actions_reached_by_an_edge(inv, screens_by_name, screen_name, offered):
    """The offered actions an existing outgoing edge already accounts for.

    Two ways, because one is not enough. A trigger is a phrase ("open a stored
    query"), so its verb is matched anywhere in it rather than anchored - but
    a trigger may name the gesture instead of the action ("the + button"), so
    an edge into a form archetype discharges on shape alone. Without the
    second, wording defeats the check; without the first, a form screen that
    is archetyped as something else escapes it.
    """
    edges = [e for e in _as_list(inv.get("navigation"))
             if isinstance(e, dict) and e.get("from") == screen_name]
    triggers = [e["trigger"].lower() for e in edges if _is_text(e.get("trigger"))]
    archetypes = {(screens_by_name.get(e.get("to")) or {}).get("archetype")
                  for e in edges}
    reached = []
    for action, verbs in RECORD_ACTION_OPENERS:
        if action not in offered:
            continue
        if any(re.search(verbs, t) for t in triggers):
            reached.append(action)
            continue
        group = RECORD_ACTION_DESTINATIONS[action]
        if not archetypes & set(group):
            continue
        # Archetype evidence is not action-specific: create and edit open the
        # same kinds of screen, so one edge into an `edit-form` cannot say
        # which of the two it serves. Letting it answer for both is how a
        # screen offering create AND edit with only an edit route passed
        # silently - the missing create destination IS the incident (Codex,
        # AH-2026-08-30-012 round 1). So this route discharges only when
        # exactly one offered action shares the destination group; where two
        # do, the trigger has to name one or the author has to declare.
        if len([a for a in offered
                if RECORD_ACTION_DESTINATIONS[a] == group]) == 1:
            reached.append(action)
    return reached


def _check_record_actions(inv, screens_by_name, errors):
    """The field is optional; a declared entry is held to its rules.

    Same bargain as `presentation_pattern` and `access_classification`: an
    inventory written before the field existed is untouched, and one that
    declares has said something a build will act on.
    """
    for name, screen in screens_by_name.items():
        entries = screen.get("record_actions")
        if entries is None:
            continue
        if not isinstance(entries, list) or not entries:
            errors.append(
                f"screen '{name}': 'record_actions' must be a non-empty list - "
                "omit the key rather than declaring nothing")
            continue
        seen = set()
        for i, entry in enumerate(entries):
            where = f"screen '{name}': record_actions[{i}]"
            if not isinstance(entry, dict):
                errors.append(f"{where}: must be an object")
                continue
            action = entry.get("action")
            if action not in RECORD_ACTIONS:
                errors.append(
                    f"{where}: 'action' must be one of "
                    f"{', '.join(RECORD_ACTIONS)}, not {action!r}")
                continue
            if action in seen:
                errors.append(
                    f"{where}: '{action}' is declared twice on this screen - "
                    "one action resolves one way")
                continue
            seen.add(action)
            resolves = entry.get("resolves_to")
            if not _is_text(resolves):
                errors.append(
                    f"{where}: 'resolves_to' required - name the screen this "
                    f"action opens, or '{RECORD_ACTION_INLINE}', or "
                    f"'{RECORD_ACTION_OUT_OF_SCOPE}'")
                continue
            if resolves == RECORD_ACTION_OUT_OF_SCOPE:
                if not _is_text(entry.get("reason")):
                    errors.append(
                        f"{where}: '{RECORD_ACTION_OUT_OF_SCOPE}' requires a "
                        "'reason' - the control must not be built, and the "
                        "next reader has to know that was decided")
                # Out-of-scope says the control is NOT built. A screen still
                # advertising the action in `key_interactions` then says both
                # things at once, and the design run reads the interactions.
                # Codex, AH-2026-08-30-012 round 1: allowing this to clear the
                # offer finding would make "clearing it is always right" false,
                # because one of the doors out left the artifact contradicting
                # itself. Withdrawing the interaction is the honest edit.
                elif action in _offered_record_actions(screen):
                    errors.append(
                        f"{where}: '{action}' is {RECORD_ACTION_OUT_OF_SCOPE}, "
                        f"but this screen still lists a key interaction that "
                        f"offers it - the inventory says the control is not "
                        "built and describes it in the same breath. Withdraw "
                        "the interaction, or resolve the action to a screen "
                        f"or '{RECORD_ACTION_INLINE}'")
                continue
            if resolves == RECORD_ACTION_INLINE:
                continue
            if resolves not in screens_by_name:
                errors.append(
                    f"{where}: '{action}' resolves to {resolves!r}, which is "
                    "not a screen in this inventory - the destination behind a "
                    "control has to exist before the build assumes it")
                continue
            if resolves == name:
                errors.append(
                    f"{where}: '{action}' resolves to this screen itself - "
                    f"say '{RECORD_ACTION_INLINE}' when it happens here")
                continue
            if not any(
                    isinstance(e, dict) and e.get("from") == name
                    and e.get("to") == resolves
                    for e in _as_list(inv.get("navigation"))):
                errors.append(
                    f"{where}: '{action}' resolves to screen {resolves!r} with "
                    f"no navigation edge from '{name}' to it - a control that "
                    "opens a screen is an edge, and the edge is what carries "
                    "the trigger and the payload")


def requirements_for_screen(inv, screen_name):
    """The requirement provenance one design run needs. Returns three lists:

    - `ids`: the requirement IDs this screen realizes, deduplicated, in the
      order the author listed the candidates.
    - `provenance`: `(candidate_id, source_ref)` for each mapped candidate
      resolving here that cites an ID - the prose note the author wrote.
    - `unbound`: `(ids, candidate_id, dissolved_into)` for DISSOLVED candidates
      that cite IDs. Their capability went somewhere named in free text, not to
      a screen, so the data model cannot say which brief they belong on. They
      are reported on every brief rather than dropped: `--source` absorption
      counts a dissolved candidate's ID as accounted for, so a brief that never
      mentions it is the one place the requirement could go missing between the
      source document and the build.
    """
    ids, provenance, unbound = [], [], []
    for cand in _as_list(inv.get("candidates")):
        if not isinstance(cand, dict):
            continue
        ref = cand.get("source_ref")
        if not _is_text(ref):
            continue
        found = REQUIREMENT_ID_PATTERN.findall(ref)
        if not found:
            continue
        label = cand.get("id") if _is_text(cand.get("id")) else "(unnamed candidate)"
        if cand.get("disposition") == "dissolved":
            unbound.append((found, label, cand.get("dissolved_into")))
        elif screen_name in _as_list(cand.get("resolves_to")):
            provenance.append((label, ref))
            ids += [i for i in found if i not in ids]
    return ids, provenance, unbound


def _check_open_decisions(inv, screen_names, errors):
    """Shape-enforce the typed open-decisions slot.

    An unresolved decision used to have no slot at all: SKILL.md hard gate 5's
    autonomous-run disclosure instructed the model to name its least-confident
    fusion in prose, and prose is not carried by the artifact. What is enforced
    here is the shape - a decision, 2-4 options, each option naming the change
    it would cause. Whether the decision is a good one is not checkable; whether
    it was written down as a real choice is.
    """
    decisions = inv.get("open_decisions")
    if decisions is None:
        return
    if not isinstance(decisions, list):
        errors.append(
            "open_decisions: must be a list of typed decisions, each with "
            "2-4 options naming their consequences")
        return
    seen = set()
    for i, decision in enumerate(decisions):
        where = f"open_decisions[{i}]"
        if not isinstance(decision, dict):
            errors.append(f"{where}: must be an object")
            continue
        did = decision.get("id")
        if not _is_text(did):
            errors.append(f"{where}: 'id' required non-empty string")
        else:
            where = f"open decision '{did}'"
            if did in seen:
                errors.append(f"{where}: duplicate open_decisions id")
            seen.add(did)
        if not _is_text(decision.get("about")):
            errors.append(
                f"{where}: 'about' required - the decision itself, stated so a "
                "reviewer can take it without reconstructing it")
        category = decision.get("category")
        if category not in OPEN_DECISION_CATEGORIES:
            errors.append(
                f"{where}: category {category!r} is not one of the "
                "screen-inventory decision categories "
                f"({', '.join(OPEN_DECISION_CATEGORIES)}) - a decision outside "
                "this skill's scope belongs to the skill that owns it, not here")
        option_ids = _check_decision_options(decision, where, errors)
        status = decision.get("status")
        if status not in DECISION_STATUSES:
            errors.append(
                f"{where}: status {status!r} must be one of "
                f"{', '.join(DECISION_STATUSES)}")
        resolution = decision.get("resolution")
        if status == "resolved":
            if not _is_text(resolution):
                errors.append(
                    f"{where}: 'resolution' required on a resolved decision - "
                    "naming the option taken, not just that someone decided")
            elif option_ids and resolution not in option_ids:
                errors.append(
                    f"{where}: resolution {resolution!r} is not one of its "
                    f"options ({', '.join(sorted(option_ids))})")
        elif status == "open" and resolution is not None:
            errors.append(
                f"{where}: is still open but records a resolution "
                f"{resolution!r} - one of the two is wrong")
        affects = decision.get("affects")
        if affects is not None:
            if not isinstance(affects, list) or not all(_is_text(x) for x in affects):
                errors.append(
                    f"{where}: 'affects' must be a list of screen names (omit "
                    "it when the decision is app-wide)")
            else:
                for name in affects:
                    if name not in screen_names:
                        errors.append(
                            f"{where}: affects {name!r}, which is not a screen "
                            "in this inventory")


def _check_decision_options(decision, where, errors):
    """Returns the set of valid option ids, for the resolution check."""
    options = decision.get("options")
    if not isinstance(options, list) or not MIN_OPTIONS <= len(options) <= MAX_OPTIONS:
        count = len(options) if isinstance(options, list) else "no"
        errors.append(
            f"{where}: needs between {MIN_OPTIONS} and {MAX_OPTIONS} options, "
            f"has {count} - one option is a position and five is a survey; "
            "neither is a decision a reviewer can take")
        return set()
    ids, labels = set(), set()
    for j, option in enumerate(options):
        at = f"{where}: options[{j}]"
        if not isinstance(option, dict):
            errors.append(f"{at}: must be an object")
            continue
        oid = option.get("id")
        if not _is_text(oid):
            errors.append(f"{at}: 'id' required non-empty string")
        elif oid in ids:
            errors.append(f"{at}: duplicate option id {oid!r}")
        else:
            ids.add(oid)
        label = option.get("label")
        if not _is_text(label):
            errors.append(f"{at}: 'label' required non-empty string")
        elif label in labels:
            errors.append(
                f"{at}: duplicate option label {label!r} - two spellings of one "
                "choice leaves the decision with fewer real options than it claims")
        else:
            labels.add(label)
        # The whole point of the slot: an option that does not name what would
        # change is the bare label this replaced.
        if not _is_text(option.get("consequence")):
            errors.append(
                f"{at}: 'consequence' required - exactly what this inventory "
                "would say if this option were taken; a label alone is the "
                "prose the typed slot exists to replace")
    return ids


def open_decisions_for(inv, screen_name=None):
    """The still-open decisions, optionally narrowed to one screen.

    A decision with no `affects` is app-wide (chrome, most navigation) and
    reaches every brief: withholding those would make the decisions with the
    widest blast radius the silent ones.
    """
    out = []
    for decision in _as_list(inv.get("open_decisions")):
        if not isinstance(decision, dict) or decision.get("status") != "open":
            continue
        if screen_name is not None:
            affects = decision.get("affects")
            if isinstance(affects, list) and affects and screen_name not in affects:
                continue
        out.append(decision)
    return out


def format_open_decisions(decisions, indent=""):
    """The disclosure lines, shared by the report and the per-screen brief."""
    lines = []
    for decision in decisions:
        lines.append(
            f"{indent}OPEN DECISION: {decision.get('id')} "
            f"[{decision.get('category')}] {decision.get('about')}")
        for option in _as_list(decision.get("options")):
            if isinstance(option, dict):
                lines.append(
                    f"{indent}  - {option.get('label')} => "
                    f"{option.get('consequence')}")
    return lines


def blueprint_menu_for_screen(inv, screen_name):
    """Translate the inventory menu into the blueprint's menu shape.

    The inventory records where each entry GOES (`{label, target}`); a
    blueprint records `{label, active}` and OUD's cross-blueprint pass
    compares only the label sequence, deliberately ignoring `active`.
    `target` never enters a blueprint - it becomes this screen's `active`
    flag (Codex AH-2026-08-08-011 finding 2: the translation is explicit,
    not "copy verbatim").
    """
    return [
        {"label": e.get("label"), "active": e.get("target") == screen_name}
        for e in _as_list(_as_dict(inv.get("app_chrome")).get("menu"))
        if isinstance(e, dict)
    ]


def collect_errors(inv, source_text=None, notes=None):
    """Contract errors. `notes` is an optional out-list for the lines that
    report a check declining to run - a degradation nobody can see is
    indistinguishable from a check that passed."""
    errors = []
    notes = notes if notes is not None else []
    if not isinstance(inv, dict):
        return ["inventory: top level must be a JSON object"]
    for field in TOP_LEVEL:
        if field not in inv:
            errors.append(f"missing required top-level field '{field}'")
    if inv.get("schema_version") != "1":
        errors.append(
            f"schema_version: {inv.get('schema_version')!r} must be \"1\"")
    if not _is_text(inv.get("app_name")):
        errors.append("app_name: required non-empty string")
    _check_source(inv, errors)
    tokens = inv.get("design_tokens_source")
    if tokens is not None and not _is_text(tokens):
        errors.append(
            "design_tokens_source: must be a non-empty string naming where "
            "the design runs read visual identity from (an approved sibling "
            "blueprint, an as-built theme)")

    require_ids, defined = provenance_mode(inv, source_text, notes)
    declared_non_screen = _check_non_screen_requirements(inv, errors)
    cited = _cited_requirement_ids(inv)
    _check_provenance_conflicts(cited, declared_non_screen, errors)
    if defined is not None:
        _check_absorption(cited, declared_non_screen, defined, errors, notes)

    screen_names = _check_screens(inv, errors)
    _check_chrome(inv, set(screen_names), errors)
    _check_candidates(inv, screen_names, errors, require_ids)
    screens_by_name = _screens_by_name(inv)
    edges = _check_navigation(inv, screens_by_name, errors)
    _check_record_actions(inv, screens_by_name, errors)
    _check_open_decisions(inv, set(screen_names), errors)

    # Reachability is a graph walk from the app's real entry surface, not a
    # has-an-incoming-edge check: two screens pointing at each other with no
    # path from any menu entry are still an island no user can land on
    # (Codex AH-2026-08-08-011 finding 3).
    menu_targets = {
        e.get("target") for e in _as_list(_as_dict(inv.get("app_chrome")).get("menu"))
        if isinstance(e, dict)
    }
    roots = {t for t in menu_targets if t in screens_by_name}
    for name, screen in screens_by_name.items():
        entry = screen.get("entry_point")
        if entry is not None and not isinstance(entry, bool):
            errors.append(
                f"screen '{name}': entry_point must be a boolean - true means "
                "users land here from outside the app's own navigation "
                "(deep link, external URL, notification)")
        elif entry is True:
            roots.add(name)
    adjacency = {}
    for src, dst in edges:
        adjacency.setdefault(src, []).append(dst)
    reachable = set(roots)
    frontier = list(roots)
    while frontier:
        for dst in adjacency.get(frontier.pop(), []):
            if dst not in reachable:
                reachable.add(dst)
                frontier.append(dst)
    for name in screen_names:
        if name not in reachable:
            errors.append(
                f"screen '{name}': unreachable - no path from any menu entry "
                "or declared entry_point leads to it, so nothing in the built "
                "app would lead a user to it (an edge from another unreachable "
                "screen does not count)")
    _check_placeholders(inv, errors)
    _check_access_classification(inv, errors)
    return errors


def collect_warnings(inv):
    warnings = []
    if not isinstance(inv, dict):
        return warnings
    screen_names = list(_screens_by_name(inv))
    absorbed = {name: 0 for name in screen_names}
    for cand in _as_list(inv.get("candidates")):
        if not isinstance(cand, dict) or cand.get("disposition") != "mapped":
            continue
        for target in _as_list(cand.get("resolves_to")):
            if target in absorbed:
                absorbed[target] += 1
    one_to_one = [n for n in screen_names if absorbed.get(n) == 1]
    if one_to_one and len(one_to_one) == len(screen_names):
        warnings.append(Finding(
            "every screen absorbs exactly one candidate - this inventory "
            "restates the source's own structure rather than deciding an "
            "information architecture. Cluster by what the user is trying to "
            "do, then check whether any grouping leaves nothing behind when "
            "its members are rehomed",
            # An information-architecture judgement, not a defect: an app that
            # really is one screen per candidate is a legitimate final state,
            # so promoting this would block a correct inventory with nothing
            # to clear it.
            graduating=False,
        ))
    # A PARTIALLY declared inventory is the only access gap this surface can
    # call: some screens carry the decision and others do not, which is an
    # oversight no reading of the artifact makes correct. A wholly undeclared
    # inventory is NOT warned - the field is optional, every inventory written
    # before it existed declares nothing, and a warning firing on all of them
    # is the always-on noise AH-2026-08-26-015 removed when it deleted a
    # warning that "accused correct rows". The fail-closed enforcement lives
    # in the downstream render gate, which scores an undeclared screen
    # `unasserted` (never `pass`) against an actual readback; this is the
    # cheap consistency check, not a second gate.
    declared_access = [
        name for name, screen in _screens_by_name(inv).items()
        if screen.get("access_classification") is not None]
    if declared_access:
        for name, screen in _screens_by_name(inv).items():
            if screen.get("access_classification") is None:
                warnings.append(Finding(
                    f"screen '{name}': no access_classification, but "
                    f"{len(declared_access)} screen(s) in this inventory "
                    "declare one - who this screen is for was left undecided "
                    "while its siblings were settled. The render gate "
                    "scores an undeclared screen 'unasserted', never 'pass', "
                    "and its promotion audit reports the gap",
                    # Advisory. `unresolved` is an error, so graduating this
                    # would leave an author who has genuinely not reached the
                    # decision no valid value to write and no way to hand off.
                    graduating=False,
                ))
    # CRUD closure: a list screen that offers create/edit/detail has to say
    # where that happens. Two apps shipped "add" and per-row "edit" controls
    # whose destination screens were in nobody's inventory; they rendered and
    # did nothing, and the second app had no data-entry path at all. Prose is
    # not read here and is not trusted to settle it: on the evidence app the
    # `behavior` field asserted "Dishes are created, edited and retired here"
    # while the build produced navigation controls to screens that did not
    # exist. Graduating, because it is always clearable by editing the
    # inventory - name the screen, say `inline`, or say `out-of-scope` with a
    # reason - which is the same bargain `behavior_notes` makes, not a waiver.
    screens = _screens_by_name(inv)
    for name, screen in screens.items():
        if screen.get("archetype") not in RECORD_LIST_ARCHETYPES:
            continue
        offered = _offered_record_actions(screen)
        if not offered:
            continue
        declared = _record_actions_declared(screen)
        reached = _actions_reached_by_an_edge(inv, screens, name, offered)
        unresolved = [a for a in offered
                      if a not in declared and a not in reached]
        if not unresolved:
            continue
        warnings.append(Finding(
            f"screen '{name}': offers {', '.join(unresolved)} on a record but "
            "does not say where that happens - no 'record_actions' entry and "
            "no outgoing navigation edge whose trigger names it. Declare each "
            f"one as a screen name, '{RECORD_ACTION_INLINE}', or "
            f"'{RECORD_ACTION_OUT_OF_SCOPE}' with a reason (the control is "
            "then not built). A control whose destination was never in the "
            "inventory is still built, renders, and does nothing",
            # Always clearable by editing the inventory: every action has one
            # of three true answers. That is the graduation test, and the
            # third answer is what keeps a genuinely inline screen valid.
            graduating=True,
        ))
    for name, screen in _screens_by_name(inv).items():
        for binding in _as_list(screen.get("data_bindings")):
            if isinstance(binding, dict) and not _is_text(binding.get("behavior_notes")):
                warnings.append(Finding(
                    f"screen '{name}': data binding "
                    f"'{binding.get('name', '?')}' has no behavior_notes - "
                    "signatures without behaviour is exactly what trial F-11 "
                    "cost (a 10-row cap sat one field away from what was captured)",
                    # Blocks at handoff: the note is always writable, and the
                    # design run downstream reads behaviour, not signatures.
                    graduating=True,
                ))
    return warnings


def format_brief(inv, screen_name):
    """The per-screen kickoff facts for one outsystems-ui-design run."""
    screens = _screens_by_name(inv)
    if screen_name not in screens:
        known = ", ".join(sorted(screens)) or "(none)"
        return None, f"no screen named {screen_name!r} in this inventory. Known: {known}\n"
    screen = screens[screen_name]
    chrome = _as_dict(inv.get("app_chrome"))
    lines = [
        f"SCREEN BRIEF: {screen_name}",
        f"app: {inv.get('app_name')}",
    ]
    # The brief is the only thing a design run reads. An undecided point that
    # reaches the report but not the brief is silent exactly where it matters.
    pending = open_decisions_for(inv, screen_name)
    if pending:
        lines.append(
            "OPEN DECISIONS affecting this screen - PROPOSED, NOT APPROVED. "
            "Do not settle one of these inside a design run; take it back to "
            "the inventory:")
        lines += format_open_decisions(pending, indent="  ")
    lines += [
        f"archetype: {screen.get('archetype')}",
    ]
    # Printed only when declared: a `None` on this line would read as a decision
    # the inventory never took. The wording says HINT because a design run may
    # diverge - it just may not do so silently.
    if _is_text(screen.get("presentation_pattern")):
        lines.append(
            f"presentation pattern: {screen['presentation_pattern']} "
            "(decided at inventory time for the whole app - HINT, not a "
            "constraint; if this design diverges, say so and say why)")
    lines += [
        f"purpose: {screen.get('purpose')}",
        f"behavior: {screen.get('behavior')}",
        "key interactions:",
    ]
    lines += [f"  - {x}" for x in _as_list(screen.get("key_interactions"))]

    # Same reason as the open decisions above: a disposition that reaches the
    # validation report and not the brief is unenforceable by construction,
    # because the brief is all a design run reads. All three kinds print
    # together so the run sees them in one place rather than inferring two of
    # them from silence, and `out-of-scope` prints as an instruction - it is
    # the one that says a control the interactions describe must NOT be built.
    declared_actions = _record_actions_declared(screen)
    if declared_actions:
        lines.append("record actions - where each one happens:")
        for action in RECORD_ACTIONS:
            resolves = declared_actions.get(action)
            if resolves is None:
                continue
            if resolves == RECORD_ACTION_INLINE:
                lines.append(
                    f"  - {action}: on THIS screen - build it here, do not "
                    "navigate away")
            elif resolves == RECORD_ACTION_OUT_OF_SCOPE:
                reason = next(
                    (e.get("reason") for e in _as_list(screen.get("record_actions"))
                     if isinstance(e, dict) and e.get("action") == action
                     and _is_text(e.get("reason"))), "no reason recorded")
                lines.append(
                    f"  - {action}: OUT OF SCOPE - DO NOT BUILD the control "
                    f"this screen's interactions describe ({reason})")
            else:
                lines.append(
                    f"  - {action}: navigates to '{resolves}' - build the "
                    "control, not the destination; that screen has its own run")

    # The brief is the only thing a per-screen design run reads. Provenance
    # recorded on candidates and never carried here would leave the design run
    # unable to name what it is realizing - and the plan's Traceability table
    # the only place the binding appears, which is what L4 exists to end.
    req_ids, provenance, unbound = requirements_for_screen(inv, screen_name)
    if req_ids:
        lines.append(f"requirements realized here: {', '.join(req_ids)}")
        for cand_id, ref in provenance:
            lines.append(f"  from candidate '{cand_id}': {ref}")
    elif _as_dict(inv.get("source")).get("kind") == "existing-app-modernization":
        lines.append(
            "requirements realized here: none recorded - this inventory's "
            "source is an existing app, so its candidates trace to that app's "
            "screens rather than to requirement IDs")
    else:
        lines.append(
            "requirements realized here: none recorded - no candidate "
            "resolving to this screen cites a requirement ID")
    if unbound:
        lines.append(
            "dissolved candidates carrying requirements (not bound to any "
            "screen - check whether any of them land here):")
        for found, cand_id, destination in unbound:
            lines.append(
                f"  - {', '.join(found)} from candidate '{cand_id}', "
                f"dissolved into '{destination}'")

    lines.append("data bindings:")
    for binding in _as_list(screen.get("data_bindings")):
        note = binding.get("behavior_notes")
        suffix = f" [{note}]" if _is_text(note) else ""
        lines.append(
            f"  - {binding.get('name')} ({binding.get('kind')}): "
            f"{binding.get('usage')}{suffix}")
    if not _as_list(screen.get("data_bindings")):
        lines.append("  (none)")
    born_here = [
        b.get("name") for b in _as_list(screen.get("data_bindings"))
        if isinstance(b, dict) and b.get("introduced_here") is True
    ]
    if born_here:
        # Trial G-05: with no other author available, the design run typed the
        # new entities' attributes itself - the unilateral naming R8 exists to
        # prevent. The brief states whose job the shapes are.
        lines.append(
            f"entities born in this inventory: {', '.join(born_here)}")
        lines.append(
            "  their names are authoritative (R8); their attribute shapes are "
            "not decided yet - typing them is the capability plan's job. The "
            "design run must not invent typed attributes for them; it carries "
            "name and behaviour notes only.")
    lines.append("app_chrome for the blueprint (layout_block/app_title verbatim; "
                 "menu translated to the blueprint's {label, active} shape):")
    lines.append(f"  layout_block: {chrome.get('layout_block')}")
    lines.append(f"  app_title: {chrome.get('app_title')}")
    for entry in blueprint_menu_for_screen(inv, screen_name):
        mark = " <- this screen" if entry["active"] else ""
        lines.append(
            f"  menu: {{\"label\": \"{entry['label']}\", "
            f"\"active\": {str(entry['active']).lower()}}}{mark}")
    assertions = screen.get("assertions")
    if assertions:
        pairs = ", ".join(f"{k}={v}" for k, v in sorted(assertions.items()))
        lines.append(f"declared assertions (carry into the blueprint): {pairs}")
    outgoing = [
        e for e in _as_list(inv.get("navigation"))
        if isinstance(e, dict) and e.get("from") == screen_name
    ]
    if outgoing:
        lines.append("navigates to:")
        for edge in outgoing:
            payload = f" carrying {edge['payload']}" if _is_text(edge.get("payload")) else ""
            lines.append(f"  - {edge.get('to')} on {edge.get('trigger')}{payload}")
    incoming = [
        e for e in _as_list(inv.get("navigation"))
        if isinstance(e, dict) and e.get("to") == screen_name
    ]
    if incoming:
        # Trial G-05: the accepts contract's other half - without it the
        # design run walked back to the full inventory to learn who sends
        # the payload it was implementing the receiving end of.
        lines.append("arrives from:")
        for edge in incoming:
            payload = f" carrying {edge['payload']}" if _is_text(edge.get("payload")) else ""
            lines.append(f"  - {edge.get('from')} on {edge.get('trigger')}{payload}")
    accepts = _as_list(screen.get("accepts"))
    if accepts:
        lines.append(f"accepts from other screens: {', '.join(accepts)}")
    tokens = inv.get("design_tokens_source")
    if _is_text(tokens):
        lines.append(f"design tokens: {tokens}")
    elif _as_dict(inv.get("source")).get("kind") == "existing-app-modernization":
        lines.append(
            "design tokens: no recorded source - modernization, so visual "
            "identity comes from the as-built theme of the app being redesigned")
    else:
        lines.append(
            "design tokens: no source yet - the first design run establishes "
            "the design_system; record it as design_tokens_source so later "
            "screens inherit it instead of re-deriving it")
    excluded = [
        c for c in _as_list(inv.get("candidates"))
        if isinstance(c, dict)
        and c.get("disposition") in EXCLUDED_DISPOSITIONS
    ]
    if excluded:
        # The excluded-scope channel. An exclusion decided at fusion time used
        # to stop at the inventory, so a design run could draw a region for it
        # and a Mentor session could build it. The list is app-wide, not
        # per-screen: what must not be designed anywhere must not be designed
        # here either. Each line carries its disposition word verbatim - the
        # three are different decisions, and downstream records them by name.
        lines.append(
            "excluded from this build - do NOT design or implement "
            "(recorded for traceability only):")
        lines += [
            f"  - {c.get('id')} [{c.get('disposition')}] "
            f"({c.get('source_ref')}): {c.get('rationale')}"
            for c in excluded
        ]
    return "\n".join(lines) + "\n", None


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Path to screen-inventory.json")
    parser.add_argument("--report",
                        help="Report path (default: beside the inventory)")
    parser.add_argument("--brief", metavar="SCREEN",
                        help="Also print the design-run kickoff brief for one screen")
    parser.add_argument("--source", metavar="PRD",
                        help="Requirements document defining the requirement ID "
                             "universe; checks every ID it defines is either a "
                             "candidate's provenance or an explicit non-screen "
                             "disposition")
    parser.add_argument("--handoff", action="store_true",
                        help="Grade this run as a handoff rather than a draft: "
                             "the graduating warnings - the ones always fixable "
                             "by the author - block instead of advising. Without "
                             "it the report is unchanged, byte for byte")
    args = parser.parse_args(argv)

    inv_path = Path(args.path)
    report_path = (Path(args.report) if args.report
                   else inv_path.with_name("screen-inventory-validation.txt"))
    try:
        inv = json.loads(inv_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report = f"INVALID: cannot parse {inv_path}: {exc}\n"
        try:
            report_path.write_text(report, encoding="utf-8")
        except OSError:
            pass
        sys.stdout.write(report)
        return 2

    source_text = None
    if args.source:
        try:
            source_text = Path(args.source).read_text(encoding="utf-8")
        except OSError as exc:
            sys.stdout.write(f"INVALID: cannot read --source {args.source}: {exc}\n")
            return 2

    notes = []
    errors = collect_errors(inv, source_text, notes)
    warnings = collect_warnings(inv)
    if errors:
        lines = [f"INVALID: {len(errors)} contract error(s)."] + [f"- {e}" for e in errors]
    else:
        screens = len(inv.get("screens", []))
        candidates = len(inv.get("candidates", []))
        lines = [f"VALID: {candidates} candidate(s) resolved into {screens} screen(s); "
                 "chrome and navigation consistent."]
    # Graduation. Two regimes over one finding set: while the inventory is
    # being written every warning advises, and at handoff the graduating subset
    # blocks instead. The finding text is identical either way - only the
    # channel it prints in, and the exit code, depend on the regime.
    blocking = graduating_findings(warnings) if args.handoff else []
    advisory = advisory_findings(warnings) if args.handoff else warnings
    lines.extend(notes)
    for warning in advisory:
        lines.append(f"WARNING: {warning}")
    if blocking:
        plural = "" if len(blocking) == 1 else "s"
        lines.append(
            f"HANDOFF BLOCKED: {len(blocking)} graduating warning{plural} - "
            "advisory while the inventory is being written, blocking here. "
            "Each is fixable in the inventory; fix and re-run")
        lines += [f"- {w}" for w in blocking]
    # SKILL.md hard gate 5's autonomous-run disclosure, made mechanical: an
    # inventory carrying an unresolved decision says so here, in the
    # disclosure's own words, whether or not it also has contract errors.
    open_now = open_decisions_for(inv) if isinstance(inv, dict) else []
    if open_now:
        plural = "" if len(open_now) == 1 else "s"
        lines.append(
            f"PROPOSED, NOT APPROVED: {len(open_now)} open decision{plural} - "
            "this inventory and everything derived from it are proposals until "
            "each is taken")
        lines += format_open_decisions(open_now)
    report = "\n".join(lines) + "\n"
    report_path.write_text(report, encoding="utf-8")
    sys.stdout.write(report)

    if args.brief:
        brief, problem = format_brief(inv, args.brief)
        if problem:
            sys.stdout.write(f"BRIEF: {problem}")
            return 1
        sys.stdout.write(brief)
    # The brief still prints above: blocking the handoff must not hide what was
    # about to be handed over.
    return 1 if (errors or blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
