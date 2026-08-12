---
name: outsystems-mentor-implementation
description: Use when the user asks for Studio-native ODC pseudocode, element placement, runtime boundary selection, action/event/timer design, Server Action or Client Action steps, UI event wiring, REST/integration logic placement, or paste-safe Mentor Studio prompts for a specific implementation block, including first scaffold prompts for a verified blank or existing ODC app shell.
---

# OutSystems Mentor Implementation

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

- **MCP preflight (mode-keyed, required before any output):** Detect the knowledge provider — never configure it. Check which retrieval tool is callable in this session, in this order:
  1. `search_outsystems_content` (`outsystems-tech-content`) → `provider: implementation-authority`. Full contract, unchanged; continue normally.
  2. otherwise `search_outsystems_public` (`workspace-knowledge-cc` or `outsystems-public-knowledge`, same tool either way) → `provider: public-grounded`. Continue to pseudocode and prompt output under the narrower authority in the next gate; do not emit the VPN block below.
  3. otherwise neither provider is callable:
  - For `mode: studio-native-pseudocode`, `mode: mentor-studio-prompt`, `mode: visual-source-ui`, `mode: existing-app-grounding` prompt output, and `Invocation mode: outsystems-plan-to-mentor`: stop immediately and tell the user:

> No OutSystems knowledge provider is reachable — `outsystems-tech-content` is unavailable and VPN is likely disconnected, and no public provider (`workspace-knowledge-cc` / `outsystems-public-knowledge`) is running either. Connect VPN or start a public provider, then start a new session, or explicitly confirm that you want to proceed with degraded quality. Proceeding without either removes grounding for function signatures, widget rules, and TrueChange errors.

  Do not fall back silently. Do not produce pseudocode or Mentor prompts until a provider is confirmed available or the user explicitly acknowledges the degraded quality and accepts the risk.
  `mode: live-validation` and any mode not listed above keep the hard preflight block for pseudocode and prompt output by default.
  - For `mode: review-only` and `mode: mentor-web-orientation`: answer with degraded implementation authority. State the degradation in one line using the word "degraded", keep exact-signature, widget-rule, and TrueChange claims labeled `Unverified gap`, and follow the classifier's degraded behavior rules.

- **`provider: public-grounded` authority (asymmetric — never present it as implementation-level authority):** grounding is public OutSystems documentation only — `docs-odc`, `docs-howtos`, `docs-product`, `outsystems-ui` via `search_outsystems_public` (pass `platform='odc'` — requires the v35+ component; pre-v35 engines silently ignore it, see the provider contract's version floor; shape queries per [references/retrieval-query-bundles.md](references/retrieval-query-bundles.md)). Attribution is unconditional: every answer identifies its provider and authority in one line, carries its Evidence Status section, and carries `Unknowns And Fallback Behavior` whenever a material gap or fallback applies — never conditional on whether the answer happens to name sources. When retrieval returns nothing usable, say so, name the queries that were run, keep the affected claims `Unverified gap`, and never answer from model memory in their place. Still groundable here: built-in function signatures, from the public `docs-odc` built-in-functions reference, and widget/pattern facts from this skill's generated catalogs, which are built from public `docs-odc` — those keep `Catalog-backed official`. **Fail closed — name the gap, keep the claim `Unverified gap`, never guess:** TrueChange and platform validation error codes or exact error text; approved internal, courseware, archive, and workshop evidence; widget-library rules and UI pattern APIs beyond the generated catalogs; and anything else that materially rests on internal-only content. `Mixed official+archived` and `Course/example-backed` require `provider: implementation-authority`. The provider owns the routing contract: [references/knowledge-provider-contract.md](references/knowledge-provider-contract.md).

- **Execution identity and confirmation gate:** before any tenant-changing action (`app_create`, `mentor_start`, `publish_start`, or any instruction that directly targets an existing app), ask explicit confirmation using the readable name, the exact action, and the canonical id from source (`APP_KEY`, `assetKey`, `runId`, etc.) when it already exists. For `app_create`, the id may not exist until after creation; in that case, confirm the readable app name plus environment context first, then verify and echo the returned canonical app key before continuing to app-targeted prompts or Mentor execution.
- **No implicit publish:** do not call `publish_start` or publish from this skill unless the user has explicitly approved publish to a specific environment in the current request. Do not ask twice when that approval is already clear and the target app/environment are unambiguous. Otherwise, treat publish as a handoff artifact for a later step.
- No tenant mutation from any mode without exact current approval: no `app_create`, `mentor_start`, `publish_start`, deploy, rollback, cleanup. Deliberately stricter than the upstream `outsystems-mcp` skill, which exempts in-memory Mentor edits from confirmation (governance decision 2026-07-11) — do not relax to match upstream.

### Mentor invocation discipline (when this skill triggers `mentor_start`)

When this skill sends a prompt through Mentor MCP, apply the same polling discipline as `outsystems-mentor-polling-behavior`:

- First poll: `mentor_get_run(runId)` **without** cursor.
- MCP 0.12.x terse default: non-terminal polls normally return `events: []` with `nextCursor: null` — an empty batch is expected, not a fault. Keep omitting the cursor until a poll returns a non-null `nextCursor`; from then on reuse each response's cursor on the next poll.
- Poll cadence: poll immediately after `mentor_start` and while `nextCursor` advances (events are cursor-paged and batched — drain polls are correctness, not token waste); once drained (no new events) and non-terminal, pause for the response's served `pollAfterMs` — re-read it from every poll, it changes; fall back to 30 seconds when absent — and stop only on terminal `succeeded` / `failed` / `cancelled`.
- At terminal, record `internal_retry_count` and `validation.error_count` from the payload; `internal_retry_count >= 3` is a friction flag even on success. Route failures by the error's `data.category`, never message text: `ValidationError` → fix the prompt/plan, no blind retry; `UpstreamError` / `InternalError` → one retry, then pause and log; `AuthError` → re-auth, don't touch the session.
- **Bound the turn, and read terminal time — not the retry count — as the health signal:** pass an explicit `max_turn_time` on every `mentor_start`, so a wedged turn has a terminal state to reach instead of running open-ended. First live colleague sprint-loop run (2026-08-09): every healthy authoring session reached terminal in 1-5 minutes, while the one unbounded outlier sat on the same internal step for 26 minutes and then returned `run_not_found` — no status, no error code, no refreshed session token, nothing to resume. Terminal time is therefore a usable health signal; `internal_retry_count` is not. Keep it as the prompt/platform mismatch detector it is — high retries mean the instruction asked for something the target cannot express, so fix the prompt and never raise a ceiling — and do not treat it as auditable: after a run goes terminal its event history is unreachable (`mentor_get_run` returns only trailing events, cursors page forward only), so the retry number has no retrievable account behind it.
- Never drop a non-null cursor on a subsequent poll and never keep reusing this skill without re-checking terminal state.
- If the user aborts, call `mentor_cancel` and treat final status as terminal.
- On a failed or cancelled run, the terminal `error` object carries the same `mentor_session_id` plus a freshly minted `mentor_session_token`, and the turn never advances committed state: resume the same session with those credentials (retry or continue the prompt) instead of starting a fresh `app_key` session — a fresh session burns a per-tenant slot and drops unpublished edits. Start fresh only when the error `code` is `session_not_found`, or on a first-turn `app_key` init failure, whose error is bare and carries no credentials.
- Recover with `fresh_context: true` — a resume-only flag on the mentor start call, passed alongside `mentor_session_id` + `mentor_session_token` — when the conversation hits max length (error `OS-AISA-40001`; its terminal `error` payload names this recovery in a `hint` field), when Mentor starts hallucinating entities or actions that do not exist, or when switching to another task on the same app. It starts a new conversation over the session's current, already-edited OML while keeping the session slot and unpublished edits; it does not revert the OML. A brand-new session (no `mentor_session_*`) is the reset path and re-downloads pristine tenant OML. The flag is strictly typed: send JSON `true`, never `"true"` or `1`; it is ignored on the first turn, and servers predating it reject the whole call, so send it only when recovering.
- **Digest gate (no-change rejection):** capture the app's `modelDigest` (plus revision) via `app_info` immediately before EACH approved publish, never per iteration (digests can repeat). Mentor summaries and MCP change signals are self-reports (recorded `no_changes_detected` false-negatives, one `change_applied` false-positive); the digest is the evidence. Session edits stay server-side, so the digest only moves at publish: re-read `app_info` after an approved publish and report `DIGEST: changed (<old> -> <new>)` or `DIGEST: unchanged`. Claimed-success publish with an unchanged digest = failed iteration — never count it as progress or hand it to grading; investigate or retry. If unpublished, report `not measurable pre-publish` rather than implying a pass. Adopted from the Enzyme investigation (2026-08-06): their build service rejects Mentor turns whose OML hash is unchanged rather than publishing an empty revision.
- **Enumeration gate (per phase, after the digest gate):** a phase gate must enumerate, never summarise. After each phase's approved publish, list the deployed model — `app_refs` plus the relevant `context_*` calls — and diff the returned names against that phase's expected element delta. Report counts and names (`server actions: expected 7, found 6, missing BookRoom`), never a sentence saying the phase completed. First live colleague sprint-loop run (2026-08-09): a session returned `change_applied: true` with two internal retries, zero validation errors and a detailed five-part summary for a server action that was never created, and the digest moved anyway because the phase's other elements did land — so the summary, the retry count, the error count and the digest gate all passed it. Enumeration was the only signal that caught it, and the same pass then caught two further discrepancies. A missing element is a failed phase: re-author it before the next phase starts, checking its name against the entity auto-generated action collision first. Surplus elements are recorded, not ignored — dependency-closure extras widen the app's consumed producer surface.
- **Assertion recompute (post-publish, after the digest gate):** when the iteration came from a blueprint whose screens declare `assertions`, recompute them against the BUILT model — `scripts/recompute_assertions.py --blueprint <blueprint.json> --oml <published .oml>`. `outsystems-ui-design`'s validator checks a blueprint against ITSELF; only this checks it against what was built, and it is the one mechanical guard against a Mentor summary describing widgets the model does not hold (trial F-17: filter widgets reported with `change_applied: true` and zero validation errors, none built). The ordering is structural, not preference — pre-publish there IS no element tree to inspect, session edits being server-side — so it runs after the digest gate, never earlier. Shortfall = failed iteration; surplus = drift, not failure. It fails closed: what the source cannot see is `UNSUPPORTED`, never a pass. `--oml` needs the internal CLI; the portable `--context-json` confirms a screen exists but not what is on it, since `context_screens` carries no widget data.
- **Converge iteration (audit-driven):** a `Mentor handoff` block from `outsystems-runtime-ui-audit` is the sole instruction source — do not add fixes it does not list; keep the batch as given (capped worst-first) and pass it to the Mentor session per [references/prompt-templates/converge-iteration-instruction.md](references/prompt-templates/converge-iteration-instruction.md) (the handoff's fix text verbatim, nothing else). One Mentor session -> one approved publish -> digest gate; only `DIGEST: changed` proceeds to re-audit of the same URL — unchanged = failed iteration (retry or investigate; never re-audit). Stop at the handoff's target tier or after two consecutive audits with no weighted-score improvement; report score delta with the digest result. `outsystems-ui-review` reports are not a converge input until they define an equivalent bounded handoff. Enzyme adoption #2 (2026-08-06).
- **Execution, render and remedy gates:** build-time gates miss these. Execute actions before building on them; render signed in, twice for fetched values; never close a fix on its report; check `deploy_list`; a `details: true` poll at 5-6 min catches loops. [execution-gates.md](references/execution-gates.md)
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
| Visual sources: Figma, screenshots, HTML mockups, UI briefs | references/odc-visual-source-enriched-blueprint.md — build or validate the enriched blueprint before emitting any Mentor Studio prompt → (shell? references/odc-app-shell-first-scaffold.md) → references/odc-visual-source-ui-discipline.md → UI generation chain |
| App-shell first scaffold, blank shell, shell classification | references/odc-app-shell-first-scaffold.md |
| No-shell new-app asks | references/omi-route-mode-classifier.md (mentor-web-orientation) |
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

Before sending any answer, write the full draft text to a temporary file and run `scripts/response_contract_lint.py --answer <draft-file> --mode <mode>` to verify these checks deterministically — do this even if the answer was never otherwise going to be saved to a file. If you cannot write files or run scripts in this session, perform the four-item checklist above as rigorously as possible instead, and disclose in `### Unknowns And Fallback Behavior` that the deterministic lint could not run this session.

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

1. `Manual Setup Gate` - prerequisites that Mentor cannot safely create or verify. Tag each item as `manual-only`, `blocked-until-manual-setup`, or already verified. When the design depends on model capability (structured output, action calling, context size), include an AI-connection row verifying the actual model id against current provider docs plus the connection's usage quota. Do not call `mentor_start` until prerequisites are verified.
2. `Session Readiness Matrix` - one row per planned Mentor session with status `manual-only`, `blocked-until-manual-setup`, or `mentor_start-ready`, plus a `Create Or Modify` column, evidence, and blocking dependency.
3. `Studio-Native Pseudocode` - detailed implementation blocks, not prose summaries. Include each applicable subsection:
   - `Data Model Pseudocode` with Static Entity records, Entity attributes, types, defaults, and relationships.
   - `Role Pseudocode` with roles, screen access, visibility rules, and guard placement.
   - `Server Action Pseudocode` with dependency-sorted actions, parameters, aggregate queries, validations, writes, status transitions, exceptions, and outputs.
   - `Client Action Pseudocode` with screen event handlers, local state changes, server calls, refreshes, notifications, and navigation.
   - `Screen And UI Pseudocode` with screens, blocks, aggregates/data actions, widgets, forms, tables/lists, buttons, input bindings, validations, empty/error/loading states, and role-based visibility.
   - `Navigation Pseudocode` with destination screens, input parameters, `ReturnTo` or equivalent return wiring, and cancel/back behavior.
   - `Verification Pseudocode` with publish/TrueChange checks, role-based smoke tests, data assertions, and regression checks from the patched plan.
4. `Mentor Executable Sessions` - paste-safe or MCP-sendable prompts derived from the pseudocode package. Each session must name prerequisites, an expected element delta (created and modified element names), verification, a `Traps` list (source-spelling preservation, similarly-named element disambiguation, join-type assertions, product-vocabulary prohibition by name on ODC targets), and whether it is `mentor_start-ready` or blocked. Write each session as a reconcile - ensure the element exists with the specified shape, update it to match when it already exists, never a bare create. Keep one action plus its verdict logic per session, split search logic from verdict assembly, and flag any session whose scope predicts a long Mentor run. The package must include a build-log table template, one row per session. See [references/session-packaging-hardening.md](references/session-packaging-hardening.md).

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
