"""Deterministic essay analysis for Pearson-aligned baseline scoring."""

from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

from core.schemas import DeterministicAnalysisResponse


TRANSITION_MARKERS = (
    "first",
    "second",
    "third",
    "however",
    "moreover",
    "therefore",
    "for example",
    "for instance",
    "in contrast",
    "on the other hand",
    "in conclusion",
    "to conclude",
    "overall",
)

COMPLEX_MARKERS = (
    "although",
    "because",
    "while",
    "whereas",
    "which",
    "who",
    "that",
    "if",
    "unless",
    "therefore",
    "however",
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

GRAMMAR_PATTERN_MARKERS = (
    r"\b(?:he|she|it|this|that)\s+(?:are|were|have|do)\b",
    r"\b(?:they|we|you|people|children|students|governments)\s+(?:is|was|has)\b",
    r"\b(?:i|you|we|they)\s+was\b",
    r"\b(?:he|she|it)\s+were\b",
    r"\b(?:should|must|can|could|may|might|will|would)\s+(?!be\b)[a-z]+ing\b",
    r"\b(?:a)\s+[aeiou][a-z]+\b",
    r"\b(?:an)\s+[bcdfghjklmnpqrstvwxyz][a-z]+\b",
    r"\bthere\s+is\s+\w+s\b",
    r"\bthis\s+people\b",
    r"\bthese\s+kind\b",
)

STOPWORDS = {
    "a",
    "about",
    "after",
    "all",
    "also",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "because",
    "but",
    "by",
    "can",
    "do",
    "for",
    "from",
    "have",
    "how",
    "if",
    "in",
    "into",
    "is",
    "it",
    "many",
    "more",
    "not",
    "of",
    "often",
    "on",
    "or",
    "other",
    "should",
    "some",
    "than",
    "that",
    "the",
    "their",
    "there",
    "these",
    "they",
    "this",
    "to",
    "we",
    "when",
    "which",
    "who",
    "why",
    "with",
    "would",
}

SPELLING_ALLOWLIST = {
    "academically",
    "behaviour",
    "colloquialisms",
    "fluency",
    "has",
    "governmental",
    "healthcare",
    "laboratory",
    "labour",
    "memorising",
    "metro",
    "organisation",
    "organise",
    "organised",
    "organising",
    "okay",
    "pearson",
    "prioritising",
    "pte",
    "real-time",
    "sustainability",
}

KNOWN_MISSPELLINGS = {
    "childrens",
    "dont",
}


def _word_tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+(?:['-][A-Za-z]+)*", text)


def _word_count(text: str) -> int:
    return len(_word_tokens(text))


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _sentence_count(text: str) -> int:
    return len(_sentences(text))


def _paragraphs(text: str) -> list[str]:
    return [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]


def _paragraph_count(text: str) -> int:
    return len(_paragraphs(text))


def _count_markers(text: str, markers: tuple[str, ...]) -> int:
    lowered = text.lower()
    return sum(lowered.count(marker) for marker in markers)


def _tokenize_keywords(text: str) -> list[str]:
    return [token.lower() for token in _word_tokens(text) if token.lower() not in STOPWORDS and len(token) >= 4]


def _top_keywords(text: str, limit: int = 8) -> list[str]:
    counts = Counter(_tokenize_keywords(text))
    ranked = sorted(counts.items(), key=lambda item: (-item[1], -len(item[0]), item[0]))
    return [token for token, _ in ranked[:limit]]


def _prompt_relevance(question: str, essay: str) -> tuple[int, float]:
    prompt_keywords = set(_top_keywords(question))
    if not prompt_keywords:
        return 0, 0.0

    essay_tokens = set(_tokenize_keywords(essay))
    overlap = len(prompt_keywords & essay_tokens)
    return overlap, overlap / len(prompt_keywords)


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


@lru_cache(maxsize=1)
def _dictionary_words() -> set[str]:
    dictionary: set[str] = set(SPELLING_ALLOWLIST)
    for path in (Path("/usr/share/dict/words"), Path("/usr/dict/words")):
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            word = line.strip().lower()
            if word:
                dictionary.add(word)
        break
    return dictionary


def _candidate_spell_forms(token: str) -> set[str]:
    lowered = token.lower().strip("'")
    forms = {lowered, lowered.replace("'", ""), lowered.replace("-", "")}

    if lowered.endswith("'s") and len(lowered) > 2:
        forms.add(lowered[:-2])
    if lowered.endswith("ies") and len(lowered) > 4:
        forms.add(lowered[:-3] + "y")
    if lowered.endswith("es") and len(lowered) > 4:
        forms.add(lowered[:-2])
    if lowered.endswith("s") and len(lowered) > 3:
        forms.add(lowered[:-1])
    if lowered.endswith("ed") and len(lowered) > 4:
        forms.add(lowered[:-2])
        forms.add(lowered[:-1])
    if lowered.endswith("ing") and len(lowered) > 5:
        stem = lowered[:-3]
        forms.add(stem)
        forms.add(stem + "e")
        if len(stem) >= 2 and stem[-1] == stem[-2]:
            forms.add(stem[:-1])
    if lowered.endswith("ly") and len(lowered) > 4:
        forms.add(lowered[:-2])
    if lowered.endswith("er") and len(lowered) > 4:
        forms.add(lowered[:-2])
        forms.add(lowered[:-1])
    if lowered.endswith("est") and len(lowered) > 5:
        forms.add(lowered[:-3])
        forms.add(lowered[:-2])
    if lowered.endswith("ier") and len(lowered) > 5:
        forms.add(lowered[:-3] + "y")

    for part in lowered.split("-"):
        if part:
            forms.add(part)

    return {form for form in forms if form}


def _detect_spelling_errors(essay: str, question: str) -> tuple[int, list[str]]:
    dictionary = _dictionary_words()
    prompt_lexicon = set(_tokenize_keywords(question))

    errors: list[str] = []
    for token in _word_tokens(essay):
        normalized = token.lower()
        if len(normalized) <= 2:
            continue
        if normalized in KNOWN_MISSPELLINGS:
            errors.append(normalized)
            continue
        if normalized in STOPWORDS:
            continue
        if normalized in prompt_lexicon or normalized in SPELLING_ALLOWLIST:
            continue
        if any(form in dictionary for form in _candidate_spell_forms(normalized)):
            continue
        if token[0].isupper():
            continue
        errors.append(normalized)

    counts = Counter(errors)
    examples = [word for word, _ in counts.most_common(3)]
    return sum(counts.values()), examples


def _sentence_word_counts(sentences: list[str]) -> list[int]:
    return [len(_word_tokens(sentence)) for sentence in sentences]


def _grammar_error_signals(essay: str, sentences: list[str]) -> tuple[int, int, int]:
    lowered = essay.lower()
    regex_hits = sum(len(re.findall(pattern, lowered)) for pattern in GRAMMAR_PATTERN_MARKERS)
    lowercase_starts = sum(1 for sentence in sentences if sentence and sentence[0].islower())
    missing_terminal_punctuation = int(bool(essay.strip()) and essay.strip()[-1] not in ".!?")
    run_on_like_sentences = sum(1 for count in _sentence_word_counts(sentences) if count >= 38)
    severe_hits = run_on_like_sentences + missing_terminal_punctuation
    total_errors = regex_hits + lowercase_starts + severe_hits
    return total_errors, regex_hits, severe_hits


def _complex_sentence_count(sentences: list[str]) -> int:
    total = 0
    for sentence in sentences:
        lowered = sentence.lower()
        if any(marker in lowered for marker in COMPLEX_MARKERS) or ";" in sentence or "," in sentence:
            total += 1
    return total


def _lexical_diversity(tokens: list[str]) -> float:
    lowered = [token.lower() for token in tokens if token.isalpha()]
    if not lowered:
        return 0.0
    return len(set(lowered)) / len(lowered)


def _academic_word_ratio(tokens: list[str]) -> float:
    lowered = [token.lower() for token in tokens if token.isalpha()]
    if not lowered:
        return 0.0
    academic_like = sum(1 for token in lowered if len(token) >= 7)
    return academic_like / len(lowered)


def _score_form_raw(word_count: int) -> tuple[int, str]:
    if 200 <= word_count <= 300:
        return 2, "Length is within the official PTE target band of 200-300 words."
    if 120 <= word_count < 200 or 301 <= word_count <= 380:
        return 1, "Length is outside the ideal band but still within the partial-credit form range."
    return 0, "Length falls outside the accepted PTE essay range."


def _score_spelling_raw(error_count: int, examples: list[str]) -> tuple[int, str]:
    if error_count == 0:
        return 2, "No spelling errors were detected at token level."
    if error_count == 1:
        example = examples[0] if examples else "one token"
        return 1, f"One likely spelling error was detected: '{example}'."
    joined = ", ".join(f"'{example}'" for example in examples) if examples else "multiple tokens"
    return 0, f"More than one likely spelling error was detected, including {joined}."


def _score_grammar_raw(
    error_count: int,
    severe_hits: int,
    complex_sentences: int,
    sentence_count: int,
) -> tuple[int, str]:
    complex_ratio = complex_sentences / sentence_count if sentence_count else 0.0

    if error_count == 0 and complex_ratio >= 0.25:
        return 2, "Grammar shows strong control, with accurate sentences and some complexity."
    if error_count <= 2 and severe_hits == 0:
        return 1, "Grammar is generally controlled, but some sentence-level problems remain."
    return 0, "Grammar contains repeated sentence-level problems or weak structural control."


def _score_content_raw(
    overlap: int,
    coverage_ratio: float,
    paragraph_count: int,
    generic_hits: int,
) -> tuple[int, str]:
    if overlap == 0 or coverage_ratio < 0.25:
        return 0, "The response does not address the prompt closely enough to earn content credit."
    if coverage_ratio < 0.45:
        return 1, "The response touches the prompt, but a major aspect is missing."
    if coverage_ratio < 0.75 or paragraph_count < 3 or generic_hits >= 3:
        return 2, "The response addresses the task but misses part of the prompt or develops it unevenly."
    return 3, "The response addresses the prompt directly and covers the task adequately."


def _score_development_raw(
    paragraph_count: int,
    transition_hits: int,
    intro_conclusion: bool,
    body_paragraphs: int,
) -> int:
    if paragraph_count >= 4 and transition_hits >= 2 and intro_conclusion and body_paragraphs >= 2:
        return 2
    if paragraph_count >= 3 and body_paragraphs >= 1:
        return 1
    return 0


def _score_linguistic_range_raw(
    lexical_diversity: float,
    academic_word_ratio: float,
    complex_sentence_ratio: float,
) -> int:
    if lexical_diversity >= 0.52 and academic_word_ratio >= 0.22 and complex_sentence_ratio >= 0.3:
        return 2
    if lexical_diversity >= 0.42 and academic_word_ratio >= 0.16:
        return 1
    return 0


def _score_vocabulary_raw(lexical_diversity: float, academic_word_ratio: float, generic_hits: int) -> int:
    if lexical_diversity >= 0.48 and academic_word_ratio >= 0.2 and generic_hits == 0:
        return 2
    if lexical_diversity >= 0.36:
        return 1
    return 0


def _map_to_rubric(
    content_raw: int,
    development_raw: int,
    form_raw: int,
    grammar_raw: int,
    linguistic_raw: int,
    vocabulary_raw: int,
    spelling_raw: int,
) -> dict[str, int]:
    return {
        "content": content_raw * 2,
        "development_structure_coherence": development_raw * 3,
        "form": form_raw,
        "grammar": grammar_raw,
        "linguistic_range": min(6, linguistic_raw * 2 + vocabulary_raw),
        "spelling": spelling_raw,
        "vocabulary": vocabulary_raw,
    }


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
    """Return a deterministic baseline analysis using Pearson-like raw trait logic."""

    paragraphs = _paragraphs(essay)
    sentences = _sentences(essay)
    tokens = _word_tokens(essay)

    word_count = len(tokens)
    paragraph_count = len(paragraphs)
    sentence_count = len(sentences)
    transition_hits = _count_markers(essay, TRANSITION_MARKERS)
    generic_hits = _count_markers(essay, GENERIC_PHRASE_MARKERS)
    overlap, coverage_ratio = _prompt_relevance(question, essay)
    all_caps_ratio = _all_caps_ratio(essay)
    bullet_line_count = _bullet_line_count(essay)
    punctuation_count = _punctuation_count(essay)

    spelling_errors, spelling_examples = _detect_spelling_errors(essay, question)
    grammar_errors, grammar_pattern_hits, severe_grammar_hits = _grammar_error_signals(essay, sentences)
    complex_sentence_count = _complex_sentence_count(sentences)
    complex_sentence_ratio = complex_sentence_count / sentence_count if sentence_count else 0.0
    lexical_diversity = _lexical_diversity(tokens)
    academic_word_ratio = _academic_word_ratio(tokens)

    last_paragraph = paragraphs[-1].lower() if paragraphs else ""
    intro_conclusion = bool(paragraphs) and any(marker in last_paragraph for marker in ("in conclusion", "to conclude", "overall"))
    body_paragraphs = max(0, paragraph_count - 2)

    form_raw, form_feedback = _score_form_raw(word_count)
    form_issues = _form_anomalies(
        essay,
        all_caps_ratio,
        bullet_line_count,
        punctuation_count,
        sentence_count,
    )
    if form_issues:
        form_raw = 0
        form_feedback = " ".join(form_issues)

    content_raw, content_feedback = _score_content_raw(overlap, coverage_ratio, paragraph_count, generic_hits)
    spelling_raw, spelling_feedback = _score_spelling_raw(spelling_errors, spelling_examples)
    grammar_raw, grammar_feedback = _score_grammar_raw(
        grammar_errors,
        severe_grammar_hits,
        complex_sentence_count,
        sentence_count,
    )
    development_raw = _score_development_raw(paragraph_count, transition_hits, intro_conclusion, body_paragraphs)
    linguistic_raw = _score_linguistic_range_raw(lexical_diversity, academic_word_ratio, complex_sentence_ratio)
    vocabulary_raw = _score_vocabulary_raw(lexical_diversity, academic_word_ratio, generic_hits)

    if content_raw == 0:
        development_raw = 0
        form_raw = 0
        grammar_raw = 0
        linguistic_raw = 0
        spelling_raw = 0
        vocabulary_raw = 0
        form_feedback = "Content received no credit, so no further trait scoring was awarded."
        grammar_feedback = "Content received no credit, so grammar was not scored further."
        spelling_feedback = "Content received no credit, so spelling was not scored further."
    elif form_raw == 0:
        development_raw = 0
        grammar_raw = 0
        linguistic_raw = 0
        spelling_raw = 0
        vocabulary_raw = 0
        grammar_feedback = "Form received no credit, so grammar was not scored further."
        spelling_feedback = "Form received no credit, so spelling was not scored further."

    rubric_scores = _map_to_rubric(
        content_raw,
        development_raw,
        form_raw,
        grammar_raw,
        linguistic_raw,
        vocabulary_raw,
        spelling_raw,
    )

    summary = (
        "Deterministic baseline completed using prompt relevance, token-level spelling, "
        "sentence-level grammar signals, and Pearson-style raw trait mapping."
    )

    analysis = DeterministicAnalysisResponse.model_validate(
        {
            "scores": {
                "content": {"score": rubric_scores["content"], "max": 6},
                "development_structure_coherence": {
                    "score": rubric_scores["development_structure_coherence"],
                    "max": 6,
                },
                "form": {"score": rubric_scores["form"], "max": 2},
                "grammar": {"score": rubric_scores["grammar"], "max": 2},
                "linguistic_range": {"score": rubric_scores["linguistic_range"], "max": 6},
                "spelling": {"score": rubric_scores["spelling"], "max": 2},
                "vocabulary": {"score": rubric_scores["vocabulary"], "max": 2},
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
                "typo_hits": spelling_errors,
                "grammar_pattern_hits": grammar_pattern_hits,
                "generic_phrase_hits": generic_hits,
                "prompt_keyword_overlap": overlap,
                "prompt_coverage_ratio": coverage_ratio,
                "all_caps_ratio": all_caps_ratio,
                "bullet_line_count": bullet_line_count,
                "punctuation_count": punctuation_count,
                "spelling_error_count": spelling_errors,
                "grammar_error_count": grammar_errors,
                "complex_sentence_count": complex_sentence_count,
                "lexical_diversity": lexical_diversity,
                "academic_word_ratio": academic_word_ratio,
                "raw_content": content_raw,
                "raw_development_structure_coherence": development_raw,
                "raw_form": form_raw,
                "raw_grammar": grammar_raw,
                "raw_linguistic_range": linguistic_raw,
                "raw_spelling": spelling_raw,
                "raw_vocabulary": vocabulary_raw,
            },
            "summary": summary,
        }
    )

    return analysis.model_dump()
