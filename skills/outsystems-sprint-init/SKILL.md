---
name: outsystems-sprint-init
description: Use when starting a new sprint-loop project (new app folder under projects/), when a sprint-loop run hits missing-setup errors (OML_EXTRACT_CLI unset, missing pack skills, no knowledge provider), or when asked to verify a machine can run the loop end to end. Scaffolds the project-local layout and runs the requisite doctor.
---

# OutSystems Sprint Init — scaffold + doctor for sprint-loop projects

One skill, two modes. First run on a new project **scaffolds** the layout the
workspace convention `sprint-loop-project-layout:v1` prescribes; any run on an
existing project is a pure **doctor** pass over the pack's requisites. The goal
is that setup gaps surface as a pre-loop report, never as a mid-loop failure
(the measured case: `OML_EXTRACT_CLI` discovered missing at a Define step).

Fully local except the two agent-probed rows below. No tenant mutation ever.

## Which mode applies — read this first

**Colleague sprint-loop pack: the only command is the doctor, with the profile
named.** There is one:

```bash
python3 "$SKILL_DIR/scripts/sprint_init.py" doctor <app-folder> \
  --profile colleague --workspace-root <the folder's parent>
```

**Scaffold and migrate are estate-only.** They build and move the internal
workspace layout — `projects/<app>/`, a nested git repo, an `outsystems.toml`,
a sibling sprint-history folder — none of which the colleague manual asks for;
it says to work in a plain folder, one per app. Running them from a colleague
install produces a layout nothing else in the pack reads.

**Never omit `--profile` on a colleague machine.** The flag defaults to
`estate`, so a bare `doctor` run checks the internal skill set and the
workspace-root convention and reports BLOCKED against requisites a colleague is
not meant to have (measured: 10 blocked rows in a bare folder). The doctor now
WARNs when it defaults into estate outside a workspace root, but the fix is to
pass the flag.

## Scaffold *(estate only)*

```bash
python3 "$SKILL_DIR/scripts/sprint_init.py" scaffold projects/<app> \
  --app-name "<Display Name>" --workspace-root <ws> \
  --tenant-hostname <t>.outsystems.dev --tenant-id <tid> \
  --env-key <ek> --env-name Development --app-key <ak> \
  [--slug <slug>] [--derivatives-remote-ok true|false]
```

Creates (idempotent — existing files are reported, never overwritten):
`docs/specs docs/plans design audits tests snapshots`, a deny-`*.oml`
`.gitignore`, `outsystems.toml` (tenant/env/app keys, `sprint_history_slug`,
`derivatives_remote_ok`), **`CLAUDE.md` canonical + `AGENTS.md` symlink**,
**`docs/specs/TEMPLATE.md`** (the PRD template), the sprint-history slug
directory, and a git repo with an initial commit.

`docs/specs/TEMPLATE.md` carries a `## Requirement Inventory` table pre-seeded
with the ID grammar (`BR-` with the `DM/SC/SEC/INT/WF` surface namespaces,
`UC-`, `C-`, unpadded `US-n`) and the usage rules that bite — one obligation
per ID, IDs never renumbered, deferrals cited rather than silent.
`superpowers:brainstorming` fills it into `docs/specs/<name>.md`; the template
itself stays put for the next PRD. This is the measured fix for PRDs written
without IDs, which cost a retrofit at the plan-coverage step.

Resolve the tenant fields before scaffolding: `auth_status` + `app_list`
(search by name) when the OutSystems MCP is up; otherwise ask the operator —
never guess keys. `--derivatives-remote-ok false` is the per-project
confidentiality decision: client-app derivatives (`.opc`, index, diffs) stay
off remotes; ask the operator once at init.

## Doctor

```bash
python3 "$SKILL_DIR/scripts/sprint_init.py" doctor projects/<app> \
  --profile estate --workspace-root <ws> [--skills-root ~/.claude/skills]
```

Pass `--profile` explicitly in both directions. It defaults to `estate`, which
is right on the estate and wrong everywhere else.

Two profiles (`--profile`, default `estate`):
- **estate** — the full internal loop: colleague ship set + estate-internal
  skills (oml-pseudocode, retrospective, ui-review, render-gate) + the
  extraction CLI with `xre`/`query`/`diff` subcommands.
- **colleague** — the shipped pack only (`required_skills` in
  `references/pack-manifest.json` = the outsystems-agents-tools export set);
  no extraction CLI, no estate skills.

Script-checked rows: project layout + toml fields (parsed, not grepped) +
`.gitignore` deny rule; **AGENTS.md must be a symlink to CLAUDE.md — a
regular file is BLOCKED** (and scaffold refuses to touch one: merge it into
CLAUDE.md and re-link); the **derivatives remote gate** — when
`derivatives_remote_ok = false` the project repo must have no git remote
(BLOCKED otherwise), and when it is `true` the repo must HAVE one (WARN
otherwise: approval with nowhere to push, the measured restaurant-app case);
**snapshot derivatives** and **unfinished branches**
(below); `git`/`python3` on PATH; profile skill set; **credentials** (below);
the root-convention
marker in the workspace `CLAUDE.md` and `AGENTS.md`. Report to stdout and
`docs/sprint-init-report.md`. Exit 0 READY, 1 BLOCKED, 2 unusable input.

**credentials** (estate profile only) — the two credentials a run needs that a
script can see, so the browser logins can be planned into one sitting instead of
discovered one at a time: the `odc` CLI (`odc auth status`, and only its
`logged_in` / `expired` booleans — never the tenant identifiers it also returns)
and the age of the newest render-gate storage-state file (its mtime only; the
file is never read, and its name is never printed because the name carries a
tenant hostname). `expired: true` on the CLI is not a warning: the access token
lapses within the hour and the CLI refreshes it transparently while its refresh
token lives, so only a real call proves usability. The MCP bearer is the third
credential and is **not** script-checkable — it lives in the agent session — so
the row says so and points at `auth_status` rather than implying a clean bill of
health. WARN only when the CLI needs a login a script cannot perform; an absent
render-gate session is normal at step 0 and never warns.

**snapshot derivatives** (estate profile only — `.opc` and `.xre` are the
extraction chain's artefacts, and a colleague has neither the renderer nor
the CLI, so the row could only BLOCK them behind a remediation they cannot
perform) — a `.opc` is the oml-pseudocode renderer's output
and always opens with its `#` header; the raw model graph is JSON and opens
with `{`. The doctor reads the first 512 bytes of every `snapshots/**/*.opc`
(any leading BOM stripped first, extensions matched case-insensitively):
JSON is **BLOCKED** ("raw model graph mislabeled as .opc — regenerate with
the `outsystems-oml-pseudocode` skill" — not part of the colleague sprint-loop pack), an unreadable one is BLOCKED (it cannot be
confirmed as evidence), and so is a `.xre` anywhere in the project repo
(`.git/` excepted) — the graph is regenerable and never committed, so keep
it outside the project repo when a run needs one. A `.opc` that is neither
JSON nor renderer output WARNs, and is listed alongside a BLOCK rather than
swallowed by it, so one run names every bad file. A PASS claims exactly what
was checked — `.opc` under `snapshots/`, `.xre` anywhere — and never more.
The measured defect: a 5.1MB graph renamed to `snapshots/rev-22.opc`, read
at a Define step as if it were evidence. There is deliberately no `*.xre`
`.gitignore` rule: a deny rule would say the graph is merely uncommittable,
while the doctor blocks on its presence at all, which is stronger.

**unfinished branches** — **WARN**, never BLOCKED (a mid-sprint worktree is
legitimate): another local branch holds files under `docs/plans/`,
`docs/specs/`, `design/` or `snapshots/` that the current branch's committed
tree lacks (`git ls-tree` comparison), so the artifacts are invisible where
the operator looks. A branch already merged into `HEAD` is finished and never
warns, however its tree compares. The measured defect: a whole sprint's
specs, plans, blueprints and snapshots sat on an unmerged branch while `main`
held only the scaffold, and the folders read as empty.

**Agent-probed rows (the script cannot call MCP tools — the report prints
them as PENDING; probe them yourself and fill them before presenting it):**

1. **Knowledge provider tier** — `search_outsystems_content` callable →
   implementation-authority; else `search_outsystems_public` →
   public-grounded (loop runs; OMI authority narrows); neither → BLOCKED for
   prompt-emitting steps. Same ladder as OMI's preflight.
2. **Tenant-match** — `auth_status.tenant_hostname` must equal
   `[tenant].hostname` in `outsystems.toml`. The MCP is registered PER
   PROJECT (`.mcp.json`, server `outsystems-<slug>`, tool prefix
   `mcp__outsystems-<slug>__`): each project owns one OAuth client and one
   refresh-token family, because ODC rotates refresh tokens on every use and
   revokes the family on reuse, so a user-scope `outsystems` credential
   shared by concurrent sessions forced a re-auth every 30-90 min
   (2026-09-02, anthropics/claude-code#91641). On mismatch STOP and OFFER to
   fix `.mcp.json` from the toml — never switch silently; Claude
   re-authenticates via `/mcp` (a mid-session change may need a session
   restart); Codex has no `outsystems` MCP surface and uses the PKCE fallback
   script pointed at the toml hostname, never Claude's registration.
   `mcp_url` and `.mcp.json` are required — the doctor BLOCKS a legacy
   project missing either (re-run scaffold: it is additive). Still one
   session per project folder for tenant work — sessions in the same folder
   share the family. Then `app_list` must resolve the app named in the toml. The
   scaffolded project CLAUDE.md carries the same guard as a standing
   instruction for EVERY sprint-loop skill run in that folder — that is what
   protects publishes and snapshots when hopping between projects targeting
   different tenants.
3. **Demo data seeded** — verify via a data read (not an empty-state
   screenshot) that every data-dependent entity holds a handful of records
   before any UI verification gate runs; if not, seed through the app's own
   UI where its entry paths work — which itself exercises them — else a data
   script/test harness. restaurant-app-v2's whole UI-verification phase ran
   against one restaurant, two menus, zero dishes and zero subscribers
   (2026-08-28/29): data-dependent screens were never rendered with data, the
   dispatch run reached zero recipients, and the app's worst defect (both
   "+ Add" buttons inert) surfaced only when seeding was finally attempted.

**Next step line.** The report ends with `**Next step:**`, derived from what
the project already holds — first unmet artifact wins, same order as the root
convention paragraph: no PRD in `docs/specs/` (`TEMPLATE.md` does not count)
→ `superpowers:brainstorming`; PRD but no `design/screen-inventory.json` →
`outsystems-screen-inventory`; inventory but no `docs/plans/*.md` →
`outsystems-plan-to-mentor` pre-plan brief then `superpowers:writing-plans`;
plan but no `design/*/blueprint.json` → `outsystems-ui-design` per screen;
blueprints but no `*-patched.md` → `outsystems-plan-to-mentor` post-plan
review; patched plan but no `*-mentor-output.md` →
`outsystems-mentor-implementation`; mentor output but no `docs/seed-log.md`
→ seed demo data through the app's own create screens (publish first, then
seed a discriminating dataset and log the seeded record ids into
`docs/seed-log.md` — see the manual's Seed demo data step); seed log present
→ the quality gates and the as-built snapshot. It prints on a BLOCKED
verdict too — the blocked rows say what to fix, the line says where the run
resumes.

**Root marker missing:** the doctor prints the convention paragraph as a
paste block and stops there. Editing the workspace root files is a
governance-sensitive shared instruction — **never apply it yourself; hand the
block to the operator.** The proposed paragraph carries the marker
`sprint-loop-project-layout:v3` (v2 plus the line naming
`outsystems-oml-pseudocode` as the only producer of the snapshot derivatives, not part of the colleague sprint-loop pack); the doctor's marker check accepts **v1, v2 and v3**, so a root
file the operator has not re-pasted never WARNs.

## Migrate (legacy projects) *(estate only)*

```bash
python3 "$SKILL_DIR/scripts/sprint_init.py" migrate projects/<app> \
  --workspace-root <ws> --match <name-substring> [--slug <slug>] [--apply]
```

Moves pre-convention artifacts into the project-local layout: root
`docs/superpowers/specs|plans` files whose **filename contains `--match`**
(root docs hold many unrelated plans — the skill never sweeps, never matches
by date), and the sprint-history slug's text derivatives (`.opc`,
`.index.json`, `-diff.json`, `-story.md`) into `snapshots/`. The `.oml`
never moves. **Dry-run by default** — review the listing, then re-run with
`--apply`. Apply refuses any existing destination file (nothing overwritten),
rewrites path references inside moved `.md`/`.json` to repo-relative form,
and **prints the three follow-up commit commands (project repo, root repo,
sprint-history) without running them** — commits to shared repos stay with
the operator/agent. After migrating, re-validate blueprints against the
moved plan (`validate_blueprint.py --plan`).

Migrate is the one path in this skill that **creates** a `snapshots/*.opc`,
so it sniffs every `.opc` it is about to move and **refuses the run** (like an
existing destination) when one is a raw model graph — moving it would
manufacture the defect the doctor then blocks on, and the reference rewrite
would edit the graph's bytes on the way. A graph is never rewritten.

Every run also **flags, never moves,** pre-convention
`projects/<app>-history/` folders holding a `.opc` that fails the same sniff.
Rehoming one is an operator decision — such a folder can carry its own remote
— so the flag only says which of them are not the evidence they claim to be.

## Hard rules

- Never overwrite an existing file in scaffold mode; re-runs report `exists:`.
- Never edit the workspace root `CLAUDE.md`/`AGENTS.md` (suggest-only).
- `.oml` bytes never enter the project repo; the `.gitignore` deny rule is a
  BLOCKED doctor row when absent.
- A `.opc` is only ever the `outsystems-oml-pseudocode` skill's output (not part of the colleague sprint-loop pack) — the
  raw model graph is never renamed or committed as one.
- The extraction CLI's name never appears in output — `OML_EXTRACT_CLI` only.

## Tests

```bash
python3 -m pytest skills/outsystems-sprint-init/tests -q
```
