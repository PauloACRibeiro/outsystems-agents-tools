# outsystems-agents-tools

Public, colleague-facing distribution of OutSystems agent tooling. This repo is a
**curated, consume-only subset** — the working/full estate lives elsewhere and is
not published here.

> **Status: pre-release scaffold.** No release artifacts or skills have been
> published yet. Distribution details (hosting, visibility, remote) are not final.

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
  and `skills/` is a build/export output. The only hand-written files in the repo
  are this `README.md` and `CHANGELOG.md`. Do not hand-edit generated content.
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
