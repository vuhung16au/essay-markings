# PTE Academic Essay Rubric

## Purpose

This document records the essay-marking rubric used by this project for `Write Essay` in PTE Academic.

It is based on the rubric notes captured in [PTE Academic Score Guide](https://www.pearsonpte.com/ctf-assets/yqwtwibiobs4/WUcBAMkYCC9Dj5vs2HfVA/941d88d07ba7c2a5007f7ce1b18eedbf/Score_Guide__Test_Taker__-_PTE_Academic_-_July_2025__web_.pdf) and is formatted here as a stable reference for implementation, calibration, and documentation.

## How to read this rubric

Each criterion contains score bands.

Example:

- `Form = 2` means the essay matches the full-credit description for `Form`
- `Form = 1` means it matches the partial-credit description
- `Form = 0` means it matches the no-credit description

The same pattern applies to the other criteria.

## Scoring categories

The essay rubric uses these criteria:

- Content `0-6`
- Form `0-2`
- Development, Structure and Coherence `1-6` in normal scoring
- Grammar `0-2`
- General Linguistic Range `0-6`
- Vocabulary Range `0-2`
- Spelling `0-2`

Maximum total score: `26`

## Content

### `6`

- The essay fully addresses the prompt in depth.
- It shows full command of the argument by reformulating the issue naturally in the writer’s own words.
- Important points are expanded with specificity.
- The argument is supported convincingly with relevant subsidiary points and examples throughout.

### `5`

- The essay adequately addresses the prompt.
- It presents a persuasive argument with relevant ideas.
- Main points are clear.
- Relevant supporting detail is given effectively, with only minor exceptions.

### `4`

- The essay adequately addresses the main point of the prompt.
- The argument is generally convincing, but lacks depth or nuance.
- Supporting detail is inconsistent and weaker for some points.

### `3`

- The essay is relevant to the prompt.
- It does not address the main points adequately.
- Supporting detail is often missing or inappropriate.

### `2`

- The essay attempts to address the prompt, but does so superficially.
- It contains little relevant information and largely generic statements.
- It may overuse language from the prompt.
- Few supporting details are included.
- Present ideas may have only tangential links to the topic.

### `1`

- The essay attempts to address the prompt, but shows incomplete understanding.
- Communication is limited to generic, repetitive, or prompt-copied phrasing.
- Supporting details, if present, are disjointed or haphazard.
- There are no clear links to the topic.

### `0`

- The essay does not properly deal with the prompt.

## Form

### `2`

- Length is between `200` and `300` words.

### `1`

- Length is between `120` and `199` words, or between `301` and `380` words.

### `0`

- Length is less than `120` words or more than `380` words.
- The essay is written in capital letters.
- The essay contains no punctuation.
- The response consists only of bullet points or very short sentences.

## Development, Structure and Coherence

### `6`

- The essay has an effective logical structure.
- It flows smoothly and can be followed with ease.
- The argument is clear, cohesive, and developed systematically at length.
- A well-developed introduction and conclusion are present.
- Ideas are organised cohesively into clear, logically sequenced paragraphs.
- A variety of connective devices is used effectively and consistently.

### `5`

- The essay has a conventional and appropriate structure.
- It follows logically, though not always smoothly.
- The argument is clear, with some points developed at length.
- Introduction, conclusion, and logical paragraphs are present.
- Connective devices link utterances into clear, coherent discourse, though some gaps or abrupt transitions may remain.

### `4`

- Conventional structure is mostly present, but some elements may be missing.
- The essay may require some effort to follow.
- An argument is present, but some elements are underdeveloped or difficult to follow.
- Paragraph breaks may be present but not always effective.
- Some elements or paragraphs are poorly linked.
- Ideas are not always well connected.

### `3`

- Traces of conventional structure are present, but the essay is made up of simple points or disconnected ideas.
- A position or opinion is present, but it is not developed into a clear logical argument.
- Paragraphing is ineffective or absent, though some logical sequencing may still be present.
- The response consists mainly of unconnected ideas and requires significant effort to follow.
- Connective devices mostly express only simple linear relationships.

### `2`

- There is little recognisable structure.
- Ideas are presented in a disorganised manner and are difficult to follow.
- A position or opinion may be present, but it lacks development or clarity.
- The essay mainly consists of disconnected elements.
- Only simple connective devices such as `and`, `but`, and `because` are used.

### `1`

- The response consists of disconnected ideas.
- There is no hierarchy of ideas or coherence among points.
- No clear position or opinion can be identified.
- Words and short statements are linked only with very basic linear connective devices such as `and` or `then`.

## Grammar

### `2`

- Shows consistent grammatical control of complex language.
- Errors are rare and difficult to spot.

### `1`

- Shows a relatively high degree of grammatical control.
- Mistakes do not lead to misunderstanding.

### `0`

- Contains mainly simple structures and/or several basic mistakes.

## General Linguistic Range

### `6`

- A variety of expressions and vocabulary are used appropriately throughout.
- Ideas are formulated with ease and precision.
- There are no clear limitations on what can be communicated.
- Errors, if present, are rare and minor.

### `5`

- A variety of expressions and vocabulary are used appropriately throughout the response.
- Ideas are expressed clearly without much sign of restriction.
- Occasional language errors may appear, but meaning is clear.

### `4`

- The range of expression and vocabulary is sufficient for basic ideas.
- Limitations appear when complex or abstract ideas are expressed.
- Repetition, circumlocution, or difficulty with formulation may appear.
- Errors cause occasional lapses in clarity, but the main idea remains understandable.

### `3`

- The range of expression and vocabulary is narrow.
- Simple expressions are used repeatedly.
- Communication is restricted to simple ideas.
- Errors in language use cause some disruption for the reader.

### `2`

- Limited vocabulary and simple expressions dominate the response.
- Communication is compromised and some ideas are unclear.
- Basic language errors are common and cause frequent breakdowns or misunderstanding.

### `1`

- Vocabulary and linguistic expression are highly restricted.
- Communication is significantly limited.
- Ideas are generally unclear.
- Errors are pervasive and impede meaning.

### `0`

- Meaning is not accessible.

## Vocabulary Range

### `2`

- Shows good command of a broad lexical repertoire.
- Idiomatic expressions and colloquialisms are used effectively where appropriate.

### `1`

- Shows a good range of vocabulary for general academic topics.
- Lexical shortcomings may lead to circumlocution or some imprecision.

### `0`

- Contains mainly basic vocabulary insufficient to deal with the topic at the required level.

## Spelling

### `2`

- Correct spelling.

### `1`

- One spelling error.

### `0`

- More than one spelling error.

## Implementation notes for this repo

This rubric is the reference point for:

- [docs/scoring.md](./scoring.md)
- [docs/api_specs.md](./api_specs.md)
- [backend/services/deterministic_scorer.py](../backend/services/deterministic_scorer.py)
- [backend/core/prompt_builder.py](../backend/core/prompt_builder.py)

If the official scoring guidance is revised later, this document should be updated first, and the scorer/docs should then be checked against it.
