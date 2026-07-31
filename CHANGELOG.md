# Changelog

All notable releases to the published component and skills are recorded here.
Because `outsystems-public-knowledge/` keeps only the latest artifact, this file
is the record of what previous versions existed.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## 2026-07-31

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

- Added `skills/outsystems-plan-to-mentor/` — first public skill export. This
  repo is now the go-forward canonical home for this skill (superseding the
  earlier vendored copy). Derived export from `portable-agent-skills` at source
  commit `cf6c2bb`; provenance recorded in `skills/EXPORT-MANIFEST.json`.
- Repository scaffold created (structure only; no component artifact published yet).
