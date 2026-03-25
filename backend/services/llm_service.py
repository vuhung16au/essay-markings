"""Placeholder LLM service for future integration with LM Studio."""

from openai import OpenAI


def build_client(base_url: str, api_key: str = "lm-studio") -> OpenAI:
    return OpenAI(base_url=f"{base_url.rstrip('/')}/v1", api_key=api_key)


def grade_essay(question: str, essay: str) -> dict:
    raise NotImplementedError(
        "Phase 1 scaffold complete. LLM grading will be implemented in a later phase."
    )
