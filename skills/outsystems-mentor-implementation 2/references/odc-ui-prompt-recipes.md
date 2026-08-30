# ODC UI Prompt Recipes

Use these recipes after `odc-ui-framework-selection.md` confirms supported paste-ready generation and `odc-ui-prompt-inventory.md` selects the right UI building-block tier. Recipes provide proven prompt sequences for common Web app + OutSystems UI screen goals. Use `odc-ui-pattern-catalog.json` for exact pattern facts.

Each recipe keeps producers before consumers and keeps Mentor Studio prompts atomic.

## Shared Authoring Rules

Screen existence rule for new-screen flows:
1. If the target Screen already exists, state `Already exists: [ScreenName] Screen. Use existing.`
2. If the target Screen does not exist, first emit a shell prompt that creates only the named empty Screen and required input parameters.
3. After the shell Screen exists, emit screen-scoped producer prompts.
4. After screen-scoped producers exist, emit layout and event-wiring prompts.

UI naming rule:
- Use standard widget only for platform widgets such as Form, Button, Input, Table, List, Expression, Link, or Container.
- Use ODC UI pattern only when the exact pattern name and facts come from `odc-ui-pattern-catalog.json`.
- Use special dependency/component guidance from `odc-ui-prompt-inventory.md` before emitting prompts for Data Grid, public Library Web Blocks, shared UI assets, or dependency-sensitive components.
- For ODC UI patterns, copy exact catalog names, mandatory properties, important optional properties, placeholders, events, compatibility notes, and security notes into the final prompt or review notes where relevant.
- If a catalog-backed pattern is not covered by one of these curated recipes, label the output `Catalog-backed official` and do not imply a proven recipe exists.

Dependency inventory rule:
- Every paste-ready prompt block must list every referenced existing Entity, Static Entity, Structure, Screen, Web Block, Action, Aggregate, Data Action, manual dependency, and navigation target.
- If a referenced producer does not exist, emit a producer or shell prompt before the consuming prompt.

## List/Search Screen

Purpose: browse records with search and optional filters.

Producer order:
1. Entity and attributes exist.
2. Screen exists; if not, create only a named empty/shell Screen before screen-scoped producers.
3. Aggregate or Data Action returns the list.
4. Optional search/filter variables exist.
5. Screen binds to the producer.
6. Search/filter events refresh the producer.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Only create the named empty Screen shell.
Do not add data producers, visual layout, widgets, patterns, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Update the [EntityName] list experience in the existing web app.

Dependency inventory:
- Already exists: [EntityName] Entity. Use existing.
- Already exists: [ScreenName] Screen. Use existing.

Create or update the data producer first:
- On [ScreenName], create or update Aggregate [GetEntityNameList].
- Source Entity: [EntityName].
- Add search filtering using local variable SearchKeyword against [NameOrLabelAttribute].
- Sort by [DefaultSortAttribute] ascending.

Do not change the visual screen layout in this prompt. Only create or update the data producer and local variables needed by the screen.
```

Follow-up Mentor Studio Prompt:

```text
Update [ScreenName] after [GetEntityNameList] exists.

Dependency inventory:
- Already exists: [EntityName] Entity. Use existing.
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [GetEntityNameList] Aggregate or Data Action. Use existing.

Use a standard Table or List widget for [EntityName] records, unless a specific ODC UI pattern is selected from `odc-ui-pattern-catalog.json`.
If using an ODC UI pattern such as Search, use the exact catalog name and documented facts.
Bind the list source to [GetEntityNameList.List].
Add search input bound to local variable SearchKeyword.
When SearchKeyword changes, refresh [GetEntityNameList].
For each record, show [PrimaryAttribute], [SecondaryAttribute], and [StatusOrDateAttribute].
Add an empty state message when [GetEntityNameList.List] is empty.
```

Review:
- Confirm [GetEntityNameList] exists before the screen references it.
- Confirm search refreshes the aggregate.
- Confirm no new duplicate Entity was created.

Evidence Status:
- `Current official`: Uses current ODC screen, aggregate, binding, and widget concepts; exact ODC UI pattern facts must be copied from the catalog when a pattern is used.

## Detail Screen

Purpose: show one record and related actions.

Producer order:
1. Entity exists.
2. Screen exists; if not, create only a named empty/shell Screen with the identifier input parameter before screen-scoped producers.
3. Screen input parameter exists.
4. Aggregate or Data Action fetches the selected record.
5. Optional actions exist.
6. Screen binds expressions and actions.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Dependency inventory:
- Already exists: [EntityName] Entity. Use existing.

Add input parameter [EntityName]Id of type [EntityName] Identifier.
Only create the named empty Screen shell and the input parameter.
Do not add data producers, visual layout, widgets, patterns, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create the producers for [EntityName] detail display.

Dependency inventory:
- Already exists: [ScreenName] Screen with input parameter [EntityName]Id. Use existing.
- Already exists: [EntityName] Entity. Use existing.

On Screen [ScreenName], add input parameter [EntityName]Id of type [EntityName] Identifier if it does not already exist.
Create Aggregate [GetEntityNameById].
Source Entity: [EntityName].
Filter: [EntityName].Id = [EntityName]Id.

Do not create visual widgets in this prompt. Only create the input parameter and data producer.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after [GetEntityNameById] exists.

Dependency inventory:
- Already exists: [ScreenName] Screen with input parameter [EntityName]Id. Use existing.
- Already exists: [EntityName] Entity. Use existing.
- Already exists: [GetEntityNameById] Aggregate or Data Action. Use existing.
- Already exists: any action buttons to place on the detail screen. Use existing actions only.

Use standard widgets such as Container, Expression, and Button for details and actions, unless a specific ODC UI pattern is selected from `odc-ui-pattern-catalog.json`.
If using an ODC UI pattern such as Card or Section, use the exact catalog name and documented facts.
Bind fields from [GetEntityNameById.List.Current] or the single returned record.
Show [PrimaryAttribute], [SecondaryAttribute], and [DateOrStatusAttribute].
Add action buttons only for actions that already exist.
```

Review:
- Confirm the screen input parameter type is the Entity Identifier.
- Confirm the detail UI binds to the detail aggregate, not a list aggregate.

Evidence Status:
- `Current official`: Uses current ODC screen input, aggregate filtering, and binding concepts; exact ODC UI pattern facts must be copied from the catalog when a pattern is used.

## Create/Edit Form

Purpose: create or update one record.

Producer order:
1. Entity exists.
2. Screen exists; if not, create only a named empty/shell Screen with optional [EntityName]Id input before screen-scoped producers.
3. Save Server Action exists.
4. Local form record exists.
5. Optional edit-load aggregate exists when editing an existing record.
6. Create-vs-edit initialization assigns a blank record for create mode or the loaded record for edit mode.
7. Form UI consumes the local form record.
8. Button event calls validation and save actions.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Dependency inventory:
- Already exists: [EntityName] Entity. Use existing.

If this screen supports edit mode, add optional input parameter [EntityName]Id of type [EntityName] Identifier.
Only create the named empty Screen shell and the optional input parameter.
Do not add data producers, visual layout, widgets, patterns, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create or update the save producer for [EntityName].

Dependency inventory:
- Already exists: [EntityName] Entity. Use existing.

Create Server Action [SaveEntityName].
Input Parameter: EntityNameRecord of type [EntityName].
Inside the action, validate mandatory fields [FieldList].
Create or update the [EntityName] record using the standard Entity action.
Return Output Parameter SavedEntityNameId of type [EntityName] Identifier.

Do not update the screen in this prompt.
```

Form-state Mentor Studio Prompt:

```text
Prepare Screen [ScreenName] form state after [SaveEntityName] exists.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [EntityName] Entity. Use existing.
- Already exists: [SaveEntityName] Server Action. Use existing.

Create local variable Form[EntityName] of type [EntityName].
If [EntityName]Id is provided for edit mode, create Aggregate [GetEntityNameForEdit] filtered by [EntityName].Id = [EntityName]Id.
Initialize Form[EntityName] with a blank [EntityName] record when creating a new record.
Initialize Form[EntityName] from [GetEntityNameForEdit] when editing an existing record.

Do not create form widgets or button event handlers in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after [SaveEntityName], Form[EntityName], and optional [GetEntityNameForEdit] exist.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [EntityName] Entity. Use existing.
- Already exists: [SaveEntityName] Server Action. Use existing.
- Already exists: Form[EntityName] local variable. Use existing.
- Already exists when editing: [GetEntityNameForEdit] Aggregate. Use existing.

Use the standard Form widget for [EntityName].
If using an ODC UI pattern around the form, use the exact catalog name and documented facts from `odc-ui-pattern-catalog.json`.
Bind form fields to Form[EntityName].
Add inputs for [FieldList].
Add client-side mandatory validation for [MandatoryFieldList].
Add Save and Cancel buttons.
On Save click, call [SaveEntityName] with Form[EntityName], then show a success feedback message and navigate or refresh as appropriate.
```

Review:
- Confirm Save button calls the existing [SaveEntityName] action.
- Confirm Form[EntityName] exists before the UI binds to it.
- Confirm edit mode loads [GetEntityNameForEdit] before assigning the local form record.
- Confirm create mode initializes a blank local form record.
- Confirm validation messages are visible.
- Confirm no save logic was duplicated in the screen.

Evidence Status:
- `Current official`: Uses current ODC Server Action, Entity action, screen variable, aggregate, and standard Form widget concepts; exact ODC UI pattern facts must be copied from the catalog when a pattern is used.

## Dashboard With Counters And Charts

Purpose: summarize records with counters, charts, and small lists.

Producer order:
1. Screen exists; if not, create only a named empty/shell Screen before screen-scoped producers.
2. Aggregate or Server Action producers calculate metrics.
3. Screen binds counters/charts.
4. Optional filters refresh producers.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [DashboardScreenName].

Only create the named empty Screen shell.
Do not add data producers, visual layout, widgets, patterns, charts, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create dashboard data producers for Screen [DashboardScreenName].

Dependency inventory:
- Already exists: [DashboardScreenName] Screen. Use existing.
- Already exists: [EntityName] Entity or read model. Use existing.

Create Aggregate or Data Action [GetDashboardMetrics] for [EntityName].
Return values needed for:
- total count
- count by status
- recent records limited to 5
- chart grouping by [DateOrStatusField]

Do not create visual widgets in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [DashboardScreenName] after [GetDashboardMetrics] exists.

Dependency inventory:
- Already exists: [DashboardScreenName] Screen. Use existing.
- Already exists: [GetDashboardMetrics] Aggregate, Data Action, or Server Action. Use existing.

Use standard widgets or exact ODC UI pattern names from `odc-ui-pattern-catalog.json` for headline metrics and layout only.
For charts, do not use `odc-ui-pattern-catalog.json`; use current chart/reference documentation from the language-elements or chart reference source and only select chart widgets when the data producer returns grouped values suitable for that chart.
Use standard containers or exact catalog-backed layout pattern names to group dashboard areas.
Bind all visual values to [GetDashboardMetrics].
Add reviewable labels that describe the metric, not generic labels.
```

Review:
- Confirm chart data shape matches the selected chart.
- Confirm chart widget names and parameters come from the chart/reference documentation, not from the generated UI pattern catalog.
- Confirm dashboard lists remain summary lists, not full browsing screens.
- Confirm any ODC UI pattern names for layout/headline metrics match the catalog before finalizing the prompt.

Evidence Status:
- `Current official`: Uses current ODC data producer and binding concepts.
  Chart facts must come from chart/reference documentation.
  Exact ODC UI pattern facts for layout or headline metrics must be copied from the generated official catalog when a pattern is used.

## Master-Detail Screen

Purpose: select from a list and show details beside it.

Producer order:
1. Screen exists; if not, create only a named empty/shell Screen before screen-scoped producers.
2. List aggregate exists.
3. SelectedId local variable exists.
4. Detail aggregate filtered by SelectedId exists.
5. Screen uses exact catalog-backed Master Detail pattern facts.
6. Selection event assigns SelectedId and refreshes detail aggregate.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Only create the named empty Screen shell.
Do not add data producers, visual layout, widgets, patterns, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create producers for [ScreenName] Master Detail.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [EntityName] Entity. Use existing.

On Screen [ScreenName], create local variable Selected[EntityName]Id of type [EntityName] Identifier.
Create Aggregate [GetEntityNameList] from Entity [EntityName].
Create Aggregate [GetSelectedEntityName] from Entity [EntityName].
Filter [GetSelectedEntityName]: [EntityName].Id = Selected[EntityName]Id.

Do not create visual widgets in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after [GetEntityNameList], Selected[EntityName]Id, and [GetSelectedEntityName] exist.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [EntityName] Entity. Use existing.
- Already exists: [GetEntityNameList] Aggregate or Data Action. Use existing.
- Already exists: Selected[EntityName]Id local variable. Use existing.
- Already exists: [GetSelectedEntityName] Aggregate or Data Action. Use existing.

Use the exact Master Detail pattern name and facts from `odc-ui-pattern-catalog.json`.
Bind the left list to [GetEntityNameList.List].
When a list item is clicked, assign Selected[EntityName]Id to the clicked record Id and refresh [GetSelectedEntityName].
Bind the right detail area to [GetSelectedEntityName].
Do not place Master Detail inside Tabs or swipe-based patterns.
```

Review:
- Confirm Master Detail has list content and detail content.
- Confirm selection refreshes the detail aggregate.
- Confirm the Master Detail pattern name, placeholders, properties, and compatibility notes match the catalog.

Evidence Status:
- `Current official`: Uses current ODC aggregate, local variable, and event wiring concepts; Master Detail pattern facts must be copied from the generated official catalog.

## Tabbed Related-Data Screen

Purpose: organize related record sections.

Producer order:
1. Screen exists; if not, create only a named empty/shell Screen with the parent identifier input parameter before screen-scoped producers.
2. Parent detail producer exists.
3. Related list producers exist.
4. Screen adds exact catalog-backed Tabs pattern facts.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Dependency inventory:
- Already exists: [ParentEntity] Entity. Use existing.

Add input parameter [ParentEntity]Id of type [ParentEntity] Identifier.
Only create the named empty Screen shell and the input parameter.
Do not add data producers, visual layout, widgets, patterns, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create related data producers for [ScreenName].

Dependency inventory:
- Already exists: [ScreenName] Screen with input parameter [ParentEntity]Id. Use existing.
- Already exists: [ParentEntity] Entity. Use existing.
- Already exists: [RelatedEntityOne] Entity. Use existing.
- Already exists: [RelatedEntityTwo] Entity. Use existing.

Confirm input parameter [ParentEntity]Id exists.
Create Aggregate [GetParentEntityById] filtered by [ParentEntity].Id = [ParentEntity]Id.
Create Aggregate [GetRelatedEntityOneList] filtered by [RelatedEntityOne].[ParentEntity]Id = [ParentEntity]Id.
Create Aggregate [GetRelatedEntityTwoList] filtered by [RelatedEntityTwo].[ParentEntity]Id = [ParentEntity]Id.

Do not update the visual layout in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after the parent and related list producers exist.

Dependency inventory:
- Already exists: [ScreenName] Screen with input parameter [ParentEntity]Id. Use existing.
- Already exists: [ParentEntity] Entity. Use existing.
- Already exists: [RelatedEntityOne] Entity. Use existing.
- Already exists: [RelatedEntityTwo] Entity. Use existing.
- Already exists: [GetParentEntityById] Aggregate or Data Action. Use existing.
- Already exists: [GetRelatedEntityOneList] Aggregate or Data Action. Use existing.
- Already exists: [GetRelatedEntityTwoList] Aggregate or Data Action. Use existing.

Use the exact Tabs pattern name and facts from `odc-ui-pattern-catalog.json`.
Create one tab for Overview, one for [RelatedEntityOne], and one for [RelatedEntityTwo].
Bind Overview to [GetParentEntityById].
Bind related tabs to their corresponding aggregates.
Keep tab labels short and specific.
```

Review:
- Confirm each tab binds to an existing producer.
- Confirm no tab requires data from a producer that was not created.
- Confirm the Tabs pattern name, properties, events, and compatibility notes match the catalog.

Evidence Status:
- `Current official`: Uses current ODC screen input, aggregate, and binding concepts; Tabs pattern facts must be copied from the generated official catalog.

## Wizard Or Multi-Step Form

Purpose: guide data entry through steps.

Producer order:
1. Screen exists; if not, create only a named empty/shell Screen before screen-scoped producers.
2. Local step state exists.
3. Draft record or local form structures exist.
4. Validation actions exist.
5. Final save action exists when the wizard will persist data.
6. Wizard UI consumes them.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Only create the named empty Screen shell.
Do not add data producers, visual layout, widgets, patterns, validation actions, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create producers for [ScreenName] Wizard.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.

Create local variable CurrentStep of type Integer with default 1.
Create local form variables for [StepOneData], [StepTwoData], and [StepThreeData].
Create Client Action [ValidateCurrentStep] that validates required fields for CurrentStep and returns IsValid.

Do not create the Wizard UI in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after CurrentStep and [ValidateCurrentStep] exist.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [ValidateCurrentStep] Client Action. Use existing.
- Already exists: [SaveEntityName] Server Action or save producer. Use existing.

If [SaveEntityName] does not exist, stop and create the save producer before wiring the final step.

Use the exact Wizard pattern name and facts from `odc-ui-pattern-catalog.json`.
Show one step content area per step.
Next button calls [ValidateCurrentStep]; if valid, increment CurrentStep.
Back button decrements CurrentStep.
Final Save button calls [SaveEntityName].
```

Review:
- Confirm step navigation does not bypass validation.
- Confirm final save uses an existing save action.
- Confirm the Wizard pattern name, placeholders, properties, events, and compatibility notes match the catalog.

Evidence Status:
- `Current official`: Uses current ODC local variable and Client Action concepts; Wizard pattern facts must be copied from the generated official catalog.

## Editable Data Grid Screen

Purpose: edit tabular data efficiently.

Producer order:
1. Screen exists; if not, create only a named empty/shell Screen before screen-scoped producers.
2. Data Grid dependency exists.
3. Data Action fetches rows and returns JSON prepared through `ArrangeData.DataJSON`.
4. Save/update producer accepts Data Grid `ChangedLines` or exposed changed-line JSON text fields.
5. Grid screen consumes the JSON data producer and save producer.
6. Grid client actions are wired with `GetChangedLines` before save and `MarkChangesAsSaved` after successful save, using the Grid widget Id as `GridWidgetId`.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Only create the named empty Screen shell.
Do not add data producers, visual layout, Grid widgets, client actions, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create producers for editable Data Grid on [ScreenName].

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Manual setup required: confirm the OutSystems Data Grid dependency is already added through Manage Dependencies.
- Already exists: [EntityName] Entity. Use existing.

Create or update Data Action [GetGridEntityData] for Entity [EntityName].
Inside [GetGridEntityData], fetch [EntityName] rows sorted by [DefaultSortAttribute].
Call ArrangeData with ToObject of the fetched [EntityName] list.
Return the JSON output from ArrangeData.DataJSON for the Grid.Data property.

Create or update Server Action [SaveGridEntityChanges].
Input Parameter: ChangedLines using the Data Grid ChangedLines structure, or the ChangedLines JSON text fields if Studio exposes those fields separately.
Parse and map ChangedLines.EditedLines before updating [EntityName] records.
Do not assume GetChangedLines returns an Entity List directly; ChangedLines.EditedLines, AddedLines, RemovedLines, and InvalidLines are JSON serialized Text fields.

Do not create the Grid widget in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after [GetGridEntityData] and [SaveGridEntityChanges] exist.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [GetGridEntityData] Data Action returning JSON from ArrangeData.DataJSON. Use existing.
- Already exists: [SaveGridEntityChanges] Server Action. Use existing.
- Manual setup required: confirm the OutSystems Data Grid dependency is already added through Manage Dependencies.

Use OutSystems Data Grid for ODC only after confirming the dependency.
Data Grid reference: odc-data-grid-reference.json.
Use the Grid widget Id as the mandatory GridWidgetId input for Data Grid client actions.
Bind Grid.Data to the JSON output from [GetGridEntityData], sourced from ArrangeData.DataJSON.
Bind Grid.IsDataFetched to the [GetGridEntityData] Data Action fetched state.
Configure columns with binding names from [ColumnList].
Allow editing only [EditableColumnList].
Add a Save button.
On Save click, call GetChangedLines with GridWidgetId, call [SaveGridEntityChanges] with changed lines, then call MarkChangesAsSaved with the same GridWidgetId after the save succeeds, and show a feedback message.
```

Review:
- Confirm Data Grid dependency exists before using Grid widgets.
- Confirm Grid.Data receives Text JSON prepared by ArrangeData.DataJSON, not an Entity List.
- Confirm Grid.IsDataFetched is bound to the Data Action fetched state.
- Confirm SaveGridEntityChanges parses ChangedLines.EditedLines JSON instead of treating GetChangedLines as returning an Entity List.
- Confirm GetChangedLines and MarkChangesAsSaved are available from the Data Grid dependency before wiring Save.
- Confirm both Data Grid client actions receive the same GridWidgetId for this Grid block.

Evidence Status:
- `Current official for documented Data Grid facts`: Uses current ODC producer and Data Grid reference concepts from `odc-data-grid-reference.json`; dependency setup remains a manual preflight gap when the reference reports `Dependency requirement not found in source`; live Mentor Studio execution remains a separate validation step.

## Card Or Gallery Browsing Screen

Purpose: browse visual or summary records.

Producer order:
1. Screen exists; if not, create only a named empty/shell Screen before screen-scoped producers.
2. List producer exists.
3. Card or Gallery UI consumes the list.
4. Click or navigation events are wired.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Only create the named empty Screen shell.
Do not add data producers, visual layout, widgets, patterns, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create or verify [GetEntityNameList] for [ScreenName].

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [EntityName] Entity. Use existing.

Source Entity: [EntityName].
Return attributes needed for each card: [PrimaryAttribute], [SecondaryAttribute], [ImageOrIconAttribute], [StatusAttribute].
Do not create visual widgets in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after [GetEntityNameList] exists.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [EntityName] Entity. Use existing.
- Already exists: [GetEntityNameList] Aggregate or Data Action. Use existing.
- Already exists: [DetailScreenName] Screen. Use existing, or create only that named empty/shell detail Screen before wiring navigation.

Use standard containers for cards, or use exact Card/Gallery ODC UI pattern names and facts from `odc-ui-pattern-catalog.json`.
Bind the repeating source to [GetEntityNameList.List].
Inside each item, show [PrimaryAttribute], [SecondaryAttribute], [ImageOrIconAttribute], and [StatusAttribute].
On item click, navigate to [DetailScreenName] with the selected record Id.
```

Review:
- Confirm the card source is an existing list producer.
- Confirm navigation passes the selected record Id.
- Confirm any Card or Gallery pattern names, placeholders, properties, and compatibility notes match the catalog.

Evidence Status:
- `Current official`: Uses current ODC aggregate, binding, and navigation concepts; exact Card or Gallery pattern facts must be copied from the generated official catalog when a pattern is used.

## Modal Or Popup Interaction

Purpose: show focused secondary interaction without navigating away.

Producer order:
1. Screen exists; if not, create only a named empty/shell Screen before screen-scoped producers.
2. Open/close state exists.
3. Save or confirm action exists.
4. UI consumes state and action.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Only create the named empty Screen shell.
Do not add data producers, visual layout, widgets, modal patterns, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create producers for [ScreenName] modal interaction.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists when confirming an operation: [ConfirmActionName] Client Action or Server Action. Use existing.

Create local variable Is[ModalName]Open of type Boolean with default False.
Create Client Action [OpenModalName] that assigns Is[ModalName]Open = True.
Create Client Action [CloseModalName] that assigns Is[ModalName]Open = False.
Confirm action [ConfirmActionName] exists before wiring confirmation.

Do not create visual widgets in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after modal state actions exist.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: Is[ModalName]Open local variable. Use existing.
- Already exists: [OpenModalName] Client Action. Use existing.
- Already exists: [CloseModalName] Client Action. Use existing.
- Already exists when confirming an operation: [ConfirmActionName] Client Action or Server Action. Use existing.

Use standard containers and visibility state, or use the exact modal/popup ODC UI pattern name and facts from `odc-ui-pattern-catalog.json`.
Bind visibility to Is[ModalName]Open.
Open button calls [OpenModalName].
Cancel button calls [CloseModalName].
Confirm button calls existing [ConfirmActionName], then [CloseModalName], then refreshes affected data.
```

Review:
- Confirm confirm logic uses an existing producer action.
- Confirm cancel closes without saving.
- Confirm any modal or popup pattern names, placeholders, properties, events, and compatibility notes match the catalog.

Evidence Status:
- `Current official`: Uses current ODC local variable and Client Action concepts; exact modal or popup pattern facts must be copied from the generated official catalog when a pattern is used.

## Reusable Web Block

Purpose: encapsulate reusable UI with explicit inputs and events.

Producer order:
1. Data and action dependencies exist.
2. Block exists; if not, create only a named empty/shell Web Block with explicit inputs before block-scoped producers.
3. Block inputs are defined.
4. Block UI consumes inputs.
5. Consuming Screen exists; if not, create only a named empty/shell Screen before placing the block.
6. Screen consumes block.

Shell Mentor Studio Prompt when Web Block does not exist:

```text
Create Web Block [BlockName].

Dependency inventory:
- Already exists when custom: [InputType] Entity, Structure, or Static Entity. Use existing.

Add input parameters:
- [InputName] of type [InputType]

Only create the named empty Web Block shell and input parameters.
Do not add data producers, visual layout, widgets, patterns, events, or consuming Screen changes in this prompt.
```

Mentor Studio Prompt:

```text
Update Web Block [BlockName] after its shell and inputs exist.

Dependency inventory:
- Already exists: [BlockName] Web Block with input parameter [InputName]. Use existing.
- Already exists when used: any block-local data producer. Use existing or create it before this prompt.

Inside the block, use standard widgets or the exact [PatternName] ODC UI pattern facts from `odc-ui-pattern-catalog.json`.
Bind displayed values to input parameters or block-local data producers.
Expose events only when the parent screen must react.
Do not update consuming screens in this prompt.
```

Shell Mentor Studio Prompt when consuming Screen does not exist:

```text
Create Screen [ScreenName].

Only create the named empty Screen shell.
Do not place [BlockName] or add data producers, visual layout, widgets, patterns, or event handlers in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update Screen [ScreenName] after Web Block [BlockName] exists.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [BlockName] Web Block. Use existing.
- Already exists: [ExistingValue] value source. Use existing.
- Already exists: any client actions that handle block events. Use existing.

Place [BlockName] in the intended screen section.
Bind [BlockName].[InputName] to [ExistingValue].
Wire block events to existing client actions only.
```

Review:
- Confirm the block exists before the screen consumes it.
- Confirm the consuming screen exists before the block is placed.
- Confirm the screen does not duplicate block internals.
- Confirm any ODC UI pattern names, placeholders, properties, events, and compatibility notes match the catalog.

Evidence Status:
- `Current official`: Uses current ODC Web Block input, event, and screen composition concepts; exact ODC UI pattern facts must be copied from the generated official catalog when a pattern is used.

## Form Validation And Save Feedback

Purpose: keep validation and feedback explicit.

Producer order:
1. Screen exists; if not, create only a named empty/shell Screen before screen-scoped producers.
2. Validation action exists.
3. Save action exists.
4. Screen event calls validation before save.

Shell Mentor Studio Prompt when Screen does not exist:

```text
Create Screen [ScreenName].

Only create the named empty Screen shell.
Do not add data producers, visual layout, widgets, validation actions, save actions, or event handlers in this prompt.
```

Mentor Studio Prompt:

```text
Create Client Action [ValidateEntityNameForm].

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [EntityName] Entity or form data source. Use existing.

Validate fields [MandatoryFieldList].
Set field validation messages for invalid values.
Return Output Parameter IsValid of type Boolean.

Do not call the save action in this prompt.
```

Follow-up Mentor Studio Prompt:

```text
Update [ScreenName] Save button after [ValidateEntityNameForm] and [SaveEntityName] exist.

Dependency inventory:
- Already exists: [ScreenName] Screen. Use existing.
- Already exists: [ValidateEntityNameForm] Client Action. Use existing.
- Already exists: [SaveEntityName] Server Action. Use existing.

If [SaveEntityName] does not exist, stop and create the save producer before wiring this button.

Use a standard Button widget for Save unless a specific ODC UI pattern is selected from `odc-ui-pattern-catalog.json`.
On Save click:
1. Run Client Action [ValidateEntityNameForm].
2. If IsValid is False, stop and show validation messages.
3. If IsValid is True, run Server Action [SaveEntityName].
4. Show success feedback message.
5. Refresh data or navigate according to the screen purpose.
```

Review:
- Confirm validation runs before save.
- Confirm user feedback appears after success or validation failure.
- Confirm any ODC UI pattern names and facts match the catalog when a pattern is used.

Evidence Status:
- `Current official`: Uses current ODC Client Action, validation, Server Action call, feedback, and navigation concepts; exact ODC UI pattern facts must be copied from the catalog when a pattern is used.

## Validation Scenarios

Use these scenarios to validate the skill behavior after implementation:

1. `Create a searchable customer list screen using cards.`
   - Expected: producers for customer list/search exist before the screen prompt consumes them.
2. `Create a master-detail account screen.`
   - Expected: list aggregate, selected identifier variable, and detail aggregate appear before the Master Detail screen prompt.
3. `Describe how to use Floating Actions on the ticket list screen.`
   - Expected: if no curated recipe exists, output is labeled `Catalog-backed official` and includes catalog-derived properties and review notes.
4. `Create a screen with Dropdown Search for assigning an owner.`
   - Expected: options list producer and selected value bindings appear before the event wiring prompt.
