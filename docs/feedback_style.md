# Feedback Style Guide

## Purpose

This document defines how learner-facing essay feedback should be written in this project.

The goal is to make feedback:

- clear
- specific
- actionable
- supportive
- consistent with the assigned score

## Audience

The target audience is learners who want to understand:

- why they received a score
- what reduced their marks
- how to improve their next essay

## Core rules

- Write for learners, not graders.
- Use plain language.
- Explain the result without exposing the internal scoring algorithm.
- Keep feedback aligned with the final displayed score.
- Prefer specific examples from the learner’s own essay.

## What feedback should include

Each category detail should aim to include:

- what the category measures
- what the essay did well, if relevant
- why marks were deducted
- a concrete next step
- an example from the user’s essay when possible

## Deduction wording

Good deduction wording:

- explains the weakness clearly
- ties the weakness to the category
- avoids vague statements such as “needs improvement”

Prefer:

- “Some ideas are relevant, but they are not developed with enough explanation.”
- “The argument is clear, but links between paragraphs are not always smooth.”
- “One spelling error reduced the score in this category.”

Avoid:

- “The algorithm detected low coherence.”
- “Coverage ratio was below threshold.”
- “Feature count was insufficient.”

## Example-based coaching

When possible, feedback should quote or paraphrase a sentence from the learner’s essay and then explain:

1. what is weak about it
2. why that affects the score
3. how it could be improved

Example structure:

- `Your essay writes: "..."`  
- `This point is relevant, but ...`
- `To improve this, ...`

## What not to expose

Do not expose:

- internal thresholds
- raw scoring formulas
- feature counts
- signal names
- prompt-engineering logic
- deterministic versus LLM conflict details

Users should see a grading explanation, not a system trace.

## Tone guidelines

- Be constructive, not harsh.
- Be direct, but not discouraging.
- Avoid exaggeration.
- Avoid making the learner feel punished.
- Prefer “To improve this...” over “This is bad because...”

## Strengths and improvements

The report should distinguish between:

- strengths to keep
- weaknesses to fix

This helps learners understand both what is working and what should change.

## Consistency rules

Feedback must remain consistent with:

- the final score
- the final spelling decision
- the final form decision
- the final grammar decision

If a category receives full marks, avoid deduction-style wording in that category.

## Related files

- [docs/scoring.md](./scoring.md)
- [docs/report_exports.md](./report_exports.md)
- [backend/services/hybrid_grader.py](../backend/services/hybrid_grader.py)
