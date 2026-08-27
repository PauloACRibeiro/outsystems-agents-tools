# Copy grounding — the words are a constraint, not a preference

Origin: written for this skill (UX-UI-Hub disposition X-11 / X-12 / X-13,
adopted 2026-08-24). The two sources it binds are harvested; this file is not.

Load this whenever the design proposes a **user-visible string**: a heading, a
button label, a menu entry, a field label or placeholder, an empty-state line,
a loading line, an error or a toast. Not for region descriptions, review notes
or acceptance items — those are ours, and nobody reads them in the product.

The rule is short. **We do not invent OutSystems product wording.** Two
OutSystems assets already decide it, and both are bundled here.

| Source | What it decides |
|---|---|
| `references/odc-taxonomy.csv` | Which **term** names a concept — 433 rows of Domain / Category / Subcategory with definitions, characteristics and keyword clusters |
| `references/product-language-style-guide.md` | How the sentence is **written** — voice and tone, grammar and punctuation, per-component copy guidance (buttons, empty states, input fields, links, tooltips, toasts, page headers, pagination, tags), and a word list with four statuses |

## The four steps

1. **Term first.** Look the concept up in the taxonomy before naming it. Prefer
   the term that is already there, in the guide's spelling.
2. **The escape hatch is real, and it has a second half.** If the concept is
   genuinely new and no term fits, you may introduce one — *and* tell the user
   to submit it at <https://forms.gle/btxJcPFja532ftkv9> so it enters the
   taxonomy. Introducing a term without routing it is half the rule.
3. **Sibling consistency.** Before drafting, look at how this app already
   phrases the same action or concept — the screen inventory, the chrome
   labels, the other screens in this blueprint. Reuse the established shape:
   verb choice, sentence shape, capitalisation, terminal punctuation. If you
   deliberately diverge, **say so and say why** in the round's diff statement.
   A string can be perfectly compliant and still be the odd one out.
4. **Run the checker before the blueprint goes out.**

```bash
python3 "$SKILL_DIR/scripts/check_copy.py" --file proposed-copy.txt
```

Exit 0 clean, 1 violations, 2 degraded — nothing was checked.

## What the checker decides, and what it refuses to

It reads **both** sources and refuses to run on either one alone.

It reports a **VIOLATION** only for a word the guide's own word list marks
*Don't use*, and it names the replacement the guide gives. That column is
unambiguous.

It reports a **TERMS** line naming which of the taxonomy's concept names this
copy uses. That is reported, never scored — the escape hatch in step 2 means an
unrecognised term can be perfectly correct, and whether you picked the right
term is a judgement. What the line guarantees is that the taxonomy was there and
was consulted, rather than assumed.

It reports a **CANDIDATE**, without failing, for a contraction whose stem is
not a pronoun. The guide bans noun contractions ("the update's ready") and the
identical form is an ordinary possessive ("the update's author"). Nothing in
the string separates them, so the checker hands it to you rather than guessing.

Everything else in the guide — tone, the per-component guidance, sentence
shape — is yours to read and apply. A clean checker run is not a compliant
string; it means no *word-list* violation was found.

## Provenance

Both files are vendored, not authored here.

- Source: `OutSystems/-UX-UI-Hub` (private) @ `9e3258b299ee38af31c4414b0772858060c6be38`
  (`main` tip, 2026-08-20), paths `docs/context/shared/`.
- `odc-taxonomy.csv` — byte-for-byte upstream. sha256
  `3950dc61d498018d245a6e5fdc6bd7b2c63bfe99c8d79947c6eec71f049657b1`.
- `product-language-style-guide.md` — upstream sha256
  `9d9841619eef004d901008b3c8fa1a011eb2a9f29718ebd72777f0c1a87478ae`, with the
  206 inline base64 images stripped (2.2 MB → 133 KB). Each image *usage* is
  replaced in place by a literal `(image omitted)` marker, never deleted with
  its line, so headings and table cells survive. The 206 dangling reference
  definitions (`[imageN]: <image-omitted>`) that only pointed at those payloads
  are removed outright — they carry no alt text and no structure, and every
  surviving stub reads to `skill_estate_lint` as a broken relative link.

Neither is ours to edit. The style guide carries its own governance section and
its own change notes; corrections go upstream.

## Degraded mode — where these files are absent

Both are internal OutSystems assets and are **withheld from every world-visible
export**, the same disposition as `references/built-in-widgets.md`. On an
install without them:

- `check_copy.py` exits **2** and says so — for a missing taxonomy exactly as
  for a missing style guide. It never scores a run it could not ground. Do not
  treat exit 2 as a pass.
- Say once, plainly, that copy is **ungrounded** — taxonomy terms and word-list
  compliance were not checked — rather than implying the wording was verified.
- Step 3, sibling consistency, still works. It reads the app you are already
  designing and needs no external file. It is the part of this rule that never
  degrades.

To obtain them, a colleague with OutSystems org access can fetch both from the
pinned commit above with `gh api`, into `references/` under these names.
