# BDD Framework (ODC) — the component contract

What the components actually define, so a generated test module can compile and
run the first time. Every claim below is labelled by how it is known:

- **MEASURED** — the component's own OML was extracted and walked as a graph.
- **DOC-PAGE** — taken from published documentation, not from the model.

Where the two disagreed, MEASURED won. Several rows here reverse a plausible
reading of the documentation, and each of those cost a real run to discover.

## The two Forge components

| Component | ID | What it gives you |
|---|---|---|
| `BDD Framework (ODC)` | 15745 | the blocks a test module is built from |
| `BDD Framework API (ODC)` | 15746 | the REST runner this skill calls |

Installing only `BDD Framework (ODC)` gives browser-run suites and **no** REST
runner (MEASURED). Neither component can be installed by Mentor or by this
skill; a human installs them from the Forge.

`Template_BDD Framework` 0.1.7 is an optional third component supplying a
clonable app skeleton. Its conventions are recorded below, but nothing here
requires it.

**`BDDFrameworkTestRunLib` is an External Logic (C#) library**, so it is
unreadable by construction rather than merely un-downloaded (MEASURED). It is
where execution actually happens. Named here so nobody hunts for an OML that
cannot exist.

## The blocks, and which are public

MEASURED from `BDD Framework (ODC)` 1.4.0.

| Block | Public? | Purpose |
|---|---|---|
| `FinalResult` | yes | aggregates the run and exposes the completion signal the runner watches |
| `BDDScenario` | yes | one scenario; holds the named placeholders |
| `BDDStep` | yes | one Given/When/Then step |
| `SetupOrTeardown` | yes | setup and teardown bodies |
| `BDDTag` | yes | attaches a tag to a scenario, for filtered runs |
| `LayoutBase` | yes | the suite screen's layout |
| `LayoutBaseDataDriven` | yes | the data-driven variant |
| `SecurityError` | yes | rendered when the token does not match |
| `StepPhase` | **no** | internal; must not be consumed |
| `ApplicationTitle` | **no** | internal; must not be consumed |

`StepPhase` and `ApplicationTitle` are not public and a generated module must
not reference either of them.

## `LayoutBase` already contains a `FinalResult`

MEASURED — the block's own widget tree:

```
LayoutBase → If (True)  → Title, MainContent, BDDFramework\FinalResult
                 (False) → If (False) → SecurityError
```

**A suite screen built on `LayoutBase` inherits a `FinalResult` and must never
add a second one.** A second makes the screen render two result widgets, only
one of which tracks the run, and the REST runner then answers
`Could not find tests in the screen`. Measured, and measured again by removing
the duplicate and watching the same call turn green.

`FinalResult` must still be reachable as a **dependency** of the test module,
because `LayoutBase` renders it — a reference the module needs, not a widget the
generator places. A module missing that dependency does not fail fast: the
runner drives the screen and waits out `DefaultExecutionTimeout`, shipped at
180000 ms.

**Corrected error signatures** (MEASURED), because these two read alike and mean
opposite things:

| Symptom | Cause |
|---|---|
| `Could not find tests in the screen` | a **duplicate** `FinalResult` |
| timeout after `DefaultExecutionTimeout` (180000 ms) | a genuinely **missing** one |

The runner drives the suite by clicking buttons and watches `finalResultButtonId`
to detect completion.

## Mandatory inputs

MEASURED.

| Block | Mandatory input | Notes |
|---|---|---|
| `LayoutBase` | `AuthToken` | the suite screen passes its own `AuthToken` screen input here; that chain, not the URL alone, is the gate |
| `LayoutBaseDataDriven` | `AuthToken`, `ScenarioCount` | the data-driven variant needs the count up front |
| `FinalResult` | `IsDataDriven` | |
| `BDDStep` | *(none)* | `BDDStep` has **zero input parameters** |

## The `BDDScenario` placeholders

MEASURED. **Fill these placeholders; do not replace them.**

| Placeholder | Holds |
|---|---|
| `ScenarioIdentifier` | the scenario's stable id |
| `ScenarioDescription` | the human sentence |
| `TagsPlaceholder` | one or more `BDDTag` blocks |
| `SetupPlaceholder` | a `SetupOrTeardown` |
| `GivenPlaceholder` | a `BDDStep` |
| `WhenPlaceholder` | a `BDDStep` |
| `ThenPlaceholder` | a `BDDStep` |
| `TeardownPlaceholder` | a `SetupOrTeardown` |

`BDDStep` carries its own `StepDescription` placeholder for the step sentence,
and `BDDTag` carries a `Tag` placeholder. A step with an empty
`StepDescription` is not a test, however correct its logic.

## Events

MEASURED. `BDDStep` defines exactly one event, `NotifyRunStepLogic`, and it is
**mandatory**. Every step's logic hangs off that event.

## The handler convention

DOC-PAGE, confirmed against `Template_BDD Framework` 0.1.7 (MEASURED). Handlers
are named so alphabetical order matches execution order:

| Handler | Runs |
|---|---|
| `a_Setup` | first |
| `b_Given` | |
| `c_When` | |
| `d_Then` | |
| `e_Teardown` | last |

`c_When`, and only `c_When`, carries an `AllExceptions` handler calling
`AssertFail` with the exception message, so an unexpected exception is a failed
scenario rather than a crashed run.

## The assertion surface

MEASURED, public: `Assert`, `AssertTrue`, `AssertFalse`, `AssertValue`,
`AssertFail`, plus `ExceptionHandler`.

## Two platform limits

MEASURED. Both are structural and neither produces a helpful error:

- A `BDDStep` may **not** be iterated by a `ListRecords` inside a `BDDScenario`.
  Data-driven iteration is a `List` wrapping the whole scenario block — outside
  the scenario, never nested inside a step.
- A data-driven scenario may **not** share a screen with a simple one.

## Two ODC preconditions the upstream architecture assumes

- **A template-cloned ODC app has no `MainFlow`.** An app cloned from
  `Template_BDD Framework` has `BusinessValuePerceptionTags`, `Common` and
  `ScreenTemplates` (MEASURED). Resolve or create the target flow before
  generating; never assume one by name.
- **`FinalResult` belongs in the app's dependencies**, per the section above.

## Three upstream names that do not exist in the ODC component

MEASURED. An agent given any of these builds something that cannot compile.
Each is named here only so it can be ruled out:

| The upstream skill says | The ODC component actually defines |
|---|---|
| `SetupOrTeardownStep` | `SetupOrTeardown` — there is no element called `SetupOrTeardownStep`, the `Step` suffix does not exist |
| drive the step from its `On Notify` handler | one mandatory block event, `NotifyRunStepLogic` — `On Notify` is not the name here |
| bind the step's `Destination` | nothing to bind: `BDDStep` has zero input parameters and no `Destination` property |

Also from upstream, and **wrong for ODC**: the instruction to make the suite
screen anonymously accessible. ODC does the opposite — the screen is gated by an
`AuthToken` that the API's bearer token must match. Carrying that instruction
over would fail *and* publish the suite screen.

## The toolchain firewall

The architecture is adopted from `OutSystems/Solutions-Discovery`'s
`solutions-outsystems-bdd-test-oml`. **Its toolchain is not.** That skill
mandates local OML editing via `oml-prism`, which collides with this estate's
rule that the model stays server-side. Nothing in this skill downloads, exports
or edits an OML file locally, and a test keeps it that way.

The O11 runner path `/BDDFramework/rest/v1/` does **not** resolve on ODC and must
never be used; the ODC path is in `runner-contract.md`.
