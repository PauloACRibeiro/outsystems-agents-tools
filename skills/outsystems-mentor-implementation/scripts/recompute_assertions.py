#!/usr/bin/env python3
"""Recompute a blueprint's declared `assertions` against the BUILT model.

`outsystems-ui-design`'s validator recomputes each screen's `assertions` from
`main_content` - the blueprint against ITSELF. This recomputes the same
declared counts against what was actually built, which is a different question
and the one the Phase 1 trial proved nobody was asking.

Trial evidence (friction log F-17): at revision 254 a Mentor session reported
an Index dropdown, a query-text input and Apply/Clear buttons in its summary,
with `change_applied: true` and zero validation errors. None existed in the
model. The blueprint declared `buttons: 10, inputs: 1` and the build held 8
and 0 - a mechanical catch that nothing in the chain performed.

ORDERING: this is structurally a POST-PUBLISH check and cannot be moved
earlier. On the MCP route there is no element tree to inspect before publish -
session edits are server-side and the Context Service reflects only published
state. Run it after the publish gate (the model digest, never the platform's
change signals) has confirmed the revision landed.

Verdict semantics, chosen on the trial's own evidence:

  built <  declared  ->  SHORTFALL, a failure. This is the F-17 defect class:
                         the design promised widgets the build does not hold.
  built == declared  ->  VERIFIED.
  built >  declared  ->  VERIFIED, with the surplus reported as drift. A build
                         legitimately adds what the design never declared -
                         rev-265 grew a Clear-all button and its confirm pair
                         while every one of the 10 declared buttons was
                         present. Failing that would make the check unusable
                         on any real iterative build.

The check FAILS CLOSED: it exits 0 only when every declared assertion was
actually checked and satisfied. An assertion this source cannot see is
reported UNSUPPORTED and is never counted as a pass - a green verdict from a
gate that could not see is the exact failure F-17 shipped.

Usage:
    python3 recompute_assertions.py --blueprint <blueprint.json> --oml <path.oml>
    python3 recompute_assertions.py --blueprint <blueprint.json> \
        --context-json <context_screens payload.json>
"""

import json
import os
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# Must stay in step with outsystems-ui-design's `_ASSERTION_WIDGETS` (the
# producer of the declared side). Keys are the assertion names a blueprint
# declares; values are the built model's widget type, matched exactly - an
# exact match is what keeps `ButtonGroup` from counting as a `Button`, which
# would have turned rev-254's real shortfall into a false pass at exactly 10.
ASSERTION_WIDGETS = {"links": "Link", "buttons": "Button", "inputs": "Input"}

WIDGET_TYPE_PREFIX = "OutSystems.Plugin.NRWidgets."

CONTEXT_UNSUPPORTED = (
    "context_screens returns a screen inventory only (key, name, description, "
    "isPublic, timestamp, ownerAppKey, additionalData) and carries no widget "
    "data - use --oml, or verify these counts by runtime audit"
)


class AssertionResult:
    def __init__(self, screen, kind, declared, built, status, detail="", surplus=0):
        self.screen = screen
        self.kind = kind
        self.declared = declared
        self.built = built
        self.status = status
        self.detail = detail
        self.surplus = surplus

    def line(self):
        if self.status == "SCREEN_MISSING":
            return f"screen '{self.screen}': SCREEN_MISSING - {self.detail}"
        head = (f"screen '{self.screen}': {self.kind} declared {self.declared} "
                f"built {self.built if self.built is not None else '?'}")
        if self.status == "VERIFIED" and self.surplus:
            return (f"{head} VERIFIED (surplus {self.surplus} - the build holds "
                    "widgets the blueprint does not declare)")
        if self.status == "SHORTFALL":
            return f"{head} SHORTFALL ({self.declared - self.built} missing)"
        if self.status == "UNSUPPORTED":
            return f"{head} UNSUPPORTED - {self.detail}"
        return f"{head} VERIFIED"


class Report:
    def __init__(self, results, verified, summary):
        self.results = results
        self.verified = verified
        self.summary = summary

    def text(self):
        return "\n".join([r.line() for r in self.results] + [self.summary])


class OmlModelSource:
    """The internal source: an XRE graph converted from a published `.oml`.

    XRE is a node/edge graph with `_type` on every node and `relationType`
    on every edge, so the widget walk is depth-unlimited and follows
    containment only. Reach: internal - the OML-extraction CLI is an
    OutSystems-proprietary binary that is never distributed; its command
    name is supplied locally via the OML_EXTRACT_CLI environment variable
    and deliberately never appears in this file.
    """

    def __init__(self, graph):
        self._nodes = graph["nodes"]
        self._adj = defaultdict(list)
        for src, dst, attr in zip(graph["edgeSrc"], graph["edgeDst"], graph["edgeAttr"]):
            self._adj[src].append((dst, attr))

    def _screen_id(self, screen_name):
        for index, node in enumerate(self._nodes):
            # endswith rather than a substring test: `IClientScreenAction`
            # also contains "Screen".
            if node.get("Name") == screen_name and str(node.get("_type", "")).endswith("Screen"):
                return index
        return None

    def screen_exists(self, screen_name):
        return self._screen_id(screen_name) is not None

    def screen_widget_counts(self, screen_name):
        node_id = self._screen_id(screen_name)
        if node_id is None:
            return None
        counts = {kind: 0 for kind in ASSERTION_WIDGETS}
        seen = set()
        stack = [dst for dst, attr in self._adj[node_id]
                 if attr.get("_type") == "Widgets"]
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            node_type = str(self._nodes[node].get("_type", ""))
            if node_type.startswith(WIDGET_TYPE_PREFIX):
                leaf = node_type[len(WIDGET_TYPE_PREFIX):]
                for kind, widget in ASSERTION_WIDGETS.items():
                    if leaf == widget:
                        counts[kind] += 1
            for dst, attr in self._adj[node]:
                # Containment only. A block instance REFERENCES its definition;
                # walking that edge would import the layout menu's buttons and
                # links into every screen that uses the layout.
                if attr.get("relationType") == "Parent":
                    stack.append(dst)
        return counts


class ContextModelSource:
    """The portable source: an OutSystems MCP `context_screens` payload.

    Contract, established against 43 recorded screens across two real apps:
    the payload is a screen INVENTORY. Its exhaustive field set is key, name,
    description, isPublic, timestamp, ownerAppKey and additionalData
    (uiFlowKey, uiFlowName, and for referenced assets globalKey,
    inputParameters, roles, title). There is no widget tree and no widget
    count, and the MCP surface exposes no OML download to derive one from.

    So this source can confirm a screen was BUILT, and cannot confirm what is
    ON it. It says so rather than reporting zeros, which would turn every
    declared assertion into a false shortfall.

    The live call (`context_screens { app: "<key>" }`) is untested pending
    tenant access; everything below the call - the payload contract and the
    verdict behavior - is pinned by tests against recorded payloads.
    """

    def __init__(self, payload):
        rows = payload.get("data", payload) if isinstance(payload, dict) else payload
        self._names = {row.get("name") for row in rows if isinstance(row, dict)}

    def screen_exists(self, screen_name):
        return screen_name in self._names

    def screen_widget_counts(self, screen_name):
        return None


def recompute(blueprint, source):
    """Check every declared assertion in `blueprint` against `source`."""
    results = []
    declared_any = False
    for screen in blueprint.get("screens", []):
        if not isinstance(screen, dict):
            continue
        assertions = screen.get("assertions")
        if not isinstance(assertions, dict) or not assertions:
            continue
        declared_any = True
        name = screen.get("name", "?")
        if not source.screen_exists(name):
            results.append(AssertionResult(
                name, None, None, None, "SCREEN_MISSING",
                "the blueprint declares assertions for a screen the built model "
                "does not contain"))
            continue
        counts = source.screen_widget_counts(name)
        for kind in sorted(assertions):
            declared = assertions[kind]
            if kind not in ASSERTION_WIDGETS:
                results.append(AssertionResult(
                    name, kind, declared, None, "UNSUPPORTED",
                    "this recompute counts only "
                    f"{', '.join(sorted(ASSERTION_WIDGETS))}"))
            elif counts is None:
                results.append(AssertionResult(
                    name, kind, declared, None, "UNSUPPORTED", CONTEXT_UNSUPPORTED))
            elif counts[kind] < declared:
                results.append(AssertionResult(
                    name, kind, declared, counts[kind], "SHORTFALL"))
            else:
                results.append(AssertionResult(
                    name, kind, declared, counts[kind], "VERIFIED",
                    surplus=counts[kind] - declared))

    if not declared_any:
        return Report(results, False,
                      "NOT VERIFIED: no screen declares assertions - nothing was "
                      "checked. Declare them in the blueprint (chain step 3) or "
                      "this gate proves nothing.")

    checked = [r for r in results if r.status == "VERIFIED"]
    failed = [r for r in results if r.status in ("SHORTFALL", "SCREEN_MISSING")]
    unsupported = [r for r in results if r.status == "UNSUPPORTED"]
    if failed or unsupported:
        summary = (f"FAILED: {len(results)} assertion(s), {len(failed)} not "
                   f"satisfied, {len(unsupported)} unverifiable by this source.")
        return Report(results, False, summary)
    drift = sum(r.surplus for r in checked)
    summary = f"VERIFIED: {len(checked)} assertion(s) satisfied"
    summary += f", {drift} undeclared widget(s) present." if drift else "."
    return Report(results, True, summary)


def xre_graph_from_oml(oml_path, work_dir):
    """Convert a published `.oml` to its XRE graph. Internal reach only."""
    cli = os.environ.get("OML_EXTRACT_CLI")
    if not cli:
        raise SystemExit(
            "OML_EXTRACT_CLI is not set. The .oml source is internal-only: "
            "set OML_EXTRACT_CLI to the internal OML-extraction CLI command "
            "(an OutSystems-proprietary binary that is never distributed with "
            "this skill). Use --context-json for the portable source, noting "
            "it cannot see widget counts.")
    out = Path(work_dir) / "model.xre"
    try:
        subprocess.run([cli, "oml", "xre", str(oml_path), str(out)],
                       check=True, capture_output=True)
    except FileNotFoundError:
        raise SystemExit(
            f"{cli} (from OML_EXTRACT_CLI) is not on PATH. The .oml source is "
            "internal-only. Use --context-json for the portable source, "
            "noting it cannot see widget counts.")
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            f"oml xre failed on {oml_path}: {exc.stderr.decode(errors='replace')[:400]}")
    return json.loads(out.read_text(encoding="utf-8"))


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--blueprint", required=True,
                        help="Path to the blueprint.json whose assertions are checked")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--oml", help="Published .oml snapshot (internal reach)")
    group.add_argument("--context-json",
                       help="Recorded OutSystems MCP context_screens payload "
                            "(portable reach; cannot see widget counts)")
    args = parser.parse_args(argv)

    blueprint = json.loads(Path(args.blueprint).read_text(encoding="utf-8"))
    if args.oml:
        with tempfile.TemporaryDirectory() as work_dir:
            source = OmlModelSource(xre_graph_from_oml(args.oml, work_dir))
            label = args.oml
    else:
        source = ContextModelSource(
            json.loads(Path(args.context_json).read_text(encoding="utf-8")))
        label = args.context_json

    report = recompute(blueprint, source)
    sys.stdout.write(f"RECOMPUTE: {args.blueprint} against {label}\n")
    sys.stdout.write(report.text() + "\n")
    return 0 if report.verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
