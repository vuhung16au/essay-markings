# PTE Essay Marker

A scaffolded PTE Academic essay grading project with a Streamlit frontend, FastAPI backend, and local-LLM integration planned for later phases.

## Current status

Phase 1 is in place:

- project structure created
- Python/`uv` project metadata added
- environment template and ignore rules added
- realistic sample questions, essays, and expected outputs added
- backend/frontend placeholder modules created for follow-up phases

## Planned architecture

1. Streamlit collects the essay prompt and essay text.
2. FastAPI receives the grading request.
3. Backend builds a PTE-specific prompt.
4. A local LM Studio model produces structured JSON output.
5. The frontend renders scores and feedback.

## Quick start

```bash
uv venv
uv sync
make run-backend
make run-frontend
```

## Repository layout

```text
docs/       Documentation and architecture notes
data/       Sample questions, essays, and expected grading JSON
frontend/   Streamlit app and static assets
backend/    FastAPI app, schemas, config, and services
```

See [QUICKSTART.md](QUICKSTART.md) for the intended setup flow.
