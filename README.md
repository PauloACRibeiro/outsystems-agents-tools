# outsystems-agents-tools

Public, colleague-facing distribution of OutSystems agent tooling. This repo is a
**curated, consume-only subset** — the working/full estate lives elsewhere and is
not published here.

> **Status: published.** Two things ship here, and they install separately: the
> **OutSystems Public Knowledge MCP server** (a local documentation server) and
> the **OutSystems sprint loop pack** (seven agent skills). Both are Release
> assets, and every link below resolves to the
> [latest release](https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest)
> rather than to a fixed version — so the prompts stay correct as new versions
> ship, and there is nothing for you to keep in sync by hand.

## Before you paste anything: how the downloads reach you

Today this repository is public and every prompt below downloads anonymously.
It is planned to move inside the OutSystems GitHub organization, after which
downloads need a signed-in GitHub account: any OutSystems employee, or an
external person who received an invite. Nothing in the prompts changes on that
day, because the install documents already carry a fallback chain: anonymous
download first, then the GitHub CLI, then files you downloaded by hand.

To be ready, do this once per machine (harmless now, required later):

1. Install the GitHub CLI: `brew install gh` on macOS, `winget install GitHub.cli`
   on Windows.
2. Sign in with the account that can see this repository:

   ```bash
   gh auth login --web
   ```

   The agent must never run this for you; it needs your browser.

If you cannot install the CLI, download the three files for your OS from the
[Releases page](https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest)
into one folder (the `INSTALL-*.md` for your OS, the archive, and its
`.sha256`), and tell the agent where that folder is. The documents accept files
that are already present.

## Install the OutSystems sprint loop pack

Seven skills that take an OutSystems screen from an idea to a published, graded
revision. Paste this into Claude Code or Codex:

```text
Install the OutSystems sprint loop pack on this machine.

Detect my OS, then download and follow the matching instructions:
  macOS:   https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-SPRINT-LOOP-MACOS.md
  Windows: https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-SPRINT-LOOP-WINDOWS.md

Follow that document literally. If its download step fails, use the fallback
routes written in that step; do not improvise another way to fetch the files.
Confirm with me which agents to install for before you write anything to disk.
When you are done, verify it and tell me the pack version, the skills roots you
installed into, and where you put the docs.
```

**The pack alone is not the whole loop.** Its build step (step 5) refuses to
run without a knowledge source: install the **OutSystems Public Knowledge MCP
server** too — next section, same release. (OutSystems employees already
running the internal tech-content server over VPN are covered.)

**Installed? Start here: [the sprint loop manual](docs/sprint-loop-manual.md)**
— the quick start from installed to first app, one paste-ready prompt per step
with its gate, plus the tenant-connection step neither installer covers.

Then read [the sprint loop entry doc](docs/sprint-loop-for-colleagues.md) before
your first run. It is short, and it covers the two things that cost people the
most time: the order the steps have to run in, and the six points where the loop
stops and waits for a person.

**This loop does not run unattended.** If you were planning to hand it a backlog
and walk away, read that document first — it explains why.

You can read the install instructions before running anything:
[macOS](https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-SPRINT-LOOP-MACOS.md)
· [Windows](https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-SPRINT-LOOP-WINDOWS.md).

### Updating the pack

New releases ship regularly. To move to the latest version, paste this:

```text
Update the OutSystems sprint loop pack on this machine to the latest release.

Detect my OS, then download and follow the UPDATE operation in the matching
instructions:
  macOS:   https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-SPRINT-LOOP-MACOS.md
  Windows: https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-SPRINT-LOOP-WINDOWS.md

Follow that document literally — an update is a per-skill replacement, never a
merge. If its download step fails, use the fallback routes written in that
step; do not improvise another way to fetch the files. When you are done, tell
me the version I moved from and to, and remind me that the updated skills are
only picked up in a NEW conversation.
```

Updating the pack does not touch the Public Knowledge server — refresh that
separately with its own prompt below.

### Telling us what broke

There is a friction-log template and an offline bundler under
[`docs/colleague-feedback/`](docs/colleague-feedback/). Fill in the template as
you work, run the bundler, and send the single archive it produces. The bundler
makes no network calls and redacts your home directory, tenant hostnames and
anything GUID-shaped before writing; `--dry-run` shows exactly what it would
include. Friction reports from real runs are what change these skills.

## Install the OutSystems Public Knowledge MCP server

Paste this into Claude Code or Codex:

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

That is all a human needs. The agent reads the rest.

### Keeping it up to date, and removing it

Paste whichever you need:

```text
Refresh my OutSystems Public Knowledge MCP server to the latest OutSystems
documentation. Follow the REFRESH section of the instructions for my OS at
https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest
Tell me the document count before and after.
```

```text
Uninstall the OutSystems Public Knowledge MCP server from this machine.
Follow the UNINSTALL section of the instructions for my OS at
https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest
Show me what will be removed before you remove anything.
```

### Read the instructions before running anything

You do not have to take the prompt on trust. The exact instructions the agent
will follow are published with every release, and you can read them first:

- [macOS instructions](https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-MACOS.md)
- [Windows instructions](https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/INSTALL-WINDOWS.md)

**The component ships as a Release asset, not as a file in this repository.**
Cloning this repo gives you the skills and this prompt — not the component.

### What this is, and what it isn't

It serves OutSystems **public** documentation — the same pages published on the
OutSystems docs sites — indexed locally and cited by commit. It holds nothing
internal, private or customer-specific, and exposes exactly six read-only tools.

It is shared as-is, with no support commitment and no service level. If it
breaks, open an issue; it may or may not be picked up.

## What's here

| Area | Contents | Source of truth |
|---|---|---|
| [Releases](../../releases/latest) | Both products' assets — the `outsystems-public-knowledge` component (ZIP + `.sha256`) and the sprint loop pack (`.tgz` + `.sha256`), each with its own per-OS install instructions | Component built from `workspace-knowledge-cc`; pack built from `portable-agent-skills` |
| [`skills/`](skills/) | Browsable source for the seven published skills | Derived from `portable-agent-skills` |
| [`docs/`](docs/) | The sprint loop manual, the entry doc, the feedback kit, and the knowledge-provider setup notes | Derived from `portable-agent-skills` |

Every release carries **both** products' assets, so `/releases/latest/download/…`
resolves for either one regardless of which product a given release was cut for.

## How to think about this repo

- **Consume-only.** Colleagues download and use what's here. There is no PR-back
  flow for the component or the skills — improvements are made upstream and
  re-published.
- **The component ships as a Release asset, not as a file in this tree.** Cloning
  this repo gives you the prompt and the skills, not the component. Keeping the
  binary out of git means no 186 KB blob accumulates per version, and an agent can
  read the current version and digest as data rather than as a file.
- **Generated, not hand-authored.** Everything under `skills/<name>/` and `docs/`
  is an export output, as are the per-OS install documents published with each
  Release. Do not hand-edit generated content —
  a CI check (`.github/workflows/verify-export.yml`) fails any push/PR where the
  generated tree no longer matches the sha256 provenance in
  `skills/EXPORT-MANIFEST.json`. Hand-authored files are limited to this `README.md`,
  `CHANGELOG.md`, and the CI infrastructure (`scripts/`, `tests/`, `.github/`).
- **The component and the skills install separately.** The component provides a
  public OutSystems knowledge MCP; the skills are the clients that use it. Getting
  one does not install the other.

## Layout

```
outsystems-agents-tools/
├── README.md                         # this file (hand-authored)
├── CHANGELOG.md                      # release history (hand-authored)
├── docs/                             # generated — entry doc + feedback kit
└── skills/                           # generated — one directory per skill
    ├── EXPORT-MANIFEST.json          # per-pack provenance + per-file sha256
    ├── outsystems-sprint-init/
    ├── outsystems-screen-inventory/
    ├── outsystems-ui-design/
    ├── outsystems-plan-to-mentor/
    ├── outsystems-mentor-implementation/
    ├── outsystems-bdd-tests/
    ├── outsystems-runtime-ui-audit/
    └── shared/                       # not a skill; a file the build skill references
```

Each Release carries its own component ZIP, checksum and per-OS install instructions. The prompt always resolves `/releases/latest`, so it never needs a version in it.

From v43 the pack archive is also an [Agent Plugins](https://agent-plugins.org/specification)
directory: a `plugin.json` manifest sits at the pack root next to `skills/`, so
clients that implement that format (Codex, Cursor, GitHub Copilot, Kiro,
VS Code) can install the extracted archive as one plugin. Claude Code ignores
the manifest and discovers `skills/` as before. The pack declares no MCP
server: the tenant is registered per project by step 0 of the loop.
