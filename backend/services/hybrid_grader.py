"""Hybrid essay grading that combines deterministic scoring with LLM feedback."""

from __future__ import annotations

from core.schemas import EssayResponse
from services.deterministic_scorer import score_essay_deterministic
from services.llm_service import grade_essay


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def _merge_scores(deterministic: dict, llm: dict) -> dict:
    det_scores = deterministic["scores"]
    llm_scores = llm["scores"]

    if det_scores["content"]["score"] == 0:
        return {key: {"score": 0, "max": value["max"]} for key, value in det_scores.items()}

    if det_scores["form"]["score"] == 0:
        merged = {}
        for key, value in det_scores.items():
            score = value["score"] if key == "content" else 0
            merged[key] = {"score": score, "max": value["max"]}
        return merged

    merged = {}

    for key in det_scores:
        det_score = det_scores[key]["score"]
        llm_score = llm_scores[key]["score"]
        max_score = det_scores[key]["max"]

        if key in {"form", "spelling"}:
            final_score = det_score
        elif key == "grammar":
            final_score = _clamp(llm_score, max(0, det_score - 1), min(max_score, det_score + 1))
            if det_score <= 1:
                final_score = min(final_score, det_score)
        elif key == "vocabulary":
            final_score = _clamp(llm_score, max(0, det_score - 1), min(max_score, det_score + 1))
        else:
            final_score = _clamp(llm_score, max(0, det_score - 1), min(max_score, det_score + 1))

        merged[key] = {"score": final_score, "max": max_score}

    return merged


def _merge_feedback(deterministic: dict, llm: dict) -> dict:
    det_feedback = deterministic["feedback"]
    llm_feedback = llm["feedback"]

    feedback = {}
    for key in ("form", "grammar", "spelling"):
        llm_text = llm_feedback.get(key, "").strip()
        det_text = det_feedback.get(key, "").strip()
        feedback[key] = llm_text or det_text
    return feedback


def _merge_points(llm: dict) -> tuple[list[str], list[str]]:
    good_points = llm.get("good_points") or ["Shows effort in addressing the essay task."]
    improvements = llm.get("improvements") or ["Develop the argument with clearer examples and tighter language."]
    return good_points[:5], improvements[:5]


async def grade_essay_hybrid(question: str, essay: str) -> dict:
    """Combine deterministic baseline scoring with bounded LLM scoring."""

    deterministic = score_essay_deterministic(question, essay)
    llm = await grade_essay(question, essay)

    merged = {
        "scores": _merge_scores(deterministic, llm),
        "feedback": _merge_feedback(deterministic, llm),
    }
    good_points, improvements = _merge_points(llm)
    merged["good_points"] = good_points
    merged["improvements"] = improvements

    validated = EssayResponse.model_validate(merged)
    return validated.model_dump()
