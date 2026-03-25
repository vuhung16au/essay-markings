# Scoring System

## Overview

The project uses a hybrid scoring system designed to be more stable than pure LLM marking while staying close to Pearson/PTE essay criteria.

The current flow is:

1. Deterministic analysis calculates measurable signals from the essay.
2. The LLM provides qualitative grading and feedback.
3. The hybrid grader merges the two under scoring rules and gates.
4. The frontend shows both the scores and the reasoning behind them.

## Scoring categories

The app scores these categories:

- Content `0-6`
- Development, Structure & Coherence `0-6`
- Form `0-2`
- Grammar `0-2`
- Linguistic Range `0-6`
- Spelling `0-2`
- Vocabulary `0-2`

Maximum total: `26`

## Internal raw-trait model

To stay closer to Pearson, the deterministic scorer first works in a raw trait space, then maps to the app rubric:

- Content: `0-3`
- Development, Structure & Coherence: `0-2`
- Form: `0-2`
- Grammar: `0-2`
- General Linguistic Range: `0-2`
- Spelling: `0-2`
- Vocabulary: `0-2`

Rubric mapping:

- Content: raw `0/1/2/3` -> app `0/2/4/6`
- Development: raw `0/1/2` -> app `0/3/6`
- Form: raw `0/1/2` -> app `0/1/2`
- Grammar: raw `0/1/2` -> app `0/1/2`
- Spelling: raw `0/1/2` -> app `0/1/2`
- Vocabulary: raw `0/1/2` -> app `0/1/2`
- Linguistic Range: derived from raw linguistic range plus vocabulary, capped at `6`

## Deterministic factors considered

The deterministic scorer currently considers:

### Content

- prompt keyword overlap
- prompt coverage ratio
- paragraph count
- generic or formulaic phrasing

### Development, Structure & Coherence

- paragraph count
- transition markers
- presence of conclusion-style ending
- body paragraph structure

### Form

- official PTE-style word count thresholds
- all-caps detection
- bullet formatting
- minimum punctuation / prose structure

### Grammar

- sentence-level grammar patterns
- modal + verb-form issues
- article mismatch patterns
- lowercase sentence starts
- missing sentence-ending punctuation
- run-on style long sentences
- complex sentence count

### Spelling

- token-level spelling detection
- vendored SCOWL-generated dictionary in [data/words.txt](/Users/vuhung/00.Work/00.Workspace/essay-markings/data/words.txt)
- known misspelling checks such as `childrens` and `dont`

Source and generation notes are recorded in [words.SOURCE.md](/Users/vuhung/00.Work/00.Workspace/essay-markings/data/words.SOURCE.md).

### Linguistic Range

- lexical diversity
- academic word ratio
- complex sentence ratio

### Vocabulary

- lexical variety
- lexical precision
- generic phrase usage
- academic wording ratio

## Hard scoring gates

Two important Pearson-style gates are enforced:

1. If `content = 0`, all other categories are zeroed.
2. If `form = 0`, the remaining traits are zeroed after content.

This prevents a badly off-topic or invalid-form response from receiving inflated marks elsewhere.

## Form thresholds

The app now uses official-style form ranges:

- `2/2`: `200-300` words
- `1/2`: `120-199` or `301-380` words
- `0/2`: below `120` or above `380`, or major form issues such as all-caps / bullet formatting / non-prose structure

## How the hybrid score works

The hybrid grader does not allow the LLM to control final numeric scores unchecked.

Instead:

- deterministic scoring anchors measurable categories
- the LLM contributes grading judgment and narrative feedback
- merged scores are bounded so the final score stays close to the deterministic baseline
- `form` and `spelling` are especially deterministic
- content/form gates cannot be bypassed by the LLM

## How to interpret scores

### High score

A high-scoring essay usually:

- addresses the prompt directly and fully
- has clear paragraphing and progression
- stays within the target word range
- contains few or no grammar/spelling issues
- uses varied, precise, and reasonably academic language

### Mid-range score

A mid-range essay usually:

- answers the prompt, but not completely
- has some structure but uneven development
- contains noticeable grammar or vocabulary limitations
- may have weaker examples or generic reasoning

### Low score

A low-scoring essay usually:

- is partly or fully off-topic
- is too short, too long, or poorly formatted
- contains repeated grammar or spelling issues
- lacks paragraph control and logical flow
- uses basic or repetitive language

## Detail section in the UI

The frontend results page includes a `Detail` section for each category.

Each category shows:

- the assigned score
- a detailed explanation of how it was judged
- specific reasons for deducted marks, when applicable

This is meant to make the grading process transparent rather than score-only.

Example UI-style detail excerpt:

```text
Detail

Content (4 / 6)
Content was judged against prompt relevance and task coverage. The essay matched 5 prompt keywords with a coverage ratio of 0.62.

Why marks were deducted
- The response does not fully cover every aspect of the prompt.
- Prompt coverage remained below the strongest band.

Grammar (1 / 2)
Grammar was judged from sentence-level error patterns and control of structure.

Why marks were deducted
- Detected grammar issues reduced the score.
```

## Exported report contents

The exported essay report includes:

- essay question
- submitted essay
- overall score
- breakdown by category
- category comments and feedback
- deduction reasons
- suggestions for improvement

Available export formats:

- Markdown
- Word
- PDF

Example exported Markdown report excerpt:

```md
## Detailed breakdown of scores

| Category | Score |
| --- | --- |
| Content | 4 / 6 |
| Development, Structure & Coherence | 6 / 6 |
| Form | 2 / 2 |
| Grammar | 1 / 2 |
| Linguistic Range | 5 / 6 |
| Spelling | 2 / 2 |
| Vocabulary | 1 / 2 |

### Vocabulary (1 / 2)
Vocabulary was judged from lexical variety, appropriateness, and precision.

Reasons for deducted marks:
- Word choice is serviceable, but not consistently precise or wide-ranging enough for full credit.
```

## Example interpretation

Example:

- Content: `4/6`
- Development: `3/6`
- Form: `2/2`
- Grammar: `1/2`
- Linguistic Range: `4/6`
- Spelling: `2/2`
- Vocabulary: `1/2`

Likely interpretation:

- The essay is relevant and acceptable, but does not fully develop the task.
- Organization is present, but linking or paragraph progression is uneven.
- Form is acceptable.
- Grammar has some noticeable sentence-level problems.
- Language range and vocabulary are adequate, but not strong enough for top-band precision.

## How to improve scores

### Improve Content

- answer every part of the prompt directly
- maintain a clear stance
- add specific supporting reasons or examples

### Improve Development, Structure & Coherence

- use a clear introduction, body, and conclusion
- keep one main idea per paragraph
- add stronger transitions between points

### Improve Form

- stay close to `200-300` words
- write in full prose, not bullet points
- use normal sentence punctuation

### Improve Grammar

- check subject-verb agreement
- avoid repeated article and verb-form errors
- use a mix of simple and complex sentence structures

### Improve Linguistic Range

- vary sentence openings and clause structures
- use a wider range of academic expressions
- avoid repeating the same sentence pattern

### Improve Spelling

- review final drafts carefully
- fix contractions and plural forms
- watch repeated known mistakes

### Improve Vocabulary

- replace generic wording with more precise terms
- use topic-relevant academic vocabulary
- avoid repeating the same key words too often

## Current limitations

The system is more stable than a pure LLM workflow, but it is still an approximation.

Main remaining gaps:

- content relevance is still keyword-oriented rather than full semantic modeling
- grammar analysis is signal-based rather than full parser-based
- discourse scoring is simpler than Pearson’s production system
- final scores still include LLM influence, even though it is bounded
