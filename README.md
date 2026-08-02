# outsystems-agents-tools

Public, colleague-facing distribution of OutSystems agent tooling. This repo is a
**curated, consume-only subset** — the working/full estate lives elsewhere and is
not published here.

> **Status: published.** The component ships as a Release asset, and every link
> below resolves to the [latest release](https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest)
> rather than to a fixed version — so the prompts stay correct as new versions
> ship, and there is nothing for you to keep in sync by hand. One skill is
> published so far; the rest of the estate is not public.

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
| [Releases](../../releases/latest) | The `outsystems-public-knowledge` MCP component — ZIP, `.sha256`, and the per-OS install instructions, published together per version | Built from `workspace-knowledge-cc` |
| [`skills/`](skills/) | Public versions of selected OutSystems agent skills | Derived from `portable-agent-skills` |

## How to think about this repo

- **Consume-only.** Colleagues download and use what's here. There is no PR-back
  flow for the component or the skills — improvements are made upstream and
  re-published.
- **The component ships as a Release asset, not as a file in this tree.** Cloning
  this repo gives you the prompt and the skills, not the component. Keeping the
  binary out of git means no 186 KB blob accumulates per version, and an agent can
  read the current version and digest as data rather than as a file.
- **Generated, not hand-authored.** Everything under `skills/<name>/` is an export
  output, as are the per-OS install documents published with each Release. Do not hand-edit generated content —
  a CI check (`.github/workflows/verify-export.yml`) fails any push/PR where the
  generated `skills/` tree no longer matches the sha256 provenance in
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
└── skills/                           # public skill exports (one per skill)
    └── <skill-name>/
```

Each Release carries its own component ZIP, checksum and per-OS install instructions. The prompt always resolves `/releases/latest`, so it never needs a version in it.
