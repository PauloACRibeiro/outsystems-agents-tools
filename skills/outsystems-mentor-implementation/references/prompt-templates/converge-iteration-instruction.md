# Converge iteration instruction (prompt template)

- version: 1 (2026-08-07 — authored for the rules-only converge surface from `SKILL.md` § "Mentor invocation discipline" → "Converge iteration (audit-driven)" (Enzyme adoption #2, AH-2026-08-06-008) and the 2026-08-06 first live converge run (13 fix instructions across 3 iterations, zero scope drift); prompts-as-data follow-up — no literal template existed before, so this is new wording, not an extraction)
- owner: `outsystems-mentor-implementation/SKILL.md` § "Mentor invocation discipline" — Converge iteration (audit-driven)
- placeholders: `<N>` (item count — exactly the handoff's, never more), `<fix instruction 1 — the handoff item's screen-scoped imperative text, verbatim>`, `<fix instruction 2 — next handoff item, handoff order preserved>`

Pass the block below as the single Mentor session instruction for a converge iteration. The audit's `Mentor handoff` block is the sole instruction source: one numbered line per handoff item, carrying that item's imperative fix text verbatim, in the handoff's order — never add, merge, reorder, or drop a fix. The handoff's criterion tags and evidence quotes stay in the audit report; the Mentor prompt carries only the fix text (short single-purpose prompts — Enzyme's "no plan, no agent" lesson, validated live 2026-08-06). The behavioral gates around this prompt (one session → one approved publish → digest gate → re-audit only on `DIGEST: changed`; stop rules) are owned by the SKILL.md bullet, not this template.

## Template

```text
Apply the following <N> UI fixes to this app, exactly as given — in this order, nothing added, and no other changes to the app.

1. <fix instruction 1 — the handoff item's screen-scoped imperative text, verbatim>
2. <fix instruction 2 — next handoff item, handoff order preserved>
```
