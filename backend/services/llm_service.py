"""LLM service for grading essays with a local LM Studio server."""

from __future__ import annotations

import json
from json import JSONDecodeError

from openai import OpenAI

from core.config import settings
from core.prompt_builder import build_pte_prompt
from core.schemas import EssayResponse


class LLMServiceError(Exception):
    """Raised when the local LLM cannot provide a valid grading response."""


def build_client(base_url: str, api_key: str = "lm-studio") -> OpenAI:
    return OpenAI(base_url=f"{base_url.rstrip('/')}/v1", api_key=api_key)


client = build_client(settings.LLM_BASE_URL)


def _extract_json_payload(raw_content: str) -> dict:
    """Parse JSON from the model response, tolerating wrapper text when possible."""

    cleaned = raw_content.strip()
    try:
        return json.loads(cleaned)
    except JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LLMServiceError("LLM response did not contain a valid JSON object.")

        try:
            return json.loads(cleaned[start : end + 1])
        except JSONDecodeError as exc:
            raise LLMServiceError("LLM returned malformed JSON.") from exc


def _request_grading(question: str, essay: str) -> dict:
    prompt = build_pte_prompt(question, essay)

    try:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
    except Exception as exc:
        raise LLMServiceError(f"Failed to contact the local LLM server: {exc}") from exc

    message = response.choices[0].message.content if response.choices else None
    if not message:
        raise LLMServiceError("LLM response was empty.")

    return _extract_json_payload(message)


async def grade_essay(question: str, essay: str) -> dict:
    """Call the local LLM and return a validated grading payload."""

    last_error: LLMServiceError | None = None

    for _ in range(2):
        try:
            payload = _request_grading(question, essay)
            validated = EssayResponse.model_validate(payload)
            return validated.model_dump()
        except LLMServiceError as exc:
            last_error = exc
        except Exception as exc:
            raise LLMServiceError(f"Failed to validate the LLM grading response: {exc}") from exc

    if last_error is not None:
        raise last_error

    raise LLMServiceError("Unknown grading failure.")
