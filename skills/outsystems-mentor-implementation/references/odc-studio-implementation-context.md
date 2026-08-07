# ODC Studio Implementation Context

This companion guide explains where ODC logic belongs, why OutSystems recommends certain implementation patterns, and which operational or security constraints should change how pseudocode is planned.

Use it together with:

- [ODC Studio Language Elements Handbook](./odc-studio-language-elements.md) for exact element names, parameters, outputs, and runtime syntax.
- [ODC Pseudocode Source Manifest](./odc-pseudocode-source-manifest.md) for total coverage, source classification, and auditability.

## 1. How To Use This Guide

Use this guide when the question is not only "what ODC element should I write", but also:

- where the logic should live
- whether the logic should be synchronous, asynchronous, scheduled, or workflow-driven
- whether an app, library, service action, event, timer, workflow, REST API, or external library is the right boundary
- what security, deployment, monitoring, or troubleshooting constraints should change the design

### Source precedence

1. Use the available public-provider role first: `workspace-knowledge-cc` and
   `outsystems-public-knowledge` expose the same public retrieval role.
2. Retain current public evidence as official URLs or repo-qualified
   `OutSystems/docs-odc:src/...` identifiers.
3. Only when neither public-provider alias is available, use local clones of
   `docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` as an
   explicitly degraded, source-backed fallback; do not rely on model memory
   alone.
4. Use internal course/example evidence only through the separate, VPN-gated
   `outsystems-tech-content` capability. Otherwise keep internal claims
   `Unverified or blocked`.

If a live source and an archived/course source differ, prefer the live source for current support and wording.

### Capability-routed corroborating references

- Public app, architecture, reuse, operational, and security exports are useful
  corroborating references when returned by the available public-provider role.
- Internal course/example context is optional supporting evidence only when
  returned by the VPN-gated `outsystems-tech-content` capability; otherwise
  keep the affected claim `Unverified or blocked`.

### Mapping rule

- Exact syntax, supported element behavior, and parameter labels belong in the language-elements handbook.
- Architecture, placement, implementation strategy, security posture, delivery lifecycle, and troubleshooting guidance belong here.
- Low-signal but still official material stays visible in the source manifest as `catalog-only`.

## 2. Architecture And Placement Rules

### Start with the runtime boundary

Choose the asset type before writing pseudocode.

| Requirement | Preferred ODC asset | Why |
| --- | --- | --- |
| UI interaction, local validation, screen state | `Screen`, `Block`, `Client Action`, lifecycle handlers | Keeps browser/mobile interaction close to the UI and avoids unnecessary server trips. |
| Fetching screen or block data | `Aggregate`, `Data Action`, `Refresh Data` | Matches ODC screen/block data flow and lifecycle. |
| Database writes, validations, integration calls, consolidated backend work | `Server Action` | Server-side authority, security checks, transactions, and lower round-trip cost. |
| Reusable backend capability across apps | `Service Action` | Weak dependency boundary with independent producer lifecycle. |
| Asynchronous cross-app reaction | `Event` and `Trigger Event` | Loose coupling and real-time async propagation. |
| Scheduled or deferred background execution | `Timer` and `Wake<TimerName>` | Fits batch, delayed, or periodic machine work. |
| Human approvals or long-running business process orchestration | `Workflow` | Explicit business-process asset with independent lifecycle and workflow nodes. |
| External system integration over HTTP | Consumed or exposed `REST API` | Native ODC integration surface with headers, status codes, and error handling. |
| Browser-side extensibility | JavaScript node and JavaScript extensibility APIs | Client-side extension only; treat CSP and browser constraints as first-class. |
| Private-network or high-code custom logic | External library / external logic | Separate execution context, separate latency model, stateless design required. |
| Platform automation and tenant management | `ODC REST APIs` | Official platform/public APIs, not Studio visual nodes. |
| AI model invocation | `Call<AIModelName>` | Use when a direct model call is enough. |
| Autonomous multi-step AI behavior | Agentic app and `Call<AgentName>` / `CallAgentV2` | Use when orchestration, tools, memory, or decision-making are required. |

### Choose app type early

From current ODC guidance:

- `Web app`: browser-first responsive UI.
- `Mobile app`: native mobile packaging or PWA distribution, mobile/offline/device concerns apply.
- `Agentic app`: server-side capability app without UI, consumed by web/mobile/workflow assets.
- `Library`: reusable code and UI building block layer, not a user-facing runtime by itself.

Pseudocode implication:

- If the logic depends on screen rendering or browser interaction, it does not belong in an agentic app.
- If the capability has no UI and should be consumed by other apps, consider an agentic app or service producer instead of a web app.
- If multiple apps need the same reusable logic or UI, push stable parts into libraries or service actions instead of duplicating flows.

### Model around bounded contexts and ownership

The app-architecture guidance consistently points to:

- identify business concepts first
- group them into bounded contexts
- keep clear ownership
- split apps when teams or business sponsors need independent change and release cadence
- prefer the balance between cohesion and loose coupling over arbitrary technical splits

Pseudocode implication:

- When describing a feature, state which app owns the capability before describing the flow.
- If one flow crosses bounded contexts, choose an explicit boundary: service action, event, workflow, or external integration.
- Avoid describing a single giant app flow if the real design should use separate apps with independent release cycles.

### Reuse strategy

- Use libraries for reusable code, UI, and public elements that do not need their own runtime.
- Use service actions when consumers need typed server capabilities across app boundaries.
- Use events when consumers should react asynchronously and independently.
- Use workflows when the process itself deserves an independent lifecycle and execution model.

### O11-to-ODC migration boundary

When the user is mapping O11 eSpaces to ODC assets, consult the internal
`migration-specialist` courseware only through the VPN-gated
`outsystems-tech-content` capability before writing pseudocode. If that
capability is unavailable, keep migration-specialist claims `Unverified or
blocked`. The asset boundary in ODC (App vs Library vs Service) does not match
the O11 eSpace layered structure (Foundation/Core/End-User), and pseudocode
written without this remap is likely to misplace logic.

Key files to consult:

- `map-o11-to-odc-architecture-for-coexistence-migration` — coexistence strategy
- `map-o11-to-odc-architecture-for-one-shot-migration` — full migration strategy
- `convert-o11-architecture-to-odc-architecture` — concrete remapping rules
- `map-o11-domains-to-odc-apps-and-libraries` — domain-to-asset mapping

Mark any pseudocode produced in an O11 migration context as `Mixed official+archived` unless the specific element is independently confirmed in current public ODC docs.

## 3. Build And Design Guidance

### Data management and modeling

ODC data guidance materially changes pseudocode quality:

- Model business concepts explicitly and isolate them well.
- Prefer relationships over duplicated attributes.
- Use static entities for predefined sets of values.
- Use settings for stage-configurable app-wide values.
- Remember that ODC turns the logical model into the physical model automatically.
- Data model changes only reach the database when you publish or deploy.

Pseudocode implication:

- Refer to stable entity or static-entity concepts instead of hard-coded text values.
- Prefer `Status = OrderStatus.Approved` over string comparisons.
- When describing writes, align them to entity relationships instead of manual denormalized copying unless there is a deliberate integration boundary.

### Logic best practices that should shape pseudocode

Current ODC best-practice guidance is clear:

- Avoid multiple `Run Server Action` calls inside the same `Client Action` flow when one consolidated server action can do the work.
- Do not put `Aggregate` or `SQL` inside `For Each`.
- Avoid isolating an aggregate in an action if returning whole records defeats field optimization.
- Avoid hard-coded values.
- Cache stable server actions when repeated requests return the same result.
- Validate permissions on server-side logic.
- Avoid exposing sensitive server actions on public screens.

Canonical planning implications:

- Prefer `Run Server Action SaveOrderAndLines(...)` over three separate sequential server calls from the client.
- Fetch full collections before loops.
- Use settings, entities, or static entities instead of literals when those values are business concepts or configurable values.
- Add explicit server-side role checks for sensitive writes, not just screen-role assumptions.

#### Performance anti-patterns (from adoption workshop Day 2)

Use this table only when the `Design For Performance` workshop material is
retrieved through the VPN-gated `outsystems-tech-content` capability. The
public-provider role and degraded public repositories do not supply workshop
evidence. If technical content is unavailable, keep these workshop-specific
claims `Unverified or blocked` and do not present the table as retrieved
evidence.

| Anti-pattern | Preferred pattern | Why |
|---|---|---|
| `Aggregate` or `SQL` inside `For Each` | Pre-fetch the full list before the loop with a single Aggregate; use joins or filters to consolidate | Avoids N+1 database queries that compound linearly with list size |
| Fetch all records then filter in memory | Use Aggregate filters and `Max. Records` to fetch only what is needed | Reduces data transfer and memory pressure |
| Uncached Server Action for static reference data | Set `Cache in Minutes` on the Aggregate or Server Action | Avoids repeated DB round-trips for stable data |
| Multiple sequential `Run Server Action` calls from one Client Action | Consolidate into a single Server Action that does the orchestration server-side | Eliminates extra client–server round-trips and keeps the unit of work transactional |
| Returning whole entity records when only a few fields are needed | Use a structure with the needed fields, or rely on Aggregate field optimization | Reduces payload size and serialization cost |

### Exception handling patterns

Sourced from web-specialist courseware (`Course/example-backed`) only through the
VPN-gated `outsystems-tech-content` capability, using the topics `Handling
exceptions` and `Exception Handling Mechanism`. If that capability is
unavailable, keep these course-specific claims `Unverified or blocked`.

**When to `Raise Exception` vs return a success-flag output:**

- Raise an exception when the caller cannot recover and the failure must abort the surrounding flow (e.g., invariant violation, integration unreachable).
- Return a typed output with a success flag when the caller is expected to branch on the outcome and continue (e.g., a validation that failed but the user can correct).
- Avoid exceptions for normal control flow — they unwind transactions and skew error logs.

**Where to place the `Exception Handler`:**

- Action level — handle failures local to a Server Action or Client Action, typically to log, transform, or rethrow.
- Screen level — global UI fallback (display message, navigate to error screen) for unhandled exceptions raised by client logic.
- Block level — for embedded UI components that own a self-contained failure surface.
- Match the handler's `Exception Type` to the most specific class; `All Exceptions` is a catch-all and should be the outermost handler only.

**Transaction behavior:**

- A raised exception in a Server Action rolls back the active transaction by default. Use `CommitTransaction()` deliberately if partial work must persist before the exception path runs.
- `Log Error` does not raise an exception by itself; it records to the runtime log. Exceptions caught by handlers are auto-logged as errors unless explicitly suppressed.

**REST and exception interaction:**

- Consumed REST methods raise an exception on HTTP `400+` status by default (see existing `### Consumed REST APIs`). Wrap the call in an Exception Handler for graceful degradation; use `OnAfterResponse` only when you need to manipulate the raw response before exception decision.

### Screen, block, and lifecycle placement

Use lifecycle moments intentionally:

- `On Initialize`: input-driven setup and first orchestration before interaction.
- `On Ready`: logic that depends on the UI already being rendered.
- `On Render`: rendering-related refresh behavior, with care to avoid loops.
- `On After Fetch`: post-fetch logic tied to aggregates or data actions.
- `On Parameters Changed`: react to changed input parameters in reusable blocks or screens.
- `On Destroy`: cleanup of local resources or subscriptions.
- `On Application Ready` and `On Application Resume`: app-level startup/resume behavior when officially available.

Pseudocode implication:

- If the flow depends on widget availability or browser APIs, place it in `On Ready`, not `On Initialize`.
- If the flow depends on newly fetched data, place it after fetch, not before the query returns.

### Async patterns

- Use `Event` for asynchronous app-to-app decoupling.
- Use `Timer` for scheduled or deferred machine work.
- Use `Workflow` for long-running, human, or multi-stage business process orchestration.

Do not collapse all asynchronous needs into timers. Events, timers, and workflows solve different problems.

### Teamwork and change management

The current and archived guidance on merge, breaking changes, and weak dependencies implies:

- design public surfaces deliberately
- assume reuse contracts matter
- watch for breaking changes in exposed functionality
- prefer clear boundaries over hidden cross-app coupling

Pseudocode implication:

- When describing a reusable capability, call out whether it is a public library element, service action, event, or workflow contract.

## 4. Integration And External Systems Guidance

### Consumed REST APIs

Consumed REST methods should be called from Server Actions when server-side
credentials, transaction control, validation, or consolidated backend
orchestration matters.

For consumed REST integrations:

- HTTP error status codes `400+` raise exceptions by default.
- Use `Exception Handler` to catch those failures in the calling logic.
- Use the `OnAfterResponse` callback when the response must be manipulated before ODC throws.
- Distinguish recoverable issues, fallback behavior, retry behavior, and user messaging.
- Keep token/OAuth handling and header customization explicit when integrations depend on them.

Pseudocode implication:

- Do not describe external API calls as guaranteed success paths.
- Add explicit exception and fallback paths around important REST method calls.
- When special transport behavior matters, note callback-based manipulation instead of pretending the REST method returns a clean business result directly.

**Web-specialist courseware patterns** (`Course/example-backed`, available only
through VPN-gated `outsystems-tech-content` queries for `Consume one or more
REST API methods`, `Handling REST Errors`, `Customize API request and response
headers`, and `REST API structures`; otherwise `Unverified or blocked`):

- **Authentication options:** API Key (header or URL parameter), Basic, OAuth2 (configured per stage in Portal). Prefer Portal-managed credentials over hard-coded values.
- **Header customization:** use `OnBeforeRequest(Request)` to add or modify headers; the callback runs once per call. Do not rebuild auth headers inline at every call site.
- **Response manipulation:** `OnAfterResponse(Response)` runs before ODC parses the response body. Use it to normalize non-standard error envelopes or to rewrite status codes when the upstream is misbehaving.
- **Generated structures:** REST import generates one structure per method input/output. When the same shape is reused across methods, refactor to a shared structure manually rather than relying on the generated copies.
- **`Server Request Timeout`:** the parameter exists on consumed REST methods. Increase it deliberately for known long calls; do not raise it as a default cure for slow integrations.

### Exposed REST APIs

For exposed APIs:

- Customize URLs intentionally.
- Use the right HTTP status code.
- Throw custom errors deliberately.
- Document the API surface if it is meant for external consumers.
- Treat token-based auth and key management as architecture concerns, not UI concerns.

Pseudocode implication:

- If the user asks where to implement an integration contract, the answer may be an exposed REST method rather than a service action.
- Service actions are for internal ODC consumption; exposed REST APIs are for external systems.

### External data and Data Fabric

The platform-architecture and integration docs matter here:

- Data Fabric does not persist external business data inside ODC as a normal app-owned store.
- It retrieves metadata and executes queries against external systems.
- Query results and parameters live in memory temporarily.
- Query statement caching exists for performance.

Pseudocode implication:

- Distinguish between ODC-owned data and externally sourced data.
- Do not describe external data fetches as if they were local entity reads when latency, ownership, or transactional guarantees differ.

### JavaScript and browser extensibility

- JavaScript is client-side extensibility.
- External browser libraries, async browser behavior, and CSP rules affect feasibility.
- Keep JavaScript usage purposeful and limited to what should truly happen in the client/browser layer.

### External logic

External libraries have a different execution model:

- every call is an HTTPS call to an external service
- design them as stateless
- pass needed context as input
- use `ILogger`, not console logging
- do not leak sensitive values into logs
- large binary payloads have input size limits
- use the `SECURE_GATEWAY` environment variable when private gateway access is required

Pseudocode implication:

- If you choose custom code, state that it is a remote call boundary with latency and failure behavior, not a normal in-process server action.

**Web-specialist courseware patterns** (`Course/example-backed`, available only
through VPN-gated `outsystems-tech-content` queries for `Extend your apps with
custom code`, `External Libraries SDK README`, and `Extending apps with
External Logic custom code`; otherwise `Unverified or blocked`):

**When to use External Logic vs other options:**

- **External Logic / external library** — when you need .NET code (CPU-bound work, complex algorithms, libraries not exposed by ODC), or when you must reach a private network resource via the secure gateway. The library is deployed as a separate ODC asset.
- **Consumed REST API** — when the capability already exists as a remote HTTPS service. Cheaper to set up; no .NET code to maintain.
- **Private gateway alone** — when the target is a private-network REST/SOAP service that ODC can call directly with the gateway tunnel; no custom code needed.

**SDK structure (external library entry point):**

- The SDK exposes the library as an annotated C# interface. Public methods on the interface become the Server Actions that ODC Studio imports.
- Each method's input and output types map to ODC structures generated on import. Keep types simple (primitives, structures of primitives) for predictable mapping.
- `ILogger` is the supported logging entry point — emitted entries surface in ODC runtime logs alongside app logs.
- The `SECURE_GATEWAY` environment variable signals that calls from the library should route through the configured private gateway.

**Deployment order:**

- The external library asset must be deployed (and its dependencies — provider-specific SDKs, configuration values) before the ODC app that consumes it.
- Updates to the library's public interface (added/changed/removed methods or parameters) are breaking for consumers; coordinate consumer redeployment.

## 5. Security And Enterprise Constraints

### Server-side authority

Security-sensitive logic belongs on the server:

- validate roles and permissions in server-side logic
- do not trust client-only checks
- do not rely on public-screen exposure for protection

Pseudocode implication:

- For create, update, delete, approval, or privileged reads, include a server-side authorization step explicitly.

### CSP and browser/mobile security

Content Security Policy guidance affects implementation:

- CSP applies to web and PWA apps, and to mobile apps under the supported MABS level
- it is stage-level, not per-app
- explicit `https://` is required for external domains on iOS
- iframe scenarios require `frame-ancestors` care
- over-permissive or under-specified directives can either break apps or weaken security

Pseudocode implication:

- When a design depends on external scripts, frames, maps, or browser-side SDKs, mention CSP implications and approved sources.

### Secrets, cookies, logging, and compliance

- Use secrets/configuration management for sensitive values.
- Do not hard-code credentials or security-sensitive endpoints.
- Log enough to troubleshoot, but never sensitive information.
- HIPAA/PCI pages are compliance context, not substitutes for concrete implementation rules.

## 6. Debugging, Testing, Deployment, And Troubleshooting Guidance

### Workflow publishing

- Workflows are published from the workflow editor and become available for execution after validation and publish to the Development stage.
- Use "Publish with message" when workflow revisions need traceability for collaboration or review.
- Workflow revision messages appear in revision history and conflict dialogs, so mention them when pseudocode includes workflow deployment or handoff steps.
- Source: `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/workflows/publish-workflows.md` (`Current official`, added in docs-odc on 2026-05-06).

### Debugging

Current debugger guidance changes how to reason about implementation:

- debugging is available only in Development
- publish before debugging
- choose the right mobile debugging target
- stepping into a service action from a consumer app is not supported
- debugger dates are shown in UTC, while client and server runtime contexts differ

Pseudocode implication:

- If a feature spans consumer app and service producer, plan troubleshooting around logs and traces as well as debugger limits.

### Testing

The testing guidance is not just tool-centric. It changes planning quality:

- define acceptance criteria early
- use Given-When-Then behavior framing
- keep scenarios business-behavior oriented, not UI-implementation prose
- involve product, development, and QA together
- reflect testing expectations in Definition of Ready and Definition of Done

Pseudocode implication:

- Feature pseudocode should align with behavior-oriented scenarios, not just low-level screen clicks.
- If a design is hard to test, treat that as an architecture smell.

### Deployment

`1-Click Publish` and deployment guidance matter operationally:

- apps compile to runtime artifacts and database synchronization scripts
- libraries compile differently and do not manage runtime data the same way as apps
- ODC follows a build-once, deploy-anywhere model
- deployment inconsistencies and rollbacks are first-class concerns

Pseudocode implication:

- Treat database model changes, library reuse, and cross-app dependencies as deployment concerns, not only coding concerns.

### Monitoring and troubleshooting

Use the ODC Portal monitoring model correctly:

- logs identify the problem
- traces help locate the problem
- analytics and metrics reveal health, usage, and error trends
- traces are server-side request oriented
- observability data retention in the portal is limited; streaming exists for longer retention

Pseudocode implication:

- For critical flows, describe expected logs, traces, or observable checkpoints when that will help debugging later.

## 7. Platform Management And Operational Implications

### Configuration management

ODC configuration management should change how you describe configurable behavior:

- settings can be changed per stage without redeploy
- timer configuration can be changed in the portal
- consumed REST integration settings can be updated in the portal
- apply is asynchronous

Pseudocode implication:

- Use settings and stage configuration for environment-specific values instead of embedding them into action logic.

### Timer patterns

Sourced from web-specialist courseware (`Course/example-backed`) only through the
VPN-gated `outsystems-tech-content` capability, using the topics `Create and run
Timers`, `Use Timers`, and `Monitor Timers`. If that capability is unavailable,
keep these course-specific claims `Unverified or blocked`.

**Ownership and asset boundary:**

- A `Timer` belongs to an App, not to a Library. Logic that must run on a schedule lives in (or is invoked from) the owning App.
- The Timer flow runs as a Server Action — same placement rules apply (transactions, security, integration calls).

**`Wake<TimerName>` system action:**

- Use `Wake<TimerName>` to trigger a Timer immediately on demand from a Server Action (e.g., after a user action that needs background processing).
- The schedule still applies — `Wake` causes one extra immediate execution, it does not replace the scheduled run.
- Calling `Wake` while the Timer is already executing does not start a second concurrent run; ODC serializes timer execution per Timer.

**Re-entry and overlap behavior:**

- If the next scheduled fire arrives while the Timer is still running, ODC does not start a parallel execution; the next fire is held or skipped per platform rules.
- Long-running timers should checkpoint progress (state in an Entity) so a re-trigger can resume from the last completed unit.

**Monitoring:**

- Timer execution logs and statuses appear in ODC Portal (Monitoring section). Use these to confirm the Timer ran, how long it took, and whether it succeeded or raised an exception.
- Exceptions raised in a Timer flow are logged automatically; they do not surface to a user UI.

**Pseudocode implication:**

- Frame scheduled work as `Timer ProcessOverdueOrders` with a flow body, then describe `Wake ProcessOverdueOrders` from the Server Action that should trigger it on demand.

### Runtime and platform architecture

The cloud-native architecture guidance matters for mental models:

- platform services and runtime stages are distinct
- runtime stages are isolated
- builds become containerized artifacts
- data platform powers analytics, audit, quality, and some AI-related data processing
- customer runtime databases are isolated per stage

Pseudocode implication:

- Separate platform/public API concerns from app runtime logic.
- Treat stage behavior, release flow, and runtime isolation as part of the implementation story when relevant.

### Network, access, and operations

Operational topics that can change implementation choices:

- private gateway for private-network access
- custom domains
- SSO and external identity providers
- IP filters and public IP allowlisting
- SMTP and email setup
- capacity and health signals

These are not usually pseudocode lines, but they often determine whether a proposed implementation is feasible.

## 8. AI And Agentic Implementation Guidance

### When to use AI models directly vs agents

Use direct AI model calls when:

- the capability is narrow
- the prompt/response contract is simple
- no tool orchestration or long-lived memory is required

Use agentic apps when:

- the capability must orchestrate steps
- the AI must decide between actions
- the solution needs grounding, memory, tools, or longer autonomous behavior
- the logic should be reused as a service capability by consumer apps or workflows

### Canonical agentic design

The official ODC agent guidance repeatedly converges on this pattern:

1. Configure AI model
2. Create agentic app
3. Define `GetGroundingData`
4. Define system prompt inside `BuildMessages`
5. Add server actions as agent actions when needed
6. Run `Call<AgentName>` / `CallAgentV2`
7. Persist memory with `StoreMemory`
8. Consume the published agent service action from a consumer app or workflow

Consumer-side guidance:

- capture `UserInput`
- manage `SessionId`
- use `GenerateGuid` or equivalent unique identifier generation
- deploy the agentic app before deploying consumer apps or workflows that depend on it

Each agent tool Server Action must validate caller permissions server-side; do
not rely only on the consumer screen, app role, or upstream agent prompt to
protect sensitive operations.

### Action calling, structured output, and control limits

Important ODC constraints:

- action calling and structured output are not used in the same agent call
- detailed action and parameter descriptions are critical to correct AI reasoning
- `Generated by AI` parameters delegate value creation to the model
- `Call condition` expressions are safety guards
- internal runtime variables like `TokenUsage`, `LoopCount`, and `TotalCallsCount` should shape safe agent design

### AI troubleshooting and enterprise concerns

- treat timeouts and long-running behavior explicitly
- test prompts and message flows deliberately
- add guardrails where the risk profile demands it
- treat MCP/tools/connectors as explicit external-dependency surfaces
- use agent evaluations as regression and quality gates for published agent service actions

### Mentor Studio authoring guidance

- Mentor Studio helps modify existing web apps in ODC Studio through natural-language prompts; it is not a runtime element and should not appear as a flow node.
- Keep Mentor prompts focused and name the target elements explicitly, such as `ValidateEmail`, `CustomerList`, or `SaveOrder`.
- Dependencies and public elements must be made available in ODC Studio before asking Mentor Studio to use them.
- Verify generated changes manually because Mentor Studio may report success even when the expected edit was not fully applied.

### A2A and external-agent integration

- Configure A2A connections in ODC Portal before using them in an agentic app.
- Current official routing evidence does not prove tenant availability.
- A2A Studio pseudocode is meaningful only after the ODC Portal connection is
  configured and tested.
- The generated `SendMessage` server action can be called directly or added to a Call Agent action as an action-calling tool.
- The external agent card drives the generated action description, so poor remote metadata reduces tool selection quality.
- A2A is an external-agent integration boundary; keep business validation and sensitive data filtering in ODC Server Actions before sending messages.

### MCP tools and connector import

- MCP server and prebuilt connector capabilities become imported tools/actions for agentic apps.
- Current official routing evidence does not prove tenant availability.
- MCP Studio pseudocode is meaningful only after the ODC Portal connection is
  configured, tested, and tools are imported.
- Unsupported MCP data structures need adaptation before import; do not show an unsupported structure as a valid ODC tool parameter.
- Treat imported tools like integration calls for error handling, timeout, security, and dependency review.

### Agent evaluations

- Agent evaluations target a published agent service action and use datasets to check behavior over repeatable conversations or tasks.
- Frame evaluation steps outside Studio pseudocode: prepare dataset, publish agent app, run evaluation, inspect results, then revise prompts/tools/guardrails.
- Use evaluations for prompt/tool regression checks when agent behavior quality is part of the requirement.

### Deployment order rule

- Deploy the agent app before the consumer app.
- Deploy Library dependencies before the apps that consume them.
- Reversing this order causes runtime reference failures on `CallAgentV2` / `Call<AgentName>`.
- Source: VPN-gated `outsystems-tech-content` query `Deploying assets`
  (`Course/example-backed`); otherwise `Unverified or blocked`.

### Timeout handling pattern

- Long AI model calls (>30s) require an async wrapper or background execution rather than synchronous Server Action with raised `Server Request Timeout`.
- Synchronous timeout extension is fragile; the recommended pattern is to fire the AI call from a background flow (Timer or async event) and surface results via state polling or notification.
- Source: `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agent-long-running.md` (`Current official`).

### AI call error handling

- Call<AIModelName> or CallAgentV2 failures should use an Exception Handler in
  the owning Server Action or orchestration flow.
- Log the failure, return a typed fallback result when the caller can recover,
  or raise a specific exception when the transaction must abort.
- Treat malformed structured output, missing tool results, and external-agent
  failures as integration failures, not as successful empty AI responses.

### Action calling architecture

- Each Server Action exposed as an agent tool must be declared in the agent definition (added as an "AI agent action" / function).
- Name tool actions clearly — the agent uses the action name plus its description to decide when to call it. Vague names degrade routing accuracy.
- Tool actions are Server Actions: they follow all standard Server Action placement rules (transactions, security, integration calls, etc.).
- Action calling and structured output cannot be used in the same agent call (see existing `### Action calling, structured output, and control limits`).

### Guardrails are Portal-configured

- Agent guardrails are configured in ODC Portal through baseline guardrails and
  stricter agent-level guardrails, not in Studio.
- Pseudocode answers about guardrails should note "configure guardrails in
  Portal for the agent" rather than showing Studio elements for that step.
- Current guardrail filters are Prompt Attack Protection, Personal information
  exposure, and Harmful Content Filtering.
- Current enforcement actions are Block request and raise exception, Mask
  sensitive data, log, and continue, or Log and continue.
- If a guardrail is configured to block, handle `OS-ABRS-FM-40005` with a
  user-friendly message and inspect guardrail events in ODC Portal logs.
- When an AI or agentic answer includes material safety risk, emit
  `### Agent Guardrail Coverage Audit` after `### Studio-Native Pseudocode` and
  before `### Evidence Status`.
- Source: `OutSystems/docs-odc:src/eap/building-apps/build-ai-powered-apps/guardrails.md`
  (`Current official`, retrieved through the available public-provider role or
  the approved degraded `docs-odc` repository fallback).
- Source: `OutSystems/docs-odc:src/eap/building-apps/build-ai-powered-apps/configure-agent-guardrails.md`
  (`Current official`, retrieved through the available public-provider role or
  the approved degraded `docs-odc` repository fallback).

## 9. Decision Tables And Anti-Patterns

### Quick placement table

| If the requirement says... | Usually implement in... | Avoid... |
| --- | --- | --- |
| change widget state or local UI validation | `Client Action` | server calls for pure local behavior |
| fetch data for a screen | `Aggregate` or `Data Action` | ad hoc server-action wrappers around simple fetches without reason |
| save data and validate permissions | `Server Action` | trusting client-side validation alone |
| reuse capability across apps | `Service Action` or library public element | copying the same flow into multiple apps |
| react after another app commits business data | `Event` consumer | tightly coupled synchronous cross-app chains when async fits |
| run nightly or delayed batch work | `Timer` | user-triggered UI flows for background scheduling |
| manage approval or human task process | `Workflow` | overloading timers or client actions for business process orchestration |
| call private network code or special SDK logic | external library | pretending it behaves like normal in-process server code |
| automate tenant/platform tasks | `ODC REST APIs` | building those operations as Studio flows only |
| build autonomous AI capability | agentic app | using direct model calls for multi-step tool orchestration |
| call an external AI agent | A2A connection + generated `SendMessage` action | treating the external agent as a normal internal Service Action |
| import external agent tools | MCP/prebuilt connector import | inventing unsupported tool parameter structures |
| improve agent quality | agent evaluation dataset + evaluation run | relying only on one manual prompt test |
| ask AI to modify an app | Mentor Studio prompt, then manual Studio verification | presenting Mentor Studio as runtime pseudocode |

### Anti-patterns to call out in future pseudocode

- Multiple sequential `Run Server Action` nodes inside a client flow when one consolidated server action would do.
- `Aggregate` or `SQL` inside `For Each`.
- Hard-coded business statuses, feature flags, endpoints, or secrets.
- Client-only authorization for sensitive operations.
- Treating service actions as if they were external public APIs.
- Treating ODC REST APIs as Studio visual elements.
- Using action calling and structured output in the same agent call.
- Treating Mentor Studio, A2A configuration, MCP import, or agent evaluations as normal Studio flow nodes.
- Designing external libraries as if they were stateful in-process code.
- Ignoring deployment order between agentic producers and consumers.

## 10. Coverage Summary Linked To The Manifest

This guide is intentionally filtered for pseudocode usefulness. Exhaustiveness lives in the manifest:

- Snapshot counts from the audit captured in the manifest: current official markdown chapters inventoried `626`
- Snapshot counts from the audit captured in the manifest: local archived/course assets inventoried `163`
- Audit ledger: [ODC Pseudocode Source Manifest](./odc-pseudocode-source-manifest.md)
- Treat these counts as dated inventory metadata unless the manifest is regenerated from the current workspace governance files.

Use the manifest when you need to prove:

- that a source family was reviewed
- how a chapter was classified
- whether a source was distilled into this guide, the language-elements handbook, both, or manifest-only

Use this guide when you need to decide how ODC logic should be structured and justified.
