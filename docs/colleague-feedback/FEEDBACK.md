# Sprint-loop friction log

Fill this in **by hand, while you work** — one entry each time the loop surprised
you, cost you time, or made you guess. Rough notes beat polished prose; a
half-sentence written in the moment is worth more than a tidy write-up from
memory a week later. When you are done (or at the end of a sprint), save this
file and run the bundler from the folder this file came in —
`python3 collect_feedback_bundle.py --feedback FEEDBACK.md` on macOS or Linux,
`python collect_feedback_bundle.py --feedback FEEDBACK.md` in Windows
PowerShell (`python3` is not a command on Windows) — then email the single
`.tgz` it produces to
`<the person who sent you this pack>`. The bundler is offline and read-only: it
gathers this file, the pack's PACKAGE-MANIFEST.json (the version and digest
record), the identity stamps of your installed OutSystems skills, and
any local run receipts, redacts your home directory, environment hostnames and
any id that looks like a GUID, and writes one archive. Nothing is uploaded, and
`--dry-run` first lists every file it would include and how many redactions
each rule made, without writing anything — review that list before the real run.

## The steps

| Step | What it is | Skill |
|---|---|---|
| 1 | Idea to requirements + screen inventory | `brainstorming` (or a hand-written PRD) |
| 2 | Requirements to capability plan | `writing-plans` |
| 3 | Wireframe to blueprint (one run per screen) | `outsystems-ui-design` |
| 4 | Plan review + patch, then hand off to the build skill | `outsystems-plan-to-mentor` |
| 5 | Build: pseudocode + Mentor prompts | `outsystems-mentor-implementation` |
| 6 | Run it on your tenant, and publish | the OutSystems MCP plugin |
| Grading | Score the published app from its live URL | `outsystems-runtime-ui-audit` |

Friction with installing the loop, or with this feedback kit itself, is in scope
too — log it against whichever step you were trying to reach.

## How to write an entry

Four fields, in this order. Keep each to a couple of lines.

- **Expected** — what you thought would happen, in your words.
- **Actually happened** — what you saw. Quote the exact message if there was one.
- **What I did next** — retried, edited by hand, asked someone, gave up, shipped anyway.
- **Cost** — rough minutes lost, or "none, just confusing". This is how we rank.

Do not sanitise your workaround. "I stopped using the skill and did it manually"
is the single most useful thing you can write here.

---

## My entries

### Entry 1 —
- **Step / skill:**
- **Expected:**
- **Actually happened:**
- **What I did next:**
- **Cost:**

### Entry 2 —
- **Step / skill:**
- **Expected:**
- **Actually happened:**
- **What I did next:**
- **Cost:**

<!-- Copy an entry block for each new one. There is no limit. -->

---

## EXAMPLES — delete this whole section before sending

### Example A — blueprint asked for a screen I had already built
- **Step / skill:** Step 3, `outsystems-ui-design`
- **Expected:** I gave it a wireframe for a screen that already exists in my app,
  and expected it to notice and reuse what was there.
- **Actually happened:** It produced a blueprint for a brand-new screen with new
  entity names, as if the app were empty.
- **What I did next:** Hand-edited the blueprint to point at my existing entity
  names before letting step 5 touch anything.
- **Cost:** ~25 min, plus the nagging feeling I had missed a flag.

### Example B — Mentor run looked like it failed but had not
- **Step / skill:** Step 5, `outsystems-mentor-implementation`
- **Expected:** A clear success or failure at the end of the run.
- **Actually happened:** It reported no changes detected, but the app in the
  portal had visibly changed and the revision number had gone up.
- **What I did next:** Checked the revision by hand in the portal, decided to
  trust the portal over the message, and carried on.
- **Cost:** 10 min, and I nearly re-ran the whole thing on top of itself.

### Example C — audit refused to score my app
- **Step / skill:** Grading, `outsystems-runtime-ui-audit`
- **Expected:** A score for my published screen from its runtime URL.
- **Actually happened:** It refused, saying the URL redirected to a login page.
- **What I did next:** Nothing — I did not have a way to make the screen
  anonymous, so I skipped the quality gate entirely for this sprint.
- **Cost:** Blocked. No grade for the sprint.
