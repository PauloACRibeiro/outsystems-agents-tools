# The sprint loop manual — from installed to first app

You have installed the sprint loop pack and the OutSystems Public Knowledge
server (the two prompts in the README). This page is the shortest honest path
from there to a published app: one paste-ready prompt per step, and what to
expect back.

Two things to know before you start:

- **The loop is human-in-the-loop.** It stops and waits for you at six points —
  a stop is the design working, not a malfunction. Do not plan an unattended run.
- **This page is the quick start.** The full companion —
  [`sprint-loop-for-colleagues.md`](sprint-loop-for-colleagues.md), installed on
  your disk with the pack — explains each step's traps and is worth one full
  read before your first run.

## One-time setup that the install prompts did not cover

1. **Connect your OutSystems tenant.** In a terminal (replace the hostname with
   your tenant's):

   ```
   claude mcp add -s user --transport http outsystems https://<your-tenant>.outsystems.dev/mcp
   ```

   Then in Claude Code type `/mcp`, pick `outsystems`, and sign in with your
   normal OutSystems login. Confirm with one prompt: *"Check the outsystems MCP
   auth status and tell me which tenant I am connected to."*

2. **Install Superpowers** (owns steps 1–2; not redistributed here) — see the
   "Steps 1–2" section of the companion doc for the install command.

3. **Prove the wiring** with the first three prompts of
   [`post-install-checks.md`](post-install-checks.md) in a **new** conversation.
   If check 1 fails, the most common cause is the knowledge server's
   registration step — re-run the registration verification from its install
   document.

## The loop, one prompt per step

Work in an empty folder — one folder per app. After each step, read what came
back before moving on; the artifacts build on each other.

| # | Step | Paste this (adapt the bracketed parts) | You get, and the gate |
|---|---|---|---|
| 1 | Requirements | `Use superpowers:brainstorming — I want to build [two sentences about your app].` | A PRD after structured questions. **Gate: you approve it.** |
| 2 | Screen list | `Use the outsystems-screen-inventory skill on the PRD we just wrote.` | `screen-inventory.json` — every screen, its purpose, and the shared chrome decision. |
| 3 | Plan | `Use superpowers:writing-plans to write the capability plan from the PRD and screen inventory.` | An ordered build plan. **Gate: you approve it.** |
| 4 | Screen design | `Use the outsystems-ui-design skill for the [name] screen.` — once per screen | An HTML preview to react to, then a blueprint. **Gate: you approve each screen.** |
| 5 | Plan review | `Use the outsystems-plan-to-mentor skill to review the plan against the PRD.` | A coverage review; real gaps block until fixed or waived. |
| 6 | Build | `Use the outsystems-mentor-implementation skill to execute the patched plan on my tenant.` | Mentor builds phase by phase on your tenant. **Gates: every publish asks you first.** |
| 7 | Test | `Use the outsystems-bdd-tests skill to generate and run the test suite.` | Generated BDD tests executed against the running app — real pass/fail per scenario. |
| 8 | Grade | `Use the outsystems-runtime-ui-audit skill on [the app's runtime URL].` | A 16-criterion scored UI audit of the deployed app. |

Steps 4–8 also **seed and click through the app signed in** as part of their
own verification — if an agent reports a screen "done" that nobody has ever
rendered or clicked, that is a skipped step, not a finished one.

## When something goes wrong

| Symptom | What it is | Do this |
|---|---|---|
| The OutSystems token expired | Normal; tenant sessions are short | `/mcp` → re-authenticate `outsystems` → tell the agent "reauthorized, continue" |
| After re-auth the outsystems tools are *gone* | Known client issue | Exit Claude Code and run `claude --continue` from the same folder |
| Knowledge check fails after a "complete" install | Registration step was skipped | Run the registration verification from the knowledge server's install document |
| A Mentor run was mid-flight at token expiry | It may or may not have survived | After re-auth, ask the agent to check the run's status before assuming |
| A publish reports `no_changes_detected` | Nothing new deployed | The change did not land — do not treat it as published |
| The build step refuses to start | No knowledge provider reachable | That refusal is correct — fix the knowledge server rather than bypassing it |

## Updating

New pack versions ship regularly — the README's **"Updating the pack"** prompt
moves you to the latest release; updated skills load only in a new
conversation. Refresh the knowledge server's *content* with its own README
prompt; the two update independently.

**Found friction?** The bundler under
[`colleague-feedback/`](colleague-feedback/) packages your notes offline, with
tenant names and GUIDs redacted. Real runs are what improve these skills.
