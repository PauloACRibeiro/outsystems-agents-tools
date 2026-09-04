# The OutSystems sprint loop for colleagues, steps 1–7 (+ grading)

This is the loop for taking an OutSystems screen or feature from an idea to a
published, graded revision — and, just as importantly, the order the steps have
to run in.

It is a **human-in-the-loop** workflow. An agent does the typing; you review and
approve between steps. There are six points where the loop stops and waits for a
person, and none of them is optional. Do not plan an unattended run.

Read this once end to end before your first run, then use it as the checklist.

## What you need

- **Claude Code or Codex.** Every step below works on both. Steps 1–2 come from
  a plugin that installs separately per harness (see below).
- **An OutSystems ODC tenant** for steps 5 and 6 — one where you are allowed to
  create an app, run Mentor, and publish. Use a non-production environment for
  your first run.
- **Node.js and Google Chrome** for the grading step. The capture script drives
  your installed Chrome through Playwright; it installs one npm package into a
  scratch folder and does not download a browser.
- **A GitHub login is NOT required to run the loop.** Nothing in steps 1-7 signs
  in to GitHub, and the feedback bundler is offline and read-only — it writes a
  `.tgz` you email, and uploads nothing. One optional capability needs a login:
  regenerating `outsystems-ui-design`'s built-in widget inventory, which reads an
  OutSystems-internal repository. If you skip it the design skill still works,
  degraded, falling back to documented guidance instead of verifying widget
  properties against the inventory.
  If you do want it and browser sign-in is refused because your machine is not
  enrolled in company MDM, **that is not a dead end**: a classic personal access
  token works from an unmanaged machine — measured on one whose browser login had
  just been refused. The skill's `skills/outsystems-ui-design/references/built-in-widgets-regeneration.md`
  carries the procedure, including the SSO authorization step people miss and the
  trap where regenerating a token silently drops that authorization.
- **The seven skills in this pack**, installed into your agent's skills
  directory, in loop order: `outsystems-sprint-init` (step 0, run once per new
  app folder — it checks the rest of this list is actually installed and wired,
  and tells you the next step whenever you lose your place),
  `outsystems-screen-inventory`, `outsystems-ui-design`,
  `outsystems-plan-to-mentor`, `outsystems-mentor-implementation`,
  `outsystems-bdd-tests`, and `outsystems-runtime-ui-audit`. Follow
  the bundled release install document for your OS
  (`INSTALL-SPRINT-LOOP-MACOS.md` / `INSTALL-SPRINT-LOOP-WINDOWS.md`, attached
  to the same release you downloaded this pack from).
  **Testing is a required step, not an optional one** — see Step 7 below.
  The quick-start manual's full step order also carries a seeding step after
  the build and a render gate step after testing; the render gate skill is
  `outsystems-render-gate` (not part of the colleague sprint-loop pack) — without it,
  click every control on every screen by hand before grading.
   Between publish and the first test — no skill owns this — you seed demo
   data yourself through the app's own create screens; see "Between steps 6
   and 7 — Seed demo data" below.
- **An OutSystems knowledge server for step 5.** The build skill refuses to
  produce pseudocode ungrounded: before any output it checks for a knowledge
  provider, and if none is reachable it stops and waits. The **OutSystems
  Public Knowledge MCP server** satisfies it and ships in the same release as
  this pack — install it before your first run (see below).
- **The OutSystems MCP plugin, if you want the loop to touch your tenant.**
  This is the difference between the two delivery modes, so it is worth deciding
  up front rather than discovering at step 5. **Without it you are in paste mode:**
  the loop still runs end to end and still produces everything — plans, blueprints,
  pseudocode, paste-ready Mentor prompts — but nothing reaches your tenant until
  you run those prompts yourself in Mentor Studio. **With it you can use direct
  mode:** step 5 drives the Mentor edit for you and step 6 publishes, each edit
  approval-gated on the exact step about to run. Paste mode needs no tenant
  connection at all and is a perfectly good first run. Install instructions and the
  OAuth walkthrough are in step 6 below and in the plugin's own repository:
  <https://github.com/OutSystems/outsystems-mcp>

You do **not** need a VPN, and you do not need an OutSystems employee account —
the Public Knowledge server stands in for the VPN-only internal one.

## Where the pieces come from

| Steps | Owned by | How you get it |
|---|---|---|
| 1–2 | The public **Superpowers** plugin | Installed separately — see below. Not redistributed here. |
| 0, 3, 4, 5, 7, grading | The seven skills in **this pack** | Install per the bundled `INSTALL-SPRINT-LOOP-<OS>.md`. |
| 5 (knowledge) | The **OutSystems Public Knowledge MCP server** | Same release as this pack, own install docs — see below. |
| 5 (direct mode), 6 | The public **OutSystems MCP** plugin | Optional — paste mode needs no tenant. `outsystems@outsystems` — see below. |
| Between 6 and 7 | You, through the app's own create screens | No skill owns this — see "Between steps 6 and 7 — Seed demo data" below. |

### Steps 1–2 — install Superpowers yourself

Steps 1 and 2 are the idea-to-plan half of the loop, and they are owned by the
public Superpowers plugin. We do **not** redistribute it. Install it from the
official source and follow that project's own instructions:

- Project home: <https://github.com/obra/superpowers>
- Claude Code marketplace listing: <https://claude.com/plugins/superpowers>

For **Claude Code**, the official instruction is to install from Anthropic's
official plugin marketplace:

    /plugin install superpowers@claude-plugins-official

For **Codex**, Superpowers is listed on the official Codex plugin marketplace
(<https://github.com/openai/plugins>): open the plugin search with `/plugins`,
search for `superpowers`, and choose *Install Plugin*. In the Codex app, it is
under **Plugins → Coding**.

If either command has moved on, the project home above is the authority — use
its README rather than this page.

### Step 5 — install the OutSystems Public Knowledge MCP server

Step 5's build skill, `outsystems-mentor-implementation`, will not produce
pseudocode or Mentor prompts ungrounded. Before any output it checks for a
knowledge provider, and if none is reachable it stops and waits for you. Two
providers satisfy it:

- **The OutSystems Public Knowledge MCP server** — grounded in the public
  OutSystems documentation; no VPN, no employee account. It ships in the **same
  release you downloaded this pack from**, with its own per-OS install
  instructions. Paste this into Claude Code or Codex:

  ```text
  Install the OutSystems Public Knowledge MCP server on this machine.

  Detect my OS, then download and follow the matching instructions:
    macOS:   https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-MACOS.md
    Windows: https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-WINDOWS.md

  Follow that document literally. Confirm the install root and the
  prerequisites with me before you write anything to disk. The install takes
  6-10 minutes, so run it backgrounded. When you are done, verify it and tell
  me the version, the install root, the doctor result and the tool count.
  ```

- **The internal tech-content server** — OutSystems employees on a trusted
  machine, over VPN. Implementation-level authority, a strict upgrade over the
  public server. If you already run it, you are covered and can skip the
  public install.

Install one of them before your first run — finding out at step 5 costs you a
session.

### Step 6 — install the OutSystems MCP plugin

Everything that touches your tenant — running a Mentor edit in step 5's direct
mode, and publishing in step 6 — goes through the public OutSystems MCP plugin:
<https://github.com/OutSystems/outsystems-mcp>

For **Claude Code**, the official instructions are:

    claude plugin marketplace add OutSystems/outsystems-mcp
    claude plugin install outsystems@outsystems

**Installing the plugin does not register a server, and you do not register
one by hand.** Step 0 of the loop (`outsystems-sprint-init`) writes a
`.mcp.json` in your project folder that registers the server as
`outsystems-<slug>`, pointing at the `mcp_url` in that project's
`outsystems.toml` — your `<your-company>.outsystems.dev` hostname. Claude Code
asks you once to approve that project-scope server on the next start. Each
project gets its own OAuth client this way on purpose: ODC rotates refresh
tokens on every use and revokes the family on reuse, so one user-scope
`outsystems` registration shared by concurrent sessions forced a re-login
every 30–90 minutes. The step 0 doctor rejects a generic `outsystems` name in
the project `.mcp.json` and warns when that file also carries one. It reads
only that file: it cannot see a user-scope registration, so if you made one
earlier, remove it yourself with `claude mcp remove -s user outsystems`.

Add no `--client-id` and no `--callback-port` anywhere: the server supports
OAuth Dynamic Client Registration, so Claude Code registers its own client on
an ephemeral loopback port, and pinning either of those breaks it.

If a tenant call fails with `No MCP server named "outsystems-<slug>"`, step 0
has not run in this folder yet, or you started the conversation somewhere
else — the registration is per project folder.

The repository README has the OAuth walkthrough and best-effort recipes for
Codex and other harnesses. Always install as `outsystems@outsystems`; the bare
plugin name is not enough to update it later.

**Order matters: authenticate first, restart second.** Authentication state
lives in your configuration, not in the session — `claude mcp login
outsystems-<slug>` (browser sign-in), confirm `claude mcp list` shows `✔ Connected`,
and only then start a new conversation. A conversation started before the
login binds an unauthenticated server and will never see the tools, however
many times you restart the client (a real first run spent two restarts
learning this). If login fails with `403 tenant_not_allowed`, that is a
server-side allowlist — nothing on your machine fixes it; contact OutSystems.

**The same command is your reconnect step.** The connector token lasts roughly
ten hours, so a full day's work outlives it — it expired twice during one real
run. When tenant tools stop responding, or `claude mcp list` stops showing
`✔ Connected`, run `claude mcp login outsystems-<slug>` again and start a new
conversation, exactly as on the first login. An expired token does not
announce itself as an auth problem; it looks like the tenant going quiet.

## The loop

### Step 1 — Idea and requirements

**Skill: `superpowers:brainstorming`** (or a hand-written PRD.)

**Invoke it by name.** Start the conversation with "Using
superpowers:brainstorming, help me turn this idea into requirements and a
screen inventory:" followed by your idea. Do not just paste the idea cold — an
idea-shaped prompt can route straight to the step 5 build skill instead,
skipping requirements, plan, and design entirely (this happened on a real
first run). Naming the skill removes the gamble.

You bring the idea; you get back requirements plus a **screen inventory** — how
many screens, what each one does, and what navigation or header they share.

Deciding the screen list is still a manual judgement call. No skill does it for
you, and it is the biggest hands-on step on an app with six or more screens.

### Step 2 — Capability plan

**Before this step, on an app of three screens or more:** run
`outsystems-screen-inventory` on the PRD first — it decides the screen list and
the one chrome decision every design run shares, and the plan reads its entity
names from that inventory. The quick-start manual
(`sprint-loop-manual.md`) carries the loop in that order.

**Skill: `superpowers:writing-plans`.**

You get back an implementation plan written in terms of **business capabilities
and data intent** — not a list of ODC Studio elements to click. That boundary is
enforced at step 4, which will reject a plan that crosses it.

**Read this before you run step 2.** The plan generator is generic, and its own
mandated plan header and hand-off section are exactly what step 4's checker
rejects — every pattern it forbids, in the generator's default output. It also
wants exact file paths, code blocks, test commands and per-task commits in every
step, which is the element-by-element recipe this loop deliberately avoids.

The fix is cheap if you do it up front and expensive if you do not: run
`outsystems-plan-to-mentor` **before** the plan is written, in its pre-plan mode,
and hand its capability-plan brief to the generator. The brief wins on the
document contract — header, section shape, level of detail. Take task
decomposition, right-sized units and the no-placeholders discipline from the
generator. Skip this and you find out at step 4, and only a plan rewrite fixes it.

### Step 3 — Screen design, one run per screen

**Skill: `outsystems-ui-design`.**

You bring **one wireframe** — a photo of a hand sketch, a screenshot of a
comparable app, a Figma frame export, a quick HTML mock — plus the entity names
from your plan. The skill maps every visual region to a named OutSystems UI web
block, renders a local HTML preview each round so you can see what it understood,
and emits a validated `blueprint.json` when you approve it. Nothing touches your
tenant here; blueprints are local files until step 5.

Two things to know:

- **It is deliberately single-screen.** A five-screen app is five runs sharing
  one screen inventory and one navigation decision made up front. Decide those
  first with `outsystems-screen-inventory`: it turns your requirements document
  into one `screen-inventory.json` holding the screen list, the archetype and
  behaviour per screen, the entity and action bindings by name, the single shared
  chrome decision, and the navigation between screens. Every per-screen design
  run then reads that file instead of re-deciding the archetype each time. Under
  three screens, skip it and go straight to the design loop.
- **Declare `assertions` on every screen** — for example
  `"assertions": {"buttons": 10, "inputs": 1, "links": 0}`. The validator
  recounts those from the screen's content and hard-fails a mismatch. It is the
  one mechanism that checks a blueprint against *itself* rather than against a
  format, and it costs one line per screen.

If your app already exists, bind what is already there rather than describing it
again: a region can point at an existing app block, and an entity can be marked
as already present. Step 5 then folds them into modification steps. Without those
bindings, a blueprint that follows every other rule tells the build to recreate
what you already have.

### Step 4 — Plan review

**Skill: `outsystems-plan-to-mentor`.**

It reviews your plan against the requirements, patches the gaps, and hands the
patched plan to the build skill. It also runs a platform-feasibility pass with
real teeth: nothing converges while a row is infeasible or unverified.

**This is also where you reconcile the two routes by hand.** The plan and the
blueprints are separate contracts on purpose — the plan owns capabilities and
logic, the blueprints own the data model and screen structure — and keeping them
separate is what stops the plan turning into an element recipe. But two things
only a person checks:

1. **Entity names must match** between the plan and the blueprints. If the app
   already exists, derive both from one inventory of the existing app and they
   cannot disagree. On a greenfield screen this check is doing real work.
2. **Block choices are platform claims too, and nothing audits them.** The
   feasibility pass reads the plan, not the blueprints, and the design
   validator checks format, not platform truth. While you have both files open,
   eyeball the blueprint's block list against the official OutSystems UI
   catalog and raise anything the documentation does not confirm.

One more thing this step must produce: the **cross-route build order** (see
"Ordering rules" below). It is a property of the combined build, so neither the
plan nor the blueprints carry it on their own — state it explicitly in the
hand-off, because nothing downstream will notice if it is missing.

### Step 5 — Build

**Skill: `outsystems-mentor-implementation`.** Needs the knowledge server from
"Step 5 — install the OutSystems Public Knowledge MCP server" above; without a
provider the skill stops before producing anything.

**Let the agent create the app, or create it yourself in ODC Portal or Studio —
either works now.** The MCP's app-creation call clones the standard application
template by default, the same thing the ODC Studio new-app wizard does, so the
app arrives with a theme, layouts, and the `Common` flow that carries Login,
password recovery, user profile, and the "you don't have permission" screen.
Until August 2026 it could not do this, and an app built on the bare shell it
produced rendered as unstyled HTML with no route by which anyone could sign in
— so any screen you restricted by role became unreachable rather than
protected. If you are following an older copy of this runbook that tells you to
create the app by hand, that is why.

Three things still worth knowing. The build skill checks what the created app
actually contains rather than trusting that the template arrived, and it will
stop and ask if it finds itself pointed at a shell with no template assets —
that gate is deliberate, and it is what protects you if your tenant has not yet
picked up the newer server. Names are compared with spaces removed, so `My App`
and `MyApp` collide, and a leftover shell will block the name you actually
want. And there is no delete call: an app that has never been published is
invisible in the ODC Portal, so clearing one out means publishing it first and
then deleting it there.

Two routes feed it, and they stay separate:

- **Route A — logic and capabilities.** Driven by the patched plan from step 4,
  turned into ODC Studio-native pseudocode and Mentor prompts.
- **Route B — screens.** Consumes each `blueprint.json` directly: typed
  entities, seeded records, region-to-block mapping. These are the blueprint's
  own design-time seed values, not the discriminating dataset you add after
  publish — see "Between steps 6 and 7 — Seed demo data" below.

**Build order across both routes, and it is dependency-safe rather than
cosmetic:** entities and data prerequisites first, then the plan logic and server
actions the screens will call, then the screens and their wiring. A screen with
no logic dependencies can be created as soon as its entities exist.

Two delivery modes. In **paste mode** you get prompt artifacts only — nothing is
built until you run them yourself, so this mode needs no tenant at all. In
**direct mode** the edit runs against your tenant, and every edit is
approval-gated on the exact step about to run.

Theme and branding do not come along automatically. Blueprints carry structure
plus basic colour seeds; the full visual identity — brand palette, dark mode — is
a separate, explicit theme instruction during this step. Ask for it.

### Step 6 — Run it on your tenant, and publish

**Plugin: the public OutSystems MCP plugin, installed as `outsystems@outsystems`.**

This is where the loop meets your tenant. Two distinct approvals live here:

- **Each Mentor edit** is approved individually, immediately before it runs.
- **Publishing the revision** to Development is its **own** approval. A Mentor
  edit is not a published app, and the grading step needs a published one.

Practical habits from real runs:

- **One bounded objective per Mentor session.** Scaffold, publish, check, then
  iterate — never one big session that tries to do everything. Large asks make
  the model rewrite more than you wanted.
- **Check that something actually changed** before you grade anything. Read the
  app's model digest before and after each iteration. Unchanged means the
  iteration failed, whatever the status said — investigate, do not grade.
- **Give every publish a short message** naming the run and objective. The
  revision note becomes your run log on the server side.
- **Route errors by their category, not their message text.** A validation error
  means your prompt or plan is wrong — fix it, do not blind-retry. Upstream or
  internal errors get one retry, then a pause. An auth error means re-authenticate.
- **Check the auth status before a long turn, but do not expect it to save
  you.** Your tenant token expires on a shorter cycle than a heavy build turn
  takes — about hourly against turns of five to twenty minutes on the run behind
  these notes — so expiry lands mid-turn more often than between turns. The auth
  status is a snapshot of whether the token is alive at that moment; it does not
  report how much life is left, so it can stop you starting a twenty-minute turn
  on a token that has already lapsed and it cannot tell you whether a live one
  will last the turn. Ask for it before a big turn anyway — it is the only part
  of this you control — and plan on the interruption arriving regardless.
- **After re-authenticating, ask what happened to the run in flight.** A turn
  interrupted by an expiry has been measured going both ways: once it kept
  building on the server and finished with nothing lost, once the agent's own
  connection dropped with a 401 and the edit was never applied. Neither is the
  rule, so the run's own status is the only answer — never the agent's
  recollection of what it was doing.
- **Do not cancel a slow Mentor run casually.** One to ten minutes is normal;
  investigate at twenty rather than cancelling. A cancelled run still consumes
  the session.
- **Three consecutive failed iterations means stop the run**, not push harder.

### Between steps 6 and 7 — Seed demo data

Before any UI verification — the render checks inside step 6, step 7's tests,
or the grading step — seed demo data through the app's own create screens.
That also proves those screens work: on a real run the "+ Add" buttons on
two screens turned out to be inert, and it surfaced only when seeding was
finally attempted (restaurant-app-v2, 2026-08-28/29, after two days of
verification against one restaurant, zero dishes and zero subscribers — the
dispatch run reached zero recipients and the product's core feature never
executed).

Seed a **discriminating** dataset, not one record per entity: for every
filter or per-record behaviour, add records whose expected results differ
per filter value (that run used subscribers with near-complement weekday
patterns, and dishes split standing versus daily). One record of each type
cannot show a filter working. Log the seeded record ids into
`docs/seed-log.md` so step 7 and the grading step can cite them, and so the
doctor's next-step line (step 0) stops pointing here once it is done. If a
create screen genuinely does not exist yet, seed through a data script or
test harness instead and say so in the log — do not skip seeding to work
around a missing screen.

### Step 7 — Test it, and get a real pass/fail

**Skill: `outsystems-bdd-tests`.** Required, not optional — a run of the
sprint loop found controls that rendered but did nothing, passed by every gate
before this step because nothing before it exercises app logic. **Prerequisite:**
two Forge components a human installs on the tenant first — see the skill's
Prerequisites; the skill's preflight names them and stops if they are missing.

Everything before this point checks that the app was *built*. This is the only
step that executes the app's own logic and tells you whether it *works*. It sits
between the publish and the grading because it needs a published app and its
answer should inform whether grading is worth doing at all.

Two halves, and you can use either alone:

- **Generate** composes a Mentor prompt that builds an `<AppName>Tests` module —
  a separate module, so tests deploy and are excluded independently of your
  production code. You still approve each Mentor edit, as in Step 6.
- **Execute** calls the BDD Framework API's runner and reports per-scenario
  pass/fail with an exit code you can gate on.

```bash
python3 scripts/odc_bdd_tests.py --hostname <tenant>-<env>.outsystems.app preflight
python3 scripts/odc_bdd_tests.py --hostname <tenant>-<env>.outsystems.app \
  run --module <YourApp>Tests --suite <YourSuiteScreen>
```

Three things worth knowing before you read a result:

- **The publish is the commit.** A Mentor turn writes into the session, so after
  it, Studio, the revision count and the Context Service all correctly show
  nothing. Publish first, then run the skill's `verify` readback gate to confirm
  the publish carried what Mentor claimed.
- **A green `IsSuccess` is not enough.** The API computes it so that an
  all-skipped suite reports success. The skill requires at least one genuinely
  passing scenario before it will exit 0, and you should too.
- **Exit 2 means inconclusive, not failed.** A rejected token, an unreachable
  host or a self-contradictory response are all exit 2. Do not read them as a
  test failure, and do not read them as a pass.

### Grading — the runtime UI audit

**Skill: `outsystems-runtime-ui-audit`.**

This is the portable half of the loop's quality gate, and it is the only grading
step in this distribution. It audits **what a user actually sees** in the running
app, from a live URL — not how the app was built.

What it does: captures the landing screen at desktop and mobile sizes, shallow-
crawls a few in-app surfaces, captures interaction states (focus ring, hover
before and after), and runs a mechanical probe that measures tap-target sizes,
motion and transition signals, and the app's real design tokens. It then scores
16 criteria from Market Leading down to Broken, with concrete evidence per
criterion, and computes a weighted percentage and an overall tier.

It is **read-only** — it never modifies your app.

Before you rely on it, check one thing: **the runtime URL must be reachable
without logging in.** If a capture lands on a login page or an SSO host, the
skill correctly refuses to score it, and any converge loop built on it is dead
before it starts. Confirm the URL is publicly reachable before the run, not
during it.

Use the score to drive a converge loop back into step 5: hand back at most five
fixes, worst-first, each citing its evidence. Small fixes get short,
single-purpose prompts — do not open a big planning session for a tap-target
change. **Stop** when you hit your target tier, or after two consecutive audits
with no improvement in the weighted score. A flat re-audit means a person looks
next, not another batch of fixes.

## The human gates

Six points where the loop stops and waits for you. This is why nobody should
expect an unattended run — none of these has a defined behaviour when the human
is absent.

| # | Step | What you are asked |
|---|---|---|
| 1 | 3 — `outsystems-ui-design` | Confirm the screen archetype before the skill goes deeper. This confirmation gates everything after it. |
| 2 | 3 — `outsystems-ui-design` | Approve the refinement round. The loop exits **only** on your explicit approval of the current tree. |
| 3 | 4 — `outsystems-plan-to-mentor` | Resolve coverage ambiguity that would change the requirements. It stops and asks rather than guessing. |
| 4 | 4 — `outsystems-plan-to-mentor` | Choose the delivery mode. Asked exactly once. |
| 5 | 5/6 — `outsystems-mentor-implementation` + MCP | Approve **each** Mentor edit, on the exact step about to run. |
| 6 | 6 — MCP | Approve the publish to Development. Separate from the edit approvals. |

Plus one manual reconciliation that is not a prompt you can wait for: the entity
names and block choices compared between the plan and the blueprints at step 4.
Nothing asks you to do it, and nothing catches it if you skip it.

Gate 2 is worth calling out. **A blueprint produced without your explicit
approval is *proposed*, not approved**, and it has to say so in three places —
the pattern tree, the blueprint's own review notes, and its acceptance checklist
— so nothing downstream mistakes it for a design you signed off. Step 3 cannot be
batched into unattended preparation. That is an accepted constraint of the loop,
not a defect to route around: schedule the design work for when you are there.

## Ordering rules

These are the ones that bite when skipped.

1. **Plan before screen design, by default.** The blueprint names data
   producers; running design after the plan means the wireframe's regions bind
   to entity names that already exist. Invert only when the UI genuinely drives
   the requirements — then feed the blueprints' entity names into the plan.
2. **Entities before screens in the build.** Mentor builds the typed data model,
   seeded records included, and only then the screens that bind to it. Every
   clean end-to-end run has followed this order. That build-time seed is not
   enough on its own to verify the app against — add the discriminating
   dataset from "Between steps 6 and 7 — Seed demo data" once it publishes.
3. **One design run per screen.** N screens is N runs sharing one screen
   inventory and one navigation decision made up front.
4. **Theme is its own step.** Ask for it explicitly during step 5.

## When a session ends mid-loop

A long run outlives its conversation. On the first real end-to-end run the
driving session archived itself part way through and the work carried on under
a new one; closing the browser later changed nothing either.

An archived session reads exactly like a stall — your last prompt sitting
there unanswered, no error, no completion. **That is not a failed build.**
Nothing was lost, because nothing load-bearing lives in the conversation.

1. **Do not re-send the prompt into the dead session**, and do not assume the
   Mentor session it started is still running. Look at the app, not the chat.
2. **Start a new conversation and point it at the artifacts on disk.** The
   Mentor package step 5 wrote — the file named on the `Output file:` line of
   the step-4 handoff, the one carrying the Manual Setup Gate, the Session
   Readiness Matrix, the pseudocode and the numbered Mentor sessions — is the
   resume artifact. That package, the patched plan and the blueprints are the
   handoff. The conversation never was.
3. **Enumerate what is actually deployed before resuming**, and tick off the
   build-log rows that already landed. A session that was in flight when the
   conversation died may have finished, half-finished, or done nothing, and the
   package's expected element delta cannot tell you which — only the deployed
   model can.

Keep those artifacts somewhere a fresh conversation can reach. The package path
is the only thing you have to carry across.

## What this distribution does not include, and why

The loop as we run it internally has two more numbered steps and a
retrospective. They are **not** part of this distribution:

- **The source-file review half of step 7** — a second, complementary grade of
  *how the app was built* rather than what it looks like at runtime. It needs a
  converter for the published app source that is not publicly distributed.
- **Step 8, the as-built snapshot** — downloading each published revision's
  source and committing it so the next sprint can diff intent against reality.
  It depends on a command-line tool for tenant asset download and source diffing
  that is likewise not publicly distributed.
- **The retrospective** — a same-day pass over the run log and the source diff
  between the first and last snapshot. It reads the artifacts step 8 produces,
  so it cannot run without step 8.

Steps 1–6 plus the runtime grade are complete and useful on their own: you can
go from an idea to a published, evidence-scored revision, and converge on a
target quality tier. What you give up is the automatic memory between sprints —
you will carry that context forward yourself, in your own repository, rather than
having the loop reconstruct it from committed source.

## Before your first run — fifteen minutes of smoke tests

Once both installs are done (this pack and the Public Knowledge server), run
the eight pasted-prompt checks in
[`post-install-checks.md`](post-install-checks.md) in a **new conversation**.
Each has a stated expected result, so every one is a clean pass/fail; the
first three cover the dependency wiring, the honesty contract, and the one
operational trap. A failure there, on a fresh install, is the most valuable
feedback you can send.

## Feedback

Found a rough edge, a step that did not behave as described, or a gap in these
instructions? There is a friction-log template and a bundler script under
`docs/colleague-feedback/` — fill in the template as you work, then run the
bundler to produce a single archive you can send back. It works offline, sends
nothing anywhere itself, and redacts your home directory, tenant hostnames and
anything GUID-shaped before writing the archive; `--dry-run` shows you exactly
what it would include.

Friction reports from real runs are what change the skills. The workaround you
are slightly embarrassed by is the most useful line in the report.
