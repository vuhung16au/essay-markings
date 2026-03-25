# Scoring System

## Overview

The project now uses the Pearson-style rubric in [Pearson-PTE-rubrics.md](/Users/vuhung/00.Work/00.Workspace/essay-markings/TODOs/Pearson-PTE-rubrics.md) as the main scoring reference for essays.

The grading flow is:

1. A deterministic scorer evaluates measurable rubric signals.
2. The LLM adds qualitative judgment and feedback.
3. A hybrid merger keeps the final score close to the rubric-aware deterministic baseline.
4. The frontend shows scores, category details, and improvement guidance.

Maximum total score: `26`

## Scoring categories

- Content `0-6`
- Development, Structure & Coherence `1-6` in normal scoring, with `0` possible through content/form gating
- Form `0-2`
- Grammar `0-2`
- Linguistic Range `0-6`
- Spelling `0-2`
- Vocabulary `0-2`

## Direct Pearson-style bands

The deterministic scorer now works directly in the essay rubric bands instead of using the older compressed raw-to-display mapping.

### Content `0-6`

- `6`: fully addresses the prompt in depth with specific and convincing support
- `5`: addresses the prompt well with relevant support and only minor weaknesses
- `4`: addresses the main point, but support or depth is uneven
- `3`: relevant, but main points are not developed adequately
- `2`: superficial, generic, repetitive, or only weakly linked to the topic
- `1`: incomplete understanding of the prompt with disjointed support
- `0`: does not properly deal with the prompt

### Development, Structure & Coherence `1-6`

- `6`: effective logical structure, smooth flow, clear cohesive argument, strong introduction/conclusion, and well-sequenced paragraphs
- `5`: conventional and appropriate structure with mostly clear flow
- `4`: mostly present structure, but some linking or sequencing is weak
- `3`: only traces of full structure; ideas are partly connected
- `2`: weak structure with disorganized ideas and only simple linking
- `1`: disconnected ideas with no clear hierarchy or argument

### Form `0-2`

- `2`: `200-300` words
- `1`: `120-199` or `301-380` words
- `0`: under `120`, over `380`, or major form problems such as all-caps, bullet formatting, or non-prose structure

### Grammar `0-2`

- `2`: consistent grammatical control of complex language, with rare hard-to-spot errors
- `1`: relatively high grammatical control; mistakes do not cause misunderstanding
- `0`: mainly simple structures and/or several basic mistakes

### General Linguistic Range `0-6`

- `6`: varied, precise, and flexible language throughout
- `5`: clear variety with only occasional language errors
- `4`: enough range for basic ideas, but limitations appear with more complex meaning
- `3`: narrow and repetitive expression with some disruption to clarity
- `2`: limited language frequently compromises communication
- `1`: highly restricted expression with pervasive meaning problems
- `0`: meaning is not accessible

### Vocabulary `0-2`

- `2`: broad lexical repertoire with strong academic phrasing
- `1`: good general academic range, but some imprecision remains
- `0`: mainly basic vocabulary, insufficient for the topic level

### Spelling `0-2`

- `2`: correct spelling
- `1`: one spelling error
- `0`: more than one spelling error

## Deterministic signals used

The deterministic scorer considers measurable signals that support the rubric:

### Content

- prompt relevance
- prompt keyword coverage
- support/example markers
- clear position markers
- generic or formulaic phrasing penalties

### Development, Structure & Coherence

- paragraph structure
- introduction/conclusion presence
- body paragraph count
- transition/connective markers
- signs of logical progression and opinion control

### Form

- word-count bands
- all-caps detection
- bullet formatting
- punctuation/prose checks

### Grammar

- sentence-level grammar patterns
- agreement and article errors
- run-on indicators
- missing sentence-ending punctuation
- complexity versus accuracy balance

### Linguistic Range

- lexical diversity
- academic-word ratio
- sentence complexity ratio
- grammar control interaction

### Vocabulary

- lexical variety
- academic wording
- generic/repetitive phrasing penalties

### Spelling

- token-level spelling checks
- vendored SCOWL-based dictionary in [data/words.txt](/Users/vuhung/00.Work/00.Workspace/essay-markings/data/words.txt)
- explicit misspelling detection for common errors
- accepted US, UK, Canadian, and Australian spelling variants
- consistency checks for mixed spelling conventions within one essay

Source notes for the dictionary are in [words.SOURCE.md](/Users/vuhung/00.Work/00.Workspace/essay-markings/data/words.SOURCE.md).

## Pearson-style hard gates

Two gating rules are enforced:

1. If `content = 0`, all remaining traits are zeroed.
2. If `form = 0`, the remaining traits are zeroed after content.

These gates prevent off-topic or invalid-form essays from receiving inflated scores elsewhere.

## Hybrid scoring behavior

The final score is not pure LLM output.

Instead:

- the deterministic scorer sets the rubric-aware baseline
- the LLM provides judgment and feedback
- the hybrid merger clamps the LLM to stay near the deterministic score
- `form` and `spelling` remain strongly deterministic
- weak grammar/spelling can still cap higher-band categories

This keeps scoring more stable than pure LLM marking while still allowing richer comments and suggestions.

## Current sample benchmark notes

The sample fixture file [expected_outputs.json](/Users/vuhung/00.Work/00.Workspace/essay-markings/data/expected_outputs.json) now reflects the current rubric implementation rather than the older calibration set.

One important example:

- Sample 1 is slightly above `300` words, so under the current `Form` rubric it receives `1/2`, not `2/2`.

This is intentional and matches the official band definition now used by the scorer.

## How to interpret scores

### High score

A high-scoring essay usually:

- answers the prompt fully and directly
- develops ideas with relevant support
- has a clear logical structure
- uses controlled grammar and precise language
- stays within the ideal form band

### Mid-range score

A mid-range essay usually:

- stays relevant but lacks depth
- has understandable structure with weaker linking
- contains noticeable language limitations
- needs stronger examples or clearer development

### Low score

A low-scoring essay usually:

- is superficial or partly underdeveloped
- has weak structure or disconnected ideas
- contains repeated grammar or spelling problems
- relies on basic or repetitive wording

## Detail section in the UI

The frontend `Detail` section is written for learners, not for internal debugging.

It focuses on:

- what each category score means
- why marks were deducted
- examples taken from the user’s own essay
- concrete next steps for improvement

It intentionally avoids exposing internal scoring formulas or raw metric values.

## Exported report contents

The exported essay report includes:

- essay question
- submitted essay
- overall score
- category breakdown
- comments and feedback for each category
- deduction reasons
- suggestions for improvement

Available export formats:

- Markdown
- Word
- PDF

## Spelling convention rule

Valid spellings from US, UK, Canadian, and Australian English are accepted.

However, Pearson-style consistency is enforced inside a single essay:

- `color` + `organize`: accepted
- `colour` + `organise`: accepted
- `color` + `organise`: inconsistent, so spelling is reduced

If the essay mixes conventions, the result report will explain that the issue is inconsistency, not that one valid variant is inherently wrong.
