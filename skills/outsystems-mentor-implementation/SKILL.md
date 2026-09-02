---
name: outsystems-mentor-implementation
description: Use when the user asks for Studio-native ODC pseudocode, element placement, runtime boundary selection, action/event/timer design, Server Action or Client Action steps, UI event wiring, REST/integration logic placement, or paste-safe Mentor Studio prompts for a specific implementation block, including first scaffold prompts for a verified blank or existing ODC app shell.
---

> Canonical indexes: error codes `../shared/reference/odc-error-registry.md`; Mentor cadence `../shared/reference/mentor-operations-registry.md`.

# OutSystems Mentor Implementation

<!-- upstream-pin: 0.16.0 -->
<!-- mentor-mcp-surface: session-based, measured live 2026-09-02 -->

Express logic in ODC Studio terms, not generic software pseudocode. Use real element names, real parameter labels, and real runtime constraints. Never present unsupported or unverified elements as confirmed ODC capabilities. Legacy name: treat `mentor-studio-code` as historical/provenance wording for this skill, not an operational alias.

Use `outsystems-plan-to-mentor` instead when the user asks for a full implementation plan artifact, coverage review, saved plan, Mentor-ready spec, approval gate, or plan-to-Mentor workflow. If a plan needs Studio-native conversion, that skill owns the coverage gate and may invoke this skill with `Invocation mode: outsystems-plan-to-mentor`.

**A raw app idea is not this skill's input.** If the request is an idea for a
new app — screens described in prose, no reviewed plan, no `blueprint.json` —
this skill is being reached as step 5 of the sprint loop with steps 1–4 unrun.
Say so before producing anything: name the loop order (idea → requirements and
screen inventory → capability plan → screen design → plan review → build; see
`sprint-loop-for-colleagues.md` in this pack's docs), note that steps 1–2 come
from the separately-installed Superpowers plugin, and ask whether the user
wants the loop from step 1 or genuinely wants standalone pseudocode for one
bounded block. Proceed standalone only on their explicit choice — and scope
the output to the single block they name, never a whole app from an idea.

## Hard Gates (read before anything else)

- **MCP preflight (mode-keyed, required before any output):** Detect the knowledge provider — never configure it. Check which retrieval tool is callable, not merely registered, in this order:
  1. `search_outsystems_content` (`outsystems-tech-content`) → `provider: implementation-authority`. Full contract, unchanged; continue normally.
  2. otherwise `search_outsystems_public` (`workspace-knowledge-cc` or `outsystems-public-knowledge`, same tool either way) → `provider: public-grounded`. Continue to pseudocode and prompt output under the narrower authority in the next gate; do not emit the VPN block below.
  3. otherwise neither provider is callable:
  - For `mode: studio-native-pseudocode`, `mode: mentor-studio-prompt`, `mode: visual-source-ui`, `mode: existing-app-grounding` prompt output, and `Invocation mode: outsystems-plan-to-mentor`: stop immediately and tell the user:

> No OutSystems knowledge provider is reachable — `outsystems-tech-content` is unavailable and VPN is likely disconnected, and no public provider (`workspace-knowledge-cc` / `outsystems-public-knowledge`) is callable either. Connect VPN or start a public provider, then start a new session, or explicitly confirm that you want to proceed with degraded quality. Proceeding without either removes grounding for function signatures, widget rules, and TrueChange errors.

  Do not fall back silently. Do not produce pseudocode or Mentor prompts until a provider is confirmed available or the user explicitly acknowledges the degraded quality and accepts the risk.
  `mode: live-validation` and any mode not listed above keep the hard preflight block for pseudocode and prompt output by default.
  - For `mode: review-only` and `mode: mentor-web-orientation`: answer with degraded implementation authority. State the degradation in one line using the word "degraded", keep exact-signature, widget-rule, and TrueChange claims labeled `Unverified gap`, and follow the classifier's degraded behavior rules.

- **`provider: public-grounded` authority (asymmetric — never present it as implementation-level authority):** grounding is public OutSystems documentation only — `docs-odc`, `docs-howtos`, `docs-product`, `outsystems-ui` via `search_outsystems_public` (pass `platform='odc'` — requires the v35+ component; pre-v35 engines silently ignore it, see the provider contract's version floor; shape queries per [references/retrieval-query-bundles.md](references/retrieval-query-bundles.md)). Attribution is unconditional: every answer identifies its provider and authority in one line, carries its Evidence Status section, and carries `Unknowns And Fallback Behavior` whenever a material gap or fallback applies — never conditional on whether the answer happens to name sources. When retrieval returns nothing usable, say so, name the queries that were run, keep the affected claims `Unverified gap`, and never answer from model memory in their place. Still groundable here: built-in function signatures, from the public `docs-odc` built-in-functions reference, and widget/pattern facts from this skill's generated catalogs, which are built from public `docs-odc` — those keep `Catalog-backed official`. **Fail closed — name the gap, keep the claim `Unverified gap`, never guess:** TrueChange and platform validation error codes or exact error text; approved internal, courseware, archive, and workshop evidence; widget-library rules and UI pattern APIs beyond the generated catalogs; and anything else that materially rests on internal-only content. `Mixed official+archived` and `Course/example-backed` require `provider: implementation-authority`. The provider owns the routing contract: [references/knowledge-provider-contract.md](references/knowledge-provider-contract.md).

- **Execution identity and confirmation gate:** before any tenant-changing action (`app_create`, `mentor_create_asset`, `mentor_prompt`, `mentor_publish`, plus the pre-2026-09 `publish_start` / `mentor_start`, or any instruction that directly targets an existing app), ask explicit confirmation using the readable name, the exact action, and the canonical id from source (`APP_KEY`, `assetKey`, `runId`, etc.) when it already exists. For `app_create`, the id may not exist until after creation; in that case, confirm the readable app name plus environment context first, then verify and echo the returned canonical app key before continuing to app-targeted prompts or Mentor execution.
- **No implicit publish:** do not call `mentor_publish` (or the pre-2026-09 `publish_start`) or publish from this skill unless the user has explicitly approved publish to a specific environment in the current request. Do not ask twice when that approval is already clear and the target app/environment are unambiguous. Otherwise, treat publish as a handoff artifact for a later step. Resolve the environment by where the app actually lives (`env_app` / its key), never by display name or a config default — one tenant carries two environments both named `Development` (V81) — and never resolve a Production-purpose environment as an automated target: when the intended target cannot be resolved, stop and ask.
- No tenant mutation from any mode without exact current approval: no `app_create`, `mentor_create_asset`, `mentor_prompt`, `mentor_publish`, the pre-2026-09 `publish_start` / `mentor_start`, deploy, rollback, cleanup. Deliberately stricter than the upstream `outsystems-mcp` skill, which exempts in-memory Mentor edits from confirmation (governance decision 2026-07-11) — do not relax to match upstream.
- **Chrome coverage gate (before emitting a prompt package from any blueprint that declares `app_chrome`):** run `scripts/check_chrome_coverage.py <blueprint-or-design-dir> <emitted-prompt-file...>` against the **prompt package**, not the run document that quotes it, and obey the computed verdict. **This holds in MCP delivery mode too, where no prompt file exists by default: write the assembled per-screen prompts to a file and run the script on it BEFORE `mentor_prompt`.** A gate that runs only when a file happens to exist is not a gate — on the v2 run (2026-08-27) MCP delivery never assembled one and the gate was satisfied by hand. `chrome verdict: NOT READY` blocks emission until every dropped chrome element is instructed by a prompt; there is no deferral bypass. This is the visual track's equivalent of the logic track's coverage review — blueprint vs schema, blueprint vs blueprint, plan vs PRD and deployed model vs expected delta were all gated, and blueprint chrome vs emitted prompts was not. LoanDesk (2026-08-12): all six blueprints carried `app_chrome.menu` (Catalogue / My loans / Manage items) and the cross-blueprint report passed them, the prompts transcribed only `app_chrome.layout_block` as each screen's `Layout: LayoutTopMenu`, and the app deployed with no menu at all — `ManageItems` reachable by no route, URL only. Prose is not evidence, however well written: coverage needs the canonical `CHROME BATCH:` block whose form Chrome Batch Discipline defines (owned by the visual-source UI discipline file the Routing Table names). On that run all three labels appeared in the prompts as screen names.

### Mentor invocation discipline (when this skill drives a Mentor session)

When this skill sends a prompt through Mentor MCP, apply the same polling discipline as `outsystems-mentor-polling-behavior`. **Session-based surface, measured live 2026-09-02:** `mentor_start`, `mentor_cancel`, `publish_start` and `mentor_get_event` are no longer exposed. The sequence is `mentor_start_session()` -> `mentor_load_asset(sessionId, assetKey[, revision])` or `mentor_create_asset(sessionId, assetType, portfolioKey, name)` -> `mentor_prompt(sessionId, message)` -> poll `mentor_get_run(sessionId, runId)` -> `mentor_publish(sessionId[, comment ≤500 chars])` -> `publish_status(publish_key=<publicationKey>)` -> `mentor_close_session(sessionId)`. **One asset per session, one run at a time:** a second `mentor_prompt` while a run is in flight is silently ignored, so never fire one without a terminal state for the previous `runId`. Open one session per build sequence and **always close it**, including on abort — the session holds a server-side workspace and its unpublished edits die with it. Four contract fields lost their counterpart (`max_turn_time`, `fresh_context`, `internal_retry_count`, and the publish payload's `no_changes_detected` / `indeterminate`); each rule below states what replaces it, and `references/execution-gates.md` §4d pins the pre-2026-09 evidence.

- First poll: `mentor_get_run(sessionId, runId)` **without** cursor, immediately after `mentor_prompt` returns its `runId`.
- **Omit the cursor on every subsequent poll too.** A bare poll returns only undelivered events; a cursor is a *re-read* control (a previous `nextCursor`, or `0` for the whole history), so threading it back re-delivers events already in context. `outsystems-mentor-polling-behavior` still says to always pass it; the server's `mentor_get_run` description contradicts that and the description wins (quoted verbatim, execution-gates §4d). Terminal polls carry no `nextCursor` and no `pollIntervalMs` key (measured): stop when `status` is terminal *and* `nextCursor` is absent; `hasMore: true` means events still to drain.
- Poll cadence: poll immediately after `mentor_prompt` and again immediately while events keep arriving (events are batched — drain polls are correctness, not token waste); once drained (no new events) and non-terminal, pause for the response's served `pollIntervalMs` (`pollAfterMs` before 2026-09) — re-read it from every poll, it changes — and stop only on terminal `succeeded` / `failed` / `cancelled` / `not_found` (`not_found` means the run or its session is gone). **The advertised interval is a floor to raise, never one to obey downward (upstream 0.16.0, verified 2026-08-26; served value measured 1000ms on 2026-09-02):** sleep it *and at least ~30 seconds*, since each poll costs a whole model turn — chase a figure above 30s, never one below. The min is Mentor-only: `publish_status`, deploy and extlib polls follow their own description, 5–15s where it gives none. Never bare-`sleep` a pause (harnesses block it); use background-sleep and end the turn.
- At terminal, record `result.changeApplied` and `result.validation.errorCount` — **camelCase now** (measured); the snake_case `change_applied` / `validation.error_count` and `currentStep` are gone. New `result.attemptedChange` separates "tried and applied" from "answered without touching the model": `attemptedChange: false` on a turn meant to build something is a failed step. Route failures by the error's `data.category`, never message text: `ValidationError` -> fix the prompt/plan, no blind retry; `UpstreamError` / `InternalError` -> one retry, then pause and log; `AuthError` -> re-auth, don't touch the session. Two exceptions: an extlib upload busy-reject arrives as `ValidationError` but is transient — retry with backoff (registry); and a rejection naming `tenant_not_allowed` is a per-tenant allowlist gate, NOT a lapsed sign-in (upstream 0.16.0, verified) — the token is valid, so re-auth, re-registering and re-adding the server all fail identically while risking a working config. Confirm the configured host is the tenant meant (right account, wrong tenant returns this too); if it is right, stop and say the tenant needs enabling — retry once only if the user says it was.
- **Bound the turn, and read terminal time — not a retry count — as the health signal.** `Unverified gap`: `internal_retry_count` and `max_turn_time` both lost their counterpart (`mentor_prompt` takes only `sessionId`, `message`, `attachmentRefs`), so nothing server-side bounds a turn and no counter reports friction. Terminal time was always the real signal: healthy small turns reach terminal in 1–5 minutes; heavy structural turns legitimately run 8–12 with ~7 quiet minutes normal — judge "stuck" against the turn's size, not a flat timer. The stuck signature is now the event stream: **no new events across two consecutive drained polls spanning ~7–10 minutes with `status` still `working`.** The two server-side bounds that sat under the old ceiling are **unverified** here: an inter-event idle timeout (deployed 600s, terminal code `idle_timeout`) and a run-key lifetime of `max(1200s, max_turn_time + 300s)` — the second was defined in terms of a parameter that no longer exists, so no run-key TTL is currently known and the old advice to pass an explicit ceiling, never a small one, has nothing left to attach to. Set the turn's budget before sending it and enforce it client-side with `mentor_cancel_prompt`; turn size stays the lever (execution-gates §4), so split the work rather than wait longer. Never synthesise a retry count from event text — `builder_retry_friction` has no observable field left and is suspended until one appears.
- **Turn-error honesty:** a turn reporting an error leaves committed state unknown, so the next turn must **reconcile-verify** actual state — enumerate what the turn was to produce and read it back — before building on it; never resume from the summary's account of how far it got (measured on `OS-AISA-50001`). Two claims are never taken at face value. A Mentor claim that validation errors are validator **false positives**: the standard is **zero errors** or restructure until they resolve, and all six errors so labelled on the v1 build were real and fixable. And a summary disclosing a **downgraded** specified behaviour ("hidden for now, requires a future expression"): that is a failed step to fix now, not a note to carry. Both read as candour and function as a pass.
- Never keep reusing this skill without re-checking terminal state.
- If the user aborts, call `mentor_cancel_prompt(sessionId, runId)` and treat final status as terminal. It cancels only the session's *current* run (any other `runId` is a no-op) and **leaves the session open**, so it is not a teardown — still call `mentor_close_session`. Poll once after to confirm `cancelled`, and re-poll the `runId` before concluding a wedge: cancelling an already-succeeded run is a no-op you will misread.
- **Resume on the same `sessionId`; there is no session token to copy.** `sessionId` is a single opaque id returned once by `mentor_start_session`, never re-minted, and it survives a failed or cancelled run — the `mentor_session_id` + freshly minted `mentor_session_token` pair this skill copied through 0.16.0 does not exist here. A failed or cancelled turn still never advances committed state, so the recovery is unchanged in substance: **send the next `mentor_prompt` on the same `sessionId`**, since a new session re-downloads pristine tenant OML and drops unpublished edits. Start fresh only on a session-closed / session-not-found error, or on a bare first-turn `assetKey` init failure — the session-surface form of the first-turn `app_key` init failure, whose error is bare and carries no credentials to resume from. A timeout follows the same rule — retry the SAME session, never `mentor_create_asset`, which discards everything the session applied. Never pass a placeholder such as `"null"` as an `assetKey`; without a real key, ask the user.
- **`Unverified gap` — conversation-length recovery now costs a publish.** `fresh_context: true` started a new conversation over the session's *already-edited* OML, keeping its unpublished edits; no flag here does that. The only reset is `mentor_close_session` -> `mentor_start_session` -> `mentor_load_asset`, which reloads the *published* asset. So on max conversation length (`OS-AISA-40001`), on Mentor hallucinating elements that do not exist, or when switching task on the same app: **publish first, then reset** — publish under its own explicit approval (the §3d stale-base gate still binds), close, reopen, load the revision that publish produced. If the work is not publishable yet, say so and stop rather than reset over it; that loss is what the old flag avoided and is now paid every time.
- **Multi-turn build sequencing:** publish the data-model turn before the screen turns. Everything a turn changes lives only in the server-side session until published, and a lost session re-downloads the tenant OML, so unpublished work is gone; publishing first bumps the revision and gives every later turn a durable base, so a mid-sequence failure costs one turn, not the build. This binds *harder* now that `fresh_context` is gone — publishing is the only way to make a turn's work survive a reset. Each publish keeps its own explicit approval. **A `mentor_publish` refusal is not a publish to retry:** the refusal names the reason and the fix, and the remedy is a further Mentor turn that completes the work — never a second `mentor_publish`. A `succeeded` turn carrying `turn_error` is the common cause: it is not a finished task (execution-gates §3c), so the publish has nothing complete to take. Run multi-screen and data-model turns on the strongest reasoning tier the harness offers — they are the most reasoning-heavy calls on this transport, and small tiers retry without converging, burning more tokens than the stronger tier would have spent finishing; say so before starting a big build on a weak tier.
- **`Unverified gap` — the publish outcome lost `indeterminate` and `no_changes_detected`.** `mentor_publish` returns `{applicationKey, environmentKey, publicationKey, revision}`; `publish_status(publish_key=…)` returns `{key, applicationKey, applicationRevision, outcome, status}` and nothing else — measured `outcome: "in_progress"` / `status: "Running"` while building, `"success"` / `"Finished"` at terminal. (Its own tool description still documents `state`, `no_changes_detected` and `indeterminate`; that half describes the gateway `publish_start` path, no longer exposed — read it as pre-2026-09 surface.) The server no longer labels which outcomes it failed to observe, so the rule that flag carried applies to **every** ambiguous publish: on any non-`success` outcome, any error, or any lost response, re-poll `publish_status` with the same `publicationKey` or verify with `env_app` — **never publish again**. A second publish while the first is building is what wedges an app, and §3a says a Mentor-published app has nothing to roll back to. The no-change question is now the digest gate's alone. `outcome: "failed"` is genuinely terminal: surface its code (`OS-BEW-*` / `OS-DPL-*` in the 5xx band are retried server-side, so a returned 5xx means retries were exhausted) rather than re-publishing; a 4xx tail is a deterministic model rejection an unchanged re-publish cannot pass, so fix the model. Bands decode in `odc-error-registry.md`.
- **Digest gate (no-change rejection):** capture the app's `modelDigest` (plus revision) via `app_info` immediately before EACH approved publish, never per iteration (digests can repeat); `app_info` still serves `modelDigest` here (measured). Record the tip revision at session start too — for a `mentor_load_asset` flow that is the `revision` you loaded — so the pre-publish read doubles as the **stale-base gate**: tip advanced since session start means do NOT publish (a publish swaps in this session's full OML, last-writer-wins, erasing newer revisions); open a fresh session, `mentor_load_asset` the new tip and replay — execution-gates §3d. **What the digest gate cannot see now:** an asset from `mentor_create_asset` does not exist to `app_info` until its first publish (measured: HTTP 404), so that one publish has no baseline and no stale-base question — grade it by `mentor_publish`'s returned `revision` plus the enumeration gate and report `DIGEST: not applicable (first publish of a session-created asset)` rather than implying a pass. Every later publish, and every `mentor_load_asset` flow, is gated normally. Mentor summaries and MCP change signals are self-reports (recorded `no_changes_detected` false-negatives, one `change_applied` false-positive); the digest is the evidence. Session edits stay server-side, so the digest only moves at publish: re-read `app_info` after an approved publish and report `DIGEST: changed (<old> -> <new>)` or `DIGEST: unchanged`. Claimed-success publish with an unchanged digest = failed iteration — never count it as progress or hand it to grading; investigate or retry. If unpublished, report `not measurable pre-publish` rather than implying a pass. Adopted from the Enzyme investigation (2026-08-06): their build service rejects Mentor turns whose OML hash is unchanged rather than publishing an empty revision.
- **Enumeration gate (per phase, after the digest gate):** a phase gate must enumerate, never summarise. After each phase's approved publish, list the deployed model — `app_refs` plus the relevant `context_*` calls — and diff the returned names against that phase's expected element delta. Report counts and names (`server actions: expected 7, found 6, missing BookRoom`), never a sentence saying the phase completed. First live colleague sprint-loop run (2026-08-09): a session returned `change_applied: true` with two internal retries, zero validation errors and a detailed five-part summary for a server action that was never created, and the digest moved anyway because the phase's other elements did land — so the summary, the retry count, the error count and the digest gate all passed it. Enumeration was the only signal that caught it, and the same pass then caught two further discrepancies. `context_*` reads can lag a successful publish by ~20–90s (external field measurement, worse after multi-screen role changes), and a stale cache is indistinguishable from that same missing-element signature — so on a miss, check terminal deploy state and digest first; when both are green, wait ~90s and re-enumerate (`context_search` has been observed to catch up faster) before ruling. A missing element that survives that wait is a failed phase: re-author it before the next phase starts, checking its name against the entity auto-generated action collision first. Surplus elements are recorded, not ignored — dependency-closure extras widen the app's consumed producer surface. **For static entities, diff record LISTS against the spec, never counts** — Mentor silently normalises record identifiers (`Pratos do Dia` → `PratosDodia`) and can reorder records, and a count is green across both.
- **Assertion recompute (post-publish, after the digest gate):** when the iteration came from a blueprint whose screens declare `assertions`, recompute them against the BUILT model — `scripts/recompute_assertions.py --blueprint <blueprint.json> --oml <published .oml>`. `outsystems-ui-design`'s validator checks a blueprint against ITSELF; only this checks it against what was built, and it is the one mechanical guard against a Mentor summary describing widgets the model does not hold (trial F-17: filter widgets reported with `change_applied: true` and zero validation errors, none built). The ordering is structural, not preference — pre-publish there IS no element tree to inspect, session edits being server-side — so it runs after the digest gate, never earlier. Shortfall = failed iteration; surplus = drift, not failure. It fails closed: what the source cannot see is `UNSUPPORTED`, never a pass. `--oml` needs the internal CLI; the portable `--context-json` confirms a screen exists but not what is on it, since `context_screens` carries no widget data.
- **Wiring check (REQUIRED, after the screens phase publishes):** `scripts/check_control_wiring.py --oml <published .oml> --blueprint <blueprint.json>` over every screen the phase built. **Any unwired control = failed phase.** The recompute counts widgets; only this asks whether any of them DO anything (restaurant-app-v2, 2026-08-28: nine controls incl. both "+ Add" buttons had no handler yet passed every gate). `--blueprint` also diffs declared `main_content` regions against the built tree. Post-publish for the recompute's reason; `--oml` only; the AGENT downloads that `.oml` (§2c(d)), never the operator. Estate-internal tooling; without it, meet the requirement manually per `references/execution-gates.md` §2c(c).
- **Seed demo data before any UI verification, after the first full publish:** seed through the app's own create screens with a discriminating dataset — see `docs/sprint-loop-manual.md`'s Seed demo data step. Do not treat build-time blueprint seed values as sufficient for this.
- **Converge iteration (audit-driven):** a `Mentor handoff` block from `outsystems-runtime-ui-audit` is the sole instruction source — do not add fixes it does not list; keep the batch as given (capped worst-first) and pass it to the Mentor session per [references/prompt-templates/converge-iteration-instruction.md](references/prompt-templates/converge-iteration-instruction.md) (the handoff's fix text verbatim, nothing else). One Mentor session -> one approved publish -> digest gate; only `DIGEST: changed` proceeds to re-audit of the same URL — unchanged = failed iteration (retry or investigate; never re-audit). Stop at the handoff's target tier or after two consecutive audits with no weighted-score improvement; report score delta with the digest result. `outsystems-ui-review` reports are not a converge input until they define an equivalent bounded handoff. Enzyme adoption #2 (2026-08-06).
- **Execution, render and remedy gates:** build-time gates miss these. Execute actions before building on them; render signed in, twice for fetched values; never close a fix on its report; three failed fix turns on one defect escalate to a recorded ODC Studio inspection instead of a fourth; check `deploy_list`; a `details: true` poll at 5-6 min catches loops. [execution-gates.md](references/execution-gates.md)
- Polish gate (per screen, after render): type hierarchy, brand-colour restraint, spacing, realistic content, active state, real headings — and verify every UI fix by measured computed style, never by class presence — `references/execution-gates.md` §2b.
- Do not auto-render the polling dashboard from this flow; generate it only on explicit request.
- In a `Plan-to-Mentor` MCP execution path, this is the execution layer above the pseudocode output layer; if there is any mismatch in behavior, follow this discipline over generic MCP defaults.

## Route First

Open [references/source-map.md](references/source-map.md) first; it routes each question type to the right reference file. Classify the route mode with [references/omi-route-mode-classifier.md](references/omi-route-mode-classifier.md) before selecting the final output form. Emit exactly the section shape its Output Shape Matrix defines for that mode. OMI summarizes behavior in this skill file and routes detailed contracts to the source owner references; do not duplicate the canonical contract in runtime docs.

## Routing Table

| Trigger | Owner (open in this order) |
| --- | --- |
| Every question — route + mode first | references/source-map.md → references/omi-route-mode-classifier.md |
| Mentor Web/Studio capability, limitation, constraint claims | references/mentor-capability-constraint-matrix.md — the Mentor Capability And Constraint Matrix; ground claims in current OutSystems documentation and do not promote generated, dry-run, fixture-only, or screenshot-only evidence into product-contract wording |
| Complex plans, large features, multi-block output | references/prompt-narrowing-preflight.md — Plan Conversion Manifest for block decomposition, not plan shrinking; emit dependency-ordered blocks and run its coverage audit; run scripts/deterministic_quality_scorer.py before Claude review when its four artifacts exist |
| Retrieval, source refresh, degraded sources, implementation authority | references/retrieval-query-bundles.md |
| Live validation decisions, optional MCP validation | references/live-execution-intake.md |
| Target suitability proof: REST, Data Grid, agentic, screenshots, default entry, rollback | references/live-target-evidence-matrix.md (Live Target Evidence Matrix) |
| Live Mentor campaigns, fixtures, publish/rollback boundaries, OMI1 live preflight, same-execution-context OutSystems MCP proof, Computer Use / Claude fallback preflight, fresh evidence boundaries | references/live-execution-intake.md (entry owner — it routes onward) |
| Deploy preview, safe-to-promote, promotion readiness | references/optional-mentor-validation-patterns.md (Deployment Preview Gate) |
| Tenant inventory, existing-app evidence, dependency/blast radius | references/tenant-context-guardrails.md |
| UI generation: screens, blocks, patterns, bindings, UI events | references/odc-ui-framework-selection.md → references/odc-ui-prompt-inventory.md → references/odc-ui-generation.md |
| Visual sources: Figma, screenshots, HTML mockups, UI briefs | references/odc-visual-source-enriched-blueprint.md — build or validate the enriched blueprint before emitting any Mentor Studio prompt → (shell? references/odc-app-shell-first-scaffold.md) → references/odc-visual-source-ui-discipline.md → scripts/render_build_brief.py for per-screen build facts, carried verbatim → UI generation chain |
| App-shell first scaffold, blank shell, shell classification | references/odc-app-shell-first-scaffold.md |
| No-shell new-app asks | references/omi-route-mode-classifier.md (mentor-web-orientation); prefer shell-first via approved `app_create` |
| Fragile Mentor patterns: SQL, data writes, JSON Deserialize, statics, button OnClick, container reparenting, named existing screens | references/odc-mentor-hardening.md (wins over general rules on conflict) |
| Layering, security/server trust, query performance, timers/async, public APIs, `User` references, not-found guards | references/odc-platform-guardrails.md |
| Structured intent, Architect Mode, deterministic Mentor plans | references/structured-intent-mode.md |
| AI models, agents, guardrails, A2A, MCP, evaluations | references/agentic-routing.md |
| app-snapshot.yaml / studio-handoff.md intake | references/omi-snapshot-intake-mode.md |
| Evidence labels and source→label decisions | references/omi-evidence-status.md |
| Exact element syntax / placement-architecture depth | language-elements handbook and implementation-context guide (paths in source-map.md) |
| Evidence coverage or source-audit questions only | references/odc-pseudocode-source-manifest.md |

## Runtime Boundary — Decide First

Identify the correct runtime boundary before writing any pseudocode:

| Requirement | Correct boundary |
|---|---|
| UI, local state, screen interaction | `Screen`, `Block`, `Client Action`, lifecycle handlers |
| Screen/block data fetching | `Aggregate`, `Data Action`, `Refresh Data` |
| Backend writes, validation, integration calls | `Server Action` |
| Cross-app reusable backend logic | `Service Action` |
| Async integration between apps | `Event`, `Trigger Event` |
| Scheduled execution | `Timer`, `Wake<TimerName>` |
| Human/process orchestration | Workflow nodes and workflow system actions |
| Exposed or consumed external APIs | Consumed/exposed REST methods |
| Platform tenant automation | ODC REST APIs |
| Private-network or high-code logic | External libraries, external logic |
| Agentic flows | `Call<AIModelName>`, `Call<AgentName>`, `CallAgentV2`, `SendMessage`, agentic workflows |
| AI-assisted ODC authoring | Mentor Studio / Mentor Web guidance, with manual verification in ODC Studio |

If placement is the core question, open [references/source-map.md](references/source-map.md) → architecture section of the implementation-context guide.

## Response Contract

Use this output shape in every answer unless the user asks for something different:

### Placement
Name the owning ODC asset first. State the placement reason in one sentence. If sequencing or deployment order matters, note it here.

### Studio-Native Pseudocode
Return pseudocode in a fenced `text` block. One Studio element per line where possible. Use real ODC element names and parameter labels.

### Evidence Status
Use exactly one label:
One answer gets one main label — decided by the weakest source that
materially grounds it; never combine two labels in the Evidence Status line,
and put sub-claim caveats in prose or `Unknowns And Fallback Behavior`, not as
a second label. Do not name any other evidence label anywhere inside the
`### Evidence Status` section — not even in explanatory prose or parentheses;
describe stronger sub-claim grounding in plain words ("pattern facts come from
the generated official catalog") or move it to
`### Unknowns And Fallback Behavior`.
- `Current official` — grounded in current OutSystems docs, approved internal docs, or current tenant/tool observation
- `Catalog-backed official` — exact UI pattern facts come from the generated official ODC UI pattern catalog, but no curated recipe exists yet
- `O11-supported ODC candidate` — confirmed ODC Studio target or approved alias with support-only O11 `Designing Screens` reference facts; not current ODC authority
- `Mixed official+archived` — materially relies on archived official PDFs or combines current and archived official material
- `Course/example-backed` — materially relies on official courseware, workshop material, or `.oml` examples
- `OutSystems-public implementation evidence` — materially relies on the public `OutSystems/outsystems-ui` source repository for implementation details; not current ODC product-contract authority unless current ODC docs, Forge routing/version evidence, or tenant observations confirm the exposed behavior
- `Unverified gap` — not confirmed well enough by the current knowledge base

Label definitions, the source→label decision table, and the special rules for
dry-run/fixture evidence, `outsystems-ui` implementation facts, and the Forge
documentation bridge are owned by
[references/omi-evidence-status.md](references/omi-evidence-status.md). When in
doubt between two labels, that file decides.

Section ordering for every situation (base, UI, agentic, UI+agentic,
plan-to-mentor invocation, review/orientation) is owned by the
**Output Shape Matrix** in
[references/omi-route-mode-classifier.md](references/omi-route-mode-classifier.md).
Classify the mode first, then emit exactly that shape. For supported web UI
generation, still run `references/odc-ui-framework-selection.md` and
`references/odc-ui-generation.md` first; for agentic safety impact, still load
`references/agentic-routing.md` first.

Add one short line explaining why that label applies. Call out any unsupported node or unresolved gap in one line when needed.

### Unknowns And Fallback Behavior
Add this section when unresolved questions, degraded retrieval, unavailable tool
support, TrueChange gaps, or signature uncertainty materially affect confidence.
Use `Unknowns:` for the missing facts and `Fallback Behavior:` for the bounded
next action, such as pausing generation, using `Unverified gap`, or asking for a
live Studio/tenant check. Omit this section only when no material gap remains.
When neither `workspace-knowledge-cc` nor `outsystems-public-knowledge` exposes
the public provider's `grounding_search` role (see
`references/knowledge-provider-contract.md`), use `docs-howtos`, `docs-odc`,
`docs-product`, and `outsystems-ui` only as an explicitly degraded,
source-backed fallback. Name that path in `Fallback Behavior` when auditability
matters, and do not rely on model memory alone.

### Optional Constraints
Add only when they materially change the implementation:
- Transaction or commit visibility rules (mention `Read Committed` when event timing matters)
- Commit-before-event or commit-before-mashup requirements
- Security or permission boundaries
- Private gateway, external logic, A2A, MCP, or REST/runtime constraints
- Deployment order, timeout, evaluation, or debugger limitations

### Dependency Order (Mentor-safe emission order)

Before outputting any pseudocode, list prerequisites first so Mentor can create dependencies in the pasted order.

1. Data model definitions (Entities, Structures)
2. Site Properties
3. External contracts (Consumed REST APIs, Agent/REST endpoints, callbacks)
4. Events and Timers
5. Server Actions in strict dependency order

For Server Actions:
- List all required producer actions first, then consumers.
- If `A` uses `Run X` / `Trigger Y`, then `X` and `Y` must be fully listed before `A`.
- When a block is reused from an existing workspace, mark each reused item as `Already exists (use existing)` and still place it before first use.
- If dependencies are missing or cyclic, stop and ask for resolution before continuing that section.

Preferred format: emit the fenced skeleton in [references/prompt-templates/dependency-safe-order.md](references/prompt-templates/dependency-safe-order.md) verbatim, filling its placeholders (`[Asset Kind]` plus the ordered `[Block ...]` lines).

### Paste-safe response format (required)

When returning Studio logic, output the section skeleton in [references/prompt-templates/paste-safe-response-format.md](references/prompt-templates/paste-safe-response-format.md) in its exact order so each pasted block compiles in Mentor without missing dependencies — seven numbered sections from `1) Dependency inventory` (Already exists / To create) through data model, platform configuration, external integration, runtime orchestration, dependency-sorted server actions, and `7) Consumer/UI blocks`, filling each bracketed placeholder with the actual blocks.

For each block:
- Include only one block per message if this would prevent dependency confusion.
- If a block calls another block, ensure the callee block appears earlier in this same response.
- If two blocks are mutually dependent, stop and ask for expected dependency preference before continuing.
- Do not reorder within this sequence unless the user explicitly asks for a different order.

### Final Self-Check (before sending)

Verify before sending any answer:

1. There is exactly one `### Evidence Status` heading, at h3, containing exactly one label with no other label named anywhere in the section.
2. Section order matches the Output Shape Matrix for the classified mode.
3. `### Unknowns And Fallback Behavior`, when present, appears after `### Evidence Status`.
4. For visual-source answers, no tenant-mutation tool identifiers appear in the visible text.
5. When the answer is the full build handoff derived from an enriched blueprint or a screen inventory, every screen and entity that artifact declares is named somewhere in the answer, spelled exactly as the artifact spells it.

Before sending any answer except a preflight block, write the full draft text to a temporary file and run `scripts/response_contract_lint.py --answer <draft-file> --mode <mode>` to verify these checks deterministically — do this even if you would not otherwise save it. If you cannot write files or run scripts in this session, perform the five-item checklist above as rigorously as possible instead, and disclose in `### Unknowns And Fallback Behavior` that the deterministic lint could not run this session.

Check item 5 by adding `--blueprint <enriched-blueprint.json>` or `--inventory <screen-inventory.json>` to that command — but only when the draft is the whole handoff, because on an answer covering one requirement of several every uncovered screen reads as an omission. It runs in the omission direction only and does not flag the reverse.

## Output Contract - when invoked by outsystems-plan-to-mentor

Use this contract when the calling prompt explicitly includes `Invocation mode: outsystems-plan-to-mentor`.

- Input: coverage-reviewed patched plan, source PRD or original request, selected delivery mode, required output file path, and `Target app state` (new-app | template-scaffold | existing-app) plus a target app inventory when not new-app.
- Delivery mode: paste-prompts | outsystems-mcp writes sequential Mentor-ready prompts and then stops or routes MCP send.
- Output: Studio-native, deterministic Mentor content derived from the patched plan.
- Target scaffold rule: Do not assume a greenfield target. If `Target app state` is missing or invalid, or a non-new state lacks its inventory source, stop and ask. For `template-scaffold` or `existing-app`, inventory the existing scaffold before generating sessions, fold pre-existing elements in as modifications, and set each session's `Create Or Modify` column in the `Session Readiness Matrix`.
- File-first rule: write the Mentor-ready output file before any MCP send.
- No generic execution handoff: do not mention `superpowers:subagent-driven-development`, `superpowers:executing-plans`, Subagent-Driven execution, or Inline Execution as next steps.
- Authority: preserve this skill's OutSystems evidence, retrieval, and MCP preflight rules before producing pseudocode or Mentor prompts.

The 10-section Mentor spec is a summary, not a substitute for Studio-Native Pseudocode. Keep the 10-section spec for orientation, but the output file must also contain a complete pseudocode package for every capability covered by the patched plan.

Required output sections:

1. `Manual Setup Gate` - prerequisites that Mentor cannot safely create or verify. Tag each item as `manual-only`, `blocked-until-manual-setup`, or already verified. When the design depends on model capability (structured output, action calling, context size), include an AI-connection row verifying the actual model id against current provider docs plus the connection's usage quota. Do not open a Mentor session (`mentor_start_session`) or send a `mentor_prompt` until prerequisites are verified.
2. `Session Readiness Matrix` - one row per planned Mentor session with status `manual-only`, `blocked-until-manual-setup`, or `mentor_start-ready`, plus a `Create Or Modify` column (`mentor_start-ready` is a readiness label, not a tool name; the call it clears is `mentor_prompt`), evidence, and blocking dependency.
3. `Studio-Native Pseudocode` - detailed implementation blocks, not prose summaries. Include each applicable subsection:
   - `Data Model Pseudocode` with Static Entity records, Entity attributes, types, defaults, and relationships.
   - `Role Pseudocode` with roles, screen access, visibility rules, and guard placement.
   - `Server Action Pseudocode` with dependency-sorted actions, parameters, aggregate queries, validations, writes, status transitions, exceptions, and outputs.
   - `Client Action Pseudocode` with screen event handlers, local state changes, server calls, refreshes, notifications, and navigation.
   - `Screen And UI Pseudocode` with screens, blocks, aggregates/data actions, widgets, forms, tables/lists, buttons, input bindings, validations, empty/error/loading states, and role-based visibility.
   - `Navigation Pseudocode` with destination screens, input parameters, `ReturnTo` or equivalent return wiring, and cancel/back behavior.
   - `Verification Pseudocode` with publish/TrueChange checks, role-based smoke tests, data assertions, and regression checks from the patched plan.
4. `Mentor Executable Sessions` - paste-safe or MCP-sendable prompts derived from the pseudocode package. Each session must name prerequisites, an expected element delta (created and modified element names), verification, a `Traps` list (source-spelling preservation, similarly-named element disambiguation, join-type assertions, product-vocabulary prohibition by name on ODC targets), and whether it is `mentor_start-ready` or blocked. Write each session as a reconcile - ensure the element exists with the specified shape, update it to match when it already exists, never a bare create. Keep one action plus its verdict logic per session, split search logic from verdict assembly, and flag any session whose scope predicts a long Mentor run. The package must include a build-log table template, one row per session. See [references/session-packaging-hardening.md](references/session-packaging-hardening.md).

Lint the finished package with `scripts/response_contract_lint.py --answer <output-file> --mode plan-to-mentor`; it enforces the four sections and all seven subsections in order. Emit every subsection — one with nothing to say says so under its heading.

Do not rerun the coverage review in this skill. The caller owns the plan coverage gate and patched plan artifact.

## Pseudocode Authoring Rules

- Prefer `Run Server Action`, `Run Client Action`, `Assign`, `If`, `For Each`, `Refresh Data`, `Trigger Event`, `Raise Exception`, `Exception Handler`, `Send Email`
- Use real parameter labels: `Condition`, `Variable`, `Value`, `Record List`, `GridWidgetId`, `Exception Message`, `Log Error`, `Cache in Minutes`, `Max. Records`, `Server Request Timeout`
- Use `<ActionCall>.<OutputParameter>` for returned values
- Use `.Current` inside `For Each`
- Name the exact source binding for every derived local (count, sum, flag): `MatchCount` = length of `Matches`, never a `.Count` from a different aggregate than the list it describes
- Treat expressions ported from an existing app as unverified — ground them like new code; write containment filters as `Index(...) >= 0` because ODC `Index` is zero-based and returns `-1` when absent, so `> 0` drops position-0 matches
- Declare Setting defaults as `Default Value:` followed by the literal (inline or fenced); the response lint enforces ODC's 2,000-character Setting default cap
- Warn against `Aggregate` or `SQL` inside `For Each`
- Warn about multiple `Run Server Action` nodes inside a single `Client Action`
- Never present logic/control-flow `Switch`, `While`, `Break`, or `Continue` as current ODC elements; the UI `Switch` widget is allowed only through Tier 1 widget catalog evidence and must keep its evidence label.
- If a node is `archived-only`, `course/example-only`, or `unverified`, keep that explicit
- For `JSON Deserialize`, follow the canonical hardening pattern in [references/odc-mentor-hardening.md](references/odc-mentor-hardening.md): set `Output` to the structure name, then read fields through `Deserialize<StructureName>.Data...`; never read directly from `<StructureName>.<field>` after deserialize.
- If there is ambiguity about the structure name or the inferred `Deserialize<StructureName>` runtime object, ask before changing naming conventions.

## Placement Rules Summary

- `Client Action` — client orchestration and UI state changes
- `Server Action` — database writes, validations, integration calls, consolidated backend logic
- `Service Action` — logic reused across apps with weak dependency semantics
- `Data Action` or screen/block `Aggregate` — fetch logic that feeds UI state
- `Event` — async communication only; mention required commit before triggering
- `Timer` — scheduled execution; use `Wake<TimerName>` to trigger manually
- `Workflow` — human tasks and multi-step orchestration
- Exposed REST — when an external system needs to call into the ODC app
- Consumed REST — when the ODC app calls an external API
- External logic — private network access or high-code operations not possible in Studio
- Agentic app/service — when the feature involves AI model calls, agent orchestration, A2A/MCP tools, structured output, or agent evaluation
