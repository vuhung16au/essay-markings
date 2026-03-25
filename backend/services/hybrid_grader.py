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


def _format_ratio(value: float) -> str:
    return f"{value:.2f}"


def _join_examples(points: list[str], limit: int = 2) -> str:
    selected = [point.strip().rstrip(".") for point in points[:limit] if point.strip()]
    return "; ".join(selected)


def _build_details(
    deterministic: dict,
    merged_scores: dict,
    feedback: dict,
    good_points: list[str],
    improvements: list[str],
) -> dict:
    signals = deterministic["signals"]
    det_scores = deterministic["scores"]

    content_analysis = (
        "Content was judged against prompt relevance and task coverage. "
        f"The essay matched {signals['prompt_keyword_overlap']} prompt keywords with a coverage ratio of "
        f"{_format_ratio(signals['prompt_coverage_ratio'])}. "
        f"Current score: {merged_scores['content']['score']} / {merged_scores['content']['max']}."
    )
    content_deductions: list[str] = []
    if merged_scores["content"]["score"] < merged_scores["content"]["max"]:
        content_deductions.append(
            "The response does not fully cover every aspect of the prompt, so content credit was reduced."
        )
        if signals["prompt_coverage_ratio"] < 0.75:
            content_deductions.append(
                f"Prompt coverage remained below the strongest band at {_format_ratio(signals['prompt_coverage_ratio'])}."
            )
        if improvements:
            content_deductions.append(f"Improvement focus: {_join_examples(improvements, 1)}.")

    development_analysis = (
        "Development, structure, and coherence were judged from paragraphing, progression, and linking. "
        f"The essay has {signals['paragraph_count']} paragraphs, {signals['transition_hits']} transition markers, "
        f"and {signals['sentence_count']} sentences. "
        f"Current score: {merged_scores['development_structure_coherence']['score']} / "
        f"{merged_scores['development_structure_coherence']['max']}."
    )
    development_deductions: list[str] = []
    if merged_scores["development_structure_coherence"]["score"] < merged_scores["development_structure_coherence"]["max"]:
        if signals["paragraph_count"] < 4:
            development_deductions.append("The essay has limited paragraph development for a top-band response.")
        if signals["transition_hits"] < 2:
            development_deductions.append("Linking language is limited, so idea progression feels less controlled.")
        development_deductions.append(
            "Some arguments or examples need clearer sequencing and stronger logical connection."
        )

    form_analysis = (
        "Form was judged using official PTE-style length and presentation checks. "
        f"The essay contains {signals['word_count']} words, punctuation count {signals['punctuation_count']}, "
        f"and bullet-line count {signals['bullet_line_count']}. "
        f"Current score: {merged_scores['form']['score']} / {merged_scores['form']['max']}. "
        f"{feedback['form']}"
    )
    form_deductions: list[str] = []
    if merged_scores["form"]["score"] < merged_scores["form"]["max"]:
        if not 200 <= signals["word_count"] <= 300:
            form_deductions.append(
                "The essay falls outside the ideal 200-300 word band, which reduces form marks."
            )
        if signals["bullet_line_count"] > 0:
            form_deductions.append("Bullet-point formatting is penalized for essay form.")
        if signals["all_caps_ratio"] > 0.85:
            form_deductions.append("Mostly-capitalized writing is penalized in the form criterion.")

    grammar_analysis = (
        "Grammar was judged from sentence-level error patterns and control of structure. "
        f"The deterministic pass found {signals['grammar_error_count']} grammar-related signal(s), "
        f"including {signals['grammar_pattern_hits']} pattern hit(s), and {signals['complex_sentence_count']} complex sentence(s). "
        f"Current score: {merged_scores['grammar']['score']} / {merged_scores['grammar']['max']}. "
        f"{feedback['grammar']}"
    )
    grammar_deductions: list[str] = []
    if merged_scores["grammar"]["score"] < merged_scores["grammar"]["max"]:
        if signals["grammar_error_count"] > 0:
            grammar_deductions.append(
                f"Detected grammar issues reduced the score: {signals['grammar_error_count']} issue signal(s) were found."
            )
        if signals["complex_sentence_count"] < max(2, signals["sentence_count"] // 4):
            grammar_deductions.append(
                "Sentence patterns are not varied enough to support the strongest grammar band."
            )

    linguistic_analysis = (
        "Linguistic range was judged from sentence variety and language flexibility. "
        f"The essay shows lexical diversity {_format_ratio(signals['lexical_diversity'])}, "
        f"academic word ratio {_format_ratio(signals['academic_word_ratio'])}, and "
        f"{signals['complex_sentence_count']} complex sentence(s). "
        f"Current score: {merged_scores['linguistic_range']['score']} / {merged_scores['linguistic_range']['max']}."
    )
    linguistic_deductions: list[str] = []
    if merged_scores["linguistic_range"]["score"] < merged_scores["linguistic_range"]["max"]:
        if signals["lexical_diversity"] < 0.52:
            linguistic_deductions.append("Language variety is not broad enough for the top linguistic-range band.")
        if signals["academic_word_ratio"] < 0.22:
            linguistic_deductions.append("The essay uses limited higher-register academic wording.")
        if signals["complex_sentence_count"] < max(2, signals["sentence_count"] // 3):
            linguistic_deductions.append("More varied sentence structures would strengthen linguistic range.")

    spelling_analysis = (
        "Spelling was judged at token level using the vendored dictionary and explicit misspelling checks. "
        f"The deterministic pass found {signals['spelling_error_count']} likely spelling error(s). "
        f"Current score: {merged_scores['spelling']['score']} / {merged_scores['spelling']['max']}. "
        f"{feedback['spelling']}"
    )
    spelling_deductions: list[str] = []
    if merged_scores["spelling"]["score"] < merged_scores["spelling"]["max"]:
        spelling_deductions.append(
            f"Spelling marks were reduced because {signals['spelling_error_count']} likely spelling error(s) were detected."
        )

    vocabulary_analysis = (
        "Vocabulary was judged from lexical variety, appropriateness, and precision. "
        f"The essay shows lexical diversity {_format_ratio(signals['lexical_diversity'])} and academic word ratio "
        f"{_format_ratio(signals['academic_word_ratio'])}. "
        f"Current score: {merged_scores['vocabulary']['score']} / {merged_scores['vocabulary']['max']}."
    )
    vocabulary_deductions: list[str] = []
    if merged_scores["vocabulary"]["score"] < merged_scores["vocabulary"]["max"]:
        vocabulary_deductions.append("Word choice is serviceable, but not consistently precise or wide-ranging enough for full credit.")
        if signals["generic_phrase_hits"] > 0:
            vocabulary_deductions.append("Some phrasing is generic, which weakens lexical precision.")

    if good_points:
        content_analysis = f"{content_analysis} Strength noted: {_join_examples(good_points, 1)}."
    if improvements:
        development_analysis = f"{development_analysis} Improvement direction: {_join_examples(improvements, 1)}."

    return {
        "content": {"analysis": content_analysis, "deductions": content_deductions},
        "development_structure_coherence": {
            "analysis": development_analysis,
            "deductions": development_deductions,
        },
        "form": {"analysis": form_analysis, "deductions": form_deductions},
        "grammar": {"analysis": grammar_analysis, "deductions": grammar_deductions},
        "linguistic_range": {"analysis": linguistic_analysis, "deductions": linguistic_deductions},
        "spelling": {"analysis": spelling_analysis, "deductions": spelling_deductions},
        "vocabulary": {"analysis": vocabulary_analysis, "deductions": vocabulary_deductions},
    }


async def grade_essay_hybrid(question: str, essay: str) -> dict:
    """Combine deterministic baseline scoring with bounded LLM scoring."""

    deterministic = score_essay_deterministic(question, essay)
    llm = await grade_essay(question, essay)
    merged_scores = _merge_scores(deterministic, llm)
    merged_feedback = _merge_feedback(deterministic, llm)
    good_points, improvements = _merge_points(llm)

    merged = {
        "scores": merged_scores,
        "feedback": merged_feedback,
        "details": _build_details(
            deterministic,
            merged_scores,
            merged_feedback,
            good_points,
            improvements,
        ),
    }
    merged["good_points"] = good_points
    merged["improvements"] = improvements

    validated = EssayResponse.model_validate(merged)
    return validated.model_dump()
