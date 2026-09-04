# ODC App-Shell First Scaffold

Use this guide when the user wants an app-shell first scaffold: the first-pass
entities, static entities, roles, screens, relationships, actions, and Mentor
Studio prompts for a blank app shell, a product-template shell, or a newly
created app shell that already has a verified app key.

This mode extracts the reusable shell-first knowledge from tested scaffold
workflows, but it keeps ownership inside `outsystems-mentor-implementation`.
Any reviewed specification workflow may feed this mode; do not depend on
`outsystems-spec-driven-build`.

## Boundary

Mentor Studio modifies an existing app shell. It needs a concrete target app,
normally identified by a readable app name plus canonical `APP_KEY` or
`assetKey`, before it can safely prepare or execute app-specific changes.
Mentor Web remains the official surface for prompt-to-app and
requirement-document-to-blueprint generation. It is no longer the only way to
obtain a usable target: since 0.14.0 `app_create` mints a template-backed shell,
so the shell-first path — create the shell, then scaffold it with Mentor Studio —
is complete end to end without leaving MCP.

This mode is valid when:

- the user has an existing empty or near-empty ODC app shell
- the user has a newly created shell and wants the first implementation pass
- the user has a verified Studio-created product-template shell and wants OMI
  to scaffold user screens and business logic without replacing shell assets
- the user provides a reviewed spec, PRD, patched implementation plan, or other
  source artifact and asks to scaffold it inside a known shell

For visual-source first scaffold work, the enriched blueprint contract in
`references/odc-visual-source-enriched-blueprint.md` is still the first step.
This guide consumes that artifact afterward for shell approval and boundary
handling once the shell already exists or explicit approval to create it has
been given. Reuse the blueprint only after the shell boundary is satisfied; do
not treat the blueprint as implicit permission to create, publish, or mutate
anything.

This mode is not valid when:

- there is no app target and no approved shell-creation path
- the request is only a Mentor Web requirement packet or blueprint-refinement
  task
- the target is a template/sample app rather than an owned implementation shell

Do not use `Template_*`, `template_*`, or `OutSystems Sample Data` as the shell.
Naming a custom tenant template as the `template` argument of an `app_create` is
a different thing and is legitimate: it clones that template into a new owned
app rather than building inside the template itself.
Do not call `app_create`, `mentor_create_asset`, `mentor_prompt`,
`mentor_publish` (or the pre-2026-09 `mentor_start` / `publish_start`), or mutate
a tenant without exact current approval for the action, readable target name, and
canonical id when it already exists.

## Required Gate

Before producing a first-scaffold Mentor Studio prompt, prove or ask for:

- target app name
- verified app key (`APP_KEY` / `assetKey`)
- environment or tenant context when more than one target could match
- shell classification: product-template shell, ODC manual empty shell,
  intentionally empty shell, blank shell, template-incomplete shell,
  or unverified shell
- whether the app shell is intentionally empty/new, not a template or sample
- whether the source artifact is reviewed enough to drive first-pass structure
- whether Mentor execution is only a prompt artifact or is explicitly approved

If tenant inventory or cached tenant evidence is used to verify the shell,
open `references/tenant-context-guardrails.md` and include a Tenant Context
Packet. Use it for target identity only. The packet does not expand approval,
does not authorize tenant-changing actions, and does not prove exact Studio
internals.

If there is no shell, do not create one silently — but since 0.14.0 `app_create`
is a first-class way to originate one, not a last resort. With one compact
approval gate covering the readable app name, the `kind` or `template` being
requested, environment context when needed, and the exact create action, OMI can
mint a template-backed shell directly. After creation, run the Shell Provenance
Gate and echo the canonical app key before preparing app-targeted prompts. If
the user would rather create it themselves, stop at setup guidance and hand them
the ODC Portal/Studio path instead.

If a shell does not exist, OMI may describe the shell setup path, but it must
not create the shell automatically. Any `app_create` path requires explicit
current approval for the readable app name, environment context, and exact
action. Do not turn that into extra ceremony when the user intent is already
clear. Create once approved, then verify and echo the canonical id after
creation. Mentor Studio first-scaffold prompts remain blocked until the shell
and app key are verified.

## Shell Classification And Entry Conditions

For app-shell first scaffold asks such as "blank app shell", "first scaffold", "bootstrap the first entities/roles/screens", or "use this reviewed spec against this app key", use this skill after the target app shell exists and the canonical app key is verified. Open [source-map.md](source-map.md) first. For non-visual scaffold sources, continue to this guide and then the Mentor hardening guide before producing output. For visual-source first-scaffold sources such as Figma, screenshots, or HTML mockups, build or validate the enriched blueprint first and let the scaffold guide consume that artifact for shell approval and boundary handling before UI discipline and generation. Mentor Studio modifies an existing app shell; Mentor Web remains the official prompt-to-app surface, though since 0.14.0 `app_create` can mint the template-backed shell that Mentor Studio then scaffolds. Any reviewed specification workflow may feed this mode; do not depend on `outsystems-spec-driven-build`. When the user asks to create a new application correctly, classify the target as a product-template shell, ODC manual empty shell, blank shell, template-incomplete shell, or intentionally empty shell before prompt generation; absence of the `Common UI flow` is a template-shell gap only when the target is expected to be product-template-backed; for an ODC manual empty shell, missing `Common` and other template assets may be blank-shell evidence, not a defect by itself.

## Product-Template And Empty-Shell Classification

**`app_create` mints a template-backed app by default (ODC MCP 0.14.0,
2026-08-18).** The rule this file carried before that date — that the call took
only `name`, `kind` and `oml_b64`, had no template parameter, and therefore
produced a bare shell by construction — described the pre-0.14.0 server and is
retired. The create now clones the kind's standard ODC application template, the
same path the ODC Studio new-app wizard uses, so a Studio-equivalent shell
(theme, `Layouts`, `Common` with its authentication screens, an `OutSystemsUI`
reference) is reachable from one approved MCP call. GAP-10 (2026-07-14) and the
2026-08-09 loop failure — a run that reached the screens phase before anyone
noticed the app had no theme, no `Layouts` and no `Common`, therefore no Login
screen and no way to reach the role-restricted screens it had just built — are
still the reason the provenance gate below exists. They are no longer a reason
to refuse `app_create`.

Verified input surface (`required: ["name"]`, `additionalProperties: false`):

| Param | Type | Notes |
| --- | --- | --- |
| `name` | string, required | Non-empty. Normalised — see the collision trap below. |
| `kind` | string enum | `CrossDevice`, `Mobile`, `MobileLibrary`, `ReactiveLibrary`, `ExternalConnection`, `ExternalLibrary`, `ModelPlugin`, `BusinessProcess`, `AIModelConnection`, `SearchServiceConnection`, `AIAgent`, `MCPConnection`, `A2AConnection`. Defaults to `CrossDevice`. |
| `template` | string | Aliases `Web`, `Mobile`, `MobileUI`, `Agent` (case-insensitive), or a custom tenant template asset-key UUID. |
| `blank` | boolean | Forces the pre-0.14.0 bare shell. |
| `model` | string | AIModelConnection name or key to wire into an agent-template create. |
| `oml_b64` | string | HTTP transport only; stdio takes `oml`, a server-local path. |

Default template by kind: `kind` omitted or `CrossDevice` → `Web`; `Mobile` →
`Mobile`; `AIAgent` → `Agent`; every other kind resolves to no template, i.e. a
blank shell. Libraries have no template at all — pass `kind: ReactiveLibrary` or
`MobileLibrary` and expect a blank library.

Four traps. Each is a hard server bail, not a warning:

- **`kind` has no `Web` and no `Agent`.** Those are `template` values. Web is
  `kind: CrossDevice`; agent is `kind: AIAgent`. Reading the release note's
  "Web, Mobile, Agent" as kind tokens produces an invalid call.
- **`template` and `kind` are mutually exclusive** — the template determines the
  created app's kind, so passing both is rejected. `blank` combines with `kind`
  but not with `template`; `model` is invalid with `blank` and `oml_b64`;
  `oml_b64` is invalid with every other generation parameter.
- **The generated paths are not idempotent.** A repeat call with an existing
  `name` is rejected with `OS-APPS-40018`. Never retry a create blindly.
- **`template: MobileUI` skips the ODC role-cleanup pass** and returns a
  warning; its first publish can fail until the template's Grant/Revoke role
  actions are removed. Do not pick it casually.

Three consequences survive 0.14.0, because they are properties of the create
call rather than of the blank shell:

- `app_create` normalises names by removing spaces, so `My App` registers as
  `MyApp` and collides with the name a Studio-created app needs — on 2026-07-14
  `Search Engine Sandbox NG` came back as `SearchEngineSandboxNG` and blocked
  the correctly-templated app that was supposed to replace it.
- There is no `app_delete` tool, and an app that has never been published is not
  visible in the ODC Portal — so cleaning up an unwanted create means publishing
  it first and then deleting it in the Portal. Budget for that before minting a
  throwaway.
- A blank shell's Default Theme dropdown offers only `(None)`, verified across
  two revisions, so "add a theme later" is not a recovery. This now applies only
  when `blank: true` was passed or the kind has no standard template.

### Shell Provenance Gate

Do not assert a shell is template-backed because the create was supposed to
clone one. Prove it, the way the digest and enumeration gates prove a publish:

- On create, record the returned `clonedFromTemplateKey`. Present = template-backed,
  and it names which template; absent = blank shell, whatever was intended.
  Record `warnings` and `wired` from the same payload.
- On a shell this session did not create, use read-only evidence instead:
  `app_refs` should show `OutSystemsUI` among the producers and `context_screens`
  should return the `Common` authentication screens. The 2026-07-14 bare-shell
  signature was the inverse — `(System)` as the only producer, `OutSystemsUI`
  absent, `context_screens --owned_only` returning 0 screens.
- If the server rejects `template` or `blank` as unknown properties, the tenant
  is running a pre-0.14.0 build. Fall back to the manual Studio path in the
  escalation ladder below and say so plainly. Do not proceed on a blank shell
  while reporting a template-backed one.

A create that intended a template and returned no `clonedFromTemplateKey` is a
failed create, not a usable target. That mismatch is exactly the 2026-08-09
failure, and it is cheap to catch at create time and expensive to catch at the
screens phase.

The rule is: classify a shell by evidence of what it CONTAINS, never by what
created it. "MCP-created" stopped being a synonym for "bare" in 0.14.0, and
"opened from ODC Studio" was never by itself a guarantee of template backing.
The official ODC documentation says app templates are starting points for
development and can define look and feel, common functionality, dependencies,
and user permission logic. It also documents editable pre-built authentication
screens under `UI Flows` > `Common`, including login, change password, recover
password, invalid permissions, and user profile; screen documentation separately
routes user screen creation through `MainFlow` and screen templates, and the
default screen through the `Mark as Default Screen` action.

ODC manual Web app creation can start from a valid empty shell. The current ODC
Getting started page says a Web app can be created by choosing `Continue in ODC
Studio`, which will "Open an empty app in the visual editor"; the Hello World
tutorial repeats the same path and says ODC Studio opens with an empty app.
Source:
https://success.outsystems.com/documentation/outsystems_developer_cloud/getting_started/.
A 2026-07-02 Documentation Assistant screenshot adds the practical
default-template clarification: there is no single preselected default
application template for this manual Web app path. Treat that as user-provided
evidence unless a current official page is fetched that says otherwise.

screen templates accelerate UI after the shell exists; they are not proof that
the app itself came from a preselected application template. The current ODC
Screen templates page says screen templates create screens with predefined
layouts, widgets, components, styles, logic, and sample data, and that ODC
Studio comes with default screen templates based on OutSystems UI. Source:
https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/user_interface/screen_templates/.
The same Getting started page also distinguishes custom app templates and Forge
templates as accelerators/foundations. Therefore manual Web app creation starts
from an empty app when the selected path is `Continue in ODC Studio`; screen
templates, custom app templates, and Forge templates are separate acceleration
paths, not a default-template guarantee.

Use the ODC custom app template page as the ODC-native authority for custom
template claims. In ODC, an ODC custom app template is a starting point for
developing an app. The page says a Custom app template is a starting point for
developing an app and can define look and feel, implement common functionality,
or manage dependencies. To be considered a template, the app name uses
`Template_<app_name>`, and the app needs a description and an icon. Publish to
make the template available in the templates list. When an app is created from
that template, further changes to the template do not impact that app, and the
new app inherits the template's colors. Source:
https://success.outsystems.com/documentation/outsystems_developer_cloud/app_architecture/create_a_custom_app_template/.
Treat an app created from an ODC custom app template as a product-template shell
only when user input, Studio inspection, or read-only tenant evidence says that
template path was used; do not infer it from the manual `Continue in ODC
Studio` path alone.

O11 Application Templates are useful as a platform-family evidence bridge for
why a Studio-created app is not the same thing as a bare app shell. The O11
Application Templates page says Service Studio bootstraps an app's modules from
the selected application template, giving apps predefined elements such as login
screens, theme, and layouts. It also says Reactive Web App, Phone App, and
Tablet App are built-in application templates that OutSystems creates and
maintains; those templates use OutSystems UI and let developers use the
compatible theme, patterns, screen templates, and other UI components. Source:
https://success.outsystems.com/documentation/11/building_apps/application_templates/.
Do not copy O11 built-in template names into ODC as exact ODC template names;
use the O11 page to reinforce the concept that normal Studio app creation is
template-backed, then verify the current platform's actual shell assets through
ODC docs, Studio, or read-only tenant evidence.

Classify the shell before first-scaffold prompt generation:

- `product-template shell`: read-only evidence shows normal Studio template
  assets such as a `Common UI flow`, authentication, profile, and
  password-recovery screens, `Layouts`, `Images`, `Themes`, `Scripts`, and
  expected UI framework references such as `OutSystemsUI`.
- `ODC manual empty shell`: the user chose the manual ODC Portal path
  `Continue in ODC Studio`, current docs/user evidence show an empty app is the
  expected starting point, and the app has no user screens or user-facing
  scaffold yet. Platform baseline assets such as `Common` may be present or
  absent in observed evidence; preserve them when verified, but do not require
  them from default-template assumptions alone. Do not classify an ODC manual
  empty shell as template-incomplete merely because Common is absent.
- `blank shell`: the app exists and may even have a `MainFlow` default screen,
  but read-only evidence or Studio inspection shows the normal product-template
  assets are absent. Reached by `blank: true`, by a `kind` with no standard
  template, or by any pre-0.14.0 create. Provenance does not classify it,
  evidence does — a 0.14.0 default create is template-backed, not blank, and
  this label must not be applied to an app merely because MCP created it.
- `template-incomplete`: the shell has some user-facing structure, but the
  expected product-template assets are missing, incomplete, or unverified.
- `intentionally empty shell`: the user explicitly accepts that the app is not a
  normal Studio-created template shell and wants a minimal scaffold anyway.

The OMI1/OMI2 campaign evidence is the regression example: `RequestPulse`,
created in ODC Studio, showed the `Common` flow and authentication template
screens; `OMISecondCampaignFixture` had `MainFlow` > `Home` as a default user
screen but lacked the `Common` template surface. That means a default `Home`
screen can prove the runtime-entry problem is solved while still leaving the app
template-incomplete.

If the user asks to create a new application correctly, first decide whether the
correct target is a template-backed shell — the 0.14.0 default, and usually the
right answer — an ODC manual empty shell, or a separate custom/Forge template
path. If the approved path is the manual ODC Web app path, an empty app shell is
acceptable after app-key verification; the first scaffold should create a
`MainFlow` user screen before expecting runtime default-entry proof. If the
expected target is product-template-backed and the only available target is a
blank or template-incomplete shell, stop before broad scaffold generation and
either:

- re-mint the shell template-backed with `app_create` under one compact approval
  — the cheapest remedy, and the right default when the blank shell holds no
  work worth keeping; mind the name-normalisation collision and the absent
  `app_delete` documented above before discarding the old one;
- ask the user to create the shell in ODC Studio and provide the verified app key
  — the fallback when the tenant predates 0.14.0, or when the existing shell
  already holds work that a re-mint would throw away;
- ask for explicit acceptance of the intentionally empty shell risk; or
- ask for a separate approved shell-normalization step.

The rule is: do not silently create authentication or password-recovery flows,
do not invent the contents of the `Common UI flow`, and do not repair a
template-incomplete shell as a side effect of unrelated screen, marker, or
publish work. If a prompt must proceed against a bare or intentionally empty
shell, record the missing template assets in `Unknowns And Fallback Behavior`.
A manual empty shell still cannot pass default-entry runtime proof until a
MainFlow user screen exists and is default.

### Web-Template Baseline Contents

What a template-backed Web app is expected to arrive carrying, so a
first-scaffold prompt stops telling Mentor to build assets the app already has. The rule above — do not
invent the contents of the `Common UI flow` — needs this list to be actionable.

**How strong each item below is, and why it matters.** The evidence is two
offline model-derived inventories of template-backed Web apps on two tenants
(one sprint-loop client app and one internal sandbox app, on two different
tenants; tenant, app and environment keys redacted), read 2026-08-26. Both were snapshotted
**after** Mentor scaffolding and neither is a live `app_refs`/`context_screens`
read — the verifying session had no authenticated MCP surface. Two
after-the-fact snapshots can show an asset is present in a template-backed app;
they cannot by themselves establish that the template is what put it there.
So only the first item below is stated as template contents — it has independent
documentation behind it — and the rest are **observed, not established**: use
them as what to expect and what to look for, and confirm against the target
before a prompt depends on them (Codex review of AH-2026-08-26-015 required this
split, 2026-08-26).

- **`Common` screens** — `Login`, `ChangePassword`, `RecoverPasswordRequest`,
  `RecoverPasswordReset`, `UserProfile`, `InvalidPermissions`. Exactly these
  six in both apps, and the same six the current ODC documentation names as the
  editable pre-built authentication screens under `UI Flows` > `Common`.
  Source: the ODC "Custom authentication flows" page, mirrored at
  `docs-odc` `src/eap/building-apps/ui/custom-auth.md` (read 2026-08-26; the
  live page is not machine-fetchable, so the mirror is the citable copy).

Observed in both apps, template attribution **unconfirmed** — expect these,
confirm them by reading the target:

- **`Common` blocks** — `Menu`, `MenuIcon`, `ApplicationTitle`, `UserInfo`.
- **`Layouts` blocks** — `LayoutTopMenu`, `LayoutBase`, `LayoutSideMenu`,
  `LayoutBaseSection`, `LayoutBlank`.
- **References** — `OutSystemsUI`, `OutSystemsCharts`, `OutSystemsMaps`,
  `(System)`. Identical set in both apps. `OutSystemsUI`'s presence is the one
  the Shell Provenance Gate above already keys on.
- **Role** — exactly one persistent role, named after the app itself
  (`ElasticSearchSandbox` in the sandbox app), with the `Common` screens wired
  to it. **Settled 2026-09-03** by a `context_roles` read on a freshly
  template-scaffolded throwaway app: exactly one role, and its name was the
  app's own name with the punctuation stripped — not `Template_WebApp`. The
  post-create-rename doubt is closed: the template's own role IS the sanitized
  app name. Still read the role name before writing a prompt that references it,
  and do not create a second app role.

**Measured 2026-09-03** (`context_themes` on the same freshly scaffolded app;
supersedes the AX-team report of 2026-08-25/26, which named the theme
`Template_WebApp`): the theme is `TemplateApplication`, carrying a base theme,
layout `LayoutTopMenu` and pre-set brand colours. A separate `EmailTheme` also
exists. The report's `LayoutTopMenu` claim held; its theme *name* did not. Still
confirm with a live read before naming a theme in a prompt — the name is the part
that moved, and it is the part prompts get wrong.

Consequence for a first scaffold, and it holds at every confidence level above:
**read the target's own screens, blocks and role before prompting, and prompt
only what the read does not already show.** In practice that means the prompt
carries the user screens, entities and logic, and does not create
authentication screens, layout blocks, a menu block, an `OutSystemsUI`
reference, or an app role. Style changes go to the existing app theme once its
real name is read back, never to a new theme. The read is what makes this safe
— none of it depends on the list above being complete.

## Output Contract

For app-shell first scaffold work, use these sections before any normal
Studio-native pseudocode sections:

### Manual Setup Gate

List shell prerequisites and mark each item:

- `verified`
- `manual-only`
- `blocked-until-manual-setup`

Include the app shell creation/verification state, product-template shell
classification, retrieval-stack state, source-artifact review state, and whether
any action is approved. If the shell is missing and no create action is
approved, the app key is not yet verified, or the app is template-incomplete
without acceptance or a separate approved shell-normalization step, stop here
and do not emit a Mentor Studio execution prompt.

### App Shell Target

Name the target app and canonical id. State whether the app shell is a
product-template shell, a blank shell, template-incomplete, newly created, or an
existing shell being treated as first-scaffold work. When the shell was created
this session, report the Shell Provenance Gate result with it — the returned
`clonedFromTemplateKey`, or its absence. Explicitly say when the shell status is
unverified.

Do not target a template, sample, or ambiguous app. If multiple app rows match,
ask the user to choose the exact one before proceeding.

### First Scaffold Coverage Checklist

Map the reviewed source artifact into first-pass ODC structure:

- data model: entities, static entities, required attributes, identifiers,
  indexes or uniqueness expectations when known
- roles and permissions: app roles, anonymous/authenticated behavior, access
  checks, admin-only areas
- UI flows and screens: initial flow, screen names, blocks, navigation,
  layouts, empty/error/loading states
- data producers: aggregates, data actions, server actions, consumed REST calls,
  external dependencies, and data-bound widgets that need a source
- write paths: create/update/delete actions, validation, transaction boundary,
  audit behavior, and failure behavior
- integrations and agents: connectors, AI model calls, agent calls, external
  tools, guardrails, and portal prerequisites
- verification: TrueChange expectations, manual checks, functional acceptance
  checks, and unresolved unknowns

Keep uncertain requirements in `Unknowns And Fallback Behavior`; do not invent
exact Studio elements when the source artifact does not support them.

When the source artifact is a visual-source enriched blueprint, use its
blueprint-derived prompt packet only as preparation or a condensed summary for
this checklist and later review notes. Do not insert a mandatory extra visible
packet section before the normal OMI prompt output contract.

### Mentor Studio First-Scaffold Prompts

Emit paste-safe prompts only after the setup gate and app target are verified.
Each prompt must:

- name the target app and verified app key
- say this is a first scaffold inside an existing shell
- create producers before consumers
- create entities/static entities/roles before screens that depend on them
- create actions/data actions/aggregates before binding widgets to them
- avoid publishing, deploying, or external promotion
- ask Mentor to leave unrelated shell assets unchanged
- preserve verified product-template assets, especially `Common`, `Layouts`,
  `Images`, `Themes`, `Scripts`, and UI framework references
- include a post-generation review checklist for Studio validation

Prefer one bounded prompt per coherent generation slice when the scaffold is
large. Example slices are data model and roles, main navigation and screen
shells, first data-bound screen, integration stubs, then review fixes.

## Iterative App Identity And Delta Discipline

For iterative shell-first reruns, reuse the same canonical app key; do not call `app_create` again
for the same logical app unless the user explicitly asks to
create a separate app.

Before writing a follow-up prompt, classify source sections as:

- `unchanged`: preserve existing implementation and do not restate the full
  construction
- `changed`: describe the exact delta to apply
- `new`: create after required producers exist
- `removed`: remove only when explicitly approved

When resuming with a `mentor_session_token`, write a delta prompt that focuses
on what changed instead of replaying all previous work. If the new work depends
on unpublished prior Mentor changes, state the publish/session baseline risk in
Unknowns And Fallback Behavior. No implicit publish.

When the scaffold source requires non-default shared chrome, review whether
chrome should be handled as its own batch before screen work rather than being
buried inside screen-level prompts.

## Post-Mentor Preservation Decision Gate

After an approved Mentor execution succeeds, stop and ask which preservation
route the user wants:

- publish to a specific environment, requiring explicit current approval before
  `mentor_publish` (pre-2026-09: `publish_start`) unless the current request
  already clearly approved implementation plus publish to that exact environment.
  `mentor_publish` ships to the connected dev environment and takes no
  environment argument, so "that exact environment" is the session's own; any
  other target is a separate, separately approved `deploy_start`
- stop with the open session's `sessionId` and its idle-expiry risk recorded
  (pre-2026-09 this was the newest Mentor session id/token pair)
- create a prompt-only handoff for manual ODC Studio review

No mandatory publish. No implicit publish. No duplicate publish confirmation
when the user already clearly approved publish to a specific environment. No
production promotion from this skill.

## Safety Notes

- Treat shell creation as a separate approved action, not an implicit side
  effect of prompt generation. Keep the approval compact when creation intent is
  already clear.
- Treat shell normalization as a separate approved action. Missing Studio
  template assets are not fixed by a generic first-scaffold prompt.
- Treat Mentor execution as interpretive, not deterministic. Even a strong
  prompt requires Studio review.
- Use the Mentor hardening guide for SQL, data writes, JSON Deserialize,
  status/static-entity values, screen targeting, button OnClick wiring,
  container reparenting, producer-first UI generation, and data-bound widget
  sources.
- For true app generation from a requirement document without a shell, route to
  Mentor Web guidance in `references/agentic-routing.md`.
