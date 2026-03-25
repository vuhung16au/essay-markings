# Coding Style Policy

## Goals

- Keep code readable and maintainable.
- Prefer explicit logic over clever shortcuts.
- Keep scoring behavior understandable and auditable.

## Rules

- Match existing project structure and naming patterns.
- Keep functions small when practical.
- Use clear names for rubric and scoring logic.
- Prefer deterministic, testable logic for numeric scoring.
- Avoid introducing unnecessary abstraction.
- Keep comments short and useful.
- Update docs when behavior changes.

## Scoring-specific guidance

- Keep rubric logic easy to trace.
- Avoid hidden score manipulation.
- Put scoring rules close to the category they affect.
- Keep user-facing wording separate from internal heuristics when possible.
