# ODC ModelAPI — The Code-Application Surface

> **Provenance.** Curated 2026-08-27 from `OutSystems/modelapidocs.github.io`
> (**private** repository — a reader without access to the OutSystems
> organisation cannot open the cited pages, and that is why the citations are
> paths and not links), read read-only over authenticated `gh api` at commit
> `fe7818a710d7d1b85b3be056be1140531830362b` on its default branch. Nothing was
> cloned. The repository is a DocFX site generated from the ModelAPI source on
> every push, so **an entry is only checkable against the commit above**; a
> refresh that changes entries must change that commit too.
>
> **This file is not part of any retrieval corpus and must not be added to one.**
> Indexing the source repository was ruled out and stays ruled out — the corpus
> is ~1,830 generated pages of which only a small minority carry prose, and the
> curated slice below is the whole of its value. Keep this file hand-sized.

## 1. What This Says, And What It Does Not

Every entry below is a **declaration or a doc comment emitted from the ModelAPI
source**. That makes this file authoritative for **what the ModelAPI exposes**:
which interfaces exist, which properties are settable, what a method takes, and
which constraints the API documents about itself.

It is authoritative for **nothing else**. The surface is not the runtime
behaviour, and this file never claims it is. When a question is "what does the
platform *do* when this runs", the answer is not here — it is in
`odc-studio-language-elements.md` for element semantics, in
`odc-platform-guardrails.md` for platform rules, and in
`odc-mentor-hardening.md` for measured Mentor behaviour with its own evidence
lines. Two authority classes, deliberately kept apart:

| Question | Answered by |
|---|---|
| "Is there a way to set an entity attribute's delete rule from code?" | this file — it is an API-surface question |
| "What delete rule should an ODC same-app reference use?" | `odc-platform-guardrails.md` — a platform rule |
| "Mentor said it set it and nothing changed" | `odc-mentor-hardening.md` → host execution model — measured behaviour |

Anything below that the corpus does not state outright is marked **inferred**.
There are only a handful of those, and each one names what it is inferred from.

**How this connects to Mentor.** Mentor's coding agent emits an `execute_code`
call which the host applies through `applyModelApiCode` against exactly this
API, with the code plus an `imports` list. That mechanism, its transaction
granularity and its failure classification are described in
`odc-mentor-hardening.md` → `### The Host Execution Model`; the provenance for
it lives under `docs/adoption/`. This file is the other half of that pair: the
hardening reference says **how code is applied**, this one says **what the code
may address**. A prompt that asks Mentor for a code-shaped edit is asking for
something on this surface, so the names, the settability and the creation route
below are what determine whether the request is expressible at all.

### 1a. ODC code resolves to the Mobile branch — inferred, and load-bearing

The UI namespace has two parallel branches, `OutSystems.Model.UI.Web` and
`OutSystems.Model.UI.Mobile`. **Inferred rule: applied code against an ODC app
resolves to the Mobile branch** — ODC screens as `IMobileScreen`, ODC blocks as
`IMobileBlock`, ODC widgets deriving from `IMobileWidget` in
`OutSystems.Model.UI.Mobile.Widgets`.

**This is inferred, not stated.** The corpus carries no ODC-versus-O11 marking
anywhere (§16), so it does not say that either branch belongs to either product,
and this file cannot make it say so. What the rule actually rests on is this
estate's own **measured compile evidence**: the widget-wrapping and
screen-traversal sessions recorded in `odc-mentor-hardening.md` compile against
`IMobileScreen`, `IMobileBlock` and
`OutSystems.Model.UI.Mobile.Widgets.IMobileBlockInstanceWidget`, and fail with
`CS1061` / `CS0246` against the unqualified or Web-branch names. That is real
evidence about what resolves, from real runs — but it is observed operational
behaviour, not a documented product boundary, and it is narrower than "ODC is
the Mobile model": it is "the code we have run against ODC apps resolved this
way."

It is recorded here anyway because it is load-bearing: it decides which
interfaces resolve and which `imports` entry applied code needs, and getting it
wrong produces a compile error rather than a wrong result. **Every UI entry in
this file is curated on that basis**, and where a Web-branch twin exists it is
not listed — so if the inference is ever falsified, §10 is mis-scoped as a
whole and not merely imprecise. Grounding it in an official ODC source, rather
than in our own compile evidence, is open work.

---

## 2. The Object Spine

Everything in the model is an `IModelObject`. Three interfaces stack up under
almost every type you will touch, and their members are inherited — they will
not appear on the page of the type you are looking at.

*Pages: `docs/api/OutSystems.Model.IModelObject.html`,
`…IObject.html`, `…IObjectSignature.html`.*

### 2a. Identity and navigation — `IModelObject`

| Member | Declaration | Note |
|---|---|---|
| `Key` | `IKey Key { get; }` | unique **inside a module**, may repeat across modules |
| `GlobalKey` | | "Global keys uniquely identify objects" |
| `Parent` | | "may be null for top level elements" — applications, eSpaces, extensions |
| `Children` | | direct children only |
| `Referrers` | | "the objects that refer to this one" — the reverse edge, free |
| `Generation` | `int` | increases on every transaction in which the object changes |
| `WasDeleted` | `bool` | true after `Delete()` |
| `IsDetached` | `bool` | see §3d |
| `Delete()` | `void Delete()` | "Delete the object **and its children**. The object will be automatically [removed] from its corresponding parent collection." |
| `GetInterface()` | | see below |

**`GetInterface()`, not `GetType()`.** The corpus states this plainly:
`GetType()` "always returns a class, which for the Model API is an **internal
class** and not very useful for decision purposes. `GetInterface()`, however,
returns one of the Model API interfaces, namely the most specific one
implemented by the object."

This is the documented root of a whole failure family. Code that branches on
`GetType()`, or that casts to a guessed interface, reports "the object is not
there" when the object is present and merely not addressable the way the code
asked. `odc-mentor-hardening.md` records that "created, then not found" is most
often exactly this, and never to infer a rollback from it. `GetInterface()` is
the API-surface answer to that triage step.

### 2b. Ordering and placement — `IObject`

`IObject` adds the movement surface. Every one of these carries the same caveat
in the corpus: **"This requires the object's child collection to be a
sequence."**

`IndexInParent`, `MoveToEnd()`, `MoveBefore()`, `MoveAfter()`,
`MoveBeforeSibling(IObject)`, `MoveAfterSibling(IObject)`,
`MoveToNewAbsoluteIndex(int)`, `MoveToNewRelativeIndex(int)`, plus the
`CanMoveBefore` / `CanMoveAfter` / `CanMoveToNewAbsoluteIndex(int)` /
`CanMoveToNewRelativeIndex(int)` guards, each documented as "True if
\<the matching method\> can be called."

`IObject` also carries `Copy(…)`, `Duplicate(…)` and `CreateSibling` (§3b).

### 2c. Validation and digest — `IObjectSignature`

`IsValid`, `GetValidationMessages(bool)`, `Digest`, `ObjectKey`, `GetESpace()`,
`GetAllDescendantsOfType<T>()`, `ReplaceReferences(IObjectSignature,
IObjectSignature)`, and two documented ones:

- `IsSystemObject` — "true if this is a non-user created object that always
  exists in the eSpace". The way to tell a platform-supplied element from an
  authored one.
- `ReadableIdentifier` — "a readable identifier (or null, if none exists) by
  which the object can be referred to in changeset definitions."

### 2d. The module — `IESpace`

*Page: `docs/api/OutSystems.Model.IESpace.html`.* Mostly outside what applied
code touches, but four things matter:

- **`Digest` vs `ContentDigest`.** `Digest` "changes if the app is updated";
  `ContentDigest` "will not change if the app is updated" — it is stamped at the
  last save. `SignatureCompatibilityDigest` covers only "the elements whose
  changes causes a broken reference".
- `GetValidationMessages(IPlatformCapabilities)` — validation "optionally
  filtered based on the capabilities of a target platform environment".
- `DoInDetachedMode(Action)` / `DoInDetachedMode<T>(Func<T>)` — see §3d.
- `GetWorkingTool()` / `GetWorkingAgentName()` — see §15.

---

## 3. Creating Objects

This section is the one most likely to save a wasted `applyModelApiCode` pass.

### 3a. Children come from a parent factory method

**The collections a parent exposes are not the mutation route.** `IEntity`
exposes `ISequence<IEntityAttribute> Attributes { get; }` — get-only, with no
`Add`. You cannot add to it, and there is no free-standing constructor for an
attribute. The attribute is created by asking the parent:

```csharp
IEntityAttribute CreateAttribute(string name = null, IKey key = null)
```

That shape repeats across the whole API, and the name is always
`Create<Child>`, with the same two optional trailing arguments:

| Parent | Creates |
|---|---|
| `IEntity` | `CreateAttribute` |
| `IStructure` | `CreateAttribute` |
| `IStaticEntity` | `CreateRecord` |
| `IAction` | `CreateInputParameter`, `CreateOutputParameter`, `CreateLocalVariable`, `CreateNode<T>` |
| `IMobileFlow` | `CreateScreen`, `CreateBlock`, `CreateEmail`, `CreateNode<T>` |
| `IMobileScreen` / `IMobileBlock` | `CreateScreenAction`, `CreateScreenAggregate`, `CreateDataAction`, `CreateWidget` |
| `IAssignNode` | `CreateAssignment` |
| `ISwitchNode` | `CreateCondition` |
| `ISQLNode` | `CreateInputParameter`, `CreateOutput` |
| `IBlockEvent` | `CreateInputParameter` |
| `IDatabaseAggregate` | `CreateSource`, `CreateFilter`, `CreateSort`, `CreateJoin`, `CreateGroupByAttribute`, … |

The exceptions are worth knowing because they are the only ones:

- `IEntityIndex.AddAttribute(IEntityAttribute attribute)` — **adds an existing**
  attribute rather than creating a new child. An index references attributes it
  does not own.
- `ITheme.AddOrUpdateThemeValues(Dictionary<ThemeProperty, string>)` — bulk
  upsert, not a per-child create.
- `ICollection<>`-typed members (§4) accept `Add` / `Remove` directly.

### 3b. `CreateSibling` — same collection, next position

```csharp
T CreateSibling<T>(string name = null, IKey key = null)
IModelObject CreateSibling(Type type, string name = null, IKey key = null)
```

Documented as: "Creates a new object of type `T` in the same collection as this
object. If the collection is a sequence then the new object is placed **right
after this one**. This method is **not applicable to top-level elements**
(`IApplication`, `ISolution`, `IESpace`, and `IExtension`)."

The positional guarantee is the point. Inserting a widget next to an existing
one, or a parameter after a known one, is a `CreateSibling` rather than a
`Create<Child>` followed by a `Move`.

### 3c. The generic factory — `FactoryExtensions`

*Page: `docs/api/OutSystems.Model.Factory.FactoryExtensions.html`.* When the
parent has no matching `Create<Child>`:

```csharp
CreateChild(this IModelObject parent, Type childType, IChildCollection collection,
            string name, IKey key)
CreateChild(this IModelObject parent, ModelObjectDefinition childDefinition,
            IObjectResolver resolver)
```

Documented constraint: **`childType` "must be a leaf interface."** An
intermediate or abstract interface — `IWidget`, `IActionNode`, `IAggregate` —
is not a valid `childType`. The corpus does not say what happens if you pass
one, so what the failure looks like is *not* stated here.

Two more from the same page:

- `CreateOrTransformObjects(IESpace, IObjectResolver, …)` — "Creates or
  transforms a set of objects in an eSpace in a **single shot operation**." The
  batch route, in four overloads.
- `Transform(IModelObject, ModelObjectDefinition, IObjectResolver, …)` —
  "Transforms `obj` according to definition `newDefinition`", and
  `ToModelObjectDefinition(…)` for the reverse, "converts a model object to its
  definition representation."

`ModelObjectDefinition` (*page: `…Factory.ModelObjectDefinition.html`*) is the
declarative form: a constructor over `(Type objectType, IChildCollection
childCollection, ModelObjectDefinition parent, IKey key)` plus
`Dictionary<IProperty, object> Properties`, `Children`, `Move(…)`, `Discard()`.

### 3d. Detached objects

`CreateDetachedChild(…)` is documented as: "The detached child **knows its
parent, but the parent doesn't know the detached child**. Since the detached
child is not stored in the parent's collections, it will be **garbage collected
automatically**."

`IESpace.DoInDetachedMode(Action)` runs a whole block that way — "any model
object created while executing the action will be a detached object", and they
"do not need to be direct children of the eSpace". `IModelObject.IsDetached`
reports the state.

**Inferred, from those two doc comments read together:** code that builds an
object and then cannot find it afterwards may have built it detached, in which
case nothing was lost from the model because nothing was ever added to it. The
corpus does not connect detachment to that symptom; the inference is ours, and
it is a third candidate alongside the two already in
`odc-mentor-hardening.md`'s "created, then not found" triage.

---

## 4. The Collection Type Tells You The Mutation Route

Three collection types appear across the API and they are not interchangeable.
Reading the declared type first saves guessing at an `Add` that is not there.

| Declared as | Means | Mutate by |
|---|---|---|
| `IEnumerable<T>` | read-only projection, no guaranteed order | the parent's `Create<Child>`; delete via `IModelObject.Delete()` |
| `ISequence<T>` | read-only **and ordered** | `Create<Child>` / `CreateSibling`; reorder via `ISequence<T>` or `IObject` moves |
| `ICollection<T>` | genuinely mutable set | `Add` / `Remove` directly |

`ISequence<T>` (*page: `docs/api/OutSystems.Model.ISequence-1.html`*) is
`IEnumerable<T>` plus reordering, and nothing else:

```csharp
void MoveToStart(T element);         void MoveToEnd(T element);
void MoveBeforeSibling(T sibling, T element);
void MoveAfterSibling(T sibling, T element);
void SetOrderTo(IEnumerable<T> order);
```

Note there is no `Add`, `Insert` or `Remove` on it. Reordering is available in
two equivalent places — on the sequence (`Widgets.MoveToEnd(w)`) and on the
member (`w.MoveToEnd()`, §2b).

The `ICollection<T>` members are the short list, and they are the ones where
`Add` *is* correct: `IMobileScreen.Targets` and `IMobileBlock.Targets`
(`ICollection<IUIFlowNode>`), and `RequiredScripts` (`ICollection<IScriptSignature>`)
on both.

---

## 5. Expressions

Expressions are model objects, not strings, and this section is where the most
consequential documented hazard in the whole surface lives.

*Pages: `docs/api/OutSystems.Model.Expressions.IExpression.html`,
`…ExpressionDefinition.html`, `…IMutableExpression.html`.*

### 5a. Writing a value: get-only property + `Set<Name>(ExpressionDefinition)`

The single most repeated shape in the API. An expression-valued property is
**get-only**, and is written through a sibling method taking an
`ExpressionDefinition`:

```csharp
IExpression Condition { get; }        void SetCondition(ExpressionDefinition value);
IExpression Title     { get; }        void SetTitle(ExpressionDefinition value);
IExpression Message   { get; }        void SetMessage(ExpressionDefinition value);
IExpression RecordList{ get; }        void SetRecordList(ExpressionDefinition value);
IExpression MaxRecords{ get; }        void SetMaxRecords(ExpressionDefinition value);
IExpression StartIndex{ get; }        void SetStartIndex(ExpressionDefinition value);
```

…and the same for `MaximumIterations`, `StyleClasses`, parameter and variable
default values (`SetDefaultValue`), record attribute values (`SetValue`), and
extended property values (`SetValue`). **If a property is an `IExpression` and
you are looking for a setter, look for `Set` + the property name.**

### 5b. `ExpressionDefinition` — why you cannot build one free-standing

The corpus explains the design: "Due to the way expressions are represented in
the OutSystems model (they're also model objects) we cannot create a
'disconnected' expression and then store it in some other object's property."
`ExpressionDefinition` is the stand-in for a not-yet-created expression.

You rarely construct one explicitly, because of the **implicit conversions**:
from `string`, `bool`, `int`, `long`, `float`, `double` and `decimal`. That is
why `SetCondition("Form1.Valid")` compiles.

For anything structured, use the parser:

```csharp
public static ExpressionDefinition Parse(string text)
public static ExpressionDefinition Convert(object value)
```

`Parse` "detects the special cases of record literals, list literals, and type
conversions, which provide their own parsing methods", with the corpus's own
examples: `{ Name: "Ann" }` for a record literal, `[ 1, 2, 3 ]` for a list
literal, and `user mapTo { FirstName: Name }` for a type conversion.

### 5c. `IExpression.Text` — the handle can go stale under you

The property is settable, and the corpus attaches a warning to it that changes
what correct code looks like:

> "Allows to manipulate the expression as text. Note that **setting the text of
> an expression may result in a new expression object being created, and the
> old one being deleted**. Thus, **do not assume that you can keep using an
> expression after you have changed its text. You must get the actual
> expression again from its parent.**"

So this is wrong:

```csharp
var expr = ifNode.Condition;
expr.Text = "Form1.Valid";
var t = expr.Type;            // expr may already be deleted
```

and this is the documented form — re-read from the parent after the write, or
avoid the hazard entirely by using the `Set…` method in §5a:

```csharp
ifNode.SetCondition("Form1.Valid");
var t = ifNode.Condition.Type;   // fresh handle, read back from the parent
```

**Inferred, and labelled as such:** this is a mechanism that would produce the
"reads back wrong / reads back stale" shape after a text-shaped expression
write. It is *not* the same claim as the estate's measured "Mentor mangles
string literals" observation in `odc-mentor-hardening.md`, and this file does
not assert that it explains it — the corpus says nothing about Mentor. Treat it
as a candidate to test, not as the cause.

The rest of `IExpression`: `Root` ("the root of the expression syntactic tree.
Use it [to] navigate on the expression [in] a structure[d] way, i.e. without
having to try to 'interpret' its text"), `ExpandedRoot` / `ExpandedText` (same
as `Root` / `Text` "in case the expression exists inside an aggregate and a
user-defined function is being called"), `Environment`, `Type`, and
`SubstituteAndSimplify(Dictionary<IObjectSignature, object>)` whose keys "must
be a variable (input parameter, output parameter, local variable)" and whose
values "must be a non-null literal of the same type".

### 5d. Building a tree — `IMutableExpression`

`AsMutableExpression()` opens the syntactic-tree builder; `Commit()` closes it.
It carries ~28 `Create…` factories — `CreateTextLiteral`, `CreateIntegerLiteral`,
`CreateBooleanLiteral`, `CreateDateTimeLiteral`, `CreateBinaryOperation`,
`CreateUnaryOperation`, `CreateFunctionCall`, `CreateFieldAccess`,
`CreateIndexer`, `CreateIdentifier`, `CreateRecordLiteral`, `CreateListLiteral`,
`CreateTypeConversion`, and the bindings (`CreateObjectBinding`,
`CreateByNameBinding`, `CreateBuiltinFunctionBinding`,
`CreateUnknownObjectBinding`) — each taking optional `whitespaceBefore` /
`whitespaceAfter` so round-tripped text keeps its formatting.

For most applied code the `ExpressionDefinition` route in §5b is enough; this
is the route when you need to rewrite part of an existing expression in place.

---

## 6. Data Model

*Pages: `docs/api/OutSystems.Model.Data.IEntity.html`,
`…IEntityAttribute.html`, `…IStaticEntity.html`, `…IStaticEntityRecord.html`,
`…IStructure.html`, `…IEntityIndex.html`,
`docs/api/OutSystems.Model.Types.IAttribute.html`,
`docs/api/OutSystems.Model.Data.IRecord.html`.*

### 6a. `IEntity`

Settable: `Description`, `Label`, `LabelPlural`, `Public`, `Folder`,
`ExposeReadOnly`, `ExposeProcessEvents`, `IsMultiTenant`
(`BooleanWithInheritance`), `IsRestrictedInQueries`, `ShowTenantIdentifier`,
`UseTranslations`, `UpdateBehavior` (`UpdateEntityBehaviorType`), and four
attribute pointers: `IdentifierAttribute`, `LabelAttribute`,
`OrderByAttribute`, `IsActiveAttribute` — each an `IEntityAttributeSignature`.

Read-only: `Attributes` (`ISequence<IEntityAttribute>`), `Descriptor`,
`TextResources`.

Methods: `CreateAttribute(string, IKey)`, `ConvertTo(EntityKind targetKind)`,
`CreateOrUpdateTranslation(Culture, string, string)`,
`SetTranslationBehavior(string, TranslationBehavior)`.

`EntityKind` has exactly three values: **`Server`, `Client`, `Static`** — and
`ConvertTo` is the documented route between them, not a settable property.

### 6b. `IEntityAttribute`

Settable on the attribute itself: `DataType` (`IBasicType`), **`DeleteRule`**,
`IsAutoNumber` (`AutoNumber`), `IsSearchable`, `Label`, `OriginalName`,
`OriginalType`. Read-only: `AsSearchable` (`ISearchableAttribute`) — the
accessor form again, see §9a.

**Length, decimals and mandatory live on the inherited `IAttribute`**, not on
`IEntityAttribute`, so they will not appear on the attribute's own page:

```csharp
ITypeSignature DataType { get; set; }   int? Length   { get; set; }
bool IsMandatory        { get; set; }   int? Decimals { get; set; }
string Name             { get; set; }   void SetDefaultValue(ExpressionDefinition value)
```

That matters for the spec-fidelity checks in `odc-mentor-hardening.md`
(`### Preserve Exact Attribute Types From Spec And Source`): the length a spec
pins is `IAttribute.Length`, and code that reads only `IEntityAttribute` will
not see it.

**`DeleteRule` has exactly three values: `Delete`, `Ignore`, `Protect`.** The
API exposes all three on any attribute; **which one is correct for a given
reference is a platform rule, not an API fact** — see
`odc-platform-guardrails.md`, and note the estate's own correction that
`Protect` is the ODC same-app default and the "must be `Ignore`" rule is
cross-app only.

### 6c. Static entities and records

`IStaticEntity` adds `Records` (`IEnumerable<IStaticEntityRecord>`, read-only)
and `CreateRecord(string name = null, IKey key = null)`.

`IStaticEntityRecord` carries `Identifier`, `Icon` (`byte[]`), and the audit
fields — but **not** the attribute values. Those come from the inherited
`IRecord.AttributeValues` (`IEnumerable<IRecordAttributeValue>`, read-only),
where each value is written through `IRecordAttributeValue.SetValue(ExpressionDefinition)`.

The convenience route is an extension (§14):

```csharp
ModelExtensions.SetAttributeValue(this IRecord record, IEntityAttribute attribute,
                                  ExpressionDefinition value)
```

### 6d. Structures and indexes

`IStructure` mirrors `IEntity` on the shape that matters: `Attributes`
(`ISequence<IStructureAttribute>`, read-only) plus `CreateAttribute(string,
IKey)`, with `Public`, `Description`, `Folder` settable and `IsReadOnly`
read-only. `IStructureAttribute` adds `NameInJSON` and `Label`, and inherits its
type/length/mandatory from `IAttribute` exactly as §6b describes.

`IEntityIndex`: `Name`, `Unique`, `Description`, `AutoGenerated` settable;
`IndexAttributes` (`ISequence<IEntityIndexAttribute>`) read-only; and
`AddAttribute(IEntityAttribute attribute)` — the add-existing exception noted in
§3a.

---

## 7. Logic — Actions, Parameters, Roles, Exceptions

*Pages: `docs/api/OutSystems.Model.Logic.IAction.html`, `…IServerAction.html`,
`…IClientAction.html`, `…IRole.html`, `…IAppRole.html`, `…IUserException.html`,
`…ISystemEvent.html`, `docs/api/OutSystems.Model.UI.Mobile.IScreenAction.html`,
`docs/api/OutSystems.Model.IInputParameter.html`, `…IOutputParameter.html`,
`…ILocalVariable.html`.*

### 7a. `IAction` is where the shape lives

The three concrete action kinds — `IServerAction`, `IClientAction`,
`IScreenAction` — all derive from `IAction`, and `IAction` is where the
parameters, the variables and the nodes are:

```csharp
ISequence<IInputParameter>  InputParameters  { get; }
ISequence<IOutputParameter> OutputParameters { get; }
ISequence<ILocalVariable>   LocalVariables   { get; }
IEnumerable<IActionNode>    Nodes            { get; }

IInputParameter  CreateInputParameter (string name = null, IKey key = null);
IOutputParameter CreateOutputParameter(string name = null, IKey key = null);
ILocalVariable   CreateLocalVariable  (string name = null, IKey key = null);
T                CreateNode<T>        (string name = null, IKey key = null) where T : IActionNode;
IActionNode      CreateNode(Type type, string name = null, IKey key = null);
```

**`Nodes` is `IEnumerable<>`, not `ISequence<>`.** There is no index and no
order to a flow's node collection — execution order comes entirely from the
wiring in §8. `IScreenAction` adds nothing beyond `Descriptor`; its whole
surface is `IAction`'s.

The kind-specific properties are small and worth knowing:

| Interface | Adds |
|---|---|
| `IServerAction` | `Function` (bool, settable), `CacheInMinutes` (`int?`), `Public`, `Folder`, `Icon` |
| `IClientAction` | `Function`, `Public`, `Folder`, `Icon` — **no** `CacheInMinutes` |
| `ISystemEvent` | `CreateLocalVariable`, `CreateNode` — **no `CreateInputParameter`**, though `InputParameters` is exposed |

`ISystemEvent`'s asymmetry is a real constraint on the surface: its inputs are
not author-created.

### 7b. Parameters and variables

```csharp
// IInputParameter                     // IOutputParameter        // ILocalVariable
ITypeSignature DataType { get; set; }  DataType { get; set; }     DataType { get; set; }
bool IsMandatory        { get; set; }  Name     { get; set; }     Name     { get; set; }
string Name             { get; set; }  Description               DefaultValue { get; }  // IExpression
void SetDefaultValue(ExpressionDefinition value)  — on all three
```

`Description` on all three is documented as "Text that documents the element…
**The maximum size of this property is 2000 characters.**" `IInputParameter`
also carries `IntegrationName` — "original name on the integration side (e.g.
the SAP / external system identifier)".

Only `IInputParameter` has `IsMandatory`. `ILocalVariable` alone exposes
`Metadata` and `CreateMetadata<T>`.

### 7c. Roles

`IRole`: `Description`, `Folder`, **`IsPersistent`** settable — that is the
whole base surface. `IAppRole` adds `Public` and the audit fields. There is
also `ISystemRole` for the platform-supplied ones (distinguishable via
`IsSystemObject`, §2c).

The role *surface* is this small. Which screens a role gates, and what an RBAC
scope should be, are not API facts — `odc-mentor-hardening.md`
(`### Preserve RBAC Scope Exactly As Specified`) owns that.

### 7d. Exceptions

`IUserException` (`Name` settable) under `IException`, alongside
`ISystemException` and `IRoleException`. The handler side is a flow node —
`IExceptionHandlerNode`, §8c.

---

## 8. Flow Nodes — And How Wiring Actually Works

*Pages under `docs/api/OutSystems.Model.Logic.Nodes.*.html`.*

### 8a. Connectors are a projection; `Target` is the wiring

`IActionNode`, the base every flow node derives from, exposes exactly three
members:

```csharp
IEnumerable<IActionConnector> Connectors         { get; }
IEnumerable<IActionConnector> IncomingConnectors { get; }
IActionNodeDescriptor         Descriptor         { get; }
```

Both connector collections are **read-only** — there is no `CreateConnector` on
the node and no `Add` on the collection. **Wiring is done by assigning a
`Target`-shaped property on the source node**, and the connector collections are
the read-back of that. Guessing the other way round — building connector
objects — is the expensive mistake this section exists to prevent.

The `Target` properties, all `IActionNode` and all settable:

| Node | Wiring properties |
|---|---|
| `IStartNode`, and most single-exit nodes | `Target` |
| `IIfNode` | `TrueTarget`, `FalseTarget` |
| `ISwitchNode` | `OtherwiseTarget`, plus one per `ISwitchCondition` |
| `IForEachNode` | `Target`, `CycleTarget` |
| `IExceptionHandlerNode` | `Target` |
| `IEndNode` | *(none — terminal)* |

`IIfNode` and `IForEachNode` both also carry `SwapConnectors()`, which flips the
two branches without touching either target.

### 8b. The condition/branch nodes

```csharp
// IIfNode
IExpression Condition { get; }   void SetCondition(ExpressionDefinition value);
IActionNode TrueTarget { get; set; }   IActionNode FalseTarget { get; set; }
string Label { get; set; }             void SwapConnectors();

// ISwitchNode
ISequence<ISwitchCondition> Conditions { get; }   ISwitchCondition CreateCondition();
IActionNode OtherwiseTarget { get; set; }         string Label { get; set; }

// IForEachNode
IExpression RecordList { get; }        void SetRecordList(ExpressionDefinition value);
IExpression StartIndex { get; }        void SetStartIndex(ExpressionDefinition value);
IExpression MaximumIterations { get; } void SetMaximumIterations(ExpressionDefinition value);
IActionNode Target { get; set; }       IActionNode CycleTarget { get; set; }
IEnumerable<IActionNode> NodesWithinCycle { get; }
```

`IIfNode.Condition` is get-only and written through `SetCondition`. This is the
API-surface counterpart to the string-matching pattern recorded in
`odc-mentor-hardening.md` → `### IfNode Condition String Matching`: matching a
node by `Condition.ToString()` equality is comparing against a formatted
rendering, which is why that section prescribes `StartsWith`. Matching by
`Label` (settable, plain `string`) avoids the question entirely.

### 8c. The rest of the node catalogue

| Node | Notable members |
|---|---|
| `IAssignNode` | `Assignments` (`ISequence<IAssignment>`), `CreateAssignment()`, `Label`, `Target` |
| `IExecuteServerActionNode` | `Action` (`IActionSignature`, settable), `Arguments` (read-only), `ServerRequestTimeout` (`int?`), `AnimationEffect`, `Name`, `Target` |
| `IExecuteClientActionNode` | same shape, client side |
| `IAggregateNode` | derives from **both** `IAggregate` and `IActionNode`; `Target` |
| `ISQLNode` | `Statement` (plain `string`, settable), `InputParameters` (`ISequence<ISQLInputParameter>`) + `CreateInputParameter`, `Outputs` + `CreateOutput(IRecordTypeSignature entityOrStructure, string name)`, `MaxRecords` + `SetMaxRecords`, `CacheInMinutes`, `Timeout`, `Type` (`IListType`, read-only) |
| `IDestinationNode` | `Destination` (`IObjectSignature`, settable), `Arguments`, `Transition` |
| `IExceptionHandlerNode` | `Exception` (`IException`, settable), `AbortTransaction` (bool), `LogError` (bool), `Name`, `Target` |
| `IRaiseExceptionNode` | raises a named exception |
| `IMessageNode` | `Message` + `SetMessage`, `Type` (`MessageType`), `Label`, `Target` |
| `IRefreshDataNode` | `DataSource` (`IObject`, settable), `MaxRecords` / `StartIndex` + setters, `Arguments`, `Target` |
| `IJavaScriptNode`, `IJSONSerializeNode`, `IJSONDeserializeNode`, `ISendEmailNode`, `IDownloadNode`, `IExcelToRecordListNode`, `IRecordListToExcelNode`, `ICallAgentNode`, `ISemanticSearchNode`, `ITriggerNode`, `ITriggerGlobalNode`, `IAjaxRefreshNode`, `IAttachFileNode`, `ICommentNode`, `IDecisionOutcomeNode` | the remainder of the catalogue |

Two documented ones on `IDownloadNode`: `SaveToDisk` — "set to true to allow the
user to open or save the file" — and `MimeType`, "text literal or expression
specifying the media type of the file", with the corpus's own example values
(`application/pdf`, `image/gif`, `text/html`, and others).

`ISQLNode.Statement` being a plain settable `string` — not an expression — is
worth flagging against `odc-mentor-hardening.md`'s SQL guidance: the API
imposes no structure on it whatsoever.

---

## 9. Aggregates

*Pages: `docs/api/OutSystems.Model.Logic.Aggregates.IAggregate.html`,
`…Database.IDatabaseAggregate.html`, `…Full.IFullAggregate.html`,
`…IFilter.html`, `…ISort.html`, `docs/api/OutSystems.Model.UI.Mobile.IScreenAggregate.html`.*

### 9a. `IAggregate` is a facade — the builders are behind an accessor

This is the clearest instance of the wrong-accessor trap in the whole API, so it
is worth stating flatly: **`IAggregate` has no `CreateFilter`, no `CreateSort`
and no `CreateSource`.** Its own surface is the common metadata only:

```csharp
IDatabaseAggregate AsDatabaseAggregate { get; }
IFullAggregate     AsFullAggregate     { get; }
string Name { get; set; }   int? CacheInMinutes { get; set; }   int? Timeout { get; set; }
bool IsClientSide { get; }  ITypeSignature Type { get; }
IExpression MaxRecords { get; }   void SetMaxRecords(ExpressionDefinition value);
IExpression StartIndex { get; }   void SetStartIndex(ExpressionDefinition value);
ISequence<IImplicitParameter> ImplicitParameters { get; }
```

The composition surface lives on `AsDatabaseAggregate`:

`Sources` + `CreateSource(IDataSource, string, IKey)` · `Filters` +
`CreateFilter(string, IKey)` · `Sorts` + `CreateSort(IKey)` · `Joins` +
`CreateJoin(IKey)` · `GroupByAttributes` + `CreateGroupByAttribute(string, IKey)`
· `AggregatedAttributes` + `CreateAggregatedAttribute(string, IKey)` ·
`CalculatedAttributes` + `CreateCalculatedAttribute(string, IKey)` ·
`MasterSource` · and the `…InGroupBy` variants (`FiltersInGroupBy`,
`SortsInGroupBy`, `CalculatedAttributesInGroupBy`, with matching creators).

`AsFullAggregate` is the other shape — `RootOperation`, `Operations`,
`CreateAddSourceOperation(IDataSource)`, `CreateCombineSourcesOperation()`,
`CreateGroupByOperation()`.

**`IsClientSide` is get-only.** It is fixed when the aggregate is created:
`CreateScreenAggregate(bool isClientSide, string name = null, IKey key = null)`.
Changing it after the fact is not on the surface.

`IFilter` is `Condition` (get-only `IExpression`) + `SetCondition`. `ISort` is
`Attribute` (get-only `IExpression`) + its setter.

`IScreenAggregate` adds `Fetch` (`DataSourceFetch`, settable — values `AtStart`
and `OnDemand`) and `OnAfterFetch` (`IUILifeCycleEvent`, get-only).

---

## 10. UI — Flows, Screens, Blocks, Widgets

Curated on the Mobile branch per §1a.

*Pages: `docs/api/OutSystems.Model.UI.Mobile.IMobileFlow.html`,
`…IMobileScreen.html`, `…IMobileBlock.html`, `…IDataAction.html`,
`docs/api/OutSystems.Model.UI.IWidget.html`, and
`docs/api/OutSystems.Model.UI.Mobile.Widgets.*.html`.*

### 10a. `IMobileFlow`

```csharp
IEnumerable<IMobileFlowNode> Nodes { get; }
IMobileThemeSignature Theme { get; set; }

IMobileScreen CreateScreen(string name = null, IKey key = null);
IMobileBlock  CreateBlock (string name = null, IKey key = null);
IMobileEmail  CreateEmail (string name = null, IKey key = null);
T             CreateNode<T>(string name = null, IKey key = null) where T : IMobileFlowNode;

IMobileScreen Instantiate(IMobileScreen templateScreen, IKey newScreenKey = null);
IEnumerable<IMobileScreen> Instantiate(IEnumerable<IMobileScreen> templateScreens,
                                       IEnumerable<IKey> newScreensKeys = null);
```

`Instantiate` is the template route — creating a screen *from* an existing
screen, singly or in a batch. The corpus does not describe what it copies.

### 10b. `IMobileScreen`

Settable: `AnonymousAccess` (bool), `PageName`, `CustomURL` (bool),
`URLStructure`.

Get-only: `Widgets` (`ISequence<IMobileWidget>` — **direct children only**),
`ScreenActions`, `ScreenAggregates`, `DataActions`, `Title` (`IExpression`),
`Targets` (`ICollection<IUIFlowNode>` — mutable, §4), `RequiredScripts`
(`ICollection<IScriptSignature>` — mutable), and the lifecycle events in §11.

```csharp
void SetTitle(ExpressionDefinition value);
IScreenAction    CreateScreenAction   (string name = null, IKey key = null);
IScreenAggregate CreateScreenAggregate(bool isClientSide, string name = null, IKey key = null);
IDataAction      CreateDataAction     (string name = null, IKey key = null);
IMobileWidget    CreateWidget(IWidgetDefinitionSignature widgetDefinition,
                              string name = null, IKey key = null);
T                CreateWidget<T>(string name = null, IKey key = null) where T : IMobileWidget;
```

`Widgets` holding **direct children only** is the API-surface statement of what
`odc-mentor-hardening.md` records as a compile error from the field: there is no
`AllWidgets`. The traversal answer is `GetAllDescendantsOfType<T>()` (§14).

`AnonymousAccess` being a plain settable bool is an API fact and nothing more;
whether a screen actually renders for an anonymous principal is a runtime
question only a rendered readback settles — `references/execution-gates.md`
§2.

### 10c. `IMobileBlock`

The same surface as the screen — `Widgets`, `ScreenActions`,
`ScreenAggregates`, `DataActions`, `Targets`, `RequiredScripts`, the same five
`Create…` methods, the same lifecycle events — plus `OnParametersChanged`,
which the screen does not have. Blocks are the reusable half of the pair and
that extra event is the difference the API records.

### 10d. `IDataAction`

```csharp
DataSourceFetch Fetch { get; set; }        int? ServerRequestTimeout { get; set; }
IUILifeCycleEvent OnAfterFetch { get; }    IEnumerable<IActionNode> Nodes { get; }
ISequence<IOutputParameter> OutputParameters { get; }  ISequence<ILocalVariable> LocalVariables { get; }
IOutputParameter CreateOutputParameter(…);  ILocalVariable CreateLocalVariable(…);
T CreateNode<T>(…) where T : IActionNode;
```

Note what is absent: **no `CreateInputParameter`, and no `InputParameters`.** A
Data Action takes no inputs on this surface.

### 10e. Widgets

`IWidget` (the branch-neutral base) is deliberately thin: `CustomStyle` (plain
settable `string`), `Descriptor`, the translation helpers, and one distinctive
member:

```csharp
void Delete(bool preserveChildren);
```

An overload of `Delete` that keeps the children — relevant to any unwrap or
re-parent sequence, where the plain `IModelObject.Delete()` would take the
subtree with it (§2a).

`IMobileWidget` adds `Definition` (`IWidgetDefinitionSignature`, get-only) — the
back-pointer to whatever widget definition this instance was created from.

**Two creation routes, and they are not interchangeable:**

```csharp
T             CreateWidget<T>(string name = null, IKey key = null) where T : IMobileWidget;
IMobileWidget CreateWidget(IWidgetDefinitionSignature widgetDefinition, string name = null, IKey key = null);
```

The generic overload creates a **built-in** widget whose interface exists in the
API — `ITextWidget`, `IIfWidget`, `IContent`, `IPlaceholderWidget`,
`IMobileBlockInstanceWidget`. The definition-taking overload creates a widget
from a **widget definition signature**, which is how a consumed block or a
pattern from a UI library is instantiated. In an ODC app most of the visible UI
comes through the second route, because most of it is OutSystems UI blocks
rather than built-in widgets — and there is no built-in interface to name for
those.

A third overload, `CreateWidget(Type type, string name = null, IKey key = null)`,
exists on the **container widgets** (`IContent`, `IPlaceholderWidget`,
`IIfBranchWidget`) but **not** on `IMobileScreen` or `IMobileBlock`. Screens and
blocks take only the generic and the definition-taking forms.

**Nesting only happens through container widgets.** The types exposing
`ISequence<IMobileWidget> Widgets { get; }` plus `CreateWidget` are `IContent`,
`IPlaceholderWidget` and `IIfBranchWidget`. Everything else is a leaf.

| Widget | Members |
|---|---|
| `ITextWidget` | `Text` (plain settable `string`, **not** an expression), `Name`, `ExtendedProperties` + `CreateExtendedProperty()`, `SetStyleClasses(ExpressionDefinition)` |
| `IIfWidget` | `TrueBranch` / `FalseBranch` (get-only `IIfBranchWidget` — created with the widget, not by you), `SetCondition(ExpressionDefinition)`, `Animate`, `DesignMode`, `Name` |
| `IIfBranchWidget` | `Widgets` + the three `CreateWidget` overloads |
| `IContent` | `Widgets` + `CreateWidget` overloads, `SourceProperty` (`IExpressionProperty`) — documented as "**only set when `IsIterated` is true**. It returns the property that provides the list for which the content will be iterated" |
| `IPlaceholderWidget` | `Widgets` + creators, `Events` (`ISequence<IEvent>`) + `CreateEvent()`, `ExtendedProperties` + `CreateExtendedProperty()`, and the full layout surface: `Align`, `AlignItems`, `AlignSelf`, `FlexDirection`, `FlexWrap`, `FlexBasis`, `Flexible`, `JustifyContent`, `Gap`, `Width`, `Height`, `MarginLeft`, `MarginTop`, `EffectiveWidth`, `EffectiveMarginLeft`, `WidgetGridType` |
| `IMobileBlockInstanceWidget` | `Arguments` (`IEnumerable<IArgument>`, read-only — bind via §14) |
| `IPlaceholderContentWidget` | the content filled into a block instance's named placeholder |

Reaching a block instance's placeholder is an extension method and not a
property — `GetPlaceholderContent(blockInstance, placeholderName)`, §14.

`IExtendedProperty` is `Property` (settable `string`) + `SetValue(ExpressionDefinition)`.
It is exposed on `ITextWidget` and `IPlaceholderWidget` among others, but
**`IContent` does not implement `IExtendedPropertiesNode`** — which is the API
statement behind the table-row limitation already recorded in
`odc-mentor-hardening.md`.

---

## 11. Events

*Pages: `docs/api/OutSystems.Model.UI.Mobile.Events.IEvent.html`,
`…IUILifeCycleEvent.html`, `docs/api/OutSystems.Model.UI.IBlockEvent.html`,
`…IEventHandler.html`.*

Four distinct things share the word "event", and mixing them up is easy:

**1. Lifecycle events** — get-only properties on a screen or block, always
present, never created: `OnInitialize`, `OnReady`, `OnRender`, `OnDestroy`
(screen and block), plus `OnParametersChanged` (block only). Each is an
`IUILifeCycleEvent`, whose surface is `Destination` (`IObjectSignature`,
settable — what the event runs) and `Arguments` (read-only).

**2. Sync events** — `OnSyncStart`, `OnSyncComplete`, `OnSyncError`, exposed as
get-only properties *but* with matching creators: `CreateOnSyncStart()`,
`CreateOnSyncComplete()`, `CreateOnSyncError()`. Unlike the lifecycle events,
these are created on demand.

**3. Widget events** — `ISequence<IEvent> Events` + `CreateEvent()` on
`IPlaceholderWidget`. `IEvent` is `Event` (a settable `string` naming the DOM or
widget event), `Handler` (`IObject`, settable), `Arguments` (read-only).

**4. Block events** — `IBlockEvent`, the *declared* event a block exposes:
`Name`, `Description`, `IsMandatory` settable, `InputParameters`
(`ISequence<IInputParameter>`) + `CreateInputParameter`. The consumer side is
`IEventHandler` — `Event` (`IBlockEventSignature`, get-only), `Handler`
(`IObjectSignature`, **settable**), `Arguments` (read-only).

The recurring shape: the handler is a settable pointer, the arguments are a
read-only collection bound through §14.

---

## 12. Theme

*Page: `docs/api/OutSystems.Model.UI.ITheme.html`.*

Settable: `BaseTheme` (`IThemeSignature`), `Layout`, `Header`, `Footer`, `Menu`
(each an `IBlockSignature` — a theme points at blocks), `StyleSheet` (plain
`string`), `GridType`, `Columns`, `ColumnWidth`, `GutterWidth`,
`GutterWidthPercentage`, `MaxWidth`, `MinWidth`, `Public`, `Description`,
`Folder`.

Get-only: `ThemeValues`, `StyleSheetExpression` (`ITextWithReferencedElements`).
Bulk write: `AddOrUpdateThemeValues(Dictionary<ThemeProperty, string>)`.

One documented caveat, and it is the API's own statement about transactional
visibility:

> "`StyleSheet` may contain some parts that are **generated from theme values**.
> In these cases, final CSS is **only computed when a transaction is completed
> or when the ESpace is saved**. Thus, this property may **return incomplete
> values transiently**."

So reading `StyleSheet` back immediately after writing theme values can show a
partial result *without anything having failed*. That is a documented property
of this one member. It sits alongside — but is not the same claim as — the
per-call transaction model in `odc-mentor-hardening.md`; the two are consistent,
and this is the only place the corpus itself talks about transaction-boundary
visibility.

`ITheme` also confirms an ODC-relevant fact by omission: a theme's structural
slots are **blocks**, not markup.

---

## 13. Types And Enumerations

*Pages under `docs/api/OutSystems.Model.Types.*.html` and
`…Enumerations.*.html`.*

`IType` / `ITypeSignature` is the base. `IBasicType` adds nothing but its
descriptor; `IListType` adds `ElementType` (`ITypeSignature`, get-only);
`IRecordType` is what entities and structures implement (which is why an
`IEntity` can be an aggregate source and a parameter's `DataType`);
`IIdentifierType` is the identifier form.

`ITypeSignature` carries `Kind` (`TypeKind`), `IsDisabled`, `UniqueId`, and two
`IsAssignableTo` overloads — the supported way to ask whether one type fits
another rather than comparing names.

**`TypeKind`** (a `[Flags]` enum): `Any`, `Basic`, `BinaryData`, `Boolean`,
`CSharp`, `Currency`, `Date`, `DateTime`, `Decimal`, `Email`, `File`, `Integer`,
`IntegerIdentifier`, `LambdaExpression`, `List`, `LongInteger`,
`LongIntegerIdentifier`, `None`, `Object`, `PhoneNumber`, `Record`, `Text`,
`TextIdentifier`, `Time`. Documented as describing "a type's kind at a high
level (e.g. `List` is a type kind, while `List<Integer>` is an actual type)" —
so `Kind` narrows, it does not identify.

The enumerations worth having in full because they are short and load-bearing:

| Enum | Values |
|---|---|
| `Data.EntityKind` | `Server`, `Client`, `Static` |
| `DeleteRule` | `Delete`, `Ignore`, `Protect` |
| `DataSourceFetch` | `AtStart`, `OnDemand` |
| `MessageType` | `Error`, `Info`, `Success`, `Warning` |
| `AssignMode` | `Roles`, `User` |
| `Validation` | `None`, `Server`, `ClientAndServer` |
| `InputType` | `Text`, `Email`, `Number`, `Search` |
| `ScreenTransition` | `Fade`, `SlideFromLeft`, `SlideFromRight`, `SlideFromTop`, `SlideFromBottom` |

`Culture` is a large CLDR-style enum (several hundred members) — look it up
rather than guessing a member name.

---

## 14. `ModelExtensions` — The Working Surface

*Page: `docs/api/OutSystems.Model.ModelExtensions.html`.*

A single static class of ~113 extension methods. It is the highest-value page in
the corpus for applied code, because several operations that look like they
should be properties are only reachable here. **`OutSystems.Model` must be in
the `imports` list for any of it to resolve.**

### 14a. Finding things

```csharp
T Named<T>(this IEnumerable<T> items, string name)     where T : IModelObject
T Labelled<T>(this IEnumerable<T> items, string label) where T : IModelObject
T At<T>(this IEnumerable<T> items, int horizontalPosition, int verticalPosition) where T : IFlowNode

IEnumerable<T> GetAllDescendantsOfType<T>(this IModelObject obj)  where T : IModelObject
IEnumerable<T> GetDirectChildrenOfType<T>(this IModelObject obj)  where T : IModelObject
T GetAncestorOfType<T>(this IModelObject obj)                     where T : IModelObject
T GetSelfOrAncestorOfType<T>(this IModelObject obj)               where T : IModelObject
```

`Named<T>` is the documented source of the `.Named("…")` idiom already in use in
`odc-mentor-hardening.md`. `GetAllDescendantsOfType<T>()` is the traversal
answer to the absent `AllWidgets` (§10b) — `screen.GetAllDescendantsOfType<IMobileWidget>()`
walks the whole subtree where `screen.Widgets` gives only the direct children.
`GetAncestorOfType<T>` is the same walk upward.

### 14b. Binding arguments — the only route

`Arguments` is `IEnumerable<IArgument>` and read-only everywhere it appears —
on `IExecuteServerActionNode`, `IExecuteClientActionNode`, `IDestinationNode`,
`IRefreshDataNode`, `ISQLNode`, `IJavaScriptNode`, `ISendEmailNode`,
`ICallAgentNode`, `ITriggerNode`, `IEventHandler`, `IEvent`,
`IUILifeCycleEvent`, `IMobileBlockInstanceWidget`, `ITimer` and more. There is
no `Add` and no `CreateArgument` on any of them.

The binding surface is here instead, overloaded once per hosting type:

```csharp
IArgument SetArgumentValue(this <host> obj, IInputParameterSignature parameter,
                           ExpressionDefinition value);
IExpression GetArgumentValue(this <host> obj, IInputParameterSignature parameter);
```

So passing a value to a called action, a screen destination, a block instance or
an event handler is always: get the parameter signature from the callee, then
`SetArgumentValue` on the caller. A reader who does not know this looks for an
`Add` on `Arguments`, does not find one, and concludes the binding is not
expressible.

### 14c. Placing and connecting flow nodes

```csharp
T ConnectedBelow<T>(this T node, IFlowNode referenceNode, int separation = 1773, bool snapToGrid = false)
T ConnectedAbove<T>(…)   T ConnectedToTheLeftOf<T>(…)   T ConnectedToTheRightOf<T>(…)
T Below<T>(…)  T Above<T>(…)  T ToTheLeftOf<T>(…)  T ToTheRightOf<T>(…)
T Into<T>(this T node, IConnector connector, bool snapToGrid = false)
T SnapToGrid<T>(this T node)
```

The `Connected…` family both positions **and** wires; the bare directional family
only positions. `Into` inserts a node onto an existing connector. These are what
keep a generated flow readable in Studio rather than a pile of nodes at the
origin.

### 14d. Widget surgery

```csharp
T EncloseIn<T>(this IWidget widget)                       where T : IWidget
T EncloseIn<T>(this IEnumerable<IWidget> widgets)         where T : IWidget
IWidget EncloseIn(this IWidget widget, Type containerType)
IWidget EncloseIn(this IEnumerable<IWidget> widgets, Type containerType)
IEnumerable<IWidget> TryGetContiguousWidgets(this IEnumerable<IWidget> widgets)
IPlaceholderContentWidget GetPlaceholderContent(this IMobileBlockInstanceWidget blockInstance,
                                                string placeholderName)
```

`EncloseIn` wraps existing widgets in a new container in place — the operation
that `odc-mentor-hardening.md` records taking three `applyModelApiCode` passes as
a manual create-delete-repoint sequence. **Inferred, and flagged as such:** the
single-call form looks like the direct route for that class of edit, but this
estate has not run it, so it is a candidate to try rather than a prescription.

`GetPlaceholderContent` is how a block instance's named placeholder is reached
for filling — there is no property for it.

### 14e. Values and other helpers

```csharp
void SetAttributeValue(this IRecord record, IEntityAttribute attribute, ExpressionDefinition value);
IAssignment CreateAssignment(this IAssignNode assign, ExpressionDefinition variable,
                             ExpressionDefinition value);
IRecordLiteralField SetField(this IRecordLiteralExpression expression, string fieldName,
                             ExpressionDefinition value);
IRecordLiteralField GetField(this IRecordLiteralExpression recordLiteral, string fieldName);
void SubstituteAndSimplify(this IExpression expr,
                           params (IObjectSignature variable, object value)[] substitutions);
bool IsConcrete(this Type type);        bool IsSignatureInterface(this Type type);
bool IsSignatureObject(this IModelObject obj);
```

`CreateAssignment(variable, value)` is the two-argument convenience over
`IAssignNode.CreateAssignment()` — one call instead of create-then-populate.
`IsConcrete` / `IsSignatureInterface` are the programmatic form of the
leaf-interface rule in §3c.

---

## 15. Agent-Experience Stamping

The model records which tool and which agent authored each object, and the
corpus is explicit about it.

`CreatedByTool` (enum) values: `AgentExperience`, `AppEditor`, `AppGenerator`,
`IntegrationBuilder`, `IntegrationStudio`, **`MentorWorkspace`**, `ODCStudio`,
**`ODCStudioMentor`**, `O11ToODCMigrationTool`, `ServiceStudio`,
`WorkflowEditor`, `Unspecified`.

The per-object fields, on `IEntity`, `IStructure`, `IServerAction`,
`IClientAction`, `IMobileScreen`, `IMobileBlock`, `IMobileFlow` and others:

| Field | Type |
|---|---|
| `CreatedByAgent` | `string` — **get-only** |
| `LastModifiedByAgent` | `string` — get-only |
| `ModifiedByAgents` | `IReadOnlyList<string>` — get-only |
| `CreatedByTool` / `LastModifiedByTool` | `CreatedByTool` — get-only |
| `ModifiedByTools` | `CreatedByTool` — get-only (a flags-style accumulation) |
| `CreatedBy` / `LastModifiedBy` | `string` — **settable** (the human/user field) |

`IESpace.GetWorkingAgentName()` is documented as: "Change-tracking metadata only
— the Agent Experience agent name (e.g. `Claude Code`) supplied when this espace
was loaded or created with `AgentExperience`. **Has no effect on model
behaviour**; objects stamped during this session carry this name in
`CreatedByAgent` / `LastModifiedByAgent` / `ModifiedByAgents` alongside the
`CreatedByTool` value." `GetWorkingTool()` returns the tool, and "must have been
set, as a parameter, during load or creation".

Why this earns space here: the agent fields are **get-only**, set from the
session's own load parameters, so applied code cannot forge them. That makes
them the one reliable read for telling a Mentor-authored element from a
hand-authored one when auditing what a run actually changed — and the
`ODCStudioMentor` / `MentorWorkspace` / `AgentExperience` values are how the
tools are told apart. Whether the MCP `mentor_start` surface stamps
`ODCStudioMentor` specifically is **not stated by the corpus** and has not been
measured by this estate; do not assume a particular value without reading it
back.

---

## 16. What The Corpus Does Not State

Recorded so the next round does not re-derive the gaps, and so nobody reads
silence as permission.

- **No behavioural or validation semantics.** The corpus says a property is
  settable; it never says the write will pass validation, will survive a save,
  or will mean what the name suggests at runtime. `IsValid` and
  `GetValidationMessages(…)` exist, but what any given rule *is* is not
  documented here.
- **No error contract.** Almost nothing documents what a call throws or returns
  on refusal. The leaf-interface rule in §3c is stated as a requirement with no
  stated failure mode. Reading the model back after a write is not optional.
- **No ODC-versus-O11 marking.** The API is one surface for both products; the
  Mobile/Web split in §1a is the closest thing to a product boundary and the
  corpus never labels it as one. Anything product-scoped comes from
  `odc-platform-guardrails.md` and the language-elements handbook, not here.
- **Nothing about Mentor.** No `applyModelApiCode`, no `imports` semantics, no
  tool vocabulary. That layer is `odc-mentor-hardening.md`'s, with its own
  provenance under `docs/adoption/`.
- **Nothing about the widget definitions themselves.** `CreateWidget` takes an
  `IWidgetDefinitionSignature`, but which definitions an ODC app has available,
  and what each one's parameters are, is tenant and library state. Use
  `odc-studio-widget-catalog.json` and `outsystems-ui-implementation-reference.json`
  for that, and the tenant `context_*` reads for what a specific app holds.
- **Version drift is real and unversioned here.** The published API surface
  moves with the platform release chain, and the corpus is regenerated on every
  push with no version marker on a page. Every entry above is the surface **as
  of the commit in the provenance header**, and nothing more.
