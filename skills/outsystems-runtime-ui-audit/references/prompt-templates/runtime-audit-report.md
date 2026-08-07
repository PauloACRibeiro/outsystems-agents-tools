# Runtime audit report (prompt template)

- version: 1 (2026-08-06 — extracted unchanged from `SKILL.md` § "Step 4 — Output format"; prompts-as-data, Enzyme adoption #3)
- owner: `outsystems-runtime-ui-audit/SKILL.md` § "Step 4 — Output format"
- placeholders: `<app / URL>`, `<NN>`, `<Tier>`, `<N>`, `<D>`, `<K>`, `<flag low-confidence if K≥6>`, `<url>`, `<M>`, `<worst hits first — e.g. "40% of tap targets under 44px", "no reduced-motion support">`, `<patterns worth fixing first>`, `<embed a crawled screen or focus.png when it carries a finding>`, `<final>`, `<list which criteria and why>`

Emit the report skeleton below, replacing each angle-bracket placeholder with measured values and evidence. The table rows are worked examples of the required row shape — replace them with the audited app's 16 criteria. When the user requested convergence, the `## Mentor handoff` block (rules in `SKILL.md` § "Mentor handoff (compare-and-converge)") is appended after this report.

## Template

```markdown
# UI Quality Audit — <app / URL>

**Final score: <NN>%** → **<Tier>**
- Numerator: <N> · Denominator: <D> · N/A count: <K> <flag low-confidence if K≥6>
Audited: `<url>` · captures: desktop 1440×900, mobile 390×844, <M> crawled surfaces, focus + hover, probe.json

## Per-criterion scores

| # | Criterion | Tier | Score | Weight | Evidence |
|---|---|---|---|---|---|
| 1 | Theme & Styling | Delightful | 3 | 1× | One violet brand accent + neutrals; soft shadows; consistent ~16px radius; not the `#1068eb`/`#f3f6f8` defaults |
| 5 | Tap / Click Target Size | Unpleasant | 1 | 1× | probe: 60% of 10 interactive targets ≥44px (4 nav text-links ~28px tall) |
| 6 | Keyboard Interaction | Acceptable | 2 | 1× | focus.png: default browser ring only (`outline: auto`, blue) on "Log in" — visible but not designed |
| 11 | Animations | Acceptable | 2 | 1× | probe: 10/10 elements transition at 0.2s, but prefers-reduced-motion NOT handled |
| … |
| 14 | Modern vs. Dated | Delightful | 3 (4/5) | 1.5× | Soft shadows, generous whitespace, custom violet accent; no OS default tells |

## Notable findings

- <worst hits first — e.g. "40% of tap targets under 44px", "no reduced-motion support">
- <patterns worth fixing first>

## Screenshots

![desktop](./shots/desktop.png)
![mobile](./shots/mobile.png)
<embed a crawled screen or focus.png when it carries a finding>

## Method

- URL audited: `<url>` (final URL after redirects: `<final>`)
- Captures: Playwright + system Chrome — desktop + mobile full-page, <M> crawled surfaces, focus/hover states, probe.json, session.webm
- Rubric: UI Quality Assessment (16 criteria / 6 categories)
- Criteria mechanically supported: C5 (tap-target probe), C6 (focus probe), C11/C12 (motion + hover probe)
- N/A: <list which criteria and why>
```
