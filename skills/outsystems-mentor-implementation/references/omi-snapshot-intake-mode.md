# OMI Generated App Snapshot Intake Mode

Owned by outsystems-mentor-implementation; SKILL.md routes here for app-snapshot.yaml / studio-handoff.md intake.

Use this mode when the user asks to continue from generated app review, use an
`app-snapshot.yaml`, use a `studio-handoff.md`, create surgical fixes from a
generated app snapshot, or turn a Mentor Web post-generation review into Mentor
Studio / ODC Studio prompts.

Open [source-map.md](source-map.md), then load the shared
bridge reference:

```text
../shared/mentor-generated-app-bridge.md
```

Before producing Studio-native output:

1. Read `app-snapshot.yaml`. If `app-snapshot.yaml` is missing, block and ask
   the user for the snapshot path before continuing.
2. Read `studio-handoff.md` when present.
3. Check `decision.recommendation`.
4. Emit Studio-native prompts only when `decision.recommendation` is
   `continue_in_mentor_studio`, or when the user explicitly overrides the snapshot
   decision.
5. If the recommendation is `regenerate_in_mentor_web`, route the work back to
   `mentor-app-generator` for regeneration prompts instead of producing Studio
   prompts.
6. If the recommendation is `manual_review_required`, ask for the missing
   evidence named in the snapshot before producing Studio prompts.
7. Treat observed, inferred, and unknown facts differently.
8. Use observed producers as dependency inventory.
9. Keep inferred facts as review notes, not confirmed Studio structure.
10. Do not infer exact widgets, widget IDs, local variables, event order,
   bindings, screen aggregates, data actions, or CSS class usage unless the
   snapshot or handoff explicitly exposes them.

This mode does not generate Mentor Web requirement documents or regeneration
prompts. Route those back to `mentor-app-generator`.

Example gate:

No `app-snapshot.yaml` means no Studio prompt. Ask: Which `app-snapshot.yaml` path should I use? Do not emit `### Mentor Studio Prompt` until the snapshot has been read and its `decision.recommendation` allows Studio continuation.

## Snapshot-Derived Evidence Status

- Observed snapshot facts inherit the backing source label when the snapshot
  names current public docs, mirrored `docs-odc`, generated official UI catalog
  evidence, tenant observation, or another explicit source.
- Inferred snapshot facts use `Unverified gap` unless separately grounded by
  current official evidence before output.
- Unknown snapshot facts use `Unverified gap` and should usually move to
  `Unknowns And Fallback Behavior` instead of becoming Studio structure.
