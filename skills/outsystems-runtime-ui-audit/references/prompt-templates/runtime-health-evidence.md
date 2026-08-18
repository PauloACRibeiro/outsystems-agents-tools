# Runtime health evidence (prompt template)

- version: 2 (2026-08-13 — Codex corrections round: determined no-traffic lines carry the never-deployed / UUID-not-in-tenant caveat, and all server-echoed strings are markdown-escaped by the renderer. v1 same day: P6, dossier rev. 17: optional runtime-health telemetry block from the internal `odc app health` verb, rd-ai-ase-toolkit RAOPST-3994 / Analytics API v5)
- owner: `outsystems-runtime-ui-audit/SKILL.md` § "Optional — Runtime health evidence (internal-only)"
- placeholders: `<stage key>`, `<since>`, `<to>`, `<rendered rows from health_evidence.py>`

The block is generated, not hand-filled: run `health_evidence.py` on the CLI's
JSON output and append its stdout to the report verbatim. The skeleton below
documents the shape that renderer emits, so a reviewer can check a report
against it. Never compose the block by hand from remembered numbers — the
renderer is what enforces the no-data semantics.

## Template

```markdown
## Runtime health (telemetry — does not affect the UI score)

Source: internal `odc app health` (Analytics API v5) · stage `<stage key>` · window <since> → <to>

<rendered rows from health_evidence.py>

Caveats (always apply):
- `appScore` is an Apdex-style LATENCY score (0-100), not a health verdict: it says nothing about failures, and an app with no traffic scores 100.
- An absent metric is the absence of a reading, never a zero.
```

Row semantics the renderer guarantees (do not edit them out of its output):

- A requested metric with no value prints `no reading` — never `0`.
- `noData.status = "undetermined"` prints as **no data** with the CLI's own
  reason; no app is ever described as traffic-free off an unproven page.
- `noData.status = "determined"` apps print as "no traffic in this environment
  in the window" with no score attached — an absent row is not a clean bill of
  health, and the line says so: it also covers an app never deployed to this
  environment, and for a UUID a key this tenant does not have.
- Every server-echoed string (app names, reasons, advisories, window bounds)
  is flattened to one line and markdown-escaped before it reaches the report.
- An `appScore` on fewer than 100 requests carries an inline
  "low traffic — score inflated" flag.
- `unresolved` inputs are listed: the rows cover fewer apps than were asked for.
- A `metricsAdvisory` from the CLI travels verbatim as a blockquote.
