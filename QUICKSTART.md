# Quickstart

## Prerequisites

- Python `3.13.9`
- `uv`
- LM Studio running locally
- A loaded model matching `LLM_MODEL_NAME` in [.env.local](./.env.local)

## 1. Create the environment

```bash
python3.13 --version
uv venv
uv sync
cp .env.example .env.local
```

`uv sync` installs both runtime and export dependencies, including Word/PDF report generation support.

## 2. Check configuration

Default local settings:

```env
LLM_BASE_URL=http://localhost:1234
LLM_MODEL_NAME=meta-llama-3.1-8b-instruct
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

If you change `BACKEND_PORT`, the frontend reads it from `.env.local`.

## 3. Start the backend

```bash
make run-backend
```

Expected endpoints:

- `GET http://localhost:8000/`
- `GET http://localhost:8000/health`
- `POST http://localhost:8000/api/grade-essay`
- `POST http://localhost:8000/api/analyze-deterministic`

## 4. Start the frontend

In another terminal:

```bash
make run-frontend
```

Then open [http://localhost:8501](http://localhost:8501).

## 5. Grade an essay

From the frontend you can:

- paste a custom essay question and response
- load a sample response from `data/sample_essays.json`
- submit the essay for grading
- inspect:
  - overall score
  - score breakdown
  - feedback
  - detailed per-category explanations
  - deduction reasons
  - suggestions for improvement

## 6. Export the report

When a result is available, the frontend shows an `Export Essay Report` section.

Available export formats:

- Markdown
- Word (`.docx`)
- PDF

Each report includes:

- essay question
- submitted essay
- overall score
- detailed breakdown by scoring category
- comments and feedback
- suggestions for improvement

Example Markdown export excerpt:

```md
# Essay Report

## Essay question
Some people believe that university students should be required to attend classes...

## Overall score
21 / 26

## Detailed breakdown of scores

| Category | Score |
| --- | --- |
| Content | 4 / 6 |
| Development, Structure & Coherence | 6 / 6 |
| Form | 2 / 2 |
| Grammar | 1 / 2 |

## Comments and feedback for each category

### Grammar (1 / 2)
Grammar was judged from sentence-level error patterns and control of structure.

Reasons for deducted marks:
- Detected grammar issues reduced the score.
```

## Troubleshooting

- If `uv` is missing, install it first and rerun `uv sync`.
- If the frontend cannot reach the API, make sure the backend is running and `BACKEND_PORT` matches `.env.local`.
- If the backend returns a `502`, LM Studio is likely unavailable or returned invalid/malformed output.
- If Word or PDF export buttons are disabled or missing, rerun `uv sync`.
- If scoring seems inconsistent, use `POST /api/analyze-deterministic` to inspect the deterministic baseline independently of the LLM.
