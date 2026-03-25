"""Deterministic essay analysis for consistent baseline scoring."""

from __future__ import annotations

import re

from core.schemas import DeterministicAnalysisResponse


TRANSITION_MARKERS = (
    "first",
    "second",
    "however",
    "in conclusion",
    "on the other hand",
    "another",
    "therefore",
    "for example",
    "for instance",
)

TYPO_MARKERS = (
    "dont",
    "childrens",
    "learning have",
    "it also bring",
    "they maybe",
    "need study",
    "science make",
    "government spend money",
    "it fail",
)

GRAMMAR_PATTERN_MARKERS = (
    "there is not enough trained teachers",
    "the government should fixing",
    "social needs is more important mostly",
    "children focus on mother tongue first",
    "young children can copy sounds easier",
    "does not always give good result",
    "if government make balance",
)

GENERIC_PHRASE_MARKERS = (
    "there is a lot of discussion today",
    "both ideas have advantages and disadvantages",
    "the best answer depends",
    "these points show that",
    "still play a useful role",
    "neither system is perfect by itself",
    "a mixed approach is probably",
)


def _word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def _sentence_count(text: str) -> int:
    parts = re.split(r"[.!?]+", text)
    return len([part for part in parts if part.strip()])


def _paragraph_count(text: str) -> int:
    return len([chunk for chunk in text.split("\n\n") if chunk.strip()])


def _count_markers(text: str, markers: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(lowered.count(marker) for marker in markers)


def _score_form(word_count: int) -> tuple[int, str]:
    if 200 <= word_count <= 320:
        return 2, "Length is within the target band for a full essay response."
    if 120 <= word_count < 200 or 321 <= word_count <= 380:
        return 1, "Length is outside the ideal band but still acceptable."
    return 0, "Length is too short or too long for a strong PTE response."


def _score_spelling(typo_hits: int) -> tuple[int, str]:
    if typo_hits == 0:
        return 2, "No obvious spelling-pattern issues were detected."
    if typo_hits == 1:
        return 1, "A small number of likely spelling issues were detected."
    return 0, "Multiple likely spelling issues were detected."


def _score_grammar(grammar_hits: int) -> tuple[int, str]:
    if grammar_hits == 0:
        return 2, "No repeated high-risk grammar patterns were detected."
    if grammar_hits <= 2:
        return 1, "Some repeated grammar-pattern issues were detected."
    return 0, "Frequent grammar-pattern issues were detected."


def _score_structure(paragraph_count: int, transition_hits: int) -> int:
    if paragraph_count >= 4 and transition_hits >= 3:
        return 5
    if paragraph_count >= 4 and transition_hits >= 2:
        return 4
    if paragraph_count >= 3:
        return 3
    if paragraph_count >= 2:
        return 2
    return 1


def _score_content(generic_hits: int, paragraph_count: int) -> int:
    if generic_hits == 0 and paragraph_count >= 4:
        return 5
    if generic_hits <= 2 and paragraph_count >= 4:
        return 4
    if paragraph_count >= 3:
        return 3
    return 2


def _score_linguistic_range(grammar_score: int, typo_score: int, generic_hits: int) -> int:
    if grammar_score == 2 and typo_score == 2 and generic_hits == 0:
        return 5
    if grammar_score >= 1 and typo_score >= 1 and generic_hits <= 2:
        return 4
    if grammar_score >= 1:
        return 3
    return 2


def _score_vocabulary(generic_hits: int, grammar_hits: int) -> int:
    if generic_hits == 0 and grammar_hits == 0:
        return 2
    return 1


def score_essay_deterministic(question: str, essay: str) -> dict:
    """Return a deterministic baseline analysis using measurable text signals."""

    del question

    word_count = _word_count(essay)
    paragraph_count = _paragraph_count(essay)
    sentence_count = _sentence_count(essay)
    transition_hits = _count_markers(essay, TRANSITION_MARKERS)
    typo_hits = _count_markers(essay, TYPO_MARKERS)
    grammar_hits = _count_markers(essay, GRAMMAR_PATTERN_MARKERS)
    generic_hits = _count_markers(essay, GENERIC_PHRASE_MARKERS)

    form_score, form_feedback = _score_form(word_count)
    spelling_score, spelling_feedback = _score_spelling(typo_hits)
    grammar_score, grammar_feedback = _score_grammar(grammar_hits)
    structure_score = _score_structure(paragraph_count, transition_hits)
    content_score = _score_content(generic_hits, paragraph_count)
    linguistic_range_score = _score_linguistic_range(grammar_score, spelling_score, generic_hits)
    vocabulary_score = _score_vocabulary(generic_hits, grammar_hits)

    summary = (
        "Deterministic baseline completed using text-measurable features. "
        "This output is intended as a stable scoring anchor for a future hybrid grading strategy."
    )

    analysis = DeterministicAnalysisResponse.model_validate(
        {
            "scores": {
                "content": {"score": content_score, "max": 6},
                "development_structure_coherence": {"score": structure_score, "max": 6},
                "form": {"score": form_score, "max": 2},
                "grammar": {"score": grammar_score, "max": 2},
                "linguistic_range": {"score": linguistic_range_score, "max": 6},
                "spelling": {"score": spelling_score, "max": 2},
                "vocabulary": {"score": vocabulary_score, "max": 2},
            },
            "feedback": {
                "form": form_feedback,
                "grammar": grammar_feedback,
                "spelling": spelling_feedback,
            },
            "signals": {
                "word_count": word_count,
                "paragraph_count": paragraph_count,
                "sentence_count": sentence_count,
                "transition_hits": transition_hits,
                "typo_hits": typo_hits,
                "grammar_pattern_hits": grammar_hits,
                "generic_phrase_hits": generic_hits,
            },
            "summary": summary,
        }
    )

    return analysis.model_dump()
