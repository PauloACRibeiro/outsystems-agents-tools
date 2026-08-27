#!/usr/bin/env python3
"""Check proposed UI copy against the OutSystems Product Language word list.

The rule this enforces (UX-UI-Hub disposition X-11): user-visible strings are
generated against the OutSystems Product Language and Style Guide and the ODC
taxonomy, not against general UX-writing instinct. Writing that rule into a
SKILL.md does not enforce it; this does, for the part of the guide that is
mechanically checkable.

It reads BOTH grounding sources - the style guide's word list and the ODC
taxonomy - and refuses to run on either one alone.

What it decides, and what it refuses to decide
----------------------------------------------
VIOLATION (exit 1) - a word the guide's own word list marks "Don't use". That
column is unambiguous and the guide names the replacement.

TERMS (exit unchanged) - which of the taxonomy's concept names this copy uses.
Reported, never scored: the taxonomy has a documented escape hatch for a
genuinely new concept, so an unrecognised term is not a defect, and whether the
right term was chosen is a judgement no tool can make. What the tool CAN
guarantee is that the taxonomy was available and consulted.

CANDIDATE (exit 0) - a contraction whose stem is not a pronoun. The guide bans
noun contractions ("the update's ready") but the identical form is an ordinary
possessive ("the update's author"), and nothing in the string tells the two
apart. Reported for a human to judge. Deciding here would produce a plausible
number that is sometimes wrong, which is worse than reporting.

Exit codes: 0 clean (candidates may still be reported), 1 violations,
2 either source could not be read - a DEGRADED run that scored nothing.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

_REFERENCES = Path(__file__).resolve().parents[1] / "references"
DEFAULT_GUIDE = _REFERENCES / "product-language-style-guide.md"
DEFAULT_TAXONOMY = _REFERENCES / "odc-taxonomy.csv"

# The taxonomy's first three columns are the concept hierarchy; the remaining
# columns are definitions and prose, which are not names.
_TAXONOMY_NAME_COLUMNS = 3
# One- and two-letter cells are punctuation artefacts, not concept names.
_MIN_TERM_LENGTH = 3

# Stems that may carry a contraction. Anything else is reported, not decided.
PRONOUN_STEMS = {
    "i", "it", "you", "we", "they", "he", "she", "that", "there",
    "what", "who", "here", "let", "this",
}
# Built by join rather than written as a literal alternation: the pack
# reference-graph gate reads a bare `a|b|c` run in source as a path reference.
CONTRACTION_SUFFIXES = ("s", "t", "re", "ve", "ll", "d", "m")
CONTRACTION = re.compile(
    r"\b([A-Za-z]+)['’](" + "|".join(CONTRACTION_SUFFIXES) + r")\b"
)


WORD_LIST_HEADER = "| Word | Status |"
_MAX_ROW_SPAN = 40  # a row that never closes means the table shape changed


def _word_list_rows(text):
    """Yield the word list's rows as 7-cell lists.

    The table is NOT one row per line. Upstream cells carry hard line breaks -
    `abort`'s replacement cell spans two lines, and one row spans a blank line -
    so a per-line parser silently truncates cells and drops rows. It read
    abort's replacement as "stop" where the guide says "stop cancel".
    """
    lines = text.splitlines()
    start = next(
        (n for n, line in enumerate(lines) if line.startswith(WORD_LIST_HEADER)),
        None,
    )
    if start is None:
        return
    buffer, span = "", 0
    for line in lines[start + 2 :]:
        if not buffer:
            if line.startswith("#"):
                return
            if not line.strip():
                continue
            if not line.startswith("|"):
                return
        buffer = line if not buffer else buffer + " " + line
        span += 1
        cells = [c.strip() for c in buffer.strip().strip("|").split("|")]
        if buffer.rstrip().endswith("|") and len(cells) >= 7:
            yield cells
            buffer, span = "", 0
        elif span > _MAX_ROW_SPAN:
            raise OSError(
                "the word list's table shape is not what this parser expects; "
                "a row failed to close within %d lines" % _MAX_ROW_SPAN
            )


def load_word_list(guide_path):
    """Return {phrase: replacement} for every "Don't use" row in the guide.

    Raises OSError when the guide is absent - it is withheld from public
    distributions, and a caller must report that rather than score without it.
    """
    text = Path(guide_path).read_text(encoding="utf-8")
    banned = {
        cells[0].lower(): cells[4]
        for cells in _word_list_rows(text)
        if cells[1] == "Don't use" and cells[0]
    }
    if not banned:
        raise OSError(f"no word-list rows found in {guide_path}")
    return banned


def load_taxonomy_terms(taxonomy_path):
    """Return the concept names in the taxonomy's hierarchy columns.

    Raises OSError when the taxonomy is absent. Both sources ground a run:
    scoring on one of them and reporting as though both were consulted is the
    failure this rule exists to prevent.
    """
    terms = set()
    with open(taxonomy_path, newline="", encoding="utf-8-sig") as handle:
        for row in csv.reader(handle):
            for cell in row[:_TAXONOMY_NAME_COLUMNS]:
                name = cell.strip()
                if len(name) >= _MIN_TERM_LENGTH:
                    terms.add(name)
    terms.discard("Domain")
    terms.discard("Category")
    terms.discard("Subcategory")
    if not terms:
        raise OSError(f"no concept names found in {taxonomy_path}")
    return terms


def find_terms(copy_text, terms):
    return sorted(
        term
        for term in terms
        if re.search(rf"\b{re.escape(term)}\b", copy_text, flags=re.IGNORECASE)
    )


def find_violations(copy_text, banned):
    hits = []
    for phrase, replacement in sorted(banned.items()):
        if re.search(rf"\b{re.escape(phrase)}\b", copy_text, flags=re.IGNORECASE):
            hits.append((phrase, replacement))
    return hits


def find_candidates(copy_text):
    return [
        match.group(0)
        for match in CONTRACTION.finditer(copy_text)
        if match.group(1).lower() not in PRONOUN_STEMS
        and match.group(2) != "t"  # verb + n't is the form the guide allows
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="copy to check, inline")
    source.add_argument("--file", help="file of copy to check, one string per line")
    parser.add_argument(
        "--style-guide",
        default=str(DEFAULT_GUIDE),
        help="path to the vendored Product Language and Style Guide",
    )
    parser.add_argument(
        "--taxonomy",
        default=str(DEFAULT_TAXONOMY),
        help="path to the vendored ODC Taxonomy",
    )
    args = parser.parse_args(argv)

    try:
        banned = load_word_list(args.style_guide)
        terms = load_taxonomy_terms(args.taxonomy)
    except OSError as exc:
        print(
            f"DEGRADED: a grounding source is unavailable ({exc}). No copy was "
            "checked. Both sources are withheld from public distributions - see "
            "references/copy-grounding.md for how to obtain them.",
            file=sys.stderr,
        )
        return 2

    try:
        copy_text = args.text if args.text is not None else Path(args.file).read_text(
            encoding="utf-8"
        )
    except OSError as exc:
        print(f"DEGRADED: cannot read the copy ({exc}). Nothing checked.", file=sys.stderr)
        return 2

    violations = find_violations(copy_text, banned)
    candidates = find_candidates(copy_text)

    for phrase, replacement in violations:
        instead = replacement or "(the guide names no replacement)"
        print(f"VIOLATION  \"{phrase}\" is marked Don't use. Use this instead: {instead}")
    for candidate in candidates:
        print(
            f"CANDIDATE  {candidate} - a non-pronoun contraction, or an ordinary "
            "possessive. The guide bans the first and allows the second; judge it."
        )
    if not violations and not candidates:
        print("clean: no word-list violations, no contraction candidates")

    recognised = find_terms(copy_text, terms)
    print(
        "TERMS      "
        + (
            ", ".join(recognised)
            if recognised
            else "none of the taxonomy's concept names appear in this copy"
        )
    )

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
