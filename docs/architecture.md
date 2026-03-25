# Architecture

## Overview

The application follows a simple request-response path:

1. Streamlit collects a question and essay from the user.
2. FastAPI accepts a grading request.
3. The backend builds a prompt for the local LLM.
4. LM Studio returns grading JSON.
5. The backend validates the result and sends it back to the frontend.

## Diagram

```mermaid
graph TD
    User([User]) -->|Inputs Essay & Question| UI[Frontend: Streamlit\napp.py]
    UI -->|POST JSON Request| API[Backend: FastAPI\nmain.py]

    subgraph Local Environment
        API -->|Format & Validate Prompt| Core[Backend Core\nprompt_builder.py]
        Core -->|OpenAI API Call\nlocalhost:1234/v1| LLM[(LM Studio\nLocal LLM Server)]
        LLM -->|Returns JSON Scoring| Core
    end

    Core -->|Parses JSON via Pydantic| API
    API -->|Returns HTTP 200| UI
    UI -->|Renders Scores & Feedback| User
```

## Phase 1 status

This repository currently contains the scaffolding, sample data, and placeholder modules required to support later implementation phases.
