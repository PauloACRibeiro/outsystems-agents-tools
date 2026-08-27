# Delivery Modes

Ask this question after the patched plan passes the handoff scanner:

```text
1 - Create prompts ready to paste sequentially in Mentor in ODC Studio
2 - Send to Mentor using the OutSystems MCP
```

## Paste mode

Use when the user chooses option 1 or when OutSystems MCP tools are unavailable.

This is Paste mode.

- Write the Mentor-ready output file first.
- Produce sequential prompts ready to paste into Mentor in ODC Studio.
- Stop after reporting the output path.
- Do not attempt tenant mutation.
- If the user then explicitly asks for supervised paste execution, follow `references/paste-mode-execution-protocol.md` for the per-block paste, verify, and recovery loop.

## MCP mode

Use when the user chooses option 2 and OutSystems MCP tools are available in the active agent.

This is MCP mode.

- Always write the Mentor-ready output file before sending anything.
- Use the cursor discipline and no auto-publish boundary from `outsystems-mentor-polling-behavior`.
- Preserve the structured spec, anti-failure guardrail, and show-before-firing discipline from `outsystems-spec-driven-build` when a full app spec is being converted.
- Send the already-written prompt through Mentor.
- Poll Mentor with cursor discipline, sleeping the interval the poll advertises and at least ~30s (upstream plugin 0.16.0) — the advertised figure is a floor to raise, not one to obey downward.
- Save the terminal result under `docs/superpowers/reviews/`.
- do not publish automatically.
- If publish is separately approved, branch on the outcome rather than retrying: a `publish_start` refusal is answered by a further Mentor turn that completes the work, never by a second publish; and a `failed` carrying `indeterminate: true` has no observed outcome — re-poll `publish_status` with its `publication_key` or verify with `env_app`, and never re-publish. Full rules: `outsystems-mentor-implementation` execution-gates §3b.
- Do not deploy, rollback, promote, package, push, or create pull requests.

If OutSystems MCP tools are unavailable, explain the gap and fall back to paste mode unless the user chooses to stop.
