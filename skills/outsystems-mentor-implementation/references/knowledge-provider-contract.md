# Knowledge-Provider Contract

`outsystems-mentor-implementation` (OMI) depends on a **knowledge-provider
role**, not on a named MCP server. For public OutSystems grounding, use the
available public knowledge-provider role. The maintainer may bind it to
`workspace-knowledge-cc`; a colleague may bind it to
`outsystems-public-knowledge`. Both expose the same public retrieval role.
Provider availability determines the mode, not the machine owner or alias.

This file defines the current OMI public-routing interface. `SKILL.md` and the
runtime references resolve public retrieval through these roles instead of
hard-coding a provider's tool names.

Internal or private content must not flow through the public-provider role.
This is a routing safety boundary; it does not remove provider-engine tools
outside the OMI contract.

`outsystems-tech-content` is a separate, VPN-gated, non-substitutable hard gate
for internal, course, archive, and workshop evidence as well as implementation
authority (function signatures, TrueChange, widget rules). It is not part of
this public-provider contract and keeps its own dedicated preflight in
`SKILL.md`. The public-provider role does not supply those restricted sources.
If the separate capability is unavailable, keep claims that depend on them
`Unverified or blocked`.

## Provider modes

OMI detects the provider at preflight from the callable tool set — there is no
config file and no user-selected mode. `SKILL.md` owns the detection order;
this table owns what each mode may claim.

| Mode | Detected by | Grounding | Authority |
|---|---|---|---|
| `provider: implementation-authority` | `search_outsystems_content` is callable | public docs plus internal, courseware, archive, and workshop content | implementation-level: function signatures, TrueChange and platform errors, widget-library rules and UI pattern APIs |
| `provider: public-grounded` | `search_outsystems_content` is absent and `search_outsystems_public` is callable | public OutSystems documentation only | public-docs authority only; never implementation-level |
| no provider | neither is callable | none | `SKILL.md` hard preflight block, or the four local repos as an explicitly degraded, source-backed fallback |

`provider: implementation-authority` wins whenever both are callable. A public
provider is a route, not a downgrade of the block — but it is also not a
substitute for internal authority.

### `provider: public-grounded` — what it can and cannot ground

Can ground, from the public corpus:

- Built-in function signatures and semantics — the public docs-odc mirror
  carries the full reference at `src/eap/reference/built-in-functions/`
  (text, dateandtime, math, numeric, format, data-conversion, url, email,
  roles, organization). Verified by live retrieval 2026-08-07: the query
  `Index text function` with `platform='odc'` returns that reference at rank 1.
- Mentor and platform service error codes — docs-odc `src/error/` (`aisa/`,
  `aica/`, `ctxs/`), including the `OS-AISA-*` family. Distinct from TrueChange
  validation errors, which are not public.
- Widget and UI pattern facts already captured in this skill's generated
  catalogs (`odc-studio-widget-catalog.json`, `odc-ui-pattern-catalog.json`,
  `odc-data-grid-reference.json`), which are generated from the public docs-odc
  mirror and keep `Catalog-backed official`.
- Placement, architecture, security and roles, performance, timers and events,
  agentic, REST, and Mentor Studio/Web capability facts that the four public
  repos document.

Must fail closed — name the gap, keep the claim `Unverified gap`, never guess:

- TrueChange and platform validation error codes or exact error text. Measured
  2026-08-07: the public corpus mentions TrueChange only incidentally — top
  hits score 7.7-10.5 against 25-70 for well-covered topics, and every one is a
  passing reference. `outsystems-tech-content` `content_source='model'`
  (`model-truechange`) is the only authority. Do not over-read this: the corpus
  DOES ship service error catalogs under docs-odc `src/error/` (`aisa/` Mentor
  Studio, `aica/` Mentor Web, `ctxs/` context service), which cover the
  `OS-AISA-*` codes this skill's Mentor invocation discipline cites. Those are
  publicly groundable; TrueChange validation errors are the gap.
- Approved internal, courseware, archive, and workshop evidence — so
  `Mixed official+archived` and `Course/example-backed` are unreachable in this
  mode.
- Widget-library rules and UI pattern APIs beyond what the generated catalogs
  already carry.
- Anything else that materially rests on internal-only content.

## Roles

### `grounding_search(query, scope="public")`

Keyword/semantic search over OutSystems grounding material.

- `query`: free-text search string.
- `scope`: fixed to `"public"`; searches public OutSystems documentation and
  public repository content only.
- Returns: `hits: [{title, path, source_url, snippet, source_family?}]`

### `fetch(doc_id)`

Fetch the full content of a document previously returned by
`grounding_search`.

- `doc_id`: the identifier returned in a prior `hits`/`documents` entry.
- Returns: `{content, truncated}`

## Binding Table

| Role | Maintainer binding — `workspace-knowledge-cc` | Colleague binding — `outsystems-public-knowledge` |
|---|---|---|
| `grounding_search(query, scope="public")` | `search_outsystems_public` | `search_outsystems_public` (same tool name, served over the cloned public repos) |
| `fetch(doc_id)` | `fetch_doc` | `fetch_doc` |

Verified tool signature, both bindings **at current versions**:
`search_outsystems_public(query: str, top_k: int = 5, platform: str | None = None)`.
`top_k` is clamped to 1–20. `platform` accepts `'odc'` or `'o11'` and is
refused before dispatch when it is anything else; omit it to search both.
**Version floor for the colleague binding:** the `platform` argument exists
from engine wheel `workspace_knowledge_cc` 1.4.0 (first shipped in release
v35). **Pre-v35 components silently ignore the argument instead of refusing
it** — retrieval still answers, with O11 material crowding the results.
Probe when in doubt: pass `platform='bogus'` once — a current engine refuses,
a stale one answers as if unfiltered. On a stale engine, treat platform
filtering as unavailable: rely on query shaping (two-pass rule) and tell the
user to re-bootstrap from the current release.
Documents that apply to both platforms, and the platform-neutral OutSystems UI
guides, are returned either way. Pass `platform='odc'` for OMI work so O11
material does not crowd the result set. Then `fetch_doc(doc_id)` for the full
document.

The public corpus is exactly four mirrored repos — `docs-odc`, `docs-howtos`,
`docs-product`, and `outsystems-ui`. `docs-support` is **not** in it.

Measured composition, from a real OPK instance on 2026-08-07: **2633 documents,
of which 1780 (67.6%) are tagged `o11`** and 843 `odc` (2 both, 8 untagged).
`docs-product` is an O11 corpus. That is why `platform='odc'` is load-bearing
for OMI work rather than a refinement — it removes about two thirds of the
index before ranking.

The two aliases are interchangeable and public-only for this role. Internal,
course, archive, and workshop evidence routes separately through VPN-gated
`outsystems-tech-content`, never through this contract. OMI routes by capability
and availability instead of inferring quality from the alias or machine owner.

## Degraded behavior

If neither public-provider alias is available, use the four approved local
repositories (`docs-howtos`, `docs-odc`, `docs-product`, `outsystems-ui`) as an
explicitly degraded fallback. Require source-backed search and reads, keep the
fallback path visible in `Fallback Behavior`, and do not rely on model memory
alone. Internal, course, archive, and workshop evidence remains available only
through VPN-gated `outsystems-tech-content`; otherwise it is `Unverified or
blocked`.
