# Mentor handoff block (prompt template)

- version: 2 (2026-08-07 — Mentor-handoff-side follow-up to the C15/C16 design pass: declared design-scope gaps are skipped in worst-first ranking and noted rather than turned into a manufactured fix, and C16's four identity dimensions can each yield their own dimension-scoped item. The v1 (AH-2026-08-06-008) ≤5 / worst-first / evidence-cited / read-only contract is unchanged — see "Semantics guard" below.)
- owner: `outsystems-runtime-ui-audit/SKILL.md` § "Mentor handoff (compare-and-converge)"
- placeholders: `<tier>` (the loop's target tier), `<requested by the user | defaulted from <current tier>>` (pick one; always record which), `<Skipped: C<N> — design-scope gap, see report.>` (one line per skipped design-scope gap; omit the line entirely when none was skipped), `<G>` (weighted gap), `<screen-scoped imperative fix instruction>`, `<evidence line quoted from the per-criterion table>`, `<next item — same shape, worst-first; at most five, never padded>`, `<target tier>`, `<tier at audit>`. The `C<N>` slot is the criterion number and may combine criteria (C14+C16, with a combined weighted gap) when one fix addresses both, or split C16 into per-dimension items — tag each item C16 (<Dimension>) for Palette / Typography / Shape & depth / Imagery & iconography — when more than one dimension is reported unauthored; every such item still counts toward the five-item cap and sits at C16's ranked position in the worst-first order.

Append the block below after the audit report, only under the emission conditions in the owner section (user requested convergence or named a target ODC app; target-tier defaulting and the already-Market-Leading rule live there too). Every item must trace to a scored evidence line — the rules capping the batch at five, ordering worst-first, and forbidding invented or padded fixes are owned by the SKILL.md section, not this template. A criterion the report declares a design-scope gap (currently only C15's, per the rubric's design-scope note) is never turned into a manufactured item: the worst-first ranking skips it and moves to the next-worst actionable criterion, and the block records the skip as a single line above the numbered list so the human sees a decision, not an omission. This skill remains read-only: the block is text for `outsystems-mentor-implementation` to execute.

## Semantics guard

This revision only adds the skip line and the C16 per-dimension tag. It does not touch: the five-item cap, worst-first ordering, the evidence-quote requirement, the ban on invented or padded fixes, the target-tier line and its defaulting rule, or the read-only / delegated-execution contract — all still owned by SKILL.md and unchanged from v1.

## Template

```markdown
## Mentor handoff

Target tier: **<tier> (<requested by the user | defaulted from <current tier>>)**

<Skipped: C<N> — design-scope gap, see report.>

1. **[C<N> — <tier at audit>, weighted gap <G>]** <screen-scoped imperative fix instruction>. Evidence: "<evidence line quoted from the per-criterion table>".
2. <next item — same shape, worst-first; at most five, never padded>

Execution belongs to `outsystems-mentor-implementation` (Converge iteration); the digest gate decides whether the publish changed anything. Loop closes by re-audit of the same URL: stop at <target tier>, or after two consecutive audits with no weighted-score improvement.
```
