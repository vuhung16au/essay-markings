"""Hybrid essay grading that combines deterministic scoring with LLM feedback."""

from __future__ import annotations

import re

from core.schemas import EssayResponse
from services.deterministic_scorer import score_essay_deterministic
from services.llm_service import grade_essay


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(value, upper))


def _merge_scores(deterministic: dict, llm: dict) -> dict:
    det_scores = deterministic["scores"]
    llm_scores = llm["scores"]
    signals = deterministic.get("signals", {})

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
        elif key == "development_structure_coherence":
            final_score = _clamp(llm_score, max(0, det_score - 1), min(max_score, det_score + 1))
        else:
            final_score = _clamp(llm_score, max(0, det_score - 1), min(max_score, det_score + 1))

        merged[key] = {"score": final_score, "max": max_score}

    if signals.get("spelling_error_count", 0) >= 1 and merged["grammar"]["score"] <= 1:
        merged["development_structure_coherence"]["score"] = min(
            merged["development_structure_coherence"]["score"],
            3,
        )
        merged["linguistic_range"]["score"] = min(
            merged["linguistic_range"]["score"],
            2 if merged["grammar"]["score"] == 1 else 1,
        )
        merged["vocabulary"]["score"] = min(merged["vocabulary"]["score"], 1)

    if signals.get("grammar_error_count", 0) >= 4:
        merged["development_structure_coherence"]["score"] = min(
            merged["development_structure_coherence"]["score"],
            2,
        )
        merged["linguistic_range"]["score"] = min(
            merged["linguistic_range"]["score"],
            1,
        )

    return merged


def _merge_feedback(deterministic: dict, llm: dict) -> dict:
    det_feedback = deterministic["feedback"]
    llm_feedback = llm["feedback"]

    feedback = {}
    feedback["form"] = det_feedback.get("form", "").strip()
    feedback["spelling"] = det_feedback.get("spelling", "").strip()

    llm_text = llm_feedback.get("grammar", "").strip()
    det_text = det_feedback.get("grammar", "").strip()
    feedback["grammar"] = llm_text or det_text
    return feedback


def _merge_points(llm: dict) -> tuple[list[str], list[str]]:
    good_points = llm.get("good_points") or ["Shows effort in addressing the essay task."]
    improvements = llm.get("improvements") or ["Develop the argument with clearer examples and tighter language."]
    return good_points[:5], improvements[:5]


def _join_examples(points: list[str], limit: int = 2) -> str:
    selected = [point.strip().rstrip(".") for point in points[:limit] if point.strip()]
    return "; ".join(selected)


def _essay_sentences(essay: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", essay.strip())
    return [part.strip() for part in parts if part.strip()]


def _essay_paragraphs(essay: str) -> list[str]:
    return [part.strip() for part in essay.split("\n\n") if part.strip()]


def _quote(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3].rstrip() + "..."


def _extract_feedback_example(text: str) -> str | None:
    match = re.search(r"'([^']+)'", text)
    if match:
        return match.group(1).strip()
    return None


def _extract_feedback_examples(text: str) -> list[str]:
    return [match.strip() for match in re.findall(r"'([^']+)'", text)]


def _find_sentence_containing(sentences: list[str], phrase: str | None) -> str | None:
    if not phrase:
        return None
    lowered = phrase.lower()
    for sentence in sentences:
        if lowered in sentence.lower():
            return sentence
    return None


def _first_argument_sentence(sentences: list[str]) -> str | None:
    for sentence in sentences:
        lowered = sentence.lower()
        if lowered.startswith(("first", "second", "for instance", "for example", "another", "however")):
            return sentence
    for sentence in sentences[1:]:
        if len(sentence.split()) >= 8:
            return sentence
    return sentences[0] if sentences else None


def _build_details(
    deterministic: dict,
    merged_scores: dict,
    feedback: dict,
    good_points: list[str],
    improvements: list[str],
    essay: str,
) -> dict:
    signals = deterministic["signals"]
    sentences = _essay_sentences(essay)
    paragraphs = _essay_paragraphs(essay)
    first_argument = _first_argument_sentence(sentences)
    grammar_example_phrase = _extract_feedback_example(feedback["grammar"])
    grammar_example_sentence = _find_sentence_containing(sentences, grammar_example_phrase)
    spelling_example = _extract_feedback_example(feedback["spelling"])
    spelling_examples = _extract_feedback_examples(feedback["spelling"])

    content_analysis = (
        "This score reflects how clearly the essay answers the question and how fully the main ideas are developed. "
        "The response stays on the topic, but it does not yet address the task with enough depth and completeness "
        "to reach the highest band."
    )
    content_deductions: list[str] = []
    if merged_scores["content"]["score"] < merged_scores["content"]["max"]:
        content_deductions.append(
            "Some parts of the response need fuller explanation or more direct support for the main argument."
        )
        if signals["prompt_coverage_ratio"] < 0.75:
            content_deductions.append(
                "The essay would be stronger if it addressed the question more completely and directly throughout."
            )
        if first_argument:
            content_deductions.append(
                f'Your essay writes: "{_quote(first_argument)}" This point is relevant, but it would score more strongly if you added a concrete example, explanation, or result.'
            )
        if improvements:
            content_deductions.append(
                f"To improve this, expand one of your main points with a specific example. Suggested next step: {_join_examples(improvements, 1)}."
            )

    development_analysis = (
        "This score reflects how well the essay is organized, how smoothly ideas connect, and how clearly the argument progresses. "
        "The response shows an understandable direction, but the flow between points can still be improved."
    )
    development_deductions: list[str] = []
    if merged_scores["development_structure_coherence"]["score"] < merged_scores["development_structure_coherence"]["max"]:
        if signals["paragraph_count"] < 4:
            development_deductions.append("The essay needs clearer paragraph development to make each main point stand out.")
        if signals["transition_hits"] < 2:
            development_deductions.append("Ideas do not always connect smoothly, so the argument can feel abrupt in places.")
        development_deductions.append(
            "Some arguments or examples need clearer sequencing and stronger logical links."
        )
        if first_argument:
            development_deductions.append(
                f'Your essay writes: "{_quote(first_argument)}" The idea itself is useful, but it would be easier to follow if it were introduced, explained, and then linked clearly to the next point.'
            )
            development_deductions.append(
                "To improve this, place one main idea in each paragraph and end the paragraph by linking it back to your overall argument."
            )
        elif len(paragraphs) <= 1:
            development_deductions.append(
                "To improve this, separate the essay into a clear introduction, body paragraphs, and conclusion so each idea has its own space."
            )

    form_analysis = (
        "This score reflects whether the essay is presented in an appropriate academic essay format and stays within the expected length range. "
        f"{feedback['form']}"
    )
    form_deductions: list[str] = []
    if merged_scores["form"]["score"] < merged_scores["form"]["max"]:
        if not 200 <= signals["word_count"] <= 300:
            form_deductions.append(
                "The essay is outside the ideal length range for a strong PTE response."
            )
        if signals["bullet_line_count"] > 0:
            form_deductions.append("The response should be written as a continuous essay rather than as bullet points.")
        if signals["all_caps_ratio"] > 0.85:
            form_deductions.append("Using capital letters throughout weakens the formal presentation of the essay.")
        form_deductions.append(
            "To improve this, keep the essay in standard paragraph form and aim for a clear academic structure within the target length."
        )

    grammar_analysis = (
        "This score reflects the accuracy and control of sentence construction across the essay. "
        f"{feedback['grammar']}"
    )
    grammar_deductions: list[str] = []
    if merged_scores["grammar"]["score"] < merged_scores["grammar"]["max"]:
        if signals["grammar_error_count"] > 0:
            grammar_deductions.append(
                "Grammar mistakes reduce clarity and make some sentences sound less controlled."
            )
        if signals["complex_sentence_count"] < max(2, signals["sentence_count"] // 4):
            grammar_deductions.append(
                "Using a wider range of accurate sentence patterns would strengthen this category."
            )
        if grammar_example_sentence:
            grammar_deductions.append(
                f'Your essay writes: "{_quote(grammar_example_sentence)}" This sentence would be stronger if the grammar were tightened so the meaning sounds more natural and precise.'
            )
        elif grammar_example_phrase:
            grammar_deductions.append(
                f'One phrase to review is "{grammar_example_phrase}". Rewrite it as a complete, natural sentence that fits smoothly into the paragraph.'
            )
        grammar_deductions.append(
            "To improve this, revise sentences with article, verb-form, or phrasing problems and read them aloud to check whether they sound complete and natural."
        )

    linguistic_analysis = (
        "This score reflects how flexibly the essay uses language, including sentence variety and the ability to express ideas clearly. "
        "The language is effective overall, but there is still room for more variety and control."
    )
    linguistic_deductions: list[str] = []
    if merged_scores["linguistic_range"]["score"] < merged_scores["linguistic_range"]["max"]:
        if signals["lexical_diversity"] < 0.52:
            linguistic_deductions.append("The essay would benefit from a broader range of sentence styles and expressions.")
        if signals["academic_word_ratio"] < 0.22:
            linguistic_deductions.append("More precise academic-style language would strengthen the overall range.")
        if signals["complex_sentence_count"] < max(2, signals["sentence_count"] // 3):
            linguistic_deductions.append("More varied sentence structures would make the writing sound more mature and flexible.")
        if first_argument:
            linguistic_deductions.append(
                f'Your essay writes: "{_quote(first_argument)}" This idea is clear, but it could sound more advanced if you varied the sentence structure and used more precise phrasing.'
            )
        linguistic_deductions.append(
            "To improve this, combine simple and complex sentence forms and vary how you introduce reasons, examples, and conclusions."
        )

    spelling_analysis = (
        "This score reflects spelling accuracy across the essay. "
        f"{feedback['spelling']}"
    )
    spelling_deductions: list[str] = []
    if merged_scores["spelling"]["score"] < merged_scores["spelling"]["max"]:
        if "mixes conventions" in feedback["spelling"].lower() and len(spelling_examples) >= 2:
            spelling_deductions.append(
                "The essay mixes accepted spelling conventions within the same response, so it did not receive full spelling credit."
            )
            spelling_deductions.append(
                f'Your essay uses both "{spelling_examples[0]}" and "{spelling_examples[1]}". Both forms can be valid, but they should not be mixed in one essay.'
            )
            spelling_deductions.append(
                "To improve this, choose one spelling convention for the entire essay and keep it consistent from beginning to end."
            )
        else:
            spelling_deductions.append(
                "A spelling mistake was found, so the essay did not receive full marks for spelling."
            )
            if spelling_example:
                spelling_deductions.append(
                    f'Your essay writes: "{spelling_example}". Check this word carefully and replace it with the correct spelling in the final draft.'
                )
            spelling_deductions.append(
                "To improve this, leave time for a final spelling check, especially for common errors and contractions."
            )

    vocabulary_analysis = (
        "This score reflects the precision, appropriateness, and range of word choice used in the essay. "
        "The vocabulary supports the message, but higher-band responses show more precise and varied wording."
    )
    vocabulary_deductions: list[str] = []
    if merged_scores["vocabulary"]["score"] < merged_scores["vocabulary"]["max"]:
        vocabulary_deductions.append("Word choice is clear, but not consistently precise or wide-ranging enough for full credit.")
        if signals["generic_phrase_hits"] > 0:
            vocabulary_deductions.append("Some expressions are too general, which weakens the impact of the argument.")
        if first_argument:
            vocabulary_deductions.append(
                f'Your essay writes: "{_quote(first_argument)}" This communicates the idea, but a more precise verb or noun choice would make the argument stronger.'
            )
        vocabulary_deductions.append(
            "To improve this, replace general words with more exact academic vocabulary and avoid repeating the same wording across paragraphs."
        )

    if good_points:
        content_analysis = f"{content_analysis} Strength noted: {_join_examples(good_points, 1)}."
    if improvements:
        development_analysis = f"{development_analysis} A useful next step would be: {_join_examples(improvements, 1)}."

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
            essay,
        ),
    }
    merged["good_points"] = good_points
    merged["improvements"] = improvements

    validated = EssayResponse.model_validate(merged)
    return validated.model_dump()
