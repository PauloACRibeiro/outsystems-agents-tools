# The fusion method — harvested rules

Source: the method log and fusion map of a real 2026-07-14 redesign that took an
existing 23-screen OutSystems app down to 9 screens
(`docs/superpowers/evidence/2026-07-14-ui-design-graduation/ia/`), plus the
2026-08-08 Phase 1 chain trial's friction log. Every rule below is something
that log paid for. Nothing here is invented for tidiness.

---

## R1 — The source's structure is the previous author's guess at the IA. Do not inherit it.

The strongest evidence in the whole redesign was a naming convention that
described nothing. `Adv_` looked like a domain; rehoming its six screens left
**nothing behind**, which is the proof it was never a domain — only a junk
drawer. `CRUD_` looked like four screens; they were one screen copy-pasted four
times, and the copy-paste artefacts (duplicated notes on three of four) proved
it.

**The test:** take a grouping the source asserts. Rehome every member to where
its user goal actually points. If nothing remains, the grouping was filing, not
architecture — dissolve it.

On a requirements doc the same trap wears different clothes: section headings,
epic names, and the order the author happened to write things in. A PRD section
is a unit of *writing*, not a unit of *navigation*.

## R2 — Cluster by what the user is trying to do.

Two candidates belong on one screen when they are the same job with a different
payload. Search single / search multiple / search by template are three
payloads of one job; four CRUD operations are four payloads of one job. Neither
is four screens.

Two candidates stay apart when they are different jobs over the same data.
Configuring a migration and operating one are different jobs; storing a scoring
script and running a query are different jobs — that last one was fused in the
first draft and **split back out at the human gate**, which is why the gate
exists.

## R3 — Ground the inventory in what is *behind* the screen, not what it looks like.

The single most important finding of the original phase came from a read-only
scan of the tenant, not from any screenshot: roughly 30 server actions
implementing a real migration engine with no counterpart in the public API. The
Migration screens *looked* like two more demo pages. **Without that scan the
fusion map would have been wrong.**

This skill is local and has no tenant reach, so the equivalent move is:

- **Requirements doc:** bind each screen to the entities and actions the
  document names, and treat a capability the document never grounds in data as
  a candidate to interrogate, not a screen to draw.
- **Existing app:** get the offline scaffold inventory (or the as-built
  snapshot) before deciding anything, and read it for behaviour, not only for
  names — see R6.

## R4 — Nothing is silently dropped, and some things were never destinations.

Every candidate resolves to at least one screen or is explicitly dissolved into
something that is not a screen. In the real case exactly one dissolved:
"escape this string for JSON" became an inline affordance beside every raw-DSL
textarea, because **nobody navigates somewhere to escape a string** — they need
it where they are already typing.

A candidate may also **split**: the load-data page's reference half became
onboarding and its console half became an index operation. One page, two jobs.

The validator enforces the accounting, not the judgement: it will tell you a
candidate has no disposition and that a screen traces back to nothing. It
cannot tell you a fusion is wrong.

## R5 — Let the defects choose the design, and check the premise you were given.

The strongest argument in the real redesign was not aesthetic: the app's core
value proposition was intact on **2 of 23** screens, and every failure mode was
a duplication artefact. That made fusion the cure rather than a preference.

Two of five analysis agents **contradicted the brief they were given** — and
were right (the most mature screen was not the one named; the catalogue held 50
entries, not 33). Both corrections came from agents told to verify a premise
rather than confirm a conclusion. When you delegate analysis, hand over a claim
to check.

## R6 — Inventory entries carry behaviour, not just names (trial F-11).

The Phase 1 chain trial built a scaffold inventory that captured every
signature — names, inputs, outputs — and missed that the action the entire
screen read through **returns only the 10 most recent rows**. The fact sat one
field away from what was captured, in a description nobody selected. The PRD's
own worked example ("4 of 27 entries showing") was unimplementable against it,
and nothing caught that until a human asked.

So: every screen states what it **does** and its **key interactions**, and every
data binding states its **behavioural contract** — caps, limits, states, async
semantics. Names alone hand the design run a label and no contract, and the
reconciliation then happens by hand, late.

## R7 — A hand-off needs a receiving end (trial F-12).

The trial's plan asserted "hand the query off to the console pre-loaded", the
blueprint drew the button, and the target console's only input accepted a
different type entirely. Neither route carried the receiving end and nothing
forced anyone to check the target's contract.

So a navigation edge that carries a payload must find that payload in the
target screen's `accepts`. This is the cheapest check in the skill and it
catches a class of failure that otherwise surfaces at build time.

## R8 — One inventory, and both downstream routes read their names out of it.

In the trial, all eight names shared between the plan route and the blueprint
route agreed first time. That was **not** evidence the reconciliation boundary
is well drawn — both routes read those names out of one prior inventory, so
they *could not* disagree. Agreement was structural, not earned.

That is worth mandating rather than celebrating: a shared upstream inventory
converts a manual check into an invariant and costs nothing. This artifact is
that inventory. Feed its screen names, entity names and action names to the
capability plan **and** to every design run, and do not let either invent its
own.

The honest caveat travels with it: on a greenfield screen, where the plan names
data producers from intent and the design names them from a wireframe, the
manual check is doing real work. Using one inventory removes the disagreement;
it does not verify that the names are right.

**The greenfield asymmetry (trial G-04):** on a requirements doc the
shared-name guarantee covers **entities**, and deliberately **not actions**.
New capabilities need new logic, and the logic's names do not exist at
inventory time — naming them here would pre-empt the capability plan and
violate this skill's own no-logic-design scope guard. So new behaviour travels
as prose in `behavior_notes`, and the future actions are named by the plan and
never appear in this file. Entity names flow inventory → plan, mechanically
enforced (a plan written without consuming the inventory fails the
reconciliation gate on exactly the names the inventory introduced — the
greenfield trial demonstrated this); new-action names flow plan → build, and
the inventory abstains on purpose. The gate therefore covers less in exactly
the direction where sharing matters most: the action half of the shared-name
check is manual, at build time. The same asymmetry governs shapes — a new
entity's name is authoritative here (`introduced_here`), but its attributes
are typed by the capability plan, not by this inventory and not by a design
run (the brief's delegation line says so).

## R9 — Where the judgement stops.

The original method log's own verdict, written during the work: steps 1–4
(capture, ground, analyse, cluster) are mechanical and repeatable; steps 5–6
(let the defects choose the design; wireframe without leaking the answer) are a
stance, and a skill would either trivialise them or bloat.

This skill covers 1–4 and stops. Wireframing is `outsystems-ui-design`'s job,
one run per screen, and the design there starts from a wireframe the human
brings — not from anything generated here.
