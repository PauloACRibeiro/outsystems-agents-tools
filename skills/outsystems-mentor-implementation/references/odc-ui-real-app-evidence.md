# ODC UI Real-App Observed Evidence

Use this reference only when the user asks to compare Mentor Studio UI prompts with a real ODC app, mine an app for UI-generation examples, or decide whether an observed pattern deserves a curated recipe.

Real-app observed evidence is not official platform authority. Official OutSystems docs and generated official catalogs still decide whether a widget, pattern, property, event, or dependency is `Current official` or `Catalog-backed official`.

Observed app evidence can show how a working app combines producers, dependencies, screens, actions, structures, themes, and naming. Label outputs that rely materially on this file as `Course/example-backed` unless official docs independently support the exact fact.

## Boundary Rules

- do not promote an observed app pattern to `Current official`.
- Do not claim a curated recipe exists because one app uses a pattern.
- Do not infer exact widget trees, widget ids, local variables, bindings, or events unless the source explicitly exposes them.
- Treat inferred UI structure as inferred and include a review note.
- If exact screen widget trees are needed, ask Paulo before using Mentor or another OML-deep inspection path.
- Use observed app evidence to improve prompt order, naming realism, dependency inventory, pseudocode comparison, and recipe-candidate triage.

## Read-Only MCP Evidence Workflow

Use this workflow when Paulo asks to use a real ODC app as UI prompt evidence.

If the target app identity comes from tenant inventory or cached tenant evidence, open `tenant-context-guardrails.md` first and record a Tenant Context Packet before app-specific evidence capture. Use the packet for target identity, freshness, dependency inventory, and unknowns; do not treat it as proof of exact widget trees or Studio internals.

1. Find the app with `app_list` using the app name or a narrow search term.
2. Confirm the target with `app_info`.
3. Capture dependency producers with `app_refs`.
4. Capture UI surfaces with `context_screens`.
5. Capture logic producers with `context_actions`.
6. Capture data producers with `context_entities`.
7. Capture DTO and response producers with `context_structures`.
8. Capture visual/theme evidence with `context_themes`.
9. Use `context_search` only for narrow follow-up questions against the same app.
10. Summarize what was observed, what was inferred, and what remains missing.

Do not use Mentor, publish, deploy, or external library tools for evidence gathering unless Paulo explicitly approves a separate tenant-changing or deeper-inspection action.

Always record:

- app name, type, revision, and revision timestamp
- Tenant Context Packet and evidence freshness label when tenant inventory or cached tenant evidence selected the target
- references and producer dependencies
- screens and UI flows
- actions and important parameters
- entities, static entities, and structures
- themes and CSS evidence
- missing facts that MCP context did not expose

## Evidence Capture - Elastic Search Sandbox

Source: OutSystems MCP read-only inspection of an ODC tenant on 2026-05-23.

Read-only tools used: `auth_status`, `env_list`, `app_list`, `app_info`, `app_refs`, `context_screens`, `context_actions`, `context_entities`, `context_structures`, `context_themes`, `context_roles`, and `context_search`.

No publish, deploy, Mentor edit, external library upload/download, or tenant-changing action was used for this evidence.

App:
- Name: `Elastic Search Sandbox`
- Type: `WebApplication`
- Revision observed: 23
- Revision timestamp observed: 2026-05-22T09:55:47Z
- Purpose observed from app description: companion sandbox for the Elastic Search Connector Library, with setup tips and example screens for calls to an ElasticSearch endpoint.

References observed through `app_refs`:
- `(System)`
- `OutSystemsUI` version 2.28.1
- `JSONBeautifier` version 1.0.1
- `ElasticSearchConnector`
- `Sanitization`

Main screen set observed through `context_screens`:
- Common/auth screens: `Login`, `RecoverPasswordRequest`, `RecoverPasswordReset`, `UserProfile`, `ChangePassword`, `InvalidPermissions`
- Setup/reference screens: `Setup`, `Reference`
- Index screens: `Index_GetList`, `Index_Create`, `Index_LoadData`, `Index_Delete`, `Index_SetAlias`
- CRUD sample screens: `CRUD_Create`, `CRUD_Retrieve`, `CRUD_Update`, `CRUD_Delete`
- Search sample screens: `Search_Query`, `Search_Multiple`
- Advanced sample screens: `Adv_Dictionary`, `Adv_EmailSentLog`, `Adv_ChangeHistory`, `Avd_ReIndex`, `Adv_FunctionScore`
- Migration screen: `MigrationDashboard`

Data and structure producers observed:
- Entity producers include `Allrecordings`, `TimerBLRM`, `QueryLists`, `ESMigrationRun`, `ESMigrationBucket`, `ESMigrationFailure`, `ESMigrationMetric`, `ESMigrationRunStatus`, and `ESMigrationBucketStatus`.
- Structure producers include `Record_Music`, `ES`, `Shard`, `Excel_allrecordings`, `RecordingMusicESDocument`, `source`, `RecordingMusicBounds`, `BulkInsertResponse`, `InsertedBucketResult`, and `BulkIndexResult`.

Action producers observed:
- Index actions: `ListExistingIndexes`, `CreateNewIndex`, `DeleteExistingIndex`, `IndexSetAlias`, `IndexRemoveAlias`
- Object CRUD/search actions: `CreateObject`, `CreateObjectById`, `GetObjectById`, `GetObjectByQuery`, `UpdateObjectById`, `DeleteObjectById`, `InsertDataInBulk`
- Reindex/task actions: `Reindex`, `CancelTaskById`, `GetTaskById`
- Migration actions: `PrepareNewMigrationRun`, `SetMigrationRunning`, `DispatchMigrationBuckets`, `ClaimMigrationBucket`, `HandleProcessMigrationBucket`, `ParseBulkIndexResponse`
- Bootstrap/profile/auth actions: `BootstrapAllrecordings`, `BootstrapESDataInIndex`, `InitTimerIndexBLRM`, `DoLogin`, `UpdateUser`, `SendResetPasswordEmail`

Theme and UI style evidence observed:
- The app uses an application theme with a 12-column fluid grid and top-menu layout.
- Theme CSS references standard OutSystems UI and widget classes including `table`, `list-item`, `card`, `section-expandable`, `dropdown`, `btn`, `form-control`, `pagination`, `tabs`, `wizard`, `tooltip`, `notification`, and `upload`.
- Custom classes include `response-container`, `comments_textarea`, `btn_sample`, `btn-bluelogin`, `input_password`, `label_pw`, and `menu_text`.
- Theme CSS proves styling support and class names in the app theme. It does not prove each class is used on every screen.

## Inferred UI Archetypes

Use these archetypes as comparison material, not as exact screen recipes.

Request/response sample screen:
```text
Producers:
- Existing connector/library dependency.
- Server Action wrapping one connector call, with text inputs such as Txt_Index, Txt_Request, Txt_Id, or Txt_Alias.
- Output text for response, error message, and success flag.

Screen:
- Inputs or text areas for index/request/id values.
- Button that calls the wrapper action.
- Response area that displays raw JSON or formatted JSON.
- Review note: exact widget tree and event names were not exposed by MCP context tools.
```

Index management screen:
```text
Producers:
- ListExistingIndexes or equivalent Server Action.
- Create/Delete/Alias Server Actions before consumer buttons.

Screen:
- Prefix/index input.
- Table or list for index results.
- Buttons for create, delete, set alias, or remove alias.
- Feedback message area for success/error outputs.
```

Query example screen:
```text
Producers:
- Static Entity QueryLists with Label, Order, Is_Active, Screen, and Code.
- Query action such as GetObjectByQuery or a feature-specific wrapper action.

Screen:
- Dropdown, list, or side navigation for query examples.
- Text area showing the DSL request.
- Run button.
- Response panel.
```

Migration dashboard:
```text
Producers:
- ESMigrationRun, ESMigrationBucket, ESMigrationFailure, ESMigrationMetric entities.
- Status static entities for run and bucket state.
- PrepareNewMigrationRun and dispatch/process actions.

Screen:
- Form inputs for TargetIndexName, AliasName, BucketSize, BulkMaxRecords, queue limits, and migration record limits.
- Action buttons for prepare/start/dispatch/process.
- Tables or lists for runs, buckets, failures, and metrics.
- Status and progress displays bound to run/bucket counts and status labels.
```

## How To Use This For Mentor Studio Prompt Improvement

1. Keep official docs as the authority layer.
2. Use real-app evidence to choose realistic producer-first order:
   dependencies, data/structure producers, logic producers, reusable UI producers, screen consumers, event wiring.
3. Generate pseudocode from the observed producer graph first, then mark UI details as inferred when only screens/actions/themes are visible.
4. Compare the inferred pseudocode with the skill output:
   - missing producers before consumers
   - missing dependency inventory
   - missing response/error handling
   - unrealistic action or parameter names
   - overclaiming exact widgets, bindings, or events
5. Promote a new curated recipe only after separate evidence justifies it, such as repeated use, Mentor failure, tricky bindings/events, or special compatibility guidance.

## Recipe-Candidate Triage

Real-app evidence can nominate a curated recipe candidate, but it does not promote one by itself.

Nominate a candidate when one or more of these are true:

- repeated use across screens or apps
- Mentor Studio failure or repeated manual correction
- tricky bindings or events
- dependency-sensitive setup
- compatibility guidance that would prevent a wrong UI framework choice
- official docs support the exact widget, pattern, property, event, or dependency behavior

Do not promote a candidate unless the maintenance change adds or updates:

- a curated recipe or fixture
- tests that fail before the recipe change and pass after it
- evidence labels that separate official facts from observed facts
- handoff notes for Claude review when shared skill behavior changes

If the candidate needs exact screen layout, exact bindings, exact local variables, exact event order, or exact widget ids, collect extra evidence before promotion.

## Extra Evidence Trigger

Current MCP evidence is enough for producer-first pseudocode comparison and recipe-candidate triage.

Ask Paulo for screenshots, Studio inspection, export, or approval for deeper read-only inspection when the output requires:

- exact widget tree
- exact widget names or ids
- exact local variables
- exact screen aggregates or data actions
- exact property bindings
- exact event handler call order
- exact visual layout
- curated paste-ready recipe promotion

Until that evidence exists, keep the output as inferred guidance and label it `Course/example-backed`.

## Missing Knowledge

MCP context tools did not expose a full per-screen widget tree for this app. Missing facts include:

- exact widgets and nesting per screen
- widget names and ids
- local variables
- exact screen aggregates and data actions
- exact screen event handlers and call order
- exact widget property bindings
- exact CSS classes assigned to each widget
- runtime screenshots and visual layout

Do not fill these gaps from memory. Ask for a screenshot, Studio export, or explicit approval for a deeper read-only inspection path when the prompt requires exact screen structure.
