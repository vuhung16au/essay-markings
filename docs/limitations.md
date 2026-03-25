# Limitations

## Purpose

This document records the main known limitations of the current system.

## LLM variability

The final grading path still includes an LLM.

Because of that:

- repeated runs may not always return identical wording
- small score variation can still happen
- benchmark tolerances are still needed

The hybrid scorer reduces this variability, but does not remove it completely.

## Not fully Pearson-equivalent

The project aims to be Pearson-aligned, but it is not an official Pearson scoring engine.

It does not reproduce:

- Pearson’s proprietary automated scoring models
- Pearson’s full training data
- Pearson’s exact semantic scoring pipeline
- Pearson’s internal scaling pipeline

## Heuristic boundaries

The deterministic layer uses practical heuristics rather than full language understanding.

This means some edge cases can still be misread, especially in:

- content depth
- structure quality
- sentence naturalness
- vocabulary precision

## Benchmark dependence

The sample benchmark set is useful, but limited.

It does not cover every:

- prompt type
- essay style
- borderline response
- spelling or grammar edge case

## Spelling limitations

The spelling system is much more portable now, but still has limits:

- rare proper nouns may be flagged incorrectly
- unusual domain vocabulary may need explicit handling
- mixed spelling conventions are detected through a practical rule set, not a full linguistic model

## Feedback limitations

The learner-facing report is designed to be clear and helpful, but:

- feedback quality still depends partly on LLM output
- some category explanations may be stronger than others
- example-based coaching may not always capture the single best sentence to quote

## Report limitations

- export formatting is simpler than the live UI
- long responses can render differently across Markdown, Word, and PDF
- report wording can vary slightly across runs

## Operational limitations

The project assumes a local development workflow.

It currently depends on:

- local environment setup
- LM Studio availability or an OpenAI-compatible API key
- matching local model configuration

## Recommendation

Treat this system as:

- a strong learning and feedback tool
- a rubric-aligned grading assistant
- a stable local benchmarked scorer

Do not present it as an official Pearson scoring engine.
