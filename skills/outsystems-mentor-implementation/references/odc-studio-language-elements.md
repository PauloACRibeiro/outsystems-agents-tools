# ODC Studio Language Elements Handbook

## 1. Reading Guide

This handbook is a planning and pseudocode reference for OutSystems Developer Cloud (ODC) Studio. It focuses on the language elements that matter when you need to describe implementation logic using real OutSystems names, real parameter labels, and real runtime constraints.

Use this handbook together with:

- [ODC Studio Implementation Context](./odc-studio-implementation-context.md) for architecture, placement, security, delivery, troubleshooting, and best-practice rationale.
- [ODC Pseudocode Source Manifest](./odc-pseudocode-source-manifest.md) for exhaustive source coverage and auditability.

The main rule of this document is simple:

- Use current public OutSystems ODC documentation from the available public-provider role as the source of truth.
- Use the approved public source repositories only as the explicitly degraded fallback defined below.
- Use internal PDF/course material only through the separate VPN-gated technical-content capability, never as a higher authority than current public docs.
- Never present unsupported or unsourced elements as if they were confirmed ODC capabilities.

### Evidence Status

- `Current official`: confirmed in current public ODC documentation or the official docs source repository.
- `Official archived`: confirmed only in an official archived source retrieved through an available evidence provider, not re-confirmed as current live support.
- `Official course/example`: confirmed in official OutSystems course/workshop material or example assets, but not treated as a stronger authority than live docs.
- `Unverified`: searched for, but not evidenced strongly enough to document as supported ODC language capability.

### Coverage Status

The coverage matrix at the end uses these outcome labels:

- `documented`
- `archived-only`
- `course/example-only`
- `unverified`

## 2. Source Inventory And Precedence

### Source precedence

1. Use the available public-provider role first: `workspace-knowledge-cc` and
   `outsystems-public-knowledge` expose the same public retrieval role.
2. Prefer current public pages and repo-qualified identifiers such as
   `OutSystems/docs-odc:src/...` returned by that provider role.
3. Only when neither public-provider alias is available, use local clones of
   exactly `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` as an
   explicitly degraded, source-backed fallback; do not rely on model memory
   alone.
4. Use internal course/example evidence only through the separate VPN-gated
   `outsystems-tech-content` capability; otherwise keep internal claims
   `Unverified or blocked`.

For full source inventory across architecture, build, security, debugging, deployment, monitoring, and course/archive material, see the [ODC Pseudocode Source Manifest](./odc-pseudocode-source-manifest.md).

### Primary public source families

| Source family | Role in this handbook | Status |
| --- | --- | --- |
| [OutSystems language and elements](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/) | Master index for language families, libraries, built-in functions, and system actions | Current official |
| [Client Action](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/logic_actions/client_action/) | Canonical reference for Client Action properties and exposure rules | Current official |
| [Server Action](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/logic_actions/server_action/) | Canonical reference for Server Action properties and exposure rules | Current official |
| [Service Actions](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/service_actions/) | Current public reference entry for service actions | Current official |
| [System Actions](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/system_actions/) | Current public reference entry for Authentication, User, Workflows, GetDefaultDomain | Current official |
| [Built-in Functions](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/) | Current public reference entry for built-in function families | Current official |
| [JavaScript extensibility](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/javascript_extensibility/) | Current public reference entry for `$public` JavaScript APIs | Current official |
| [ODC Data Grid reference](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/odc_data_grid_reference/) | Canonical reference for Data Grid widgets, actions, client actions, structures, and static entities | Current official |
| [Database transaction isolation level](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/database_transaction_isolation_level/) | Canonical reference for transaction visibility semantics | Current official |
| [ODC REST APIs](https://success.outsystems.com/documentation/outsystems_developer_cloud/odc_rest_apis/) | Official platform/public API area for tenant automation and management | Current official |

### Supporting current official sources used for Studio behavior

These sources were also analyzed and used because many Studio elements are documented outside the top-level language index:

- Screen and block lifecycle events
- Input Parameter
- Output Parameter
- Local Variable
- Client Variable
- Query data using aggregates
- Query data using SQL
- Implement events in ODC
- Properties of ODC events
- Create and run Timers
- Working with emails
- Sending emails
- Consume one or more REST API methods
- Expose a REST API
- Customize API request and response headers
- Handling REST Errors
- Customize REST URLs
- Change the HTTP Status Code of a REST API
- Implement workflow
- Building agentic workflows
- Agentic apps in ODC
- Adding AI models
- Adding search services
- AI agent actions

### Public and internal evidence capabilities

| Evidence capability | Role in this handbook | Availability |
| --- | --- | --- |
| Public knowledge-provider role | Preferred public ODC reference exports. | `workspace-knowledge-cc` or `outsystems-public-knowledge` |
| Approved public source repositories | Source-backed fallback for public facts and examples. | Explicitly degraded; only when neither public-provider alias is available |
| Technical-content internal evidence | Internal course, archive, workshop, and example material for lifecycle, integrations, agents, functions, widgets, and TrueChange. | Separate VPN-gated `outsystems-tech-content` capability only |

### Notes on local availability

- Use the available public-provider role first: `workspace-knowledge-cc` and
  `outsystems-public-knowledge` expose the same public retrieval role.
- Only when neither alias is available, use local clones of `docs-howtos`,
  `docs-odc`, `docs-product`, and `outsystems-ui` as an explicitly degraded,
  source-backed fallback; do not rely on model memory alone.
- Use internal courseware or internal notes only when the separate, VPN-gated
  `outsystems-tech-content` capability is available. Do not assume an
  owner-specific mirror or named local file exists.
- Use workshop `.oml` and course evidence only through VPN-gated
  `outsystems-tech-content`; otherwise keep those claims `Unverified or
  blocked`. Treat retrieved workshop assets as official examples, not as a
  stronger authority than current docs.

## 3. ODC Studio Visual Elements

This section uses the following schema whenever practical:

- `Element`
- `Category`
- `Available In`
- `Runs On`
- `Purpose`
- `Key Properties / Parameters`
- `Runtime Outputs / Context`
- `Constraints / Notes`
- `Pseudocode Pattern`
- `Evidence Status`
- `Sources`

### 3.1 Core Containers

### Screen

**Category**: Top-level UI container
**Available In**: Web apps, mobile apps
**Runs On**: Client UI with client and server-backed data fetching
**Purpose**: A page-like UI element that contains widgets, blocks, placeholders, screen data, and event handlers.
**Key Properties / Parameters**: Screen docs explicitly cover screen title/layout concepts, roles/authorization, lifecycle handlers, and support for input parameters.
**Runtime Outputs / Context**: Holds screen data such as input parameters, variables, aggregates/data actions, and validation state.
**Constraints / Notes**: Screen data changes automatically trigger rerender. Aggregates and Data Actions must be refreshed explicitly with `Refresh Data`.
**Pseudocode Pattern**: `Screen CustomerDetail(Id: CustomerId)`
**Evidence Status**: Current official
**Sources**: [screen-about.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/screen-about.md), [screen-block-lifecycle-events.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/screen-block-lifecycle-events.md), [input-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/input-parameter.md)

### Block

**Category**: Reusable UI container
**Available In**: Screens, blocks, libraries
**Runs On**: Client UI
**Purpose**: Reusable UI section that can contain placeholders, input parameters, local variables, logic, scripts, and styles.
**Key Properties / Parameters**: Blocks support input parameters and lifecycle events. Reusable blocks across apps must be public and created in libraries.
**Runtime Outputs / Context**: Supports its own local scope and rerender behavior.
**Constraints / Notes**: Cross-app reuse requires a library producer and `Public = Yes`.
**Pseudocode Pattern**: `Block CustomerSummary(CustomerId: CustomerId)`
**Evidence Status**: Current official
**Sources**: [screen-about.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/screen-about.md), [block-create-reuse.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/reuse/block-create-reuse.md), [screen-block-lifecycle-events.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/screen-block-lifecycle-events.md)

### 3.2 Core Action Types

### Client Action

**Category**: Callable logic element
**Available In**: Apps and libraries
**Runs On**: Client
**Purpose**: Runs client-side logic and orchestrates UI logic, client expressions, client-side events, JavaScript, and calls to server actions.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Name` | Required |
| `Description` | Optional; up to 2000 chars |
| `Public` | Library only; enables reuse by other apps/libraries |
| `Function` | Global scope only; must return a value; usable in client expressions |
| `Icon` | Required |
| `Original Name` | Read-only for referenced elements |
| Input Parameters | Supported |
| Output Parameters | Supported |

**Runtime Outputs / Context**: Outputs are accessible as `<ActionCall>.<OutputParameter>`.
**Constraints / Notes**:

- Cannot be exposed when defined in an app.
- In a library, cannot be exposed if it uses an unexposed static entity in its signature.
- If a client action chains multiple `Run Server Action` nodes, each call is a separate server request and separate transaction.

**Pseudocode Pattern**: `Run Client Action ValidateForm(Name: UserName, Email: UserEmail)`
**Evidence Status**: Current official
**Sources**: [Client Action](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/logic_actions/client_action/), [input-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/input-parameter.md), [output-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/output-parameter.md), [multiple-server-requests-inside-client-actions.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/monitor-and-troubleshoot/manage-technical-debt/performance/multiple-server-requests-inside-client-actions.md)

### Server Action

**Category**: Callable logic element
**Available In**: Apps and libraries
**Runs On**: Server
**Purpose**: Runs server-side logic, data access, integration logic, validation, and reusable backend functions.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Name` | Required |
| `Description` | Optional; up to 2000 chars |
| `Public` | Library only; enables reuse by other apps/libraries |
| `Function` | Global scope only; must return a value; usable in server expressions |
| `Icon` | Required |
| `Original Name` | Read-only for referenced elements |
| `Cache in Minutes` | Advanced property |
| Input Parameters | Supported |
| Output Parameters | Supported |

**Runtime Outputs / Context**: Outputs are accessible as `<ActionCall>.<OutputParameter>`.
**Constraints / Notes**:

- Cannot be exposed when defined in an app.
- In a library, cannot be exposed if it uses an unexposed static entity in its signature.
- Often used to consolidate server logic behind a single `Run Server Action` from the client.

**Pseudocode Pattern**: `Run Server Action CreateOrder(Order: NewOrder)`
**Evidence Status**: Current official
**Sources**: [Server Action](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/logic_actions/server_action/), [input-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/input-parameter.md), [output-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/output-parameter.md)

### Service Action

**Category**: Loosely-coupled reusable backend action
**Available In**: Producer apps and consumer apps via public elements / weak dependencies
**Runs On**: Server
**Purpose**: Encapsulates reusable backend logic behind a REST-based remote call that behaves similarly to a strongly typed public server action from the consumer perspective.
**Key Properties / Parameters**:

- Uses input and output parameters in its signature.
- Can expose structures and entities in signatures.
- Current public reference family explicitly documents `CallAgentV2` under `Service Actions > AIAgentBuilder`.

**Runtime Outputs / Context**: Consumer apps call a typed action and receive typed outputs.
**Constraints / Notes**:

- Exposing a service action creates a weak dependency.
- Producer implementation changes take immediate effect in consumers.
- ODC passes authentication context from the client session (`UserId`, `TenantId`) to the service action call.
- User Exceptions and Communication Exceptions raised by a service action can be caught by consumers.

**Pseudocode Pattern**: `Run Service Action CustomerService.GetCreditLimit(CustomerId: CustomerId)`
**Evidence Status**: Current official
**Sources**: [Service Actions](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/service_actions/), [Service actions architecture note](https://success.outsystems.com/documentation/outsystems_developer_cloud/app_architecture/service_actions/)

### Data Action

**Category**: Screen/block data fetch action
**Available In**: Screens and blocks, especially reactive web/mobile data fetching patterns
**Runs On**: Server-backed fetch coordinated by the client runtime
**Purpose**: Fetches non-entity or transformed data for a screen or block and exposes screen-friendly runtime state such as `IsDataFetched`.
**Key Properties / Parameters**:

- Supports output parameters.
- Supports `On After Fetch`.
- Common runtime properties used by UI widgets include `IsDataFetched`.

**Runtime Outputs / Context**:

- Output parameters hold fetched/transformed data.
- In official grid examples, a Data Action returns serialized JSON through an output parameter.

**Constraints / Notes**:

- Strongly evidenced in current official docs, but not through a single standalone element reference page.
- Screen/block lifecycle docs treat Data Actions as part of the screen/block data model.

**Pseudocode Pattern**: `Run Data Action GetAllProducts() -> ProductsJson`
**Evidence Status**: Current official
**Sources**: [screen-block-lifecycle-events.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/screen-block-lifecycle-events.md), [aggregate.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/data/fetch-data/aggregate.md), [data-grid-fetch-data.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/patterns/interaction/data-grid/data-grid-fetch-data.md)

### 3.3 Parameters And State

### Input Parameter

**Category**: Signature element
**Available In**: Server Actions, Client Actions, Screens, Blocks, Processes, exposed/consumed REST methods, callback/authentication actions for REST integrations, Emails, External Sites, JavaScript elements
**Runs On**: N/A
**Purpose**: Provides data to an element and makes it available in that element's scope.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Name` | Evidenced by examples and usage |
| `Data Type` | Evidenced by examples and usage |
| `Is Mandatory` | Explicitly documented |
| Invocation values / arguments | Set when the element is called |

**Runtime Outputs / Context**: Accessible in the scope of the element that owns the parameter.
**Constraints / Notes**:

- Mandatory inputs must be supplied at invocation.
- Input parameters are not automatically in scope of nested action calls; pass them explicitly when needed.

**Pseudocode Pattern**: `Client Action GetWeatherData(City: Text, Country: Text)`
**Evidence Status**: Current official
**Sources**: [input-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/input-parameter.md)

### Output Parameter

**Category**: Signature element
**Available In**: Server Actions, Client Actions, Processes, Process Activities, Wait elements, exposed/consumed REST methods, JavaScript elements
**Runs On**: N/A
**Purpose**: Returns computed values from an action or integration call.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Name` | Evidenced by examples and usage |
| `Data Type` | Evidenced by examples and usage |
| Value assignment | Usually set with `Assign` |

**Runtime Outputs / Context**: Access outputs from a call as `<FlowElement>.<OutputParameter>`.
**Constraints / Notes**:

- In internal logic, values are typically assigned before `End`.
- In consumed integrations, OutSystems fills outputs from the external response.

**Pseudocode Pattern**: `Output WeatherInfo: Text`
**Evidence Status**: Current official
**Sources**: [output-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/output-parameter.md)

### Local Variable

**Category**: Local state element
**Available In**: Screens, blocks, actions, and other parent scopes where Studio allows local scope
**Runs On**: Scope dependent
**Purpose**: Stores temporary state only inside the parent element's scope.
**Key Properties / Parameters**:

- Example-driven docs explicitly show setting `Name` and `Data Type`.
- Used commonly for filter input, intermediate values, and local state.

**Runtime Outputs / Context**: Exists only while execution remains inside the parent scope.
**Constraints / Notes**:

- Destroyed when leaving the parent scope.
- Cannot be shared across screens or app sessions.

**Pseudocode Pattern**: `Local Variable SearchKeyword: Text`
**Evidence Status**: Current official
**Sources**: [local-variable.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/local-variable.md)

### Client Variable

**Category**: Client-side persistent variable
**Available In**: Mobile and Reactive Web apps
**Runs On**: Client
**Purpose**: Stores client-side key-value data such as configuration or client context across screens.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Name` | Required |
| `Description` | Optional |
| `Data Type` | Required |
| `Default Value` | Optional; must be a literal |

**Runtime Outputs / Context**: Accessible through `Client.<VariableName>`.
**Constraints / Notes**:

- Supports only basic data types and entity identifiers.
- `Binary` cannot be stored.
- Resets to default on sign-out.
- Do not store sensitive or confidential data.

**Pseudocode Pattern**: `Client Variable SearchKeyword: Text = ""`
**Evidence Status**: Current official
**Sources**: [client-variable.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/data/client-variable.md)

### 3.4 Data And Query Elements

### Aggregate

**Category**: Query element
**Available In**: Screens, blocks, action flows
**Runs On**: Client-side or server-side depending on context
**Purpose**: Fetches data using optimized OutSystems queries with joins, filters, sorting, and calculated attributes.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Name` | Required |
| `Description` | Optional |
| `Timeout` / `Server Request Timeout` | Timeout in seconds; screen aggregates use the screen label |
| `Max. Records` | Max rows fetched |
| `Cache in Minutes` | Not available in client actions |
| `Start Index` | Supports expressions |
| `Fetch` | Required; default is `At start` |
| `On After Fetch` | Event handler on the aggregate |

**Runtime Outputs / Context**:

| Runtime property | Meaning |
| --- | --- |
| `List` | Returned record list |
| `Count` | Count query result |
| `IsDataFetched` | Data fetch completed |
| `HasFetchError` | Fetch failed |

**Constraints / Notes**:

- Use `Refresh Data` to rerun screen/block aggregates.
- Avoid aggregates inside `For Each` cycles.
- If a Data Action fetches all records, `Max. Records` can be left empty.

**GROUP BY / count-per-group guidance**:

Use Aggregate grouping for count-per-group summaries only when the target entity, grouping attributes, and aggregate editor grouping fields are confirmed. In Studio-native pseudocode, name the grouping fields and the calculated attribute explicitly:

```text
Aggregate GetRequestCountByStatus
Source Entity: Request
Group By: Request.StatusId
Calculated attribute RequestCount = Count(Request.Id)
```

For multi-dimensional counts, list each grouping attribute before the calculated attribute:

```text
Aggregate GetRequestCountByStatusAndSlaBucket
Source Entity: Request
Group By: Request.StatusId, Request.SlaBucketId
Calculated attribute RequestCount = Count(Request.Id)
```

Use this SQL hardening fallback when grouping semantics are uncertain: treat the grouping claim as `Unverified gap`, ask for the missing schema, and use `odc-mentor-hardening.md` only when an Aggregate cannot express the query safely.

Evidence boundary: Current official for Aggregate concepts, grouping, count, and calculated attributes; use `Unverified gap` for exact grouping prompt shape unless confirmed in Studio/docs for the specific target model.

**Pseudocode Pattern**: `Aggregate GetOrders(Max. Records: 50, Fetch: At start)`
**Evidence Status**: Current official
**Sources**: [aggregate.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/data/fetch-data/aggregate.md), [aggregate-or-sql-query-inside-a-cycle.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/monitor-and-troubleshoot/manage-technical-debt/performance/aggregate-or-sql-query-inside-a-cycle.md)

### Static Entity

**Category**: Data element
**Available In**: Data model, expressions, logic assignments, query filters
**Runs On**: Server or client expression context, depending on where referenced
**Purpose**: Defines a global set of named records for predefined values such as statuses, categories, or modes. The Records folder holds the static records.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Records` folder | Holds the named records exposed by the Static Entity |
| `Id` | Unique record identifier |
| `Label` | Display value for users; do not use as the logic identifier |
| `Order` | Display ordering |
| `Is_Active` | Runtime/scaffolding availability flag |

**Runtime Outputs / Context**:

| Runtime reference | Meaning |
| --- | --- |
| `Entities.<StaticEntity>.<Identifier>` | Static record reference by identifier |
| `Entities.Status.CheckedOut` | Example static record reference by identifier |
| `Get<StaticEntity>` | Built-in action to retrieve static entity records |

**Constraints / Notes**:

- Use Static Entities only for predefined values with global scope.
- For status checks and assignments, use the static record identifier, not the label or raw text.
- Static Entities can only contain foreign keys to other Static Entities.

**Pseudocode Pattern**: `Assign Reservation.Status = Entities.Status.CheckedOut`
**Evidence Status**: Current official
**Sources**: [entity-static.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/data/modeling/entity-static.md)

### SQL

**Category**: Query element
**Available In**: Server Actions, Service Actions, Screen Data Actions
**Runs On**: Server
**Purpose**: Executes custom SQL for advanced queries, stored procedures, bulk operations, and scenarios that are not practical in Aggregates.
**Key Properties / Parameters**:

- SQL text
- Input parameters
- Output structure / result shape
- Syntax mode chosen automatically by Studio:
  - PostgreSQL syntax for internal entities only
  - ANSI-92 when external entities are involved

**Runtime Outputs / Context**: Returns records according to the defined output structure.
**Constraints / Notes**:

- Test Query against external entities can commit `INSERT`, `UPDATE`, `DELETE`, or `CALL` immediately.
- Avoid SQL queries inside cycles.
- Prefer Aggregates unless SQL is clearly needed.

**Pseudocode Pattern**: `SQL GetOverdueInvoices(CustomerId: CustomerId)`
**Evidence Status**: Current official
**Sources**: [use-sql.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/data/fetch-data/sql/use-sql.md), [aggregate-or-sql-query-inside-a-cycle.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/monitor-and-troubleshoot/manage-technical-debt/performance/aggregate-or-sql-query-inside-a-cycle.md)

### 3.5 Events, Timers, And JavaScript

### Event

**Category**: Async communication element
**Available In**: Apps that publish or consume events
**Runs On**: Server/event infrastructure
**Purpose**: Communicates changes asynchronously between apps.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Public` | Required for other apps to consume the event |
| `Handler` | Optional server action in producer or consumer |
| Input Parameters | Payload fields; primitive types only |

**Runtime Outputs / Context**:

| Property | Constraint |
| --- | --- |
| Event payload | Max 10KB; primitive types only; text max 2000 chars |
| Event queue | Max 10000 queued events per event type |
| Delivery | Max 10 retries; order not guaranteed |
| Execution | Max 2 minutes; each app can handle 100 events concurrently |

**Constraints / Notes**:

- If you create data in the same transaction and then trigger an event, commit first.
- Producer-side exceptions include oversized payload, full queue, or undeliverable event.
- Consumer-side timeout exceptions should be handled with an `All Exceptions` handler.

**Pseudocode Pattern**: `Trigger Event OnPurchaseStarted(ProductId: ProductId)`
**Consumer Handler Pattern**:

```text
Consumer app: Add public element OnPurchaseStarted from producer app
Consumer Server Action HandlePurchaseStarted
Inputs: ProductId (primitive payload inputs from event)
Event OnPurchaseStarted Handler: HandlePurchaseStarted
Exception Handler All Exceptions
```

**Evidence Status**: Current official
**Sources**: [implement-events.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/events/implement-events.md), [events-properties.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/events/events-properties.md)

### Timer

**Category**: Scheduled async element
**Available In**: Apps
**Runs On**: Server scheduler
**Purpose**: Executes application logic periodically or on demand.
**Key Properties / Parameters**:

| Property | Notes |
| --- | --- |
| `Name` | Timer name |
| `Action` | Server action executed when timer runs |
| Schedule | Defined at design time and/or overridden in ODC Portal |
| Input arguments | Required when the timer action has inputs |

**Runtime Outputs / Context**: Timer action outputs are available only after execution completes.
**Constraints / Notes**:

- The same timer does not run twice simultaneously.
- `Wake<TimerName>` forces execution without changing the recurring schedule.
- `Wake<TimerName>` has no inputs and no outputs.

**Pseudocode Pattern**: `WakeDailyRebuildIndexes()`
**Evidence Status**: Current official
**Sources**: [timer-create-run.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/timers/timer-create-run.md)

### JavaScript node

**Category**: Client-side extensibility element
**Available In**: Client Actions
**Runs On**: Client
**Purpose**: Executes custom JavaScript and can call OutSystems-supported `$public` APIs.
**Key Properties / Parameters**:

- Supports Input Parameters.
- Supports Output Parameters.
- Can call `$public` modules such as `FeedbackMessage`, `Navigation`, `View`, and `Logger`.

**Runtime Outputs / Context**: Outputs are returned through JavaScript element output parameters.
**Constraints / Notes**:

- Only document facts confirmed by ODC docs. This handbook does not infer undocumented JavaScript node properties.

**Pseudocode Pattern**: `JavaScript(GetBrowserInfo) -> Result`
**Evidence Status**: Current official
**Sources**: [JavaScript extensibility](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/javascript_extensibility/), [input-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/input-parameter.md), [output-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/output-parameter.md)

### 3.6 Screen And Block Lifecycle Handlers

| Element | Available In | When it runs | Key notes | Evidence |
| --- | --- | --- | --- | --- |
| `On Initialize` | Screen, Block | After permission check and before data fetch | Good for default data setup; avoid data access that depends on fetched screen data | Current official |
| `On Ready` | Screen, Block | When DOM is ready, before transition ends | Use for DOM-dependent logic; avoid assuming screen data is fetched | Current official |
| `On Render` | Screen, Block | After first render and whenever screen/block data changes | Do not mutate screen data casually or you can create rerender loops | Current official |
| `On After Fetch` | Aggregate, Data Action | After data arrives, before widgets bind | Good for dependent queries and post-fetch transformations; avoid `GetUserId()` here on screens due to documented caveat | Current official |
| `On Parameters Changed` | Block | After parent changes a block input | Commonly used to recalculate variables or `Refresh Data` | Current official |
| `On Destroy` | Screen, Block | Before disposal / DOM removal | Use for cleanup such as listener removal or third-party teardown | Current official |
| `On Application Ready` | App system event | During app loading | Runs synchronously and blocks first screen render | Current official |
| `On Application Resume` | Mobile app system event | App returns from background to foreground | Mobile only | Current official |

**Sources**: `OutSystems/docs-odc:src/eap/building-apps/ui/screen-block-lifecycle-events.md`, `OutSystems/docs-odc:src/eap/building-apps/logic/application-ready.md`, and `OutSystems/docs-odc:src/eap/building-apps/logic/application-resume.md`; web-specialist course/example evidence is available only through the VPN-gated `outsystems-tech-content` query `Screen and block lifecycle events`, otherwise `Unverified or blocked`.

**Lifecycle pseudocode rules:**

- `On Initialize` runs before screen data is fetched — do not read aggregate output here. Use it to compute defaults, parse URL parameters, or call a Server Action that supplies a starter state.
- `On After Fetch` (per-aggregate) is where logic that depends on fetched data belongs. Use it for chained / dependent queries or to derive computed properties.
- `On Ready` is for DOM-dependent client logic (third-party widget initialization, focus management) and runs once per screen visit.
- `On Render` runs after first render and on every screen-data change — keep it cheap and idempotent. Mutating screen data inside `On Render` causes rerender loops.
- `On Parameters Changed` (Block-only) re-runs when a parent changes a block input. Use it to refresh the block's local state or `Refresh Data` its aggregates.
- `On Destroy` is the cleanup hook — remove listeners, cancel pending JS work, free third-party widgets.

### 3.7 Core Flow Nodes

| Element | Available In | Key Properties / Parameters | Notes for planning | Pseudocode Pattern | Evidence |
| --- | --- | --- | --- | --- | --- |
| `Start` | Action flows, workflows | None documented beyond being the start node | Entry point of the flow | `Start` | Current official |
| `End` | Action flows, workflows | None documented beyond being the end node | Exit point of the flow | `End` | Current official |
| `Assign` | Actions, Data Actions, callbacks, many logic flows | `Variable`, `Value` | Used to set variables and output parameters | `Assign IsExecuting = True` | Current official |
| `If` | Actions | `Condition`; examples also show `Label` | True/False branching | `If CheckManagerRole()` | Current official |
| `For Each` | Actions | `Record List`; loop context via `.Current` | Iterate lists; avoid Aggregate/SQL inside the loop | `For Each EditedProducts` | Current official |
| `Run Client Action` | Client Actions | Selected action and its input arguments | Invokes client logic | `Run Client Action GetChangedLines(GridWidgetId: ProductGrid.Id)` | Current official |
| `Run Server Action` | Client Actions, server-side flows | Selected action and its input arguments | In client flows, each call is a separate server request | `Run Server Action UpdateProduct(Product: EditedProducts.Current)` | Current official |
| `Refresh Data` | Screen/block logic | Target Aggregate or Data Action | Re-runs screen/block data fetch | `Refresh Data GetOrders` | Current official |
| `Trigger Event` | Server Action, Service Action | Selected event and its payload arguments | Commit first if event depends on newly written data | `Trigger Event OnPurchaseStarted(ProductId: ProductId)` | Current official |
| `Raise Exception` | Logic flows | `Exception Message`; specific exception type selected in the node | Use for exceptional conditions, not normal control flow | `Raise Exception UnavailableExternalSystem("Provider timeout")` | Current official |
| `Exception Handler` | Flow scopes | `Exception`, `ExceptionMessage`, `Log Error` | `All Exceptions`, `User`, `Database`, `Security`, `Communication` are explicitly documented families | `Exception Handler All Exceptions` | Current official |
| `Send Email` | Server or service logic that sends an Email element | `Email`, `To`, mapped email input parameters, optional `Attachments` | Runs on the server; email UI content is defined separately | `Send Email WelcomeEmail(To: User.Email, Handle: User.Name)` | Current official |
| `Wake<TimerName>` | Logic flows | No inputs; no outputs | Forces a timer execution | `WakeNightlySync()` | Current official |

**Sources**: [output-parameter.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/logic/output-parameter.md), [data-grid-save.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/patterns/interaction/data-grid/data-grid-save.md), [secure-app-with-roles.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/user-management/secure-app-with-roles.md), [screen-block-lifecycle-events.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/ui/screen-block-lifecycle-events.md), [implement-events.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/events/implement-events.md), [handle-exceptions.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/handling-exceptions/handle-exceptions.md), [sending-emails/intro.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/sending-emails/intro.md), [timer-create-run.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/timers/timer-create-run.md)

### 3.8 Workflow Nodes

| Node | Purpose | Notes for implementation | Evidence |
| --- | --- | --- | --- |
| `Start` | Begins the workflow | One per workflow | Current official |
| `Conditional start` | Starts workflow under conditions | Used to gate start criteria | Current official |
| `Automatic activity` | Executes system-driven step | Commonly calls service actions or sends emails | Current official |
| `Human activity` | Waits for user task | Runtime APIs exist for assign/open/release | Current official |
| `Decision` | Branches workflow | Conditions determine path | Current official |
| `Go to a flow step` | Returns execution to a previous node | Useful for loops and correction flows | Current official |
| `Parallel` | Runs branches simultaneously | Workflow waits for branches to complete | Current official |
| `Terminate` | Stops workflow execution | Used for exceptional stop conditions | Current official |
| `End` | Finishes workflow | Multiple end nodes allowed | Current official |

**Sources**: [workflow-components.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/workflows/workflow-components.md), [add-decisions.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/workflows/add-decisions.md), [add-human-activity.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/workflows/add-human-activity.md), [add-automatic-activity.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/workflows/add-automatic-activity.md)

## 4. OutSystems Language Catalog

This section is intentionally catalog-oriented. For very large families such as built-in functions and libraries, it lists all official families and highlights the most useful examples for planning and pseudocode.

### 4.1 Logic Actions

| Name | Family | Availability | Inputs / Parameters | Output / Return | Function? | Use In Pseudocode | Evidence Status | Official Reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Client Action | Logic Actions | Apps, libraries | Input Parameters | Output Parameters | Yes, if `Function = Yes` | Client-side orchestration | Current official | [Client Action](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/logic_actions/client_action/) |
| Server Action | Logic Actions | Apps, libraries | Input Parameters | Output Parameters | Yes, if `Function = Yes` | Server-side orchestration | Current official | [Server Action](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/logic_actions/server_action/) |

### 4.2 Service Actions

| Name | Family | Availability | Inputs / Parameters | Output / Return | Function? | Use In Pseudocode | Evidence Status | Official Reference |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Service Action | Service Actions | Producer and consumer apps | Typed inputs | Typed outputs | No dedicated `Function` reference confirmed | Loosely-coupled backend reuse | Current official | [Service Actions](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/service_actions/) |
| `CallAgentV2` | `AIAgentBuilder` | `Logic > Service Actions > AIAgentBuilder` | `AgentId`, `ChatMessages`, `Tools` | `Response`, `TokenCount`, `ToolSelection` | No | AI agent function calling | Current official | [CallAgentV2](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/service_actions/callagentv2/) |

### 4.3 System Actions

#### Authentication system actions

| Name | Kind | Inputs / Parameters | Output / Return | Use In Pseudocode |
| --- | --- | --- | --- | --- |
| `Login` | Client action | `Username`, `Password` | `UserLoginResult` | `Call System Action Login(Username, Password)` |
| `GetExternalLoginURL` | Client action | `ReturnToURL`, `IdentityProvider` | `ExternalLoginURL` | `Call System Action GetExternalLoginURL(ReturnToURL: ..., IdentityProvider: ...)` |
| `Logout` | Client action | None | None | `Call System Action Logout()` |
| `GetExternalLogoutURL` | Client action | `CallbackURL` | `ExternalLogoutURL` | `Call System Action GetExternalLogoutURL(CallbackURL: ...)` |

#### User system actions

| Name | Kind | Inputs / Parameters | Output / Return | Use In Pseudocode |
| --- | --- | --- | --- | --- |
| `ChangePassword` | Client action | `Username`, `NewPassword`, `OldPassword` | `ChangePasswordResult` | Password update flow |
| `FinishResetPassword` | Client action | `Email`, `VerificationCode`, `NewPassword` | `FinishResetPasswordResult` | Password reset completion |
| `FinishUserRegistration` | Client action | `Email`, `Password`, `VerificationCode` | `RegistrationResult` | User registration completion |
| `FinishUpdateEmail` | Client action | `VerificationCode` | `FinishUpdateEmailResult`, `FinishUpdateEmailFailureReason` | Email change completion |
| `GetPasswordComplexityPolicy` | Client action | None | `PasswordComplexityPolicy` | Client-side password validation |
| `GetUserProfile` | Client action | None | `UserInfo` | Refresh logged-in user profile |
| `IsExternalUser` | Client function | None | `IsExternalUser` | Built-in identity branch logic |
| `StartResetPassword` | Server action | `Email` | `StartResetPasswordResult` | Password reset initiation |
| `StartUpdateEmail` | Server action | `Email` | `StartUpdateEmailResult`, `StartUpdateEmailFailureReason` | Email change initiation |
| `StartUserRegistration` | Server action | `User` | `StartUserRegistrationResult` | Built-in user registration initiation |
| `UpdateUserProfile` | Server action | `User` | `UpdateUserResult` | Profile update |
| `ValidatePasswordComplexity` | Client action | See official reference | See official reference | Client-side complexity check |

#### Workflow system actions

| Name | Kind | Inputs / Parameters | Output / Return | Use In Pseudocode |
| --- | --- | --- | --- | --- |
| `HumanActivityAssign` | Server action | `ActivityInstanceId`, `UserId` | None | Assign workflow task at runtime |
| `HumanActivityOpen` | Server action | `ActivityInstanceId` | None | Open human task |
| `HumanActivityRelease` | Server action | `ActivityInstanceId` | None | Release human task |
| `ProcessTerminate` | Server action | `ProcessInstanceId` | None | Terminate running workflow |

#### Standalone system action

| Name | Kind | Inputs / Parameters | Output / Return | Use In Pseudocode |
| --- | --- | --- | --- | --- |
| `GetDefaultDomain` | Server action | None | `DefaultDomain` | `Call System Action GetDefaultDomain()` |

**Evidence Status**: Current official
**Official Reference**: [System Actions](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/system_actions/)

### 4.4 Built-in Function Families

| Family | Examples from official index | Typical use in pseudocode | Evidence Status | Official Reference |
| --- | --- | --- | --- | --- |
| Data Conversion | `BooleanToText`, `DateTimeToText`, `DecimalToInteger` | `If BooleanToText(IsValid) = "True"` | Current official | [Data Conversion](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/data_conversion/) |
| Date and Time | `AddDays`, `AddHours`, `CurrDate`, `CurrDateTime` | `Assign DueDate = AddDays(CurrDateTime(), 7)` | Current official | [Date and Time](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/date_and_time/) |
| Email | Family documented in official index | Email validation and formatting helpers | Current official | [Built-in Functions](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/) |
| Format | `FormatDateTime` | `Assign Label = FormatDateTime(OrderDate, "yyyy-MM-dd")` | Current official | [Format](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/format/) |
| Math | Math family documented in official index | Numeric math in expressions | Current official | [Math](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/math/) |
| Numeric | Numeric family documented in official index | Number conversion and comparisons | Current official | [Numeric](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/numeric/) |
| Organization | Organization family documented in official index | Organization/date or stage-aware expression support | Current official | [Organization](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/organization/) |
| Text | Text family documented in official index | String search, trim, substring, comparison | Current official | [Text](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/text/) |
| URL | URL family documented in official index | URL parsing and manipulation | Current official | [URL](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/built_in_functions/url/) |

### 4.5 OutSystems Library Families

| Family | Representative actions from official index | Typical use in pseudocode | Evidence Status | Official Reference |
| --- | --- | --- | --- | --- |
| Binary Data | `Base64ToBinary`, `BinaryToBase64`, `BinaryDataSize` | File and binary transformations | Current official | [Binary Data library](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/libraries/binary_data/) |
| Date Time | `DiffMonths`, `DiffWeeks`, `IsLeapYear` | Date arithmetic beyond built-in functions | Current official | [Date Time library](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/libraries/date_time/) |
| HTTP | `Request_GetURL`, `Request_SubmitGetRequest`, `Response_SetStatusCode` | HTTP headers, cookies, status code control | Current official | [HTTP library](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/libraries/http/) |
| Math | `Random`, `Log10`, `Ceiling` | Math helpers | Current official | [Math library](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/libraries/math/) |
| Sanitization | `SanitizeHtml`, `VerifyJavascriptLiteral`, `BuildSafe_InClauseTextList` | Safe HTML, JavaScript literals, SQL IN clause helpers | Current official | [Sanitization library](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/libraries/sanitization/) |
| Security | `AES_Encrypt`, `ComputeHash`, `JWT_CreateToken`, `GenerateSecurePassword` | Security and cryptography | Current official | [Security library](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/libraries/security/) |
| Text | `Format_DateTime`, `Regex_Replace`, `String_Split`, `String_Join` | Text formatting and regex | Current official | [Text library](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/libraries/text/) |
| TextDictionary | `TextDictionary_Get`, `TextDictionary_Set` | Key-value text storage | Current official | [OutSystems language and elements](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/) |
| URL | `EncodeURL`, `DecodeURL`, `GetURLHost` | URL helpers | Current official | [URL library](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/libraries/url/) |
| XML | `XMLDocument_Load`, `XmlElement_GetAttributeValue`, `Xsl_Transform` | XML document handling | Current official | [OutSystems language and elements](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/) |
| Zip | `CreateZip`, `AddFile`, `CommitChanges`, `GetZipBinary` | Zip creation and extraction | Current official | [OutSystems language and elements](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/) |

### 4.6 JavaScript Extensibility Modules

| Module | Purpose | Use In Pseudocode | Evidence Status | Official Reference |
| --- | --- | --- | --- | --- |
| `ApplicationContext` | Current app/screen/module context | `Use $public.ApplicationContext...` | Current official | [JavaScript extensibility](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/javascript_extensibility/) |
| `ApplicationLifecycle` | App lifecycle state | Upgrade/load handling | Current official | same |
| `Device` | Native/device capabilities | Device integration | Current official | same |
| `FeedbackMessage` | Show client feedback messages | `Use $public.FeedbackMessage.showFeedbackMessage(...)` | Current official | same |
| `Logger` | Log messages/errors to ODC Portal | Client-side logging | Current official | same |
| `Navigation` | Navigation and history override support | Advanced navigation behavior | Current official | same |
| `Validation` | Validation message helpers | Widget validation in advanced cases | Current official | same |
| `View` | Active view state helpers | View/component coordination | Current official | same |

### 4.7 ODC Data Grid Reference Pack

| Group | Representative official items | Use In Pseudocode | Evidence Status | Official Reference |
| --- | --- | --- | --- | --- |
| Widgets | `Grid`, `TextColumn`, `NumberColumn`, `CurrencyColumn`, `DateColumn`, `DateTimeColumn`, `CheckboxColumn`, `DropdownColumn`, `ActionColumn`, `ContextMenu` | Grid UI composition | Current official | [ODC Data Grid reference](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/odc_data_grid_reference/) |
| Actions | `ArrangeData` | Grid data preparation inside server-side logic | Current official | same |
| Client Actions | `GetChangedLines`, `MarkChangesAsSaved`, `SetValidationStatus`, `AddNewRows`, `RemoveSelectedRows`, `GetSelectedRowsData`, `GetViewLayout`, `SetViewLayout`, `ActivateFilter`, `SearchData` | Grid runtime orchestration | Current official | same |
| Structures | `ChangedLines`, `RowData`, `RangeData`, `ErrorMessage`, `DropdownOption`, `Mandatory`, `OptionalConfigs` | Grid signatures and result typing | Current official | same |
| Static Entities | `AlignMode`, `DateOperator`, `Filter_OperatorType`, `Filter_Type`, `NumberOperator` | Grid option values | Current official | same |

### 4.8 AI And Agentic ODC Catalog

| Item | Scope | Key planning notes | Evidence Status | Official Reference |
| --- | --- | --- | --- | --- |
| Agentic app | App type | Runs on server, no UI, exposes capabilities to other apps through service actions | Current official | [agentic-apps.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agentic-apps.md) |
| `Call<AIModelName>` | AI model server action pattern | Direct model invocation from app logic | Current official | [add-ai-models.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/add-ai-models.md) |
| `Call<AgentName>` | Agent service action pattern | Consuming app calls agent app through service action | Current official | [agentic-apps.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agentic-apps.md) |
| AI models | ODC Portal + Studio | Provider-backed endpoints; public element consumed as server action | Current official | [add-ai-models.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/add-ai-models.md) |
| Search services | ODC Portal | Azure AI Search, Amazon Kendra, custom search | Current official | [add-ai-search-services.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/add-ai-search-services.md) |
| AI agent actions | Agent Flow | Server actions exposed to the model; metadata quality matters | Current official | [function-calling.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/function-calling.md) |
| Call condition | Agent Flow | Internal variables: `TokenUsage`, `LoopCount`, `TotalCallsCount` | Current official | [function-calling.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/function-calling.md) |
| Structured output | Agent call | Cannot be used in the same agent call as action calling | Current official | [structured-output.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/structured-output.md) |
| External tools | Agentic apps | Custom MCP servers and prebuilt connectors are officially documented tool approaches | Current official | [agentic-apps.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agentic-apps.md) |
| MCP imported tools | Agentic apps | Imported MCP tools are callable actions; unsupported MCP data structures must be resolved before import | Current official | [mcp-connectors.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/tools/mcp-connectors.md), [unsupported-structures.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/tools/unsupported-structures.md) |
| A2A external agents | ODC Portal + agentic apps | ODC supports external agents through A2A connections; generated `SendMessage` can be used as an action-calling tool | Current official | [agent-2-agent.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agent-2-agent/agent-2-agent.md), [using-agent-2-agent.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agent-2-agent/using-agent-2-agent.md) |
| `SendMessage` | Generated A2A server action | Created from an A2A connection; can be added to an agent call as a tool action | Current official | [using-agent-2-agent.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agent-2-agent/using-agent-2-agent.md) |
| Building agentic workflows | Workflows | Combine agents with automatic activities, parallel nodes, loops, and human review | Current official | [agentic-workflows.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/workflows/agentic-workflows.md) |
| Agent evaluations | ODC Portal quality workflow | Evaluates a published agent service action against datasets and expected behavior; not a Studio flow node | Current official | [about-agent-evaluations.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/about-agent-evaluations.md), [construct-dataset.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/construct-dataset.md) |
| Mentor Studio | ODC Studio AI assistant | Generates or modifies supported web app elements through natural-language prompts; verify generated changes manually | Current official | [how-it-works.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/agentic-development/mentor-studio/how-it-works.md), [capabilities.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/agentic-development/mentor-studio/capabilities.md), [ai-limitations.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/agentic-development/ai-limitations.md) |
| Consuming AI agents in apps | Consumer app pattern | `UserInput`, `SessionId`, `GenerateGuid`, deploy agentic app before consumer | Current official | [consumer-app.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/consumer-app.md) |
| Agent guardrails | ODC Portal configuration | Configured per agent in ODC Portal, not in Studio. Studio pseudocode for guardrails should note "configure in Portal" rather than showing Studio elements. Covers content filtering, topic restrictions, and PII handling. | Current official | `OutSystems/docs-odc:src/eap/building-apps/build-ai-powered-apps/guardrails.md`; `OutSystems/docs-odc:src/eap/building-apps/build-ai-powered-apps/configure-agent-guardrails.md` |
| AI call timeout handling | Async pattern | Long AI calls (>30s) require async wrapper or background processing; do not raise `Server Request Timeout` as the primary fix | Current official | [agent-long-running.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agent-long-running.md) |
| Agentic deployment order | Cross-app dependency | Deploy agent app before consumer app; reversing this order breaks `CallAgentV2` references at runtime | Course/example-backed | VPN-gated `outsystems-tech-content` query `Deploying assets`; otherwise `Unverified or blocked` |

## 5. Integration And Platform API Surfaces

This section separates Studio integration elements from ODC tenant/public platform APIs.

### 5.1 Studio REST integrations

| Element | Category | Key Properties / Parameters | Runtime / behavior notes | Evidence Status |
| --- | --- | --- | --- | --- |
| Consumed REST API | Integration definition | Base URL, auth, imported methods | Prefer encapsulation in a library for reuse | Current official |
| Consumed REST Method | Generated action under `Logic > Integrations > REST` | HTTP method, URL, input params, request body, response body, generated structures | Used like a server action in logic | Current official |
| `OnBeforeRequest` callback | Request customization | `Request` input; `CustomizedRequest` output | Can add or change headers, URL, request text | Current official |
| `OnAfterResponse` callback | Response customization | `StatusCode`, `StatusLine`, `Headers`, `ResponseText`, `ResponseBinary` | Runs before OutSystems processes the REST response | Current official |
| REST error handling | Exception path | Exception Handler with `All Exceptions`; optional OnAfterResponse manipulation | HTTP 400+ throws exception by default | Current official |
| Exposed REST API | Service definition | REST API name; version-style naming recommended | Creates endpoints after deployment | Current official |
| Exposed REST Method | Exposed action | `HTTP Method`, default/custom `URL Path`, input/output params | Default endpoint derived from method name and verb | Current official |
| Custom REST URL | Exposed method property | `URL Path` | URL parameters used in path must be mandatory | Current official |
| HTTP status customization | Exposed method logic | `Response_SetStatusCode(StatusCode)` | Use before `End` to return custom status codes such as `201` | Current official |

**Sources**: [consume-a-rest-api.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/integration-with-systems/consume_rest/consume-a-rest-api.md), [simple-customizations.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/integration-with-systems/consume_rest/simple-customizations.md), [handling-rest-errors.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/integration-with-systems/consume_rest/handling-rest-errors.md), [expose-a-rest-api.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/integration-with-systems/exposing_rest/expose-a-rest-api.md), [customize-rest-urls.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/integration-with-systems/exposing_rest/customize-rest-urls.md), [change-the-http-status-code-of-a-rest-api.md](https://github.com/OutSystems/docs-odc/blob/main/src/eap/integration-with-systems/exposing_rest/change-the-http-status-code-of-a-rest-api.md)

### 5.2 Platform/public APIs

| API area | What it is | Key notes | Evidence Status |
| --- | --- | --- | --- |
| ODC REST APIs | Platform APIs for automation and management | Separate from Studio visual language elements | Current official |
| Auth model | OAuth 2.0 / OIDC | Used to authorize access to public REST APIs | Current official |
| Usage model | Resource-oriented JSON APIs | Standard HTTP verbs and status codes | Current official |
| Domains | User/access management, portfolio management, build operations, deployments, dependency management, asset repository, asset configurations, external library generation, code quality | Useful for automation and governance, not for screen/action flow design | Current official |

**Pseudocode distinction**:

- Studio integration pseudocode: `Call REST Method GetCustomer(Id: CustomerId)`
- Platform automation pseudocode: `Call ODC REST API to list deployed assets`

**Source**: [ODC REST APIs](https://success.outsystems.com/documentation/outsystems_developer_cloud/odc_rest_apis/)

## 6. Execution And Transaction Semantics

These rules materially affect how you should describe logic and ordering in pseudocode.

### 6.1 Database isolation

- ODC uses `Read Committed`.
- Dirty reads are not allowed.
- Only committed data is visible to separate transactions and event handlers.

**Source**: [Database transaction isolation level](https://success.outsystems.com/documentation/outsystems_developer_cloud/outsystems_language_and_elements/database_transaction_isolation_level/)

### 6.2 Transaction boundaries

- Transactions start when logic performs a write operation such as `Create`, `Update`, `Delete`, `GetForUpdate`, and related write semantics.
- Transactions end with `Commit`, `Rollback`, or the end of the request.

**Planning implication**: if later logic depends on persisted visibility outside the current request boundary, call the appropriate commit action before crossing that boundary.

### 6.3 Events and committed visibility

- If an event depends on data created in the same transaction, commit before `Trigger Event`.
- Otherwise, the event handler may not see the new data.

### 6.4 Data mashup and external entity transaction notes

- When mixing OutSystems entities and external entities in the same aggregate, changed OutSystems data may not be visible to the mashup query until committed.
- Official docs explicitly recommend `CommitTransaction` before the mashup query in these cases.
- This applies to Server Actions, Service Actions, Client Actions, Data Actions, and Timers when the runtime path needs the committed data for the mashup.

### 6.5 Client/server sequencing

- Multiple `Run Server Action` nodes inside a Client Action mean multiple server round trips and multiple transactions.
- Prefer composing required server logic into a single Server Action where possible.

### 6.6 Query performance

- Avoid Aggregate or SQL nodes inside `For Each`.
- Prefer one outer query with joins or richer result shape over repeated inner queries.

### 6.7 Lifecycle timing

- `On Application Ready` blocks the initial screen render.
- `On Ready` and the first `On Render` do not guarantee screen data is already fetched.
- `On After Fetch` is the correct post-query hook when you need the data itself.

### 6.8 REST execution semantics

- Consumed REST methods raise exceptions when the HTTP response status is `400` or higher.
- `OnAfterResponse` can manipulate status/body before OutSystems raises the exception.

### 6.9 AI/agentic sequencing

- In an agent call, action calling and structured output cannot be combined in the same call.
- `Call condition` can stop execution based on `TokenUsage`, `LoopCount`, or `TotalCallsCount`.
- Official course material and deployment docs align on deployment ordering: deploy the agentic app before the consumer app/workflow that depends on it.

## 7. Pseudocode Authoring Rules

### 7.1 Naming conventions

- Use the real ODC element kind: `Run Client Action`, `Run Server Action`, `Trigger Event`, `Refresh Data`, `Send Email`.
- Use real parameter labels whenever the docs expose them.
- Refer to outputs using `<CallNode>.<OutputParameter>`.
- Refer to loop current item with `.Current`.

### 7.2 Canonical patterns

| Goal | Canonical pattern |
| --- | --- |
| Call reusable backend logic | `Run Server Action DoSignup(User: User)` |
| Call reusable client logic | `Run Client Action ValidateForm(Name: Name, Email: Email)` |
| Update local state | `Assign IsExecuting = True` |
| Branch logic | `If CheckManagerRole()` |
| Iterate records | `For Each EditedProducts` |
| Use loop current record | `Run Server Action UpdateProduct(Product: EditedProducts.Current)` |
| Use action output | `If StartUserRegistration.StartUserRegistrationResult.Success` |
| Refresh screen data | `Refresh Data GetOrders` |
| Raise a business exception | `Raise Exception UnavailableExternalSystem("Provider timeout")` |
| Catch integration failures | `Exception Handler All Exceptions` |
| Trigger async event | `Trigger Event OnPurchaseStarted(ProductId: ProductId)` |
| Send email | `Send Email WelcomeEmail(To: User.Email, Handle: User.Name)` |
| Wake timer | `WakeNightlySync()` |
| Use built-in function | `Assign DisplayDate = FormatDateTime(OrderDate, "yyyy-MM-dd")` |
| Use library function | `Assign SafeHtml = SanitizeHtml(UserInputHtml)` |
| Use system action | `Call System Action Login(Username, Password)` |
| Use Data Grid client action | `Run Client Action GetChangedLines(GridWidgetId: ProductGrid.Id)` |
| Consume REST method | `Call REST Method GetCustomer(Id: CustomerId)` |
| Call an agent | `Run Service Action CallAgentV2(AgentId: AgentId, ChatMessages: ChatMessages, Tools: Tools)` |
| Consume agent app capability | `Call Agent Service Action(UserInput: UserInput, SessionId: SessionId)` |
| Use external A2A agent | `Configure Call Agent > Action calling > Add Action SendMessage` |
| Evaluate an agent | `Run agent evaluation against published Call<AgentName> service action` |

### 7.3 Distinguish the element types explicitly

- `Visual flow nodes`: `Assign`, `If`, `For Each`, `Raise Exception`, `Refresh Data`
- `Callable actions`: Client Actions, Server Actions, Service Actions, REST Methods
- `System actions`: Authentication, User, Workflow runtime actions, `GetDefaultDomain`
- `Built-in functions`: expression-time functions such as `FormatDateTime`
- `Library actions/functions`: HTTP, Text, Security, URL, Sanitization, etc.
- `JavaScript extensibility APIs`: `$public.<Module>`
- `Platform/public APIs`: ODC REST APIs for tenant automation

### 7.4 Authoring rules for correctness

- Mention commits before event triggering or cross-transaction visibility when the logic depends on newly written data.
- Prefer one server action in pseudocode when the client would otherwise perform several server requests.
- Avoid describing Aggregate/SQL inside a loop unless the design explicitly accepts the cost.
- In agentic flows, state whether action calling, structured output, or both are involved. If both are needed, describe two distinct agent calls.

## 8. Coverage Matrix And Verification Gaps

### 8.1 Source-family coverage

| Source family | Final status | Notes |
| --- | --- | --- |
| OutSystems language and elements | documented | Used as the master language index |
| Client Action | documented | Included in visual elements and catalog |
| Server Action | documented | Included in visual elements and catalog |
| Service Actions | documented | Included in visual elements and catalog |
| System Actions | documented | Included in catalog |
| Built-in Functions | documented | Included at family level |
| JavaScript extensibility | documented | Included in catalog and JavaScript node notes |
| ODC Data Grid reference | documented | Included as first-class catalog section |
| Database transaction isolation level | documented | Included in semantics |
| ODC REST APIs | documented | Included as platform/public API area |
| ODC building-apps pages | documented | Used for Studio visual elements and runtime behavior |
| OutSystems/docs-odc | documented | Used as official verification fallback |
| ODC Architect | archived-only | Included as archived official cross-check |
| ODC Web Specialist | archived-only | Included as archived official training/reference support |
| ODC Agentic AI Specialization | course/example-only | Included for agentic examples and local workshop context |

### 8.2 Studio and language-family coverage

| Family / element set | Final status | Notes |
| --- | --- | --- |
| Screens | documented | Current official |
| Blocks | documented | Current official |
| Client Actions | documented | Current official |
| Server Actions | documented | Current official |
| Service Actions | documented | Current official |
| Data Actions | documented | Current official, usage-based rather than single standalone reference |
| Input Parameters | documented | Current official |
| Output Parameters | documented | Current official |
| Local Variables | documented | Current official |
| Client Variables | documented | Current official |
| Aggregates | documented | Current official |
| SQL nodes | documented | Current official |
| Events | documented | Current official |
| Timers | documented | Current official |
| Screen/block lifecycle handlers | documented | Current official |
| Workflow nodes | documented | Current official |
| System action families | documented | Current official |
| Built-in function families | documented | Current official |
| Library families | documented | Current official |
| JavaScript `$public` modules | documented | Current official |
| Data Grid widgets/actions/structures/static entities | documented | Current official |
| Studio REST consume/expose surfaces | documented | Current official |
| ODC public REST APIs | documented | Current official |
| AI models | documented | Current official |
| Search services | documented | Current official |
| Agentic apps | documented | Current official |
| AI agent actions | documented | Current official |
| Structured output | documented | Current official family discovered during implementation |
| External tools / MCP / connectors | documented | Current official |
| A2A external agents and `SendMessage` | documented | Current official |
| Agent evaluations | documented | Current official, not a Studio flow node |
| Mentor Studio authoring assistant | documented | Current official, not a runtime element |
| Consuming AI agents in apps | documented | Current official |

### 8.3 Candidate flow-node coverage

| Candidate node / concept | Final status | Notes |
| --- | --- | --- |
| `Start` | documented | Action flows and workflows |
| `End` | documented | Action flows and workflows |
| `Assign` | documented | Current official usage evidence |
| `If` | documented | Current official usage evidence |
| `For Each` | documented | Current official usage evidence |
| `Run Client Action` | documented | Current official usage evidence |
| `Run Server Action` | documented | Current official usage evidence |
| `Refresh Data` | documented | Current official |
| `Trigger Event` | documented | Current official |
| `Raise Exception` | documented | Current official |
| `Exception Handler` | documented | Current official |
| `Send Email` | documented | Current official |
| `Wake<TimerName>` | documented | Current official |
| JavaScript node | documented | Current official, but only partially property-documented |
| `Switch` | unverified | No strong official ODC language evidence found during implementation |
| `While` | unverified | No strong official ODC language evidence found during implementation |
| `Break` | unverified | No strong official ODC language evidence found during implementation |
| `Continue` | unverified | No strong official ODC language evidence found during implementation |

## 9. Provider And Course Notes

### 9.1 Public provider and degraded repository navigation

- Use the available public-provider role first; `workspace-knowledge-cc` and
  `outsystems-public-knowledge` are aliases for that same role.
- Search by topic and retain the provider's public page URL or repo-qualified
  identifier such as `OutSystems/docs-odc:src/...` in the evidence record.
- Only when neither alias is available, use exactly `docs-howtos`, `docs-odc`,
  `docs-product`, and `outsystems-ui` as an explicitly degraded, source-backed
  fallback. Do not add other repositories or replace missing evidence with
  model memory.

### 9.2 Internal ODC Web-Specialist Evidence

- Retrieve this internal official training/documentation evidence only through
  the separate VPN-gated `outsystems-tech-content` capability; if it is
  unavailable, keep course-specific claims `Unverified or blocked`.
- Relevant query topics include:
  - asynchronous processes
  - screen and block lifecycle events
  - exception and transaction handling
  - REST APIs
  - integrations
  - troubleshooting
  - best practices for logic and data management

### 9.3 Internal ODC Agentic-AI Evidence

- Retrieve official course/example evidence only through the separate VPN-gated
  `outsystems-tech-content` capability; if it is unavailable, keep
  course-specific claims `Unverified or blocked`.
- Relevant query topics and course assets include:
  - course PDFs for AI models, search services, structured output, image input, tools/connectors, MCP servers, timeouts, agentic patterns, workflows, and deployment guidance
  - workshop `.oml` apps such as `PR_Agent_WithMCPTools.oml`
  - `Consuming AI agents in apps`
  - current public-provider evidence for Mentor Studio, A2A, agentic apps, and
    agentic patterns, which takes precedence over older course-only evidence
    when they overlap

### 9.4 Course/example facts captured here

The following items are useful for planning and are explicitly preserved as course/example evidence:

- When deploying dependencies to a new stage, the agentic app should be deployed before the consumer app or workflow that depends on it.

### 9.5 How to extend this handbook later

If you want a stricter "full signature" version later, the next expansion steps should be:

1. Expand every built-in function family into item-level signature tables.
2. Expand every library family into item-level signature tables.
3. Expand each Data Grid client action into full parameter/return tables.
4. Expand AI/agentic pages into a dedicated AI appendix with exact ODC Studio labels for `Call Agent`, structured output, external tools, and MCP configuration paths.
