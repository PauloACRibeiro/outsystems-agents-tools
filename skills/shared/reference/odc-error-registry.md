# ODC Error-Code Registry

Rule (adapted from an internal OutSystems team's service-registry pattern): this registry is
the canonical INDEX of ODC error codes — one row per code, giving its layer,
meaning, countermeasure, and the file that holds the long-form treatment. Skills
resolve a code's meaning here first. The owning file keeps its full treatment; a
skill that needs more than the row provides follows the Owning column. Adding a
code's treatment to a file that is not its owner, or letting a row's meaning drift
from its owner's text, is a lint finding.

Note: some rows name an owning skill that is estate-only and not part of every
distribution pack. Where the owning file is absent, the row itself — layer,
meaning, countermeasure — is the usable guidance.

Diagnostics: see `odc-diagnostics-recipes.md` for the live tool-call sequence
that surfaces the evidence behind any row below.

## Code bands

This section decodes the Code column; it adds no rows. The registry stays keyed
by observation — a code earns a row when someone hits it — but a band can be
read off any build-worker code, including one with no row yet, and it answers
the only question asked in the moment: is re-publishing this worth anything?

Build-worker codes end in a five-digit tail that the platform's own message
catalogs write as `NNN_NN`, grouped under band comments:

| Tail | Catalog grouping | What it means for a retry |
|---|---|---|
| `000_xx` | Warnings | Not a failure. The build carries the message and continues. |
| `400_xx` | Validation errors | A **deterministic** rejection of the model as authored — a static entity with an auto-number identifier, a server action exposed on a weak application reference, a name that is not a valid identifier. The same OML fails the same way, so **do not re-publish unchanged; fix the model**. |
| `500_xx` | Business and internal errors | The band our publish contract's server-side-retry lore is about — but it is **not uniformly transient**. The same band holds deterministic business errors (a resource target directory that is too long, a resource that cannot be opened) that no retry would clear, so a 5xx tail licenses one re-read of the message, not a retry loop. |

Three limits on how far this can be pushed:

- **The catalogs establish determinism, not retry policy.** They define message
  text and band grouping and say nothing about what the publish pipeline
  retries; the server-side-retry claim is the upstream plugin contract's, cited
  where it is used. Nothing here takes a position on the pipeline's internal
  retry behaviour for any band — it does not matter. Determinism alone settles
  the action: the same OML fails the same way, so an unchanged re-publish cannot
  pass, whatever the pipeline did or did not try first.

- **The band is a routing hint, not a countermeasure.** It tells you whether to
  reach for the model or for the message trail. The rows below, and the owning
  files they point at, are what actually say *what* to change.
- **The full `OS-BEW-<PREFIX>-<tail>` string is composed outside these
  catalogs.** They define a bare integer code plus an optional second prefix —
  `RDM` for the data-model generator, `DFAB` for data fabric, `POST` for
  frontend post-processing; the backend code generator declares none at this
  revision, with a comment saying so. `RDM` in the `OS-BEW-RDM-50001` row is
  therefore traceable to a catalog; the `CODE` in `OS-BEW-CODE-50008` is not,
  and any wider prefix-to-catalog mapping is unverified.

Source (read-only, via `gh api` 2026-08-27): message catalogs under `src/` in
`OutSystems/OutSystems.Backend.Build.Worker` at
`17bfd5794ad4162460185ac13c000a08a3744a5b` and
`OutSystems/OutSystems.Frontend.Build.Worker` at
`9e07acd1ad2bd54967063a948f064ca922f6d681`. Both are internal repos; the
catalogs are authoritative for message text and band grouping, and for nothing
beyond that.

## Tool-level fault axis

This section decodes a layer *below* every `OS-*` code in the table; it adds no
rows. Mentor's turn is many host tool calls, and each call carries a fault
classification that never reaches the MCP error payload. Reading it matters for
one reason: two of its shapes make a failed edit arrive as a green signal.

**The axis is who is at fault, never how bad it is.** A host tool call ends in
one of two classes — a **caller fault** (the input was wrong: a bad key, code
that does not compile) or a **tool fault** (the tool itself broke) — plus two
pass-throughs that are neither: a **cancellation**, which is not recorded at
all, and a **corrupted model**, which means the session's in-memory model is
unusable until the host reloads it. The consequence worth carrying: a caller
fault counts as a **successful execution** in the host's own reliability
metric, because the tool worked correctly when it correctly rejected bad input.
A platform-side "tool success rate" therefore does not count compile rejections
or bad keys as failures.

**The write verb rejects in two different shapes.** A compile error or a
sandbox-restriction violation is *thrown* — the caller sees an error carrying
the list of compilation errors (`(line,col) error: CS…`) or the list of
restriction errors. Nothing ran, and the rejection is deterministic: the same
code fails the same way. A runtime exception *inside* code that did run is not
thrown at all — the call returns a normal result whose `exceptionMessage` is
set, with the stack trace withheld unless the host budgets it. That second
shape is the phantom-success class, and it is the one public docs acknowledge
without mechanism under "Success reporting". What was applied before the throw
is decided inside the engine and is not established here.

**The reference-adding call reports per item, and the call as a whole
succeeds.** Its result carries a referenced list and an errors list; the reason
text is the only channel, and the closed list of reasons is: a key that cannot
be parsed; a producer requested at multiple revisions; conflicting upgrade
flags for one producer; a producer signature that cannot be resolved; an
indirect producer signature that cannot be resolved; a producer that is a
library with no version tag; an element not found in the producer; an element
not found in the currently referenced version, which asks for a retry with the
upgrade flag set; and one internal-error reason. Only the version-tag reason
has a documented product rule behind it — see guardrail 9 in
`outsystems-plan-to-mentor/references/mentor-spec-guardrails.md`, and the
library first-release rule in ODC's public library documentation.

**Validation messages are typed, per call.** Every write result, and the
validation read verbs, carry entries shaped `{ id, type: Info | Warning |
Error, message, detail, ownerKey, ownerPath, ownerType }` — TrueChange, scoped
to that call. The per-turn `validation.error_count` roll-up an agent sees is
above this layer.

Three limits, the same discipline the Code bands section states:

- **It decodes, it does not prescribe.** The axis tells you whether to reach
  for the input or for the tool; what to change is the rows below and the files
  they point at.
- **Determinism only, never retry policy.** A compile or restriction rejection
  is deterministic, so re-sending the same code cannot pass. A tool fault says
  nothing at all about whether a retry would clear it.
- **The mapping onto the MCP error's `data.category` is unverified.** Nothing
  here licenses a change to category-based routing; the routing rule in
  `outsystems-mentor-implementation/SKILL.md` stands untouched, and the one
  documented exception to it is the Error-category routing exceptions section
  below.

Public docs draw a different boundary: ODC's Mentor Studio error pages group
their codes into three categories by *where* the failure occurs — the Mentor
Studio service, the AI Provider service, and conversation state — and none of
those three is this axis. So this layer is not visible in the public taxonomy
and must not be read into it.

Source (read-only, 2026-09-02): the platform's own agent-tool source and the
thin shell that consumes it, two internal repositories read at commits pinned
2026-08-31 and 2026-08-28. The pins, the file-and-line citations and the
verdicts are in the batch record under `docs/adoption/`; they are named there
rather than here because internal repository names do not ship. The source is
authoritative for facts about the tools themselves — a parameter name, an
exception type, a reason string — and for nothing about Mentor's deployed
build, which was not observed.

The rows below are the registry proper. Nothing in this section adds one.

| Code | Layer | Meaning | Countermeasure | Owning skill · reference |
|---|---|---|---|---|
| OS-APPS-40028 | publish | AVS publish-time validation rejects invalid OML from Mentor-generated List/Table widgets, RadioGroup/ButtonGroup duplicate children, Identifier-bound Input widgets, or Server Action naming conflicts. | Strip the risky element (stub Container + Expression + Button instead), start a brand-new Mentor session (`mentor_start_session` + `mentor_load_asset`; pre-2026-09 `mentor_start`) because no resume/patch path exists, and add the complex element manually in ODC Studio after a clean publish. | outsystems-mentor-implementation · references/odc-mentor-hardening.md |
| OS-DPL-50205 | deploy | "Model features validation failed" at deploy time despite zero pre-publish validation errors; known triggers are an authored `User`-typed attribute plus seed user-lookup, or a `GetUser(GetUserId()).User.Name` call inside an expression. | Author `User` references by hand in ODC Studio (Mentor may only carry them afterward) and replace the `GetUser().User.Name` expression with a literal; do not retry the same publish. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-BLD-40409 | publish | "Using the feature X, a feature that has been removed" — publish fails because Mentor set a model feature ODC no longer supports, unprompted. Three are on file: `ModelFeature_ServerActionPublicPropertyApp` (a Server Action's `Public` flag), and `ModelFeature_DeleteRuleOnReferences` / `ModelFeature_DeleteRuleOnSystemReferences` (a delete rule on a foreign-key attribute, system references such as `User` included). | For the `Public` flag: enumerate every Server Action's `Public` property (utility actions first) and leave `Public = false` on any action called only from within the app. For delete rules: instruct every data-model prompt to create FK attributes with no delete-rule configuration, system references included, and strip the config from every affected attribute in one further Mentor turn on the same session — referential behaviour belongs in server actions, not in a delete rule. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-DPL-50204 | deploy | Deploy-time failure from an in-place entity attribute type change on an attribute that already has data; conversion fails deterministically. | Add a new attribute with the target type, migrate the data, and retire the old attribute name instead of converting in place. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-DPL-RDBS-40020 | deploy | Deploy-time failure from dropping and recreating an attribute under the same name; retired attribute names stay burned across an app's deploy history. | Pick a fresh attribute name rather than reusing a previously dropped one. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-BEW-CODE-50008 | publish | Publish fails at "Generating database scripts" because Mentor emitted a static sort bound to a runtime value on a sortable list; re-introduced whenever Mentor regenerates that list. | Standing prompt line for any sortable list: implement sorting as a dynamic sort (`IsDynamic = True`), never a static sort on a runtime value. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-ABRS-FM-40005 | Mentor | Runtime exception raised when an ODC Portal agent guardrail (Prompt Attack Protection, Personal information exposure, or Harmful Content Filtering) is configured to block a request. | Add an exception path with a user-friendly message and monitor guardrail activity through Portal `MONITOR > Logs`. | outsystems-mentor-implementation · references/agentic-routing.md |
| OS-CLRT-60500 | deploy | Client-side runtime `TypeError: Cannot read properties of undefined (reading 'render')` that took live screens off the air after an unverified remedy was applied to a diagnosed issue. | Hold every remedy to the same evidence standard as its diagnosis — measure that the cure actually rendered correctly before trusting a `change_applied: true` report. | outsystems-mentor-implementation · references/execution-gates.md |
| OS-BERT-62000 | Mentor | BadRequest naming `response_format`, raised on the first agent call when the AI connection's configured model lacks `response_format: json_schema` support even though the app compiled and published cleanly. | Verify the actual model id and usage quota behind each AI connection against current provider docs before packaging the session; correcting the model id/quota takes effect without republishing the app. | outsystems-mentor-implementation · references/session-packaging-hardening.md |
| OS-AISA-40001 | Mentor | Mentor Studio conversation has hit its max length (its terminal `error` payload names the recovery in a `hint` field). | Resume with `fresh_context: true` on the same `mentor_session_id`/`mentor_session_token` to start a new conversation over the session's current edited OML without reverting unpublished edits; use a brand-new session (no `mentor_session_*`) only to fully reset to pristine tenant OML. | outsystems-mentor-implementation · SKILL.md |
| OS-RDBS-GEN-40002 | publish | An entity-attribute value outside a platform closed enum: it validates cleanly and then fails the publish-time database-migration-script generator. Two are on file — "Unknown OsAttributeTypes" (a `DataType` string outside the enum, e.g. an `Identifier`-suffixed type; surfaced through the MCP publish path as opaque `OS-DPL-50203`) and "Invalid delete rule" (a `DeleteRule` argument value, raised alongside `OS-BLD-40409` and `OS-DPL-50205` when Mentor sets delete rules on foreign keys by default). | For `DataType`: use the literal string `Long Integer` (with `IsAutoNumber`, `IsMandatory`, `IsPrimaryKey` set) for entity primary keys instead of any `Identifier`-suffixed type; when uncertain, read the literal string off an already-published app in the same tenant. For `DeleteRule`: create FK attributes with no delete-rule configuration, system references included — see the `OS-BLD-40409` row, which owns that treatment. | outsystems-mentor-implementation · references/odc-visual-source-enriched-blueprint.md |
| OS-RDBS-GEN-40001 | publish | "Null record PK" — a Static Entity with `IsAutoNumber = Yes` leaves every design-time record with a null primary key, validating cleanly but failing publish; surfaced through the MCP publish path as opaque `OS-DPL-50203`. | Set `IsAutoNumber = No` and give every Static Entity record an explicit, non-null integer `Id` plus a populated Label/display attribute. | outsystems-mentor-implementation · references/odc-visual-source-enriched-blueprint.md |
| OS-DPL-50203 | deploy | Opaque deploy-time wrapper surfaced through the MCP publish path for the underlying database-migration-script generator failures `OS-RDBS-GEN-40002` (invalid attribute `DataType`) and `OS-RDBS-GEN-40001` (static entity null record PK). | Check entity/static-entity `DataType` and `IsAutoNumber`/`Id` settings first, per the two underlying `OS-RDBS-GEN-*` rows, rather than guessing at the cause. | outsystems-mentor-implementation · references/odc-visual-source-enriched-blueprint.md |
| OS-AIMS-40401 | quality-API | On-demand ODC Code Quality trigger returns `TriggerFailed` — `HTTP 404 OS-AIMS-40401 "The record doesn't exist"` — for `Agent` (Agentic Apps) and `Workflow` assets; Mentor never produces a real analysis for these asset types and the ODC Portal Code Quality console omits them entirely. | Don't report a score for Agents/Workflows and don't treat the 404 as "clean" — the absence of a listing is not a passing result. `analyze --all` (no `--type`) defaults to only `WebApplication`/`LowCodeLibrary` for this reason; pass `--type Agent`/`--type Workflow` explicitly only to see the failure for yourself. | outsystems-code-quality-score · SKILL.md |
| OS-CLRT-00000 | deploy | One of the permission-wall marker strings (alongside `"Not Authorized"` / `"Invalid Permissions"`) that render-gate's `permissionMarkers.texts` watches for in the rendered DOM to detect a screen returning a permission-denied wall instead of the expected content. | A permission wall found on a screen the spec says the principal should reach is recorded as a finding — it fails that screen's verification row and the run continues; it is never silently read as a pass. | outsystems-render-gate · SKILL.md |
| OS-BEW-RDM-50001 | publish | Server-build failure that can surface (alongside `OS-DPL-50205`, "or similar") when stale `ReferersData.xml` / `ReferersForCompilerData.xml` caches — left over from manual XML edits outside the Model API — are uploaded to ODC for publish. | Strip the stale `ReferersData.xml` / `ReferersForCompilerData.xml` files before publish; the server will rebuild them. | outsystems-design-to-app · references/gotchas/publish-validator-rejections.md |

## Error-category routing exceptions

Failures are routed by the error's `data.category`, never by message text —
with one documented exception, recorded here so the routing rule itself can
stay simple.

| Case | Category served | Why the category misleads | Correct handling |
|---|---|---|---|
| External-library upload arriving while every per-replica concurrency permit is held: waits 5s, then rejected with `Server is busy, retry shortly` (upstream plugin 0.13.1) | `ValidationError` | `ValidationError` normally means "fix the prompt/plan, no blind retry" — fatal. Here the condition is transient. | Match that message string to recognise the case and retry with backoff. This is the ONE place message text is load-bearing; keep routing everything else by category alone. |

## Static vs live facts (resolve, never hardcode)

Static facts (portal-only steps such as library release, URL patterns,
error-code semantics) live in this shared/reference directory. Live tenant
facts (app keys, env keys, revisions, runtime URLs) are resolved at run time
via the OutSystems MCP (`app_list`, `env_list`, `env_app`) and MUST NOT be
inlined into any skill body. Tenant-shaped literals in a skill are a lint
finding; the ES-sandbox keys in session memory are memory, not skill content.
