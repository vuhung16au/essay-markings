# Configuration Guide

## Purpose

This document explains runtime configuration for the project.

## Main config file

The project uses:

- [.env.local](../.env.local)

If it does not exist yet, copy:

```bash
cp .env.example .env.local
```

## Core settings

Common settings include:

```env
LLM_BASE_URL=http://localhost:1234
LLM_MODEL_NAME=meta-llama-3.1-8b-instruct
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501
PANDOC_PATH=/opt/homebrew/bin/pandoc
PDF_ENGINE_PATH=
```

## LLM requirements

The backend expects:

- LM Studio running locally
- an OpenAI-compatible API exposed at the configured base URL
- a loaded model matching `LLM_MODEL_NAME`

## Port behavior

- backend default: `8000`
- frontend default: `8501`
- LM Studio default in this repo: `1234`

If you change backend settings, make sure the frontend reads the same values.

## Runtime assumptions

The current project assumes:

- local-only development usage
- a locally hosted LLM
- Python `3.13.9`
- dependencies installed through `uv`

## Backend configuration behavior

Backend config is loaded through:

- [backend/core/config.py](../backend/core/config.py)

This is the main source of typed application settings.

## Frontend configuration behavior

The frontend reads runtime settings so it can call the backend on the expected host and port.

It also reads optional export-tool settings:

- `PANDOC_PATH`
  - explicit path to the `pandoc` binary
- `PDF_ENGINE_PATH`
  - explicit path to a preferred PDF engine such as `wkhtmltopdf` or `weasyprint`

If these are unset, the frontend falls back to auto-detection from common system paths.

Main frontend entry:

- [frontend/app.py](../frontend/app.py)

## When to update config docs

Update this document when:

- environment variable names change
- default ports change
- model assumptions change
- local deployment expectations change

## Related files

- [README.md](../README.md)
- [QUICKSTART.md](../QUICKSTART.md)
- [backend/core/config.py](../backend/core/config.py)
