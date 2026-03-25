# PTE Essay Marker

A local PTE Academic essay grading app with a Streamlit frontend, a FastAPI backend, and a hybrid scoring pipeline that combines deterministic checks with LLM-based feedback.

## What the project does

The app lets a user:

- paste an essay prompt and essay response
- submit the essay to a local grading API
- view a full score breakdown across PTE-style categories
- inspect transparent per-category detail and deduction reasons
- export the essay report as Markdown, Word, or PDF

## Current scoring approach

The codebase no longer relies on pure LLM scoring.

Instead, the main grading endpoint uses a hybrid strategy:

1. A deterministic scorer checks measurable features such as:
   - prompt relevance
   - word count and gross form issues
   - token-level spelling
   - sentence-level grammar signals
   - paragraphing, transitions, and discourse structure
   - lexical diversity and academic word usage
2. The LLM generates qualitative grading output and feedback.
3. A hybrid merger applies Pearson-style gates and bounded score merging.
4. The frontend renders:
   - score breakdown
   - feedback
   - good points
   - improvements
   - detailed category analysis with deduction reasons

The scoring rubric now follows the direct Pearson-style essay bands documented in [docs/pte_essay_rubric.md](./docs/pte_essay_rubric.md):

- Content `0-6`
- Development, Structure & Coherence `1-6` in normal scoring, with `0` possible through gating
- Form `0-2`
- Grammar `0-2`
- Linguistic Range `0-6`
- Spelling `0-2`
- Vocabulary `0-2`

## Main features

- FastAPI backend with:
  - `GET /`
  - `GET /health`
  - `POST /api/grade-essay`
  - `POST /api/analyze-deterministic`
- Streamlit frontend with:
  - dark/light theme toggle
  - sample essay loader
  - detailed results section
  - exportable essay reports
- Pearson-aligned deterministic baseline with:
  - official form thresholds
  - content/form gating
  - direct Pearson-style band scoring for content, development, and linguistic range
  - vendored SCOWL-based dictionary in [data/words.txt](./data/words.txt)
  - support for accepted US/UK/AU/CA spellings with mixed-convention detection

## Tech stack

- Python `3.13.9`
- `streamlit==1.33.0`
- `fastapi==0.110.1`
- `uvicorn==0.29.0`
- `openai==1.16.2`
- `pydantic==2.12.5`
- `python-dotenv==1.0.1`
- `python-docx==1.1.2`
- `reportlab==4.2.0`

## Project layout

```text
backend/    FastAPI app, schemas, prompt builder, deterministic scorer, hybrid grader, LLM service
frontend/   Streamlit UI, styling, report export helpers
data/       Sample questions, essays, expected outputs, vendored word list
docs/       Architecture, API, and scoring documentation
```

## Setup

```bash
python3.13 --version
uv venv
uv sync
cp .env.example .env.local
make run-backend
make run-frontend
```

Then open [http://localhost:8501](http://localhost:8501).

## Local LLM configuration

Default local settings:

- `LLM_BASE_URL=http://localhost:1234`
- `LLM_MODEL_NAME=meta-llama-3.1-8b-instruct`
- `BACKEND_HOST=0.0.0.0`
- `BACKEND_PORT=8000`
- `FRONTEND_PORT=8501`

The backend expects LM Studio to expose an OpenAI-compatible `/v1` API.

## Documentation

- [QUICKSTART.md](./QUICKSTART.md)
- [docs/architecture.md](./docs/architecture.md)
- [docs/api_specs.md](./docs/api_specs.md)
- [docs/scoring.md](./docs/scoring.md)
- [data/words.SOURCE.md](./data/words.SOURCE.md)

## Sample result snippet

The frontend results area now shows a score summary plus a detailed explanation for each criterion.

Example:

```text
Overall score: 21 / 26

Content: 4 / 6
Development, Structure & Coherence: 6 / 6
Form: 2 / 2
Grammar: 1 / 2
Linguistic Range: 5 / 6
Spelling: 2 / 2
Vocabulary: 1 / 2

Detail -> Grammar
- Analysis: Grammar was judged from sentence-level error patterns and control of structure.
- Why marks were deducted: Detected grammar issues reduced the score.
```

## Notes

- The frontend export buttons for Word and PDF require the installed dependencies from `uv sync`.
- The deterministic scorer is intentionally more stable than the LLM and acts as the scoring anchor.
- The LLM is still used for richer judgment and narrative feedback, but final numeric scores are bounded in code.
- Sample fixtures in [data/expected_outputs.json](./data/expected_outputs.json) now reflect the current direct-band rubric implementation rather than the older mapped-band calibration.
