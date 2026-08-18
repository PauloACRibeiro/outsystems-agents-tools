# ODC Error-Code Registry

Rule (adapted from OutSystems/o11toodc-conversions-marketplace): this registry is
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

| Code | Layer | Meaning | Countermeasure | Owning skill · reference |
|---|---|---|---|---|
| OS-APPS-40028 | publish | AVS publish-time validation rejects invalid OML from Mentor-generated List/Table widgets, RadioGroup/ButtonGroup duplicate children, Identifier-bound Input widgets, or Server Action naming conflicts. | Strip the risky element (stub Container + Expression + Button instead), start a brand-new `mentor_start` session (no resume/patch path exists), and add the complex element manually in ODC Studio after a clean publish. | outsystems-mentor-implementation · references/odc-mentor-hardening.md |
| OS-DPL-50205 | deploy | "Model features validation failed" at deploy time despite zero pre-publish validation errors; known triggers are an authored `User`-typed attribute plus seed user-lookup, or a `GetUser(GetUserId()).User.Name` call inside an expression. | Author `User` references by hand in ODC Studio (Mentor may only carry them afterward) and replace the `GetUser().User.Name` expression with a literal; do not retry the same publish. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-BLD-40409 | publish | `ModelFeature_ServerActionPublicPropertyApp` — publish fails because Mentor set a Server Action's `Public` flag unprompted, a feature that has been removed. | Enumerate every Server Action's `Public` property (utility actions first) and leave `Public = false` on any action called only from within the app. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-DPL-50204 | deploy | Deploy-time failure from an in-place entity attribute type change on an attribute that already has data; conversion fails deterministically. | Add a new attribute with the target type, migrate the data, and retire the old attribute name instead of converting in place. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-DPL-RDBS-40020 | deploy | Deploy-time failure from dropping and recreating an attribute under the same name; retired attribute names stay burned across an app's deploy history. | Pick a fresh attribute name rather than reusing a previously dropped one. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-BEW-CODE-50008 | publish | Publish fails at "Generating database scripts" because Mentor emitted a static sort bound to a runtime value on a sortable list; re-introduced whenever Mentor regenerates that list. | Standing prompt line for any sortable list: implement sorting as a dynamic sort (`IsDynamic = True`), never a static sort on a runtime value. | outsystems-mentor-implementation · references/odc-platform-guardrails.md |
| OS-ABRS-FM-40005 | Mentor | Runtime exception raised when an ODC Portal agent guardrail (Prompt Attack Protection, Personal information exposure, or Harmful Content Filtering) is configured to block a request. | Add an exception path with a user-friendly message and monitor guardrail activity through Portal `MONITOR > Logs`. | outsystems-mentor-implementation · references/agentic-routing.md |
| OS-CLRT-60500 | deploy | Client-side runtime `TypeError: Cannot read properties of undefined (reading 'render')` that took live screens off the air after an unverified remedy was applied to a diagnosed issue. | Hold every remedy to the same evidence standard as its diagnosis — measure that the cure actually rendered correctly before trusting a `change_applied: true` report. | outsystems-mentor-implementation · references/execution-gates.md |
| OS-BERT-62000 | Mentor | BadRequest naming `response_format`, raised on the first agent call when the AI connection's configured model lacks `response_format: json_schema` support even though the app compiled and published cleanly. | Verify the actual model id and usage quota behind each AI connection against current provider docs before packaging the session; correcting the model id/quota takes effect without republishing the app. | outsystems-mentor-implementation · references/session-packaging-hardening.md |
| OS-AISA-40001 | Mentor | Mentor Studio conversation has hit its max length (its terminal `error` payload names the recovery in a `hint` field). | Resume with `fresh_context: true` on the same `mentor_session_id`/`mentor_session_token` to start a new conversation over the session's current edited OML without reverting unpublished edits; use a brand-new session (no `mentor_session_*`) only to fully reset to pristine tenant OML. | outsystems-mentor-implementation · SKILL.md |
| OS-RDBS-GEN-40002 | publish | "Unknown OsAttributeTypes" — an entity attribute `DataType` string outside the platform's closed enum (e.g. an `Identifier`-suffixed type) validates cleanly but fails the publish-time database-migration-script generator; surfaced through the MCP publish path as opaque `OS-DPL-50203`. | Use the literal `DataType` string `Long Integer` (with `IsAutoNumber`, `IsMandatory`, `IsPrimaryKey` set) for entity primary keys instead of any `Identifier`-suffixed type; when uncertain, read the literal string off an already-published app in the same tenant. | outsystems-mentor-implementation · references/odc-visual-source-enriched-blueprint.md |
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
