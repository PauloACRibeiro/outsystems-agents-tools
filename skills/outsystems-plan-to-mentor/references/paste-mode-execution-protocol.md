# Paste-Mode Execution Protocol

Optional supervised execution of a paste-mode Mentor package in ODC Studio,
driven by an agent (screen automation) or a human following the same loop. Use
it only when the user explicitly asks for supervised paste execution after the
Mentor-ready output file is written. Publishing requires separate explicit
approval; this protocol never publishes on its own.

## Execution gate

Before the first paste:

- Confirm the readable target name and the canonical app identity when
  available (app key from OutSystems MCP context or the package's Manual
  Setup Gate), not just a window or tab title.
- Obtain explicit approval for the exact tenant-changing action about to run:
  which app, which package, which blocks. Approval of supervised paste
  execution does not authorize direct hand-fixes or building directly in
  Studio; each of those is a different mutation scope needing separate
  confirmation unless it was already explicit in the approval.

## Session loop

Run the package as written: one block per paste, in the package's
producers-first order (references and producers before consumers). For each
block:

1. Verify the target app and tab before pasting. Similarly named apps and
   draft copies are the highest-risk mistake; confirm the app name and
   revision in the Studio title before every paste, not once per session.
2. Paste the block, submit once, and wait for Mentor to finish. Do not cancel
   a Mentor run merely because it is slow; slow is normal for large blocks.
   A user-requested abort or safety stop always remains available. After any
   abort, inspect the resulting app state before resuming: what an
   interrupted run leaves behind is not defined by the reviewed sources.
3. After Mentor finishes, read Mentor's own change summary line by line
   against the block's expected changes. This catches silent logic slips
   (wrong source bound to a count, wrong entity chosen) that compile cleanly
   and that TrueChange never flags.
4. Then run the TrueChange check: expect 0 errors, and record the warning
   delta against the baseline. New warnings are findings, not noise; falling
   warnings as elements get wired in are expected.
5. Record the block outcome (time, first-try or not, defects found) in the
   project build log, and make a checkpoint commit so the run is resumable
   from any block. Check the repository status first and inspect the
   already-staged path set and staged content before touching the index.
   If any unrelated change is already staged, do not modify the index and
   skip the checkpoint commit; report it as skipped. Otherwise stage only
   the build log and package artifacts touched by this run, never a blanket
   add, and verify the staged set matches before committing. Skip the commit
   when no suitable repository or clean surgical scope exists. A checkpoint
   commit does not snapshot the ODC tenant; on resume, tenant state must be
   reverified separately in Studio.

## Defect handling

- Re-prompt once per defective block with a corrective prompt naming the
  exact defect; hand-fix only after the re-prompt fails, and only within a
  mutation scope the user confirmed at the execution gate or since.
- Abandon criterion: three consecutive hand-fixed blocks means the approach
  is not working for this package. Stop and report; building directly in
  Studio using the package as the spec is a new mutation scope that needs
  its own separate confirmation.

## Duplicate and lost-input guards

- Never resubmit a creating prompt because the panel looks stuck; verify the
  panel state first. A duplicated modifying prompt is usually idempotent; a
  duplicated creating prompt can create duplicate elements.
- A click reporting success is not proof; verify the button or panel state
  changed before moving on. Focus changes during long waits silently swallow
  clicks (a publish click can be lost with the button still showing pending).

## Boundaries

- Publishing requires separate explicit approval; report the built state and
  stop.
- Runtime verification (smoke test, acceptance cases) is a separate stage
  after publish; see the runtime verification guardrails in
  `mentor-spec-guardrails.md`.
