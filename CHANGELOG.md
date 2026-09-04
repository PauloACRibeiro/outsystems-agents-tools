# Changelog

All notable releases to the published component and skills are recorded here.
Because `outsystems-public-knowledge/` keeps only the latest artifact, this file
is the record of what previous versions existed.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Pending v43 (PAS `main` after `527399e9`; export not yet cut)

What has landed upstream since the v42 export and will ship with the next
pack. Written before the cut; the export line and OPK decision are added when
it happens.

- **Agent Plugins manifest.** `plugin.json` ships at the pack root per the
  Agent Plugins 1.0.0 specification, so the extracted archive installs as one
  plugin in Codex, Cursor, GitHub Copilot, Kiro and VS Code. Claude Code
  ignores it and keeps auto-discovering `skills/`. No `mcp.json` ships: the
  specification allows no placeholder in a remote URL, and the tenant is
  registered per project by step 0.
- **Tenant MCP registered per project by step 0.** `outsystems-sprint-init`
  writes a project `.mcp.json` naming the server `outsystems-<slug>` from the
  project's `outsystems.toml`, and its doctor rejects a generic `outsystems`
  entry in that file (it cannot see a user-scope registration; remove one by
  hand). One user-scope credential shared by concurrent sessions forced
  a re-login every 30–90 minutes, because ODC rotates refresh tokens and
  revokes the family on reuse. The manual, the entry doc and both install
  documents no longer instruct `claude mcp add -s user`; login is
  `claude mcp login outsystems-<slug>`.
- **Retired Mentor tool names closed out.** The v42 migration to the
  session-based Mentor surface covered the files it enumerated; this pass
  rewrote the remaining shipped references that still named only
  `mentor_start`/`publish_start` in prohibitions and approval gates, where a
  stale name silently weakens the rule instead of failing.
- **ODC platform rules adopted in the build and plan references.** The
  generated entity-action family is six names and a colliding Server Action is
  renamed, not refused; an aggregate `Count` is a Long Integer; SQL
  `Max. Records` applies in the app, not the statement, and `.Count` on a SQL
  node re-executes it; a credential-bearing Setting is `Is Secret = Yes`; the
  `Length()` prohibition is about the Text function, not a list's `.Length`;
  a library producer must be released with a version, not merely published,
  before its consumer can resolve it.
- **Blueprint and inventory contract.** An `exists: true` entity can gain
  attributes through an attribute-level `create: true` channel instead of
  being recreated; sample content carries no real personal data; data-flow
  prose carries no expression or API syntax; screen-inventory approval uses
  the Confirm/Correct/Missing vocabulary.

### Export 2026-09-02.6 (PAS `527399e9`) — released as v42

Nine packs re-exported for the v42 cut. Ship set frozen at `320a648f`; the
exported tip differs only in maintainer evidence files.

- **`outsystems-sprint-init` ships** as manual step 0 (the doctor, colleague
  profile); the pack is seven skills.
- **Mentor contract on the session-based OutSystems MCP surface** — the old
  `mentor_start`/`publish_start` names were removed server-side on 2026-09-02.
- Test phase required before grading; control-behaviour contract in screen
  prompts; navigation destinations named in the inventory; seed-demo-data step
  with a doctor-read log; containment rows paired by requirement ID.
- Install documents: seven skills; executed on a clean Windows 11 VM (9/9).
- OPK component unchanged (`8644fd60`); the refresh-trap check-3 failure is
  carried forward and disclosed in the release notes.

### Export 2026-08-31.1 (PAS `63311456`)

Build skill only — three reference files. Retrospective #6 from the
restaurant-app-v2 typeahead work, where one mistaken assumption about
`.Current` produced two separate defects in a day and validation reported
`error_count: 0` for both.

- **Failure-shapes catalog grows to twelve.** #11 is live logic behind a
  condition the UI cannot satisfy — a complete, correct branch guarded on a
  shared aggregate no user action could point at. The probe is to name the UI
  element that makes each guarded branch's condition true; where there is none,
  delete the aggregate feeding it rather than leave it fetching for nobody.
  #12 is a handler reading `.Current` when the thing bound is a Container's
  Click rather than the List Item's own On Click.
- **Pass the clicked row as arguments.** The prompt-side rule for #12, in the
  Mentor hardening reference: give the handler one input per value the row
  supplies. This follows ODC's own documented shape for a row click, where the
  List Item's On Click passes the current item's identifier as an input
  argument. Scoped to the binding actually measured — `.Current` on the row's
  own event is legitimate, and the entry says so.
- **Stale screens, warning counts, dead theme classes.** A verification verdict
  now requires a post-reload read, because feedback messages and list counts
  survive across probes and were twice misread. The validation WARNING count is
  recorded per turn and diffed — a turn meant to remove an aggregate took it
  from 61 to 71 with errors at zero. And the measured list of theme classes
  that resolve to nothing grows: `badge-primary`, `align-items-end`,
  `cursor-pointer`.

### Export 2026-08-31 (PAS `0f3b4843`)

Publishes four exports at once: the three cut on 2026-08-30 were committed
locally and never pushed, so this is the first push carrying any of them.

- **Build skill** — four new execution gates plus a failure-shapes catalog, and
  the Mentor-prompting lore from the restaurant-app-v2 run.
- **Design skill** — every token prescription now has to come from the measured
  token table.
- **Screen inventory + plan review** — the CRUD-closure rule (a record action
  must say where it happens) and the contract-reachability check (an action
  input no UI can supply).

Also removes `skills/outsystems-mentor-implementation 2/`, a macOS conflict-copy
of the build skill swept into the 2026-08-30 export commit by `git add skills/`.
It was never pushed, so no published tree ever carried it.

## v37 — 2026-08-09

The first release shaped by its own audience: every change below traces to a
finding from the maintainer running the full colleague flow by hand on a clean
Windows machine (15 findings, all fixed, all independently reviewed).

### Sprint loop pack (`outsystems-sprint-loop-pack-2026-08-09.1`)

- The install now ends with ONE next action: a link to the sprint loop entry
  doc on GitHub. Local doc paths are secondary reference, not the handoff.
- "Restart the client" was wrong on Claude Desktop and is gone: skills load in
  a NEW conversation; resuming an old one keeps the old skill registry.
- The design skill's missing widget inventory is now an offered completion
  step for OutSystems staff (regenerate locally in about a minute), not a
  footnote — and its routing note no longer names a skill the pack does not
  carry as if it were installed.
- The feedback bundle now records WHICH pack version it came from
  (PACKAGE-MANIFEST.json travels with it), no longer ships every skill twice,
  its --dry-run claim matches what --dry-run actually shows, and all three
  privacy redaction rules are now proven by tests rather than asserted.

### OutSystems Public Knowledge server (component unchanged, documents new)

- The component archive is byte-identical to v36 (engine 1.4.0); both INSTALL
  documents are newly rendered.
- Refresh is now ON DEMAND: update when the index reports stale content. The
  weekly scheduled job is deliberately no longer offered — measured on a real
  machine, an unattended weekly fire finds the index bound and silently
  refuses almost every time (and the one real registered task observed was
  itself broken since creation by argument corruption, invisibly, because a
  background task logs nothing). Documents from earlier releases may have
  registered a job; both REFRESH and UNINSTALL now carry its removal by name.
- The pre-update safety check now recognizes BOTH server binaries and scopes
  matches to the install root by path (with the sibling-folder trap fixed —
  a naive prefix match would have blocked every future refresh).
- The install documents state the expected snapshot age on a fresh install
  (~3 weeks; the documented one-time refresh brings it current).


### v36 — the OutSystems sprint loop pack (release candidate, not yet cut)

> **Draft.** Written against the candidate build; the version number and the
> "verified" claims below must be re-checked at the cut. The Windows install
> walkthrough and the no-VPN rehearsal have **not** been run yet.

Three skills join `outsystems-plan-to-mentor`, so the published set now covers
steps 1–6 of the sprint loop plus the runtime grade: `outsystems-ui-design`
(wireframe to validated blueprint), `outsystems-mentor-implementation` (build),
and `outsystems-runtime-ui-audit` (score the published app from its live URL).
`outsystems-plan-to-mentor` is re-exported from current source.

- **A single entry document**, `docs/sprint-loop-for-colleagues.md`, is the
  thing to read first. It gives the loop in order, names which skill owns each
  step, and points at the Superpowers and OutSystems MCP plugins' own official
  installs for the steps we do not redistribute. It lists the **six human
  gates** as a table, because the honest headline is that this loop does not run
  unattended and planning for one wastes a day.
- **What is not included is stated plainly**, and by function rather than by
  internal name: the source-review half of step 7, step 8, and the
  retrospective all depend on tooling that is not publicly distributed.
- **A feedback kit**, `docs/colleague-feedback/`: a friction-log template and a
  standard-library bundler that collects the filled template, installed-skill
  frontmatter and any run receipts into one archive. It makes no network calls,
  and it redacts the home directory, OutSystems hostnames and anything
  GUID-shaped before writing — verified end to end against a fixture carrying
  all three, including that a skill's body never leaves the machine.
- **The pack installs from per-OS instructions**, not from a script.
  `INSTALL-SPRINT-LOOP-MACOS.md` and `INSTALL-SPRINT-LOOP-WINDOWS.md` ship as
  release assets alongside `outsystems-sprint-loop-pack.tgz` and its `.sha256`.
  Both agents are covered — Claude Code reads `~/.claude/skills/`, Codex reads
  `~/.agents/skills/`, and neither needs a config file edited.

### Rewritten for a reader outside the maintainer's workspace

Most of this content existed before, but only ever went to an invite-only
repository. Going world-visible surfaced four things that were fine in a
personal workspace and wrong in a pack a stranger installs. **All four were
found by grepping the exported tree, not by the gates** — and two of them the
gates could not have caught, for reasons given under "Repository changes".

- **The bundles address you, not a named individual.** 81 lines across 24 files
  told the reading agent to ask the maintainer by name before proceeding, or to
  tell him when a manual dependency update was required — an instruction to
  consult a stranger the page never introduces. Those are now "the user",
  matching the voice the
  same bundles already used 98 times. Where the distinction is genuinely
  between the maintainer and you it is kept and said plainly: the
  knowledge-provider contract still explains that the maintainer binds an
  internal index while a colleague binds the public one.
- **A tenant name is gone.** One provenance line named the specific tenant an
  inspection was run against. It now says "an ODC tenant"; the line never
  needed the name to do its job.
- **Three citations pointed into a directory that does not ship.** The audit
  rubric and two prompt templates cited a source-repo-only path as the evidence
  behind the C15/C16 redesign and the converge contract, so following them from
  this tree found nothing. The findings stay and are now stated in place: what
  the first live converge run showed about scoring C15 and C16 from a single
  observation, and the 13 fix instructions across 3 iterations that produced no
  scope drift.
- **`outsystems-ui-design` named a knowledge provider you cannot get.** It
  referred to the maintainer's internal index four times and never once named
  the public alternative, so there was no way to know what to use instead. It
  now names the role and both bindings, matching what
  `outsystems-mentor-implementation` already did everywhere else. Nothing here
  is required — both providers are optional enrichment, and the skill runs on
  its bundled catalog without either.

**One file is deliberately withheld.** `outsystems-ui-design` normally carries a
generated inventory of the built-in platform widgets' runtime properties. It is
derived from an OutSystems-internal repository that publishes no licence, so it
must not enter a world-visible repo. The generator script ships instead, with a
new `references/built-in-widgets-regeneration.md` covering both how to produce
the file with OutSystems GitHub access and how the skill behaves without it:
fall back to the block index and say a property list is unverified rather than
inventing one that looks right and fails at build time.

### Verified by execution

The macOS install document was walked end to end against this build: digest
check, extraction, copy into a skills root, and the verification block. All four
skills report their own `name:` line afterwards. The design skill's validator
was then run inside that install, with the widget inventory absent, against both
worked-example blueprints it now ships — both validate.

### Not yet verified

- **The Windows document has not been executed.** It is written PowerShell-native
  rather than translated from the macOS commands, but every previous release
  found defects on Windows that were invisible on macOS by construction. Treat it
  as unproven until it is walked in a VM.
- **The no-VPN rehearsal has not been run.** The build skill's retrieval is
  pluggable, and the claim that a colleague needs no VPN is a design claim here,
  not a measurement.

### Repository changes

`skills/EXPORT-MANIFEST.json` now records **every** exported pack rather than
only the most recent one. Before this, exporting a second skill overwrote the
manifest, and the CI integrity check kept passing while covering nothing but the
last export. `docs/` is generated output too, and is covered by the same check.

Two of the four scrubs above got through gates that were built to stop exactly
that, and both for the same reason: **the check only ever finds what its
pattern describes.** The tenant rule required a full hostname, so a tenant
named in prose scanned clean. The reference checker only treats a quoted token
as a path when it starts with one of five known directories, so a citation into
a sixth was invisible to it by construction. Both gaps are closed — a rule for
the bare tenant name, one for the maintainer's own name, and the internal-only
source directories added to the non-shipped reference triggers — and there is
now a test that watches each new guard actually fail on a planted violation,
rather than trusting that a clean run means a working check.

A third review round proved the same lesson again at a smaller grain: an
internal network endpoint and forty-one references to a maintainer-only
repository sat in the exported tree, invisible to every pattern above. Both
are gone from the source, and the gate now also hard-fails private IP
addresses, any address-with-port, Windows user paths, *any* tenant hostname
(not just the known one), and the maintainer repository's name — each with a
regression test carrying the exact string that got through.

**The maintainer's catalog-refresh tooling no longer ships, and the catalogs it
produces no longer point at a machine you cannot reach.** Six scripts
regenerated the bundled reference catalogs from a documentation mirror that
exists only on the maintainer's machine; they could not run here and nothing in
the pack referenced them, so they are gone. The two catalogs themselves recorded
their provenance as paths into that same mirror — 57 references that resolved
for nobody reading them. Both are regenerated: provenance is now relative to the
harvest root (`Interface/Block Widget/Block Widget.md`), and the mirror is named
by role rather than by its path on one machine. The regeneration was verified
field by field to change provenance and nothing else.

## 2026-08-05 — outsystems-plan-to-mentor: mechanical coverage gate

Skill export from PAS `f8482d5`. The self-reported coverage score (0–100,
converge at ≥98) is replaced by a mechanical gate: stable `BR-`/`UC-`/`C-`
requirement IDs (new `references/requirement-id-conventions.md`), a stdlib
checker `scripts/check_requirement_coverage.py` (uncovered = defined −
referenced, dangling = referenced − defined, verdict `READY`/`NOT READY`),
and a computed — never hand-authored — readiness verdict. Deferrals must cite
their ID in the plan's scope boundaries; there is no waiver mechanism.

## 2026-07-31 (v32)

**Every change below was found by watching real coding agents use v31 on real
machines — Claude Code and Codex, on Windows and macOS. None came from a code
review.** Component `1.3.0`, ZIP digest
`640d7b0d76e1f7549288a179283551b77a89668148fd4c213d06d56425d46d8f`, built twice
byte-identical. Supersedes v31 `cc2200c7…`.

### Product fixes

- **`update` no longer breaks a running server silently.** It replaces the index
  atomically, so a server already bound to the old file rejected the new one
  permanently — still answering health checks while every query failed. It now
  warns before and after, naming the processes, and says that a client restart
  may not stop them. It also prints a success line: the previous silence is what
  made this take a day to diagnose.
- **A partial uninstall is now recoverable.** If removal fails part way — a file
  held by an indexer, antivirus, or a shell sitting inside the root — the tree was
  left half-deleted, and re-running refused because the receipt had already been
  removed. A resume marker lets the same command finish the job, with a bounded
  retry for momentary locks and, on Windows, the name of what holds the file.
- **The printed MCP removal command carries the scope it registered with.** The
  unscoped form crashed with an access violation and left the registration behind.
- **`doctor` reports how old the mirrored content is** and flags it past a week.
  It measures when content was last actually fetched, so a reindex cannot make a
  stale corpus look fresh.
- **`refresh_index` and `ping` no longer describe themselves as things they are
  not.** `refresh_index` reindexes local files and fetches nothing; `ping` reports
  liveness and identity and cannot detect a broken index binding.

### Instruction fixes

- Installer path, interpreter, digest verification and extraction commands are now
  correct and concrete on both platforms. Several were valid in bash and inert in
  PowerShell — something no macOS test could have caught.
- The Windows document declares PowerShell as its shell. The two shells need
  opposite forms for the same command; no single form works in both.
- Uninstall deregisters and stops the server **first**. The previous order failed
  for everyone, because the agent's own server holds the root it is about to delete.
- A copy of the operations document is written into the install root at install
  time. Without it, an agent asked months later to "follow the instructions" has
  nothing to follow — one invented a procedure that removed the package and left
  1.4 GB of mirrors and index behind.
- The agent verifies prerequisites itself and asks the human only about the install
  root — the one thing that is a decision rather than a measurement.

### Verified, and not

Verified by execution on both platforms against this build: digest, install,
`doctor` (15 on macOS, 19 on Windows), `update` including the live-server guard,
the staleness warning clearing after an update, and uninstall.

**Fixed but not proven on a real machine:** partial-uninstall recovery (unit tests
only), Windows holder identification (written from the API contract, never
executed on Windows), and the update runner script — which is
**specified, not standardized**: the instructions say what it must do rather than
giving literal source, so each agent writes its own and none have been compared.

The automated Windows walkthrough runs the eight documented commands. It does not
exercise keeping the extraction directory, writing the local `INSTALL.md`, or
writing the runner script — those are instructions to an agent, and the harness is
not one.

### Known issues, carried forward unchanged

- **Windows install intermittency**: two failures in three attempts on one pilot
  machine, unexplained, undiagnosable because logs were deleted before the retry.
  Both documents require preserving logs before retrying.
- **A fresh install reports STALE immediately** when the release is more than a
  week old. That is accurate, not a fault — the shipped corpus is pinned at build
  time — and `update` clears it.

## 2026-07-31

- **Distribution authorization.** World-public distribution of this component was
  authorized by Paulo on 2026-07-30. Before that date, distribution beyond a
  hand-picked pilot was explicitly un-granted. Recorded here because this file is
  the governing release record; the cross-agent review (AH-2026-07-31-001) did not
  itself establish that authorization.
- **First component release: `v31` (OutSystems Public Knowledge 1.3.0).**
  Published as a GitHub Release with four assets — the component ZIP, its
  `.sha256`, `INSTALL-MACOS.md` and `INSTALL-WINDOWS.md`. ZIP digest
  `cc2200c7b6a83d3e9e53b757f208ffeed9bef8c72093d3a00d39079255546957`.
- **The component ships as a Release asset, not in the repository tree.**
  This supersedes the 2026-07-18 decision to commit the ZIP under
  `outsystems-public-knowledge/`, which now holds only a pointer to the
  Releases page. The tree therefore never accumulates a binary per version,
  and the agent gets a version and digest as data rather than as a file.
- **Install is now agent-native.** `README.md` carries one short, version-free
  prompt a colleague pastes into Claude Code or Codex; the agent resolves
  `/releases/latest`, reads the instructions for its own OS, confirms the
  install root and prerequisites with the human, then installs and verifies.
  Prompts for refresh and uninstall are alongside it. This replaces a
  605-line setup document that had to be sent by hand.
- **Both platforms verified by execution before publication.** The macOS
  document was walked end to end on a real install; the Windows document was
  walked end to end inside a disposable VM, including the uninstall ordering
  guard firing with a live server holding the install root. Nine document
  defects were found and fixed in the process — five of them invisible on
  macOS by construction, including a command form that is valid in bash and
  inert in PowerShell.

## 2026-07-29

- Regenerated `skills/outsystems-plan-to-mentor/` from `portable-agent-skills`
  at `2cac278` — the paste-mode execution protocol gains a verbatim-literal
  entry rule (clipboard entry where grantable, then read the stored value
  back and compare it to the source text; a committed field is not proof of
  verbatim storage). Part of the driving-Mentor lessons batch from the
  PlayRight runtime phase, cross-agent reviewed (AH-2026-07-29-001).

## 2026-07-28 (second export)

- Regenerated `skills/outsystems-plan-to-mentor/` from `portable-agent-skills`
  at `1ea6cb2` — the companion invocation contract now also requires reconcile
  session phrasing, a per-session expected element delta and `Traps` list, and
  a build-log table template in the Mentor package (session-packaging
  hardening, cross-agent reviewed).

## 2026-07-28

- Regenerated `skills/outsystems-plan-to-mentor/` from `portable-agent-skills`
  at `1d39c6c` — six workflow improvements from a live build retrospective,
  cross-agent reviewed: pre-plan capability brief handed to the plan generator
  (new `references/capability-plan-brief.md`) with pre-plan/post-plan mode
  routing; platform-feasibility rows in the coverage loop with an
  official-source authority rule; fail-closed `Target app state` +
  scaffold-inventory fields in the companion invocation contract; supervised
  paste execution protocol (new
  `references/paste-mode-execution-protocol.md`); Known Platform Bounds and
  Runtime Verification guardrails; scanner now also rejects ODC
  element-recipe section headings case-insensitively.

## 2026-07-19

- Regenerated `skills/outsystems-plan-to-mentor/` from `portable-agent-skills`
  at `b24cc05` — strips a trailing space in `references/delivery-modes.md` so the
  tree passes `git diff --check`. No behavior change.

## 2026-07-18

> **Superseded on 2026-07-31 — read this section as history, not as current
> layout.** The in-tree component drop described below was replaced by
> Release-asset delivery; `outsystems-public-knowledge/` is now intentionally
> empty. See the 2026-07-31 entry.

- Added `skills/outsystems-plan-to-mentor/` — first public skill export. This
  repo is now the go-forward canonical home for this skill (superseding the
  earlier vendored copy). Derived export from `portable-agent-skills` at source
  commit `cf6c2bb`; provenance recorded in `skills/EXPORT-MANIFEST.json`.
- Repository scaffold created (structure only; no component artifact published yet).
