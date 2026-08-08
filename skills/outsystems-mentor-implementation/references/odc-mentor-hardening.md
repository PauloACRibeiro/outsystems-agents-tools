# ODC Mentor Hardening

Use this guide before generating ODC Studio or Mentor Studio output that includes SQL, data writes, JSON parsing, status or enum values, dependency-sensitive paste blocks, or any pattern known to be fragile in Mentor Studio.

This guide captures real corrections from the Recording Music Elasticsearch Bulk PoC and turns them into reusable generation rules. Apply these rules to future output. Do not silently rewrite historical plans unless the user explicitly asks for plan reconciliation.

## Evidence Classes

- **Real PoC correction**: learned from a successful Mentor Studio correction during the Recording Music Elasticsearch Bulk PoC.
- **Official SQL syntax**: supported by OutSystems SQL documentation or current `OutSystems/docs-odc` source.
- **Existing skill rule**: already present in `outsystems-mentor-implementation` and consolidated here.
- **Ask-required gap**: depends on the active ODC model or naming, so the skill must ask or emit an explicit substitution note.

## Entry Shape

Each hardening entry uses this shape:

```text
Failure pattern
Preferred pattern
Why
When to ask
Evidence
```

## TrueChange Pre-Mortem Checklist

Before emitting paste-ready Mentor Studio prompts for fragile areas, run this
short pre-mortem and move any unresolved item to `Unknowns And Fallback
Behavior`.

- Check for missing Button `OnClick`. Every Button must navigate or call a
  screen action; create a named action first when no action exists.
- Check for invalid widget reparenting. Use create-delete-repoint patterns
  rather than unsupported move-style instructions.
- Check JSON Deserialize runtime data access. Reference the runtime Data object,
  such as `DeserializeSomething.Data.Field`, instead of the structure name.
- Check CRUD wrapper output assumptions. Name the exact entity action or wrapper
  output only when the active model evidence exposes it.
- Check each static entity or status identifier. Bind to the active model value
  instead of hardcoding text status names.
- Check manual dependency setup. Do not ask Mentor to install dependencies or
  mutate dependency references implicitly.
- Check data-bound widget producer order. Create or verify the source Aggregate,
  Data Action, list variable, or resource producer before wiring the consumer
  widget.
- Check screen navigation target order. Create destination screens or use a
  minimal shell before wiring navigation to them.
- Check `Unknowns And Fallback Behavior`. Any unresolved pre-mortem item must
  stay blocked or become an explicit substitution note there.

If a pre-mortem item cannot be verified, keep the prompt blocked or include a
clear substitution note. Do not convert a pre-mortem gap into confident Studio
structure.

For REST, Data Grid, timer, External Logic, and consumed integration work, copy
the protected contract checklist from `live-target-evidence-matrix.md` into the
prompt. Mentor should preserve those surfaces and report unrelated mutations as
a blocker.

## Forbidden Mentor Model-Introspection Patterns

Use this as the Forbidden Mentor model-introspection patterns rule for prompts
that need exact Studio element proof.

Unsupported model traversal and guessed node properties can make Mentor loop,
invent target evidence, or report contradictory completion signals. Do not ask
Mentor to rely on these patterns for proof or edits:

- `AllDescendants(...)` traversal for exact Studio elements.
- `IActionNode.Name`.
- `IFlowNode.Name`.
- unsupported node-name inspection or target property access.
- Broad traversal that assumes every screen/action node exposes the same
  property set.
- Speculative inspection code that treats missing properties as proof of
  absence.

Preferred fallback:

```text
If the exact node cannot be identified through supported context, visible
Studio proof, or a narrow Mentor-supported query:
stop with no change
report the missing evidence
do not speculate
do not create replacement elements just to make the prompt succeed
```

When this issue appears in a live run, cancel or stop the run before publish
unless the run reaches clean terminal evidence and proves no unrelated mutation.

## Split Proof/Edit Retry Pattern

For fragile targets, use dependent steps instead of one large Mentor prompt.

Use this pattern:

1. Fresh read-only target proof.
2. Proof-only Mentor prompt or Studio visual proof. The proof step must not
   edit, save, publish, trigger timers, execute external calls, or mutate data.
3. Second narrow Mentor edit only if proof cleanly identifies the target and
   protected surfaces; this is the second narrow Mentor edit gate.
4. Publish only if explicitly approved and required, and only if the edit run
   has `attempted_change=true`, `change_applied=true`, validation 0 errors, no
   contradictory no-change/tooling caveat, and no unrelated mutations.
5. Post-publish proof before terminal success.

For dependent construction, prove each dependency before the next step when
Mentor needs the earlier element to exist. Example shape:

```text
Step A: create or confirm the screen/container.
Step B: after proof, create or repair entities/statics/references.
Step C: after proof, add the action or button wiring.
```

If a proof-only run reports `attempted_change=true` or
`change_applied=true`, treat that as contradictory completion evidence and stop
before edit or publish.

## Advanced Edit Stop Conditions

For complex refactor, Data Grid wiring, workflow/event/async, and
external-library lifecycle requests, do not perform speculative edits. Use
proof-only inspection first and stop with no change when the exact target,
blast radius, dependency boundary, rollback posture, or protected contract
cannot be proven.

Stop before Mentor edit when:

- the request would change a shared producer without a selected compatibility
  strategy;
- Data Grid wiring lacks a proven save, validation, or persistence boundary;
- workflow/event/async behavior would require triggering background work or
  mutating state without approval;
- external-library lifecycle work would require upload, publish, source
  download, or binary replacement without explicit current approval;
- MCP/context cannot expose the hidden edit point and no bounded Studio visual
  proof is available.

## Spec-First Scaffold Reliability

### Preserve RBAC Scope Exactly As Specified

**Failure pattern**

Mentor-generated prompts default one or more screens to anonymous/public or alter role mappings not explicitly defined in the spec:

```text
Create Screen Login, Home, Dashboard ...
Use default anonymous access while the spec says only Admin/Approver roles can access AdminDashboard.
```

**Preferred pattern**

When spec text defines role-per-screen or role-per-action scope, treat those mappings as exact contracts:

```text
For each screen and entry action:
set role access exactly as specified
do not assign anonymous/public unless explicitly requested
mark any missing role mapping as a block and ask for explicit confirmation before proceeding
```

**Why**

Role drift at this boundary is a high-replay failure mode because it changes runtime access behavior and can invalidate downstream validation assumptions.

**When to ask**

If any screen, block, or action has no explicit role mapping, pause and ask the user before generating prompts.

**Evidence**

Spec-driven build hardening patterns and post-run review notes from greenfield scaffold runs.

### Force ODC UI Terms And Layout Contracts

**Failure pattern**

Mentor prompts reference legacy concepts or unsupported bare-layout patterns:

```text
Generate screens with plain HTML containers only.
Use "Service Studio" or "eSpace" wording in generated implementation guidance.
```

**Preferred pattern**

Emit output with ODC-first vocabulary and UI constraints:

```text
Use OutSystems UI structures for screens and standard blocks.
Do not emit bare HTML-only layouts where native UI patterns are expected.
Do not reference legacy O11-only terms as current ODC implementation guidance.
```

**Why**

Legacy terms and unsupported layouts increase non-determinism and raise the chance of rework in first-pass scaffolds.

**When to ask**

If the user explicitly requests nonstandard legacy behavior, confirm scope before generating and document any risk as an unresolved item.

**Evidence**

Observed failures captured in spec-first bootstrap guidance and recurring Mentor output drift.

### Never Trigger Forbidden Dependency Mutations In Generated Mentor Prompts

**Failure pattern**

Prompt asks Mentor to apply dependency-library mutations directly, especially model-layer dependency APIs:

```text
Add missing dependency automatically.
Use AddDependency calls to fix missing library references.
```

**Preferred pattern**

Keep dependency installation explicit and manual before this generated pass:

```text
If a dependency is required:
ask user to install it manually in Studio first
do not include dependency mutation calls in the generation prompt
```

**Why**

Dependency mutation via generated prompts is brittle and can create avoidable retries, especially in new app scaffolding workflows.

**When to ask**

When required dependencies are missing from the model, ask for confirmation after listing required manual preconditions.

**Evidence**

Spec-driven build anti-failure guardrails and verified Mentor retries tied to dependency mutation assumptions.

### Enforce Out-of-Scope Contract as a Blocking Boundary

**Failure pattern**

Mentor gets asked to do things the user explicitly excluded:

```text
Build a reporting dashboard and publish it immediately.
The spec said:
"No public REST endpoints and no Admin UI for audit logs".
```

**Preferred pattern**

Keep explicit exclusions as hard requirements and mark them as blockers when they conflict with requested output:

```text
If section says out of scope includes <feature>, do not generate that feature.
Before proceeding, ask for explicit sign-off if you need to include it anyway.
If uncertain, pause and ask for the spec delta.
```

**Why**

Out-of-scope drift causes unplanned work and invalidates follow-up review assumptions.

**When to ask**

Any request that attempts to add a blocked feature or conflicts with an explicit exclusion should be blocked until explicit user confirmation.

**Evidence**

Spec-driven build interview pattern and post-run review notes from bootstrap flows.

### Preserve Exact Attribute Types From Spec And Source

**Failure pattern**

Replacing specified attribute types to something more convenient in generated output:

```text
Spec says Long Integer, generated as Integer.
Spec says Email, generated as Text.
```

**Preferred pattern**

Use the exact type contract unless a typed migration is requested up front:

```text
Use exact type names from the validated spec or existing model.
If type mismatch is required, call it out and ask before generating.
```

**Why**

Type drift in attributes and identifiers can create compile or data migration gaps in first-pass scaffolds.

**When to ask**

When any model-specific or spec-reported type is ambiguous, pause and ask for explicit confirmation before generating.

**Evidence**

`outsystems-spec-driven-build` guardrails and existing OMI data-model guidance for typed constructs.

### Keep Seed Data As Explicit Setup, Not Implicit Background Mutation

**Failure pattern**

Mentor is asked to build seeded records or bootstrap data implicitly in the same pass without explicit setup ownership:

```text
Create seed products/orders while building the app shell, without declaring setup ownership.
```

**Preferred pattern**

If seed/preset data is required, treat it as an explicit post-build setup requirement and route through a dedicated setup action:

```text
Create and document an explicit BootstrapData action (idempotent) or explicit manual setup instructions.
Do not assume seed data exists unless scope explicitly allows it.
```

**Why**

Seed behavior that is not explicit is the fastest way to non-replayable first-pass scaffolds.

**When to ask**

If data seeding is needed and there is no explicit owner/entry-point yet, ask before generating and document as a manual setup prerequisite.

**Evidence**

Spec-driven build anti-failure guidance and visitlog/podcast scaffold follow-up patterns.

### Avoid Reserved Generic Theme Class Names In Generated Layout CSS

**Failure pattern**

Prompt output asks Mentor to create custom layout classes using generic names that collide with OutSystems UI or common layout theme rules:

```text
Create containers with CSS classes main-content, sidebar, header, content, and footer.
Use the class sidebar for the generated side navigation container.
```

**Preferred pattern**

Namespace custom layout classes by app, screen, block, or domain intent:

```text
Use app-prefixed layout classes such as banking-sidebar, requestpulse-header, or dashboard-main-content.
Avoid unprefixed custom classes named main-content, sidebar, header, content, or footer.
When using OutSystems UI layout patterns, prefer the pattern's own structure and only add custom classes for app-specific styling.
```

**Why**

Generic layout class names are easy for Mentor to generate but hard to reason about after theme CSS applies. Prefixing keeps scaffold and existing-app prompts from accidentally colliding with OutSystems UI layout styles or another app-specific style family.

**When to ask**

If the user provides an existing CSS naming convention or shared theme library, ask whether to follow that convention before generating new custom class names.

**Evidence**

Tested `outsystems-spec-driven-build` prompt-builder guardrail for reserved theme class names; adapted here as OMI UI hardening without copying greenfield-only scaffold mechanics.

### Require Explicit Producer Bindings For Data-Bound Widgets

**Failure pattern**

Mentor creates a data-bound widget or pattern without a concrete producer or binding source. `TableRecords` is the tested scaffold failure, but the same class of issue applies to any widget that renders from source-like data:

```text
Create a static demo table for recent requests.
Leave Source empty and place row-looking content inside the table structure.
Create a List, Dropdown Search, Carousel, Gallery, or Data Grid without naming its Source, OptionsList, placeholder List, Record List, URL/ImageURL, selected value, or equivalent producer binding.
```

**Preferred pattern**

Every generated data-bound widget must name its producer before consumer UI is emitted:

```text
For collection widgets and patterns:
bind Source, OptionsList, placeholder List, Record List, or equivalent input to an Aggregate, Data Action output, static entity list, mapped option list, or verified List variable.

For value-bound widgets:
bind Variable, SelectedValue, SelectedOptions, URL/ImageURL, or equivalent input to a verified local variable, input parameter, Aggregate field, Data Action output, or mapped structure field.

For static demo tables:
create an explicit Local Variable typed as List<EntityOrStructure>
populate it in On Initialize with one ListAppend per demo row
bind the TableRecords Source to that list.

For persistent seed data:
use an explicit idempotent BootstrapData action or manual setup gate before the table prompt.
```

Never leave source-like inputs unset: `TableRecords.Source`, `List.Source`, dropdown `OptionsList`, carousel/gallery placeholder List or item producer, Data Grid source/data action wiring, media `URL`/`ImageURL`, or selected/value variables. If no valid producer exists yet, block the consumer prompt and ask whether to create a producer first or emit a non-data-bound placeholder.

**Why**

Widget shape can look structurally complete while rendering no records, no options, no images, or no selected value at runtime when its source-like binding is empty. Producer-first binding keeps UI prompts deterministic and reviewable.

**When to ask**

Ask when the widget source, list type, aggregate, data action, mapped option structure, media URL producer, selected-value variable, or seed owner is not known before the data-bound widget is generated.

**Evidence**

Tested `outsystems-spec-driven-build` prompt-builder guardrail for `TableRecords` source binding, generalized here to OMI producer-first UI prompt rules for data-bound widgets and bootstrap setup guidance.

## ODC SQL Generation

### Prefer Aggregates For Simple Reads

**Failure pattern**

Generating a SQL node for a basic read that can be expressed with an Aggregate:

```text
Create SQL GetActiveProducts just to filter Product.IsActive = True and sort by Name.
```

**Preferred pattern**

Prefer Aggregates for simple reads. Use SQL only when an Aggregate cannot express the query safely, such as a CTE, `RETURNING`, a window function, external-entity SQL syntax, or a tested bulk write/read pattern.

```text
Create Aggregate GetActiveProducts
  Source: Product
  Filter: Product.IsActive = True
  Sort: Product.Name ascending
```

**Why**

Aggregates keep simple reads Studio-native and easier for Mentor to validate. SQL nodes remain appropriate for advanced query shapes, tested bulk operations, and documented SQL-only behavior.

**When to ask**

Ask when the requested query may need SQL-only behavior, when Aggregate support is uncertain, or when performance constraints require a tested SQL shape.

**Evidence**

Existing skill rule and current official Aggregate/SQL guidance.

### Insert Target Columns And Returning

**Failure pattern**

Using qualified entity attributes in the target column list of an `INSERT INTO {Entity}` statement:

```sql
INSERT INTO {ESMigrationBucket}
  (
    {ESMigrationBucket}.[ESMigrationRunId],
    {ESMigrationBucket}.[SequenceNumber],
    {ESMigrationBucket}.[Status]
  )
...
RETURNING {ESMigrationBucket}.[Id] AS BucketId
```

**Preferred pattern**

Use bare target attributes in the insert column list and bare returned attributes in `RETURNING`:

```sql
INSERT INTO {ESMigrationBucket}
  (
    [ESMigrationRunId],
    [SequenceNumber],
    [Status]
  )
SELECT
  @RunId,
  BucketedRows.SequenceNumber,
  @QueuedStatusValue
FROM BucketedRows
RETURNING [Id] AS BucketId
```

**Why**

OutSystems SQL uses `{Entity}` for the target table and `[Attribute]` for attributes. Current ODC SQL difference guidance shows the ODC insert target pattern as `INSERT INTO {Product}([Name])`.

**When to ask**

Ask or emit a substitution note when the status value type is unknown. `@QueuedStatusValue` may be a text value, integer value, or static entity Identifier depending on the model.

**Evidence**

Real PoC correction and official SQL syntax.

### Deterministic First-N Rows

**Failure pattern**

Using a parameterized `LIMIT` inside an `IN` subquery to choose a bounded first-N source set:

```sql
SELECT
  MIN({Allrecordings}.[Id]) AS MinRecordingId,
  MAX({Allrecordings}.[Id]) AS MaxRecordingId,
  COUNT(*) AS TotalRecords
FROM {Allrecordings}
WHERE (@PoCMaxRecords = 0)
   OR ({Allrecordings}.[Id] IN (
        SELECT {Allrecordings}.[Id]
        FROM {Allrecordings}
        ORDER BY {Allrecordings}.[Id]
        LIMIT @PoCMaxRecords
      ))
```

**Preferred pattern**

Rank the source rows once, select the desired rows by `RowNumber`, then aggregate over the selected set:

```sql
WITH NumberedRecordings AS (
  SELECT
    {Allrecordings}.[Id] AS RecordingId,
    ROW_NUMBER() OVER (ORDER BY {Allrecordings}.[Id]) AS RowNumber
  FROM {Allrecordings}
),
SelectedRecordings AS (
  SELECT
    RecordingId
  FROM NumberedRecordings
  WHERE @MigrationMaxRecords = 0
     OR RowNumber <= @MigrationMaxRecords
)
SELECT
  MIN(SelectedRecordings.[RecordingId]) AS MinRecordingId,
  MAX(SelectedRecordings.[RecordingId]) AS MaxRecordingId,
  COUNT(*) AS TotalRecords
FROM SelectedRecordings
```

This bracketed CTE alias style mirrors the Mentor-corrected PoC SQL. For new CTE aliases, preserve the SQL node's tested alias style and ask or run Test Query before normalizing bracketed alias references to generic PostgreSQL dot syntax.

**Why**

This expresses the business rule directly: order records deterministically, assign a row number, keep the first N rows, and aggregate over exactly that set. It also matches the bucket-generation pattern used later in the PoC.

**When to ask**

Ask if the SQL node input parameter name is unclear. Do not rename `@PoCMaxRecords` to `@MigrationMaxRecords`, or the reverse, unless the SQL node input is also named that way.

**Evidence**

Real PoC correction.

### Bucket Sequence Arithmetic

**Failure pattern**

Emitting casts and math that are more complex than the ODC SQL node needs:

```sql
FLOOR(((RowNumber - 1)::numeric / BucketSize))::integer + 1 AS SequenceNumber
```

**Preferred pattern**

Use the simpler integer arithmetic when both values are integer inputs:

```sql
((RowNumber - 1) / BucketSize) + 1 AS SequenceNumber
```

**Why**

ODC SQL supports PostgreSQL syntax for internal entities, but casts such as `::numeric` and `::integer` should be emitted only when needed to fix an actual type mismatch.

**When to ask**

Ask if `RowNumber`, `BucketSize`, or the output structure type is not known. If decimal division is required, state the reason before adding casts.

**Evidence**

Real PoC correction.

### SQL Parameters And Output Structures

**Failure pattern**

Using different names for the same SQL input between the SQL node declaration and the SQL body, or returning aliases that do not match the output structure.

**Preferred pattern**

Choose the SQL node input names first and use them exactly inside the SQL body:

```text
SQL GetRecordingMusicBounds
  Input Parameter: MigrationMaxRecords: Long Integer
  Output Structure: RecordingMusicBounds
```

```sql
WHERE @MigrationMaxRecords = 0
   OR RowNumber <= @MigrationMaxRecords
```

Return aliases in the same order and compatible data types as the output structure:

```sql
SELECT
  MIN(SelectedRecordings.[RecordingId]) AS MinRecordingId,
  MAX(SelectedRecordings.[RecordingId]) AS MaxRecordingId,
  COUNT(*) AS TotalRecords
FROM SelectedRecordings
```

**Why**

OutSystems SQL output structures require matching column order and data types. Mentor Studio is more reliable when the node declaration and SQL body use exact names.

**When to ask**

Ask when the output structure attributes or SQL node input names are not available.

**Evidence**

Official SQL syntax and real PoC correction.

## Entity Action Writes

### Create, Update, And Delete Entity Actions Need Explicit Action Calls

**Failure pattern**

Do not write vague prompts like these, because they hide the actual write operation:

```text
Persist this order.
Save the current product changes.
Remove these stale rows.
```

**Preferred pattern**

Name the exact generated CRUD wrapper or entity action visible in the active ODC model, and state whether the operation creates, updates, upserts, or deletes records. ODC CRUD wrapper accelerators can create these server action wrappers for ODC Studio entities:

- `<Entity>Create`
- `<Entity>CreateOrUpdate`
- `<Entity>Update`
- `<Entity>Delete`

For Create or Update:

```text
Run Server Action ProductCreateOrUpdate
  Product: EditedProduct
```

For list writes, name the Source List explicitly:

```text
For Each ImportedProducts
  Run Server Action ProductCreateOrUpdate
    Product: ImportedProducts.Current
```

For Delete:

```text
Run Server Action ProductDelete
  ProductId: ProductIdToDelete
```

State the delete scope before emitting the prompt. Prefer soft delete when the model has an `Is_Active`, `IsDeleted`, or status field intended for lifecycle state.

**Why**

ODC write prompts are safer when Mentor sees the concrete action and record shape. Vague "persist this" wording can produce duplicate creates, missing update identifiers, unbounded deletes, or writes that bypass wrapper validation.

**When to ask**

Ask when the active action name, input record shape, Identifier value, delete scope, or soft-delete convention is not visible. Do not infer CRUD wrapper names from the entity label if the model might have custom wrapper actions.

**Evidence**

Current official CRUD wrapper guidance and database event guidance. Database events can be configured for Create, Update, or Delete entity actions and run after successful commit, so writes that trigger event behavior must call out commit visibility explicitly.

## Status And Static-Entity Values

### Do Not Assume Status Is Text

**Failure pattern**

Emitting text literals for status fields without confirming the attribute type:

```sql
'Queued'
```

or:

```text
ESMigrationBucket.Status = "Queued"
```

**Preferred pattern**

Determine the ODC attribute type first:

- If `Status` is `Text`, use ODC expression text such as `"Queued"` and SQL text such as `'Queued'`.
- If `Status` is `Integer`, use the agreed numeric value or pass it as a SQL input parameter.
- If `Status` is a Static Entity Identifier, use the static entity Identifier in ODC expressions and pass the Identifier value into SQL when the SQL node inserts it.
- If `Status` is an Entity Identifier, use the referenced entity Identifier value.

When the type is unknown, emit a substitution note:

```text
Use `@QueuedStatusValue` as the SQL input value for the queued status. If `Status` is Text, pass "Queued". If `Status` is a static entity Identifier, pass the queued static entity Identifier.
```

**Why**

The PoC plan originally modeled statuses as text, but Mentor Studio corrected one SQL insert to use a numeric value. That means the active ODC model can differ from the plan text.

**When to ask**

Ask before hard-coding a status value when the data model is not visible or when the plan and current Studio model disagree.

**Evidence**

Real PoC correction and ask-required gap.

## JSON Deserialize

### Read Parsed Data Through The Deserialize Runtime Object

**Failure pattern**

Reading fields directly from the structure type after `JSON Deserialize`:

```text
JSON Deserialize
  Input = ResponseText
  Output = ElasticBulkResponse

Assign
  Result.Errors = ElasticBulkResponse.errors

For Each ElasticBulkResponse.items
```

**Preferred pattern**

Set `Output` to the structure name, then read parsed data through the generated deserialize runtime object:

```text
JSON Deserialize
  Input = ResponseText
  Output = ElasticBulkResponse

Assign
  Result.Errors = DeserializeElasticBulkResponse.Data.errors
  Result.TookMs = DeserializeElasticBulkResponse.Data.took

For Each DeserializeElasticBulkResponse.Data.items
  Item = DeserializeElasticBulkResponse.Data.items.Current
```

**Why**

The usable runtime payload after deserialization is the generated `Deserialize<StructureName>` object, with parsed values under `.Data`.

**When to ask**

Ask if the structure name or generated deserialize object name is ambiguous. Do not invent a different runtime object naming convention silently.

**Evidence**

Existing skill rule.

## Mentor-Paste Reliability

### Emit Producers Before Consumers

**Failure pattern**

Emitting a consumer action, screen, event handler, or SQL block before the entities, structures, site properties, REST methods, events, timers, or producer actions it references.

**Preferred pattern**

Use dependency-safe order:

1. Entities and structures
2. Site properties
3. External contracts
4. Events and timers
5. Producer server actions
6. Consumer server actions
7. Screens, blocks, and client actions

**Why**

Mentor Studio is more reliable when every referenced producer already exists or is clearly marked as existing.

**When to ask**

Ask when dependencies are cyclic or when a referenced existing item cannot be named exactly.

**Evidence**

Existing skill rule.

### Keep Blocks Atomic

**Failure pattern**

Emitting a large paste block that mixes data model creation, SQL, REST configuration, server actions, events, and UI wiring in a single request.

**Preferred pattern**

Split large work into atomic blocks with exact target names:

```text
Create structure `ElasticBulkResponse`.
Create SQL node `GetRecordingMusicBounds`.
Create Server Action `CreateMigrationRun`.
Wire Timer `DispatchMigrationBuckets`.
```

**Why**

Smaller blocks make Mentor Studio corrections easier to isolate and reduce dependency confusion.

**When to ask**

Ask when the user wants a single large paste block but the block crosses many dependency boundaries.

**Evidence**

Existing skill rule.

## Screen-Targeting Preflight

### Do Not Infer Screen Role Assignments From MCP Screen Context

**Failure pattern**

Prompt or review output cross-products app roles with screen names from
`context_screens` and claims exact Accessible by role assignments.

**Preferred pattern**

Use `context_screens` only for facts it exposes, such as screen identity,
flow, and `isPublic` when present. `context_screens` does not expose per-screen
role assignments. Do not infer Accessible by roles, and do not cross-product
roles and screens. If exact screen authorization is required, ask for a live
Studio check or another verified source.

**Why**

Per-screen access claims affect security and validation scope. Inventing them
can make a Mentor prompt change access behavior that the user did not approve.

**When to ask**

Ask when output depends on exact role-per-screen assignments and no verified
source exposes them.

**Evidence**

The upstream skills catalog's conventions document records the current MCP limitation.
For broader tenant context and payload guardrails, see
`references/tenant-context-guardrails.md`.

### Verify Flow Name Before Writing Prompt

**Failure pattern**

Writing a prompt that names a screen with an assumed flow (e.g., "Login screen in MainFlow") without verifying the actual flow the screen belongs to.

**Preferred pattern**

Before writing any Mentor Studio prompt that targets a screen by flow + screen name, call `context_screens` on the app and confirm the exact flow name from the result. Never assume "MainFlow".

```text
# Before writing:
context_screens(app_key=...) → find "Login" → actual flow = "Common"
# Prompt uses:
"In the Login screen in Common flow, ..."
```

Common screens in ODC system-generated apps that are NOT in MainFlow:
- `Login` → Common flow
- `ChangePassword` → Common flow
- `RecoverPasswordRequest` → Common flow

**When to ask**

When `context_screens` is unavailable or returns no match, ask the user for the exact flow name before writing the prompt.

If the lookup returns `context_screens=[]` or zero matching rows, the screen name is unverifiable. Use `Evidence Status: Unverified gap`, add `Unknowns And Fallback Behavior`, and ask the user whether to proceed with a new-screen assumption before any prompt continues.

Do not emit a confident existing-screen Mentor Studio prompt from a zero-row lookup. If the user confirms a new-screen path, include a substitution note such as:

```text
Screen lookup returned context_screens=[].
Replace [ScreenName] with the confirmed existing screen name, or confirm this prompt should create [ScreenName] as a new Screen.
```

**Evidence**

Real session correction: Login screen targeted as MainFlow — Mentor self-corrected after calling `getScreenNames`.

---

### Verify Existing Variable and Action Names Before Prompt

**Failure pattern**

Using assumed names for local variables and screen actions in a prompt (`Username`, `OnLogin`) when the actual ODC model may use different names (`UserEmail`, `LoginOnClick`).

**Preferred pattern**

Before writing a prompt that references existing screen local variables or screen actions by name, call `context_screens` (or use Mentor's `getScreen` in a prior run) to confirm exact names. Do not infer names from UI labels or generic conventions.

```text
# Wrong (assumed):
"... input bound to Username local variable"
"... wired to OnLogin client action"

# Right (verified):
"... input bound to UserEmail local variable"
"... wired to LoginOnClick client action"
```

**When to ask**

When MCP tools are unavailable, emit explicit substitution notes:

```text
Replace UserEmail with the actual local variable name for email in the Login screen.
Replace LoginOnClick with the actual client action name wired to the log in button.
```

**Evidence**

Real session correction: Block 2 originally used wrong variable and action names caught by pre-prompt screen inspection.

---

## Multi-Block Cross-Block Consistency

### Block N Must Not Reference Deleted Widgets as Existing

**Failure pattern**

Block N-1 clears or replaces all screen widgets; Block N then says "keep the existing Form widget" or "use the existing Button" — the referenced element no longer exists.

**Preferred pattern**

When planning multi-block Mentor sessions, track each block's destructive scope. If Block N-1 empties or replaces the screen's widget tree, Block N must create everything from scratch, not reference existing widgets.

```text
# Block 1: "replace the current layout with LayoutBlank" → all prior widgets gone
# Block 2 must say: "add a Form widget named LoginForm" NOT "keep the existing Form"
```

Before writing Block 2+, explicitly check: "Did any prior block delete or replace the target container or its children?"

**When to ask**

When scope of prior blocks is unclear, ask whether the prior block left existing widgets intact before referencing them.

**Evidence**

Real session: Block 2 said "keep the existing Form widget" after Block 1 had deleted all screen widgets. Mentor created a new Form gracefully, but the prompt instruction was wrong.

---

## Form Widget Deletion

### Deleting a Form Widget Breaks FormName.Valid References

**Failure pattern**

A Mentor prompt deletes a Form widget (or clears all screen widgets containing a Form). Any screen client action that references `FormName.Valid` in an If node condition breaks silently — the condition becomes a dangling reference, typically set to literal `True`.

**Preferred pattern**

Whenever a block deletes or recreates a Form widget, always include a follow-up step (same block or next block) that:

1. Restores `FormName.Valid` in all If nodes that reference it.
2. Use the pattern: find the If node with a condition containing `"True "` (the dangling literal), then restore with `ifNode.SetCondition("LoginForm.Valid")`.

Template to include in the prompt or as a separate Block:

```text
After recreating the Form widget named LoginForm, in the LoginOnClick screen action,
find the If node that validates the form before login and restore its condition to
LoginForm.Valid (it may currently be set to True as a placeholder).
```

**When to ask**

Before deleting a Form widget, ask: "Does any screen action reference `FormName.Valid`?" If yes, include the restoration step explicitly.

**Evidence**

Real session: Block 1 deleted all widgets (including the Form). LoginForm.Valid condition in LoginOnClick became dangling. Block 2 included explicit restoration.

---

## Mentor ApplyModelApiCode Patterns

### IfNode Condition String Matching

**Failure pattern**

Matching an IfNode by exact condition string equality:

```csharp
// Fails — condition ToString() includes type suffix
n.Condition?.ToString() == "True"

// Also fails — label can be empty string but FirstOrDefault still misses
n.Label == "" && n.Condition?.ToString() == "True"
```

**Preferred pattern**

Use `.StartsWith()` because `n.Condition.ToString()` for a literal `True` condition returns `"True [Condition[ServiceStudio.Expressions.AbstractExpression]]"`:

```csharp
var ifNode = action.Nodes.OfType<IIfNode>()
    .FirstOrDefault(n =>
        (n.Condition?.ToString() ?? "").StartsWith("True "));

if (ifNode != null) {
    ifNode.SetCondition("LoginForm.Valid");
}
```

**When to ask**

Not applicable — this is a deterministic API behavior, not model-dependent.

**Evidence**

Real session: Mentor tried 4 approaches before `StartsWith("True ")` succeeded. Pattern documented for future Mentor Studio code generation.

---

## ODC Studio Acceptance Checklist

Use this checklist when a generated block will be pasted into a real ODC app. Local Python tests do not execute ODC code. They only verify that the skill keeps generating the safer patterns documented above.

1. Paste the corrected SQL into the target ODC SQL node.
2. Confirm SQL input parameters exactly match the names used in the SQL body.
3. Confirm SQL output structure names, order, and data types match the returned aliases.
4. Run the SQL node's SQL Test Query with a small safe parameter set.
5. Bind each status value to the active model value, not to an assumed text literal.
6. Publish the app.
7. Run a small PoC migration, such as 10 records and a small bucket size.
8. Confirm created buckets have expected sequence numbers, ranges, record counts, and status values.
9. Process one bucket and confirm bulk response parsing reads through `DeserializeElasticBulkResponse.Data`.
10. Confirm failure rows record status code, error type, and error reason when Elasticsearch returns an item error.

When reporting validation, use one of these exact outcomes:

- `Completed in ODC Studio` with the environment name, date, and observed result.
- `Not run locally - requires ODC Studio and the active app model`.

## UI Layout And Styling Fidelity

### btn-primary Background Is Overridden By OutSystems UI Theme — And `!important` Is Stripped

**Failure pattern**

Combining `btn btn-primary` style class with an Extended Properties `style` attribute that sets `background`, even with `!important`:

```text
Style Classes: "btn btn-primary"
Extended Properties: style = "height:47px; background:#1068eb !important; ..."
```

ODC's runtime strips `!important` from Extended Properties `style` attribute values. The theme's `.btn-primary` stylesheet rule therefore wins regardless. The button renders teal/slate — the OutSystems UI default primary color — not the custom hex.

**Preferred pattern**

Drop `btn btn-primary` entirely. Apply all button styling through Extended Properties:

```text
Style Classes: (empty)
Extended Properties: style = "height:47px; border-radius:10px; font-size:15px; font-weight:600; width:100%; color:#fff; background:#1068eb; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 6px 18px rgba(16,104,235,.40);"
```

This loses OutSystems UI hover/focus states. Accept that tradeoff when design fidelity is the goal. Do NOT use `!important` as a workaround — it is silently stripped by ODC.

**When to ask**

Ask whether to preserve OutSystems UI hover/focus behavior. If fidelity to a prototype is the priority, always drop the class.

**Evidence**

Real session (two runs): First run — button teal due to theme specificity. Second run — applied `background:#1068eb !important` via Extended Properties, confirmed applied by Mentor, button still teal. Conclusion: ODC strips `!important` from Extended Properties style attribute values.

---

### Use `height:100vh` Not `height:100%` For Top-Level Split-Panel Containers

**Failure pattern**

Using `height:100%` on a top-level Container (BrandPanel, FormPanel) that is a direct flex child of SplitWrapper:

```text
BrandPanel Extended Properties:
  style = "flex:0 0 47%; height:100%; display:flex; flex-direction:column; justify-content:space-between; ..."
```

ODC's LayoutBlank inserts wrapper divs between the screen root and any widget-tree Containers. The parent-height chain breaks before reaching SplitWrapper, so `height:100%` on BrandPanel collapses to content height (not viewport height). `justify-content:space-between` then has no space to distribute — children cluster at the top or bottom.

Confirmed: `!important` is also stripped (see btn-primary entry above) — do not use `!important` to force heights either.

**Preferred pattern**

Use `height:100vh` directly on any top-level split-panel Container. This breaks free of the parent chain:

```text
BrandPanel Extended Properties:
  style = "flex:0 0 47%; height:100vh; display:flex; flex-direction:column; justify-content:space-between; ..."

FormPanel Extended Properties:
  style = "flex:1; min-height:100vh; display:flex; align-items:center; justify-content:center; ..."
```

Use `min-height:100vh` on form panels (not `height:100vh`) so content can overflow if the form grows taller than viewport.

**When to ask**

Not needed — always use `height:100vh` (not `height:100%`) on any Container that is meant to fill the full viewport height inside ODC's LayoutBlank.

**Evidence**

Real session (two runs): First run — `height:100%` omitted, BrandPanel collapsed. Second run — `height:100%` added, BrandPanel still collapsed (ODC LayoutBlank wrapper chain breaks the resolution). Fix is `height:100vh` directly.

---

### Decorative Absolute-Positioned Overlay (Dot Grid, Gradient Mask)

**Failure pattern**

Omitting decorative full-bleed background elements (dot grids, radial gradient masks, noise overlays) because they have no semantic content.

**Preferred pattern**

Use a dedicated Container inside the target Container, positioned absolutely to fill it:

```text
Container named GridOverlay:
  Extended Properties:
    style = "position:absolute; inset:0; pointer-events:none; background-image:radial-gradient(rgba(255,255,255,.16) 1px, transparent 1px); background-size:22px 22px; -webkit-mask-image:radial-gradient(130% 90% at 28% 16%, #000, transparent 72%); mask-image:radial-gradient(130% 90% at 28% 16%, #000, transparent 72%);"
```

The parent Container must have `position:relative` (or it is already positioned via `position:absolute` itself).

Place GridOverlay as the FIRST child of the parent so it renders behind all other content.

**When to ask**

When the design uses a dot grid, noise texture, or gradient overlay, ask if it should be included or omitted for simplicity.

**Evidence**

Real session: `essplit-grid` dot pattern from Claude Design prototype was completely absent in Mentor output because it was not included in Block 1 prompt.

---

### Icon Badge Container Recipe

**Failure pattern**

Using a Text widget with a Unicode character as an icon approximation inside a rounded-square badge:

```text
Container LogoMark (32x32 rounded square)
  Text widget, value "⌕"
```

Unicode characters for icons are font-dependent and render inconsistently across browsers and ODC's runtime font stack. U+2315 (⌕) renders as "p" or a fallback box in many contexts.

**Preferred pattern**

Use an OutSystems UI Icon widget from the icon library inside the badge Container:

```text
Container named FeatIcon (32×32 rounded square):
  Extended Properties: style = "width:32px; height:32px; border-radius:9px; background:rgba(255,255,255,.15); display:flex; align-items:center; justify-content:center; flex-shrink:0;"
  Icon widget from OutSystems UI (e.g. "search", "flash", "copy") — set Size to Small or set font-size via Extended Properties
```

If OutSystems UI icons are not available in the app, use an Expression widget with an SVG string as a fallback, and mark it as a manual review item.

**When to ask**

Ask which OutSystems UI icon name maps to each design icon when the prototype uses custom SVG paths. If no mapping exists, omit the icon and include a review note.

**Evidence**

Real session: Logo mark "⌕" rendered as wrong glyph. Feature row icons were omitted entirely from the prompt.

---

### Password Eye Toggle Recipe

**Failure pattern**

Styling a password Input widget without including the reveal Button that toggles visibility.

**Preferred pattern**

Create a relative-positioned wrapper Container, then place the Input and a Button inside it:

```text
Container named PasswordWrap:
  Extended Properties: style = "position:relative; display:flex; align-items:center;"

  Inside PasswordWrap:
    Input widget Input_Password (type=Password, fill width)

    Button named Btn_RevealPassword:
      Style Classes: (empty — no OutSystems UI class)
      Extended Properties: style = "position:absolute; right:7px; width:32px; height:32px; background:transparent; border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; border-radius:8px; color:#8b949e;"
      OnClick → Client Action that toggles a Boolean local variable ShowPassword
        and sets Input_Password InputType to "Text" when ShowPassword=True, "Password" when False
```

Note: toggling InputType dynamically via a Client Action requires the Input widget to be redrawn. Verify this works in ODC Studio before relying on it.

**When to ask**

Ask whether eye toggle is required when the design includes a reveal icon on password fields.

**Evidence**

Real session: eye toggle was present in the Claude Design prototype but completely absent from the Mentor prompt and generated output.

---

## Button Widget Rules

### Button OnClick Is Required — Never Leave It Empty

**Failure pattern**

Prompt creates a Button widget and says "leave OnClick empty for now":

```text
Add a Button named Btn_RevealPwd...
Leave Btn_RevealPwd OnClick event empty for now.
```

ODC TrueChange error fires immediately: `Required Property Value: On Click must be set.` The app will not publish until every Button has an OnClick destination.

**Preferred pattern**

Every Button prompt must include an OnClick wiring step. If the real logic doesn't exist yet, create an empty placeholder screen action in the same block:

```text
Create a screen action named TogglePassword on the Login screen (Start node → End node, no logic).
Add a Button named Btn_RevealPwd...
  OnClick → TogglePassword
```

Never say "leave OnClick empty". Instead say: "Create a placeholder screen action named X and wire it to Btn_RevealPwd's OnClick."

**Coverage audit obligation**

The mandatory audit category "Interactive widgets" must flag any Button with no OnClick destination as `✗ missing`. Fix it before delivering the prompt.

**When to ask**

When no appropriate existing action exists and the correct action name is unclear, ask the user before inventing a name.

**Evidence**

Real session: `Btn_RevealPwd` prompt said "leave OnClick empty." Mentor self-recovered by creating `TogglePasswordVisibility`, but the prompt was wrong and burned an extra `applyModelApiCode` pass.

---

## Widget Reparenting

### Wrapping An Existing Widget In A New Container Requires Recreation

**Failure pattern**

Prompt says "wrap Input_Password in a new Container named PasswordWrap" as if the ODC API supports reparenting directly:

```text
Wrap Input_Password in PasswordWrap. Keep its existing binding.
```

ODC's `applyModelApiCode` API has no `reparent()` or `MoveToParent()` method. Mentor cannot simply move a widget from one parent Container to another.

**Preferred pattern**

Express the intent as a create-delete-repoint sequence. Mentor must:

1. Create the new Container sibling (e.g., `PasswordWrap` added to `FieldPassword`).
2. Create a new widget with the same name and configuration INSIDE the new Container — re-specify all properties (type, variable binding, placeholder, style) from scratch.
3. Delete the original widget from its old parent.
4. Re-point any `Label.TargetWidget` or other cross-references to the new widget.

Prompt template for wrapping an Input:

```text
Inside FieldPassword, add a Container named PasswordWrap (position:relative; display:flex; align-items:center).

Inside PasswordWrap, add an Input widget named Input_Password:
  - Type: Password
  - Variable: Password (existing local variable)
  - Placeholder: "••••••••"
  - Extended Properties: style = "..."

Delete the original Input_Password that is a direct child of FieldPassword.

Find the Label widget in FieldPassword whose TargetWidget is the original Input_Password and re-point it to the new Input_Password inside PasswordWrap.
```

This makes the 3-step operation explicit so Mentor can execute it in one pass without trial and error.

**Why**

Without these explicit steps, Mentor may attempt to use `MoveBeforeSibling` or similar positional methods on a different-parent target, fail silently or with a compilation error, then recover in a second/third pass.

**When to ask**

When multiple Labels or other references point to the input being moved, list them all explicitly before asking Mentor to re-point them.

**Evidence**

Real session: "wrap Input_Password in PasswordWrap" took 3 `applyModelApiCode` passes — one for sibling creation, one compilation error from a debug loop (`IModelObject.Name`), one for the actual create-delete-repoint sequence. Documenting the 3-step pattern makes this single-pass.

---

## Widget Traversal API

### No `.AllWidgets` — Use `.Widgets` With Explicit Recursion

**Failure pattern**

```csharp
screen.AllWidgets  // CS1061: 'IMobileScreen' does not contain a definition for 'AllWidgets'
block.AllWidgets   // CS1061: 'IMobileBlock' does not contain a definition for 'AllWidgets'
```

**Preferred pattern**

`.Widgets` returns direct children only. For deep traversal, write an explicit recursive helper:

```csharp
ServiceStudio.Plugin.NRWidgets.IButton FindButton(
    System.Collections.Generic.IEnumerable<OutSystems.Model.UI.IWidget> widgets, string name)
{
    foreach (var w in widgets)
    {
        if (w is ServiceStudio.Plugin.NRWidgets.IButton btn && w.Name == name) return btn;
        var result = FindButton(w.Widgets, name);
        if (result != null) return result;
    }
    return null;
}
```

**Why**

`IMobileScreen` and `IMobileBlock` expose only `.Widgets` (direct children). `.AllWidgets` is not part of the ODC model API.

**When to ask**

Not applicable — this is a deterministic API constraint.

**Evidence**

Real session: two consecutive CS1061 errors on `AllWidgets` before self-recovery with `.Widgets` recursion.

---

### `System.Collections.Generic` Required for Recursive Helpers

**Failure pattern**

Declaring a local recursive helper with `IEnumerable<T>` parameter type without adding `System.Collections.Generic` to the `imports` array:

```csharp
// imports: ["System.Linq", "OutSystems.Model", ...]  ← missing Collections.Generic
ServiceStudio.Plugin.NRWidgets.IButton FindButton(
    IEnumerable<OutSystems.Model.UI.IWidget> widgets, string name)  // CS0246
```

**Preferred pattern**

Always add `System.Collections.Generic` to `imports` when any local function uses `IEnumerable<T>`:

```csharp
// imports: ["System.Collections.Generic", "System.Linq", "OutSystems.Model", ...]
ServiceStudio.Plugin.NRWidgets.IButton FindButton(
    System.Collections.Generic.IEnumerable<OutSystems.Model.UI.IWidget> widgets, string name)
// OR use the fully-qualified name inline and skip the import
```

**Rule**

Whenever a recursive `FindWidget` / `FindButton` helper is generated, add `System.Collections.Generic` to `imports` unconditionally. Alternatively, use the fully-qualified `System.Collections.Generic.IEnumerable<T>` inline — this avoids needing the import.

**When to ask**

Not applicable — deterministic requirement.

**Evidence**

Real session: CS0246 on `IEnumerable<>` on two consecutive attempts after switching from `.AllWidgets` to recursive helper.

---

## Layout Block Navigation

### Screen Content Widgets Live Inside PlaceholdersContent, Not Directly on the Screen

**Failure pattern**

```csharp
var screen = mainFlow.Nodes.OfType<IMobileScreen>().Named("Search_Query");
var form = screen.Widgets.OfType<IForm>().Named("FormSearch");
// runtime: "Unable to find object with Name equal to FormSearch in collection"
```

**Why it fails**

ODC screens that use a Layout block (LayoutSideMenu, LayoutBlank, etc.) have exactly ONE direct child in `.Widgets` — the Layout block instance widget. All page-content widgets (Forms, Containers, etc.) live inside that block instance's `PlaceholdersContent` collection, under the matching placeholder (usually `"MainContent"`).

**Preferred pattern**

```csharp
// imports must include: "OutSystems.Model.UI.Mobile.Widgets"

var screen = mainFlow.Nodes.OfType<IMobileScreen>().Named("Search_Query");

var layoutInstance = screen.Widgets
    .OfType<OutSystems.Model.UI.Mobile.Widgets.IMobileBlockInstanceWidget>()
    .FirstOrDefault();

var mainContent = layoutInstance?.PlaceholdersContent
    .FirstOrDefault(p => p.Placeholder?.Name == "MainContent");

var form = mainContent?.Widgets
    .OfType<ServiceStudio.Plugin.NRWidgets.IForm>()
    .Named("FormSearch");
```

**When to apply**

Any `applyModelApiCode` targeting content widgets on a screen that uses a Layout block. Assume ALL MainFlow screens use a layout block unless the screen was built without one (bare screen).

**Import required**

Add `"OutSystems.Model.UI.Mobile.Widgets"` to `imports` when using `IMobileBlockInstanceWidget`.

**When to ask**

Not applicable — this is a structural property of how ODC screens with layout blocks are modeled.

**Evidence**

Real session: 4th `applyModelApiCode` attempt before correct traversal. First 3 used `screen.Widgets.OfType<IForm>()` directly — all failed with runtime "Unable to find object" exception.

---

## ODC Platform Limits (Cannot Fix Via Prompt Alone)

These gaps cannot be resolved by improving the Mentor Studio prompt. Document them as review notes.

### TableRecords — No Per-Row Extended Properties

`ITableRecords.Row` returns an `IContent`. `IContent` does not implement `IExtendedPropertiesNode`. There is no way to add Extended Properties to individual table rows.

When a prompt asks for "row card" styling on a `TableRecords` widget, the only writable target is the table widget itself — the style applies to the `<table>` element, not `<tr>`.

True per-row card styling requires converting `TableRecords` to a `List` widget with an item `Container` — a structural refactor, not a cosmetic change. Document as a manual ODC Studio task.

**Evidence**

Real session: Mentor correctly identified the limit and applied row-card style to `Table_RecentQueries` (table element) instead of per-row.

---

### SVG Icons Cannot Go In Text Widgets

OutSystems Text widgets render plain text. SVG `<path>` strings are not rendered as graphics. Options:
- Use OutSystems UI Icon widget (limited icon set, but safe)
- Use Expression widget with `<svg>...</svg>` HTML string — works but is fragile and not Mentor-friendly
- Omit icon and add a review note: "Replace icon placeholder with Icon widget from OutSystems UI after Mentor applies"

Never use arbitrary Unicode as an SVG approximation — rendering is font-dependent and unreliable.

When adapting tested design-to-app or spec-driven scaffold prompts, treat raw SVG and font-icon markup as UI review risks before hardening:

- Do not emit `ph ph-*` font icon classes unless the target app's icon font dependency is explicitly verified.
- Prefer an OutSystems UI Icon widget when a matching icon exists.
- If raw SVG is explicitly required inside a dark or colored container, review whether `fill` and `stroke` must be fixed directly on the SVG rather than relying on `currentColor` or descendant CSS selectors.
- Keep raw SVG guidance as a review note unless current ODC docs, generated catalog facts, or tenant observation confirms the exact rendering path for this target.

Evidence: tested `outsystems-spec-driven-build` prompt-builder guardrail for SVG icon color baking and missing Phosphor font rendering, reconciled with OMI's safer Icon-widget-first guidance.

### Checkbox Internal Styling Not Reachable

ODC Checkbox widget generates its own `<input type="checkbox">` element inside a wrapper div. Extended Properties on the Checkbox widget apply to the outer wrapper, not the inner input element. The following cannot be controlled via Extended Properties:
- Checkbox square color (accent-color requires a CSS class, not inline style)
- Checkbox size
- Checkmark color

Workaround: add a CSS class to the module's stylesheet that sets `accent-color: #1068eb` on `input[type=checkbox]`, then reference that class. This requires manual CSS in the module — it cannot be done through a Mentor Studio prompt alone.

---

## Screen Navigation Target Ordering

### Create Navigation Target Screens Before Consumer Screens

**Failure pattern**

Ordering screen batches so that a screen navigating to another screen is created before the navigation target exists:

```text
Batch 3: Dashboard — navigates to RequestDetail (doesn't exist yet)
Batch 4: Requests  — navigates to RequestDetail (doesn't exist yet)
Batch 5: RequestDetail — created last, too late
```

Mentor cannot wire `Navigate to RequestDetail` when RequestDetail does not exist. The navigation is either skipped, left as a broken reference, or Mentor creates an unintended placeholder screen.

**Preferred pattern**

Before ordering screen batches, build the full screen navigation graph by listing every `Navigate to <Screen>` call across all screens. Any screen that appears as a navigation destination is a **navigation producer**. Create it before any screen that navigates to it:

```text
Batch 3: RequestDetail — navigation target, exists first ✓
Batch 4: Dashboard — navigates to RequestDetail ✓
Batch 5: Requests  — navigates to RequestDetail ✓
```

**Why**

Screens are navigation producers for the screens that reference them. Producer-first ordering applies to screen-to-screen navigation exactly as it applies to server actions and entities.

For bidirectional navigation or circular dependency, split the screens into shell and wiring batches:

```text
Batch 3: Requests — minimal shell, no outbound navigation yet
Batch 4: RequestDetail — navigates back to Requests ✓
Batch 5: Requests — complete filters/table and navigate to RequestDetail ✓
```

Always defer outbound navigation wiring from the target screen until its destination screen exists, or create that destination as the minimal shell first. Do not wire `Navigate to <Screen>` in any prompt block where `<Screen>` is neither already present nor created in an earlier block.

For saved prompt packs, run `scripts/validate_screen_navigation_order.py <prompt-file>` before delivery.

**When to ask**

When two screens navigate to each other (circular dependency), ask which is the primary entry point and create it first as a minimal shell, then fully implement both in subsequent turns.

**Evidence**

Caught in RequestPulse implementation planning (2026-06-22): Dashboard and Requests batches were ordered before RequestDetail. Both referenced `Navigate to RequestDetail` which did not yet exist.

---

## List And Table Widgets Produce Invalid OML (OS-APPS-40028)

### Never Create List Or Table Widgets In Mentor Screen Prompts

**Failure pattern**

Including a List widget or Table widget in a Screen Mentor prompt:

```text
Screen: MyRequests
Add a List widget with Source = GetMyRequests.List, displaying SupplyItem.Name and SupplyRequest.Status per row.
```

**Preferred pattern**

Use Container + Expression + Button stubs only. Mentor cannot produce valid OML for List or Table widgets. The AVS validation service rejects the binary with OS-APPS-40028 on publish.

```text
Screen: MyRequests
Layout (Container only — NO List widget, NO Table widget):
- Expression: GetMyRequests.List.Current.SupplyItem.Name
- Expression: GetMyRequests.List.Current.SupplyRequest.Status
- Button "View Details" → GoToRequestDetail
```

After publishing the stub successfully, add the List/Table widget manually in ODC Studio.

**Why**

Confirmed across 3 Mentor sessions (sessions 7b074f4c, 186003ce, 01b0ad41) on the RequestPulse app: every screen prompt that included a List or Table widget produced OS-APPS-40028 on publish regardless of the step sequence (with or without `getThemeNames`). Stub screens using only Container + Expression + Button published successfully every time.

**When to ask**

Always. Do not include List or Table widgets in any Mentor screen prompt. Mark as a review note that list display must be added manually in ODC Studio.

**Evidence**

Real session correction (RequestPulse implementation, 2026-06-24/25).

---

## Selective Publish-Validator Classifiers

### RadioGroup And ButtonGroup Duplicate Default Children

**Failure pattern**

Direct OML/model pipelines report OS-APPS-40028 when generated RadioGroup or
ButtonGroup structures duplicate default children instead of using or editing
the default children.

**Preferred pattern**

For OMI prompt guidance, do not append replacement children blindly when a
RadioGroup or ButtonGroup pattern may already create default child items. Ask
for ODC Studio review of the generated item structure, or use catalog-backed
properties and explicit options only when current evidence supports the exact
generation path.

**Why**

This is useful as a publish-validator classifier and review note, but it comes
from direct OML/model-pipeline evidence. direct OML cache cleanup, Entities
chunk repair, ReferersData, VerifyCaches, RebindData, and OML header mutation
rules are not migrated into OMI prompt guidance because OMI does not mutate OML
files directly.

**When to ask**

If OS-APPS-40028 appears after a prompt involving RadioGroup or ButtonGroup,
inspect publish logs and generated widget children before retrying. Ask the user
before guessing if the failing construct is unclear.

---

## Identifier Input Binding Produces Invalid OML

### Never Bind An Input Widget Directly To An Identifier Type Variable

**Failure pattern**

Creating an Input widget bound to a local variable of Identifier type:

```text
Input bound to SelectedItemId (SupplyItem Identifier)
```

**Preferred pattern**

Use LongInteger or Text as the local variable type for any Input widget. Convert to Identifier after the user provides the value.

```text
Local variable SelectedItemIdValue (LongInteger)
Input bound to SelectedItemIdValue
```

If the SA call requires an Identifier, pass `SupplyItem.Id` directly from an aggregate result rather than through an Identifier-typed Input variable.

**Why**

ODC platform does not allow binding a plain Input widget directly to an Identifier type variable. Mentor generates OML that is rejected by AVS with OS-APPS-40028 on publish.

**Evidence**

Real session correction (RequestPulse CreateRequest screen, 2026-06-24).

---

## Server Action / Entity Action Naming Conflict

### Use Unique Names For Server Actions When An Entity Has A Same-Named Entity Action

**Failure pattern**

Creating a Server Action named `CreateSupplyRequest` when an entity action of the same name already exists:

```text
Server Action: CreateSupplyRequest
```

**Preferred pattern**

Choose a distinct SA name that does not conflict with any entity action:

```text
Server Action: SubmitSupplyRequest  ← avoids conflict with CreateSupplyRequest entity action
```

**Why**

When Mentor creates a SA with a name that conflicts with an existing entity action, it either auto-renames to `CreateSupplyRequest2` (breaking the prompt intent) or produces invalid OML referencing the wrong action. The mismatch triggers OS-APPS-40028 on publish.

**When to ask**

Before naming any Server Action, check whether the entity has an action with the same name. This commonly happens with entity actions like `CreateX`, `UpdateX`, `GetX`, `DeleteX`. If the SA must be named the same, ask the user before proceeding.

**Evidence**

Real session correction (RequestPulse CreateRequest screen, 2026-06-24): Mentor called `CreateSupplyRequest2` instead of `CreateSupplyRequest`. Root cause: entity action naming conflict.

---

## One Server Action Per Mentor Session

### Never Batch Multiple Server Actions In A Single `mentor_start` Call

**Failure pattern**

Sending a prompt that creates or substantially modifies two or more Server Actions in a single Mentor session:

```text
Create Server Actions CreateSupplyRequest and ReviewRequest. [both in one prompt]
```

**Preferred pattern**

One SA per `mentor_start` call. Publish and confirm before starting the next SA session.

```text
Session 1: Create Server Action CreateSupplyRequest → publish → confirm Finished
Session 2: Create Server Action ReviewRequest       → publish → confirm Finished
```

**Why**

Multiple SAs in one Mentor session consistently produce OS-APPS-40028 on publish. The AVS validator rejects the generated OML binary. This limit is independent of SA complexity.

**When to ask**

Never batch. Always one SA per session.

**Evidence**

Real session (RequestPulse implementation, 2026-06-24): confirmed across all 5 SA sessions.

---

## Session Isolation — Each `mentor_start` Reads From Last Published Revision

### Mentor Sessions Do Not Inherit Prior Session State

**Failure pattern**

Assuming a new Mentor session continues from where a previous session left off — including a session whose publish failed or was never started:

```text
# Session 1 made changes but publish returned OS-APPS-40028
# Session 2 assumes those changes are available as a baseline
```

**Preferred pattern**

Each `mentor_start` reads from the **last successfully published revision**. A failed or unpublished session leaves no trace. Plan accordingly:

- If a publish fails, the next session's baseline is the revision before the failure.
- Publish gates are required between sessions when later sessions depend on earlier ones.
- If multiple sessions can be independent of each other, they can run in parallel (see parallel publish pattern below).

```text
Published rev 12 → mentor_start session A (reads rev 12) → publish → rev 13
                                                              ↓
                                             mentor_start session B (reads rev 13) → publish → rev 14
```

**When to ask**

Not applicable — deterministic platform behavior. State it as a constraint in every multi-session plan.

**Evidence**

Real session (RequestPulse implementation, 2026-06-24): confirmed by retry sessions that correctly re-read from the last Finished publish, not from failed or abandoned sessions.

---

## OS-APPS-40028 Recovery Procedure

### Fresh Session Is The Only Valid Recovery Path

**Failure pattern**

After `publish_status` returns `Finished` but the actual result is OS-APPS-40028, attempting to resume, patch, or retry the same Mentor session:

```text
# publish failed with OS-APPS-40028
# attempting to continue the same mentor_session_id
mentor_start(resume: true, mentor_session_id: "...")  # not valid
```

**Preferred pattern**

When publish returns OS-APPS-40028:

1. Identify the element that caused invalid OML (List widget, Identifier Input, SA naming conflict, etc.).
2. Strip or replace that element from the prompt.
3. Start a fresh `mentor_start` — new session, reads from the last successful publish.
4. Publish the new session.

There is no resume or patch path. The broken OML binary is discarded automatically.

```text
# Step 1: identify root cause from failure pattern
# Step 2: remove offending element from prompt
# Step 3:
mentor_start(app_key=..., prompt="[corrected prompt without offending element]")
# Step 4: poll until succeeded, then publish_start
```

**When to ask**

When the root cause of OS-APPS-40028 is not clear: inspect `publish_logs` for the failed publication, examine the Mentor session summary for clues, then ask the user before guessing.

**Evidence**

Real session (RequestPulse implementation, 2026-06-24): 3 recovery cycles — List widget removed (sessions 7b074f4c, 186003ce, 01b0ad41 → all failed), List widget completely omitted (session 6a2ea56a → succeeded).

---

## Stub-First — Prefer A Publishable Stub Over A Complete-But-Broken Implementation

### Strip Elements That Risk OS-APPS-40028 And Publish The Stub

**Failure pattern**

Including every planned element in a single Mentor prompt, then debugging repeated OS-APPS-40028 failures without isolating the offending element:

```text
Screen: MyRequests
List widget, aggregates, navigation, client actions, filters — all in one prompt
# publish fails → unclear which element caused it → retry whole prompt → fails again
```

**Preferred pattern**

When any element risks OS-APPS-40028 (List widget, Table widget, Identifier Input, SA call with naming conflict, or any element of uncertain OML validity), apply stub-first:

1. Strip the risky element.
2. Build the minimal publishable version: Container + Expression + Button + navigation client action.
3. Publish the stub and confirm Finished.
4. Add the complex element manually in ODC Studio.

```text
# Stub pattern (always publishes):
Screen: MyRequests
Layout (Container only — NO List widget, NO Table widget):
- Expression: GetMyRequests.List.Current.SupplyItem.Name
- Button "View Details" → GoToRequestDetail
# → publish succeeds
# → add List widget in ODC Studio manually
```

**Why**

A published stub is infinitely more useful than a complete-but-broken OML that blocks the whole app. Stub screens compose correctly with other screens, appear in navigation, and accept manual completion in ODC Studio.

Generalizes beyond List widgets: any future OML invalidity source should be stripped to stub first, not debugged in repeated Mentor sessions.

**When to ask**

When unsure whether an element is safe, ask before including it. Default to stub-first whenever OML validity of a widget or binding is unconfirmed.

**Evidence**

Real session (RequestPulse implementation, 2026-06-24/25): stub-first used for MyRequests, CreateRequest, ApprovalQueue, CatalogManagement, UserRoles — all published successfully on first try.

---

## Mentor SA Sessions May Silently Modify The Data Model

### Verify Entity Structure After Each SA Session Publish

**Failure pattern**

Assuming a Server Action Mentor session only creates or modifies the SA itself:

```text
# Session: Create SaveSupplyItem SA
# Assumption: only SaveSupplyItem logic is created
# Reality: Mentor also added UnitPrice and Category attributes to SupplyItem entity
```

**Preferred pattern**

After each SA session publish succeeds, inspect affected entity structure:

```text
context_entities(app_key=...) → check SupplyItem attributes
```

Look for:
- Attributes added that were not in the original data model
- Attributes renamed or type-changed to resolve the SA's compile errors
- New entities or structures created as dependencies

If unexpected changes appear, decide whether to accept them (update the plan's data model map) or revert them in the next Mentor session.

**Why**

Mentor resolves TrueChange errors autonomously. When a SA references attributes that don't exist, Mentor may add them rather than raising an error. This is sometimes desirable (missing attributes get added automatically) but can silently diverge from the planned data model.

**When to ask**

When the Mentor session summary mentions entity changes not in the original prompt, confirm with the user whether to accept or revert.

**Evidence**

Real session (RequestPulse SaveSupplyItem session 341ed881, 2026-06-24): Mentor added `UnitPrice` (Decimal) and `Category` (Text) to `SupplyItem` because the SA referenced them and they were absent from the published model.

---

## Screen Input Parameter Collision Causes Action Input Auto-Rename

### Use Distinct Names For Screen Action Inputs That Share Names With Screen Inputs

**Failure pattern**

Screen has input parameter `ItemId`; screen action also declares input `ItemId`:

```text
Screen: CatalogManagement
  Input: ItemId (SupplyItem Identifier)

Screen Action: GoToEditItem
  Input: ItemId (SupplyItem Identifier)  ← collision with screen input
```

Mentor auto-renames the action input to `ItemId2`. Any code referencing `GoToEditItem(ItemId: ...)` now must use `GoToEditItem(ItemId2: ...)`.

**Preferred pattern**

When a screen action receives the same value as a screen input, name the action input differently:

```text
Screen Action: GoToEditItem
  Input: TargetItemId (SupplyItem Identifier)  ← distinct name, no collision
```

Or accept the auto-rename and read it from the Mentor session summary before writing any downstream prompt that calls the action.

**When to ask**

When a screen action input name matches a screen-level input parameter, decide before writing the prompt whether to use a distinct name or accept the auto-rename. Check the session summary for `InputName2` patterns before writing the next prompt.

**Evidence**

Real session (RequestPulse CatalogManagement session bbd563a3, 2026-06-25): Mentor reported `ItemId2` auto-rename in session summary. Wiring stayed correct because the button call also used the renamed param.

---

## Navigation Wiring Targets The Menu Web Block, Not A Screen

### TopMenu Navigation Prompts Must Reference The Menu Block, Not MainFlow Screens

**Failure pattern**

Prompt says "add menu links to all screens" or "update the TopMenu on each screen" — Mentor does not know which block to target and may attempt to modify each screen's layout block instance independently:

```text
# Wrong: vague target
"Add navigation links to MyRequests, ApprovalQueue, CatalogManagement, UserRoles across all screens."
```

**Preferred pattern**

Target the Menu web block directly. Mentor uses `getWebBlockNames → getWebBlock` to locate it:

```text
"On the Menu block (the TopMenu layout's navigation web block), add menu links:
- 'My Requests' → MyRequests screen
- 'Approval Queue' → ApprovalQueue screen
- 'Catalog' → CatalogManagement screen
- 'User Roles' → UserRoles screen"
```

All screens that use `LayoutTopMenu` will inherit the change automatically because they reference the same block instance.

**Why**

ODC layout blocks are shared. Changes to the block propagate to all screens using it. Modifying each screen individually is redundant and may create inconsistent state.

**When to ask**

When the layout block name is unknown, call `context_screens` to find the layout block used (appears as a block instance in the screen widget tree), then reference that block name in the prompt.

**Evidence**

Real session (RequestPulse navigation session bf89f0ff, 2026-06-25): Mentor correctly used `getWebBlockNames → getWebBlock` steps when the prompt targeted the Menu block. All 4 nav links created in one session.

---

## `getTrueChangeErrors` Mid-Session Is A Positive Signal

### Do Not Treat `getTrueChangeErrors` Step As A Risk Indicator

**Failure pattern**

Observing `getTrueChangeErrors` in the `mentor_get_run` step sequence and interpreting it as a sign the session is about to fail:

```text
currentStep: getTrueChangeErrorsAndWarnings
# Assumption: this step correlates with OS-APPS-40028
# Action: cancel and retry with different prompt
```

**Preferred pattern**

`getTrueChangeErrors` means Mentor is self-validating against TrueChange before finalizing the OML. This is correct behavior. Let the session complete. Intervene only if the session reaches `status: failed` or the final `publish_status` returns a failure.

The real OS-APPS-40028 signal is `publish_status → Finished` combined with AVS rejection text in `publish_logs` — not the presence of `getTrueChangeErrors` in the step sequence.

Sessions that omit `getTrueChangeErrors` may actually be higher risk: Mentor committed without self-validation.

**When to ask**

Never cancel a session based on step sequence alone. Wait for terminal `status: succeeded` or `status: failed` from `mentor_get_run`.

**Evidence**

Real session (RequestPulse implementation, 2026-06-24): early hypothesis that `getTrueChangeErrors` → failure was disproven. Root cause of all OS-APPS-40028 failures was the List widget, not the step sequence.

---

## Parallel Publish + Mentor Session Pattern

### Start Next Mentor Session While Previous Publish Is Running

**Failure pattern**

Waiting for publish to complete before starting the next Mentor session:

```text
publish_start → poll until Finished → mentor_start (next)
# Sequential: publish time + Mentor time for every revision
```

**Preferred pattern**

Start the next Mentor session immediately after `publish_start` returns, while polling `publish_status` in parallel:

```text
publish_start(session A) → [parallel]
  ├── poll publish_status until Finished
  └── mentor_start(session B) → poll mentor_get_run until succeeded

# When publish Finished AND session B succeeded:
publish_start(session B)
```

This works because each `mentor_start` reads from the last **published** revision — as long as session B does not depend on changes introduced in session A's publish, the parallel start is safe.

**Safety constraint**

Do NOT publish session B until session A's publish is confirmed Finished. Publishing out of order against uncommitted state corrupts the revision chain.

**When NOT to parallel**

When session B's prompt references elements created or modified by session A's publish (e.g., a screen that calls a SA created in session A). In that case, wait for session A's publish before starting session B.

**Evidence**

Real session (RequestPulse implementation, 2026-06-25): CatalogManagement (rev 16) publish ran in parallel with UserRoles Mentor session (rev 17), saving ~2–3 minutes of wall-clock time per revision pair.

---

## Maintenance

Add future corrections here as compact entries. Each entry should include the failure pattern, preferred pattern, why the preferred pattern is safer, when to ask, and a minimal example.

Do not treat every Mentor Studio correction as official platform truth. When a rule is syntax-sensitive, verify it against current OutSystems public documentation or source documentation before promoting it.

### MCP-driven Mentor execution (added 2026-07-18)

Lessons from a full agentic-app build (PlayRight "Member Support") driven end-to-end via `mentor_start` / `publish_start` over the OutSystems MCP.

**1. Decompose data-write and multi-element turns.**
- Failure pattern: one `mentor_start` prompt that creates a large action (e.g. a seed action writing ~20 records) or many elements at once. Observed: Mentor entered a non-converging build → delete → rebuild loop for ~21 min, then had to be cancelled — and the cancel itself wedged in `cancelling`.
- Preferred pattern: one entity-group, one member, or one action per turn. Build a seed action incrementally (idempotency guard first, then one member per turn, appending before the End node).
- Why safer: small turns converge and land with 0 errors; large data-write turns are the most failure-prone step.
- When to ask: if a single turn must create more than roughly one write-heavy action, split it first.
- Minimal example: `Turn 1: BootstrapData guard + member A → Turn 2: append member B → …`.

**2. Publish after every session; never orphan a session.**
- Failure pattern: running several turns then starting a *new* session on the same app before publishing. Mentor changes are **session-local until published** — a fresh session forks from the last *published* revision and cannot see unpublished work. Field-observed over the MCP (not in official docs): starting a new session appeared to **invalidate the prior session's token** (`publish_start` → `signature_invalid`), stranding the unpublished work. Treat the publish-before-new-session rule below as a conservative operational safeguard rather than a documented platform guarantee.
- Preferred pattern: `publish_start` + poll `publish_status` at each stage boundary and before ever starting another session on that app; keep working in one session per app until you publish.
- Why safer: guarantees work persists and is visible cross-session/cross-app; avoids losing a whole build (this cost a full screen rebuild).
- When to ask: never start a second concurrent session on an app that has unpublished changes.
- Minimal example: `stage done → publish_start(session) → publish_status success → then continue or start next session`.

**3. Consider decoupling cross-app parameters from entity Identifiers.**
- Note on authority: official ODC docs state service actions are strongly typed and **may use entities and structures in their signatures** (`Service actions`; `Reuse elements across apps`). This is an optional decoupling pattern, not a platform requirement.
- Field-observed failure pattern: exposing a service action (e.g. `Call<Agent>`) with an input typed as an `<Entity>` Identifier, then wiring it from a consumer that does not reference that entity — the argument could not be wired in that build and the cross-app signature cache lagged.
- Optional decoupling pattern: when a consumer should not take an entity dependency, type cross-app keys as **Long Integer** (or use a structure, which ODC best practice prefers over entities) and convert internally with `LongIntegerToIdentifier()` where an entity identifier is required.
- Why safer: a consumer can always pass a Long/structure without referencing or exposing the producer's entity.
- When to ask: any time a public / service-action input references an entity key and the consumer should stay loosely coupled.
- Minimal example: `CallMemberSupport(SessionId Text, UserInput Text, MemberId Long)` then internally `GetMemberProfile(LongIntegerToIdentifier(MemberId))`.

**4. Use the built-in `GenerateGuid` Server action for `SessionId`; it is not an expression function.**
- Authority: official ODC docs prescribe generating the agent `SessionId` with the built-in `GenerateGuid` **Server action** in ODC Studio ("though you can use any method that produces a unique identifier") — `Consuming AI agents in apps`.
- Failure pattern: instructing Mentor to call `GenerateGuid` as though it were an **expression function**; it is a Server action element, so an expression-context search finds nothing and Mentor burns minutes.
- Preferred pattern: add the `GenerateGuid` Server action to the flow (drag from toolbox / type its name) and assign its output to `SessionId`. `crypto.randomUUID()` in a JavaScript node is a deliberate **client-side** alternative when you want the GUID generated on the client rather than via the server action.
- Why safer: matches the documented consumer-app pattern; avoids the fruitless expression-function search.
- When to ask: confirm whether the GUID should be generated server-side (`GenerateGuid` Server action) or client-side (`crypto.randomUUID()`) before prompting the SessionId step.
- Minimal example: add the `GenerateGuid` Server action to the flow → assign its output to `SessionId` (server-side), or `Assign SessionId = <JavaScript node: return crypto.randomUUID()>` (client-side). (Output-parameter name is not asserted here — read it off the action in Studio.)

**5. The MCP `test_setup_start` / `exec_in_app` harness cannot verify agentic apps end-to-end.**
- Scope: this is about the observed MCP fork harness (`test_setup_start` / `exec_in_app` / `db_query` v1), **not** ODC's platform test tooling. Official ODC docs show generated **test apps** and **Agent Evaluations** that *do* execute a public agentic **service action** against a dataset (`Test agentic apps`; `Run your first evaluation`; `Create and manage datasets`).
- Failure pattern: expecting the MCP `test_setup_start` / `exec_in_app` harness to invoke an agent. Observed: the harness exposes **server actions only** — **service actions 404** (an agent's `Call<Agent>` / `AgentFlow` is a service action). Forks may also lack **static-entity records**, so seed actions can fail with FK errors (`... does not exist in the referenced entity`) inside the fork even when the real app is fine; and `db_query` (v1) returns no rows (minimal binding), so it cannot confirm table contents.
- Preferred pattern: use this MCP harness to verify server-action tools/logic; verify the agent flow via ODC's own **Agent Evaluations / generated test app**, or through the **published UI** (logged in).
- Why safer: avoids false negatives from *this harness's* limitations while still using the platform's supported agentic-test paths.
- When to ask: before promising headless verification of an agent via `exec_in_app`, confirm the entry point is a server action, not a service action — and prefer Agent Evaluations for the service-action path.
- Minimal example: `exec_in_app(GetDistributions, MemberId=…)` verifies tool data; agent flagging/drafting must be verified via the deployed screen.
