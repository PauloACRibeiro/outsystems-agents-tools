#!/usr/bin/env python3
"""Lint a draft OMI answer against the response contract for its route mode.

Deterministic checks shared with golden_scenario_check.py:
- section order for the route or lint mode (Output Shape Matrix defaults)
- exactly one evidence label inside the ### Evidence Status section
- h3 heading contract for Evidence Status
- ### Unknowns And Fallback Behavior only after ### Evidence Status
- no tenant-mutation tool identifiers in visual-source-ui visible answers
- for --mode plan-to-mentor only: the seven required Studio-Native Pseudocode
  subsections, present and in order inside that section

Generic (scorecard-free) shape checks, always run regardless of mode:
- unresolved placeholder text (TBD:/TODO:/FIXME:, lorem ipsum, manifest
  template literals)
- paste-safe structure of any ### Mentor Studio Prompt block found (acceptance
  checks / unknowns-manual-verification / prerequisites-reuse markers, and
  merged-prompt detection) - runs on any block found, no minimum count
  without a scorecard to say what's expected
- Plan Conversion Manifest structural shape, only when the answer actually
  contains a coverage_map: marker (an answer that never claimed to write a
  manifest is not held to the manifest contract); minimum coverage-entry
  count defaults to 1 (a manifest with zero entries is unconditionally
  broken) - a stricter minimum stays scorecard-only, not a generic default

Source-fidelity check (opt-in, only when a source artifact is supplied):
- omission direction only - every in-scope screen and entity the enriched
  blueprint or screen inventory declares must be named somewhere in the
  answer. The INVENTION direction (a name in the answer that resolves to no
  source artifact) is deliberately NOT implemented; see check_source_fidelity.

This is the same lint SKILL.md's Final Self-Check requires running before
every answer (mandatory, not conditional on saving a draft file) - see the
Final Self-Check section of SKILL.md. The test-only regression harness
(omi_regression_harness.py) imports these same functions so the live
self-check and the test harness never drift apart.

Exit 0 on pass, 1 on fail. --json prints a machine-readable report.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from golden_scenario_check import check, find_heading_position  # noqa: E402

ALL_LABELS = [
    "Current official",
    "Catalog-backed official",
    "O11-supported ODC candidate",
    "Mixed official+archived",
    "Course/example-backed",
    "OutSystems-public implementation evidence",
    "Unverified gap",
]

# Default required section order per route mode. Scorecards in
# tests/golden_scenarios/expected/ stay the richer per-scenario instrument.
# A small number of stricter lint-only modes are allowed when a scenario needs
# more structure than the base classifier mode guarantees.
MODE_SECTIONS = {
    "studio-native-pseudocode": [
        "### Placement", "### Studio-Native Pseudocode", "### Evidence Status"],
    "existing-app-grounding": [
        "### Placement", "### Studio-Native Pseudocode", "### Evidence Status"],
    "mentor-studio-prompt": ["### Mentor Studio Prompt", "### Evidence Status"],
    "visual-source-ui": [
        "### Mentor Studio Prompt", "### Prompt Coverage Audit",
        "### Studio-Native UI Spec", "### Evidence Status"],
    "review-only": ["### Evidence Status"],
    "mentor-web-orientation": ["### Evidence Status"],
    "live-validation": ["### Evidence Status"],
    "live-validation-row": [
        "### Placement",
        "### Evidence Status",
        "### Unknowns And Fallback Behavior",
        "### Protected Contract",
        "### Execution Boundary",
    ],
    # `Invocation mode: outsystems-plan-to-mentor` package (SKILL.md, "Output
    # Contract - when invoked by outsystems-plan-to-mentor"). Its four required
    # sections are h2 - that is the level the invocation actually emits - and
    # the universal `### Evidence Status` h3 closes the package.
    "plan-to-mentor": [
        "## Manual Setup Gate",
        "## Session Readiness Matrix",
        "## Studio-Native Pseudocode",
        "## Mentor Executable Sessions",
        "### Evidence Status",
    ],
}

PLAN_TO_MENTOR_MODE = "plan-to-mentor"
PLAN_TO_MENTOR_PSEUDOCODE_HEADING = "## Studio-Native Pseudocode"
PLAN_TO_MENTOR_SESSIONS_HEADING = "## Mentor Executable Sessions"
# Required subsections of the plan-to-mentor `Studio-Native Pseudocode`
# section, in the order SKILL.md lists them. All seven are required, not
# "whichever applied": a package that genuinely has no roles still has to say
# so under `### Role Pseudocode`, because a silently absent subsection and a
# deliberately empty one are indistinguishable to the reader who has to decide
# whether the plan was covered.
PLAN_TO_MENTOR_SUBSECTIONS = [
    "### Data Model Pseudocode",
    "### Role Pseudocode",
    "### Server Action Pseudocode",
    "### Client Action Pseudocode",
    "### Screen And UI Pseudocode",
    "### Navigation Pseudocode",
    "### Verification Pseudocode",
]

MUTATION_TOOL_IDENTIFIERS = ["app_create", "mentor_start", "publish_start", "deploy_start"]
TOOL_NAME_FORBIDDEN_MODES = {"visual-source-ui"}

# Unresolved-output markers. TBD/TODO/FIXME require a trailing colon (the
# conventional unresolved-marker shape, e.g. "TODO: fill this in") so prose
# like "the user wants a TODO list app" does not false-positive; template
# literals are exact strings from references/prompt-narrowing-preflight.md's
# manifest template.
PLACEHOLDER_REGEXES = [
    re.compile(r"\bTBD\s*:"),
    re.compile(r"\bTODO\s*:"),
    re.compile(r"\bFIXME\s*:"),
    re.compile(r"lorem ipsum", re.IGNORECASE),
    re.compile(r"<placeholder", re.IGNORECASE),
    re.compile(r"\[to be filled\]", re.IGNORECASE),
]
MANIFEST_TEMPLATE_LITERALS = [
    "[stable source requirement id or short quote]",
    "[block identifier]",
    "[stable id]",
    "[one concrete implementation goal]",
    "[path, URL, or user-provided source label]",
]
MANIFEST_REQUIRED_MARKERS = [
    "source_plan_path:", "coverage_map:", "dependency_order:", "blocks:"]
PROMPT_HEADING = "### Mentor Studio Prompt"
# Paste-safe required contents (prompt-narrowing-preflight.md), asserted as
# case-insensitive keyword markers, not prose:
PROMPT_MARKERS = {
    "acceptance checks": re.compile(r"acceptance", re.IGNORECASE),
    "unknowns/manual verification": re.compile(
        r"unknown|manual verification", re.IGNORECASE),
    "prerequisites/reuse": re.compile(
        r"prerequisite|reuse|existing", re.IGNORECASE),
}

# Generic (scorecard-free) default: a manifest with zero coverage entries is
# unconditionally broken; anything above that is plan-specific and stays a
# scorecard-only minimum (see omi_regression_harness.py's min_coverage_entries).
GENERIC_MIN_MANIFEST_ENTRIES = 1

# ODC rejects a Setting default value above this many characters. Declared
# defaults use the `Default Value:` label (see SKILL.md Pseudocode Authoring
# Rules) with a bounded grammar, parsed in a single pass that never reads
# labels inside fenced blocks:
# - inline form: the remainder of the label's line, surrounding whitespace
#   trimmed; wrap the value in a backtick code span to preserve exact
#   characters (including boundary whitespace).
# - fenced form: an empty label whose next non-blank line opens a fence
#   (backtick or tilde, three or more delimiters); the literal is the fence
#   body verbatim. Anything else after an empty label, or an unclosed fence,
#   is a malformed declaration.
SETTING_DEFAULT_MAX_CHARS = 2000
SETTING_DEFAULT_LABEL = re.compile(r"Default Value\s*:(.*)$", re.IGNORECASE)
FENCE_OPEN = re.compile(r"^(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"^(`+)(.*)\1$", re.DOTALL)


def scan_placeholders(text):
    failures = []
    for regex in PLACEHOLDER_REGEXES:
        match = regex.search(text)
        if match:
            failures.append({"check": "placeholder_text",
                             "detail": f"unresolved placeholder {match.group(0)!r}"})
    for literal in MANIFEST_TEMPLATE_LITERALS:
        if literal in text:
            failures.append({"check": "template_literal",
                             "detail": f"unresolved manifest template {literal!r}"})
    return failures


def _fence_close_index(lines, start, marker, width):
    """Index of the line closing a fence opened before `start`, or None."""
    for index in range(start, len(lines)):
        stripped = lines[index].strip()
        if stripped and set(stripped) == {marker} and len(stripped) >= width:
            return index
    return None


def check_setting_defaults(text):
    """Measure every declared Setting default against the ODC 2,000-char cap.

    Single pass over the document: fenced blocks are skipped whole (labels
    inside them are content, not declarations), and each declaration is
    parsed with the bounded grammar documented above.
    """
    failures = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        fence = FENCE_OPEN.match(stripped)
        if fence:
            close = _fence_close_index(
                lines, index + 1, fence.group(1)[0], len(fence.group(1)))
            if close is None:
                break  # unclosed document-level fence: the rest is content
            index = close + 1
            continue
        match = SETTING_DEFAULT_LABEL.search(lines[index])
        if not match:
            index += 1
            continue
        inline = match.group(1).strip()
        if inline:
            span = CODE_SPAN.match(inline)
            literal = span.group(2) if span else inline
            if len(literal) > SETTING_DEFAULT_MAX_CHARS:
                failures.append({
                    "check": "setting_default_length",
                    "detail": (f"Setting Default Value literal is {len(literal)} characters; "
                               f"ODC caps Setting defaults at {SETTING_DEFAULT_MAX_CHARS}")})
            index += 1
            continue
        # Empty label: the fenced form requires a fence as the next non-blank
        # syntactic item; anything else is a malformed declaration.
        follow = index + 1
        while follow < len(lines) and not lines[follow].strip():
            follow += 1
        fence = FENCE_OPEN.match(lines[follow].strip()) if follow < len(lines) else None
        if not fence:
            failures.append({
                "check": "setting_default_declaration",
                "detail": ("Setting Default Value declaration has no inline literal and "
                           "no fenced literal as the next non-blank item")})
            index += 1
            continue
        close = _fence_close_index(
            lines, follow + 1, fence.group(1)[0], len(fence.group(1)))
        if close is None:
            failures.append({
                "check": "setting_default_declaration",
                "detail": "Setting Default Value fenced literal is never closed"})
            break
        literal = "\n".join(lines[follow + 1:close])
        if len(literal) > SETTING_DEFAULT_MAX_CHARS:
            failures.append({
                "check": "setting_default_length",
                "detail": (f"Setting Default Value literal is {len(literal)} characters; "
                           f"ODC caps Setting defaults at {SETTING_DEFAULT_MAX_CHARS}")})
        index = close + 1
    return failures


def check_manifest(text, min_entries):
    failures = []
    for marker in MANIFEST_REQUIRED_MARKERS:
        if not re.search(rf"^{re.escape(marker)}", text, re.MULTILINE):
            failures.append({"check": "manifest_marker",
                             "detail": f"missing manifest marker {marker!r}"})
    if failures:
        return failures
    entries = len(re.findall(r"source_requirement:", text))
    if entries < min_entries:
        failures.append({
            "check": "coverage_entries",
            "detail": f"coverage_map has {entries} entries, expected >= {min_entries}"})
    coverage_start = re.search(r"^coverage_map:", text, re.MULTILINE).start()
    dependency_start = re.search(r"^dependency_order:", text, re.MULTILINE).start()
    blocks_start = re.search(r"^blocks:", text, re.MULTILINE).start()
    coverage_region = text[coverage_start:dependency_start]
    dependency_region = text[dependency_start:blocks_start]
    coverage_ids = set(re.findall(r"block_id:\s*(\S+)", coverage_region))
    for block_id in sorted(coverage_ids):
        if not re.search(rf"^\s*-\s*{re.escape(block_id)}\s*$",
                         dependency_region, re.MULTILINE):
            failures.append({
                "check": "dependency_order",
                "detail": f"coverage_map block {block_id!r} missing from dependency_order"})
    return failures


def split_prompt_blocks(text):
    """Bodies of every ### Mentor Studio Prompt section (to the next ### heading)."""
    blocks = []
    for match in re.finditer(rf"^{re.escape(PROMPT_HEADING)}\s*$", text, re.MULTILINE):
        rest = text[match.end():]
        nxt = re.search(r"^### ", rest, re.MULTILINE)
        blocks.append(rest[: nxt.start()] if nxt else rest)
    return blocks


def check_prompt_structure(text, min_blocks):
    failures = []
    blocks = split_prompt_blocks(text)
    if min_blocks and len(blocks) < min_blocks:
        failures.append({
            "check": "prompt_block_count",
            "detail": f"found {len(blocks)} Mentor prompt block(s), expected >= {min_blocks}"})
    for index, block in enumerate(blocks, start=1):
        for name, regex in PROMPT_MARKERS.items():
            if not regex.search(block):
                failures.append({
                    "check": "paste_safe_contents",
                    "detail": f"Mentor prompt block {index} missing {name} marker"})
        # One requirement per Mentor prompt (prompt-narrowing-preflight.md):
        # a merged/concatenated prompt carries multiple acceptance-check
        # clusters; a single paste-safe message carries exactly one.
        if len(re.findall(r"acceptance checks?\s*:", block, re.IGNORECASE)) > 1:
            failures.append({
                "check": "merged_prompt",
                "detail": (f"Mentor prompt block {index} carries multiple "
                           "acceptance-check clusters - merged requirements "
                           "suspected (one requirement per Mentor prompt)")})
    return failures


def check_plan_to_mentor_subsections(text):
    """Required subsections inside the plan-to-mentor pseudocode section.

    Scoped to the region between `## Studio-Native Pseudocode` and
    `## Mentor Executable Sessions`, so a subsection heading that drifted into
    the sessions package reads as missing rather than as satisfied. When the
    pseudocode section itself is absent the section-order check already names
    that, so nothing is reported here.
    """
    start = find_heading_position(text, PLAN_TO_MENTOR_PSEUDOCODE_HEADING)
    if start == -1:
        return []
    end = find_heading_position(text, PLAN_TO_MENTOR_SESSIONS_HEADING)
    region = text[start:end] if end > start else text[start:]

    failures = []
    last = -1
    for heading in PLAN_TO_MENTOR_SUBSECTIONS:
        index = find_heading_position(region, heading)
        if index == -1:
            failures.append({
                "check": "pseudocode_subsection",
                "detail": (f"missing subsection {heading!r} inside "
                           f"{PLAN_TO_MENTOR_PSEUDOCODE_HEADING!r}")})
        elif index < last:
            failures.append({
                "check": "pseudocode_subsection",
                "detail": f"subsection {heading!r} out of order"})
        else:
            last = index
    return failures


def _named_elements(items, key="name"):
    """Non-empty string `key` values, in artifact order, from a list of dicts."""
    names = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            names.append(value.strip())
    return names


def blueprint_scope_names(blueprint):
    """(kind, name) pairs an enriched blueprint puts in scope for the build.

    Screens and entities only - `blocks`, `roles` and region-level names are
    outside the narrowed scope of this check. An entity flagged
    ``exists: true`` stays in scope: the build still has to name it to verify
    or reuse it (see blueprint_intake_plan.build_intake_plan).
    """
    pairs = [("screen", name) for name in _named_elements(blueprint.get("screens"))]
    pairs += [("entity", name) for name in _named_elements(blueprint.get("entities"))]
    return pairs


def inventory_scope_names(inventory):
    """(kind, name) pairs a screen inventory puts in scope for the build.

    Screens, plus the entity-kind data bindings they declare. Action bindings
    are excluded on purpose: an action's name is born in the capability plan,
    not the inventory (screen-inventory.schema.json, `introduced_here`), so the
    inventory is not authoritative for it. Candidates are not read either -
    a dissolved candidate is by definition not a destination, and a mapped one
    already resolves to a screen in ``screens``.
    """
    pairs = []
    for screen in inventory.get("screens") if isinstance(inventory.get("screens"), list) else []:
        if not isinstance(screen, dict):
            continue
        name = screen.get("name")
        if isinstance(name, str) and name.strip():
            pairs.append(("screen", name.strip()))
        for binding in screen.get("data_bindings") if isinstance(
                screen.get("data_bindings"), list) else []:
            if not isinstance(binding, dict) or binding.get("kind") != "entity":
                continue
            bound = binding.get("name")
            if isinstance(bound, str) and bound.strip():
                pairs.append(("entity", bound.strip()))
    return pairs


def _is_named(text, name):
    """True when `name` appears in `text` as a whole identifier.

    Exact spelling is required - a longer identifier that merely contains the
    name does not satisfy it. This is the same source-spelling-preservation
    rule the Mentor session contract already imposes (SKILL.md, `Traps`), so
    `Orders` does not stand in for an element the artifact spells `Order`.
    """
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_])",
                     text) is not None


def check_source_fidelity(text, blueprint=None, inventory=None):
    """Omission half of the prompt-hop fidelity lint.

    Returns ``(failures, checked)`` where `checked` is how many distinct
    in-scope names were measured - a caller can tell a real pass from a
    vacuous one.

    OMISSION ONLY. The invention direction - a PascalCase name in the answer
    that resolves to nothing in the source artifact - is explicitly held as a
    separate, evidence-gated experiment (fx-blueprint disposition, W1.5 group
    O3): upstream gets it free from a structural node index, whereas here it
    would need a name regex plus a whole-widget-surface allowlist, and a wrong
    allowlist flags correct answers.

    Both artifacts are optional because a lint run may be scoped to a partial
    answer; pass them only when the answer is the full build handoff derived
    from them, or every screen it legitimately does not cover reads as an
    omission.
    """
    failures = []
    pairs = []
    for label, artifact, extract in (
            ("blueprint", blueprint, blueprint_scope_names),
            ("inventory", inventory, inventory_scope_names)):
        if artifact is None:
            continue
        if not isinstance(artifact, dict):
            failures.append({
                "check": "source_artifact",
                "detail": f"{label} artifact is not a JSON object"})
            continue
        found = extract(artifact)
        if not found:
            failures.append({
                "check": "source_artifact",
                "detail": (f"{label} artifact declares no in-scope screens or "
                           "entities - there is nothing to check the answer against")})
        pairs += [(label, kind, name) for kind, name in found]

    seen = set()
    checked = 0
    for label, kind, name in pairs:
        if (kind, name) in seen:
            continue
        seen.add((kind, name))
        checked += 1
        if not _is_named(text, name):
            failures.append({
                "check": "source_omission",
                "detail": (f"{label} {kind} {name!r} is in scope but is never "
                           "named in the answer")})
    return failures, checked


def lint(text, mode, blueprint=None, inventory=None):
    """Failures only. Use lint_report when the in-scope name count is wanted."""
    return lint_report(text, mode, blueprint, inventory)[0]


def lint_report(text, mode, blueprint=None, inventory=None):
    expected = {
        "required_sections_in_order": MODE_SECTIONS[mode],
        "allowed_evidence_labels": ALL_LABELS,
        "required_phrases": [],
        "forbidden_phrases": (
            MUTATION_TOOL_IDENTIFIERS if mode in TOOL_NAME_FORBIDDEN_MODES else []),
    }
    failures = check(text, expected)

    if re.search(r"^## Evidence Status\s*$", text, re.MULTILINE):
        failures.append({
            "check": "heading_level",
            "detail": "Evidence Status must use the h3 heading `### Evidence Status`",
        })

    unknowns_idx = find_heading_position(text, "### Unknowns And Fallback Behavior")
    evidence_idx = find_heading_position(text, "### Evidence Status")
    if unknowns_idx != -1 and evidence_idx != -1 and unknowns_idx < evidence_idx:
        failures.append({
            "check": "section_order",
            "detail": "### Unknowns And Fallback Behavior must follow ### Evidence Status",
        })

    if mode == PLAN_TO_MENTOR_MODE:
        failures += check_plan_to_mentor_subsections(text)

    # Generic shape checks - no scorecard needed, run on every answer.
    failures += scan_placeholders(text)
    failures += check_prompt_structure(text, min_blocks=0)
    failures += check_setting_defaults(text)
    if re.search(r"^coverage_map:", text, re.MULTILINE):
        failures += check_manifest(text, GENERIC_MIN_MANIFEST_ENTRIES)

    # Opt-in source-fidelity check: runs only when an artifact was supplied.
    fidelity, checked = check_source_fidelity(text, blueprint, inventory)
    failures += fidelity

    return failures, checked


def _load_artifact(path, label, failures):
    """Parse a source artifact, or record why it could not be read."""
    if path is None:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        failures.append({
            "check": "source_artifact",
            "detail": f"{label} artifact {str(path)!r} could not be read: {error}"})
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--answer", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=sorted(MODE_SECTIONS))
    parser.add_argument("--blueprint", type=Path,
                        help="enriched blueprint JSON this answer was built from; "
                             "every screen and entity it declares must be named "
                             "in the answer")
    parser.add_argument("--inventory", type=Path,
                        help="screen inventory JSON this answer was built from; "
                             "every screen and entity binding it declares must be "
                             "named in the answer")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    artifact_failures = []
    blueprint = _load_artifact(args.blueprint, "blueprint", artifact_failures)
    inventory = _load_artifact(args.inventory, "inventory", artifact_failures)

    failures, checked = lint_report(
        args.answer.read_text(encoding="utf-8"), args.mode, blueprint, inventory)
    failures = artifact_failures + failures
    if args.json:
        print(json.dumps({"mode": args.mode, "pass": not failures,
                          "source_names_checked": checked, "failures": failures},
                         indent=2))
    else:
        for failure in failures:
            print(f"FAIL [{failure['check']}] {failure['detail']}")
        print("PASS" if not failures else f"{len(failures)} failure(s)")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
