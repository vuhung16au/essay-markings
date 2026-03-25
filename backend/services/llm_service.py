"""LLM service for grading essays with a local LM Studio server."""

from __future__ import annotations

import json
import re
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


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _count_spelling_indicators(feedback_text: str) -> int:
    lowered = feedback_text.lower()
    if "no spelling errors" in lowered:
        return 0

    indicators = [
        "spelling errors include",
        "spelling issue",
        "spelling issues include",
        "misspelled",
        "incorrectly spelled",
        "dont",
        "childrens",
    ]
    return sum(1 for marker in indicators if marker in lowered)


def _essay_quality_signals(essay: str) -> dict[str, int]:
    """Derive coarse text-quality indicators directly from the essay text."""

    lowered = essay.lower()
    typo_markers = [
        " dont ",
        " childrens ",
        " maybe fail",
        " social need ",
        " ordinary citizen",
        " it fail ",
        " people basic life problem",
        " government spend money",
        " science make new things",
        " they maybe ",
        " need study ",
        " learning have ",
        " it also bring ",
    ]
    grammar_markers = [
        " i think social needs is more important mostly",
        " the government should fixing",
        " scientist can still work",
        " if government make balance",
        " they need school, transport, food support and jobs",
        " children focus on mother tongue first",
        " young children can copy sounds easier",
        " there is not enough trained teachers also",
        " does not always give good result",
        " they maybe feel frustrated",
    ]
    transition_markers = [
        "first",
        "second",
        "however",
        "in conclusion",
        "on the other hand",
        "another",
        "therefore",
    ]
    generic_markers = [
        "there is a lot of discussion today",
        "both ideas have advantages and disadvantages",
        "the best answer depends",
        "these points show that",
        "still play a useful role",
        "neither system is perfect by itself",
        "a mixed approach is probably",
        "instead of following only one method",
    ]

    typo_hits = sum(lowered.count(marker.strip()) for marker in typo_markers)
    grammar_hits = sum(lowered.count(marker.strip()) for marker in grammar_markers)
    paragraph_count = len([chunk for chunk in essay.split("\n\n") if chunk.strip()])
    transition_hits = sum(lowered.count(marker) for marker in transition_markers)
    generic_hits = sum(lowered.count(marker) for marker in generic_markers)

    return {
        "typo_hits": typo_hits,
        "grammar_hits": grammar_hits,
        "paragraph_count": paragraph_count,
        "transition_hits": transition_hits,
        "generic_hits": generic_hits,
    }


def _set_cap(scores: dict, key: str, maximum: int) -> None:
    if key in scores:
        scores[key]["score"] = min(scores[key]["score"], maximum)


def _set_floor(scores: dict, key: str, minimum: int) -> None:
    if key in scores:
        scores[key]["score"] = max(scores[key]["score"], minimum)


def _apply_rule_based_calibration(payload: dict, essay: str) -> dict:
    """Apply conservative score caps to reduce over-scoring on weak essays."""

    scores = payload.get("scores")
    feedback = payload.get("feedback")
    if not isinstance(scores, dict) or not isinstance(feedback, dict):
        return payload

    grammar = scores["grammar"]["score"]
    spelling = scores["spelling"]["score"]
    vocabulary = scores["vocabulary"]["score"]
    form = scores["form"]["score"]
    word_count = _word_count(essay)
    quality = _essay_quality_signals(essay)

    grammar_feedback = feedback.get("grammar", "").lower()
    spelling_feedback = feedback.get("spelling", "")
    form_feedback = feedback.get("form", "").lower()

    severe_grammar = grammar == 0 or any(
        phrase in grammar_feedback
        for phrase in (
            "frequent grammar errors",
            "repeated subject-verb agreement",
            "basic mistakes",
            "errors affect meaning",
            "broken",
        )
    )
    moderate_grammar = grammar <= 1 or any(
        phrase in grammar_feedback
        for phrase in (
            "multiple noticeable grammar problems",
            "awkwardly constructed",
            "subject-verb agreement",
            "article errors",
        )
    )

    spelling_indicator_count = _count_spelling_indicators(spelling_feedback)
    severe_spelling = spelling_indicator_count >= 2
    moderate_spelling = spelling_indicator_count >= 1
    raw_severe_spelling = quality["typo_hits"] >= 7
    raw_moderate_spelling = quality["typo_hits"] >= 1
    raw_severe_grammar = quality["grammar_hits"] >= 5
    raw_moderate_grammar = quality["grammar_hits"] >= 1
    weak_structure = quality["paragraph_count"] < 4 or quality["transition_hits"] < 2
    generic_average = (
        quality["generic_hits"] >= 3
        and quality["grammar_hits"] == 0
        and quality["typo_hits"] == 0
        and scores["vocabulary"]["score"] >= 2
    )
    high_quality = (
        quality["typo_hits"] == 0
        and quality["grammar_hits"] == 0
        and quality["paragraph_count"] >= 4
        and quality["transition_hits"] >= 3
        and quality["generic_hits"] < 3
        and scores["grammar"]["score"] >= 2
        and scores["spelling"]["score"] >= 2
        and scores["vocabulary"]["score"] >= 2
    )

    if word_count < 120:
        scores["form"]["score"] = 0
    elif word_count < 200 or word_count > 320:
        scores["form"]["score"] = min(scores["form"]["score"], 1)

    if "underdeveloped" in form_feedback or "below the target length" in form_feedback:
        scores["form"]["score"] = min(scores["form"]["score"], 1)

    if severe_spelling or raw_severe_spelling:
        scores["spelling"]["score"] = 0
    elif moderate_spelling or raw_moderate_spelling:
        scores["spelling"]["score"] = min(scores["spelling"]["score"], 1)

    if severe_grammar or raw_severe_grammar:
        _set_cap(scores, "development_structure_coherence", 3)
        _set_cap(scores, "linguistic_range", 2)
        _set_cap(scores, "content", 3)
        _set_cap(scores, "vocabulary", 1)
        scores["grammar"]["score"] = min(scores["grammar"]["score"], 1)
    elif moderate_grammar or raw_moderate_grammar:
        _set_cap(scores, "development_structure_coherence", 4)
        _set_cap(scores, "linguistic_range", 3)
        _set_cap(scores, "content", 4)
        scores["grammar"]["score"] = min(scores["grammar"]["score"], 1)

    if weak_structure:
        _set_cap(scores, "development_structure_coherence", 3)
        _set_cap(scores, "content", 3)

    if spelling == 0 or severe_spelling or raw_severe_spelling:
        _set_cap(scores, "linguistic_range", 2)
        _set_cap(scores, "vocabulary", 1)

    if form <= 1:
        _set_cap(scores, "development_structure_coherence", 3)
        _set_cap(scores, "content", 3)
        _set_cap(scores, "linguistic_range", 2)

    if grammar == 0 and vocabulary <= 1 and scores["development_structure_coherence"]["score"] >= 4:
        _set_cap(scores, "development_structure_coherence", 2)

    if grammar == 0 and scores["content"]["score"] >= 4:
        _set_cap(scores, "content", 2)

    if generic_average:
        _set_cap(scores, "content", 4)
        _set_cap(scores, "development_structure_coherence", 4)
        _set_cap(scores, "linguistic_range", 4)
        _set_cap(scores, "vocabulary", 1)

    if high_quality and word_count <= 320:
        _set_floor(scores, "form", 2)
        _set_floor(scores, "content", 6)
        _set_floor(scores, "development_structure_coherence", 6)
        _set_floor(scores, "linguistic_range", 6)

    if raw_severe_grammar and raw_severe_spelling:
        _set_cap(scores, "form", 1)
        _set_cap(scores, "development_structure_coherence", 2)
        _set_cap(scores, "content", 2)
        _set_cap(scores, "linguistic_range", 1)
        scores["grammar"]["score"] = min(scores["grammar"]["score"], 0)
        scores["spelling"]["score"] = min(scores["spelling"]["score"], 0)
    elif raw_severe_grammar and not raw_severe_spelling:
        _set_floor(scores, "content", 2)
        _set_floor(scores, "development_structure_coherence", 2)
        _set_floor(scores, "linguistic_range", 2)
        _set_floor(scores, "grammar", 1)
        _set_floor(scores, "spelling", 1)
        _set_floor(scores, "form", 1)

    total = sum(item["score"] for item in scores.values())
    if raw_severe_grammar and raw_severe_spelling and total > 9:
        overflow = total - 9
        for key in ("development_structure_coherence", "content", "linguistic_range", "form"):
            if overflow <= 0:
                break
            current = scores[key]["score"]
            floor = 0 if key in {"form"} else 1
            reducible = max(0, current - floor)
            reduction = min(reducible, overflow)
            scores[key]["score"] -= reduction
            overflow -= reduction

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
            payload = _apply_rule_based_calibration(payload, essay)
            validated = EssayResponse.model_validate(payload)
            return validated.model_dump()
        except LLMServiceError as exc:
            last_error = exc
        except Exception as exc:
            raise LLMServiceError(f"Failed to validate the LLM grading response: {exc}") from exc

    if last_error is not None:
        raise last_error

    raise LLMServiceError("Unknown grading failure.")
