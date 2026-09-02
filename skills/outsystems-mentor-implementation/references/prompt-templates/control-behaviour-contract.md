# Control behaviour contract (prompt template)

- version: 1 (2026-09-02 — authored from the restaurant-app-v2 run, 2026-08-27 to 2026-08-31, where "+ Adicionar", the reorder arrows, language promote/remove, the dispatch retry, the digital switch, the language tabs' `OnTabChange` and a suggestion row all rendered and did nothing. Every one passed Mentor validation with `error_count: 0` and was found by a human clicking it. The screen prompts had transcribed the blueprint's region tree — which widgets exist — and never said what each control's event does. Runtime catalog of the shapes: `../execution-gates.md` §6, shapes 1, 2, 11 and 12)
- owner: `outsystems-mentor-implementation/references/odc-visual-source-ui-discipline.md` § "Every Interactive Control Ships Its Behaviour"
- placeholders: `<ScreenName>`, `<WidgetName>`, `<Event>`, `<ActionName>`, `<InputArgs>`, `<ObservableResult>`

Use this block inside every screen-creating or screen-editing Mentor prompt on the
blueprint route, once per interactive control the blueprint's interaction inventory
lists (prompt packet item 1). A control is interactive when a user can activate it:
Button, Link, List Item, Icon, Switch, Checkbox, Dropdown, Input with an on-change
behaviour, Tabs, and any row a click is meant to act on.

**A prompt that names a control without its behaviour is incomplete.** Naming the
widget and its region is the region tree; it is not an instruction to wire anything,
and Mentor building exactly what such a prompt says produces a control that renders
and does nothing. State four things per control, and state them on the widget:

1. `<Event>` — the widget's own event property (`On Click`, `On Change`, `On Tab Change`).
2. `<ActionName>` — the screen or client action the event points at, by name.
3. `<InputArgs>` — every input argument the event passes, with the expression for each,
   or `none`. Values the handler needs from a repeated row are passed here.
4. `<ObservableResult>` — what a person sees after activating it. Written so the same
   sentence can be checked by clicking the control in the published app.

Give every interactive control a stable widget name (`<WidgetName>`, e.g. `BtnAddSopa`,
`SwtDigital`, `TabsLanguage`) and use that same name in the prompt, the read-back and
any later verification. A control the prompt names only by its caption cannot be
targeted by anything downstream. The name is a model and read-back identifier: it
makes the widget addressable in the built model and in the turn's own report. It is
not yet a runtime selector — what a rendered control can be clicked by needs an
interaction-spec mapping that does not exist yet.

## Template

```text
Screen: <ScreenName>

Interactive controls — for each control, wire the event as stated. Do not add
controls this list does not name, and do not leave any event on this list unset.

- Widget <WidgetName> (<widget kind>)
  <Event> -> <ActionName>
  Input arguments: <InputArgs>
  Observable result: <ObservableResult>

Constraints for this screen:
- Prefer a Button, a Link, or the List Item's own On Click for anything a user
  activates. On Click is mandatory on those three, so an unset pointer fails
  TrueChange; a Container's click event is optional, so an unset or unbuilt one
  publishes, renders, and does nothing with no build-time signal at all. If a
  Container event is used deliberately, it must pass its values as explicit input
  arguments and its binding must be named in the read-back below.
- Do not read `<Aggregate>.List.Current` inside a handler that is not bound to the
  row's own event. Pass the row's values as input arguments on the widget's event
  and use only those parameters in the action body.

Before ending this turn, read back the body of every client action and every
server action you created or changed on this screen, node by node, in order.
Then report, for each named widget above, the value its event property now holds.
```

The read-back is the closing instruction of the turn, not an optional audit. Ask for
the body node by node and for the event property per widget: a question phrased about
what an action does is answered from the action, which exists, so the one field in
doubt — the widget's pointer — is the field the answer never reads
(`../odc-mentor-hardening.md` → `## Ask What The Event Points At, Not What The
Action Does`). A read-back that returns an empty body, or a widget whose event reads
empty, means the turn is not clean regardless of `error_count`.
