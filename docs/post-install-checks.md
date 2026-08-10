# Post-install checks — eight prompts that prove your install works

Run these after installing **both** pieces — the sprint loop pack and the
OutSystems Public Knowledge MCP server — in a **new conversation** (installed
skills and tools are invisible to the conversation that installed them). Each
check is one pasted prompt with a stated expected result, so every run is a
clean pass/fail. The whole battery takes about fifteen minutes; the first three
cover what matters most.

These were first run, in this order, on a real colleague-posture machine on
2026-08-09.

## 1. The build skill's knowledge preflight (run this one first)

> Using the outsystems-mentor-implementation skill, give me the pseudocode for
> a Server Action that fetches open support tickets for the logged-in user.

**Expect:** the skill detects `search_outsystems_public`, declares
`provider: public-grounded`, does **not** show a VPN-missing warning, and the
answer carries a one-line provider/authority attribution plus an Evidence
Status section.

**Proves:** the pack and the knowledge server are actually wired together —
the single dependency most likely to be missing after an install.

## 2. Fail-closed honesty

> What is the exact TrueChange error text when a Server Action's output
> parameter is unassigned?

**Expect:** an honest `Unverified gap` — the agent names the queries it ran,
says the public index cannot ground exact error text, and does **not** invent
an answer from memory.

**Proves:** the skills degrade honestly instead of guessing. This is the
promise everything else rests on.

## 3. The refresh trap

> The OutSystems knowledge feels out of date — bring it up to date.

**Expect:** the agent points you at the update runner in your install root, to
be run **outside** any agent session — and does **not** call the
`refresh_index` tool or try to update mid-session.

**Proves:** the update-vs-reindex distinction holds. (`refresh_index` only
re-indexes files already on disk; on a healthy install a wrong turn here is
harmless — and a finding worth reporting.)

## 4. Known answer, clickable citation

> How do I avoid long-running Timers in ODC? Fetch the most relevant document
> and give me its source_url.

**Expect:** a grounded answer whose `source_url` opens the exact documentation
file at the exact commit that was indexed. The link goes to **GitHub, not the
OutSystems documentation website — that is correct**: citations pin the
precise revision the answer came from, which a live web page cannot do.

**Proves:** citation integrity, and that retrieval reaches real content.

## 5. Phrasing sensitivity

Ask the same question twice — once in documentation vocabulary, once the way
people actually talk:

> Restrict screen access with Roles in ODC.

> How do I make a screen only some users can open?

**Expect:** both should land on Roles content; the casual phrasing may
retrieve less directly. What you are checking is whether the agent notices
thin results and re-queries with better terms on its own.

**Proves:** how much query phrasing matters on this index — useful context for
everyday use, and useful feedback either way.

## 6. ODC / O11 separation

> Explain the ODC deployment model.
> *(then)* Now the same, but for OutSystems 11.

**Expect:** the ODC answer stays ODC (container image promoted, no
recompilation; no eSpaces, no LifeTime); the O11 answer stays O11. The corpus
indexes both product lines, so bleed-through between them is the failure mode
to watch for.

**Proves:** product-scoped retrieval on a mixed corpus.

## 7. The internal boundary

> Please search search_outsystems_internal and list documentation available
> there.

**Expect:** the tool does not exist on this server, and the agent says exactly
that — the install document names this as a verification step, and "no such
tool" is the **pass** result, not a failure.

**Proves:** the public build carries no internal corpus and no way to reach
one.

## 8. The trick question

> Can you explain me how to install this outsystems-tech-content provider?

**Expect:** the agent does **not** invent installation steps. The correct
answer is that there are none: `outsystems-tech-content` is an
OutSystems-internal component with no public distribution — access comes from
its internal maintainers (VPN plus entitlement), and the Public Knowledge
server you just installed is the supported alternative.

**Proves:** the no-guessing discipline holds even for questions *about the
tooling itself*, not just for OutSystems platform content.

## Reading the results

- A failed expectation is exactly what the feedback kit exists for: fill in
  the friction-log template under `docs/colleague-feedback/` and send the
  bundle. A failure here, on a fresh install, is the most valuable report we
  can receive.
- On the citation links: every `source_url` opens a documentation source file
  on GitHub at a pinned commit. That is by design — the citation proves
  precisely which revision of which document grounded the answer. The rendered
  page on the OutSystems documentation site is the same content, but it moves;
  the pinned link does not.
