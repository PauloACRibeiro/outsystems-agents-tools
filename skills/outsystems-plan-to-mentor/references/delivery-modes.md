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

## MCP mode

Use when the user chooses option 2 and OutSystems MCP tools are available in the active agent.

This is MCP mode.

- Always write the Mentor-ready output file before sending anything.
- Use the cursor discipline and no auto-publish boundary from `outsystems-mentor-polling-behavior`.
- Preserve the structured spec, anti-failure guardrail, and show-before-firing discipline from `outsystems-spec-driven-build` when a full app spec is being converted.
- Send the already-written prompt through Mentor.
- Poll Mentor with cursor discipline.
- Save the terminal result under `docs/superpowers/reviews/`.
- do not publish automatically.
- Do not deploy, rollback, promote, package, push, or create pull requests.

If OutSystems MCP tools are unavailable, explain the gap and fall back to paste mode unless the user chooses to stop.
