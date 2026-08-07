# OutSystems Public Knowledge — Colleague Setup

The component ZIP named by the sibling `RELEASE-CONTRACT.json` is the canonical
way to install OMI's public knowledge provider. It contains a checksum-verified engine
wheel and a standard-library installer; the installer provisions only the four
approved public repositories (`docs-odc`, `docs-howtos`, `docs-product`, and
`outsystems-ui`), builds the local index, and prints registration commands. It
does not read or change Claude Code or Codex configuration.

The public provider is intentionally narrower than Paulo's personal provider.
OMI uses its `outsystems-public-knowledge` alias for public search and document
fetching only. Internal, private, course, archive, and workshop material is not
in this component.

## Prerequisites

- macOS, Linux, or Windows.
- Git and Python 3.11 or newer.
- Claude Code and/or Codex installed.
- The component ZIP and its sibling `RELEASE-CONTRACT.json` from the same
  approved internal handoff channel.
- VPN access for the separate `outsystems-tech-content` server when using OMI
  for implementation-detail work.

No private engine-repository access or GitHub sign-in is needed. The installer
downloads only the four public OutSystems repositories.

## Contract-driven ZIP setup

### 1. Read and verify the candidate contract

Use the exact `component.archive.name`, `component.archive.sha256`, and
`component.archive.layout` values in `RELEASE-CONTRACT.json`. Stop unless
`component.archive.layout == "flat"`; OMI onboarding never assumes a wrapping
top-level directory. The SHA-256 digest must match before extraction. The
following standard-library check is version-neutral.

macOS/Linux:

```bash
ARCHIVE="$(python3 -c 'import json; print(json.load(open("RELEASE-CONTRACT.json"))["component"]["archive"]["name"])')"
python3 -c 'import hashlib,json,pathlib,sys; c=json.load(open("RELEASE-CONTRACT.json"))["component"]["archive"]; p=pathlib.Path(c["name"]); actual=hashlib.file_digest(p.open("rb"), "sha256").hexdigest(); print(actual); raise SystemExit(0 if c["layout"] == "flat" and p.name == c["name"] and actual == c["sha256"] else "release-contract mismatch")'
```

Windows PowerShell:

```powershell
$Archive = python -c "import json; print(json.load(open('RELEASE-CONTRACT.json'))['component']['archive']['name'])"
python -c "import hashlib,json,pathlib; c=json.load(open('RELEASE-CONTRACT.json'))['component']['archive']; p=pathlib.Path(c['name']); actual=hashlib.file_digest(p.open('rb'), 'sha256').hexdigest(); print(actual); raise SystemExit(0 if c['layout'] == 'flat' and p.name == c['name'] and actual == c['sha256'] else 'release-contract mismatch')"
```

Stop if verification reports a mismatch.

### 2. Extract and install

After the contract check proves the flat layout, extract the exact archive into
a locally named `outsystems-public-knowledge` directory. Confirm that the root
`install.py` is present and run its bounded, non-mutating help command before
installation:

These commands invoke the same root launcher as `python install.py` after
entering the extracted directory, while keeping the directory location explicit.

macOS/Linux:

```bash
python3 -m zipfile -e "$ARCHIVE" outsystems-public-knowledge
test -f outsystems-public-knowledge/install.py
python3 outsystems-public-knowledge/install.py --help
python3 outsystems-public-knowledge/install.py
```

Windows PowerShell:

```powershell
python -m zipfile -e $Archive outsystems-public-knowledge
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

## Contract-bound OMI skill-pack setup

The OMI TGZ remains separate from the component ZIP. They are two separate
candidate files bound by the same `RELEASE-CONTRACT.json`; do not combine or
repack them. Read `omi.archive_name` from the contract and keep the sibling OMI
receipt beside it. Each platform sequence below derives all candidate names,
verifies the four-file release pair, extracts only the manifest-bound root
installer, checks its bounded help output, installs to explicit roots, and then
runs the read-only check. Do not extract anything before pair verification.

### macOS/Linux OMI sequence

```bash
CONTRACT="RELEASE-CONTRACT.json"
COMPONENT_ARCHIVE="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["component"]["archive"]["name"])' "$CONTRACT")"
OMI_ARCHIVE="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["omi"]["archive_name"])' "$CONTRACT")"
OMI_RECEIPT="${OMI_ARCHIVE%.tgz}.receipt.json"
python3 verify_release_pair.py \
  --contract "$CONTRACT" \
  --component "$COMPONENT_ARCHIVE" \
  --omi "$OMI_ARCHIVE" \
  --omi-receipt "$OMI_RECEIPT"
mkdir -p omi-installer
python3 -c 'import pathlib,tarfile,sys; a=pathlib.Path(sys.argv[1]); n=a.name[:-4]+"/install.py"; t=tarfile.open(a,"r:gz"); m=t.getmember(n); assert m.isfile() and not m.issym() and not m.islnk(); pathlib.Path(sys.argv[2]).write_bytes(t.extractfile(m).read())' "$OMI_ARCHIVE" omi-installer/install.py
python3 omi-installer/install.py --help
CODEX_SKILLS_ROOT="$HOME/.agents/skills"
CLAUDE_SKILLS_ROOT="$HOME/.claude/skills"
python3 omi-installer/install.py --pack "$OMI_ARCHIVE" \
  --codex-root "$CODEX_SKILLS_ROOT" \
  --claude-root "$CLAUDE_SKILLS_ROOT"
python3 omi-installer/install.py --pack "$OMI_ARCHIVE" \
  --codex-root "$CODEX_SKILLS_ROOT" \
  --claude-root "$CLAUDE_SKILLS_ROOT" \
  --check
```

### Windows PowerShell OMI sequence

```powershell
$Contract = 'RELEASE-CONTRACT.json'
$ComponentArchive = python -c "import json,sys; print(json.load(open(sys.argv[1]))['component']['archive']['name'])" $Contract
$OmiArchive = python -c "import json,sys; print(json.load(open(sys.argv[1]))['omi']['archive_name'])" $Contract
$OmiReceipt = $OmiArchive -replace '\.tgz$', '.receipt.json'
python .\verify_release_pair.py --contract $Contract --component $ComponentArchive --omi $OmiArchive --omi-receipt $OmiReceipt
New-Item -ItemType Directory -Force .\omi-installer | Out-Null
python -c "import pathlib,tarfile,sys; a=pathlib.Path(sys.argv[1]); n=a.name[:-4]+'/install.py'; t=tarfile.open(a,'r:gz'); m=t.getmember(n); assert m.isfile() and not m.issym() and not m.islnk(); pathlib.Path(sys.argv[2]).write_bytes(t.extractfile(m).read())" $OmiArchive .\omi-installer\install.py
python .\omi-installer\install.py --help
$CodexSkillsRoot = Join-Path $HOME '.agents\skills'
$ClaudeSkillsRoot = Join-Path $HOME '.claude\skills'
python .\omi-installer\install.py --pack $OmiArchive --codex-root $CodexSkillsRoot --claude-root $ClaudeSkillsRoot
python .\omi-installer\install.py --pack $OmiArchive --codex-root $CodexSkillsRoot --claude-root $ClaudeSkillsRoot --check
```

The OMI installer verifies the exact TGZ and embedded `PACKAGE-MANIFEST.json`,
then writes plain managed copies (never symlinks) to the two explicit skill
roots. Its receipt is written last and binds the exact TGZ digest plus a
canonical size/sha256 inventory of the OMI tree and managed shared files.
`--check` verifies that inventory. An idempotent rerun uses staged files and an
identity-bound backup so a failed update restores the prior managed install;
unexpected transaction residue is preserved and refused for manual recovery.
The installer replaces only its own managed files. It does not inspect, read,
register, or change either client's persistent configuration. In particular,
it does not read or change Claude Code or Codex configuration; discovery
remains the client's ordinary filesystem scan.

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

## Transition-only bootstrap

The repository script below exists for one transition release only. It is not
the canonical installer or lifecycle authority, it does not accept URLs, and it
has no private default. Use it only when the versioned ZIP cannot yet be used and
you have an explicit local engine input:

```bash
python3 scripts/bootstrap_public_knowledge.py \
  --engine-source /path/to/workspace_knowledge_cc-<version>-py3-none-any.whl
```

`--engine-source` may instead name an unpacked component directory containing
exactly one matching wheel under `wheels/`, or a local
`workspace-knowledge-cc` checkout. Remote URLs, `git+` specifications, missing
paths, and ambiguous component directories are rejected before the bootstrap
creates or changes its managed root. New installs and updates should use the
verified ZIP path above.
