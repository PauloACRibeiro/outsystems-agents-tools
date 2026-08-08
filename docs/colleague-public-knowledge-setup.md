# OutSystems Public Knowledge — Colleague Setup

The component ZIP published on the distribution repo's latest release is the canonical
way to install OMI's public knowledge provider. It contains a checksum-verified engine
wheel and a standard-library installer; the installer provisions only the four
approved public repositories (`docs-odc`, `docs-howtos`, `docs-product`, and
`outsystems-ui`), builds the local index, and prints registration commands. It
does not read or change Claude Code or Codex configuration.

The public provider is intentionally narrower than the maintainer's personal provider.
OMI uses its `outsystems-public-knowledge` alias for public search and document
fetching only. Internal, private, course, archive, and workshop material is not
in this component.

## Prerequisites

- macOS, Linux, or Windows.
- Git and Python 3.11 or newer.
- Claude Code and/or Codex installed.
- The component ZIP and its sibling `.sha256` digest file from the same
  approved internal handoff channel.
- VPN access for the separate `outsystems-tech-content` server when using OMI
  for implementation-detail work.

No private engine-repository access or GitHub sign-in is needed. The installer
downloads only the four public OutSystems repositories.

## Contract-driven ZIP setup

### 1. Download and verify the component archive

Fetch both files from the same release — the archive and its digest:

- `https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/outsystems-public-knowledge.zip`
- `https://github.com/PauloACRibeiro/outsystems-agents-tools/releases/latest/download/outsystems-public-knowledge.zip.sha256`

Verify the SHA-256 digest before extracting; if it does not match, STOP and report — do
not extract or install:

Both platforms use the same Python check — no shell-native hash tools, so the
command is the same on each. It needs **Python 3.11 or newer**, which is the
same floor `install.py` enforces a few steps later, so nothing that can run the
installer will fail this check.

The Windows form needs the explicit exit-code check. PowerShell does not stop on
a failing native command, so without it `digest OK` would print over a mismatch
and an agent reading the output would extract a corrupted archive.

```bash
python3 -c 'import hashlib,pathlib,sys; want=pathlib.Path("outsystems-public-knowledge.zip.sha256").read_text().split()[0]; got=hashlib.file_digest(open("outsystems-public-knowledge.zip","rb"),"sha256").hexdigest(); sys.exit(0) if want==got else sys.exit("SHA-256 digest mismatch - stop and report")' && echo "digest OK"
```

```powershell
python -c "import hashlib,pathlib,sys; want=pathlib.Path('outsystems-public-knowledge.zip.sha256').read_text().split()[0]; got=hashlib.file_digest(open('outsystems-public-knowledge.zip','rb'),'sha256').hexdigest(); sys.exit(0) if want==got else sys.exit('SHA-256 digest mismatch - stop and report')"
if ($LASTEXITCODE -ne 0) { throw "SHA-256 digest mismatch - stop and report" }
"digest OK"
```

**Version floor:** the release you install from must carry engine wheel
`workspace_knowledge_cc` **1.4.0 or newer** (first shipped in v35) — check
`wheels/` inside the ZIP. Older components lack the `platform` search argument
and **silently ignore it** rather than refusing, which quietly degrades OMI's
ODC-focused retrieval. If you installed before v35, re-run this setup from the
current release. Quick probe on an installed component: call
`search_outsystems_public` with `platform='bogus'` — a current engine refuses
the value; a pre-v35 engine answers as if you had not passed it.

### 2. Extract and install

After the contract check proves the flat layout, extract the exact archive into
a locally named `outsystems-public-knowledge` directory. Confirm that the root
`install.py` is present and run its bounded, non-mutating help command before
installation:

These commands invoke the same root launcher as `python install.py` after
entering the extracted directory, while keeping the directory location explicit.

macOS/Linux:

```bash
python3 -m zipfile -e outsystems-public-knowledge.zip outsystems-public-knowledge
test -f outsystems-public-knowledge/install.py
python3 outsystems-public-knowledge/install.py --help
python3 outsystems-public-knowledge/install.py
```

Windows PowerShell:

```powershell
python -m zipfile -e outsystems-public-knowledge.zip outsystems-public-knowledge
if (-not (Test-Path .\outsystems-public-knowledge\install.py -PathType Leaf)) { throw "missing root install.py" }
python .\outsystems-public-knowledge\install.py --help
python .\outsystems-public-knowledge\install.py
```

The default managed root is `~/outsystems-public-knowledge` (the equivalent
directory under `%USERPROFILE%` on Windows). Pass `--root <path>` only when you
need a different location. A successful install verifies the archive and wheel,
creates the component-owned virtual environment, clones the approved public
repositories, builds and smoke-tests the index, writes the success receipt last,
and prints Claude Code and Codex registration commands.

### 3. Apply the printed registration command

Installation never mutates client configuration. Copy the command printed for
the client you use and run it yourself. To print the same registration output
again without changing the component, run:

macOS/Linux:

```bash
~/outsystems-public-knowledge/.venv/bin/outsystems-public-knowledge registration
```

Windows PowerShell:

```powershell
& "$HOME\outsystems-public-knowledge\.venv\Scripts\outsystems-public-knowledge.exe" registration
```

The MCP alias must be exactly `outsystems-public-knowledge`. Claude Code and
Codex may both use the same component root and index.

### 4. Verify from a new agent session

Close the current agent session and start a new agent session so the newly
registered MCP is discovered. Call `ping()` on `outsystems-public-knowledge`,
then run a public query with `search_outsystems_public`; fetch one returned
`doc_id` with `fetch_doc`. Results should cite paths from one of the four approved
public repositories. Internal and private search scopes are empty by design.

## Health checks and updates

`doctor` is read-only. It checks prerequisites, repository identity and
cleanliness, manifest and receipt integrity, index health, and a smoke query:

```bash
~/outsystems-public-knowledge/.venv/bin/outsystems-public-knowledge doctor
```

Windows PowerShell uses the same executable under
`$HOME\outsystems-public-knowledge\.venv\Scripts\`.

To fast-forward the approved repositories and atomically rebuild the index:

```bash
~/outsystems-public-knowledge/.venv/bin/outsystems-public-knowledge update
```

The update command has a deliberate dirty-repository boundary: local edits or
an unexpected origin/branch stop the update before pull or rebuild. The component
never discards colleague changes. Resolve or preserve those changes yourself,
then rerun `doctor` and `update`. A failed update keeps the previous complete
index and receipt usable; it does not report partial success.

## OMI skill-pack setup (standalone OMI colleague pack only)

**Sprint-loop pack users: skip this whole section.** Your four skills install
via the release's own `INSTALL-SPRINT-LOOP-<OS>.md` documents; this section
covers only the standalone `omi-colleague-pack-*` channel, whose archive ships
with a root `install.py` consumed by the repository's `install_skill_pack.py` installer.

For that standalone channel: download the pack `.tgz` and its `.sha256` from
the release that published them, verify the digest exactly as in step 1 above
(same command, the pack's filenames), then run the pack's bundled installer
per the pack repository's packaging README → "Install (Phase 2)" (`--claude-root` /
`--codex-root` accepted; `--check` verifies an existing install). The installer
writes plain managed copies (never symlinks) and does not read or change Claude
Code or Codex configuration. There is no separate pair-verification step: each
asset carries its own digest file.

## OMI provider states

Provider availability selects one of three explicit OMI modes:

| Mode | Public provider | Authority |
|---|---|---|
| Full local | `workspace-knowledge-cc` | Full local Workspace knowledge provider. |
| Colleague | `outsystems-public-knowledge` | Public OutSystems grounding only. |
| Neither available | None | Explicitly degraded source-backed fallback; report the missing provider. |

The colleague provider supplies public grounding, not restricted implementation authority.
`outsystems-tech-content` remains a separate VPN-gated prerequisite whenever OMI
needs restricted implementation details.

## OMI and the VPN-gated implementation source

The component supplies OMI's public grounding, not restricted implementation
authority. `outsystems-tech-content` remains a separate VPN-gated prerequisite
for function signatures, TrueChange details, widget rules, courses, archives,
and workshops. Connect the VPN and register that MCP separately using the
approved internal instructions for your client. If it is unavailable, OMI must
report the missing implementation authority rather than infer those details
from the public component.

## Transition-only bootstrap (maintainer-side only)

`scripts/bootstrap_public_knowledge.py` exists in the maintainer's private
repo and does **not** ship in any release asset — if you are reading this
from an installed pack, this path is not available to you; use the release
channel above instead. Kept here for the maintainer's own migrations:


The repository script below exists for one transition release only. It is not
the canonical installer or lifecycle authority, it does not accept URLs, and it
has no private default. Use it only when the versioned ZIP cannot yet be used and
you have an explicit local engine input:

```bash
python3 scripts/bootstrap_public_knowledge.py \
  --engine-source /path/to/workspace_knowledge_cc-<version>-py3-none-any.whl
```

On Windows PowerShell, use `python` instead of `python3` and put the command on
one line — `\` does not continue a line there.

`--engine-source` may instead name an unpacked component directory containing
exactly one matching wheel under `wheels/`, or a local
`workspace-knowledge-cc` checkout. Remote URLs, `git+` specifications, missing
paths, and ambiguous component directories are rejected before the bootstrap
creates or changes its managed root. New installs and updates should use the
verified ZIP path above.
