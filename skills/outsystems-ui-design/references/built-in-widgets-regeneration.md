---
name: builtin-widgets-regeneration
description: How to generate references/built-in-widgets.md, the runtime-contract inventory of the built-in platform widgets. Read this when that file is missing — the public distribution of this skill does not include it.
---

# Generating the built-in widget inventory

> **Origin:** written for this skill (2026-08-07) alongside the public
> distribution of the sprint loop, which withholds the generated inventory on
> licensing grounds. The procedure below mirrors the maintainer refresh
> procedure; `scripts/generate_builtin_widgets.py` is the authority on its own
> arguments.

`references/built-in-widgets.md` is a generated inventory of the ~30 built-in
platform widgets (Button, Input, Dropdown, TableRecords, AdvancedHtml, …) and
their exact runtime property, event, enum, and placeholder names. The skill uses
it to verify a widget's real property names instead of guessing them.

**It is not included in the public distribution of this skill.** It is derived
from an OutSystems-internal source repository that publishes no license, so the
generated file cannot be redistributed. The generator script ships instead, so
you can produce the file yourself in about a minute.

## Working without it

The skill functions without this file. When it is absent:

- Map regions and choose blocks normally — nothing else in the bundle depends
  on it.
- When a step needs a built-in widget's exact property name, use
  `references/blocks-index.md` for block arguments and placeholders, and state
  plainly that the built-in widget's property list is **unverified**.
- Do not invent property names from memory. An unverified name that looks right
  is worse than an acknowledged gap: it fails at build time, after the design is
  already approved.

## Generating it

You need access to the OutSystems GitHub organization and the `gh` CLI
authenticated against it (`gh auth status` should show you are logged in). If
you do not have that access, keep working without the file as described above.

Two things that stop people here, neither of which is a defect:

- **A freshly installed `gh` is only visible in new terminals.** After
  `winget install GitHub.cli` (or an installer on macOS), the terminal that ran
  the install still has its old PATH — `gh` appears "not recognized". Open a
  new terminal, or on Windows refresh PATH in place:
  `$env:Path = [Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')`
- **Browser sign-in fails on machines the OutSystems IT policy does not trust**
  (conditional access / unmanaged device). That is not the end of the road, and
  treating it as one gives up the capability for no reason. A classic personal
  access token works from an untrusted machine — measured 2026-08-10 on an
  unmanaged Windows VM whose browser login had just been refused. Create one at
  <https://github.com/settings/tokens> with scopes `repo` and `read:org`, then —
  this is the step people miss — **authorize it for the OutSystems
  organization** through *Configure SSO* on the token list. Run `gh auth login`
  and choose *Paste an authentication token*. Two traps worth knowing: a valid
  but unauthorized token fails with a 403 that names SAML SSO rather than the
  missing authorization, and **regenerating a token silently drops its SSO
  authorization**, so if you regenerate one to add an expiry you must authorize
  it again. Confirm access before running the generator:
  `gh api repos/OutSystems/runtime-widgets-js --jq .full_name`.
- **If the token route is refused as well, stop there.** That is a real hard
  stop, not something to retry around: keep working without the file as
  described above. The skill stays fully usable; only built-in widget property
  names remain unverified. Do not leave the user with an open-ended "come back
  when authenticated" as the only exit — proceeding without the file is the
  documented, supported outcome.

Run from this skill's own directory.

macOS/Linux:

```bash
TMP=$(mktemp -d)
for f in $(gh api repos/OutSystems/runtime-widgets-js/contents/src/Generated --jq '.[].name'); do
  gh api "repos/OutSystems/runtime-widgets-js/contents/src/Generated/$f" --jq '.content' \
    | base64 -d > "$TMP/$f"
done
COMMIT=$(gh api repos/OutSystems/runtime-widgets-js/commits/HEAD --jq '.sha[:12]')

python3 scripts/generate_builtin_widgets.py \
  --source "$TMP" --out references/built-in-widgets.md \
  --commit "$COMMIT" --date "$(date +%F)"
```

Windows PowerShell. Do not translate the block above — `mktemp`, `base64` and
`python3` do not exist on Windows, and `date +%F` resolves to the `Get-Date`
alias and fails with a parameter-binding error rather than a missing-command
one:

```powershell
$Tmp = (New-Item -ItemType Directory -Path (Join-Path $env:TEMP ("bw-" + [guid]::NewGuid().ToString("N").Substring(0,8)))).FullName
foreach ($f in (gh api repos/OutSystems/runtime-widgets-js/contents/src/Generated --jq '.[].name')) {
  $B64 = gh api "repos/OutSystems/runtime-widgets-js/contents/src/Generated/$f" --jq '.content'
  # GitHub wraps base64 across lines; FromBase64String rejects the whitespace.
  [IO.File]::WriteAllBytes((Join-Path $Tmp $f), [Convert]::FromBase64String((($B64 -join '') -replace '\s','')))
}
$Commit = gh api repos/OutSystems/runtime-widgets-js/commits/HEAD --jq '.sha[:12]'

python scripts\generate_builtin_widgets.py `
  --source $Tmp --out references\built-in-widgets.md `
  --commit $Commit --date (Get-Date -Format 'yyyy-MM-dd')
```

The generator is Python 3.7+ standard library only and is deterministic: the
same inputs always produce byte-identical output, because the commit and date
are passed in rather than read from the clock.

Regenerate when the platform ships new built-in widgets. Once generated, treat
the file as read-only — it is machine output, and a hand edit is silently lost
on the next run.

## Keep it local

Do not commit the generated file to a public repository or share it outside
OutSystems. The source repository it is derived from is internal and carries no
published license; that restriction follows the generated content.
