# Paste-safe response format (prompt template)

- version: 1 (2026-08-06 — extracted unchanged from `SKILL.md` § "Paste-safe response format (required)"; prompts-as-data, Enzyme adoption #3)
- owner: `outsystems-mentor-implementation/SKILL.md` § "Paste-safe response format (required)"
- placeholders: `[list every referenced existing item with: Already exists (use existing)]`, `[list entities, structures, site properties, REST APIs, events/timers, screen blocks, etc.]`, `[one block per entity]`, `[one block per structure]`, `[site properties]`, `[Consumed/Exposed REST, callbacks]`, `[events, timers, wake actions]`, `[all producers first, then dependents]`, `[blocks/screens that call the above actions]`

Emit the skeleton below verbatim as the section scaffold, replacing each bracketed placeholder with the actual blocks. Do not reorder, rename, or drop sections.

## Template

```text
### 1) Dependency inventory
#### 1.1 Already exists
[list every referenced existing item with: Already exists (use existing)]

#### 1.2 To create (none yet)
[list entities, structures, site properties, REST APIs, events/timers, screen blocks, etc.]

### 2) Data model blocks
#### 2.1 Entities
[one block per entity]

#### 2.2 Structures
[one block per structure]

### 3) Platform configuration blocks
[site properties]

### 4) External integration blocks
[Consumed/Exposed REST, callbacks]

### 5) Runtime orchestration blocks
[events, timers, wake actions]

### 6) Server action blocks (dependency sorted)
[all producers first, then dependents]

### 7) Consumer/UI blocks
[blocks/screens that call the above actions]
```
