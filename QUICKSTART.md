# Quickstart

## Prerequisites

- Python `3.13.9`
- `uv`
- LM Studio running locally
- A loaded model named `meta-llama-3.1-8b-instruct` or a matching local override in `.env.local`

## 1. Create the environment

```bash
python3.13 --version
uv venv
uv sync
cp .env.example .env.local
```

## 2. Check configuration

Default local settings:

```env
LLM_BASE_URL=http://localhost:1234
LLM_MODEL_NAME=meta-llama-3.1-8b-instruct
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

If you change `BACKEND_PORT`, the frontend will pick it up from `.env.local`.

## 3. Start the backend

```bash
make run-backend
```

Expected endpoints:

- `GET http://localhost:8000/`
- `GET http://localhost:8000/health`
- `POST http://localhost:8000/api/grade-essay`

## 4. Start the frontend

In another terminal:

```bash
make run-frontend
```

Then open `http://localhost:8501`.

## 5. Test with sample data

The frontend can preload the sample essays from `data/sample_essays.json`. Use the "Load a sample response" dropdown to quickly exercise the UI.

## Troubleshooting

- If `uv` is missing, install it first and rerun `uv sync`.
- If `uv sync` recreates `.venv`, that is expected when the existing environment is not using Python `3.13.9`.
- If the frontend cannot reach the API, make sure the backend is running and `BACKEND_PORT` matches in `.env.local`.
- If the backend returns a `502`, LM Studio is likely unavailable or returned malformed JSON.
- If imports fail on startup, dependencies have probably not been installed yet.
