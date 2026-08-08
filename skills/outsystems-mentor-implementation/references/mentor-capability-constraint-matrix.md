# Mentor Capability And Constraint Matrix

This matrix is the OMI source owner for Mentor Web and Mentor Studio capability,
constraint, route, and evidence-status claims. Use it before claiming what
Mentor can create, refine, or modify.

## Authority Rules

- Current OutSystems documentation authority controls product-contract claims.
- Product-contract facts must come from current OutSystems public docs,
  approved internal docs, current tool observations, or explicit
  user-supplied evidence.
- Generated references, dry-runs, fixtures, and screenshots are not
  product-contract authority by themselves.
- Do not promote generated, dry-run, fixture-only, or screenshot-only evidence
  into product-contract wording unless it is separately grounded by current
  official documentation, approved internal documentation, current tool
  observation, or explicit user-supplied evidence.
- Treat complex full-scope input as a requirement document or source plan first,
  then decompose it into focused requests.

Current official OutSystems sources used by this matrix:

- Effective prompts for Mentor:
  <https://success.outsystems.com/documentation/outsystems_developer_cloud/agentic_development/effective_prompts_for_mentor/>
- AI app generation in Mentor Web:
  <https://success.outsystems.com/documentation/outsystems_developer_cloud/agentic_development/ai_app_generation_in_mentor_web/>
- Capabilities and patterns for Mentor Web:
  <https://success.outsystems.com/documentation/outsystems_developer_cloud/agentic_development/ai_app_generation_in_mentor_web/capabilities_and_patterns_for_mentor_web/>
- AI development in Mentor Studio:
  <https://success.outsystems.com/documentation/outsystems_developer_cloud/agentic_development/ai_development_in_mentor_studio/>
- Capabilities and patterns for Mentor Studio:
  <https://success.outsystems.com/documentation/outsystems_developer_cloud/agentic_development/ai_development_in_mentor_studio/capabilities_and_patterns_for_mentor_studio/>
- Known limitations:
  <https://success.outsystems.com/documentation/outsystems_developer_cloud/agentic_development/known_limitations/>

## Mentor Web

Mentor Web is the OutSystems route for app generation and refinement of web
apps from prompts or requirement documents. It uses a blueprint review before
app generation, so review the blueprint as the interpretation checkpoint before
committing to generation.

Use Mentor Web when the source asks for:

- a new web app from a prompt or requirement document
- refinement of new and existing web apps in Mentor Web
- blueprint review, blueprint refinement, or first-generation app structure
- refinement in the web editor after generation

Do not use OMI to imply that Mentor Studio creates no-shell apps. OMI may
prepare shell-first or Studio-native handoff content only after a target shell
exists or after the user explicitly approves the exact shell-creation action.

## Mentor Studio

Mentor Studio is the OutSystems route for modifying existing apps through
conversation inside ODC Studio. Current documentation describes Mentor Studio
scope as web apps, libraries, and agentic apps. Mentor Studio modifies the
elements that the open asset supports; element coverage depends on the asset
type.

The exact element availability depends on the open asset type and current Known
limitations; verify both before confident OMI output. Non-web asset support is
current official scope, but it does not mean every web-app element is available
in libraries or agentic apps.

Build mobile apps manually in ODC Studio.

Current official capability families for Mentor Studio include:

| Family | Capability examples / verification targets |
| --- | --- |
| Logic | Server Actions, Client Actions, Service Actions, Aggregates, SQL nodes |
| UI | Screens, Web Blocks, Emails |
| Data | Entities, Attributes, Relationships |
| Other | Timers, Events |

Use Mentor Studio when the source asks for Studio-native implementation detail,
element placement, logic design, UI changes in an existing app shell or
supported non-mobile asset, or a paste-safe prompt that targets a verified web
app, library, or agentic app.

## Route Selection

| Source request | Primary route |
| --- | --- |
| New app from prompt or requirement documents | Mentor Web |
| Blueprint review or blueprint correction before generation | Mentor Web |
| Refinement inside the browser editor after generation | Mentor Web |
| Existing web app, library, or agentic app modification | Mentor Studio |
| Existing app logic, UI, data, timer, or event modification when the open asset supports the element type | Mentor Studio |
| Studio-native pseudocode or paste-safe prompt for an existing shell or verified non-mobile asset | OMI routed to Mentor Studio guidance |
| Mobile app generation or modification | Build mobile apps manually in ODC Studio |
| Complex full-scope input | Keep as requirement document or source plan, then decompose into focused requests |
| Unknown app state, target identity, or evidence freshness | Stop, label the gap, and ask for the missing evidence |

## Evidence Status

Use these labels for capability and constraint claims:

| Label | Meaning |
| --- | --- |
| Current official | Grounded in current OutSystems public documentation or an approved current official mirror. |
| Tenant-observed | Observed through a current read-only tenant/tool check; use as observation evidence, not universal product contract. |
| Unverified gap | Not confirmed by current official docs, approved internal docs, current tool observations, or explicit user-supplied evidence. |

When a claim depends only on generated references, dry-runs, fixtures, or
screenshots, use `Unverified gap` until stronger evidence is available.

## Known Limitations And Stop Conditions

Known limitations are current-contract constraints, not optional warnings.
Check the current Known limitations page before making capability claims about
Mentor Web or Mentor Studio.

Stop and ask before producing confident OMI output when:

- the request treats Mentor Studio as a no-shell new-app generator
- the target asset is not verified as an existing web app, library, agentic app,
  or approved app shell
- the request targets a mobile app as Mentor Studio work instead of manual ODC
  Studio development
- the requested element type is not confirmed as supported by the open asset
  type
- the request depends on the current screen, current selection, or hidden Studio
  state that Mentor Studio does not automatically expose
- external/public dependencies are needed but have not been confirmed as added
  to the app
- a broad prompt combines many unrelated changes that should be decomposed
- the only evidence is generated, dry-run, fixture-only, or screenshot-only

## Refresh Procedure

Refresh this matrix when any current OutSystems Mentor documentation changes or
when the user supplies newer explicit evidence.

1. Re-check the current OutSystems public or approved internal docs listed in
   `Authority Rules`.
2. Keep generated references, dry-runs, fixtures, and screenshots out of
   product-contract authority unless separately promoted by an approved source.
3. Update this matrix first, then keep `SKILL.md`, `README.md`,
   `source-map.md`, and `odc-pseudocode-source-manifest.md` as thin routes.
4. Run:

```bash
python3 -m unittest skills/outsystems-mentor-implementation/tests/test_deterministic_quality_master.py -v
git diff --check
```

On Windows PowerShell, use `python` instead of `python3` — `python3` is not a
command there.
