# Changelog

All notable releases to the published component and skills are recorded here.
Because `outsystems-public-knowledge/` keeps only the latest artifact, this file
is the record of what previous versions existed.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## 2026-08-05 — outsystems-plan-to-mentor: mechanical coverage gate

Skill export from PAS `f8482d5`. The self-reported coverage score (0–100,
converge at ≥98) is replaced by a mechanical gate: stable `BR-`/`UC-`/`C-`
requirement IDs (new `references/requirement-id-conventions.md`), a stdlib
checker `scripts/check_requirement_coverage.py` (uncovered = defined −
referenced, dangling = referenced − defined, verdict `READY`/`NOT READY`),
and a computed — never hand-authored — readiness verdict. Deferrals must cite
their ID in the plan's scope boundaries; there is no waiver mechanism.

## 2026-07-31 (v32)

**Every change below was found by watching real coding agents use v31 on real
machines — Claude Code and Codex, on Windows and macOS. None came from a code
review.** Component `1.3.0`, ZIP digest
`640d7b0d76e1f7549288a179283551b77a89668148fd4c213d06d56425d46d8f`, built twice
byte-identical. Supersedes v31 `cc2200c7…`.

### Product fixes

- **`update` no longer breaks a running server silently.** It replaces the index
  atomically, so a server already bound to the old file rejected the new one
  permanently — still answering health checks while every query failed. It now
  warns before and after, naming the processes, and says that a client restart
  may not stop them. It also prints a success line: the previous silence is what
  made this take a day to diagnose.
- **A partial uninstall is now recoverable.** If removal fails part way — a file
  held by an indexer, antivirus, or a shell sitting inside the root — the tree was
  left half-deleted, and re-running refused because the receipt had already been
  removed. A resume marker lets the same command finish the job, with a bounded
  retry for momentary locks and, on Windows, the name of what holds the file.
- **The printed MCP removal command carries the scope it registered with.** The
  unscoped form crashed with an access violation and left the registration behind.
- **`doctor` reports how old the mirrored content is** and flags it past a week.
  It measures when content was last actually fetched, so a reindex cannot make a
  stale corpus look fresh.
- **`refresh_index` and `ping` no longer describe themselves as things they are
  not.** `refresh_index` reindexes local files and fetches nothing; `ping` reports
  liveness and identity and cannot detect a broken index binding.

### Instruction fixes

- Installer path, interpreter, digest verification and extraction commands are now
  correct and concrete on both platforms. Several were valid in bash and inert in
  PowerShell — something no macOS test could have caught.
- The Windows document declares PowerShell as its shell. The two shells need
  opposite forms for the same command; no single form works in both.
- Uninstall deregisters and stops the server **first**. The previous order failed
  for everyone, because the agent's own server holds the root it is about to delete.
- A copy of the operations document is written into the install root at install
  time. Without it, an agent asked months later to "follow the instructions" has
  nothing to follow — one invented a procedure that removed the package and left
  1.4 GB of mirrors and index behind.
- The agent verifies prerequisites itself and asks the human only about the install
  root — the one thing that is a decision rather than a measurement.

### Verified, and not

Verified by execution on both platforms against this build: digest, install,
`doctor` (15 on macOS, 19 on Windows), `update` including the live-server guard,
the staleness warning clearing after an update, and uninstall.

**Fixed but not proven on a real machine:** partial-uninstall recovery (unit tests
only), Windows holder identification (written from the API contract, never
executed on Windows), and the update runner script — which is
**specified, not standardized**: the instructions say what it must do rather than
giving literal source, so each agent writes its own and none have been compared.

The automated Windows walkthrough runs the eight documented commands. It does not
exercise keeping the extraction directory, writing the local `INSTALL.md`, or
writing the runner script — those are instructions to an agent, and the harness is
not one.

### Known issues, carried forward unchanged

- **Windows install intermittency**: two failures in three attempts on one pilot
  machine, unexplained, undiagnosable because logs were deleted before the retry.
  Both documents require preserving logs before retrying.
- **A fresh install reports STALE immediately** when the release is more than a
  week old. That is accurate, not a fault — the shipped corpus is pinned at build
  time — and `update` clears it.

## 2026-07-31

- **Distribution authorization.** World-public distribution of this component was
  authorized by Paulo on 2026-07-30. Before that date, distribution beyond a
  hand-picked pilot was explicitly un-granted. Recorded here because this file is
  the governing release record; the cross-agent review (AH-2026-07-31-001) did not
  itself establish that authorization.
- **First component release: `v31` (OutSystems Public Knowledge 1.3.0).**
  Published as a GitHub Release with four assets — the component ZIP, its
  `.sha256`, `INSTALL-MACOS.md` and `INSTALL-WINDOWS.md`. ZIP digest
  `cc2200c7b6a83d3e9e53b757f208ffeed9bef8c72093d3a00d39079255546957`.
- **The component ships as a Release asset, not in the repository tree.**
  This supersedes the 2026-07-18 decision to commit the ZIP under
  `outsystems-public-knowledge/`, which now holds only a pointer to the
  Releases page. The tree therefore never accumulates a binary per version,
  and the agent gets a version and digest as data rather than as a file.
- **Install is now agent-native.** `README.md` carries one short, version-free
  prompt a colleague pastes into Claude Code or Codex; the agent resolves
  `/releases/latest`, reads the instructions for its own OS, confirms the
  install root and prerequisites with the human, then installs and verifies.
  Prompts for refresh and uninstall are alongside it. This replaces a
  605-line setup document that had to be sent by hand.
- **Both platforms verified by execution before publication.** The macOS
  document was walked end to end on a real install; the Windows document was
  walked end to end inside a disposable VM, including the uninstall ordering
  guard firing with a live server holding the install root. Nine document
  defects were found and fixed in the process — five of them invisible on
  macOS by construction, including a command form that is valid in bash and
  inert in PowerShell.

## 2026-07-29

- Regenerated `skills/outsystems-plan-to-mentor/` from `portable-agent-skills`
  at `2cac278` — the paste-mode execution protocol gains a verbatim-literal
  entry rule (clipboard entry where grantable, then read the stored value
  back and compare it to the source text; a committed field is not proof of
  verbatim storage). Part of the driving-Mentor lessons batch from the
  PlayRight runtime phase, cross-agent reviewed (AH-2026-07-29-001).

## 2026-07-28 (second export)

- Regenerated `skills/outsystems-plan-to-mentor/` from `portable-agent-skills`
  at `1ea6cb2` — the companion invocation contract now also requires reconcile
  session phrasing, a per-session expected element delta and `Traps` list, and
  a build-log table template in the Mentor package (session-packaging
  hardening, cross-agent reviewed).

## 2026-07-28

- Regenerated `skills/outsystems-plan-to-mentor/` from `portable-agent-skills`
  at `1d39c6c` — six workflow improvements from a live build retrospective,
  cross-agent reviewed: pre-plan capability brief handed to the plan generator
  (new `references/capability-plan-brief.md`) with pre-plan/post-plan mode
  routing; platform-feasibility rows in the coverage loop with an
  official-source authority rule; fail-closed `Target app state` +
  scaffold-inventory fields in the companion invocation contract; supervised
  paste execution protocol (new
  `references/paste-mode-execution-protocol.md`); Known Platform Bounds and
  Runtime Verification guardrails; scanner now also rejects ODC
  element-recipe section headings case-insensitively.

## 2026-07-19

- Regenerated `skills/outsystems-plan-to-mentor/` from `portable-agent-skills`
  at `b24cc05` — strips a trailing space in `references/delivery-modes.md` so the
  tree passes `git diff --check`. No behavior change.

## 2026-07-18

> **Superseded on 2026-07-31 — read this section as history, not as current
> layout.** The in-tree component drop described below was replaced by
> Release-asset delivery; `outsystems-public-knowledge/` is now intentionally
> empty. See the 2026-07-31 entry.

- Added `skills/outsystems-plan-to-mentor/` — first public skill export. This
  repo is now the go-forward canonical home for this skill (superseding the
  earlier vendored copy). Derived export from `portable-agent-skills` at source
  commit `cf6c2bb`; provenance recorded in `skills/EXPORT-MANIFEST.json`.
- Repository scaffold created (structure only; no component artifact published yet).
