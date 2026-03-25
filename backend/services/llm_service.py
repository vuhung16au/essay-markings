"""LLM service for grading essays with a local LM Studio server."""

from __future__ import annotations

import json
from json import JSONDecodeError

import httpx
from openai import OpenAI

from core.config import settings
from core.prompt_builder import build_pte_prompt
from core.schemas import EssayResponse


class LLMServiceError(Exception):
    """Raised when the local LLM cannot provide a valid grading response."""


def build_client(base_url: str, api_key: str = "lm-studio") -> OpenAI:
    return OpenAI(base_url=f"{base_url.rstrip('/')}/v1", api_key=api_key)


def _get_client() -> OpenAI | None:
    """Build the OpenAI client lazily so server startup doesn't fail on import."""

    try:
        return build_client(settings.LLM_BASE_URL)
    except TypeError:
        # Older OpenAI SDK versions can be incompatible with newer httpx releases.
        return None


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


def _normalize_scores(payload: dict) -> dict:
    """Coerce model score values into the integer schema expected by the API."""

    scores = payload.get("scores")
    if not isinstance(scores, dict):
        return payload

    for item in scores.values():
        if not isinstance(item, dict):
            continue

        value = item.get("score")
        if isinstance(value, float):
            item["score"] = int(round(value))

        maximum = item.get("max")
        if isinstance(maximum, float):
            item["max"] = int(round(maximum))

    return payload


def _normalize_feedback(payload: dict) -> dict:
    """Coerce feedback fields into strings when the model returns lists or other types."""

    feedback = payload.get("feedback")
    if not isinstance(feedback, dict):
        return payload

    for key in ("form", "grammar", "spelling"):
        value = feedback.get(key)
        if isinstance(value, list):
            feedback[key] = " ".join(str(item).strip() for item in value if str(item).strip())
        elif value is None:
            feedback[key] = ""
        elif not isinstance(value, str):
            feedback[key] = str(value)

    return payload


def _normalize_string_list(values: object) -> list[str]:
    """Coerce arbitrary list-like model output into a compact list of strings."""

    if isinstance(values, list):
        cleaned = [str(item).strip() for item in values if str(item).strip()]
        return cleaned[:5]
    if values is None:
        return []

    value = str(values).strip()
    return [value] if value else []


def _normalize_lists(payload: dict) -> dict:
    """Normalize feedback and bullet-point collections to the API schema."""

    payload = _normalize_feedback(payload)
    payload["good_points"] = _normalize_string_list(payload.get("good_points"))
    payload["improvements"] = _normalize_string_list(payload.get("improvements"))
    return payload


def _request_grading(question: str, essay: str) -> dict:
    prompt = build_pte_prompt(question, essay)
    client = _get_client()

    if client is not None:
        try:
            response = client.chat.completions.create(
                model=settings.LLM_MODEL_NAME,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]},
                ],
                temperature=0.3,
                response_format={"type": "text"},
            )
        except Exception as exc:
            raise LLMServiceError(f"Failed to contact the local LLM server: {exc}") from exc

        message = response.choices[0].message.content if response.choices else None
        if not message:
            raise LLMServiceError("LLM response was empty.")

        return _extract_json_payload(message)

    try:
        response = httpx.post(
            f"{settings.LLM_BASE_URL.rstrip('/')}/v1/chat/completions",
            json={
                "model": settings.LLM_MODEL_NAME,
                "messages": [
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": prompt["user"]},
                ],
                "temperature": 0.3,
                "response_format": {"type": "text"},
            },
            headers={"Content-Type": "application/json", "Authorization": "Bearer lm-studio"},
            timeout=90.0,
        )
        response.raise_for_status()
    except Exception as exc:
        raise LLMServiceError(f"Failed to contact the local LLM server: {exc}") from exc

    try:
        payload = response.json()
        message = payload["choices"][0]["message"]["content"]
    except Exception as exc:
        raise LLMServiceError("LLM response format was not recognized.") from exc

    if not message:
        raise LLMServiceError("LLM response was empty.")

    return _extract_json_payload(message)


async def grade_essay(question: str, essay: str) -> dict:
    """Call the local LLM and return a validated grading payload."""

    last_error: LLMServiceError | None = None

    for _ in range(2):
        try:
            payload = _request_grading(question, essay)
            payload = _normalize_scores(payload)
            payload = _normalize_lists(payload)
            validated = EssayResponse.model_validate(payload)
            return validated.model_dump()
        except LLMServiceError as exc:
            last_error = exc
        except Exception as exc:
            raise LLMServiceError(f"Failed to validate the LLM grading response: {exc}") from exc

    if last_error is not None:
        raise last_error

    raise LLMServiceError("Unknown grading failure.")
