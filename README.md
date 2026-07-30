# outsystems-agents-tools

Public, colleague-facing distribution of OutSystems agent tooling. This repo is a
**curated, consume-only subset** — the working/full estate lives elsewhere and is
not published here.

> **Status: pre-release scaffold.** No release artifacts or skills have been
> published yet. Distribution details (hosting, visibility, remote) are not final.

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
| [`outsystems-public-knowledge/`](outsystems-public-knowledge/) | The `outsystems-public-knowledge` MCP component, as a downloadable release ZIP + checksum + install README | Built from `workspace-knowledge-cc` |
| [`skills/`](skills/) | Public versions of selected OutSystems agent skills | Derived from `portable-agent-skills` |

## How to think about this repo

- **Consume-only.** Colleagues download and use what's here. There is no PR-back
  flow for the component or the skills — improvements are made upstream and
  re-published.
- **Generated, not hand-authored.** Everything under `outsystems-public-knowledge/`
  and `skills/<name>/` is a build/export output. Do not hand-edit generated content —
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
├── outsystems-public-knowledge/      # component drop — LATEST VERSION ONLY
│   ├── README.md                     # install/verify/update (build-generated)
│   ├── outsystems-public-knowledge-<version>.zip
│   └── outsystems-public-knowledge-<version>.zip.sha256
└── skills/                           # public skill exports (one per skill)
    └── <skill-name>/
```

The component folder holds **only the latest version** — a new release overwrites
the previous ZIP, checksum, and README in place. Version history is tracked in
`CHANGELOG.md`, not by keeping old artifacts.
