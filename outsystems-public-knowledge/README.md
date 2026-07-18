# outsystems-public-knowledge (component)

> **Placeholder.** This README is replaced at release time by the colleague
> install README generated during the component build (`workspace-knowledge-cc`,
> per the component implementation plan). Do not hand-author the final content
> here — it must match the shipped ZIP.

At first release this folder will contain, for the **latest version only**:

- `outsystems-public-knowledge-<version>.zip` — the installable component
- `outsystems-public-knowledge-<version>.zip.sha256` — published outer digest
- `README.md` — build-generated: intent, requirements, install, verify, update

## What the component is (summary, for orientation only)

A public-only OutSystems knowledge MCP: a narrowed subset of the
`workspace-knowledge-cc` engine that indexes four approved public OutSystems
documentation repositories. Installs and registers independently of any skill.
Non-public search scopes return empty by design.

Requirements, exact install commands, and registration syntax are intentionally
**not** duplicated here — they ship in the build-generated README alongside the
ZIP so they cannot drift from the released artifact.
