# PTE Essay Marker

A PTE Academic essay grading application with a Streamlit frontend, a FastAPI backend, and a local LM Studio integration through an OpenAI-compatible API.

## Current implementation

The repository now includes:

- a working FastAPI backend with `POST /api/grade-essay`
- an LM Studio service layer that builds prompts, calls the local model, and validates JSON responses
- a Streamlit frontend that submits essays to the backend and renders the returned scores and feedback
- sample questions, essays, and expected outputs for local testing
- project setup files for `uv`, environment variables, and common development commands

## How it works

1. The frontend collects the essay prompt and essay text.
2. The frontend sends a JSON request to the backend.
3. The backend builds a PTE-specific system and user prompt.
4. The local LM Studio server returns a JSON grading response.
5. The backend validates the response with Pydantic.
6. The frontend shows the score breakdown, feedback, strengths, and improvements.

## Tech stack

- Python `3.13.9`
- `streamlit==1.33.0`
- `fastapi==0.110.1`
- `uvicorn==0.29.0`
- `openai==1.16.2`
- `pydantic==2.12.5`
- `python-dotenv==1.0.1`

## Project layout

```text
backend/    FastAPI app, schemas, prompt builder, settings, and LM Studio service
frontend/   Streamlit UI and CSS
data/       Sample questions, essays, and expected outputs
docs/       Architecture and API documentation
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

## Local LLM configuration

The backend expects LM Studio to be available at:

- `LLM_BASE_URL=http://localhost:1234`
- `LLM_MODEL_NAME=meta-llama-3.1-8b-instruct`

The app assumes LM Studio exposes an OpenAI-compatible `/v1` API.

## Notes

- `uv.lock` is ignored in this project because the FRD explicitly requested it.
- The backend and frontend are wired together, but successful live grading still depends on local dependencies being installed and LM Studio running.

See [QUICKSTART.md](QUICKSTART.md), [docs/architecture.md](docs/architecture.md), and [docs/api_specs.md](docs/api_specs.md) for more detail.
