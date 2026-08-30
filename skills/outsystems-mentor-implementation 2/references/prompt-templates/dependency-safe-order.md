# Dependency-safe order format (prompt template)

- version: 1 (2026-08-06 — extracted unchanged from `SKILL.md` § "Dependency Order (Mentor-safe emission order)"; prompts-as-data, Enzyme adoption #3)
- owner: `outsystems-mentor-implementation/SKILL.md` § "Dependency Order (Mentor-safe emission order)"
- placeholders: `[Asset Kind]`, `[Block 1: prerequisites ...]`, `[Block 2: producer actions ...]`, `[Block N: dependent actions]`

Emit the skeleton below for each asset kind, replacing the bracketed placeholders with the actual ordered blocks.

## Template

```text
### [Asset Kind] Dependency-safe order
[Block 1: prerequisites ...]
[Block 2: producer actions ...]
[Block N: dependent actions]
```
