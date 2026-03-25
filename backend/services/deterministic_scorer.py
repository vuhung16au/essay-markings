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

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "more",
    "not",
    "of",
    "on",
    "or",
    "other",
    "should",
    "than",
    "that",
    "the",
    "their",
    "there",
    "this",
    "to",
    "often",
    "why",
    "with",
}


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


def _tokenize_keywords(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z'-]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS and len(token) >= 4]


def _top_keywords(text: str, limit: int = 8) -> list[str]:
    counts: dict[str, int] = {}
    for token in _tokenize_keywords(text):
        counts[token] = counts.get(token, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
    return [token for token, _ in ranked[:limit]]


def _prompt_relevance(question: str, essay: str) -> tuple[int, float]:
    prompt_keywords = set(_top_keywords(question))
    if not prompt_keywords:
        return 0, 0.0

    essay_tokens = set(_tokenize_keywords(essay))
    overlap = len(prompt_keywords & essay_tokens)
    coverage_ratio = overlap / len(prompt_keywords)
    return overlap, coverage_ratio


def _all_caps_ratio(text: str) -> float:
    letters = [char for char in text if char.isalpha()]
    if not letters:
        return 0.0
    caps = sum(1 for char in letters if char.isupper())
    return caps / len(letters)


def _bullet_line_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if re.match(r"^\s*([-*]|\d+\.)\s+", line))


def _punctuation_count(text: str) -> int:
    return len(re.findall(r"[.!?,;:]", text))


def _score_form(word_count: int) -> tuple[int, str]:
    if 200 <= word_count <= 300:
        return 2, "Length is within the target band for a full essay response."
    if 120 <= word_count < 200 or 301 <= word_count <= 380:
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


def _score_content(
    overlap: int,
    coverage_ratio: float,
    paragraph_count: int,
    generic_hits: int,
) -> tuple[int, str]:
    if overlap == 0 or coverage_ratio < 0.25:
        return 0, "The response does not address the prompt closely enough to earn content credit."
    if coverage_ratio >= 0.75 and paragraph_count >= 4 and generic_hits == 0:
        return 6, "The response addresses the prompt directly and covers the main task well."
    if coverage_ratio >= 0.5 and paragraph_count >= 3:
        return 4, "The response is relevant to the prompt but does not fully cover all aspects."
    return 2, "The response addresses the prompt only partially and misses important aspects."


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


def _form_anomalies(
    essay: str,
    all_caps_ratio: float,
    bullet_line_count: int,
    punctuation_count: int,
    sentence_count: int,
) -> list[str]:
    issues: list[str] = []
    if all_caps_ratio > 0.85:
        issues.append("Essay is written mostly in capital letters.")
    if bullet_line_count >= 2:
        issues.append("Essay is formatted as bullet points instead of continuous prose.")
    if punctuation_count == 0 or sentence_count <= 1:
        issues.append("Essay lacks enough sentence punctuation for normal prose.")
    if re.fullmatch(r"[\W\d_]+", essay.strip() or " "):
        issues.append("Essay does not contain enough valid prose text.")
    return issues


def score_essay_deterministic(question: str, essay: str) -> dict:
    """Return a deterministic baseline analysis using measurable text signals."""

    word_count = _word_count(essay)
    paragraph_count = _paragraph_count(essay)
    sentence_count = _sentence_count(essay)
    transition_hits = _count_markers(essay, TRANSITION_MARKERS)
    typo_hits = _count_markers(essay, TYPO_MARKERS)
    grammar_hits = _count_markers(essay, GRAMMAR_PATTERN_MARKERS)
    generic_hits = _count_markers(essay, GENERIC_PHRASE_MARKERS)
    overlap, coverage_ratio = _prompt_relevance(question, essay)
    all_caps_ratio = _all_caps_ratio(essay)
    bullet_line_count = _bullet_line_count(essay)
    punctuation_count = _punctuation_count(essay)

    form_score, form_feedback = _score_form(word_count)
    form_issues = _form_anomalies(
        essay,
        all_caps_ratio,
        bullet_line_count,
        punctuation_count,
        sentence_count,
    )
    if form_issues:
        form_score = 0
        form_feedback = " ".join(form_issues)

    spelling_score, spelling_feedback = _score_spelling(typo_hits)
    grammar_score, grammar_feedback = _score_grammar(grammar_hits)
    structure_score = _score_structure(paragraph_count, transition_hits)
    content_score, content_feedback = _score_content(overlap, coverage_ratio, paragraph_count, generic_hits)
    linguistic_range_score = _score_linguistic_range(grammar_score, spelling_score, generic_hits)
    vocabulary_score = _score_vocabulary(generic_hits, grammar_hits)

    if content_score == 0:
        structure_score = 0
        form_score = 0
        grammar_score = 0
        linguistic_range_score = 0
        spelling_score = 0
        vocabulary_score = 0
        form_feedback = "Content received no credit, so no further trait scoring was awarded."
        grammar_feedback = "Content received no credit, so grammar was not scored further."
        spelling_feedback = "Content received no credit, so spelling was not scored further."
    elif form_score == 0:
        structure_score = 0
        grammar_score = 0
        linguistic_range_score = 0
        spelling_score = 0
        vocabulary_score = 0
        grammar_feedback = "Form received no credit, so grammar was not scored further."
        spelling_feedback = "Form received no credit, so spelling was not scored further."

    summary = (
        "Deterministic baseline completed using text-measurable features. "
        "This output is intended as a stable scoring anchor for a Pearson-aligned hybrid grading strategy."
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
                "form": f"{content_feedback} {form_feedback}".strip(),
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
                "prompt_keyword_overlap": overlap,
                "prompt_coverage_ratio": coverage_ratio,
                "all_caps_ratio": all_caps_ratio,
                "bullet_line_count": bullet_line_count,
                "punctuation_count": punctuation_count,
            },
            "summary": summary,
        }
    )

    return analysis.model_dump()
