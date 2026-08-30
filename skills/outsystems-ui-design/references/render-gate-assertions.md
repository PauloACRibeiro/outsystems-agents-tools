# Render-gate assertions — turning a disclosure into a check

Origin: written for this skill, 2026-08-30, from the restaurant-app-v2
execution walkthrough of 2026-08-28 (sprint-loop retrospective item P3).

## The failure this exists to remove

That run's blueprint carried a loudly worded build trap: the dispatch screen
must show the payload each channel will actually receive — requirement
`BR-SC-006`, *"show exactly what each channel will receive"*. It was written
down **twice**, in `evidence_boundary.review_notes` and in
`acceptance_checklist`. It shipped **unmet**: the channel cards rendered
placeholder descriptions and the attempts accordion expanded to nothing.

Neither place it was written carries authority. `acceptance_checklist` says so
in its own schema description — *"Advisory, human-facing prose only. NOT
authoritative"* — and `review_notes` is a note channel. **A disclosure that
reads like coverage and discharges nothing is worse than silence, because it
stops anyone looking.**

So the rule is not "disclose more carefully". It is: a claim about what the
screen must SHOW goes in a slot a machine can execute, exactly as an enforced
count goes in `screens[].assertions` rather than into prose.

## The slot

`screens[].render_gate`, an array of named assertions. Optional; each entry:

| Key | Required on | Means |
|---|---|---|
| `label` | every entry | Names the row the gate emits. Unique across the blueprint — a disclosure references it by this name alone. |
| `assert` | every entry | `widget` \| `populated` \| `text` \| `known-unverified` |
| `selector` | `widget`, `populated`, `text` | CSS. An **empty string** is the honest *no confident selector*; the gate records that screenshot-only. Guessing one is worse than admitting there is none. |
| `contains` | `text` (exclusive with `equals`) | A fragment the displayed text must carry. Case-insensitive at the gate. |
| `equals` | `text` (exclusive with `contains`) | The exact displayed text. Case-sensitive at the gate. |
| `reason` | `known-unverified` | Why no assertion is derivable. Must name a token this blueprint declares. |
| `discharges` | optional | Requirement ids this entry answers. The link a reviewer follows from a cited requirement to its check. |

```json
"render_gate": [
  { "label": "payload-exato", "assert": "text",
    "selector": "#payload", "contains": "Ementa de",
    "discharges": ["BR-SC-006"] },
  { "label": "registo-da-tentativa", "assert": "known-unverified",
    "reason": "O payload gravado em DispatchAttempt.Payload so aparece depois de expandir a tentativa, e o gate nunca clica." }
]
```

**`populated` cannot make the BR-SC-006 claim.** A placeholder is not empty, so
a placeholder **passes** a populated check while showing the user the wrong
thing — which is precisely how the v2 cards shipped. Only `text` can fail on
one. When a disclosure is about *which* content appears, the assertion is
`text`, never `populated`.

## Writing the expected string

Take it from the DOM or the copy deck, **never off a screenshot**: CSS
`text-transform` renders `Despacho` as `DESPACHO` while the text a gate reads is
still `Despacho`. The trap is invisible for a word you know and unguessable for
a localized label whose source casing you never saw.

The gate NFC-normalizes both sides and collapses runs of whitespace (a
non-breaking space included), so DOM indentation and an NFD/NFC difference are
not mismatches.

## The two rules that bind

**1. Every disclosure says where it is discharged.** Each line of
`evidence_boundary.review_notes`, `evidence_boundary.grounding_notes` and
`target_context.review_notes` carries one of two markers — by convention at
the end of the line, though the validator accepts it anywhere in the entry:

- `[render-gate: <label>]` — this note is checked by that assertion.
- `[no-runtime-claim]` — this note asserts nothing observable on the rendered
  screen (a provenance note, a scale warning, a platform constraint).

One of the two is always the right answer, which is why this blocks at
`--handoff` and needs no waiver. Write them **while writing the note**, not in a
later sweep: the judgement is cheapest in the moment the claim is made.

A **mistyped** marker is a contract error, not silent prose — `[render gate: x]`,
`[Render-Gate: x]`, `[render_gate: x]` and `[no runtime claim]` all fail loudly.
So does a line that *opens* with the token (`render-gate: Screen/label — ...`),
which is an assertion written where prose goes; it names where assertions
actually live. A near-miss must never be quieter than a miss; a marker that
degrades to prose is the original defect one hop later.

Both checks are deliberately narrow. The words themselves are ordinary, and a
note reading *"the render gate never sees it"* is correct prose — the most
likely sentence to sit next to a declared gap. Only a bracketed near-marker and
a line that starts with the token count.

**2. Every requirement id the blueprint cites is answered.** Any id in those
channels or in `acceptance_checklist` (`BR-SC-006`, `UC-005`, `C-016`) must
appear in some entry's `discharges`, `label` or `reason`. This is opt-in by your
own citation — a blueprint that cites no ids gets no finding — and it fires on
the specific miss rather than on general absence. A per-screen "does this screen
have any check" floor would not have caught v2: that screen was not check-free,
it was check-**incomplete**, and one trivial assertion clears any floor.

The id rule admits the forms the PRDs assign — two letter segments
(`BR-SC-006`) or a zero-padded tail (`UC-005`, `C-016`, `BR-001`) — and nothing
else, so `ISO-8601`, `AH-2026-08-28-001` and `A4-PDF-300` are not requirement
ids. One known miss, stated rather than papered over: an unpadded
single-segment id such as `US-9`. Widening the rule to catch it would readmit
every version number and ratio in the prose, and this rule blocks at handoff.

**On a busy screen, most cited ids will land `known-unverified`, and that is
the rule working.** The v2 dispatch screen cites eleven. Perhaps three are
observable on a rendered page without clicking; the rest are workflow and data
rules a render gate cannot see. Writing eight `known-unverified` entries is not
failure — each becomes an `unasserted` row in the gate run, the run exits 4,
and `execution-gates.md` §2 says plainly that exit 4 does not discharge the
render gate. The obligation stays visible instead of evaporating into prose.

**`populated` is not a content check.** A requirement about *which* content
appears is discharged by `text`, or declared `known-unverified` — never by
`widget` or `populated`, both of which pass on the exact placeholder the v2
cards shipped. The validator cannot tell a content requirement from a presence
one, so this is judgement the author owes; it is also the single easiest way to
make a requirement look answered while nothing checks it.

### What a discharge claim may say

Three constraints keep the claim cheap to read. Each closes a measured escape:
on the real v2 dispatch blueprint, one `widget` on `body` carrying all eleven
cited ids validated clean with zero warnings.

- **One id per `discharges` element.** `"BR-SC-006, BR-SC-009"` as a single
  string is rejected; the array reads one line at a time.
- **A `widget` or `populated` entry discharges at most one id.** A presence
  check answers one question about one element, so several ids on one is the
  shape of a rubber stamp. A `known-unverified` entry may name several —
  declaring several things uncovered at once is honest, and each still becomes
  an `unasserted` row the gate run must answer for.
- **An entry with an empty `selector` discharges nothing.** The gate records it
  `unasserted` — screenshot-only — so it answers no requirement. Name a
  selector, or declare the gap.

**The limit these do not cover, stated rather than claimed away:** nothing here
can judge whether a selector names the thing the requirement is about, or
whether a `known-unverified` reason names the thing actually left uncovered.
The anchor forces the reason to be concrete; it does not prove it is apt. These
rules make a claim auditable, not self-proving — a reviewer still reads them.

**The `acceptance_checklist` is not marker-bound.** It stays advisory by its own
schema description, so rule 1 does not reach it; what binds there is rule 2, the
requirement ids. A runtime claim written into the checklist that cites no id is
caught by neither — write that claim in `evidence_boundary.review_notes`, which
is the channel for it.

## When nothing is derivable

Say so, in the slot: `assert: "known-unverified"` with a reason that names what
is left uncovered. It is **not** free — it reaches the gate as an `unasserted`
row, which blocks automated discharge and owes a human screenshot verdict. It
is also not a length game: the reason must name a requirement id, a region or
an entity this blueprint declares, because a character floor accepts filler in
any language and an anchor does not. The screen the entry is on does not count
— naming the screen you are already on is free, and *"not checkable on this
screen"* is exactly the sentence the anchor exists to reject.

What it must never be is prose in the checklist that reads like coverage.
**Known-unverified is an honest verdict; an unmarked disclosure is not.**

## The sweep, at Step 4

Read by **structure**, not by wording. The artifact this rule comes from is
written in European Portuguese, so an English phrase trigger — "show exactly",
"must display" — fires on nothing that mattered.

1. Every entry of the three disclosure channels above.
2. Every requirement id the blueprint cites anywhere.

For each, one question: **does this assert a state a signed-in user could
observe on the rendered screen?** If yes, it becomes a named assertion. If no,
it is `[no-runtime-claim]`. If yes but nothing here can check it, it is
`known-unverified` with the reason.

### Worked case — BR-SC-006, verbatim

Shipped (v2, unmet). Note that neither line carries a marker, and nothing
answers `BR-SC-006`:

```
evidence_boundary.review_notes[0]:
  "ARMADILHA DE CONSTRUÇÃO - o payload da tentativa é um REGISTO, não uma
   previsão. Ao expandir uma tentativa, o conteúdo tem de vir de
   DispatchAttempt.Payload, gravado no momento da execução."
acceptance_checklist[3]:
  "Os quatro canais mostram, antes de qualquer execução, o payload exato que
   receberiam (BR-SC-006)."
```

*(gloss: "BUILD TRAP — the attempt's payload is a RECORD, not a forecast…" /
"The four channels show, before any execution, the exact payload they would
receive.")*

Written as checks:

```json
"render_gate": [
  { "label": "payload-exato", "assert": "text", "selector": "#payload",
    "contains": "Ementa de", "discharges": ["BR-SC-006"] },
  { "label": "registo-da-tentativa", "assert": "known-unverified",
    "reason": "DispatchAttempt.Payload so aparece depois de expandir a tentativa; o gate nunca clica." }
]
```

```
evidence_boundary.review_notes[0]:
  "ARMADILHA DE CONSTRUÇÃO - ... [render-gate: registo-da-tentativa]"
```

The first is executable and would have failed on the shipped build. The second
is not executable and says so — the accordion's content is behind a click, and
the render gate never clicks. Between them, nothing is left reading like
coverage.

## Handing the assertions to the gate

Project them; do not retype them. Retyping is the step that already failed once.

```bash
python3 scripts/validate_blueprint.py design/<screen-slug>/blueprint.json \
  --emit-render-gate-spec design/<screen-slug>/render-gate-screens.json
```

Windows PowerShell:

```powershell
python scripts\validate_blueprint.py design\<screen-slug>\blueprint.json `
  --emit-render-gate-spec design\<screen-slug>\render-gate-screens.json
```

Each entry becomes `expectWidgets` / `expectPopulated` / `expectText` /
`knownUnverified` on that screen. What the projection cannot supply is `path`
and `recordState`: neither is a design fact, both belong to the run, and the
gate rejects a screen missing either — loudly, so the omission cannot pass for
a check.
