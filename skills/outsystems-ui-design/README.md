# outsystems-ui-design

Portable skill for turning a single wireframe screenshot into an approved,
validated OutSystems UI blueprint through a short interactive design loop. You
bring a wireframe; the agent iterates the design *with you in the loop* —
rendering a local HTML preview and a compact pattern tree each round, mapping
every visual region to a named OutSystems UI web block — and emits a validated
enriched `blueprint.json` only once you approve. It designs; it never builds.

This README is for humans using the skill from this repo. The agent-facing
behavior lives in [SKILL.md](SKILL.md).

## What this skill is for

Use this skill when you want an agent to:

- read a wireframe screenshot and propose a screen-archetype read (dashboard,
  list-table, edit-form, and so on) before going deeper
- map every visual region to a named OutSystems UI block — a real layout, a
  real `Columns*`/`Card` skeleton, real patterns — never a vague approximation
- iterate the design with you across rounds, showing an HTML preview and a
  pattern tree each round and re-inferring only the parts you react to
- emit, on your approval, a validated enriched `blueprint.json` that
  `outsystems-mentor-implementation` can execute

It works on one screen per run and OutSystems UI **web** patterns only. Mobile
designs and multi-screen apps are out of scope for a single loop.

## Where this sits in the design → build estate

This skill is the interactive *design* half of a three-skill estate. It owns
the loop up to an approved blueprint and nothing past it.

| Skill | Role |
| --- | --- |
| `outsystems-ui-design` (this skill) | Design loop: wireframe → iterate with human → validated blueprint. Never calls the OutSystems MCP; no Mentor, no tenant access. |
| `outsystems-mentor-implementation` | Execution: consumes the blueprint via its existing visual-source route; owns all Mentor/tenant discipline and approval gates. |
| `outsystems-design-to-app` (not part of the colleague sprint-loop pack) | Unchanged. Non-interactive one-shot path from design source to app. |

## Which skill to reach for

- **Use this skill (`outsystems-ui-design`)** when you want to iterate on the
  design first, with a human in the loop, before anything touches a tenant. You
  have a wireframe, you are not yet certain of every mapping, and you want to
  see and steer the design round by round until it is right.
- **Use `outsystems-design-to-app`** (not part of the colleague sprint-loop pack) when you already know exactly
  what you want and want a one-shot, non-interactive path straight from a design
  source (Figma URL, image, HTML mockup) to an app — no refinement rounds.
- **Use `outsystems-mentor-implementation`** when you already have an approved
  blueprint and are ready to execute it against Mentor. That skill owns all the
  Mentor and tenant discipline; this skill hands the blueprint to it and stops.

The blueprint this skill emits is the handoff contract between the two: nothing
is auto-invoked, and you decide if and when execution happens.

## How it handles the messy cases

The loop is built to refuse to fake things rather than guess quietly:

- **An unreadable or ambiguous wireframe** gets a plain request for a better
  crop or a higher-resolution export of the unclear area — never a whole-screen
  guess from an image the agent cannot actually read.
- **A live mockup URL or HTML page instead of a screenshot** is a supported
  source: the agent reads the page's real computed styles for the design tokens,
  records what it read in `wireframe.md`, designs the one screen you name, and
  says plainly when a screen has no surface in the mockup rather than inventing
  one. Where the mockup shows more product than your requirements approved, it
  adopts the visual language and raises the scope conflict instead of absorbing
  it.
- **A region that matches no OutSystems UI pattern** is flagged
  `custom_block_needed` in both the pattern tree and the blueprint, with a
  one-line note on what that custom block must do — never approximated with a
  styled `Container` that would hide a real build decision from you and from the
  downstream skill.
- **A validator failure at emission** reopens the refinement loop with the
  validator's output shown to you verbatim. The design is fixed and re-validated
  before anything is handed off; a failing blueprint is never handed off.

## Knowledge prerequisites (optional, best-effort)

This skill has **zero OutSystems MCP dependency**. It runs fully local on Python
3.7+ stdlib, produces files plus chat, and performs no tenant operation of any
kind.

Two knowledge sources can *enrich* a run when they happen to be reachable, but
neither is ever required:

- `outsystems-tech-content` — consulted to verify widget nesting rules and
  pattern API facts for the blocks chosen during inference and refinement
- a public knowledge provider — `workspace-knowledge-cc` or
  `outsystems-public-knowledge`, whichever you have bound — consulted only if
  you ask a product-behavior question mid-loop

When neither is reachable (off-VPN, a colleague's machine, no MCP configured),
the skill degrades gracefully: it discloses the degraded mode in a single line
and keeps going on its bundled reference catalog. This is deliberate — the skill
emits a design *proposal* that `outsystems-mentor-implementation` re-validates
on intake, so a degraded-with-disclosure run is a correct and useful outcome,
not a blocked one.

## What you get

Each run creates one per-screen directory under your current project root — a
visible deliverable, not a hidden cache:

```
design/<screen-slug>/
  wireframe.<ext>          # copy of your input screenshot — or wireframe.md
                           # (source URL, observed anatomy, extracted design
                           # tokens) when the source is a live URL or HTML page
  pattern-tree.md          # current round's tree
  preview.html             # current round's self-contained HTML preview
  blueprint.json           # emitted only on your approval
  validation-report.txt    # validator output for the emitted blueprint
```

The `blueprint.json` is the canonical artifact — the file you hand to
`outsystems-mentor-implementation` when you are ready to build.
