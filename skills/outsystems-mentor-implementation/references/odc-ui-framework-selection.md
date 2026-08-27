# ODC UI Framework Selection For OutSystems Mentor Implementation

Use this reference before `odc-ui-generation.md` for any request involving ODC UI generation, Mobile UI, OutSystems UI on mobile, shared UI libraries, icon libraries, or UI framework migration.

This file decides whether `outsystems-mentor-implementation` can generate paste-ready Mentor Studio prompts or must stop at framework guidance and review guardrails.

## Core Rule

Classify the target app type and UI framework before generating UI instructions.

If the app type or framework is unknown and the distinction affects correctness, ask one clarifying question before generating.

Preferred clarifying question:

```text
Is this target a Web app using OutSystems UI, a Mobile app using OutSystems UI, a Mobile app using the newer Mobile UI framework, a Library, or a Mobile Library?
```

## Preflight

Run this preflight for every UI request:

```text
1. What ODC asset is being changed?
2. Is it a Web app, Mobile app, Library, or Mobile Library?
3. Which UI framework is in play: OutSystems UI, Mobile UI, or unknown?
4. Is Mentor Studio documented and suitable for this target?
5. Can the skill generate a paste-ready prompt, or should it emit guardrails and review guidance only?
```

## OutSystems UI ODC Forge Documentation Bridge

The official OutSystems UI (ODC) Forge component page is current official evidence that the ODC component is supported for ODC and routes its documentation to the O11 "Using Mobile and Reactive Patterns" page.

Use this bridge as follows:

- Treat the Forge-to-O11 link as official routing evidence for OutSystems UI pattern documentation in ODC.
- Use catalog-backed OutSystems UI pattern facts when the exact pattern is present in `odc-ui-pattern-catalog.json`.
- Do not treat the bridge as proof that Mobile UI and OutSystems UI are the same framework.
- Do not treat it as proof that every O11 standard widget or platform behavior is current ODC authority.
- Do not promote mirror-only TypeScript or SCSS facts from `OutSystems/outsystems-ui` to `Current official` or `Catalog-backed official`.

## Decision Matrix

| Target | Framework | Skill behavior | Evidence label |
| --- | --- | --- | --- |
| Web app | OutSystems UI | Use the existing producer-first Mentor Studio UI prompt flow in `odc-ui-generation.md`. | `Current official` or `Catalog-backed official` |
| Mobile app | OutSystems UI | Use catalog-backed OutSystems UI facts only when the catalog entry applies to mobile apps. State that this is cross-platform OutSystems UI, not Mobile UI. Emit catalog-backed guidance/review unless mobile Mentor Studio generation is verified. | `Catalog-backed official` |
| Mobile app | Mobile UI | Do not emit confident paste-ready Mentor Studio generation. Emit framework guidance, rewrite guardrails, library placement notes, and review guidance. | `Current official` for framework facts; `Unverified gap` for paste-ready generation |
| Library | OutSystems UI or shared UI | Explain producer-library placement and versioned consumption before consumer prompts. | `Current official` |
| Mobile Library | Mobile UI or mobile-specific UI/native behavior | Explain mobile-library placement and consumption restrictions before consumer prompts. | `Current official` |
| Unknown | Unknown | Ask one clarifying question before generating UI guidance. | `Unverified gap` until clarified |

### Unknown framework branch

When the target/framework is unknown, return only framework guidance and do not generate a paste-ready Mentor Studio prompt in the same turn.

- Ask the clarifying question above.
- Use:
  - `### Placement`
  - `### Studio-Native Guidance`
  - `### Evidence Status`
- Keep evidence at: `Unverified gap for paste-ready Mentor Studio generation until framework and target type are clarified.`

### Known target, unknown framework branch

When the target is already clear (for example `Library` or `Mobile Library`) but the framework is ambiguous, do not assume framework-specific behavior.

- Ask the same clarifying question above.
- Return only:
  - `### Placement`
  - `### Studio-Native Guidance`
  - `### Evidence Status`
- Do not emit a paste-ready Mentor Studio prompt in this branch.
- Keep evidence at: `Unverified gap for paste-ready Mentor Studio generation until framework and target type are clarified.`

### Known framework, unknown target branch

When the framework is clearly stated (for example `OutSystems UI` or `Mobile UI`) but the target is still unknown, stop with the same non-ready clarification envelope.

- Ask the same clarifying question above.
- Return only:
  - `### Placement`
  - `### Studio-Native Guidance`
  - `### Evidence Status`
- Do not emit a paste-ready Mentor Studio prompt in this branch.
- Keep evidence at: `Unverified gap for paste-ready Mentor Studio generation until framework and target type are clarified.`

## Web App + OutSystems UI

Use the existing UI generation flow:

1. Open `odc-ui-generation.md`.
2. Use `odc-ui-prompt-recipes.md` for common screen goals.
3. Use `odc-ui-pattern-catalog.json` for exact OutSystems UI pattern names, properties, events, placeholders, client actions, compatibility notes, and security notes. A pattern's `client_actions` are the named actions the official docs give for driving it from an action flow (for example `SidebarOpen` / `SidebarClose`); an empty list means the docs name none, not that none exist.
4. For keyboard focus, skip links, ARIA roles and text spacing, use the catalog's top-level `accessibility_client_actions` block. These six actions live in ODC Studio under **Logic > OutSystemsUI > Accessibility** and are NOT per-pattern — they are called from any screen or block action flow, so they do not appear in any pattern's `client_actions`. Reach for them when a screen needs the accessibility behaviour that criteria C4/C5/C6 of `outsystems-runtime-ui-audit` score: `SetFocus` and `MasterDetailSetContentFocus` for focus placement, `SkipToContent` for the skip link, `SetAccessibilityRole` and `SetAriaHidden` for ARIA state, `ToggleTextSpacing` for readability.
5. Preserve producer-first order.

Do not change the existing Mentor Studio prompt output shape for this case.

## Mobile App + OutSystems UI

OutSystems UI remains a cross-platform framework. Some catalog entries apply to `mobile apps`.

Rules:

- Use an OutSystems UI pattern only when the catalog entry applies to mobile apps.
- State that the guidance or verified prompt is for the cross-platform OutSystems UI framework.
- Do not imply the app uses the newer Mobile UI framework.
- Copy compatibility notes from the catalog into review notes.
- Emit catalog-backed guidance/review unless mobile Mentor Studio generation is verified.
- When a pattern is catalog-backed but has no curated recipe, label the output `Catalog-backed official`.

## Mobile App + Mobile UI

Mobile UI is a mobile-only framework with its own visual language and widget model.

Rules:

- Do not emit confident paste-ready Mentor Studio generation for Mobile UI widgets yet.
- Emit current-official framework guidance and review notes instead.
- Label paste-ready Mobile UI generation requests as `Unverified gap` until a dedicated Mobile UI widget catalog and recipe layer exists.
- Explain that Mobile UI and OutSystems UI are separate complete frameworks.
- Warn that switching from OutSystems UI to Mobile UI requires rebuilding screens, layouts, and UI components.
- State that backend logic and data handling may still be reusable when the user is planning a rewrite.

Use this response shape for Mobile UI guardrail answers:

```text
### Placement
[Mobile app or Mobile Library placement]

### Studio-Native Guidance
[framework decision, reusable producers, review guidance, and rewrite warning when relevant]

### Evidence Status
Current official for framework facts; Unverified gap for paste-ready Mentor Studio generation.

### Optional Constraints
[CSP, library versioning, native runtime, or review constraints when relevant]
```

## Rewrite Guardrail

When the user asks to migrate, convert, or move an OutSystems UI mobile screen to Mobile UI, say:

```text
Mobile UI is not a drop-in migration target for OutSystems UI screens. Treat this as a UI rewrite: reuse backend logic and data handling where possible, but rebuild screens, layouts, and UI components with Mobile UI widgets.
```

Do not describe this as a direct migration.

## Icon Library Nuance

Do not infer Mobile UI only because the user mentions Phosphor icons.

Current ODC guidance says OutSystems UI also supports Phosphor 2.0 for newer versions, while Font Awesome remains available for existing apps and legacy compatibility. Treat icon library as a weak signal and ask for the UI framework when the framework is not otherwise clear.

## Library Placement

Use general-purpose Libraries for reusable logic, themes, UI blocks, design-system elements, and utilities that can be consumed by web or mobile apps.

Use Mobile Libraries for mobile-specific UI, native behavior, extensibility configurations, plugin wrappers, or mobile-only reusable components.

Producer-first implication:

```text
1. Create or confirm the producer Library or Mobile Library.
2. Confirm the public UI or logic elements exposed by that producer.
3. Tell the user to update the consumer dependency in ODC Studio when needed.
4. Generate consumer app guidance only after the producer and dependency are available.
```

Mentor Studio cannot add public dependencies by itself. Tell the user when a manual dependency update is required.

## CSP And Security Review Notes

For Mobile UI requests involving Icon, Card, Date Picker, Input OTP, Text Area, or similar Mobile UI widgets, include a version-sensitive CSP review note:

```text
Review CSP settings if the app uses Mobile UI versions earlier than 1.1.1 or has removed unsafe directives. Official docs identify visual or icon-loading impacts for some Mobile UI widgets in that scenario.
```

Do not present this as a universal requirement for all Mobile UI apps.

## Future Mobile UI Catalog Hook

A future `odc-mobile-ui-widget-catalog.json` should capture:

- widget name
- source URL
- target platform
- properties
- events
- slots or placeholders
- styling variables
- Shadow Parts
- native behavior notes
- CSP or compatibility notes
- Mentor prompt fragment
- evidence status

Do not invent this catalog during normal delivery work.

## Future Mobile UI Recipe Hook

A future `odc-mobile-ui-prompt-recipes.md` should be added only after the Mobile UI widget catalog exists and there is evidence that ODC Studio or Mentor Studio prompt generation can reliably apply those widgets.

Promote Mobile UI recipes only through explicit skill maintenance with validation and handoff review.

## Source Basis

Current official source basis:

- `OutSystems/docs-odc`: `src/eap/building-apps/mobile/mobile-ui/framework-comparison.md`
- `OutSystems/docs-odc`: `src/eap/building-apps/mobile/mobile-ui/mobile-ui-overview.md`
- `OutSystems/docs-odc`: `src/eap/building-apps/ui/icons/intro.md`
- `OutSystems/docs-odc`: `src/eap/building-apps/libraries/libraries.md`
- `OutSystems/docs-odc`: `src/eap/security/impacts-removing-unsafe-directives.md`
- generated `odc-ui-pattern-catalog.json` for OutSystems UI pattern facts
- OutSystems UI (ODC) Forge component documentation page, which links ODC component documentation to O11 "Using Mobile and Reactive Patterns"

Do not use Gemini output as authority. Treat it only as a user-provided prompt that surfaced the question.
