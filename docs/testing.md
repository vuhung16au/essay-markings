# Testing Guide

## Purpose

This document explains how to validate the project locally.

## Main testing layers

The project is usually checked through:

- backend startup checks
- frontend startup checks
- deterministic analysis checks
- sample-based verifier runs
- Python syntax checks

## Backend checks

Start the backend:

```bash
make run-backend
```

Useful endpoints:

- `GET http://localhost:8000/`
- `GET http://localhost:8000/health`
- `POST http://localhost:8000/api/grade-essay`
- `POST http://localhost:8000/api/analyze-deterministic`

## Frontend checks

Start the frontend:

```bash
make run-frontend
```

Then open:

- [http://localhost:8501](http://localhost:8501)

Frontend checks usually include:

- loading the app
- submitting a sample essay
- inspecting the result details
- checking export buttons

## Syntax checks

To catch obvious backend issues quickly:

```bash
./.venv/bin/python -m py_compile backend/core/schemas.py backend/core/prompt_builder.py backend/services/deterministic_scorer.py backend/services/hybrid_grader.py backend/services/llm_service.py backend/main.py
```

## Sample-based verification

Use:

```bash
./.venv/bin/python scripts/verify_sample_ranges.py
```

This submits the sample essays to the live backend and compares the results with:

- [data/sample_questions.json](../data/sample_questions.json)
- [data/sample_essays.json](../data/sample_essays.json)
- [data/expected_outputs.json](../data/expected_outputs.json)

## What the verifier checks

The verifier checks:

- total score difference
- category-level drift
- overall pass/fail status

Current tolerance settings are documented in [docs/calibration.md](./calibration.md).

## Troubleshooting

### Backend is not reachable

Check:

- backend process is running
- `BACKEND_PORT` is correct
- frontend and verifier point to the same backend

### Verifier fails after rubric changes

Check:

- whether the scorer changed intentionally
- whether [data/expected_outputs.json](../data/expected_outputs.json) still matches the intended rubric
- whether the change is deterministic logic drift or LLM variation

### LLM-related failures

Check:

- LM Studio is running
- the configured model is loaded
- the backend can reach `LLM_BASE_URL`

### Export issues

Check:

- `uv sync` was run
- Word/PDF dependencies are installed

## Recommended validation flow after scoring changes

1. Run syntax checks.
2. Start the backend.
3. Run the sample verifier.
4. Spot-check one strong sample and one weak sample in the frontend.
5. Confirm the report details still match the displayed scores.

## Related files

- [docs/calibration.md](./calibration.md)
- [docs/configuration.md](./configuration.md)
- [scripts/verify_sample_ranges.py](../scripts/verify_sample_ranges.py)
