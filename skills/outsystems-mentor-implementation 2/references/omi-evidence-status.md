# OMI Evidence Status — Decision Table

Pick exactly one main label per answer. Decide by the weakest source that
materially grounds the claim.

| Source that materially grounds the claim | Label |
| --- | --- |
| Current OutSystems docs, approved internal docs, or current tenant/tool observation | `Current official` |
| Generated official ODC UI pattern catalog only (no curated recipe) | `Catalog-backed official` |
| O11 `Designing Screens` support-only facts for a confirmed ODC target/alias | `O11-supported ODC candidate` |
| Archived official PDFs, alone or mixed with current material | `Mixed official+archived` |
| Official courseware, workshop material, `.oml` examples | `Course/example-backed` |
| Public `OutSystems/outsystems-ui` source repository implementation details | `OutSystems-public implementation evidence` |
| Dry-run output, local fixtures, screenshots alone, memory, or anything weaker | `Unverified gap` |

One answer gets one main label — decided by the weakest source that materially
grounds it; never combine two labels in the Evidence Status line, and put
sub-claim caveats in prose or `Unknowns And Fallback Behavior`, not as a second
label. Do not name any other evidence label anywhere inside the
`### Evidence Status` section — not even in explanatory prose or parentheses;
describe stronger sub-claim grounding in plain words or move it to
`### Unknowns And Fallback Behavior`.

## Label Definitions

- `Current official` — grounded in current OutSystems docs, approved internal docs, or current tenant/tool observation
- `Catalog-backed official` — exact UI pattern facts come from the generated official ODC UI pattern catalog, but no curated recipe exists yet
- `O11-supported ODC candidate` — confirmed ODC Studio target or approved alias with support-only O11 `Designing Screens` reference facts; not current ODC authority
- `Mixed official+archived` — materially relies on archived official PDFs or combines current and archived official material
- `Course/example-backed` — materially relies on official courseware, workshop material, or `.oml` examples
- `OutSystems-public implementation evidence` — materially relies on the public `OutSystems/outsystems-ui` source repository for implementation details; not current ODC product-contract authority unless current ODC docs, Forge routing/version evidence, or tenant observations confirm the exposed behavior
- `Unverified gap` — not confirmed well enough by the current knowledge base

Dry-run evidence and fixture-only evidence are not standalone Evidence Status
labels; use `Unverified gap` for product-contract claims that rely only on
dry-run output or local fixtures; upgrade only when separately grounded by
current official docs, catalog facts, course/example material,
implementation-reference evidence, or tenant observation.

`outsystems-ui` implementation-reference facts are never enough to use `Current official` or `Catalog-backed official` by themselves. If they materially affect the answer without current docs or generated catalog support, use `OutSystems-public implementation evidence` and state that the fact is not current ODC product-contract authority unless confirmed by current ODC docs, Forge routing/version evidence, or tenant observations.

The OutSystems UI (ODC) Forge documentation bridge is current official routing evidence: the ODC Forge component page links its documentation to the O11 "Using Mobile and Reactive Patterns" page. Use that bridge for OutSystems UI pattern documentation routing, but do not use it to claim Mobile UI equivalence or to promote repo-only TypeScript facts to current ODC product-contract authority.

## Live Row Terminal And Advisory Statuses

Use these row statuses in campaign artifacts and summaries when they are more
precise than a generic evidence label:

- `done`: completed with sufficient proof and no material caveat.
- `done-read-only`: completed by read-only proof; no Mentor edit, publish,
  deploy, execution, or tenant mutation was needed.
- `done-read-only-advisory`: completed as advisory evidence only, such as
  Development-only validation or deploy-preview wording that does not prove
  promotion readiness.
- `done-read-only-direct-call-site-proven`: completed read-only using direct
  call-site proof, often from Studio visual proof when MCP context under-reports
  the hidden layer.
- `done-with-publish-advisory`: completed with `publish_status` reaching
  terminal success but `no_changes_detected=true`; not overclaimed as publish
  proof.
- `done-manual-studio-published`: completed by a manual Studio edit/publish
  followed by read-only Codex verification.
- `blocked-evidence`: stopped because exact target, hidden node, validation, or
  post-publish proof was missing, degraded, contradictory, or malformed.
- `blocked-auth`: stopped because the current runner could not prove
  authenticated OutSystems MCP access in the same execution context.
- `blocked-tool-unavailable`: stopped because an approved required tool was
  unavailable.
- `rollback-unavailable`: terminal outcome when exact safe rollback support is
  unavailable or unproven; do not call rollback.

Do not rewrite a completed row as pending because historical blocked attempts
inside the feedback file were blocked. Preserve prior blocked attempts as
history, but the top-level status must match the final terminal result.
