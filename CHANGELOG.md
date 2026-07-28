# Changelog

All notable releases to the published component and skills are recorded here.
Because `outsystems-public-knowledge/` keeps only the latest artifact, this file
is the record of what previous versions existed.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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
