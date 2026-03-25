# Calibration Guide

## Purpose

This document explains how score calibration works in this project, how the sample essays are used, what the benchmark expectations mean, and how to recalibrate the grader safely.

## Calibration goals

The calibration process aims to keep the grader:

- reasonably close to the project’s rubric benchmarks
- stable across repeated runs
- strict enough on weak essays
- consistent with the direct Pearson-style essay rubric used by the repo

Calibration does not try to make every run identical. Because the system still uses an LLM in the hybrid pipeline, small variation is expected.

## Sample essay benchmark set

The repo includes a fixed reference set:

- [data/sample_questions.json](../data/sample_questions.json)
- [data/sample_essays.json](../data/sample_essays.json)
- [data/expected_outputs.json](../data/expected_outputs.json)

These samples cover a range of quality levels:

- excellent
- good
- average
- poor
- very poor

The benchmark set is used to check whether scoring stays within an acceptable range after code or prompt changes.

## Verifier script

Use:

```bash
./.venv/bin/python scripts/verify_sample_ranges.py
```

The verifier submits the sample essays to the live backend and compares the result with [data/expected_outputs.json](../data/expected_outputs.json).

## Current tolerance rules

The current verifier uses:

- per-score tolerance: `1`
- total-score tolerance: `3`

This means:

- a category can differ by `1` point and still be acceptable
- the total score can differ by up to `3` points and still pass

These tolerances exist because the hybrid grader still includes LLM judgment.

## What counts as a calibration problem

Recalibration is usually needed when one or more of these happen:

- excellent essays are clearly under-scored
- poor or very poor essays are clearly over-scored
- one category repeatedly swings outside tolerance
- a rubric change makes the benchmark fixture out of date
- the verifier fails overall

Repeated low-end generosity is especially important to watch.

## Safe recalibration process

Use this order when recalibrating:

1. Check whether the issue comes from the deterministic baseline or the hybrid merge.
2. Compare the live result with the benchmark fixture.
3. Identify which categories drifted.
4. Change the smallest scoring rule or prompt section that addresses the problem.
5. Re-run the full sample verifier.
6. Only update [data/expected_outputs.json](../data/expected_outputs.json) when the rubric or intended scoring standard has genuinely changed.

## What to tune first

Prefer these tuning levels in order:

1. Deterministic rubric logic in [backend/services/deterministic_scorer.py](../backend/services/deterministic_scorer.py)
2. Hybrid merge rules in [backend/services/hybrid_grader.py](../backend/services/hybrid_grader.py)
3. Prompt wording in [backend/core/prompt_builder.py](../backend/core/prompt_builder.py)
4. Expected outputs in [data/expected_outputs.json](../data/expected_outputs.json)

Do not start by changing the benchmark fixture unless the underlying rubric reference has changed.

## When to update expected outputs

Update [data/expected_outputs.json](../data/expected_outputs.json) only when:

- the scoring rubric changed intentionally
- official scoring guidance changed
- the deterministic baseline was intentionally redesigned
- the benchmark file is clearly based on an older scoring model

Do not update the fixture just to hide random drift.

## Common calibration patterns

### Poor essays are too generous

Usually tune:

- grammar-linked caps
- development/coherence caps
- linguistic range caps
- content penalties for shallow support

### Strong essays are too low

Usually tune:

- paragraph/discourse recognition
- support/example recognition
- stance detection
- overly harsh hybrid clamps

### Form score changed unexpectedly

Check:

- word count against the official bands
- all-caps detection
- punctuation and bullet-point checks

## Calibration checklist

Before merging a scoring change:

- run the verifier
- inspect category-level drift, not only totals
- spot-check at least one strong and one weak sample
- confirm the docs still match the implemented rubric
- confirm user-facing feedback still makes sense after the score change

## Related files

- [docs/scoring.md](./scoring.md)
- [docs/pte_essay_rubric.md](./pte_essay_rubric.md)
- [docs/testing.md](./testing.md)
- [backend/services/deterministic_scorer.py](../backend/services/deterministic_scorer.py)
- [backend/services/hybrid_grader.py](../backend/services/hybrid_grader.py)
