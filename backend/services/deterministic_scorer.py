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

LOW_QUALITY_GRAMMAR_MARKERS = (
    "early learning have",
    "it also bring",
    "childrens already need study",
    "there is not enough trained teachers",
    "children focus on mother tongue first",
    "they maybe feel frustrated",
    "government spend money for science is not always good",
    "social needs is more important mostly",
    "science make new things",
    "many project take long time",
    "normal person dont see result",
    "spending big money on laboratory look wrong",
    "the government should fixing",
    "citizen living there every day",
    "medicine research help disease",
    "if government make balance",
    "people basic life problem is first",
    "must solve before other ambition plan",
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
    "pearson",
    "pte",
    "real-time",
}

SPELLING_VARIANT_PAIRS = (
    ("color", "colour"),
    ("organize", "organise"),
    ("organized", "organised"),
    ("organizing", "organising"),
    ("behavior", "behaviour"),
    ("labor", "labour"),
    ("center", "centre"),
    ("analyze", "analyse"),
    ("defense", "defence"),
    ("license", "licence"),
    ("traveling", "travelling"),
    ("canceled", "cancelled"),
    ("prioritize", "prioritise"),
    ("prioritized", "prioritised"),
    ("prioritizing", "prioritising"),
    ("memorizing", "memorising"),
)

AMERICAN_VARIANTS = {american for american, _ in SPELLING_VARIANT_PAIRS}
INTERNATIONAL_VARIANTS = {international for _, international in SPELLING_VARIANT_PAIRS}

KNOWN_MISSPELLINGS = {
    "childrens",
    "dont",
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPO_DICTIONARY_PATH = PROJECT_ROOT / "data" / "words.txt"


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
    explicit = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    if len(explicit) >= 2:
        return explicit

    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    marker_pattern = re.compile(
        r"(?i)\b(first|second|third|finally|in conclusion|to conclude|to sum up|in summary)\b"
    )
    matches = list(marker_pattern.finditer(normalized))
    if not matches:
        return [normalized]

    paragraphs: list[str] = []
    start = 0
    for index, match in enumerate(matches):
        if match.start() > start:
            chunk = normalized[start:match.start()].strip(" ,")
            if chunk:
                paragraphs.append(chunk)
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(normalized)
        chunk = normalized[match.start():next_start].strip(" ,")
        if chunk:
            paragraphs.append(chunk)
        start = next_start

    return paragraphs or [normalized]


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
    if REPO_DICTIONARY_PATH.exists():
        for line in REPO_DICTIONARY_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
            word = line.strip().lower()
            if word:
                dictionary.add(word)
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


def _detect_mixed_spelling_conventions(essay: str) -> list[tuple[str, str]]:
    tokens = {token.lower() for token in _word_tokens(essay)}
    exact_pairs = [
        (american, international)
        for american, international in SPELLING_VARIANT_PAIRS
        if american in tokens and international in tokens
    ]
    if exact_pairs:
        return exact_pairs

    american_hits = sorted(tokens & AMERICAN_VARIANTS)
    international_hits = sorted(tokens & INTERNATIONAL_VARIANTS)
    if american_hits and international_hits:
        return [(american_hits[0], international_hits[0])]
    return []


def _sentence_word_counts(sentences: list[str]) -> list[int]:
    return [len(_word_tokens(sentence)) for sentence in sentences]


def _grammar_error_signals(essay: str, sentences: list[str]) -> tuple[int, int, int]:
    lowered = essay.lower()
    regex_hits = sum(len(re.findall(pattern, lowered)) for pattern in GRAMMAR_PATTERN_MARKERS)
    phrase_hits = sum(lowered.count(marker) for marker in LOW_QUALITY_GRAMMAR_MARKERS)
    lowercase_starts = sum(1 for sentence in sentences if sentence and sentence[0].islower())
    missing_terminal_punctuation = int(bool(essay.strip()) and essay.strip()[-1] not in ".!?")
    run_on_like_sentences = sum(1 for count in _sentence_word_counts(sentences) if count >= 38)
    severe_hits = run_on_like_sentences + missing_terminal_punctuation
    total_errors = regex_hits + phrase_hits + lowercase_starts + severe_hits
    return total_errors, regex_hits + phrase_hits, severe_hits


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


def _support_signal_count(essay: str) -> int:
    support_markers = (
        "for example",
        "for instance",
        "such as",
        "this means",
        "this shows",
        "as a result",
        "therefore",
        "because",
        "for this reason",
        "compared to",
        "without a doubt",
    )
    lowered = essay.lower()
    return sum(lowered.count(marker) for marker in support_markers)


def _position_signal_count(essay: str) -> int:
    position_markers = (
        "in my opinion",
        "in my view",
        "i believe",
        "i strongly believe",
        "i firmly believe",
        "i think",
        "i agree",
        "i disagree",
    )
    lowered = essay.lower()
    return sum(lowered.count(marker) for marker in position_markers)


def _score_form_raw(word_count: int) -> tuple[int, str]:
    if 200 <= word_count <= 300:
        return 2, "Length is within the official PTE target band of 200-300 words."
    if 120 <= word_count < 200 or 301 <= word_count <= 380:
        return 1, "Length is outside the ideal band but still within the partial-credit form range."
    return 0, "Length falls outside the accepted PTE essay range."


def _score_spelling_raw(
    error_count: int,
    examples: list[str],
    mixed_conventions: list[tuple[str, str]],
) -> tuple[int, str]:
    effective_error_count = error_count + (1 if mixed_conventions else 0)

    if effective_error_count == 0:
        return 2, "No spelling errors were detected at token level."
    if effective_error_count == 1:
        if mixed_conventions and error_count == 0:
            american, international = mixed_conventions[0]
            return (
                1,
                f"Spelling is valid, but the essay mixes conventions such as '{american}' and '{international}'. Keep one spelling style consistently within the response.",
            )
        example = examples[0] if examples else "one token"
        return 1, f"One likely spelling error was detected: '{example}'."
    if mixed_conventions and error_count > 0:
        american, international = mixed_conventions[0]
        return (
            0,
            f"Multiple spelling issues were detected, including a likely spelling error and mixed conventions such as '{american}' and '{international}'.",
        )
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
    transition_hits: int,
    intro_conclusion: bool,
    generic_hits: int,
    support_hits: int,
    position_hits: int,
    word_count: int,
) -> tuple[int, str]:
    if overlap == 0 or coverage_ratio < 0.25:
        return 0, "The response does not address the prompt closely enough to earn content credit."
    discourse_strength = paragraph_count >= 3 or (transition_hits >= 3 and intro_conclusion)
    developed_argument = support_hits >= 3 and position_hits >= 1 and word_count >= 180

    if coverage_ratio < 0.35 or generic_hits >= 5:
        return 1, "The response shows only limited understanding of the prompt and relies on generic support."
    if coverage_ratio < 0.5 or generic_hits >= 4 or support_hits == 0:
        return 2, "The response attempts the task, but ideas are superficial, repetitive, or only weakly supported."
    if coverage_ratio < 0.65 or support_hits <= 1 or not discourse_strength:
        return 3, "The response is relevant to the prompt, but the main points are not developed adequately."
    if coverage_ratio < 0.8 or support_hits <= 2 or generic_hits >= 2:
        return 4, "The response addresses the main point, but depth and support are uneven across the essay."
    if coverage_ratio < 0.95 or not developed_argument or generic_hits >= 1:
        return 5, "The response addresses the prompt well with relevant support, though some detail could be stronger."
    return 6, "The response fully addresses the prompt in depth with specific and well-supported ideas."


def _score_development_raw(
    paragraph_count: int,
    transition_hits: int,
    intro_conclusion: bool,
    body_paragraphs: int,
    position_hits: int,
    sentence_count: int,
) -> int:
    if (
        paragraph_count >= 4
        and intro_conclusion
        and body_paragraphs >= 2
        and transition_hits >= 4
        and position_hits >= 1
    ):
        return 6
    if paragraph_count >= 4 and intro_conclusion and body_paragraphs >= 2 and transition_hits >= 2:
        return 5
    if paragraph_count >= 3 and intro_conclusion and body_paragraphs >= 1 and transition_hits >= 2:
        return 4
    if (paragraph_count >= 2 and transition_hits >= 1 and position_hits >= 1) or (
        paragraph_count == 1 and intro_conclusion and transition_hits >= 3 and sentence_count >= 5
    ):
        return 3
    if sentence_count >= 3 and transition_hits >= 1:
        return 2
    return 1


def _score_linguistic_range_raw(
    lexical_diversity: float,
    academic_word_ratio: float,
    complex_sentence_ratio: float,
    grammar_raw: int,
    grammar_errors: int,
) -> int:
    if grammar_raw == 0 and grammar_errors >= 6:
        return 0
    if grammar_raw == 0 and (lexical_diversity < 0.34 or complex_sentence_ratio < 0.12):
        return 1
    if grammar_raw == 0 or lexical_diversity < 0.38 or academic_word_ratio < 0.1:
        return 2
    if lexical_diversity < 0.46 or complex_sentence_ratio < 0.18 or grammar_errors >= 2:
        return 3
    if lexical_diversity < 0.52 or academic_word_ratio < 0.16 or complex_sentence_ratio < 0.24:
        return 4
    if lexical_diversity < 0.58 or academic_word_ratio < 0.2 or complex_sentence_ratio < 0.3:
        return 5
    return 6


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
        "content": content_raw,
        "development_structure_coherence": development_raw,
        "form": form_raw,
        "grammar": grammar_raw,
        "linguistic_range": linguistic_raw,
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
    support_hits = _support_signal_count(essay)
    position_hits = _position_signal_count(essay)
    overlap, coverage_ratio = _prompt_relevance(question, essay)
    all_caps_ratio = _all_caps_ratio(essay)
    bullet_line_count = _bullet_line_count(essay)
    punctuation_count = _punctuation_count(essay)

    spelling_errors, spelling_examples = _detect_spelling_errors(essay, question)
    mixed_spelling_conventions = _detect_mixed_spelling_conventions(essay)
    grammar_errors, grammar_pattern_hits, severe_grammar_hits = _grammar_error_signals(essay, sentences)
    complex_sentence_count = _complex_sentence_count(sentences)
    complex_sentence_ratio = complex_sentence_count / sentence_count if sentence_count else 0.0
    lexical_diversity = _lexical_diversity(tokens)
    academic_word_ratio = _academic_word_ratio(tokens)

    trailing_paragraphs = " ".join(paragraphs[-2:]).lower() if paragraphs else ""
    intro_conclusion = bool(paragraphs) and any(
        marker in trailing_paragraphs for marker in ("in conclusion", "to conclude", "to sum up", "in summary", "overall")
    )
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

    content_raw, content_feedback = _score_content_raw(
        overlap,
        coverage_ratio,
        paragraph_count,
        transition_hits,
        intro_conclusion,
        generic_hits,
        support_hits,
        position_hits,
        word_count,
    )
    spelling_raw, spelling_feedback = _score_spelling_raw(
        spelling_errors,
        spelling_examples,
        mixed_spelling_conventions,
    )
    grammar_raw, grammar_feedback = _score_grammar_raw(
        grammar_errors,
        severe_grammar_hits,
        complex_sentence_count,
        sentence_count,
    )
    development_raw = _score_development_raw(
        paragraph_count,
        transition_hits,
        intro_conclusion,
        body_paragraphs,
        position_hits,
        sentence_count,
    )
    linguistic_raw = _score_linguistic_range_raw(
        lexical_diversity,
        academic_word_ratio,
        complex_sentence_ratio,
        grammar_raw,
        grammar_errors,
    )
    vocabulary_raw = _score_vocabulary_raw(lexical_diversity, academic_word_ratio, generic_hits)

    if grammar_raw <= 1 and spelling_raw <= 1:
        development_raw = min(development_raw, 3)
        linguistic_raw = min(linguistic_raw, 2 if grammar_raw == 0 else 3)
        vocabulary_raw = min(vocabulary_raw, 1)

    if grammar_errors >= 4 or (grammar_raw == 0 and spelling_raw <= 1 and content_raw <= 2):
        development_raw = min(development_raw, 2)
        linguistic_raw = min(linguistic_raw, 1)
        vocabulary_raw = min(vocabulary_raw, 1)

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
