# Quickstart

## Prerequisites

- Python 3.12.2
- `uv`
- LM Studio running locally for later phases

## Setup

```bash
uv venv
uv sync
cp .env.example .env.local
```

## Development commands

```bash
make run-backend
make run-frontend
```

## Notes

- Phase 1 focuses on scaffolding and sample data only.
- Backend/frontend modules are placeholders until the grading flow is implemented.
- `uv.lock` is intentionally not committed because the FRD asks for it to be ignored.
