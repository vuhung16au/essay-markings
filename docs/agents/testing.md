# Testing Policy

## Goals

- Catch regressions early.
- Keep the grading path and docs in sync.

## Rules

- Run syntax checks after backend changes.
- Run the sample verifier after scoring changes.
- Check backend startup and health.
- Spot-check the frontend after UI or report changes.
- Recheck docs when behavior changes.

## Priority

- scoring correctness
- benchmark stability
- user-facing consistency
