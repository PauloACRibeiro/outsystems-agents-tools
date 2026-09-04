# ODC Platform Guardrails

> ODC error codes: see `../../shared/reference/odc-error-registry.md` for the canonical index of every code named below.

Use this OMI-owned reference when a prompt or pseudocode block touches
platform-level risk: architecture layering, public services, security-sensitive
server calls, query performance, timers/background processing, or public API
contracts.

This reference is read-only prompt discipline. It does not authorize
`app_create`, does not authorize `mentor_create_asset`, `mentor_prompt` or
`mentor_publish` (nor the pre-2026-09 `mentor_start` / `publish_start`), and does
not authorize deploy, rollback, cleanup, or tenant mutation. It does not replace current official docs, `outsystems-tech-content`,
or ODC Portal impact analysis.

Ground this guidance in current OutSystems public documentation before making
product-contract claims. Use `outsystems-tech-content` when available for
current Studio syntax, function signatures, widget rules, TrueChange messages,
and implementation-level authority.

This reference does not require any sibling architecture skill and does not
require a graph, HTML report, script, client-specific cache path, fixed filename,
or fixed JSON shape.

## Entry Routing

For platform guardrail-sensitive requests involving architecture layering,
public services, server trust, anonymous or registered access, query
performance, timers, background processing, async retry, imports, bulk work, or
public API contract changes, open [references/source-map.md](source-map.md)
and [references/odc-platform-guardrails.md](odc-platform-guardrails.md)
before producing output. Apply the Architecture Layering Gate, Security
Server-Trust Gate, Performance Query Pre-Mortem, Timer / Async Idempotency Gate,
or Public API Contract Gate as applicable.

Apply the User Reference Authoring Gate in addition whenever the design
touches the platform `User` entity.

Apply the Not-Found Guard Gate in addition whenever an action takes a record id
from outside itself — update, cancel, delete, detail — or whenever the symptom
is **a 500 on a missing row**, **a delete that reports success for a row that
never existed**, or **a not-found refusal that never fires**.

Route onward when the symptom is Mentor **silently rewriting** what the prompt
asked for — most often a Server Action auto-renamed because the entity already
carries an action of that name. For that class, this file is not the owner:
open [references/odc-mentor-hardening.md](odc-mentor-hardening.md), which holds
the rule in full with its dated session evidence, and resolve the publish code
through the index in `../../shared/reference/odc-error-registry.md`. Do not
restate that rule here — a second home whose meaning drifts from its owner's
text is what the registry calls a lint finding.

## Gate Precedence

The gates below are written to compose, and in nearly every design they do —
each covers a different risk. This section is for the case where two that both
apply prescribe different constructions, because the order they happen to
appear in this file was never chosen to settle anything, and adjacency is not
an answer.

**A gate carrying measured platform-refusal evidence outranks an advisory
design gate.** A gate counts as evidence-backed here only when this file
records a dated observation of the platform itself refusing, reverting, or
renaming the construct — not when it records a strong design preference.
Advisory gates say what a good design does; evidence-backed gates say what this
platform will not accept, and a design already measured as rejected does not
become buildable because another gate prefers it. Precedence settles the
*construction* only. It never waives the losing gate's requirement: that
requirement stands and must be met another way, and where it cannot be, the
result is a stop, not a trade.

**Two advisory gates in conflict do not have a winner.** Where neither side
carries platform-refusal evidence, do not pick one. Name both outcomes, say
which gate asks for each, and stop for a decision. The conflict is a real
design choice, and settling it quietly hides it from the person entitled to
make it.

**The one conflict measured so far.** The Security Server-Trust Gate requires
server-side identity and ownership on sensitive reads and writes, which points
a design straight at a `User`-typed attribute or a foreign key into `User`. The
User Reference Authoring Gate records that Mentor cannot author that reference:
three publishes of one app differing only in it went fail, fail, succeed on the
first live colleague sprint-loop run (2026-08-09). The authoring gate takes
precedence, because its side is a measured platform refusal while the security
gate's claim on the mechanism is a preference. What it wins is narrow — the
reference is authored in ODC Studio as a `Manual Setup Gate` row and Mentor
carries it from there. The security requirement itself is untouched: identity
is still derived server-side with `GetUserId()`, and ownership is still
enforced in server-side logic.

**Maintenance.** Add to this section only when a conflict has actually been
observed between two gates in this file, and only together with the evidence
that settled it; a conflict reasoned about but never met belongs here in no
form. What is recorded is not a ranking of the gates — a gate that takes
precedence over another on one construct carries no standing on any other.
Scope is this file's gates only. The precedence statements that already exist
elsewhere are untouched and are not this: `SKILL.md`'s Routing Table gives
`references/odc-mentor-hardening.md` priority over general rules on conflict,
and the source-precedence sections of the language-elements and
implementation-context guides rank sources. The nearest neighbour,
`references/execution-gates.md` §3b, says which *signal* answers which question
at publish time — `modelDigest` reports that the model changed, terminal deploy
state reports that the deployment succeeded, and neither substitutes for the
other — which is signal authority, not gate precedence.

## Architecture Layering Gate

Use this gate before OMI suggests reusable services, entities, public actions,
shared libraries, or cross-app dependencies.

Check:

- producer/consumer layer fit: the producer should belong below the consumer in
  the intended architecture direction.
- lifecycle independence: avoid references that couple applications or teams
  unnecessarily.
- one clear owner: do not place shared public services in an application with
  unclear or mixed ownership.
- sponsor or line-of-business boundary: isolate different sponsors or lines of
  business when their change pace differs.
- service exposure intent: Orchestration and End-user areas should not become
  generic service providers.
- foundation isolation: Foundation assets should not depend on business-specific
  Core assets.
- cycles: stop if the proposed dependency creates or reinforces a cycle.

Treat Orchestration, End-user, Foundation, and Core as application-composition
heuristics from public layering guidance, not as exact ODC runtime artifact
types.

Fallback behavior:

- If layer fit is unknown, add an `Unknowns And Fallback Behavior` item instead
  of emitting a confident dependency instruction.
- If the change touches a shared producer, also apply the existing Shared
  Producer Compatibility Gate in `tenant-context-guardrails.md`.
- If architecture-style or existing-app structure evidence is supplied, reduce it
  into OMI-owned evidence first. Do not require the producing tool, graph, report,
  cache path, or fixed data shape.
- If the supplied structure evidence is tenant-backed or names an existing app,
  run the Tenant Context Packet and Target App Resolution Gate in
  `tenant-context-guardrails.md` first, then reduce the result into OMI-owned
  evidence.

### Settings are read-only at runtime — mutable state is an entity

`Current official`: *"Settings are read-only at runtime. You can only update
the value of a setting through the ODC Portal, which will then run an
asynchronous process to update the runtime configuration of your app"*
(`OutSystems/docs-odc:src/eap/building-apps/data/data-best-practices/intro.md`).

So a Setting is deploy-time and operator-time configuration, never a value a
flow writes. Two consequences for placement:

- **Never emit a prompt that writes a Setting from a logic flow.** There is no
  ODC action for it. When a capability needs state that changes while the app
  runs — a counter, a toggle a user flips, anything a screen action updates —
  the state belongs in an **entity attribute**, not a Setting.
- **A "feature flag" splits by who flips it.** Settings are the documented
  home for feature-toggle flags that an operator changes per stage through the
  Portal. A flag the *application* flips at runtime is not that, and modelling
  it as a Setting produces a design that cannot work. Decide which one the
  requirement means before emitting either.

Settings remain correct for what they are documented for: application-wide
values that do not change frequently, secrets marked as such in Studio, and
per-stage configuration.

### A foreign key across an app boundary supports only `Ignore`

`Current official`: for a relationship between entities of different apps,
*"the only supported Delete Rule for the foreign key attribute is Ignore"*
(`OutSystems/docs-product:src/migration-to-odc/code-patterns/elem-unsupported-delete-rule.md`).
Within one app the same property defaults to `Protect` and all three values are
supported
(`OutSystems/docs-odc:src/eap/building-apps/data/modeling/relationship/relationships.md`).

The rule is about the app boundary, not about identifier references:

- **Same-app foreign key: leave `Protect` alone.** It is the platform default
  and it publishes. Never emit an instruction that rewrites a same-app delete
  rule to `Ignore` for publish safety — that is a real constraint applied at
  the wrong scope, and it silently drops the referential integrity the design
  asked for.
- **Cross-app foreign key: emit `Ignore`, then enforce integrity in logic.**
  No database constraint exists across the boundary, so a parent delete leaves
  orphans. When the design needs `Protect` behavior, pair the reference with a
  server-side check that refuses the delete while related records exist and
  returns a reason; when it needs `Delete` behavior, delete the related records
  explicitly first.

Unmeasured, so do not assert it either way: whether a cross-app `Protect`
reaches publish and fails with a named code, or is coerced to `Ignore` the way
the O11 conversion tool rewrites it. Cite no error code for this rule until
someone measures it.

### Reuse crosses an app boundary as a Service Action, a library boundary as a Server Action

`Current official`: a Service Action *"is a REST-based remote call to another
process"* exposed by an app, creating a weak dependency
(`OutSystems/docs-odc:src/eap/app-architecture/service-actions.md`). A library
is the other case: dependencies on libraries *"are always strong dependencies.
The producer's code is necessary for compiling the app"*
(`OutSystems/docs-odc:src/eap/building-apps/reuse/intro.md`), and the ODC
library element table lists Server Action and Client Action under `Logic` with
no Service Action row
(`OutSystems/docs-odc:best-practices/.../o11-migration/code-elements-reference.md`).

So the boundary decides the element, and OMI should not emit the other one:

- **A library's public surface is public Server Actions.** Never emit a prompt
  that creates a Service Action inside a library; the reusable-logic element a
  library exposes is a Server Action, consumed by compiling it into the caller.
- **An app's cross-app surface is Service Actions.** A second app calls into an
  app through a Service Action, not by reaching for its internal Server Actions.
- **Cross-app entity access is read-only.** Current best-practice guidance
  states that *"Public Entities referenced between ODC applications can only be
  read. Writes need to be refactored into Service Actions in the owning app"*
  (`OutSystems/docs-odc:best-practices/.../o11-migration/code-patterns.md`). So
  a design that has app B creating or updating app A's rows is emitted as a
  Service Action on **A**, never as B calling A's generated entity actions.

**Measured, and the refusal is structural rather than a publish failure.**
Observed on tenant 2026-08-27 (app `98c8428a` rev 5, consuming another app's
public entity): the consuming app is offered exactly one entity action on that
entity — the `Get<Entity>` read — and no `Create`, `CreateOrUpdate`, `Update`
or `Delete` action is exposed to it at all. The consumed entity carries
`ExposeReadOnly = True`, and the write action slots (`CreateAction`,
`CreateOrUpdateAction`, `UpdateAction`, `GetForUpdateAction`, `DeleteAction`,
`CreateOrUpdateAllAction`, `DeleteAllAction`) are null — never imported. The
same app's own entity, read in the same turn as a control, carries all eight.
So the write is not something that
validates locally and then fails on publish; it is something that cannot be
written down in the consumer in the first place. Validation stayed at zero
errors precisely because there was no write to express.

Say it that way. A prompt that warns a reader the write "breaks at publish" is
telling them to expect a failure they will never see, and sends them looking
for an error code that does not exist.

### Publish producers before consumers, and say which dependency kind it is

`Current official`: for a strong dependency *"the consumer needs to refresh the
dependency on the producer and to be republished"* when the producer's
signature or implementation changes; for a weak dependency a producer change
*"becomes immediately available to all consumers without requiring a new
compilation and deployment of the consumer"*
(`OutSystems/docs-odc:src/eap/building-apps/reuse/intro.md`). A consumer
deployed without its producer is a named deployment inconsistency, `Missing app`
(`OutSystems/docs-odc:src/eap/deploying-apps/deployment-inconsistencies.md`).

- **Order every multi-asset emission producer-first**, and say so in the
  session plan: libraries before the apps that compile them, an owning app
  before the app that calls its Service Action.
- **A signature change on a library is a consumer republish**, not just a
  producer publish. Name the consumers in the plan or record them unknown.
- **A signature change on a Service Action is not.** Weak dependencies pick up
  the new implementation without a consumer publish, so do not emit a
  republish-everything step for one.

### Entity creation and data movement follow FK-topological order

Order is not cosmetic here: a child row written before its parent exists has no
value to put in its foreign key. So any emission that creates entities, seeds
reference data, or moves data incrementally is ordered parents-first:

1. static entities and reference data — nothing points out of them;
2. independent aggregate roots — entities with no outbound foreign key;
3. dependents, shallowest first, deepest last.

**Mentor does not do this on its own.** Our own estate observation is that
Mentor's entity emission order is not FK-topological, so the order has to be
stated in the prompt rather than assumed from the plan's section order.

Where a design moves data incrementally rather than seeding it once, the
checkpoint contract is part of the design, not an implementation detail:

- **Store the run's start time as the watermark**, not its end time, so a
  record changed while the run was in flight is picked up next run instead of
  being skipped.
- **Advance the watermark only after the batch is validated, written and
  audited.** A watermark advanced on entry turns one failed run into permanent
  silent data loss.
- **Resolve every incoming reference by its external key to a local
  identifier.** Never write a provider's key straight into an identifier
  attribute, and never invent one.

This is design-level ordering and state, adopted as a pattern. The three-module
sync architecture it comes from is not adopted.

### Give an entity at most one Binary Data attribute

**The actionable rule is public and unconditional**: put each binary attribute
in its own entity. Do that and the design is right whether or not the limit
below applies to your platform, so treat this as the instruction and the
validation as the reason it is not merely advice.

A compiler validation on file says the one-per-entity limit is hard rather than
advisory: *"{0} can only have one attribute of 'Binary Data' data type"*
(`Invalid Entity`). Read the scope carefully — see **Evidence** below. If it
holds for ODC, a data model giving one entity both a photo and a signed
document is rejected at validation time, and the cost of assuming it holds when
it does not is zero, because the public guidance asks for the same shape.

The remedy is the one the public best practice already asks for. ODC's *Best
practices for data management* says to **"isolate binary data attributes in a
separate entity"**, because fetching and updating an entity that carries binary
data is heavy and the cost lands on every read of the parent
([best-practices-for-data-management](https://success.outsystems.com/documentation/outsystems_developer_cloud/building_apps/data_management/best_practices_for_data_management/)).
One binary attribute per entity, in its own entity, satisfies the limit and the
performance guidance at once — so a design needing two binaries needs two
entities, each referencing the parent, not a wider parent.

Two adjacent validations worth stating in the same breath, from the same
catalog: a `Binary Data` attribute **cannot participate in an entity index**
(`Invalid Entity Index`), and an entity carrying one should have its **Update
Behavior set to 'Changed Attributes'** (`Scalability Suggestion`) so an update
that does not touch the binary does not rewrite it.

**Evidence, and its one soft joint.** The isolation practice and its rationale
are **public and ODC-specific**, cited above. The three quoted validations are
not: they come from the `model-truechange` collection via
`outsystems-tech-content` (retrieved 2026-09-03), which publishes no public URL,
so they are entitled access rather than `Current official` — the same evidence
class as the `Destination` / `Download` Screen-Action restrictions in the
Language-elements handbook §3.7.

The soft joint is the platform scope. `outsystems-tech-content`'s own catalogue
tags that collection as applying to **both O11 and ODC**, and that tag is a
property of the *collection*, asserted by the server — not a statement inside
any message, and the tool exposes no per-message platform scope at this
revision. So the ODC applicability of the limit is **reported, not
established**, and this rule does not rest on it: the instruction above is the
public practice, which stands either way. Do not cite the limit as a settled
ODC platform bound elsewhere without stronger evidence. The catalogue output is
recorded verbatim in `docs/adoption/evidence/oros-refactoring-spec-disposition/
tech-content-collections-2026-09-03.md` so the claim can be audited without
re-running the tool.

### Folders are per-area, so one concept name is several folders

Current best-practice guidance organizes folders *"by application concept"* and
applies that *"to all element types in ODC Studio"*, with the worked example
showing the same concept name repeated as a separate folder under `Interface/`,
`Logic/`, `Data/` and `Processes/`
(`OutSystems/docs-odc:best-practices/.../architecture/naming-conventions.md`).

So when a prompt places an element in a folder, the folder is named **within
its area**: a `Logic` folder cannot hold a screen, and asking for "the
`Billing` folder" without saying which area names up to four different folders.
Emit the area with the folder name.

**Measured, so a prompt may rely on it: a folder's area is fixed at creation.**
Observed on tenant 2026-08-27, app `98c8428a` rev 3 — a folder created in the
`Logic` area could not be relocated to `Interface`. The model's `ParentFolder`
property carries a getter and no setter, and the model exposes no move
operation at all; two independent Mentor sessions report the same. So an
element placed under the wrong area is not repaired by moving its folder
afterwards. Name the right area when the folder is first created.

The measurement is of the ModelAPI surface Mentor drives, which is the surface
these prompts reach. Whether ODC Studio's own UI offers a cross-area move was
not observed, so do not assert anything about the Studio gesture.

## Security Server-Trust Gate

Use this gate when OMI writes role-sensitive UI, anonymous or registered access,
client actions calling server actions, exposed REST, consumed REST with
credentials, or any operation that reads or mutates sensitive data.

Check:

- server-side authorization: sensitive reads and writes need validation in
  server-side logic.
- do not trust hidden or disabled UI controls: visibility and enabled state are
  user experience hints, not authorization.
- do not trust client-passed identity: derive user identity on the server side
  for server-side authorization and data filters.
- anonymous or registered access: state when a screen, REST endpoint, or action
  is public, authenticated, or custom-role restricted.
- input validation: validate externally supplied IDs, filters, status
  transitions, and ownership on the server.
- output minimization: do not expose sensitive system/user data unless the role
  and use case justify it.
- REST security: exposed REST endpoints need authentication and
  transport/security assumptions stated when relevant.
- no entity action on the client side: a Client Action or Screen Action must not
  call a generated entity action (`Create<E>`, `CreateOrUpdate<E>`, `Update<E>`,
  `Delete<E>`) directly. Wrap it in a Server Action that validates first, and
  call that. The naming for those wrappers is in `odc-mentor-hardening.md`.

### The compiler states this one

Exposing a database operation client-side is not only a design preference — it
raises `Security Warning . You're exposing a database operation in the client
side. Validate the data in a Server Action before changing the database.` Write
the wrapper because the platform asks for it, and note that the platform's own
remediation names *validation*, not merely indirection: a pass-through Server
Action that adds no validation satisfies the compiler but not the gate.
Local storage entity actions are exempt: calling them from client actions is
the standard offline-app pattern, and the platform's "Database operation in the
client-side logic of a screen" Code Quality finding states that exclusion
explicitly ([database-operation-in-client-side.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/monitor-and-troubleshoot/manage-technical-debt/security/database-operation-in-client-side.md), verified 2026-08-27).

Two adjacent warnings share this shape and are worth planning against: a Server
Action reachable from a screen carrying the Anonymous Role raises `You're
exposing a Server Action for public access and without authentication`, and a
Client Action calling several Server Actions raises a Performance Warning
directing you to group them into one.

Fallback behavior:

- If explicit role evidence is missing, use the Role/Security Evidence Gate in
  `tenant-context-guardrails.md`.
- If server-side authorization cannot be specified, stop and ask for the policy
  instead of relying on UI-only restrictions.

### An SQL element takes parameters; `Expand Inline` is the risk

`Current official`: ODC *"uses prepared statements by default"* and *"uses an
SQL parameter for every Query Parameter that has the `Expand Inline` property
disabled. The system disables this property by default"*; enabling it means the
value is no longer handled as a parameter and *"your end-users may exploit
this"*
(`OutSystems/docs-odc:src/eap/monitor-and-troubleshoot/manage-technical-debt/security/sql-injection.md`).
The SQL-element guidance says to *"incorporate input parameters to pass values
into your SQL queries, enhancing security and preventing SQL injection
vulnerabilities"*
(`OutSystems/docs-odc:src/eap/building-apps/data/fetch-data/sql/use-sql.md`).

Whenever OMI emits an SQL element whose text depends on anything a user
supplied:

- **Pass the value as a Query Parameter and leave `Expand Inline` at its
  default `No`.** That is the whole rule for a value — a filter term, an id, a
  date. Never emit a prompt that concatenates a user-supplied value into the
  query text.
- **`Expand Inline = Yes` is only for an SQL fragment**, such as a
  caller-chosen sort direction, and it needs a named justification in the
  prompt. Where the fragment comes from a fixed set, emit the set as a switch
  over literals instead, so no user text reaches the statement.
- **When `Expand Inline` is unavoidable, encode string literals with
  `EncodeSql()`** — never with `Replace`, which the same source calls
  *"prone to errors"* — and encode **the literal only**. Wrapping a whole
  clause, as in `EncodeSql("WHERE surname = " + @a)`, is called out as a
  pattern that *"is often wrong, so you get a warning if you use it."*
- Prefer an Aggregate where one will do. The default data element carries none
  of this exposure.

The `Sanitization` library's `BuildSafe_InClauseTextList` is already cataloged
in `odc-studio-language-elements.md`; use it for an `IN` clause built from a
list rather than assembling the list into the query text.

## User Reference Authoring Gate

Use this gate whenever a design touches the platform `User` entity: a User
Identifier attribute, a foreign key into `User`, an aggregate over `User`, or
any element whose creation would add a `User` reference to the app.

The distinction is authoring versus carrying, and it is the whole gate.
Mentor carries an existing User reference through a publish without trouble.
It fails when it authors one. Measured on the first live colleague
sprint-loop run (2026-08-09): three publishes of the same app differing only
in a `User` reference went fail, fail, succeed, and succeeded the moment the
User-typed attribute and the seed's user lookup were removed; both failures
were `OS-DPL-50205` "Model features validation failed". The same attribute
added by hand in ODC Studio (User Identifier, optional, delete rule Ignore)
published first time, and a later Mentor publish carried that
Studio-authored attribute through untouched.

Check:

- author in Studio, carry with Mentor: a User-typed attribute or a foreign key
  into `User` is a `Manual Setup Gate` row for the human to add in ODC Studio
  before the session that needs it, never a Mentor create step.
- carrying is not authoring: once the reference exists, later sessions may
  read, write, and filter on that attribute freely.
- derive identity server-side with `GetUserId()` rather than reading the
  platform User entity; an aggregate over `User` is itself an authored
  reference and falls under this gate.
- classify the reference as already-conformant in the session's expected
  element delta, so the enumeration gate does not read a pre-existing
  attribute as drift.
- treat a recurring `ImplicitSelfUserProvider` warning as a hard check, not a
  dismissible note. In the same run it named the exact capability the design
  depended on and was explained away in near-identical words, session after
  session, by the agent that produced the work — a warning dismissed by its
  own author is a self-report. One check would have saved two failed publishes
  and three diagnostic sessions.

Fallback behavior:

- If it is unverified whether the target app already carries the reference,
  inspect the app before packaging and record `User reference state unknown`
  rather than emitting a create step on a guess.
- If the design needs a User reference and ODC Studio access is not available,
  stop and say so. No Mentor-side workaround for authoring has been measured.

## Not-Found Guard Gate

Use this gate whenever an action takes an entity identifier from outside itself
— a screen parameter, an API input, another action — and the row it names may
not exist. That is nearly every update, cancel, delete and detail action.

Three platform behaviours, all measured by execution against a live ODC
development environment (2026-08-11), and no two of them alike:

| Generated action | Missing row |
|---|---|
| `Get<Entity>ForUpdate(Id)` | **raises** |
| `Get<Entity>(Id)` | **raises** — byte-identical error to the locking read |
| `Delete<Entity>(Id)` | **returns silently**, no error at all |

**The first consequence: `If Id = NullIdentifier()` after a read is dead code.**
The read raises before the guard is reached, so the refusal branch can never
execute and the caller gets a 500 instead of the declared outcome. Three
instances of exactly this shipped in one generated app.

**The second consequence, and the one that catches reviewers: swapping the
locking read for the plain one is not a fix.** Both raise. A repair framed as
*"don't use `GetForUpdate`"* leaves an action that already uses `Get` equally
dead while reading as already-correct — measured, in the same app, on the
second of two dead guards.

**The third is the dangerous one.** A delete-shaped action has no broken guard
to find, because it has no guard at all: `Delete` does not raise, so the action
reports success for a row that never existed. It fails toward success — no
error, no log, and a test asserting `Outcome = "Success"` passes on a random id.

**The platform has no null except the Entity Identifier**: every type has a default value
assigned at creation (`""`, `0`, `False`, `#1900-01-01#`), and a missing optional input
reads as that default — so an "unset" value is its type's zero, never something to test
for truthiness. Existence of a row is decided by the aggregate-`Count` guard below, never
by inspecting a returned record. **An attribute's `Is Mandatory` is validated in the UI
only**; the column is created allowing NULL, so integrity a design relies on belongs in the
server action, not in the flag ([Data types](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/data/data-types.md) for the no-null rule and the
default-value table; [Entity](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/data/modeling/entity.md) for the
mandatory-is-UI-only rule).

### The construction that works

Aggregate first, guard on its `Count`, then the locking read:

1. Aggregate over the entity, filtered `<Entity>.Id = <input>` — existence only.
2. `If <aggregate>.Count = 0` → assign the refusal outcome, End. Nothing written.
3. `Get<Entity>ForUpdate(Id: <input>)` — the row existed at step 1.
4. Business rules → refuse or update.

The guard tests the **aggregate's `Count`**, never a returned record's `Id`. The
locking read stays exactly where it was; it simply stops deciding existence.
Aggregates return `Count = 0` for a missing row rather than raising — verified
independently in a second app — which is what makes step 1 usable as a guard.

**What this construction is verified to do, and what it is not.** It was
measured against a **sequential** missing-row call: an id that does not exist,
one caller, no competing writer. On that path it turns a 500 into the declared
refusal, repeatably, in two apps.

**Concurrency between steps 1 and 3 is unverified.** There is a window: the
aggregate can see a row that a concurrent delete removes before the locking read
runs, and step 3 would then raise exactly as the unguarded version did. Nothing
here has been measured under contention, and no transaction-isolation evidence
was gathered. So: **do not treat this as a race-free construction.** Where rows
can be deleted concurrently, keep exception handling around the read as well, or
establish the platform's isolation behaviour first. The gate removes a
guaranteed failure on a common path; it does not prove the path is safe under
every schedule.

Check:

- every action taking an identifier from outside declares a not-found outcome,
  **including delete-shaped ones**, where the omission is invisible;
- the existence check is an aggregate `Count`, evaluated **before** any read;
- the refusal returns the declared outcome and writes nothing.

Fallback behavior:

- **Verify by calling the action with an id that does not exist.** Static
  inspection cannot settle this: grepping for `NullIdentifier()` finds the dead
  guards and is structurally blind to the absent one, which is the more
  dangerous of the two. A coverage checker cannot see it either — it can only
  confirm the refusals a design declared, never the one it forgot.
- If an action cannot be executed (role-gated, no authenticated route), record
  its not-found behavior as **unverified**. A role-gated action probed through
  an unauthenticated harness answers *"Not authorised."* — a clean HTTP 200 that
  is easily mistaken for a correct refusal.

## Performance Query Pre-Mortem

Use this gate when OMI writes Aggregates, SQL, list screens, dashboards, loops
over data, bulk operations, exports, imports, or data-heavy Server Actions.

Check:

- Max Records or pagination: every list or search query should state the expected
  limit.
- Aggregate or SQL inside `For Each`: do not emit this pattern without a
  pre-mortem and a reason it cannot be refactored.
- fetch only the fields needed: prefer structures or narrowed outputs for
  large/wide records when passing data through actions.
- query count: prefer a single joined query over sequences of dependent queries
  when that reduces round trips without hiding important business logic.
- index candidates for filters and joins: list candidate entity attributes used
  in frequent filters, joins, or sorts; do not claim an index must exist without
  current evidence.
- bulk writes: use set-based SQL only when the operation is truly bulk-oriented
  and the validation/transaction boundary is explicit.
- linked/external data: avoid cross-server joins when the data source boundary is
  known.

Fallback behavior:

- If expected volume is unknown, add `Volume/performance unknown` to
  `Unknowns And Fallback Behavior`.
- If performance is not the main risk, keep the pre-mortem short and do not force
  premature optimization.

## Timer / Async Idempotency Gate

Use this gate when OMI writes Timers, wake actions, background processing,
imports, long-running calls, retry loops, queue/status/polling flows, or async
cleanup.

Check:

- idempotency key or progress marker: repeated execution must not duplicate work
  or corrupt state.
- checkpoint: record where processing can safely resume.
- partial commit strategy: describe when partial commits are acceptable and what
  data is protected by each commit.
- safe retry behavior: define what happens after timeout, interruption, or
  scheduler retry.
- wake/polling behavior: for long work, define whether the flow wakes a timer,
  queues work, or exposes status for polling.
- batch size: state how many records/items are processed per run when volume is
  material.
- error isolation: record failed items separately when one bad record should not
  block the entire batch.

Fallback behavior:

- If idempotency cannot be proven, stop and ask for the durable progress model.
- If live execution is involved, use `live-mentor-campaign-guidance.md` before
  any Mentor, publish, deploy, rollback, cleanup, or tenant action.

## Public API Contract Gate

Use this gate when OMI creates or changes a public action, Service Action,
exposed REST method, consumed REST integration, shared producer API, event
contract, or reusable library boundary.

Check:

- input and output contract: name parameters, required/optional behavior, data
  types, and null/empty behavior.
- public descriptions: public elements and parameters need meaningful
  descriptions when they are part of a reusable contract.
- transaction behavior: state whether the public action commits, aborts, or
  relies on caller transaction scope.
- error semantics: define expected exceptions, error outputs, and retry-safe
  responses.
- compatibility: prefer additive changes, wrappers, or versioned actions when
  existing consumers may break. A breaking signature change (such as a new
  mandatory input) means every consumer must be updated; the documented path
  for exposed elements is to duplicate the element and rename it (a v2), change
  the copy, and migrate consumers progressively
  ([handle-changes.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/reuse/handle-changes.md), verified 2026-08-27).
  The same obligation applies inside one app when changing an existing
  attribute's data type: the change succeeds locally and breaks at every
  reference site, so sweep for all of them before agreeing to it — aggregate
  filters and sort expressions, calculated attributes, action assignments,
  widget bindings, and displayed expressions. Where the sweep is large, prefer
  adding a correctly typed attribute and migrating, rather than retyping in
  place.
- consumer impact: list known consumers or mark them unknown; route broad
  shared-producer changes through the Shared Producer Compatibility Gate.
- security: combine with the Security Server-Trust Gate for exposed REST or
  sensitive reusable actions.
- ODC `Public` flag: leave `Public = false` on any Server Action called only
  from the app's own screens, actions, or timers — seed and utility actions
  included. Mentor has set it unprompted; the flag validates clean and then
  fails at publish with `OS-BLD-40409:
  ModelFeature_ServerActionPublicPropertyApp, a feature that has been removed`
  (external field evidence, Arjan fork review 2026-08-12). On that failure,
  enumerate every Server Action's `Public` property — utility actions first —
  rather than guessing the culprit.

Fallback behavior:

- If consumer impact is unknown, do not emit a confident breaking-change prompt.
- If transaction behavior is unknown, require clarification before making a
  public reusable action paste-ready.

## Deploy-Time Error Code Gate

External field evidence: an internal OutSystems project (adopted 2026-08-14); field-observed over the Mentor MCP, not in official docs. Error-code claims here are field observations — exact official semantics stay `Unverified gap` under `provider: public-grounded`.

Deploy-time failures that pass model validation. Route by code, never by message text:

- **`OS-DPL-50204`** — entity attribute **type change with existing data**. In-place conversion fails deterministically. Fix: **rename to a fresh attribute** (add new attribute with the target type, migrate, retire the old name) — never re-attempt the conversion.
- **`OS-DPL-RDBS-40020`** — **drop + recreate an attribute under the same name**. Attribute names are additive across an app's deploy history: retired names stay burned. Fix: pick a fresh name.
- **`OS-DPL-50205`** — "Model features validation failed": deterministic and **invisible to model validation** (zero validation errors before publish). Known field triggers: a `User`-typed attribute plus seed user-lookup (this guide's User Reference Authoring Gate, above) and a `GetUser(GetUserId()).User.Name` call inside an expression (fix: stamp a literal). Do not burn retries on it — the same publish fails the same way; remove the triggering construct.
- **`OS-BLD-40409` + `OS-RDBS-GEN-40002` + `OS-DPL-50205`, raised together** — Mentor set **delete rules on foreign-key attributes**, which it does BY DEFAULT. `ModelFeature_DeleteRuleOnReferences` and `ModelFeature_DeleteRuleOnSystemReferences` are **removed ODC features**, so the publish reports all three codes at once: "Value provided for argument DeleteRule was not within expected values.: Invalid delete rule (`OS-RDBS-GEN-40002`)", "Using the feature ModelFeature_DeleteRuleOnReferences, a feature that has been removed. (`OS-BLD-40409`)", "Model features validation failed (`OS-DPL-50205`)". Measured 2026-08-27 (restaurant-app-v2): the authoring turn that created 17 entities — **system references such as `User` included** — returned `validation.error_count: 0` and `change_applied: true`, and the publish failed anyway (3 attempts, `indeterminate: false` — so genuinely terminal, not an unresolved publish). Fix: **one further Mentor turn on the same session** removing delete-rule configuration from every affected attribute — 83 of them on that run — then re-publish, which succeeded. Do not re-publish unchanged; the 4xx tail is deterministic. The standing prompt line that prevents it is in `odc-mentor-hardening.md`, which owns the authoring rule.
- **`OS-BEW-CODE-50008`** — Mentor emitted a **static sort bound to a runtime value**: zero save errors, then the publish fails at "Generating database scripts", which reads like a platform outage. It is re-introduced whenever Mentor regenerates a sortable list. Standing prompt line for any sortable list: **"Implement sorting as a DYNAMIC sort (`IsDynamic = True`), never a static sort on a runtime value."**
- **Probe-once discipline:** the first publish after a fix is a single engine probe. On failure: diagnose once against this table, report blocked with the code, and wait for an explicit retry decision — never hammer `mentor_publish` at a deterministic code.

## Library Release Visibility Gate

External field evidence: an internal OutSystems project (adopted 2026-08-14); field-observed over the Mentor MCP, not in official docs.

- A just-published library (or agent app) **must be RELEASED in the ODC Portal before any consumer can locate it** — until release it is invisible to consumer dependency resolution. No MCP tool performs the release; it is a manual Portal step.
- Diagnostic: a consumer that "can't find" a just-published producer is almost always waiting on that release — check release state before debugging names, scopes, or references.

## Unknowns And Fallback Behavior

Use these exact labels in OMI output when the gate cannot be satisfied. Every
label in the list below is a missing-information label: supply the fact it
names and the design proceeds. One further label follows in its own subsection,
for the opposite case.

- `Layer fit unknown`: architecture layer, owner, sponsor, or consumer direction
  is not verified.
- `Server-trust policy unknown`: the authorization, identity, or validation rule
  is missing.
- `Volume/performance unknown`: expected record count, page size, or query
  frequency is missing.
- `Idempotency model unknown`: no durable progress marker or safe retry behavior
  is defined.
- `Public contract impact unknown`: public consumers, transaction behavior, or
  compatibility strategy is missing.
- `User reference state unknown`: whether the target app already carries the
  platform `User` reference is unverified, so the design cannot be classified
  as carrying an existing reference rather than authoring a new one.

When any of these labels materially affects safety, return a prompt/spec with an
explicit unknown rather than a paste-ready Mentor Studio instruction.

### `Blocked by platform rule`

Every label above says something is unverified. This one says the opposite:
nothing is missing. The design is understood, and a gate in this file has
already recorded that the platform refuses it, reverts it, or renames it.

Use it when all three hold:

- the construct the design needs is named — by a gate in this file, or by an
  owner file this file routes to — as one the platform will not accept as
  written;
- nothing is outstanding: a further question to the user would not change the
  outcome;
- the owning gate already carries the remedy, and that remedy is a different
  construction rather than another attempt at the same one.

Name the owning gate alongside the label, and give the gate's remedy in the
same breath:

> `Blocked by platform rule` (User Reference Authoring Gate) — author the
> `User`-typed attribute in ODC Studio as a `Manual Setup Gate` row; Mentor
> carries it from there.

Where the owning gate records a publish or deploy code, quote that code from
the gate; do not characterise the platform's behaviour independently here.

**Why the label earns its place: a retry is not a diagnosis.** The converge
iteration in `SKILL.md` stops on a budget — the handoff's target tier, or two
consecutive audits with no weighted-score improvement. A budget cannot tell a
design that has not converged *yet* from one that never will, so a
platform-refused construct absorbs whatever budget is left and ends the run
looking like an ordinary near-miss. Each attempt costs a turn and changes
nothing. This label ends the loop on the diagnosis instead, at the first
attempt, with the remedy already attached.

`Blocked by platform rule` is an OMI output label and nothing more. It records
how this workflow classifies its own stop; it does not create a platform claim,
and it never stands in for the evidence held by the gate it names.
