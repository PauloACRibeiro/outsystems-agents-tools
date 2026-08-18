# ODC Diagnostics Recipes

Rule (adapted from an internal OutSystems team's service-registry pattern, mirroring
`odc-error-registry.md`): this file is the canonical INDEX of diagnostic
recipes for ODC error layers — one row per family, giving the first tool
call to run, the follow-up call when the first one is inconclusive or 404s,
and what the returned output must show before a diagnosis is trusted. Skills
resolve "what do I call to investigate this" here first. `odc-error-registry.md`
stays the source of a code's meaning and countermeasure; this file adds the
live tool-call sequence that surfaces the evidence behind a row. Adding a
diagnostic-call sequence to a skill body instead of linking this file, or
letting a row drift from the source procedure it condenses, is a lint
finding.

Codes and meanings: see `odc-error-registry.md`. That registry links back
here for diagnostics.

| Error prefix / layer | Applies to (registry code) | First tool call | Follow-up | What the output must show |
|---|---|---|---|---|
| publish | OS-APPS-40028 | `publish_logs` for the failed publication (needs the `operation_key`, not the gateway `publish_start` response's `operation_id` — see Follow-up if it 404s). | If `publish_logs` 404s on the `operation_id`, find the app's record in `env_deploy_history` and use that record's key as `operation_key` instead (the history is a 100-row unpaged window, so a miss after the fact is not proof nothing ran); then read the Mentor session's terminal `mentor_get_run` event for corroborating detail. | `publish_status` must read `Finished` (terminal) before the logs are trusted, and `publish_logs` must contain AVS rejection text naming the specific offending element (List/Table widget, Identifier-bound Input, Server Action naming conflict) — `getTrueChangeErrors` appearing mid-session is self-validation, not the signal, per `odc-mentor-hardening.md`. |
| deploy | OS-DPL-50203, OS-DPL-50204, OS-DPL-50205, OS-DPL-RDBS-40020 | `deploy_status` for the terminal state, then `deploy_messages` with the `operation_key` resolved from `env_deploy_history` (same operation_id/operation_key mismatch as the publish row — `deploy_messages` 404s on the gateway's `operation_id` too). | Re-read `deploy_messages` for the per-line error trail once `deploy_status` is terminal; if the trail is ambiguous between the four `OS-DPL-*`/`OS-RDBS-GEN-*` causes on file, check the entity/attribute's `DataType` and `IsAutoNumber`/`Id` settings per `odc-error-registry.md`'s rows before guessing. | A per-line error trail naming the entity/attribute involved (e.g. an in-place type change on an attribute with existing data, a retired attribute name reused, an authored `User`-typed attribute) — enough to tell the four underlying deploy-layer codes apart. |
| Mentor | OS-AISA-40001, OS-ABRS-FM-40005, OS-BERT-62000 | `mentor_get_run(runId)` — first poll with no cursor, then poll again passing the previous response's `nextCursor` until a terminal state. | On a guardrail block (`OS-ABRS-FM-40005`), check ODC Portal `MONITOR > Logs` for guardrail activity; on a max-conversation-length hit (`OS-AISA-40001`), read the terminal `error` payload's own `hint` field for the resume path (`fresh_context: true` on the same session) rather than starting a brand-new session. | Terminal `status: succeeded` / `failed` / `cancelled` from `mentor_get_run` — never cancel on step sequence alone. For a guardrail block, the Portal execution trace must show which specific guardrail (Prompt Attack Protection, Personal information exposure, or Harmful Content Filtering) fired. |
| quality-API | (no `OS-*` code — quality-API layer) | `python3 scripts/odc_code_quality.py analyze --name "<asset>" --summary` (or `--all --summary` for a tenant sweep) from `outsystems-code-quality-score`. | `status ANALYSIS_KEY` to re-poll one in-flight analysis by its key, or `summary ASSET_KEY REVISION` to fetch the stored summary for an already-analyzed revision, when the trigger call's own output is inconclusive. | The CLI's per-asset table: finding count plus the critical/high/medium/low counts for *this* run. Never quote the `raw`/`qualityScore` column as a gate — it is reported for reference only, per `outsystems-code-quality-score/SKILL.md`. |
