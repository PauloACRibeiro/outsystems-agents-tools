# ODC Visual-Source Enriched Blueprint

> ODC error codes: see `../../shared/reference/odc-error-registry.md` for the canonical index of every code named below.

## Purpose

This is the OMI-owned portable enriched blueprint for visual-source and
shell-first scaffold work. Use the enriched blueprint as the primary structured artifact.
Treat the Visual-Source UI Prompt Packet as the emitted prompt-facing summary
derived from this asset, not as the replacement for it.

Build or validate the OMI Visual-Source Enriched Blueprint before emitting the
paste-ready Mentor Studio prompt.
Do not treat visual-source intake as Mentor Web new-app generation.
The Visual-Source UI Prompt Packet remains blueprint-derived preparation or
summary, not a required extra visible response section, and this route produces
paste-ready Mentor Studio prompts only for verified or explicitly approved
app-shell targets.

## What It Reuses From design-to-app

This guide keeps the quality-bearing structure that proved useful in
`outsystems-design-to-app`, while re-homing it inside OMI as a portable file:

- `app_chrome`
- `blocks`
- `design_system`
- `entities`
- `screens`
- `icon_mapping`
- `roles`
- `acceptance_checklist`

The goal is not to recreate the full design-to-app workflow. The goal is to
preserve the parts of the enriched blueprint that make UI intent reviewable,
traceable, and less likely to drift before Mentor prompt emission.

## OMI-Specific Additions

OMI adds two top-level sections that design-to-app did not use in the same way:

- `target_context`: records target mode, readable app name, canonical app key,
  verified shell requirement, existing assets, target surfaces, and review
  notes
- `evidence_boundary`: records evidence status, grounding notes, and review
  notes so the artifact can stay portable without overstating certainty

These additions keep the artifact aligned with OMI's reviewed-shell and
existing-app boundaries.

## Every evidence_boundary Disclosure Owes A Check

An `evidence_boundary` entry carried into a Mentor package must map to a named,
executable **post-publish** check **before the phase is reported done**. Exactly
two forms count:

- a **render-gate row** — the disclosure becomes something a principal opening
  the screen can see to be true or false, recorded with the screen and that
  principal named
- an **enumeration assertion** — the disclosure becomes a named element, count,
  or record list diffed against the deployed model

A disclosure with neither is not a caveat. It is a known gap the run has agreed
not to look at.

On the v2 run the most loudly disclosed trap of the entire build — the dispatch
payload display, `BR-SC-006` — was carried into the package, restated in the
prompt, and restated in the summary, and it shipped unmet. Nothing was hidden
and nothing was checked: every reader of that phase saw the disclosure and read
it as evidence that the risk was being managed. Volume of disclosure is not
coverage, and it correlates with the opposite often enough to be a warning sign.

Write the check into `acceptance_checklist` at the moment the disclosure is
written, not later. A disclosure authored on its own is authored at the moment
somebody decided not to solve the problem, which is the worst available moment
to be trusted to remember it.

## primary_color

`primary_color` is the top-level brand anchor for the blueprint. Set it to the
single color that best represents the intended app identity when that signal is
clear from the source material or approved brand guidance.

Treat `primary_color` as informational unless the rest of the artifact makes
the mapping explicit. It may guide theme alignment and help seed
`design_system.colors`, but it does not replace the fuller token set under
`design_system` and should not be treated as an automatic one-value theme
generator.

## Required Invariants

The enriched blueprint must preserve these invariants before prompt emission:

- Block Mapping Gate
- Layout Skeleton Gate
- Source-Name To Block Gate
- Four-part section contract
- Data-Flow Parity Gate
- producer before consumer
- states and feedback
- polish acceptance

In practice, that means each section should remain specific enough to recover
component choices, data producers, repeated-content ordering, and feedback
states without falling back to screenshot imitation or generic container sprawl.

## Boundary Rules

- No automatic app_create
- No implicit mentor_prompt or mentor_create_asset (pre-2026-09: mentor_start)
- No implicit publish, via mentor_publish or otherwise (pre-2026-09: publish_start)
- Do not add sessionId
- Do not add mentor_session_id
- Do not add mentor_session_token
- Do not add env_key
- Do not add Claude-only cache paths

The enriched blueprint is a portable planning and prompt-grounding artifact. It
must not become a side channel for execution state, tenant credentials, cache
locations, or publish intent. Shell creation, Mentor execution, and publish
remain separately approved actions outside this file.

## Target Modes

- existing-app
- verified blank shell
- shell-first scaffold

Use `existing-app` when the target already has verified assets that must be
reused or changed carefully. Use `verified blank shell` when the app exists but
the initial structure is intentionally minimal. Use `shell-first scaffold` when
the first-pass structure should be prepared for a shell that already exists or
has separately approved creation.

A shell freshly minted by an approved `app_create` is `shell-first scaffold`, not
`verified blank shell` — since ODC MCP 0.14.0 that shell arrives template-backed,
carrying `Common`, `Layouts` and `Themes` that must be preserved rather than
rebuilt. Reserve `verified blank shell` for a shell proven blank by the Shell
Provenance Gate: the `blank` opt-out, a kind with no standard template, or a
pre-0.14.0 create.

## Existing-Asset Reuse Channel

`target_context.existing_assets` **announces that the target app has verified
assets**. It does not say which part of this blueprint is one of them. The reuse
channel is the other half: it **binds one region or one entity to a named
asset** that already exists in the target app, so the build is told what not to
create instead of inferring it.

Two fields carry the binding:

- **Region-level** `"reuse": {"block": "<name>"}` on a `main_content` section
  (leaf section or group item): this region is an app-local web block that
  already exists. The `<name>` may be flow-qualified (`MainFlow/RecentQueriesPanel`)
  and is therefore **not required to be a bare catalog token** like a
  `outsystems_hints.block` value; it names an asset, not a catalog pattern.
  A region carrying `reuse` satisfies the Block Mapping Gate on its own — it
  needs no `outsystems_hints.block` and no `custom_block_needed` flag, and it
  **must not carry either**: a region binds to an existing block OR describes
  one to build, never both, and the emitter's validator rejects the
  combination.
- **Entity-level** `"exists": true` on an `entities[]` entry: this entity is
  already in the target app. Its declared `attributes` are the shape the screens
  bind against and the shape to **verify**, not to create.
- **Attribute-level** `"create": true`, on one attribute of an `exists: true`
  entity: this attribute is **not yet** on the existing entity and must be
  ADDED to it, with its declared `data_type`; every other attribute on that
  entity stays a shape to verify. `create: true` on an attribute of an entity
  without `exists: true` is an error — a created entity creates all of its
  attributes already.

Both fields are valid **only when `target_context.target_mode` is
`existing-app`**. In any other target mode they contradict the declared target
and the blueprint must be returned for producer correction.

Reuse never widens the announcement: **name every reused asset in
`target_context.existing_assets` as well**, so the target boundary stays
readable on its own.

### Intake rule

Reused and existing elements **fold into modification steps, never creation
steps**:

1. For a region with `reuse`, emit a step that places and binds the existing
   block on the screen. Do not emit a create-block step, and **do not add it to
   `blocks`** — that array stays the list of blocks this build creates.
2. For an entity with `exists: true`, do not emit create-entity steps; emit a
   verification step for every attribute without `create: true`, and one
   add-attribute modification step for each attribute carrying it, stated in
   the ODC literal register (`Add attribute DigitalAdoptionScore (Integer,
   default 0) to Customer`). Do not create its relationship targets on its
   behalf.
3. Ordering still applies: an existing entity satisfies the producer-before-
   consumer requirement as soon as it is verified, so it never forces a data
   model step it does not need.
4. If a reused block or an existing entity cannot be verified in the target app
   — it is absent, or it lacks a declared attribute — **stop prompt emission and
   return the blueprint for producer correction**; **do not invent a
   replacement** and do not silently fall back to creating it.

This rule has an executable form: `scripts/blueprint_intake_plan.py
<blueprint.json>` classifies every element into creations, modifications, and
verifications exactly as above and exits non-zero on any
return-to-producer condition. Run it as a pre-flight before prompt emission.

### Declare assertions, or the post-publish guard has nothing to check

`scripts/recompute_assertions.py` is the one mechanical check of the built model
against the blueprint — and it is **inert when no screen declares
`assertions`**. It has nothing to recompute, so it reports nothing, and its
silence is indistinguishable from a pass. A run whose blueprints declare no
assertions has quietly dropped that guard.

So carry at least the **read-only zero-affordance assertions** on every screen —
the ones that say a display-only screen holds no `Button`, no `Input`, no
`Link`, no form widget. They cost a line each, they are true by construction on
a screen that was designed read-only, and they give the post-publish guard a
contract to fail against. Richer per-widget assertions are better; none at all
is the case to avoid.

The canonical **example asset is deliberately greenfield**: it carries neither
`reuse` nor `exists`, because every element in it is created. Read it for
structure, not as evidence that the existing-app path does not exist.

## Quality Sources To Preserve

The enriched blueprint should continue to absorb the durable guidance that was
previously spread across visual-source prompt packets and design-to-app review
materials:

- component selection
- states and feedback
- workflow block-mapping discipline
- gotcha review

Those inputs still shape how sections, blocks, producers, and review notes are
written. They should influence the blueprint itself and the derived
Visual-Source UI Prompt Packet, rather than being remembered only as loose prose
at the end of a prompt.

## Typed Create-Only Entities Sub-Schema

`entities` is an ordered, create-only array. Each entity object contains
`name`, `type`, and `attributes`. Each attribute contains `name` plus
`data_type`, `is_primary_key`, `is_foreign_key`, and `enum_values`, matching the
producer's snake_case field names exactly. A Static Entity may also carry the
optional entity-level `records` array defined by the producer schema.

Treat every entry as declare-and-create input for the current app scope. There
are no tenant-reference semantics inside `entities`: do not search for or
silently reuse a same-named tenant entity. Record separately verified reusable
assets in `target_context.existing_assets`; do not duplicate them in
`entities`.

The array is create-only except for entries flagged `exists: true` under the
Existing-Asset Reuse Channel above — the one declared, explicit way an entity in
this array is verified rather than created. An unflagged entry is always a
create.

Translate the typed model into Mentor data-model steps before emitting screen
steps:

1. Create supporting relationship targets before the entities that consume
   them.
2. For a normal attribute, create the declared `name` with its declared
   `data_type`; apply `is_primary_key` as declared. `enum_values` is `null`.
   For an ordinary auto-number primary key, **state the literal `DataType`
   string `Long Integer`** with `IsAutoNumber`, `IsMandatory` and
   `IsPrimaryKey` set. Do NOT request any `Identifier`-suffixed type —
   `Integer Identifier`, `Long Integer Identifier` and `Identifier` all
   validate cleanly and then fail every publish, because the model API accepts
   any string as a `DataType`, validation checks shape rather than membership in
   the platform's closed enum, and the enum is only enforced by the publish-time
   database-migration-script generator (`OS-RDBS-GEN-40002 Unknown
   OsAttributeTypes`, surfaced through the MCP publish path as an opaque
   `OS-DPL-50203`). **The class rule, scoped to the path it was measured on — an
   entity-attribute `DataType`: a string outside the platform's enum
   passes validation and fails at publish** — the same trap is documented
   for `Text Identifier` and static-entity autonumber. When a string is
   uncertain, read it off an already-published app in the same tenant rather
   than guessing a second name. Mentor applies the same convention to every
   entity it creates in a phase, so a fix turn is not assumed comprehensive:
   enumerate every entity's `Id` and check the literal string. This governs
   **entity attributes** only — an `Identifier`-suffixed type on an action
   *parameter* publishes normally. A genuinely explicit 64-bit key
   requirement must not be silently narrowed to Integer Identifier: stop and
   surface it as a Mentor/publish-path limitation requiring a deliberate
   platform or manual resolution. One attribute is the Entity Identifier —
   there are no composite keys (an alternate or composite key is a **unique
   index**), only one attribute per entity may be sequential (AutoNumber), and
   **the identifier attribute cannot be changed or renamed after the first
   publish**, so a blueprint that names it names it for the life of the app
   ([Entity](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/data/modeling/entity.md)).
3. For `is_foreign_key: true`, require `data_type` to use the relationship form
   `<TargetEntityName> Identifier`. **Instruct the delete rule away explicitly**:
   every data-model prompt carries the line **`create FK attributes with no
   delete-rule configuration, system references included`**. Mentor sets delete
   rules by default, and `ModelFeature_DeleteRuleOnReferences` /
   `ModelFeature_DeleteRuleOnSystemReferences` are removed ODC features, so the
   authoring turn is clean (`error_count: 0`, `change_applied: true`) and the
   publish fails — the same validation-passes-publish-fails class as the
   `DataType` and static-entity autonumber rules above, reported as
   `OS-RDBS-GEN-40002` ("Invalid delete rule") plus `OS-BLD-40409` and
   `OS-DPL-50205`. Referential behaviour belongs in the server action that
   performs the delete. The rule is owned by `odc-mentor-hardening.md` and its
   error treatment by `odc-platform-guardrails.md`.
4. When that foreign-key attribute has a non-empty `enum_values` list, treat
   `<TargetEntityName>` as a Static Entity: create the Static Entity first, add
   one record for each `enum_values` item, set the consuming attribute's type to
   `<StaticEntityName> Identifier`, and create the foreign-key relationship.
5. When `enum_values` is `null`, require the target to be another declared
   create-only entity, create that target first, and then create the relationship
   through its Identifier type.
6. For a standalone Static Entity, treat a non-empty `records` array as a
   non-empty ordered list of strings. Create the Static Entity and exactly one
   record per declared value, in declared order; do not require an incoming
   foreign key. Emit each static entity's `Id` with `IsAutoNumber = No` and an
   explicit, non-null integer `Id` per record, and populate the
   display/`Label` attribute — `IsAutoNumber = Yes` on a static entity leaves
   every design-time record with a null primary key: it validates clean and
   fails at publish with `OS-RDBS-GEN-40001` ("Null record PK", surfaced with
   `OS-DPL-50203`). On that failure, check static-entity `Id`s first (external
   field evidence, Arjan fork review 2026-08-12; the same
   validation-passes-publish-fails class as the `DataType` rule above). If both `records` and incoming FK `enum_values` seed the same
   Static Entity, identical ordered lists seed the Static Entity exactly once.
   If the lists differ, stop prompt emission and return the blueprint for
   producer correction. Require a matching producer-side validation gate for
   this contradiction before treating the producer and consumer as aligned.

`enum_values` on a non-foreign-key attribute is invalid because it cannot
identify a relationship target. A standalone Static Entity used as a data
source with absent or empty `records` and no incoming foreign-key attribute
with non-empty `enum_values` has no record intake path. In either case, stop
prompt emission and return the blueprint for producer correction; do not invent
records from screen prose or attribute names. The producer must supply
entity-level `records`, supply the FK-plus-`enum_values` shape, or model
runtime-populated data as a normal entity.

Do not invent a missing target entity, attribute type, or Static Entity record.
If the four typed fields contradict one another or the relationship target
cannot be derived, stop prompt emission and return the blueprint for correction.

## Screens Sub-Schema

`screens` is an ordered array of screen objects. Each screen records its
identity and intent (`name`, `type`, `description`, `entities`, `template`,
`title`, and `subtitle`) plus an ordered `main_content` array. Each
non-group `main_content` section records its layout, data source, content,
conditional rendering, and `outsystems_hints` so the prompt can preserve both
visual and data-flow intent.

Each content item may carry an optional `binds` object, for example
`binds: {"entity": "WorkItem", "attribute": "Count"}`. The `entity` names a
declared entry in top-level `entities`, and `attribute` names one of that
entity's declared attributes. Treat `binds` as a structured companion to prose
`data`: it is an additive structured hint for deterministic validation and
generation, but it does not replace prose `data`, which stays authoritative for
human-readable intent.

A section that is an app-local block the target app already has carries
`reuse` instead of `outsystems_hints.block`; see the Existing-Asset Reuse
Channel above.

Use `type: "group"` for a section whose children occupy an adaptive columns
block. In that shape, `columns` names the adaptive block, `items` contains the
ordered child sections, and each child uses `column: N` to identify the target
placeholder. Keep `columns` and every `outsystems_hints.block` value
as a bare block name such as `Columns3` or `ColumnsMediumRight`; describe
custom content in the section or item fields instead of joining names with
`plus`.

## Shared Chrome Edit Discipline

Edit the shared chrome before screen-specific polish when the reviewed source
requires more than the default brand plus avatar shell. Treat
`Common/ApplicationTitle`, `Common/UserInfo`, and `Common/Menu` as shared
chrome surfaces that should be reviewed before screen consumers depend on them.

If the reviewed source keeps the default brand plus avatar only, note that in
the artifact and leave chrome in the normal screen pass. If the reviewed source
adds custom title treatment, search, notification icons, or utility controls,
record the dedicated chrome batch in review notes so the shell does not drift.

## Design-System Discipline

This guide is portable across Codex and Claude and does not depend on
`outsystems-design-to-app` at runtime.

Capture theme-level tokens first. Prefer ThemeValues, CSS variables, and
existing theme classes for shared color, typography, spacing, radius, and
shadow rules. Use screen CSS only for screen-specific exceptions. Use block CSS
only for reusable block internals.

Record token decisions in `design_system` and keep review notes explicit when a
source treatment remains approximate. Do not move brand logic into ad hoc
screen-level overrides when a shared theme token is the correct home.

## Reusable Block Extraction Rules

Extract a reusable block when a pattern is used on multiple screens or has its
own interaction logic. Record the expected inputs, events, placeholders, and
ExtendedClass so the block stays reviewable as a first-class producer. When a
single-screen component is only local to one screen, single-screen components
stay inline instead of being promoted to `blocks`.

Use this rule for repeated KPI cards, filter bars, action groups, empty states,
and other patterns that would otherwise be redescribed multiple times. Keep the
artifact explicit about whether the reusable block is new, verified existing,
or a review-only candidate: a verified existing block is expressed with the
region-level `reuse` binding, not by adding it to `blocks`.

## Domain-Aware Styling Heuristics

Keep business/workspace apps quiet, dense, and scan-friendly; store only the
distilled review conclusion in `design_system`, `app_chrome`, and section
descriptions.

The detailed styling review contract lives in
`references/odc-visual-source-ui-discipline.md`. Avoid duplicating the full
review checklist here.

## Icon Mapping Review Contract

Use `icon_mapping` to preserve source icon intent before prompt emission. Each
entry should capture the source icon name when known, the OutSystems icon name,
the intended location, and a review note when rendering depends on target
dependencies or raw SVG behavior.

For Lucide-derived sources, map Lucide names to Phosphor/OutSystems intent and
store the bare icon name, such as `magnifying-glass`, not `ph-magnifying-glass`
or `ph ph-magnifying-glass`. The mapping is not a second icon library and does
not authorize adding Lucide as a dependency.

## How To Use It In OMI

1. Confirm the target mode and shell boundary in `target_context`.
2. Capture evidence status and grounding limits in `evidence_boundary`.
3. Fill `app_chrome`, `blocks`, `design_system`, `entities`, and `screens`
   with the structured detail needed for review.
4. Preserve `acceptance_checklist` as a first-class verification surface.
5. Derive the Visual-Source UI Prompt Packet from this enriched blueprint once
   the artifact is coherent and the target boundary is satisfied.

This keeps OMI portable, keeps the richer design intent close to the reviewed
artifact, and avoids depending on design-to-app runtime behavior or hidden local
paths.
