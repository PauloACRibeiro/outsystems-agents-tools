# Build-log table (prompt template)

- version: 1 (2026-08-06 — extracted unchanged from `references/session-packaging-hardening.md` § "Build-Log Table Template"; prompts-as-data, Enzyme adoption #3)
- owner: `outsystems-mentor-implementation/references/session-packaging-hardening.md` § "Build-Log Table Template"
- placeholders: `S1` (session id — one row per session; the executor fills `Time`, `Outcome`, `Notes`)

Include the table below in every session package, pre-formatted with one row per session. The outcome vocabulary in the sample row is fixed — see the owner section for which outcomes count toward the run tally.

## Template

```markdown
| Session | Time | Outcome | Notes |
|---|---|---|---|
| S1 | | first-try / re-prompted / hand-fixed / blocked / aborted / skipped / already-conformant | |
```
