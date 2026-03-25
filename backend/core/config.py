"""Environment loading utilities for the backend."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]


def _load_environment() -> None:
    for candidate in (".env.local", ".env"):
        env_path = ROOT_DIR / candidate
        if env_path.exists():
            load_dotenv(env_path, override=False)


@dataclass(frozen=True)
class Settings:
    LLM_BASE_URL: str
    LLM_MODEL_NAME: str
    BACKEND_HOST: str
    BACKEND_PORT: int
    FRONTEND_PORT: int


def get_settings() -> Settings:
    _load_environment()
    return Settings(
        LLM_BASE_URL=os.getenv("LLM_BASE_URL", "http://localhost:1234"),
        LLM_MODEL_NAME=os.getenv("LLM_MODEL_NAME", "meta-llama-3.1-8b-instruct"),
        BACKEND_HOST=os.getenv("BACKEND_HOST", "0.0.0.0"),
        BACKEND_PORT=int(os.getenv("BACKEND_PORT", "8000")),
        FRONTEND_PORT=int(os.getenv("FRONTEND_PORT", "8501")),
    )


settings = get_settings()
