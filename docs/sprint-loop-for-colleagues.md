# The OutSystems sprint loop for colleagues, steps 1–6 (+ grading)

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
- **The four skills in this repository**, installed into your agent's skills
  directory: `outsystems-ui-design`, `outsystems-plan-to-mentor`,
  `outsystems-mentor-implementation`, and `outsystems-runtime-ui-audit`. Follow
  this repository's own install instructions.

You do **not** need a VPN, and you do not need an OutSystems employee account.

## Where the pieces come from

| Steps | Owned by | How you get it |
|---|---|---|
| 1–2 | The public **Superpowers** plugin | Installed separately — see below. Not redistributed here. |
| 3, 4, 5, grading | The four skills in **this repository** | Install per this repository's instructions. |
| 6 | The public **OutSystems MCP** plugin | `outsystems@outsystems` — see below. |

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

### Step 6 — install the OutSystems MCP plugin

Everything that touches your tenant — running a Mentor edit in step 5's direct
mode, and publishing in step 6 — goes through the public OutSystems MCP plugin:
<https://github.com/OutSystems/outsystems-mcp>

For **Claude Code**, the official instructions are:

    claude plugin marketplace add OutSystems/outsystems-mcp
    claude plugin install outsystems@outsystems

Then register the server against your own tenant hostname and authenticate — the
repository README has the exact command and the OAuth walkthrough, plus a
best-effort recipe for Codex and other harnesses. Always install as
`outsystems@outsystems`; the bare plugin name is not enough to update it later.

## The loop

### Step 1 — Idea and requirements

**Skill: `superpowers:brainstorming`** (or a hand-written PRD.)

You bring the idea; you get back requirements plus a **screen inventory** — how
many screens, what each one does, and what navigation or header they share.

Deciding the screen list is still a manual judgement call. No skill does it for
you, and it is the biggest hands-on step on an app with six or more screens.

### Step 2 — Capability plan

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
  one screen inventory and one navigation decision made up front.
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

**Skill: `outsystems-mentor-implementation`.**

Two routes feed it, and they stay separate:

- **Route A — logic and capabilities.** Driven by the patched plan from step 4,
  turned into ODC Studio-native pseudocode and Mentor prompts.
- **Route B — screens.** Consumes each `blueprint.json` directly: typed
  entities, seeded records, region-to-block mapping.

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
- **Do not cancel a slow Mentor run casually.** One to ten minutes is normal;
  investigate at twenty rather than cancelling. A cancelled run still consumes
  the session.
- **Three consecutive failed iterations means stop the run**, not push harder.

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
   clean end-to-end run has followed this order.
3. **One design run per screen.** N screens is N runs sharing one screen
   inventory and one navigation decision made up front.
4. **Theme is its own step.** Ask for it explicitly during step 5.

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
