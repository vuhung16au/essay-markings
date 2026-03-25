# Spelling Policy

## Purpose

This document defines how spelling is handled in the project.

## Accepted spelling conventions

The project accepts valid spellings from:

- American English
- British English
- Canadian English
- Australian English

A valid variant is not penalized just because it belongs to one English convention instead of another.

## Consistency rule

Within a single essay, spelling should remain consistent.

Examples:

- `color` + `organize` -> accepted
- `colour` + `organise` -> accepted
- `color` + `organise` -> inconsistent within one essay

When conventions are mixed in the same essay, the spelling score can be reduced.

## Dictionary source

The spelling checker uses the vendored word list in [data/words.txt](../data/words.txt).

That file is generated from SCOWL and documented in [data/words.SOURCE.md](../data/words.SOURCE.md).

This avoids OS-dependent reliance on system dictionaries.

## What counts as a spelling issue

The spelling scorer considers:

- token-level misspellings
- explicit known misspellings
- mixed accepted spelling conventions within one essay

Examples of explicit misspellings currently handled include:

- `childrens`
- `dont`

## What does not count as a spelling issue by itself

- valid US spelling
- valid UK spelling
- valid AU spelling
- valid Canadian spelling
- domain terms intentionally allowlisted by the project

## Edge cases

Some tokens may need special treatment:

- proper nouns
- abbreviations
- project-specific terms
- hyphenated forms
- contractions

When a valid token is repeatedly misclassified, the first fixes to consider are:

- dictionary coverage
- normalization rules
- allowlist policy

## User-facing feedback

If spelling is reduced because of inconsistency, the result report should explain:

- both forms may be valid individually
- the issue is inconsistency within one essay
- the learner should choose one convention and keep it throughout the response

## Related files

- [docs/scoring.md](./scoring.md)
- [data/words.SOURCE.md](../data/words.SOURCE.md)
- [backend/services/deterministic_scorer.py](../backend/services/deterministic_scorer.py)
