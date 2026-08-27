#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


PATTERN_ROOT = Path("src/eap/building-apps/ui/patterns")
DEFAULT_REPO_URL = "https://github.com/OutSystems/docs-odc.git"
SOURCE_BASE_URL = "https://github.com/OutSystems/docs-odc/blob/main"
FAMILIES = {"adaptive", "content", "interaction", "navigation", "numbers", "utilities"}
# The dormant OutSystems/outsystems-frontend-skills snapshot (tip c7a376e7d,
# 2026-07-20). It is a CROSS-CHECK, never an authority -- the official ODC docs
# are, and the catalog this script writes is identical with or without it.
#
# The snapshot is an unzipped folder outside this repo that no colleague has, so
# this constant has NO built-in default: it comes from
# OUTSYSTEMS_FRONTEND_SKILLS_PATH or --upstream-cross-check, and is None when
# neither is set. It previously defaulted to the maintainer's own absolute path,
# which resolved on exactly one machine, shipped inside the colleague pack, and
# told every other reader the cross-check was skipped because a directory they
# have never heard of is missing.
_ENV_CROSS_CHECK = os.environ.get("OUTSYSTEMS_FRONTEND_SKILLS_PATH")
UPSTREAM_CROSS_CHECK = Path(_ENV_CROSS_CHECK) if _ENV_CROSS_CHECK else None

# The official ODC docs document six OutSystemsUI client actions OUTSIDE the
# pattern pages, in the Accessibility subtree -- the "Logic > OutSystemsUI >
# Accessibility" folder in ODC Studio. PATTERN_ROOT does not reach them, which
# is the whole reason they were missing from the catalog.
ACCESSIBILITY_ROOT = Path("src/eap/building-apps/ui/accessibility")

# Populated from a VERIFIED ALLOWLIST rather than a regex, deliberately.
# Measured 2026-08-23 against docs-odc tip bfbee88: a conservative
# bold-CamelCase-near-"action" rule over this subtree yields these six plus
# seven tokens that are not actions, and one of those seven --
# SkipToContentOnClick -- is phrased by the docs exactly like a real action
# ("Double-click the **SkipToContentOnClick** action") while the real action on
# the very next line is called a "node". No adjacency rule can separate them,
# so a rule here would either invent SkipToContentOnClick or drop
# SkipToContent. Each row below is verified against its cited doc at generation
# time, and anything new in the subtree is reported as a candidate for a human
# -- never auto-added.
_ACCESSIBILITY_INTRO = ACCESSIBILITY_ROOT / "intro.md"
_ACCESSIBILITY_PATTERNS = ACCESSIBILITY_ROOT / "ui-patterns-accessibility-reference.md"

ACCESSIBILITY_CLIENT_ACTIONS = (
    {
        "name": "SetFocus",
        "purpose": "Move keyboard focus to a named widget (WidgetId), for example "
                   "highlighting an input when a screen with a form opens.",
        "doc_path": _ACCESSIBILITY_INTRO,
    },
    {
        "name": "SkipToContent",
        "purpose": "Send keyboard focus past the layout chrome to the main content "
                   "region (TargetId). The layout's own SkipToContentOnClick screen "
                   "action wraps this node -- SkipToContent is the framework action.",
        "doc_path": _ACCESSIBILITY_INTRO,
    },
    {
        "name": "ToggleTextSpacing",
        "purpose": "Let the user increase text spacing for readability; call it from "
                   "an action wired to a control the user operates.",
        "doc_path": _ACCESSIBILITY_INTRO,
    },
    {
        "name": "SetAccessibilityRole",
        "purpose": "Set a widget's ARIA role at runtime (WidgetId, Role) -- for "
                   "example giving an Alert the \"status\" role.",
        "doc_path": _ACCESSIBILITY_PATTERNS,
    },
    {
        "name": "SetAriaHidden",
        "purpose": "Update a widget's aria-hidden attribute when toggling its "
                   "visibility, so assistive technology follows the change.",
        "doc_path": _ACCESSIBILITY_PATTERNS,
    },
    {
        "name": "MasterDetailSetContentFocus",
        "purpose": "Switch focus to the Master Detail pattern's detail pane, "
                   "preferably after the pane is populated.",
        "doc_path": _ACCESSIBILITY_PATTERNS,
    },
)

# Bold CamelCase tokens in the accessibility subtree that are NOT client
# actions. Measured 2026-08-23; each carries the reason it is excluded, so the
# candidate scan below stays silent on today's docs and speaks only on change.
ACCESSIBILITY_NON_ACTIONS = {
    "ListItem": "a pattern name (\"Open the **ListItem** pattern\")",
    "ListItemOnClick": "a walkthrough invention (\"for example, **ListItemOnClick**\")",
    "MainContent": "a widget the reader names (\"if you name your element\")",
    "OutSystemsUI": "a Logic-tree breadcrumb, not a leaf action",
    "SkipToContentOnClick": "the layout's own screen action, which wraps SkipToContent",
    "TargetId": "a property (\"edit the **TargetId** in the action properties\")",
    "TextSpacing": "a walkthrough invention (\"Set the action name as **TextSpacing**\")",
}

# Baseline for the upstream cross-check, recorded 2026-08-23 against docs-odc
# tip bfbee88 and the dormant snapshot (tip c7a376e7d, frozen 2026-07-20).
#
# 155 upstream names; this generator documents 12 of them; the other 143 appear
# NOWHERE in the whole docs-odc repo (937 .md files, measured) -- the official
# docs simply do not name them, so no extractor change can recover them.
# Printing one warning per name produced 149 lines nothing consumed and nothing
# could act on. Only the COUNT and a DIGEST of those 143 are recorded: the
# snapshot is machine-local and is a cross-check, never an authority, so its
# names must not enter this repo. The 12 documented names are recorded in full
# because they are already published in the catalog this script generates.
UNDOCUMENTED_UPSTREAM_BASELINE_COUNT = 143
UNDOCUMENTED_UPSTREAM_BASELINE_DIGEST = (
    "25f8544d88e5f947d649345f49653e095bd60695a195ef3097b2a3320c8dd214"
)
DOCUMENTED_UPSTREAM_BASELINE = (
    "BottomSheetClose",
    "BottomSheetOpen",
    "MasterDetailSetContentFocus",
    "NotificationClose",
    "NotificationOpen",
    "SetAccessibilityRole",
    "SetAriaHidden",
    "SetFocus",
    "SidebarClose",
    "SidebarOpen",
    "SkipToContent",
    "ToggleTextSpacing",
)


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data = {}
    current_key = None
    for line in raw.splitlines():
        if not line.strip():
            continue
        if line.startswith("  - ") and current_key:
            data.setdefault(current_key, []).append(line[4:].strip())
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip().strip('"')
            data[current_key] = value if value else []
    return data, body


def first_heading(body, fallback):
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    if match:
        return re.sub(r"`|\*", "", match.group(1)).strip()
    return fallback.stem.replace("-", " ").title()


def first_paragraph(body):
    lines = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!") or line.startswith("<"):
            if lines:
                break
            continue
        if line.startswith("|") or line.startswith("1.") or line.startswith("- "):
            if lines:
                break
            continue
        lines.append(re.sub(r"\s+", " ", line))
    return " ".join(lines)


def parse_properties(body):
    mandatory = []
    optional = []
    section_match = re.search(r"^## Properties\s*\n(?P<section>.*?)(?=^##\s+|\Z)", body, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if not section_match:
        return mandatory, optional
    for table_match in re.finditer(r"(?P<table>(?:^\|.*\n?)+)", section_match.group("section"), re.MULTILINE):
        for line in table_match.group("table").splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2 or cells[0].lower() == "property" or set(cells[0]) <= {"-", ":"}:
                continue
            prop_name = cells[0].split("(")[0].strip()
            if "mandatory" in cells[0].lower():
                mandatory.append(prop_name)
            elif "optional" in cells[0].lower():
                optional.append(prop_name)
    return sorted(set(mandatory)), sorted(set(optional))


def extract_events(body):
    non_events = {"OnPhone", "OnTablet", "OnDesktop"}
    events = set()
    for event in re.findall(r"\bOn[A-Z][A-Za-z0-9]+", body):
        if event not in non_events:
            events.add(event)
    return sorted(events)


# Bold CamelCase tokens that appear beside the phrase "client action" but are
# not actions: parameter names, UI chrome, and branch labels.
CLIENT_ACTION_DENYLIST = {
    "WidgetId", "Properties", "Select", "Name", "Text", "True", "False",
    "Toolbox", "Content", "Header", "Id", "Condition", "Assign", "If",
    "StartIndex", "NewStartIndex",
}


def extract_client_actions(body):
    """Client actions the docs name for driving a pattern from an action flow.

    Scoped to blocks (blank-line separated) that actually mention a client
    action, then filtered to single-word CamelCase tokens that are not chrome.
    A document-wide regex over CamelCase would emit widget names and property
    names as actions -- see the negative tests.
    """
    # Tokens the docs explicitly call out as a local variable anywhere in the
    # document (e.g. "set the **IsOpened** local variable to **True**") are
    # never client actions -- even in a later block that re-mentions the same
    # token without the "local variable" marker attached (docs re-mention a
    # walkthrough-picked name in prose without repeating why it isn't an
    # action). Scanned over the whole body, not per block, for that reason.
    local_vars = set(
        re.findall(r"\*\*([A-Za-z][A-Za-z0-9]*)\*\*\s+local variable", body)
    )
    # Tokens the docs introduce with "we call it X" / "we call the Y X"
    # are a name the walkthrough's author picked for something they just
    # told the reader to create (a client action, a local variable, a
    # button, an aggregate) -- never a name the framework defines. Real
    # client action mentions are imperative ("call the X client action",
    # "add the X client action") and never carry the "we" pronoun.
    # Measured: every "we call" occurrence in the docs-odc corpus names a
    # local variable, button, or aggregate, never a real client action.
    # Scanned over the whole body (not per block): the same walkthrough name
    # is routinely re-mentioned in a later block without the "we call"
    # marker (e.g. Master Detail's ClickSelectedUser, introduced once and
    # referenced again several paragraphs later).
    walkthrough_named = set(
        re.findall(r"\bwe call\b[^*\n]{0,40}\*\*([A-Za-z][A-Za-z0-9]*)\*\*", body, re.IGNORECASE)
    )
    found = set()
    for block in re.split(r"\n\s*\n", body):
        if "client action" not in block.lower():
            continue
        # A block that explicitly drags a "Run Server Action" step names the
        # server action it selects the same way a Run Client Action step
        # names its client action ("the X action"), but it is the wrong step
        # type. Gated on "run server action" being present in the SAME block
        # so it cannot reach into an unrelated "the X action" mention (e.g.
        # the Bottom Sheet fixture's "navigate to the BottomSheetOpen action").
        server_action_named = set()
        if re.search(r"run server action", block, re.IGNORECASE):
            server_action_named = set(
                re.findall(r"\*\*([A-Za-z][A-Za-z0-9]*)\*\*\s+action\b", block, re.IGNORECASE)
            )
        for token in re.findall(r"\*\*([A-Za-z][A-Za-z0-9]*)\*\*", block):
            if (
                token in CLIENT_ACTION_DENYLIST
                or token in local_vars
                or token in walkthrough_named
                or token in server_action_named
            ):
                continue
            if not re.fullmatch(r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+", token):
                continue
            # On* tokens are event-handler names (OnClick, OnSelect, ...),
            # already surfaced separately by extract_events. Measured against
            # the upstream client-action catalog (155 names, 2026-08-22): none
            # start with "On", so excluding the whole prefix loses no real
            # action while dropping event names that share a block with the
            # phrase "client action" (e.g. "the On Click dropdown ... New
            # Client Action").
            if re.match(r"^On[A-Z]", token):
                continue
            # *WidgetId is the recurring "which widget instance" parameter
            # (WidgetId, GridWidgetId, ...) passed alongside a real action
            # call, not an action itself. Measured against the upstream
            # catalog: no client action name ends in "WidgetId".
            if token.endswith("WidgetId"):
                continue
            found.add(token)
    return sorted(found)


def cross_check_upstream(entries, upstream_path, extra_known=None):
    """Split the upstream names into (missing, documented) against our pass.

    OutSystems/outsystems-frontend-skills is dormant (tip c7a376e7d,
    2026-07-20) and is NOT an authority -- the official ODC docs are. This
    measures the delta without letting the private repo write entries into the
    catalog. summarize_cross_check() turns the split into a one-line summary or
    a named alarm; see its docstring for why this is no longer a warning list.
    """
    upstream_path = Path(upstream_path)
    if not upstream_path.is_file():
        return [], []
    text = upstream_path.read_text(encoding="utf-8")
    # Read ONLY the first column of the catalog tables. The file backticks
    # parameter names as densely as action names, so a regex over backticked
    # CamelCase anywhere returns 241 candidates -- mostly parameters. The
    # table's first column returns 155, all of them actions. Deprecated
    # aliases live in prose, not table rows, so they are excluded for free.
    catalog = text[text.index("\n## Catalog"):]
    upstream_names = set(
        re.findall(r"^\|\s*`([A-Za-z][A-Za-z0-9]*)`\s*\|", catalog, re.M)
    )
    known = set(extra_known or ())
    for entry in entries:
        known.update(entry.get("client_actions", []))
    missing = sorted(upstream_names - known)
    documented = sorted(upstream_names & known)
    return missing, documented


def accessibility_action_names():
    """The names on the verified accessibility allowlist."""
    return [action["name"] for action in ACCESSIBILITY_CLIENT_ACTIONS]


def verify_accessibility_client_actions(source_root):
    """Verify the accessibility allowlist against the docs; report drift.

    Returns (entries, warnings). An allowlisted action whose cited doc no
    longer names it is DROPPED and warned about, so the catalog never outlives
    its evidence. A bolded, action-shaped token in the subtree that is neither
    allowlisted nor a known non-action is reported as a candidate for a human
    to verify -- never auto-added, so this cannot invent an action name.
    """
    source_root = Path(source_root)
    root = source_root / ACCESSIBILITY_ROOT
    if not root.is_dir():
        return [], [
            f"{ACCESSIBILITY_ROOT.as_posix()}: accessibility subtree not found in "
            "this docs-odc checkout; its client actions were not verified"
        ]

    texts = {}
    for path in sorted(root.rglob("*.md")):
        texts[path.relative_to(source_root).as_posix()] = path.read_text(
            encoding="utf-8", errors="replace"
        )

    entries = []
    warnings = []
    for action in ACCESSIBILITY_CLIENT_ACTIONS:
        doc = Path(action["doc_path"]).as_posix()
        body = texts.get(doc, "")
        if f"**{action['name']}**" not in body:
            warnings.append(
                f"{action['name']}: no longer named in {doc} -- the official docs "
                "may have renamed or dropped it; verify against "
                "success.outsystems.com and update the allowlist"
            )
            continue
        entries.append(
            {
                "name": action["name"],
                "purpose": action["purpose"],
                "doc_path": doc,
                "source_url": f"{SOURCE_BASE_URL}/{doc}",
                "studio_location": "Logic > OutSystemsUI > Accessibility",
                "evidence_status": "Current official",
            }
        )

    listed = set(accessibility_action_names())
    candidates = set()
    for doc, body in texts.items():
        for block in re.split(r"\n\s*\n", body):
            if "action" not in block.lower():
                continue
            for token in re.findall(r"\*\*([A-Za-z][A-Za-z0-9]*)\*\*", block):
                if (
                    token in listed
                    or token in ACCESSIBILITY_NON_ACTIONS
                    or token in CLIENT_ACTION_DENYLIST
                ):
                    continue
                if not re.fullmatch(r"[A-Z][a-z0-9]+(?:[A-Z][a-z0-9]*)+", token):
                    continue
                if re.match(r"^On[A-Z]", token) or token.endswith("WidgetId"):
                    continue
                candidates.add((token, doc))
    for token, doc in sorted(candidates):
        warnings.append(
            f"{token}: bolded beside 'action' in {doc} but not on the verified "
            "accessibility allowlist -- check success.outsystems.com and add it "
            "if it is a real client action"
        )
    entries.sort(key=lambda item: item["name"])
    return entries, warnings


def _digest(names):
    return hashlib.sha256("\n".join(sorted(names)).encode("utf-8")).hexdigest()


def summarize_cross_check(missing, documented, baseline=None):
    """Collapse the upstream delta to one line, or raise a named alarm.

    143 of the delta can never resolve (the official docs do not name those
    actions at all), so a per-name warning list was 149 lines nothing consumed.
    What IS worth knowing is movement: OutSystems newly documenting an action,
    or one disappearing. Returns (lines, changed).
    """
    if baseline is None:
        baseline = {
            "count": UNDOCUMENTED_UPSTREAM_BASELINE_COUNT,
            "digest": UNDOCUMENTED_UPSTREAM_BASELINE_DIGEST,
            "documented": DOCUMENTED_UPSTREAM_BASELINE,
        }
    missing = sorted(missing)
    documented = sorted(documented)
    digest = _digest(missing)
    baseline_documented = sorted(baseline.get("documented", ()))

    if digest == baseline["digest"] and len(missing) == baseline["count"]:
        return (
            [
                f"cross_check: {len(missing)} upstream client-action names remain "
                f"undocumented in the official ODC docs; {len(documented)} are "
                "documented and in the catalog -- unchanged from the recorded "
                f"baseline (digest {digest[:12]})"
            ],
            False,
        )

    lines = [
        "cross_check: ALARM -- the upstream delta moved from the recorded baseline.",
        f"  recorded: undocumented={baseline['count']} digest={baseline['digest'][:12]}",
        f"  measured: undocumented={len(missing)} digest={digest[:12]}",
    ]
    newly = [name for name in documented if name not in baseline_documented]
    lost = [name for name in baseline_documented if name not in documented]
    if newly:
        lines.append(
            "  newly documented by the official docs (add to the catalog's "
            f"coverage story): {', '.join(newly)}"
        )
    if lost:
        lines.append(
            "  no longer documented by the official docs (verify before "
            f"relying on them): {', '.join(lost)}"
        )
    if not newly and not lost:
        lines.append(
            "  the undocumented set changed without any documented name moving "
            "-- the upstream snapshot itself likely changed"
        )
    lines.append(
        "  if this is expected, update UNDOCUMENTED_UPSTREAM_BASELINE_COUNT/"
        "_DIGEST and DOCUMENTED_UPSTREAM_BASELINE in this script."
    )
    return lines, True


def extract_placeholders(body):
    placeholders = set()
    for match in re.findall(r"\b([A-Z][A-Za-z0-9]*Content)\b", body):
        placeholders.add(match)
    if "placeholder" in body.lower():
        placeholders.add("Pattern placeholders described in source")
    return sorted(placeholders)


def extract_notes(body, keywords):
    notes = []
    for paragraph in re.split(r"\n\s*\n", body):
        clean = re.sub(r"\s+", " ", paragraph.strip())
        if not clean:
            continue
        if clean.startswith(("#", "|", "![")):
            continue
        lowered = clean.lower()
        if any(re.search(rf"\b{re.escape(keyword)}\b", lowered) for keyword in keywords):
            notes.append(clean)
    return notes[:4]


def extract_compatibility_notes(body):
    notes = []
    compatibility_patterns = [
        r"\bcompatib(?:le|ility)\b",
        r"\bincompatib(?:le|ility)\b",
        r"\b(?:applies|apply)\s+to\b",
        r"\bnote\s*:",
        r"\bavoid\s+using\b.*\balone\b",
        r"\bdo\s+not\s+use\b.*\balone\b",
    ]
    for paragraph in re.split(r"\n\s*\n", body):
        clean = re.sub(r"\s+", " ", paragraph.strip())
        if not clean:
            continue
        if clean.startswith(("#", "|", "![", "- ")):
            continue
        if re.match(r"^\d+\.", clean):
            continue
        if "in this example" in clean.lower():
            continue
        if any(re.search(pattern, clean, re.IGNORECASE) for pattern in compatibility_patterns):
            notes.append(clean)
    return notes[:4]


def family_for(path):
    try:
        family = path.relative_to(PATTERN_ROOT).parts[0]
    except ValueError:
        family = path.parts[-2] if len(path.parts) > 1 else "unknown"
    return family if family in FAMILIES else "unknown"


def catalog_entry(source_root, markdown_path):
    relative = markdown_path.relative_to(source_root)
    text = markdown_path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(text)
    title = first_heading(body, markdown_path)
    purpose = frontmatter.get("summary") or first_paragraph(body)
    mandatory, optional = parse_properties(body)
    events = extract_events(body)
    client_actions = extract_client_actions(body)
    placeholders = extract_placeholders(body)
    compatibility = extract_compatibility_notes(body)
    security = extract_notes(body, ["sanitize", "security", "safe", "html", "script", "injection"])
    applies_to = frontmatter.get("app_type", "")
    if isinstance(applies_to, str):
        applies_to = [item.strip() for item in applies_to.split(",") if item.strip()]
    entry = {
        "name": title,
        "family": family_for(relative),
        "doc_path": str(relative),
        "source_url": f"{SOURCE_BASE_URL}/{relative.as_posix()}",
        "purpose": purpose,
        "applies_to": applies_to,
        "mandatory_properties": mandatory,
        "important_optional_properties": optional,
        "events": events,
        "client_actions": client_actions,
        "placeholders": placeholders,
        "data_binding_shape": infer_data_binding_shape(body),
        "compatibility_notes": compatibility,
        "security_or_sanitization_notes": security,
        "mentor_prompt_fragment": (
            f"Use the {title} pattern and configure its documented properties "
            "before wiring events."
            + (f" Drive it from an action flow with: {', '.join(client_actions)}."
               if client_actions else "")
        ),
        "evidence_status": "Current official",
    }
    warnings = []
    if not mandatory and not optional:
        warnings.append(f"{relative}: missing properties table")
    if not title:
        warnings.append(f"{relative}: missing title")
    return entry, warnings


def infer_data_binding_shape(body):
    lowered = body.lower()
    shapes = []
    if "aggregate" in lowered or "fetch data" in lowered:
        shapes.append("usually binds to an Aggregate or Data Action result")
    if "source" in lowered and "list" in lowered:
        shapes.append("list source binding is documented")
    if "optionslist" in lowered:
        shapes.append("requires an options list structure")
    if "value" in lowered and "label" in lowered:
        shapes.append("requires value and label bindings")
    return shapes


def iter_pattern_files(source_root):
    root = source_root / PATTERN_ROOT
    return sorted(path for path in root.rglob("*.md") if path.name != "intro.md")


def build_catalog(source_root):
    """Build the catalog from source_root.

    The warnings returned here are GENERATOR findings about the official docs
    -- a pattern page missing its properties table, and the like. They are
    reproducible by anyone who runs this script, so they are safe to serialise
    into the artifact. Cross-check output against the private upstream
    snapshot is deliberately NOT part of this list: it is machine-local, and
    committing it would make the artifact unreproducible. main() computes it
    separately and prints it.
    """
    source_root = Path(source_root)
    entries = []
    warnings = []
    for markdown_path in iter_pattern_files(source_root):
        entry, entry_warnings = catalog_entry(source_root, markdown_path)
        entries.append(entry)
        warnings.extend(entry_warnings)
    entries.sort(key=lambda item: (item["family"], item["name"]))
    return entries, warnings


def ensure_expected_family_coverage(entries):
    families = Counter(entry["family"] for entry in entries)
    missing = sorted(family for family in FAMILIES if families[family] == 0)
    if missing:
        raise ValueError(f"Missing expected pattern families: {', '.join(missing)}")


def write_catalog(entries, warnings, output_path, generated_at_utc=None,
                  accessibility_actions=()):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    families = dict(sorted(Counter(entry["family"] for entry in entries).items()))
    generated_at_utc = generated_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "generated_at_utc": generated_at_utc,
        "source_family": "official_outsystems_docs_odc",
        "source_pattern_root": str(PATTERN_ROOT),
        "summary": {
            "pattern_count": len(entries),
            "families": families,
            "warning_count": len(warnings),
            "accessibility_client_action_count": len(accessibility_actions),
        },
        "warnings": sorted(warnings),
        "accessibility_client_actions": list(accessibility_actions),
        "patterns": entries,
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def clone_repo(repo_url):
    tmp = tempfile.TemporaryDirectory()
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, tmp.name],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return tmp


def find_local_source():
    env_path = os.environ.get("OUTSYSTEMS_DOCS_ODC_PATH")
    candidates = []
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.extend(
        [
            Path.cwd() / "projects" / "docs-odc",
            Path.cwd() / "docs-odc",
            Path.home() / "Documents" / "Workspace" / "projects" / "docs-odc",
        ]
    )
    for candidate in candidates:
        if (candidate / PATTERN_ROOT).is_dir():
            return candidate
    return None


def main():
    parser = argparse.ArgumentParser(description="Refresh the ODC UI pattern catalog for outsystems-mentor-implementation.")
    parser.add_argument("--source", help="Path to a local OutSystems/docs-odc checkout.")
    parser.add_argument("--repo-url", default=DEFAULT_REPO_URL, help="Git repository to clone when --source is omitted.")
    parser.add_argument("--output", required=True, help="Output JSON catalog path.")
    parser.add_argument(
        "--strict-cross-check",
        action="store_true",
        help="Exit non-zero when the upstream delta moves from the recorded baseline.",
    )
    parser.add_argument(
        "--upstream-cross-check",
        default=UPSTREAM_CROSS_CHECK,
        help="Path to the dormant upstream client-action catalog to cross-check "
             "against. Optional: defaults to OUTSYSTEMS_FRONTEND_SKILLS_PATH, and "
             "the cross-check is skipped when neither is set.",
    )
    args = parser.parse_args()

    cloned = None
    if args.source:
        source_root = Path(args.source)
    else:
        source_root = find_local_source()
        if source_root is None:
            if not shutil.which("git"):
                raise SystemExit("git is required when --source is omitted and no local docs-odc checkout is found")
            cloned = clone_repo(args.repo_url)
            source_root = Path(cloned.name)

    entries, warnings = build_catalog(source_root)
    accessibility_actions, accessibility_warnings = verify_accessibility_client_actions(
        source_root
    )
    warnings.extend(accessibility_warnings)
    if not entries:
        raise SystemExit(f"No pattern Markdown files found under {source_root / PATTERN_ROOT}")
    try:
        ensure_expected_family_coverage(entries)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    write_catalog(entries, warnings, args.output,
                  accessibility_actions=accessibility_actions)
    print(f"patterns={len(entries)}")
    print(f"accessibility_client_actions={len(accessibility_actions)}")
    for family, count in sorted(Counter(entry["family"] for entry in entries).items()):
        print(f"{family}={count}")
    print(f"warnings={len(warnings)}")
    # Cross-check output goes to stdout, never into the artifact -- see
    # build_catalog's docstring.
    upstream_path = (
        Path(args.upstream_cross_check) if args.upstream_cross_check else None
    )
    if upstream_path is None:
        print(
            "cross_check_notes=skipped: no upstream snapshot configured. The "
            "catalog above is complete without it; set "
            "OUTSYSTEMS_FRONTEND_SKILLS_PATH or pass --upstream-cross-check to "
            "enable the optional cross-check."
        )
    elif upstream_path.is_file():
        missing, documented = cross_check_upstream(
            entries, upstream_path, extra_known=accessibility_action_names()
        )
        lines, changed = summarize_cross_check(missing, documented)
        for line in lines:
            print(line)
        if changed and args.strict_cross_check:
            raise SystemExit(
                "cross-check delta moved from the recorded baseline and "
                "--strict-cross-check is set"
            )
    else:
        print(
            f"cross_check_notes=skipped: no upstream snapshot at {upstream_path}. "
            "Set OUTSYSTEMS_FRONTEND_SKILLS_PATH to enable the cross-check."
        )
    if cloned:
        cloned.cleanup()


if __name__ == "__main__":
    main()
