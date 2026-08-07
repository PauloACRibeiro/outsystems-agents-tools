# ODC UI Acceptance Coverage Map

This map tracks realistic, user-ready acceptance fixtures for `outsystems-mentor-implementation` UI prompt hardening, plus explicitly gated review-only artifacts that must not be treated as paste-ready web prompts.

It complements `odc-ui-pattern-coverage-queue.md`, which remains the catalog-wide authority for the 69-pattern matrix. This file does not upgrade catalog or live evidence into current ODC product-contract authority. It only helps decide whether the next fixture should add a new realistic domain, compose already-live-backed corrections in a different workflow, or pause until a concrete signature uncertainty justifies a fresh live Mentor probe.

Do not run a live Mentor probe from this map alone. Use a live in-memory Mentor session only when a named property, placeholder, event, or value type is still uncertain after checking the catalog, the approved review matrix, and existing live-backed fixtures.

## Live Signature Composition Coverage

| Pattern or cluster | Realistic domains | Coverage state | Notes |
| --- | --- | --- | --- |
| Search | campaign preview; support triage; field service dispatch; incident response | Cross-domain realistic | Search internal `Input.Variable` binding is covered across marketing, support, field-service, and incident-response workflows. |
| Sidebar | campaign preview; support triage; field service dispatch; incident response | Cross-domain realistic | Sidebar typed direction, width, overlay, and live `OnToggle` handling are covered across four domains. |
| Animate | campaign preview; field service dispatch | Cross-domain realistic | Typed animation, speed, and Integer delay guidance is covered outside a single workflow. |
| Scrollable Area | campaign preview; support triage; field service dispatch; incident response | Cross-domain realistic | `ScrollbarStyle`, fixed sizing, and eventless review guidance are covered across four domains. |
| Video | campaign preview; support triage; field service dispatch; incident response | Cross-domain realistic | Live `URL` input plus `OptionalConfigs` ownership is covered across four domains. |
| Bottom Sheet | field service dispatch | Gated follow-up | Bottom Sheet has one realistic workflow, but current ODC docs say the pattern applies to Mobile Apps only; do not add another web fixture without a specific live Mentor applicability check. |
| Accordion | support resolution; support triage; policy library | Cross-domain realistic | Parent/item ownership is covered in support and policy-library workflows. |
| List Item Content | support resolution; support triage; policy library | Cross-domain realistic | Placeholder ownership is covered in support and policy-library workflows. |
| Tooltip | support resolution; support triage; policy library | Cross-domain realistic | Typed Position/Trigger and live `OnToggle` are covered in support and policy-library workflows. |
| Blank Slate | support resolution; policy library | Cross-domain realistic | Empty-state placeholder ownership is covered in support and policy-library workflows. |
| Action Sheet | inventory exception review; procurement approval | Cross-domain realistic | Action Sheet `IsOpen`, `OnClose`, and child-control command placement are covered in inventory and procurement workflows. |
| Floating Actions | warehouse quick actions; service visit quick actions | Cross-domain realistic | Floating Actions `IsExpanded`, `OnToggle`, and child-item command placement are covered in warehouse and service-visit workflows. |
| Floating Actions Item | warehouse quick actions; service visit quick actions | Cross-domain realistic | ExtendedClass-only child-item constraint is covered; command behavior uses `Button.OnClick` on Button widgets inside the Item placeholder. No live probe from this map alone. |
| Navigation/status plus interaction/media composition | incident response command center | One realistic domain | Navigation/status patterns are now composed with Search, Sidebar, Scrollable Area, and Video live-signature corrections in one workflow. |

## Current Realistic Fixtures

| Fixture | Domain | Main composition value | Evidence boundary |
| --- | --- | --- | --- |
| `web_acceptance_service_workspace_content_layout.md` | service manager workspace | Content/layout/status patterns in a practical dashboard workflow. | Catalog-backed official; no live signature upgrade. |
| `web_acceptance_service_visit_floating_actions.md` | service visit quick actions | Floating Actions expansion state and child-item command placement in a field-service workflow. | Catalog-backed official plus live ODC Mentor signature corrections. |
| `web_acceptance_campaign_controls_inputs_media.md` | campaign controls | Input, range, tag, owner, and image-preview value flow with TrueChange-safe option-list guidance. | Catalog-backed official; no live signature upgrade. |
| `web_acceptance_campaign_preview_interaction_media.md` | campaign preview | Search, Sidebar, Animate, Scrollable Area, and Video live-signature corrections in one marketing workflow. | Catalog-backed official plus live ODC Mentor signature corrections. |
| `web_acceptance_field_dispatch_bottom_sheet_media.md` | field service dispatch board | Review-only gated artifact: Bottom Sheet composed with Search, Sidebar, Animate, Scrollable Area, and Video in a non-support workflow. | Unverified gap for paste-ready web-app Mentor Studio generation; live ODC Mentor signature corrections do not override current ODC Mobile Apps only applicability. |
| `web_acceptance_fulfillment_navigation_status.md` | fulfillment operations | Navigation, timeline, progress, and rating patterns in an operations workflow. | Catalog-backed official; no live signature upgrade. |
| `web_acceptance_incident_response_navigation_media.md` | incident response command center | Navigation/status patterns composed with live Search, Sidebar, Scrollable Area, and Video corrections. | Catalog-backed official plus live ODC Mentor signature corrections. |
| `web_acceptance_inventory_exception_action_sheet.md` | inventory exception review | Action Sheet state and dismissal boundaries with child-control command placement. | Catalog-backed official plus live ODC Mentor signature corrections. |
| `web_acceptance_policy_library_content_patterns.md` | policy library workspace | Non-support Accordion, Blank Slate, List Item Content, and Tooltip content-pattern corrections. | Catalog-backed official plus live ODC Mentor signature corrections. |
| `web_acceptance_procurement_approval_action_sheet.md` | procurement approval workspace | Action Sheet state and dismissal boundaries with approval child-control command placement. | Catalog-backed official plus live ODC Mentor signature corrections. |
| `web_acceptance_support_resolution_content_patterns.md` | support resolution workspace | Accordion, Blank Slate, List Item Content, and Tooltip live content-pattern corrections. | Catalog-backed official plus live ODC Mentor signature corrections. |
| `web_acceptance_support_triage_cross_cluster.md` | support triage cockpit | Cross-cluster composition of interaction/media and content corrections in one support workflow. | Catalog-backed official plus live ODC Mentor signature corrections. |
| `web_acceptance_warehouse_floating_actions.md` | warehouse quick actions | Floating Actions expansion state and child-item command placement in an operations workflow. | Catalog-backed official plus live ODC Mentor signature corrections. |

## Candidate Next Batches

| Candidate | Why it might be next | Stop rule |
| --- | --- | --- |
| Bottom Sheet applicability follow-up | Existing web fixture has live signature corrections, but current ODC docs say Bottom Sheet applies to Mobile Apps only. | Stop for a named live Mentor applicability check before adding another web Bottom Sheet fixture. |
| Floating Actions IsExpanded state sync | current docs describe IsExpanded as initial visibility only; existing fixtures bind it but do not prove internal toggle write-back. Re-verified 2026-07-07 against the current ODC Floating Actions pattern doc: `IsExpanded (Boolean): Optional` is documented as an input controlling expansion only; no write-back behavior is documented. | Stop for a named live Mentor check before claiming two-way state tracking or adding state-sync assertions. |
| Fresh live Mentor probe | Use only for a specific unresolved property, placeholder, event, or value-type question. | Do not probe just to add more fixtures; tenant work must stay evidence-driven and in-memory only. |
