#!/usr/bin/env python3
"""sprint_init.py — scaffold and doctor for sprint-loop project folders.

Two commands:

  scaffold <project-dir>   create the sprint-loop project layout (idempotent)
  doctor   <project-dir>   check the project + machine against the pack's
                           requisites; write docs/sprint-init-report.md

Layout convention: workspace root CLAUDE.md, marker
`sprint-loop-project-layout:v1`. The doctor NEVER edits root files — on a
missing marker it prints the paragraph to paste and leaves the decision to
the operator (governance-sensitive shared instruction).

Knowledge-provider (MCP) and tenant-auth checks are agent-probed per the
SKILL.md — a script cannot call MCP tools. Everything filesystem-checkable
lives here.

Stdlib only. The internal extraction CLI is configured via OML_EXTRACT_CLI
(or OMLMAP_CLI) and is never named in this file or in any output.

Exit codes: 0 = no BLOCKED rows, 1 = at least one BLOCKED row, 2 = unusable
input (missing project dir, unreadable manifest).
"""
from __future__ import annotations

import argparse
import codecs
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
MANIFEST = SKILL_DIR / "references" / "pack-manifest.json"
PRD_TEMPLATE = SKILL_DIR / "references" / "prd-template.md"

SUBDIRS = ("docs/specs", "docs/plans", "design", "audits", "tests", "snapshots")

GITIGNORE = """# OML binaries never enter this repo — they live in projects/sprint-history/<slug>/ (local-only).
*.oml
.DS_Store
.claude/

# Render-gate working dir: playwright scripts, its node_modules symlink and run output.
# Committed evidence packets go to audits/ instead. Node resolves node_modules by walking
# up from the script, so this dir exists to keep the gate's working files inside the
# project rather than in the home directory (measured 2026-08-31).
.render-gate/
"""

CONVENTION_PARAGRAPH = """<!-- sprint-loop-project-layout:v3 -->
## Sprint-Loop Project Layout

- Sprint-loop artifacts are project-local under `projects/<app>/`: `docs/specs/` (PRD), `docs/plans/` (plan, patched plan, coverage reviews, mentor output, waivers), `design/` (screen inventory + blueprints), `audits/`, `tests/`, and `snapshots/` (text derivatives: `.opc`, `.index.json`, rev diffs/stories). This overrides the skills' default `docs/superpowers/...` paths.
- `snapshots/` text derivatives (`rev-N.opc`, `rev-N.index.json`) are produced ONLY by the `outsystems-oml-pseudocode` skill — never by a raw model graph renamed to `.opc` (mislabeled twice; the sprint-init doctor's derivative sniff blocks it).
- Each project folder is its own nested git repo with `CLAUDE.md` canonical and `AGENTS.md` a symlink to it; `outsystems.toml` carries tenant, env key, app key, `sprint_history_slug`, and `derivatives_remote_ok`.
- `.oml` files NEVER enter a project repo: they live only in `projects/sprint-history/<slug>/` (local-only, no remote).
- Root `docs/superpowers/` is cross-workspace only.
- New sprint-loop projects are scaffolded and preflighted by the `outsystems-sprint-init` skill.
- Loop order, with the owning skill per step (the full chain, including the quality gates and the as-built snapshot, stays in `docs/superpowers/workflows/outsystems-ui-delivery-chain.md`):
  1. PRD in `docs/specs/` — `superpowers:brainstorming` (fill the scaffolded `docs/specs/TEMPLATE.md`; requirement IDs are assigned here, never retrofitted).
  2. `design/screen-inventory.json` — `outsystems-screen-inventory`.
  3. Capability plan in `docs/plans/` — `outsystems-plan-to-mentor` pre-plan brief first, then `superpowers:writing-plans` (the brief wins on the document contract).
  4. `design/<screen>/blueprint.json`, one run per screen — `outsystems-ui-design`.
  5. `docs/plans/<plan>-patched.md` — `outsystems-plan-to-mentor` post-plan coverage review.
  6. `docs/plans/<plan>-mentor-output.md` — `outsystems-mentor-implementation` (approval-gated; publish is its own gate).
- The doctor (`sprint_init.py doctor`) prints the next step of this order from what the project already holds.
"""


def slugify(name: str) -> str:
    out = []
    for ch in name.strip().lower():
        if ch.isalnum():
            out.append(ch)
        elif out and out[-1] != "-":
            out.append("-")
    return "".join(out).strip("-")


def load_manifest() -> dict:
    try:
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    except OSError as exc:
        sys.exit(f"cannot read pack manifest {MANIFEST}: {exc}")


# ---------------------------------------------------------------- scaffold

def toml_text(args, slug: str) -> str:
    return f"""[tenant]
hostname = "{args.tenant_hostname}"
tenant_id = "{args.tenant_id}"
mcp_url = "https://{args.tenant_hostname}/mcp"

[environment]
key = "{args.env_key}"
name = "{args.env_name}"

[app]
name = "{args.app_name}"
asset_key = "{args.app_key}"

[sprint_loop]
sprint_history_slug = "{slug}"
derivatives_remote_ok = {str(args.derivatives_remote_ok).lower()}
"""


def claude_md(args, slug: str) -> str:
    return f"""# {args.app_name} — Sprint-Loop Project

Keys and tenant facts: `outsystems.toml`.

Layout (workspace convention `sprint-loop-project-layout:v1`):
- `docs/specs/` PRD · `docs/plans/` plan, patched plan, coverage reviews, mentor output, waivers
- `design/<screen>/` blueprints + previews · `audits/` · `tests/`
- `snapshots/` text derivatives (`rev-N.opc`, `rev-N.index.json`, rev diffs/stories)
- `.oml` files NEVER here — `projects/sprint-history/{slug}/` only.
- Published `.oml` revisions are downloaded by the agent, not exported by the
  operator: `odc app download --revision <N> <app-key> --quiet` from this
  folder, `<N>` = the tip revision the digest gate read (internal `odc` CLI;
  `odc auth login` when its token expires), then move `<app-key>.oml` to
  `projects/sprint-history/{slug}/rev-<N>.oml`.

## Tenant Guard

The OutSystems MCP registration is user-scoped (one per machine), so it may
still point at another project's tenant. **Before any tenant-touching MCP
call** (mentor sessions, publish, deploy, app/oml downloads), verify
`auth_status.tenant_hostname` equals `[tenant].hostname` in `outsystems.toml`.
On mismatch STOP and offer to re-register — never switch silently:

- Claude: `claude mcp add -s user --transport http outsystems <mcp_url from
  outsystems.toml>`, then re-authenticate; a mid-session URL change may need
  a session restart.
- Codex: has no `outsystems` MCP surface (standing issue) — point the PKCE
  fallback (`projects/workspace-agent-tools/scripts/outsystems_mcp_pkce_fallback.sh`)
  at the toml's `[tenant].hostname` and re-run `auth`; never edit
  Claude's MCP registration from Codex.
- Claude only: if the outsystems MCP tools are absent from the session after
  a re-authorization, a plain re-auth may not restore them — exit and run
  `claude --continue` from the project directory (observed 3x, 2026-08-28).
  Codex has no equivalent continuation flag; if its outsystems MCP surface
  misbehaves, use the PKCE fallback above and report the failure to the
  pack maintainer.
"""


def ensure(cond: bool, created: list, existed: list, label: str, make):
    if cond:
        existed.append(label)
    else:
        make()
        created.append(label)


def cmd_scaffold(args) -> int:
    proj = Path(args.project_dir).resolve()
    ws = Path(args.workspace_root).resolve()
    slug = args.slug or slugify(args.app_name)
    created: list = []
    existed: list = []

    proj.mkdir(parents=True, exist_ok=True)
    for d in SUBDIRS:
        p = proj / d
        ensure(p.is_dir(), created, existed, d + "/", lambda p=p: p.mkdir(parents=True))

    gi = proj / ".gitignore"
    ensure(gi.is_file(), created, existed, ".gitignore",
           lambda: gi.write_text(GITIGNORE, encoding="utf-8"))
    tm = proj / "outsystems.toml"
    ensure(tm.is_file(), created, existed, "outsystems.toml",
           lambda: tm.write_text(toml_text(args, slug), encoding="utf-8"))
    tp = proj / "docs" / "specs" / "TEMPLATE.md"
    ensure(tp.is_file(), created, existed, "docs/specs/TEMPLATE.md",
           lambda: tp.write_text(PRD_TEMPLATE.read_text(encoding="utf-8"),
                                 encoding="utf-8"))
    cm = proj / "CLAUDE.md"
    ensure(cm.is_file(), created, existed, "CLAUDE.md",
           lambda: cm.write_text(claude_md(args, slug), encoding="utf-8"))
    am = proj / "AGENTS.md"
    if am.exists() and not am.is_symlink():
        sys.exit("AGENTS.md exists as a regular file — the contract is a symlink to "
                 "CLAUDE.md (canonical). Merge its content into CLAUDE.md and remove "
                 "it, then re-run scaffold. Nothing was overwritten.")
    ensure(am.is_symlink(), created, existed, "AGENTS.md -> CLAUDE.md",
           lambda: os.symlink("CLAUDE.md", am))

    hist = ws / "projects" / "sprint-history" / slug
    ensure(hist.is_dir(), created, existed, f"sprint-history/{slug}/",
           lambda: hist.mkdir(parents=True))

    if not (proj / ".git").is_dir():
        subprocess.run(["git", "init", "-q"], cwd=proj, check=True)
        subprocess.run(["git", "add", "-A"], cwd=proj, check=True)
        subprocess.run(["git", "commit", "-q", "-m",
                        f"init: sprint-loop project layout for {args.app_name}"],
                       cwd=proj, check=True)
        created.append("git repo (initial commit)")
    else:
        existed.append("git repo")

    for label in created:
        print(f"created: {label}")
    for label in existed:
        print(f"exists:  {label}")
    print(f"scaffold OK: {proj} (slug: {slug})")
    return 0


# ------------------------------------------------------------------ doctor

class Row:
    def __init__(self, name: str, state: str, detail: str):
        self.name, self.state, self.detail = name, state, detail


def check_cli(manifest: dict) -> Row:
    cli = os.environ.get("OML_EXTRACT_CLI") or os.environ.get("OMLMAP_CLI") or ""
    if not cli or not os.access(cli, os.X_OK):
        return Row("extraction CLI", "BLOCKED",
                   "OML_EXTRACT_CLI is not set or not executable — the "
                   "oml-pseudocode and retrospective steps cannot run")
    try:
        out = subprocess.run([cli, "oml", "--help"], capture_output=True,
                             text=True, timeout=30).stdout
    except Exception as exc:  # noqa: BLE001 — any spawn failure blocks
        # The exception text carries the CLI's path, and this row is written
        # into a committed report: report the failure TYPE, never the name.
        return Row("extraction CLI", "BLOCKED",
                   f"OML_EXTRACT_CLI could not be invoked "
                   f"({type(exc).__name__}) — check the local configuration")
    missing = [s for s in manifest["required_cli_subcommands"] if s not in out]
    if missing:
        return Row("extraction CLI", "BLOCKED",
                   f"`oml --help` lacks subcommand(s): {', '.join(missing)}")
    return Row("extraction CLI", "PASS", "executable; xre/query/diff present")


ODC_STATUS_ARGV = ("odc", "auth", "status")


def _run_odc_status(argv):
    return subprocess.run(list(argv), capture_output=True, text=True, timeout=30)


def _odc_credential(runner) -> tuple:
    """(state, phrase) for the `odc` CLI's own token cache.

    `odc auth status` is the real surface (`odc auth --help`: login / logout /
    status, verified 2026-09-02). It answers with JSON carrying `logged_in`,
    `expired`, `hostname`, `tenant_hostname` and `tenant_id`. Only the two
    booleans may be reported: the doctor writes docs/sprint-init-report.md, so
    an identifier printed here is an identifier a commit can carry.

    `expired: true` is deliberately NOT a warning. The access token lapses within
    the hour and the CLI refreshes it transparently on the next real call while
    the refresh token lives — measured 2026-09-02 at `logged_in: true` with
    `expired: true` two hours past the access token's expiry, and named in the
    CLI's own `--quiet` help as the `Token expired, refreshing...` progress line.
    What actually stopped the run of 2026-08-30 was the refresh token itself
    lapsing, and that surfaces on a call, never in this status. So the honest
    report is the state plus the caveat, not a verdict.
    """
    try:
        res = runner(ODC_STATUS_ARGV)
    except Exception as exc:  # noqa: BLE001 — any spawn failure is reportable
        # As in check_cli: the exception text carries the binary's path, so
        # report the failure TYPE and never the name.
        return "WARN", (f"odc CLI could not be invoked ({type(exc).__name__}) — "
                        "the as-built snapshot cannot run; check the local install")
    try:
        data = json.loads(res.stdout)
    except Exception:  # noqa: BLE001 — malformed output is the finding
        return "WARN", ("odc auth status returned output this row could not read "
                        "— run it yourself; it is not echoed here because its "
                        "output carries tenant identifiers")
    if not data.get("logged_in"):
        return "WARN", ("odc CLI signed out — `odc auth login` opens a browser, "
                        "so only the operator can do it; batch it with the "
                        "render-gate bootstrap rather than discovering it later")
    if data.get("expired"):
        return "PASS", ("odc CLI signed in, access token lapsed — normal; the CLI "
                        "refreshes on the next call while its refresh token "
                        "lives, and only a real call proves that, so treat a "
                        "failing call as the signal to run `odc auth login`")
    return "PASS", "odc CLI signed in, access token live"


def _render_gate_credential(now: float) -> str:
    """Age of the newest render-gate storage-state file. Never its contents.

    The skill's hygiene rule is absolute — never read, print or commit the state
    file — and the filename alone is `<env-host>--<principal>.json`, so the name
    carries a tenant hostname. This stats and reports an age, nothing else.
    """
    state_dir = Path.home() / ".outsystems-render-gate" / "state"
    newest = None
    try:
        for f in state_dir.iterdir():
            try:
                if not f.is_file():
                    continue
                mtime = f.stat().st_mtime
            except OSError:
                continue
            if newest is None or mtime > newest:
                newest = mtime
    except OSError:
        newest = None
    if newest is None:
        return ("render-gate session: none on this machine — bootstrap one "
                "immediately before the gate run, not before composing the spec")
    age = int((now - newest) // 60)
    return (f"render-gate session: newest is {age} min old — bootstrap again "
            "immediately before the run; the shortest session measured on this "
            "estate lasted about ten minutes, the longest six and a half hours, "
            "and the file cannot tell you which one this is")


def check_credentials(runner=None, now: float | None = None) -> Row:
    """One row for the three credentials a sprint-loop run burns operator time on.

    Across the restaurant-app-v2 run (2026-08-26 to 09-02) the OutSystems MCP
    bearer, the `odc` CLI token cache and the render-gate browser session each
    expired on their own schedule and each interrupted the operator separately.
    The point of the row is to surface, in one place at step 0, which browser
    logins the run is about to need — so they can be done in one round instead of
    three interruptions.

    Only two of the three are knowable from a script, and the row says so rather
    than implying a clean bill of health. The MCP bearer lives in the agent
    session, not on disk; a PASS that quietly covered it would be worse than
    silence, because the operator would read it as the reassurance the row exists
    to withhold.

    Estate-only, gated by the caller: `odc` serves the as-built snapshot and the
    render gate is an `estate_skills` entry, so for a colleague this row could
    only prescribe remediations they cannot perform.
    """
    odc_state, odc_phrase = _odc_credential(runner or _run_odc_status)
    parts = [
        odc_phrase,
        _render_gate_credential(time.time() if now is None else now),
        "MCP bearer: not checkable from a script — it lives in the agent session, "
        "so have the agent run auth_status before any turn expected to run long",
    ]
    return Row("credentials", odc_state, "; ".join(parts))


def _check_profile_routing(ws: Path, profile: str, explicit: bool) -> "Row":
    """WARN when the estate profile was defaulted into rather than chosen.

    The colleague pack's accepted non-shipped-skill mentions are all justified
    by "that code path is estate-only, so a colleague never reaches it". That
    premise held only if the colleague actually ran `--profile colleague`, and
    nothing made them: `doctor` defaulted to estate and the manual's step 0 said
    only "use the skill". A colleague who followed the manual got the estate
    report — the paste block about a workspace root they do not have, the
    optional-skill WARNs for internal drafts, and the rest.

    `projects/` is the discriminator because the estate convention puts every
    sprint-loop project under it, while the colleague manual says to work in a
    plain folder. WARN, never BLOCKED: the run is still valid and the report is
    still readable, it is just the wrong audience's report.
    """
    if explicit:
        return Row("profile routing", "PASS", f"--profile {profile} passed explicitly")
    if (ws / "projects").is_dir():
        return Row("profile routing", "PASS",
                   "no --profile given; estate is right here — the workspace "
                   "root holds projects/")
    return Row("profile routing", "WARN",
               "no --profile given, so this ran as estate, but the workspace "
               "root has no projects/ — if you installed the colleague "
               "sprint-loop pack, re-run with --profile colleague; the estate "
               "rows below check skills and layout you are not meant to have")


def check_skills(manifest: dict, skills_root: Path, profile: str) -> list:
    rows = []
    names = list(manifest["required_skills"])
    if profile == "estate":
        names += manifest.get("estate_skills", [])
    for s in names:
        if (skills_root / s / "SKILL.md").is_file():
            rows.append(Row(f"skill {s}", "PASS", "installed"))
        else:
            rows.append(Row(f"skill {s}", "BLOCKED",
                            f"not installed under {skills_root}"))
    # Estate only: the optional skills are internal drafts that never ship, so a
    # colleague would get a WARN naming a skill they cannot obtain — a route to
    # nowhere, which is the class the non-shipped-mention gate exists to stop.
    if profile == "estate":
        for s in manifest.get("optional_skills", []):
            if not (skills_root / s / "SKILL.md").is_file():
                rows.append(Row(f"skill {s} (optional)", "WARN", "not installed"))
    return rows


def check_root_marker(ws: Path, manifest: dict) -> list:
    # Earlier markers stay accepted: each bump (v2 loop order, v3 derivative
    # producer) is an addition, and a root file the operator has not
    # re-pasted must not WARN.
    markers = manifest.get("accepted_root_convention_markers") or \
        [manifest["root_convention_marker"]]
    rows = []
    for name in ("CLAUDE.md", "AGENTS.md"):
        f = ws / name
        try:
            text = f.read_text(encoding="utf-8")
            present = any(m in text for m in markers)
        except OSError:
            present = False
        rows.append(Row(f"root {name} convention", "PASS" if present else "WARN",
                        "marker present" if present else
                        "convention marker missing — paste block below (suggest-only, "
                        "never auto-edited)"))
    return rows


def _check_stray_render_gate(proj: Path) -> "Row":
    """WARN when a render-gate working dir for this project sits outside it.

    The gate needs a directory where `node_modules` resolves. Node walks UP from
    the script, so a scratch dir under /tmp cannot see the operator's modules and
    the tempting fix is ~/render-gate-<app> — which scatters a project's files
    outside the project and is invisible where the operator looks for them. The
    convention is project-local `.render-gate/` with a `node_modules` symlink.
    Scaffold reserves the `.gitignore` rule ONLY — it does not create the directory
    or the symlink, because the operator's `node_modules` location is theirs to
    choose. The render-gate procedure creates both on first run.

    WARN, never BLOCKED: a stray dir is misfiling, not a broken loop, and the
    remediation is one `mv`. Measured 2026-08-31 on restaurant-app-v2, where two
    such directories accumulated in the home directory across sessions.
    """
    home = Path.home()
    slug = proj.name
    # EXACT name only. An earlier substring test (`slug in d.name`) warned a project
    # slugged "app" about ~/render-gate-happy-path, and a bare ~/render-gate warned
    # every project on the machine. A stray dir is this project's only when it carries
    # this project's slug exactly (Codex review, AH-2026-08-31-009).
    # No glob: `[`, `]`, `*` and `?` are pattern metacharacters, so a project
    # slugged "app[1]" never matched its own literal ~/render-gate-app[1] and the
    # row silently PASSed on a real stray. The name is fully known here, so build
    # the path directly (Codex review, AH-2026-08-31-009 round 4).
    candidate = home / f"render-gate-{slug}"
    strays = [candidate] if candidate.is_dir() else []
    local = proj / ".render-gate"
    if strays:
        names = ", ".join("~/" + d.name for d in strays)
        return Row("render-gate working dir", "WARN",
                   f"outside the project: {names} — move to {slug}/.render-gate/ "
                   f"(then resolve which node_modules actually holds playwright on "
                   f"this machine, symlink that one in, and verify with: "
                   f"cd .render-gate && node -e \"import('playwright')\")")
    if local.is_dir():
        has_modules = (local / "node_modules").exists()
        return Row("render-gate working dir", "PASS",
                   ".render-gate/ present" + ("" if has_modules else " (no node_modules symlink yet)"))
    return Row("render-gate working dir", "PASS",
               "none yet — scaffolded on first gate run as .render-gate/")


def check_project(proj: Path, profile: str = "estate") -> list:
    """Project-layout rows.

    The layout rows below (SUBDIRS, the *.oml deny rule, the AGENTS.md symlink,
    outsystems.toml) describe the ESTATE convention. A colleague working from the
    shipped pack is told by the manual to "work in an empty folder — one folder
    per app": there is no scaffold step on that side and none of these artifacts
    exist, so under --profile colleague the doctor reported BLOCKED with 9 layout
    blocks while all six pack skills passed — unusable by the audience the profile
    is named for. They are estate-only (maintainer decision 2026-08-31; the
    cross-agent review chose this option
    on AH-2026-08-31-009).
    """
    rows = []
    if profile != "estate":
        rows.append(Row("project layout", "PASS",
                        "skipped — colleague profile works in a plain folder, "
                        "so the estate scaffold layout does not apply"))
        return rows
    for d in SUBDIRS:
        ok = (proj / d).is_dir()
        rows.append(Row(f"dir {d}/", "PASS" if ok else "BLOCKED",
                        "present" if ok else "missing — re-run scaffold"))
    gi = proj / ".gitignore"
    ok = gi.is_file() and "*.oml" in gi.read_text(encoding="utf-8")
    rows.append(Row("gitignore denies *.oml", "PASS" if ok else "BLOCKED",
                    "present" if ok else ".gitignore missing the *.oml deny rule"))
    rows.append(_check_stray_render_gate(proj))
    am = proj / "AGENTS.md"
    ok = am.is_symlink() and os.readlink(am) == "CLAUDE.md"
    rows.append(Row("AGENTS.md symlink", "PASS" if ok else "BLOCKED",
                    "AGENTS.md -> CLAUDE.md" if ok else
                    "AGENTS.md is not a symlink to CLAUDE.md — a regular file drifts "
                    "from the canonical CLAUDE.md; merge and re-link"))
    tm = proj / "outsystems.toml"
    remote_ok = None
    if tm.is_file():
        # Parse, never grep: a commented-out or misplaced key must not PASS.
        import tomllib
        try:
            data = tomllib.loads(tm.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001 — unparseable toml
            data = None
            rows.append(Row("outsystems.toml", "BLOCKED", "file is not valid TOML"))
        if data is not None:
            required = {
                "[tenant].hostname": data.get("tenant", {}).get("hostname"),
                "[tenant].mcp_url": data.get("tenant", {}).get("mcp_url"),
                "[app].asset_key": data.get("app", {}).get("asset_key"),
                "[sprint_loop].sprint_history_slug":
                    data.get("sprint_loop", {}).get("sprint_history_slug"),
            }
            missing = [k for k, v in required.items()
                       if not (isinstance(v, str) and v.strip())]
            if data.get("sprint_loop", {}).get("derivatives_remote_ok") is None:
                missing.append("[sprint_loop].derivatives_remote_ok")
            hostname = required["[tenant].hostname"]
            mcp_url = required["[tenant].mcp_url"]
            bad_url = (hostname and isinstance(mcp_url, str) and mcp_url.strip()
                       and mcp_url != f"https://{hostname}/mcp")
            if missing:
                detail = f"missing/empty field(s): {', '.join(missing)}"
                if "[tenant].mcp_url" in missing:
                    detail += (" — legacy project: add mcp_url = "
                               "\"https://<hostname>/mcp\" under [tenant] (the "
                               "Tenant Guard's remediation command depends on it)")
                rows.append(Row("outsystems.toml", "BLOCKED", detail))
            elif bad_url:
                rows.append(Row("outsystems.toml", "BLOCKED",
                                f"[tenant].mcp_url is '{mcp_url}' but the derived "
                                f"URL for hostname '{hostname}' is "
                                f"'https://{hostname}/mcp' — fix whichever is wrong"))
            else:
                rows.append(Row("outsystems.toml", "PASS",
                                "parsed; required fields present, mcp_url matches "
                                "the hostname"))
            remote_ok = data.get("sprint_loop", {}).get("derivatives_remote_ok")
    else:
        rows.append(Row("outsystems.toml", "BLOCKED", "missing — re-run scaffold"))

    # Remote gate, both directions: `false` means this repo must have NO git
    # remote (client-app derivatives stay local); `true` is an approval that
    # needs somewhere to push, and restaurant-app carried it with no remote
    # configured at all, so the snapshot procedure's "push the branch"
    # dead-ended. WARN, never BLOCKED — a fresh scaffold has no remote yet.
    remotes = []
    if remote_ok is not None:
        try:
            remotes = subprocess.run(["git", "remote"], cwd=proj, capture_output=True,
                                     text=True, timeout=15).stdout.split()
        except Exception:  # noqa: BLE001
            remotes = []
    if remote_ok is False:
        rows.append(Row("derivatives remote gate",
                        "BLOCKED" if remotes else "PASS",
                        f"derivatives_remote_ok=false but git remote(s) configured: "
                        f"{', '.join(remotes)} — remove them or flip the flag "
                        "deliberately" if remotes else
                        "derivatives_remote_ok=false and no git remote configured"))
    elif remote_ok is True:
        rows.append(Row("derivatives remote gate",
                        "PASS" if remotes else "WARN",
                        f"derivatives_remote_ok=true — remotes permitted "
                        f"({', '.join(remotes)})" if remotes else
                        "derivatives approved for remote but no remote configured "
                        "— nowhere to push; add the remote or flip the flag"))
    return rows


_SEED_LOG_STRUCTURE = re.compile(r"^[ \t]*(?:#{1,6}[ \t]+\S|[-*+][ \t]+\S)", re.M)


def _seed_log_is_current(proj: Path, mentor_outputs: list[Path]) -> bool:
    """Whether `docs/seed-log.md` is real evidence, not just a present file.

    Codex review (AH-2026-09-02-015): a bare `.is_file()` check accepts an
    empty, malformed, or stale log — a leftover from an earlier build phase
    would silently pass. Nonempty, structured (a heading or a list item —
    the shape the manual's Seed demo data step asks for) and written no
    earlier than the latest build output are the three things a script can
    actually check; they do not replace the agent-probed data read that
    confirms records exist in the app itself.
    """
    log = proj / "docs" / "seed-log.md"
    if not log.is_file():
        return False
    text = log.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return False
    # Structure means Markdown heading or list-item SYNTAX at line start, not
    # the characters `#` / `-` anywhere: hyphenated prose ("well-known records
    # were seeded") passed the looser test (Codex, AH-2026-09-02-015 round 2).
    if not _SEED_LOG_STRUCTURE.search(text):
        return False
    latest_build = max(f.stat().st_mtime for f in mentor_outputs)
    return log.stat().st_mtime >= latest_build


def next_step(proj: Path, profile: str = "estate") -> str:
    """The next chain step, derived from what the project already holds.

    Same order as the root convention paragraph; the first unmet artifact
    wins. `TEMPLATE.md` is the scaffold's own PRD stub, so it never counts as
    a PRD — otherwise every fresh project would read as past step 1.

    The PRD line names the stub only when it exists. `--profile colleague`
    scaffolds no layout, so telling that operator to fill "the scaffolded
    TEMPLATE.md" sends them looking for a file no run of this tool created.

    Past the build, the chain no longer has one committed artifact per step,
    and presence alone is not evidence — a stray file, a failed run, or a
    result carried over from an earlier build must not read as "this step is
    done". Test evidence is a JSON file under the project's tests directory
    matching `outsystems-bdd-tests`' own exit-0 contract (SKILL.md "Reading
    the result"): `TestScenarioResults` non-empty, `IsSuccess: true`,
    `FailedScenarios` absent or zero, `SuccessfulScenarios > 0`. Render-gate
    evidence is `gate-results.json` under its documented working dir
    (`.render-gate/`, gitignored by convention) matching
    `outsystems-render-gate`'s own exit-0 contract (SKILL.md "Result
    semantics"): not aborted, at least one row, every row `status: "pass"`
    (a `fail`, `unasserted` or `unverified` row means the run did not reach
    exit 0, so it must not read as done). Both are further required to be no
    older than the current build (`_newest_valid_json` picks the newest
    match; the caller compares its mtime against the mentor-output file's).
    `outsystems-render-gate` is not part of the colleague sprint-loop pack, so that
    branch tells a colleague to verify by hand instead of naming a skill
    they cannot run.
    """
    prds = [f for f in sorted((proj / "docs" / "specs").glob("*.md"))
            if f.name != "TEMPLATE.md"]
    if not prds:
        stub = proj / "docs" / "specs" / "TEMPLATE.md"
        fill = (", filling the scaffolded `TEMPLATE.md`" if stub.is_file() else "")
        return ("write the PRD — `superpowers:brainstorming` into "
                f"`docs/specs/<name>.md`{fill} "
                "(assign the requirement IDs there; retrofitting them later "
                "costs a coverage pass)")
    if not (proj / "design" / "screen-inventory.json").is_file():
        return ("decide the screens — `outsystems-screen-inventory` reads the "
                "PRD and writes `design/screen-inventory.json` (one shared "
                "chrome decision for the whole app)")
    plans = sorted((proj / "docs" / "plans").glob("*.md"))
    if not plans:
        return ("write the capability plan — `outsystems-plan-to-mentor` "
                "pre-plan mode for the capability brief, then "
                "`superpowers:writing-plans` into `docs/plans/` (the brief "
                "wins on the document contract)")
    if not sorted((proj / "design").glob("*/blueprint.json")):
        return ("design the screens — `outsystems-ui-design`, ONE run per "
                "screen in `design/screen-inventory.json`, each emitting "
                "`design/<screen>/blueprint.json`")
    if not sorted((proj / "docs" / "plans").glob("*-patched.md")):
        return ("review the plan against the PRD — `outsystems-plan-to-mentor` "
                "post-plan mode, emitting `docs/plans/<plan>-patched.md` "
                "(reconcile entity names with the blueprints while there)")
    mentor_outputs = sorted((proj / "docs" / "plans").glob("*-mentor-output.md"))
    if not mentor_outputs:
        return ("build it — `outsystems-mentor-implementation` from the "
                "patched plan (Route A) and the blueprints (Route B), "
                "approval-gated per edit, into "
                "`docs/plans/<plan>-mentor-output.md`")
    # `mentor-output.md`'s mtime stands in for "when this build was finalized" —
    # nothing local marks the actual publish, which happens over MCP. A test
    # or gate result older than the build it is meant to verify is evidence
    # of an earlier iteration, not this one, and must not read as done.
    if not _seed_log_is_current(proj, mentor_outputs):
        # restaurant-app-v2, 2026-08-28/29: the build chain finished but
        # UI verification ran against zero dishes and zero subscribers
        # because nothing forced seeding before it.
        return ("publish the build (its own approval gate), then seed demo "
                "data through the app's own create screens with a "
                "discriminating dataset (records whose expected results "
                "differ per filter value), logging the seeded record ids "
                "into `docs/seed-log.md` per the manual's Seed demo data "
                "step — before `outsystems-bdd-tests` (required, not "
                "optional) and any other UI verification")
    build_time = max(f.stat().st_mtime for f in mentor_outputs)
    tests_evidence = _newest_valid_json(
        (proj / "tests").glob("**/*.json"), _is_passing_bdd_result)
    if not (tests_evidence and tests_evidence.stat().st_mtime >= build_time):
        return ("test it — `outsystems-bdd-tests` generates and runs the "
                "suite against the published, seeded app; required, not "
                "optional, before the render gate or grading")
    gate_evidence = _newest_valid_json(
        (proj / ".render-gate").glob("**/gate-results.json"), _is_passing_gate_result)
    if not (gate_evidence and gate_evidence.stat().st_mtime >= build_time):
        if profile == "estate":
            return ("run the render gate — `outsystems-render-gate` with "
                    "`--interact`, to verify every screen renders and every "
                    "control on it responds for a signed-in principal, "
                    "before grading")
        return ("verify it by hand — click every control on every screen, "
                "signed in; the render gate that would automate this, "
                "`outsystems-render-gate`, is not part of the colleague sprint-loop pack")
    if profile == "estate":
        return ("grade it — `outsystems-runtime-ui-audit` on the app's "
                "runtime URL, then the as-built snapshot per "
                "`docs/superpowers/workflows/outsystems-ui-delivery-chain.md`")
    return ("grade it — `outsystems-runtime-ui-audit` on the app's runtime "
            "URL")


def _is_strict_int(v) -> bool:
    """True for a real integer count, false for a bool. `bool` is a subclass
    of `int` in Python, so `True == 1` and `False == 0` — an API field that
    came back malformed as a boolean would otherwise silently pass a `> 0` or
    `== 0` count check meant for a genuine counter.
    """
    return isinstance(v, int) and not isinstance(v, bool)


def _is_passing_bdd_result(d: dict) -> bool:
    """Mirrors `outsystems-bdd-tests`' own exit-0 row (SKILL.md "Reading the
    result"): `TestScenarioResults` non-empty, `FailedScenarios == 0`,
    `IsSuccess: true`, `SuccessfulScenarios > 0`. Zero-valued fields are
    omitted by the API rather than zero-filled, so `FailedScenarios` and
    `SuccessfulScenarios` are read with `.get(..., 0)`, not required present
    — but a present value must be a genuine integer count, not a boolean
    (see `_is_strict_int`). A failed, inconclusive, malformed, or all-skipped
    run must not read as "tested".
    """
    if not isinstance(d, dict):
        return False
    results = d.get("TestScenarioResults")
    if not isinstance(results, list) or not results:
        return False
    failed = d.get("FailedScenarios", 0)
    successful = d.get("SuccessfulScenarios", 0)
    if not (_is_strict_int(failed) and _is_strict_int(successful)):
        return False
    return d.get("IsSuccess") is True and failed == 0 and successful > 0


def _is_passing_gate_result(d: dict) -> bool:
    """Mirrors `outsystems-render-gate`'s own exit-0 row (SKILL.md "Result
    semantics"): not aborted, at least one row, every row `status: "pass"`.
    A `fail`, `unasserted` or `unverified` row — or a login-wall abort — means
    the run did not reach exit 0, and must not read as "gated".
    """
    if not isinstance(d, dict) or d.get("aborted") is not None:
        return False
    rows = d.get("rows")
    if not isinstance(rows, list) or not rows:
        return False
    return all(isinstance(r, dict) and r.get("status") == "pass" for r in rows)


def _newest_valid_json(paths, is_valid) -> "Path | None":
    """The newest path among `paths` whose parsed JSON satisfies `is_valid`.

    A directory holding an unrelated file (a README, a stray note) or a
    result carried over from an earlier build must not read as "this step is
    done" — every candidate is opened and its content shape checked, not just
    its presence. Unreadable or non-JSON files are skipped, not fatal.
    """
    best = None
    for p in paths:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not is_valid(data):
            continue
        if best is None or p.stat().st_mtime > best.stat().st_mtime:
            best = p
    return best


WATCHED_BRANCH_PREFIXES = ("docs/plans/", "docs/specs/", "design/", "snapshots/")

# A `.opc` is renderer output and always opens with its `#` header line; the
# raw model graph is JSON and opens with `{`. Renaming a graph to `.opc` is the
# measured defect the sniff catches — the file reads as evidence but carries
# none. A BOM is not whitespace, so it must come off before the first character
# is read, or a BOM-writing exporter downgrades BLOCKED to WARN. UTF-32's BOMs
# start with UTF-16's, so they are tested first.
BOMS = (codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE, codecs.BOM_UTF8,
        codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)


def opc_sniff(path: Path) -> str:
    """`graph` (JSON), `ok` (renderer header), `odd`, or `unreadable`.

    Reads a head, never the file: the measured graph was 5.1MB.
    """
    try:
        with path.open("rb") as fh:
            raw = fh.read(512)
    except OSError:
        return "unreadable"
    for bom in BOMS:
        if raw.startswith(bom):
            raw = raw[len(bom):]
            break
    head = raw.decode("utf-8", "replace").lstrip().lstrip("﻿").lstrip()
    if head.startswith("{"):
        return "graph"
    if head.startswith("#"):
        return "ok"
    return "odd"


def _name_list(paths: list, root: Path, limit: int = 3) -> str:
    shown = [str(p.relative_to(root)) for p in paths[:limit]]
    extra = len(paths) - len(shown)
    return ", ".join(shown) + (f" (+{extra} more)" if extra else "")


def find_opc(root: Path) -> list:
    """Every `.opc` under `root`, matched case-insensitively — a hand-renamed
    `rev-22.OPC` is the same defect, and glob would miss it."""
    return sorted(p for p in root.rglob("*")
                  if p.is_file() and p.suffix.lower() == ".opc")


def check_snapshot_derivatives(proj: Path) -> Row:
    """P9: every `snapshots/**/*.opc` must be renderer output, and no `.xre`
    graph may sit anywhere in the project repo."""
    graphs, odd, unreadable = [], [], []
    snaps = proj / "snapshots"
    if snaps.is_dir():
        for f in find_opc(snaps):
            verdict = opc_sniff(f)
            if verdict == "graph":
                graphs.append(f)
            elif verdict == "odd":
                odd.append(f)
            elif verdict == "unreadable":
                unreadable.append(f)

    # os.walk, not rglob: `.git` is pruned rather than filtered afterwards, so
    # a large object store is never walked.
    xre = []
    for dirpath, dirnames, filenames in os.walk(proj):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        xre += [Path(dirpath) / f for f in filenames
                if f.lower().endswith(".xre")]
    xre.sort()

    details = []
    if graphs:
        details.append(f"{_name_list(graphs, proj)}: raw model graph mislabeled "
                       "as .opc — regenerate with the `outsystems-oml-pseudocode` skill "
                       "(omlpseudo.py -o rev-N.opc --index rev-N.index.json)")
    if unreadable:
        details.append(f"{_name_list(unreadable, proj)}: unreadable, so it cannot "
                       "be confirmed as evidence")
    if xre:
        details.append(f"{_name_list(xre, proj)}: raw model graph in the project "
                       "repo — the graph is regenerable and never committed; "
                       "delete it, or keep it outside the project repo, and "
                       "commit only the rendered .opc")
    # Reported alongside a BLOCK, not swallowed by it: otherwise the operator
    # fixes the graphs, re-runs, and only then learns about the rest.
    if odd:
        details.append(f"{_name_list(odd, proj)}: not renderer output (a .opc "
                       "opens with its '#' header) — confirm it is evidence, "
                       "not notes")
    if graphs or xre or unreadable:
        return Row("snapshot derivatives", "BLOCKED", "; ".join(details))
    if odd:
        return Row("snapshot derivatives", "WARN", "; ".join(details))
    # Scoped exactly as checked: the .opc sniff reads snapshots/, the .xre walk
    # reads the whole repo. A PASS that claimed more would be the same false
    # reassurance the row exists to prevent.
    return Row("snapshot derivatives", "PASS",
               "every .opc under snapshots/ opens with the renderer header; "
               "no .xre anywhere in the repo")


def _git_text(proj: Path, *args) -> str:
    """git stdout, or "" on any failure — no git, no repo, no such rev: there
    is simply nothing to compare, which is not the operator's problem here."""
    try:
        p = subprocess.run(["git", *args], cwd=proj, capture_output=True,
                           text=True, timeout=30)
    except Exception:  # noqa: BLE001
        return ""
    return p.stdout if p.returncode == 0 else ""


def _git_lines(proj: Path, *args) -> list:
    return [l for l in _git_text(proj, *args).split("\n") if l]


def check_unfinished_branches(proj: Path) -> Row:
    """P10: another local branch holding sprint artifacts the current branch
    lacks means the operator sees empty folders. WARN, never BLOCKED — a
    mid-sprint worktree is legitimate."""
    def artifacts(rev: str) -> set:
        # -z, not --name-only alone: git C-quotes any path with non-ASCII bytes
        # ("docs/plans/caf\303\251.md"), and a quoted path fails the prefix test
        # silently. The pathspecs keep the listing to the watched trees.
        out = _git_text(proj, "ls-tree", "-r", "--name-only", "-z", rev, "--",
                        *WATCHED_BRANCH_PREFIXES)
        return {p for p in out.split("\0") if p}

    def merged(ref: str) -> bool:
        """Already an ancestor of HEAD: finished, whatever its tree holds. Without
        this, a merged branch WARNs forever once any artifact it carried is later
        renamed or deleted on the current branch."""
        try:
            return subprocess.run(["git", "merge-base", "--is-ancestor", ref, "HEAD"],
                                  cwd=proj, capture_output=True,
                                  timeout=30).returncode == 0
        except Exception:  # noqa: BLE001
            return False

    # %(refname) is the full ref: %(refname:short) lengthens to "heads/x" when a
    # tag shares the name, and re-prefixing that yields refs/heads/heads/x.
    refs = [r for r in _git_lines(proj, "for-each-ref", "--format=%(refname)",
                                  "refs/heads/") if r]
    current = "".join(_git_lines(proj, "symbolic-ref", "-q", "HEAD")).strip()
    here = artifacts("HEAD")
    behind = [r for r in refs
              if r != current and not merged(r) and artifacts(r) - here]
    if not behind:
        return Row("unfinished branches", "PASS",
                   "no other local branch holds sprint artifacts missing here")
    names = ", ".join(r[len("refs/heads/"):] for r in behind)
    return Row("unfinished branches", "WARN",
               f"{names} carries docs/plans, docs/specs, design or snapshots "
               "files absent from the current branch's committed tree; merge or "
               "finish the branch — artifacts invisible on main")


PYTHON_CANDIDATES = ("python3", "python", "py")
_PY_VERSION = re.compile(r"\d+\.\d+(\.\d+)?([abrc]+\d+)?")  # used with fullmatch: the WHOLE line is a version


def _working_python() -> tuple:
    """(command, path, version) for the first candidate that actually runs.

    `shutil.which("python3")` is not evidence of a Python: on Windows the
    Microsoft Store app-execution alias `python3.EXE` resolves on PATH and
    prints "Python was not found" when run (v42 judgement half, 2026-09-02:
    the doctor reported `binary python3 PASS` against that stub on the VM).
    So run each candidate and accept the first that reports a version.
    """
    for cmd in PYTHON_CANDIDATES:
        path = shutil.which(cmd)
        if not path:
            continue
        try:
            r = subprocess.run([path, "-c", "import sys; print(sys.version.split()[0])"],
                               capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            continue
        out = r.stdout.strip()
        # A version is `major.minor[.patch]`; any other stdout (a shim's
        # chatter, an installer's prompt) is not a Python (Codex,
        # AH-2026-09-02-019 round 1: `not-a-version` was being accepted).
        if r.returncode == 0 and _PY_VERSION.fullmatch(out):
            return cmd, path, out
    return None, None, None


def check_binaries() -> list:
    rows = []
    git = shutil.which("git")
    rows.append(Row("binary git", "PASS" if git else "BLOCKED", git or "not on PATH"))
    cmd, path, ver = _working_python()
    if cmd:
        rows.append(Row("binary python3", "PASS", f"{cmd} {ver} at {path}"
                        + ("" if cmd == "python3" else " (python3 on PATH is not a working interpreter here; use this command instead)")))
    else:
        rows.append(Row("binary python3", "BLOCKED",
                        "no working Python found among python3/python/py — on Windows a "
                        "`python3` that prints \"Python was not found\" is the Store alias, not an install"))
    return rows


def cmd_doctor(args) -> int:
    proj = Path(args.project_dir).resolve()
    if not proj.is_dir():
        print(f"project dir not found: {proj}", file=sys.stderr)
        return 2
    ws = Path(args.workspace_root).resolve()
    skills_root = Path(args.skills_root).expanduser().resolve()
    manifest = load_manifest()

    profile_explicit = args.profile is not None
    if args.profile is None:
        args.profile = "estate"

    rows = []
    rows.append(_check_profile_routing(ws, args.profile, profile_explicit))
    rows += check_project(proj, args.profile)
    # Estate-only, like the CLI row: `.opc`/`.xre` are the extraction chain's
    # artefacts. A colleague has neither the renderer nor the CLI, so the row
    # could only ever BLOCK them behind a remediation they cannot perform
    # (Codex review, AH-2026-08-30-002 round 1).
    if args.profile == "estate":
        rows.append(check_snapshot_derivatives(proj))
    rows.append(check_unfinished_branches(proj))
    rows += check_binaries()
    if args.profile == "estate":
        rows.append(check_cli(manifest))
        # Estate-only for the same reason as the CLI row: the `odc` CLI serves
        # the as-built snapshot and the render gate is an estate skill, so a
        # colleague would get a row prescribing logins for tools they do not have.
        rows.append(check_credentials())
    rows += check_skills(manifest, skills_root, args.profile)
    # Estate governance only: the paste block describes `projects/<app>/`,
    # `projects/sprint-history/` and `docs/superpowers/`, none of which exist
    # for a colleague working in a plain folder. Emitting it there produced two
    # WARNs about a workspace root the colleague does not have, followed by 18
    # lines of estate layout (measured 2026-09-01).
    if args.profile == "estate":
        rows += check_root_marker(ws, manifest)

    lines = [f"# sprint-init doctor — {proj.name} — {date.today().isoformat()}", "",
             "| Check | State | Detail |", "|---|---|---|"]
    for r in rows:
        lines.append(f"| {r.name} | {r.state} | {r.detail} |")
    blocked = [r for r in rows if r.state == "BLOCKED"]
    warned = [r for r in rows if r.state == "WARN"]
    # `outsystems.toml` and the project Tenant Guard are estate scaffold
    # artifacts. A colleague has neither, so they get the same check stated
    # against what they DO have: the tenant they meant to connect.
    if args.profile == "estate":
        lines.append("| tenant-match (agent-probed) | PENDING | compare "
                     "auth_status.tenant_hostname to [tenant].hostname in "
                     "outsystems.toml; on mismatch offer re-register per the "
                     "project CLAUDE.md Tenant Guard |")
    else:
        lines.append("| tenant-match (agent-probed) | PENDING | confirm "
                     "auth_status.tenant_hostname is the tenant you meant to "
                     "build on; on mismatch re-register the outsystems MCP "
                     "before any build step |")
    lines.append("| knowledge provider tier (agent-probed) | PENDING | "
                 "search_outsystems_content -> implementation-authority; else "
                 "search_outsystems_public -> public-grounded |")
    lines.append("| demo data seeded (agent-probed) | PENDING | verify via a "
                 "data read (not an empty-state screenshot) that every "
                 "data-dependent entity holds a handful of records before any "
                 "UI verification gate; if not, seed through the app's own UI "
                 "where its entry paths work, else a data script/harness |")
    lines += ["", f"**Verdict:** {'BLOCKED' if blocked else 'READY'} "
              f"({len(blocked)} blocked, {len(warned)} warnings). "
              "PENDING rows are agent-probed per SKILL.md; the agent fills "
              "them before presenting this report.",
              "", f"**Next step:** {next_step(proj, args.profile)}"]
    report = "\n".join(lines) + "\n"
    print(report)

    if any(r.state == "WARN" and "convention" in r.name for r in rows):
        print("--- paste block for the workspace root CLAUDE.md (operator decision) ---")
        print(CONVENTION_PARAGRAPH)

    out = proj / "docs" / "sprint-init-report.md"
    if out.parent.is_dir():
        out.write_text(report, encoding="utf-8")
    return 1 if blocked else 0




# ----------------------------------------------------------------- migrate

DERIVATIVE_SUFFIXES = (".opc", ".index.json", "-diff.json", "-story.md")


def _rewrite_references(path: Path, proj_name: str, slug: str) -> bool:
    """Repo-relative path rewrite inside a migrated text file. The
    sprint-history rewrite keys on the RESOLVED slug (which may differ from
    the project dir name), the design rewrite on the project dir name."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    new = (text
           .replace("docs/superpowers/specs/", "docs/specs/")
           .replace("docs/superpowers/plans/", "docs/plans/")
           .replace(f"projects/{proj_name}/design/", "design/")
           .replace(f"projects/sprint-history/{slug}/", "snapshots/")
           .replace(f"projects/sprint-history/{proj_name}/", "snapshots/"))
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def flag_stray_history(ws: Path, proj: Path) -> None:
    """Report — never touch — pre-convention `projects/<app>-history/` folders
    holding a raw model graph renamed to `.opc`. Rehoming them is an operator
    decision (they can carry their own remote); the flag only says which are
    not the evidence they claim to be."""
    root = ws / "projects"
    if not root.is_dir():
        return
    for d in sorted(root.iterdir()):
        if (not d.is_dir() or d == proj or d.name == "sprint-history"
                or not d.name.endswith("-history")):
            continue
        bad = [f for f in find_opc(d) if opc_sniff(f) == "graph"]
        if bad:
            print(f"FLAG legacy stray history folder (not moved — operator "
                  f"decision): {d.relative_to(ws)} — {_name_list(bad, d)} "
                  "is a raw model graph mislabeled as .opc; regenerate with "
                  "the `outsystems-oml-pseudocode` skill before trusting it "
                  "as evidence")


def cmd_migrate(args) -> int:
    proj = Path(args.project_dir).resolve()
    ws = Path(args.workspace_root).resolve()
    if not proj.is_dir():
        print(f"project dir not found: {proj} — run scaffold first", file=sys.stderr)
        return 2
    match = args.match.strip()
    if not match:
        print("--match must be a non-empty filename substring — an empty match "
              "would select every root spec and plan (201 files on the live "
              "root at last count)", file=sys.stderr)
        return 2
    slug = args.slug or proj.name

    moves = []  # (src, dest)
    specs = ws / "docs" / "superpowers" / "specs"
    plans = ws / "docs" / "superpowers" / "plans"
    if specs.is_dir():
        for f in sorted(specs.iterdir()):
            if f.is_file() and match in f.name:
                moves.append((f, proj / "docs" / "specs" / f.name))
    if plans.is_dir():
        for f in sorted(plans.iterdir()):
            if f.is_file() and match in f.name:
                moves.append((f, proj / "docs" / "plans" / f.name))
    hist = ws / "projects" / "sprint-history" / slug
    if hist.is_dir():
        for f in sorted(hist.iterdir()):
            if f.is_file() and f.name.endswith(DERIVATIVE_SUFFIXES):
                moves.append((f, proj / "snapshots" / f.name))
            # .oml never moves — sprint-history is its only home

    flag_stray_history(ws, proj)

    if not moves:
        print(f"nothing to migrate: no artifact matching '{match}' in "
              f"{specs} / {plans}, no text derivatives in {hist}")
        return 0

    # migrate is the one path here that CREATES a snapshots/*.opc, so it sniffs
    # what it is about to move: moving a mislabeled graph in would manufacture
    # exactly the defect the doctor then blocks on, and _rewrite_references
    # would edit the graph's bytes on the way.
    mislabeled = [src for src, _ in moves
                  if src.suffix.lower() == ".opc" and opc_sniff(src) == "graph"]
    conflicts = [d for _, d in moves if d.exists()]
    header = "MIGRATE" if args.apply else "MIGRATE (DRY RUN — pass --apply to execute)"
    print(header)
    for src, dest in moves:
        print(f"  {src.relative_to(ws)}  ->  {dest.relative_to(ws)}")
    for src in mislabeled:
        print(f"refusing: {src} is a raw model graph mislabeled as .opc — "
              "regenerate it with the `outsystems-oml-pseudocode` skill (or remove it) "
              "before migrating; moving it would put a file that carries no "
              "evidence into snapshots/", file=sys.stderr)
    if conflicts:
        for d in conflicts:
            print(f"refusing: destination exists: {d}", file=sys.stderr)
    if mislabeled or conflicts:
        return 1
    if not args.apply:
        return 0

    rewritten = 0
    for src, dest in moves:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dest))
        # Never rewrite a model graph: a substring edit inside one corrupts it
        # silently. Anything else keeps the documented rewrite.
        rewritable = (dest.suffix in (".md", ".json")
                      or (dest.suffix.lower() == ".opc"
                          and opc_sniff(dest) != "graph"))
        if rewritable and _rewrite_references(dest, proj.name, slug):
            rewritten += 1
    print(f"moved {len(moves)} file(s); rewrote path references in {rewritten}.")
    print("Follow-up commits (run and verify each — this script never commits):")
    q = shlex.quote
    proj_dests = sorted({str(d.relative_to(proj)) for _, d in moves})
    root_srcs = sorted({str(src.relative_to(ws)) for src, _ in moves
                        if str(src).startswith(str(ws / "docs"))})
    hist_srcs = sorted({str(src.relative_to(ws / "projects" / "sprint-history"))
                        for src, _ in moves
                        if str(src).startswith(str(hist))})
    print(f"  git -C {q(str(proj))} add {' '.join(q(x) for x in proj_dests)} && "
          f"git -C {q(str(proj))} commit "
          f"-m {q('migrate: legacy sprint artifacts into project-local layout')}")
    if root_srcs:
        print(f"  git -C {q(str(ws))} add {' '.join(q(x) for x in root_srcs)} && "
              f"git -C {q(str(ws))} commit -m "
              f"{q(f'docs: move {slug} sprint artifacts to projects/{proj.name} (sprint-loop-project-layout:v1)')}")
    if hist_srcs:
        hist_repo = str(ws / "projects" / "sprint-history")
        print(f"  git -C {q(hist_repo)} add {' '.join(q(x) for x in hist_srcs)} && "
              f"git -C {q(hist_repo)} commit -m "
              f"{q(f'{slug}: text derivatives rehomed to projects/{proj.name}/snapshots')}")
    print("Then re-validate any design blueprints against the moved plan "
          "(validate_blueprint.py --plan) before relying on them.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    sc = sub.add_parser("scaffold", help="create the sprint-loop project layout")
    sc.add_argument("project_dir")
    sc.add_argument("--app-name", required=True)
    sc.add_argument("--slug", help="sprint-history slug (default: slugified app name)")
    sc.add_argument("--workspace-root", required=True)
    sc.add_argument("--tenant-hostname", default="")
    sc.add_argument("--tenant-id", default="")
    sc.add_argument("--env-key", default="")
    sc.add_argument("--env-name", default="Development")
    sc.add_argument("--app-key", default="")
    sc.add_argument("--derivatives-remote-ok", default="true",
                    type=lambda v: v.lower() in ("1", "true", "yes"))
    sc.set_defaults(fn=cmd_scaffold)

    dr = sub.add_parser("doctor", help="check pack requisites; write the report")
    dr.add_argument("project_dir")
    dr.add_argument("--workspace-root", required=True)
    dr.add_argument("--skills-root", default="~/.claude/skills")
    # default=None, not "estate": the resolved value is still estate, but the
    # doctor has to be able to tell a deliberate estate run from a caller who
    # never passed the flag. Every accepted non-shipped mention in the pack
    # manifest rests on "a colleague never reaches this path", and before this
    # the only thing standing between a colleague and the estate path was a
    # flag the manual never told them to pass (Codex review, AH-2026-09-01-006).
    dr.add_argument("--profile", choices=("estate", "colleague"), default=None,
                    help="estate (default): full internal loop (extraction CLI "
                         "+ estate skills required); colleague: the shipped "
                         "pack only — pass this if you installed the colleague "
                         "sprint-loop pack")
    dr.set_defaults(fn=cmd_doctor)

    mg = sub.add_parser("migrate", help="move legacy root-docs artifacts and "
                        "sprint-history text derivatives into this project "
                        "(dry-run by default)")
    mg.add_argument("project_dir")
    mg.add_argument("--workspace-root", required=True)
    mg.add_argument("--match", required=True,
                    help="filename substring identifying THIS app's specs/plans "
                         "(root docs hold many unrelated plans — never sweep)")
    mg.add_argument("--slug", help="sprint-history slug (default: project dir name)")
    mg.add_argument("--apply", action="store_true",
                    help="execute the moves; without it, dry-run listing only")
    mg.set_defaults(fn=cmd_migrate)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
