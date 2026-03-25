# Calibration Policy

## Goals

- Keep grading stable.
- Keep scoring aligned with the repo rubric.
- Avoid hidden drift after prompt or heuristic changes.

## Rules

- Use the sample essay benchmark set before and after scoring changes.
- Prefer deterministic fixes before broad prompt changes.
- Do not update expected outputs just to hide random drift.
- Track strong and weak essay behavior separately.
- Treat repeated low-end generosity as a priority issue.

## Required checks

- Run the sample verifier after scoring changes.
- Inspect category-level drift, not only total scores.
- Ensure user-facing feedback still matches final scores.
