# Agentic ODC - Routing Reference

> ODC error codes: see `../../shared/reference/odc-error-registry.md` for the canonical index of every code named below.

Open this file when the question involves AI model calls, agent creation, consuming agents, structured output, action calling, guardrails, Mentor Studio, A2A/external agents, MCP tools/connectors, agent evaluations, agentic workflows, or search services in ODC.

## Evidence note

Use the available public-provider role first: `workspace-knowledge-cc` and
`outsystems-public-knowledge` expose the same public retrieval role. Query it
for current public `docs-odc` evidence and retain repo-qualified identifiers in
review notes. For guardrail freshness, verify these four current sources:

- `OutSystems/docs-odc:src/eap/building-apps/build-ai-powered-apps/guardrails.md`
- `OutSystems/docs-odc:src/eap/building-apps/build-ai-powered-apps/configure-agent-guardrails.md`
- `OutSystems/docs-odc:src/eap/building-apps/build-ai-powered-apps/about-agent-evaluations.md`
- `OutSystems/docs-odc:src/eap/building-apps/build-ai-powered-apps/agent-long-running.md`

Only when neither public-provider alias is available, use local clones of
`docs-howtos`, `docs-odc`, `docs-product`, and `outsystems-ui` as an explicitly
degraded, source-backed fallback; do not rely on model memory alone. Use older
internal course/example evidence only through the separate, VPN-gated
`outsystems-tech-content` capability. Otherwise keep internal claims
`Unverified or blocked`.

Portal prerequisite rule: Current official routing evidence does not prove
tenant availability. A2A Studio pseudocode is meaningful only after the ODC
Portal connection is configured and tested. MCP Studio pseudocode is meaningful
only after the ODC Portal connection is configured, tested, and tools are
imported.

## Target Evidence Boundary

For an existing app target, route through
`references/live-target-evidence-matrix.md` before claiming that the app
contains agentic assets, AI model calls, External Logic, timers, events,
workflows, A2A, MCP tools, or imported connectors.

Current official documentation grounds product behavior and pattern shape, but
named-app claims require direct target evidence: an agent context row, AI model
connection, `ExternalLibrary` dependency, callable external logic action, timer
action, event action, workflow action, or other direct asset proof described by
the matrix. Dependency-chain evidence can support routing or accepted-risk
wording, but it must not be described as direct usage unless the direct asset
is visible. If proof is missing, hand off or block the confident path, or mark
the claim `Unverified gap`.

## Route by agentic question type

| Question | Primary file | Evidence class |
|---|---|---|
| Agentic development SDLC and architecture | `ODC-Agentic development in the SDLC` normalized public page or the matching `docs-odc` chapter | Current official |
| Mentor Studio workflow and how it works | `ODC-AI development in Mentor Studio` normalized public page and `docs-odc` `agentic-development/mentor-studio/how-it-works.md` | Current official |
| Mentor Studio capabilities and generation boundaries | `ODC-Capabilities and patterns for Mentor Studio` normalized public page and `docs-odc` `agentic-development/mentor-studio/capabilities.md` | Current official |
| Mentor Studio prompts for app modification | `ODC-Modify an app with AI in ODC Studio` normalized public page and `docs-odc` `agentic-development/mentor-studio/prompts.md` | Current official |
| Mentor Web app generation and prompts | `ODC-AI app generation in Mentor Web` and `ODC-Capabilities and patterns for Mentor Web` normalized public pages | Current official |
| Mentor known limitations | `ODC-Known limitations` normalized public page and `docs-odc` `agentic-development/ai-limitations.md` | Current official |
| Effective prompts for Mentor / AI-assist | `ODC-Effective prompts for Mentor` normalized public page | Current official |
| Agent guardrails - what they are and how to configure | `Agent guardrails` and `Configure agent guardrails` normalized public pages | Current official |
| AI models and search services - adding to an app | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/ai-models.md`, `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/add-ai-models.md`, and `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/add-ai-search-services.md` | Current official |
| Adding search services (vector/semantic) | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/semantic-search/using-semantic-search.md` | Current official |
| Integrating AI models and search services into flows | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/integrate-ai-models-logic-rag.md` | Current official |
| Agentic apps in ODC - what they are | `ODC-Agentic apps in ODC` normalized public page and `docs-odc` `building-apps/build-ai-powered-apps/agentic-apps.md` | Current official |
| Creating an agent in ODC Studio | `ODC-Creating an agent in ODC Studio` normalized public page and `docs-odc` `building-apps/build-ai-powered-apps/create-agent.md` | Current official |
| Consuming AI agents in apps (`Call<AgentName>` / `CallAgentV2`, consumer pattern) | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/consumer-app.md` | Current official |
| AI agent actions (action calling pattern) | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/function-calling.md` | Current official |
| Image input for AI models | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/image-input.md` | Current official |
| Structured output from AI model calls | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/structured-output.md` | Current official |
| Timeout handling on AI agent calls | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/agent-long-running.md` | Current official |
| Agentic patterns (multi-agent, orchestrator/worker) | `ODC-Agentic patterns` normalized public page and `docs-odc` `building-apps/build-ai-powered-apps/agentic-patterns.md` | Current official |
| Building agentic workflows | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/workflows/agentic-workflows.md` | Current official |
| A2A concepts and architecture | `ODC-Agent-to-agent communication in ODC` normalized public page and `docs-odc` `building-apps/build-ai-powered-apps/agent-2-agent/agent-2-agent.md` | Current official |
| Adding external agents through A2A and using `SendMessage` | `ODC-Adding external agents in the ODC portal using A2A` normalized public page and `docs-odc` `building-apps/build-ai-powered-apps/agent-2-agent/using-agent-2-agent.md` | Current official |
| MCP servers and imported tools | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/tools/mcp-connectors.md` and `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/tools/unsupported-structures.md` | Current official |
| Agent evaluations and datasets | `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/about-agent-evaluations.md`, `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/construct-dataset.md`, and `https://github.com/OutSystems/docs-odc/blob/main/src/eap/building-apps/build-ai-powered-apps/run-your-first-evaluation.md` | Current official |
| Reuse elements across agentic apps | `Reuse elements across apps` normalized public page, `Agentic apps in ODC`, `Consuming AI agents in apps`, and the `Agent architecture` best-practices reuse-rules table (weak app-to-app, strong library references; re-verified 2026-07-07) | Current official |
| Deploying agentic assets (order, dependencies) | Internal `Deploying assets` course/example evidence through VPN-gated `outsystems-tech-content`; otherwise `Unverified or blocked` | Course/example-backed when retrieved |
| Building AI-powered apps overview | `Build AI-powered apps` public evidence through the available public-provider role | Current official |

## Key pseudocode rules for agentic flows

- Keep `Call<AIModelName>`, `Call<AgentName>`, `CallAgentV2`, and `SendMessage` separate. They represent different invocation paths and deployment/runtime constraints.
- Mentor Studio is an authoring assistant, not a runtime element. Use it to shape implementation prompts, then verify generated screens, logic, data, and dependencies in ODC Studio.
- Structured output requires a typed output structure defined on the agent/model call. Do not combine action calling and structured output in the same agent call.
- Structured output with conversation memory: current official guidance is to serialize the structured output before `Store Memory` and deserialize it in the consumer. The stronger claim that the flow must assemble an assistant `AIMessage` from the structured answer is session-observed only — an `Unverified gap` under `references/omi-evidence-status.md`; do not treat it as load-bearing without current docs or a fresh bounded target observation.
- When a public entry point's response type changes, include the consumers that read the old shape in the same session as a packaging dependency check. This is a conservative packaging rule, not documented platform behavior; verify actual consumer impact against the target rather than asserting breakage.
- Action calling allows the agent to invoke Server Actions as tools; name these clearly and note that each tool action must be declared in the agent definition.
- Entity-resolution tools and stages return match provenance (which attribute matched: own name, pseudonym, identifier) alongside the match count, and prompts require confirmation on indirect matches even when exactly one candidate returns — a count-based disambiguation rail alone passes a single wrong-person pseudonym hit (session-observed; treat as design guidance, not platform behavior).
- A2A external-agent connections are configured in ODC Portal. The generated `SendMessage` server action can be used directly or added as an action-calling tool in an agentic app.
- MCP/prebuilt connector tools are external dependencies. Imported tools behave like callable server actions, but unsupported MCP data structures must be handled before import.
- Agent evaluations run against a published agent service action and a dataset. They are quality gates around agent behavior, not Studio runtime logic.
- Deploy the agent app before the consumer app; deploying in the wrong order breaks the `CallAgentV2` / `Call<AgentName>` reference.
- For long AI calls, use the dedicated long-running guidance. The pattern involves async wrapper or background processing and is not a simple timeout parameter change.
- Guardrails are configured in the ODC Portal, not in Studio; pseudocode should note "configure guardrails in Portal" rather than showing Studio elements for that step.

## Agent Guardrail Coverage Audit

Include `### Agent Guardrail Coverage Audit` in OMI answers when the request
creates or changes AI model calls, agent definitions, `Call<AgentName>` /
`CallAgentV2`, A2A `SendMessage`, MCP/imported tools, action calling,
structured output, agent evaluations, or AI model migration.

Do not include the audit for unrelated UI, data, REST, timer, or workflow work
unless the requested change materially changes AI or agent behavior.

Use this checklist:

- Portal boundary: guardrails are configured in ODC Portal through baseline
  guardrails and stricter agent-level guardrails, not Studio flow nodes.
- Risk filters: call out Prompt Attack Protection, Personal information
  exposure, and Harmful Content Filtering when the agent handles user prompts,
  sensitive data, or open-ended model responses.
- Enforcement action: identify whether the expected policy shape is Block
  request and raise exception, Mask sensitive data, log, and continue, or Log
  and continue. Agent-level guardrails can be stricter than baseline guardrails,
  not more lenient.
- Violation handling: if blocking is possible, add an exception path for
  `OS-ABRS-FM-40005`, a user-friendly message, and Portal monitoring through
  `MONITOR > Logs`.
- Evaluation gate: when prompts, tools, grounding, or guardrails materially
  affect behavior, describe an agent evaluation against the published agent
  service action with a dataset. Inspect execution trace details, including
  guardrail activity, before publish handoff.
- Runtime resilience: for long calls, decide between `Server Request Timeout`
  up to the documented 60 second pattern and an asynchronous
  queue/status/polling design. Treat malformed structured output, missing tool
  results, and external-agent failures as integration failures with typed
  fallback or a specific exception.

This audit is output discipline only. It does not authorize live Portal
changes, Mentor execution, publish, or tenant mutation.
