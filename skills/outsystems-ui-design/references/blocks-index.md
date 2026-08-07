---
name: osui-blocks-index
description: Single-page reference for every OutSystems UI block — SourceBlock names, key arguments, placeholders, events, reference enums (Entities.Color, Entities.Position, etc.). Use when picking a block by requirement, looking up exact argument/placeholder names during region mapping, or validating block usage in a pattern tree without loading full patterns/<category>.md files.
---

# OutSystems UI — All Blocks Index

> **Harvested from:** `outsystems-frontend-skills` (OutSystems official, BSD-3-Clause) `ui-frameworks/outsystems-ui/blocks-index.md` (harvested 2026-08-05).
> **Merge note:** local corrections preserved where noted in `maintenance/refresh-checklist.md` (Pagination placeholders row corrected against live-verified behavior).
> See `maintenance/refresh-checklist.md` for the refresh procedure.


> **Purpose:** Single-page reference of every block in OutSystems UI with its `SourceBlock` identifier, key arguments, placeholders, and category. Use when picking a block, when looking up the exact block name, or when validating an existing block usage.

## Parameter and placeholder naming

When using OutSystems UI blocks via the modelAPI (typed `IMobileBlockInstanceWidget`), every `Parameter` and `Placeholder` value uses **FULL PATH format** — `<SourceBlock>.<Name>`.

| Field | Example value |
|---|---|
| `Parameter` | `"Card.UsePadding"`, `"Counter.IsVertical"`, `"Columns2.GutterSize"` |
| `Placeholder` | `"Card.Content"`, `"Counter.Content"`, `"Tabs.Header"` |

Bare names like `"UsePadding"` or `"Content"` only work in the older serializer JSON (used inside the StyleGuide app source). When generating new model patches, always include the `SourceBlock.` prefix.

Every `IMobileBlockInstanceWidget` MUST include both `Arguments: []` and `PlaceholdersContent: []`, even when empty. Omitting either causes a `childCollection cannot be null` error.

## Reference entities (enums)

Used as values for many block arguments. Reference as `Entities.<Name>.<Value>`:

| Entity | Values |
|---|---|
| `Entities.Color` | `Primary`, `Secondary`, `Transparent`, `Neutral0`–`Neutral10`, `Red`, `Orange`, `Yellow`, `Lime`, `Green`, `Teal`, `Cyan`, `Blue`, `Indigo`, `Violet`, `Grape`, `Pink` |
| `Entities.Position` | `Center`, `Top`, `Bottom`, `Left`, `Right`, `TopLeft`, `TopRight`, `BottomLeft`, `BottomRight` |
| `Entities.Orientation` | `Horizontal`, `Vertical` |
| `Entities.Direction` | `Right`, `Left` |
| `Entities.Size` | `Small`, `Medium` |
| `Entities.Shape` | `Rounded`, `Sharp`, `SoftRounded` |
| `Entities.Space` | `None`, `ExtraSmall`, `Small`, `Base`, `Medium`, `Large`, `ExtraLarge`, `XXLarge` |
| `Entities.GutterSize` | `None`, `ExtraSmall`, `Small`, `Base`, `Medium`, `Large`, `ExtraLarge`, `XXLarge` (same values as `Space`, distinct enum — use `Entities.GutterSize.*` for column gaps). |
| `Entities.Trigger` | `Hover`, `Click` (used by `Tooltip.Trigger`). |
| `Entities.BreakColumns` | `None`, `All`, `First` (column collapse behavior per breakpoint). |
| `Entities.Alert` | `Success`, `Error`, `Info`, `Warning` |
| `Entities.Speed` | `Slow`, `Normal`, `Fast` |
| `Entities.AnimationType` | `TopToBottom`, `BottomToTop`, `LeftToRight`, `RightToLeft`, `FadeIn`, `Scale`, `ScaleDown`, `Bounce`, `Spinner` |
| `Entities.Gradient` | `LinearHorizontal`, `LinearVertical`, `LinearDiagonally`, `Radial` |
| `Entities.AccordionIconType` | `Caret`, `PlusMinus`, `Custom` |
| `Entities.CarouselNavigation` | `Arrows`, `Dots`, `Both`, `None` |
| `Entities.StackedOptions` | `Bottom`, `Top`, `None` |
| `Entities.Steps` | `Past`, `Active`, `Next` (Wizard step status) |
| `Entities.DatePickerTimeFormat` | `Time24hFormat`, `Time12hFormat`, `Disabled` |

## Content patterns (17)

| SourceBlock | Purpose | Key arguments | Placeholders |
|---|---|---|---|
| `Accordion` | Collapsible sections container | `MultipleItems`, `ExtendedClass` | `Content` (accepts `AccordionItem` children) |
| `AccordionItem` | Single section inside Accordion | `StartsExpanded`, `IsDisabled`, `Icon`, `IconPosition`, `ExtendedClass` | `Title`, `Content`, `CustomIcon` |
| `Alert` | Inline contextual feedback | `AlertType` (`Entities.Alert`), `ExtendedClass` | `MessageText` |
| `BlankSlate` | Empty state placeholder | `FullHeight`, `ExtendedClass` | `Icon`, `Content`, `Actions` |
| `Card` | Generic content container | `UsePadding`, `ExtendedClass` | `Content` |
| `CardBackground` | Card with background image overlay | `MinHeight`, `Color`, `ExtendedClass` | `BackgroundImage`, `Content` |
| `CardItem` | Card row with Left / Title / Content / Right | `ExtendedClass` | `Left`, `Title`, `Content`, `Right` |
| `CardSectioned` | Card with image + title + content + footer | `IsVertical`, `UsePadding`, `ImagePadding`, `ExtendedClass` | `Image`, `Title`, `Content`, `Footer` |
| `ChatMessage` | Chat message bubble | `MessageStatus`, `IsRight`, `ExtendedClass` | `MessageText`, `Actions` |
| `FlipContent` | Flippable front/back container | `StartsFlipped`, `FlipOnClick`, `ExtendedClass` | `Front`, `Back` |
| `FloatingContent` | Anchored floating overlay | `Position`, `UseFullWidth`, `UseMargin`, `ExtendedClass` | `Trigger`, `Content` |
| `ListItemContent` | Structured row for `IList` items | `ExtendedClass` | `Left`, `Title`, `Content`, `Right` |
| `Section` | Titled grouping container | `UsePadding`, `ExtendedClass` | `Title`, `Actions`, `Content` |
| `SectionGroup` | Group of `Section`s with optional sticky index | `HasStickyTitles`, `ExtendedClass` | `Sections` (accepts `Section` children) |
| `Tag` | Inline label / chip | `Color`, `Size`, `IsLight`, `Shape`, `ExtendedClass` | `Content` |
| `Tooltip` | Hover/focus popup | `StartsOpen`, `Position`, `Trigger` (`Entities.Trigger.Hover` / `Click`), `ExtendedClass` | `Content` (popup body), `Trigger` (anchor element) |
| `UserAvatar` | User photo with initials fallback | `Name`, `Image`, `Color`, `Size`, `Shape`, `IsLight`, `ExtendedClass` | *(none)* |

Detail: [`patterns/content.md`](./patterns/content.md)

## Interaction patterns (24)

| SourceBlock | Purpose | Key arguments | Placeholders / Events |
|---|---|---|---|
| `ActionSheet` | Bottom action menu (≤5 buttons) | `IsOpen` | `Button1`–`Button5` · event `OnClose` |
| `Animate` | CSS animation wrapper | `AnimationType`, `Speed` | `Content` |
| `AnimatedLabel` | Input with animated floating label | `ExtendedClass` | `Input` |
| `BottomSheet` | Slide-up panel from bottom | `IsOpen`, `ExtendedClass` | `Content` |
| `Carousel` | Horizontal slide gallery | `Navigation` (`Entities.CarouselNavigation`), `Height`, `ItemsPerSlide`, `OptionalConfigs` | `CarouselItems` · event `OnSlideMoved` (`Index`) |
| `DatePicker` | Single-date picker (with optional time) | `DateFormat`, `ShowTodayButton`, `TimeFormat`, `OptionalConfigs`, `ExtendedClass` | *(none)* · event `OnSelected` (`SelectedDateTime`) |
| `DatePickerRange` | Date-range picker | `DateFormat`, `ShowTodayButton`, `OptionalConfigs`, `ExtendedClass` | *(none)* · event `OnSelected` (`DatePickerId`, `SelectedStartDate`, `SelectedEndDate`) |
| `DropdownSearch` | Searchable single-select | `OptionsList`, `StartingSelection`, `Prompt`, `OptionalConfigs` (`{ NoResultsText, SearchPrompt }`), `ExtendedClass` | *(none)* · event `OnChanged` **mandatory** |
| `DropdownTags` | Multi-select dropdown with chips | `OptionsList`, `Prompt`, `OptionalConfigs` | event `OnChanged` |
| `DropdownServerSide` | Server-side dropdown wrapper | `IsDisabled` | *(delegates)* |
| `DropdownServerSide_SingleSelectionTextImage` | Single-select with per-option image | `OptionsList`, `IsDisabled` | event `OnChanged` |
| `DropdownServerSide_MultipleSelection` | Multi-select with server-side search | `OptionsList`, `IsDisabled` | event `OnChanged` |
| `DropdownServerSide_MultipleSelectionWithFooter` | Multi-select with apply/clear footer | `OptionsList`, `IsDisabled` | event `OnChanged` |
| `DropdownServerSide_WithOnScrollEnding` | Infinite-scroll dropdown | `OptionsList`, `IsDisabled` | events `OnChanged`, `OnScrollEnding` |
| `FloatingActions` | Speed-dial floating action button | `IsHover` | `Content` |
| `InputWithIcon` | Input with leading or trailing icon | `AlignIconRight`, `ExtendedClass` | `Icon`, `Input` |
| `LightBoxImage` | Click-to-open full-size image | `ExtendedClass` | `Image` |
| `MonthPicker` | Month/year selector | `DateFormat`, `MinDate`, `MaxDate`, `ExtendedClass` | *(none)* · event `OnSelected` (`SelectedMonth`) |
| `Notification` | Toast notification | `StartsOpen`, `Position`, `Width`, `OptionalConfigs`, `ExtendedClass` | `Content` · event `OnClose` |
| `RangeSlider` | Single-value slider | `MinValue`, `MaxValue`, `StartingValue`, `Orientation`, `Size`, `OptionalConfigs`, `ExtendedClass` | *(none)* · event `OnValueChange` **mandatory** |
| `RangeSliderInterval` | Two-handle interval slider | `MinValue`, `MaxValue`, `StartingValueFrom`, `StartingValueTo`, `OptionalConfigs`, `ExtendedClass` | event `OnChange` (`From`, `To`) |
| `ScrollableArea` | Scrollable container with custom scrollbar | `ScrollbarStyle`, `IsVertical`, `Height`, `ExtendedClass` | `Content` |
| `Search` | Search input wrapper *(deprecated → use `Input` with search icon)* | `Prompt` | `Input` |
| `Sidebar` | Slide-out side panel | `StartsOpen`, `Direction`, `Width`, `HasOverlay`, `ExtendedClass` | `Header`, `Content` · event `OnToggle` (`IsOpen`, `SidebarId`) |
| `StackedCards` | Swipeable stacked cards | `Direction`, `StackedOptions`, `ExtendedClass` | `CardItems` · events `OnCardClicked`, `OnEndStack` |
| `TimePicker` | Time picker | `TimeFormat`, `InitialTime`, `Is24Hours`, `OptionalConfigs`, `ExtendedClass` | *(none)* · event `OnSelected` (`SelectedTime`) |
| `Video` | HTML5 video player | `URL`, `Controls`, `Loop`, `Mute`, `Autoplay`, `ExtendedClass` | *(none)* · client actions `VideoPlay`, `VideoPause` |

Detail: [`patterns/interaction.md`](./patterns/interaction.md)

## Navigation patterns (12)

| SourceBlock | Purpose | Key arguments | Placeholders / Events |
|---|---|---|---|
| `BottomBarItem` | Mobile bottom-bar tab | `ExtendedClass` | `Icon`, `Text` |
| `Breadcrumbs` | Crumb-trail container | `ExtendedClass` | `Content` (accepts `BreadcrumbsItem`) |
| `BreadcrumbsItem` | Single breadcrumb | `ExtendedClass` | `Title` (separators rendered automatically by `Breadcrumbs` parent) |
| `Pagination` | Page-through controls | `StartIndex`, `MaxRecords`, `TotalCount`, `ShowGoToPage`, `ExtendedClass` | `Previous`, `Next` (icon glyphs — live-verified; upstream wrongly claims none) · event `OnNavigate` (`NewStartIndex` Integer) |
| `SectionIndex` | Anchor-based section navigation | `ExtendedClass` | `Content` (accepts `SectionIndexItem`) |
| `SectionIndexItem` | Single anchor link | `ScrollToWidgetId`, `ExtendedClass` | `Content` |
| `Submenu` | Collapsible nav group | `ExtendedClass` | `Menu`, `Items` |
| `Tabs` | Tabbed content switcher | `StartingTab`, `TabsOrientation` (`Entities.Orientation`), `TabsVerticalPosition` (`Entities.Direction`), `Height`, `OptionalConfigs` (`{ JustifyHeaders, … }`) | `Header` (accepts `TabsHeaderItem`), `Content` (accepts `TabsContentItem`) · event `OnTabChange` (`ActiveTab` Integer), `Initialized` |
| `TabsHeaderItem` | Single tab header | `IsDisabled`, `ExtendedClass` | `Title` |
| `TabsContentItem` | Single tab content panel | `ExtendedClass` | `Content` |
| `TimelineItem` | Single timeline event | `Color` | `Left`, `Icon`, `Title`, `Content`, `Right` |
| `Wizard` | Step indicator | `IsVertical` | `Content` (accepts `WizardItem`) |
| `WizardItem` | Single step | `Status` (`Entities.Steps`), `UseTopLabel`, `ExtendedClass` | `Icon`, `Label` |

Detail: [`patterns/navigation.md`](./patterns/navigation.md)

## Numbers patterns

| SourceBlock | Purpose | Key arguments | Placeholders / Events |
|---|---|---|---|
| `Counter` | KPI card | `BackgroundColor`, `Height`, `IsVertical`, `ExtendedClass` | `Content` (icon + value + label, all in this single placeholder) |
| `ProgressBar` | Linear progress indicator | `Progress` (0–100), `ProgressColor`, `TrailColor`, `Thickness`, `OptionalConfigs`, `ExtendedClass` | *(none)* |
| `ProgressCircle` | Circular progress indicator | `Progress` (0–100), `ProgressColor`, `TrailColor`, `Size`, `Thickness`, `OptionalConfigs`, `ExtendedClass` | *(none)* |
| `Rating` | Star rating display/input | `RatingValue`, `RatingScale`, `IsEdit`, `Size`, `ExtendedClass` | *(none)* · event `OnSelect` (`RatingValue` Integer, fires only when `IsEdit = True`) |
| `Badge` | Inline count/status pill | `Color`, `IsLight`, `Number`, `Shape`, `Size`, `ExtendedClass` | *(none)* — also available as a CSS-only `IContainer` pattern |
| `IconBadge` | Icon with overlaid count badge | `Color`, `IsLight`, `Number` | `Icon` — also available as a CSS-only `IContainer` pattern |

Detail: [`patterns/numbers.md`](./patterns/numbers.md)

## Adaptive patterns (12)

| SourceBlock | Purpose | Key arguments | Placeholders |
|---|---|---|---|
| `Columns2` | 2 equal columns | `GutterSize` (`Entities.GutterSize`), `PhoneBehavior` / `TabletBehavior` (`Entities.BreakColumns`: `None` / `All` / `First`), `ExtendedClass` | `Column1`, `Column2` |
| `Columns3` | 3 equal columns | same as `Columns2` | `Column1`–`Column3` |
| `Columns4` | 4 equal columns | same | `Column1`–`Column4` |
| `Columns5` | 5 equal columns | same | `Column1`–`Column5` |
| `Columns6` | 6 equal columns | same | `Column1`–`Column6` |
| `ColumnsMediumLeft` | 2 cols ~60/40 (wider left) | same | `Column1` (wide), `Column2` (narrow) |
| `ColumnsMediumRight` | 2 cols ~40/60 (wider right) | same | `Column1` (narrow), `Column2` (wide) |
| `ColumnsSmallLeft` | 2 cols ~33/67 (narrow left) | same | `Column1` (narrow), `Column2` (wide) |
| `ColumnsSmallRight` | 2 cols ~67/33 (narrow right) | same | `Column1` (wide), `Column2` (narrow) |
| `DisplayOnDevice` | Conditional rendering per device | *(none)* | `OnDesktop`, `OnTablet`, `OnPhone` |
| `Gallery` | Responsive item grid (1–8 per row) | `RowItemsDesktop` / `RowItemsTablet` / `RowItemsPhone` (Integer), `ItemsGap` (quoted text token: `"\"base\""`, `"\"s\""`, …), `ExtendedClass` | `Content` (typically wraps an `IList`) |
| `MasterDetail` | Split list/detail view | `Height`, `LeftPercentage`, `OpenedOnPhone` | `LeftContent`, `RightContent` · event `DetailClose` |

Detail: [`patterns/adaptive.md`](./patterns/adaptive.md)

## Utility patterns (9)

| SourceBlock | Purpose | Key arguments | Placeholders / Events |
|---|---|---|---|
| `AlignCenter` | Centers content (H or V) | `IsHorizontal` | `Content` |
| `ButtonLoading` | Wraps a Button to show loading spinner | `IsLoading`, `ShowLabelOnLoading` | `Button` |
| `CenterContent` | Top/Center/Bottom zones in fixed height | `Height` | `Top`, `Center`, `Bottom` |
| `InlineSVG` | Renders raw SVG markup | `SVGCode` | *(none)* |
| `MarginContainer` | Wraps content with responsive side margins | `ExtendedClass` | `MarginContainer` |
| `MouseEvents` | Detects mouse drag on a target | `WidgetId` | event `Move` (`OffsetX`, `OffsetY`) |
| `Separator` | Horizontal or vertical divider | `Color`, `IsVertical`, `Space` | *(none)* |
| `SwipeEvents` | Detects swipe gestures | `WidgetId` | events `SwipeUp`, `SwipeDown`, `SwipeLeft`, `SwipeRight` |
| `TouchEvents` | Detects touch drag | `WidgetId`, `PreventDefaults` | event `Move` (`OffsetX`, `OffsetY`) |

Detail: [`patterns/utilities.md`](./patterns/utilities.md)

## Popup widget (built-in, not a UI block)

`Popup` is a native widget (not a `IMobileBlockInstanceWidget`). Toggled via a Boolean LocalVariable bound to `ShowPopup`. For end-to-end recipes (confirmation, lookup, form data-entry), see upstream `recipes/popup-modal-dialogs.md` (not bundled).

| Property | Type | Purpose |
|---|---|---|
| `ShowPopup` | Boolean expression | Visibility |
| `Style` | Text | Use `"\"popup-dialog\""` for standard modal |
| `content` | Widget[] | Body widgets (lowercase `content` per widget conventions (see [ui-reference.md](ui-reference.md))) |

## Form input widgets (built-in, not blocks)

These are native OutSystems widgets, not OutSystems UI blocks:

| Widget | Purpose |
|---|---|
| `Button` / `Link` | Action triggers (`OnClick` → ScreenAction) |
| `Input` | Single-line text/date/number input (`Variable`, `InputType`, `Mandatory`) |
| `TextArea` | Multi-line input |
| `Checkbox` | Boolean toggle |
| `RadioButton` / `RadioGroup` | Single-choice |
| `Switch` | On/off toggle |
| `Dropdown` | Select from list (Source bound to aggregate `.List`) |
| `Upload` | File upload |
| `Form` | Validation container (children in `content`, includes `OnSaveClick` action with `Form1.Valid` check) |
| `Label` | Field label (use `TargetWidget` to point to its Input's `Name`) |
| `List` / `ListItem` | Repeating container bound to `Source = <Aggregate>.List` |
| `TableRecords` | Tabular data with `headerRow` + `row` arrays |
| `Container` | Generic block-level wrapper |
| `IfWidget` | Conditional rendering (`Condition`, `TrueBranch`, `FalseBranch`) |
| `TextWidget` | Static text |
| `Expression` | Bound text from a variable or expression |
| `Icon` | Icon glyph |
| `ImageWidget` | Image |
| `AdvancedHtml` | Custom HTML tag (use `Tag: "h1"` for screen titles) |

See [`ui-reference.md`](ui-reference.md) for casing and binding rules.

## Quick lookup by requirement

| Requirement keyword | Block(s) |
|---|---|
| FAQ / collapsible | `Accordion` + `AccordionItem` |
| empty / no-results | `BlankSlate` |
| toast / notification | `Notification` (auto-dismiss) or `Alert` (inline) |
| confirmation modal | `Popup` — see upstream `recipes/popup-modal-dialogs.md` (not bundled) |
| date picker | `DatePicker` (single) / `DatePickerRange` (range) / `MonthPicker` / `TimePicker` |
| dropdown with search | `DropdownSearch` |
| multi-select dropdown | `DropdownTags` or `DropdownServerSide_MultipleSelection` |
| infinite-scroll dropdown | `DropdownServerSide_WithOnScrollEnding` |
| carousel / slideshow | `Carousel` |
| sidebar / drawer | `Sidebar` |
| bottom sheet | `BottomSheet` |
| FAB / speed dial | `FloatingActions` |
| swipe cards (Tinder) | `StackedCards` |
| video | `Video` |
| image lightbox | `LightBoxImage` |
| pagination | `Pagination` (bound to a paginated aggregate) |
| tabs | `Tabs` + `TabsHeaderItem` + `TabsContentItem` |
| wizard / steps | `Wizard` + `WizardItem` |
| breadcrumbs | `Breadcrumbs` + `BreadcrumbsItem` |
| timeline | `TimelineItem` |
| star rating | `Rating` |
| progress bar | `ProgressBar` (linear) / `ProgressCircle` (radial) |
| badge / chip | `Tag` (chip) / `Badge` (numeric) / `IconBadge` (overlay on icon) |
| user avatar | `UserAvatar` |
| tooltip | `Tooltip` |
| chat bubble | `ChatMessage` |
| flip card | `FlipContent` |
| floating panel | `FloatingContent` |
| product card grid | `Gallery` (with `IList` + `Card`/`CardSectioned`) |
| master/detail layout | `MasterDetail` |
| device-specific content | `DisplayOnDevice` |
| 2/3/N column layout | `Columns2`–`Columns6` (or `ColumnsSmall*` / `ColumnsMedium*` for asymmetric) |
| swipe gestures | `SwipeEvents` |
| inline SVG | `InlineSVG` |
| visual divider | `Separator` |
| centered content | `AlignCenter` (1D) / `CenterContent` (with top/center/bottom zones) |
| button with spinner | `ButtonLoading` |

## Critical rules (don't ignore)

1. **Every `IMobileBlockInstanceWidget` MUST have `Arguments: []` and `PlaceholdersContent: []`** even if both are empty. Missing either crashes the model.
2. **Use FULL PATH format** (`"SourceBlock.Name"`) for `Parameter` and `Placeholder` values when generating new model patches.
3. **`Gallery` content must wrap an `IList`** when the items come from an aggregate. `Gallery → Content → IList → Card`.
4. **`Counter` has only ONE placeholder** (`Counter.Content`). Put icon, value, and label all inside it. There are no separate `Value`/`Label`/`Icon` placeholders.
5. **`UIBlockInstanceWidget` does not accept `Width`, `Style`, `Margin`, or `CustomStyle`** directly. To style a block, wrap it in a `Container`.
6. **Tabs / Accordion / Wizard / Breadcrumbs / SectionIndex / SectionGroup / Submenu** require their child item blocks (`TabsHeaderItem`, `AccordionItem`, etc.) inside specific named placeholders. See per-category files.
7. **`Pagination` requires `StartIndex` + `MaxRecords` LocalVariables** bound to its source aggregate. The `OnNavigate` handler must `Assign(StartIndex = NewStartIndex)` and `RefreshDataNode` the aggregate.
8. **Toggle pattern** for ActionSheet, BottomSheet, Notification, Sidebar, Popup: a `LocalVariable Show*Popup`/`IsOpen` (Boolean) + a `Toggle*` ScreenAction that assigns `not <variable>` + the block's visibility argument bound to that variable.
