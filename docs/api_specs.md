# API Specifications

## Base URL

Local default:

`http://localhost:8000`

## Endpoints

### `GET /`

Returns a simple service message.

Example response:

```json
{
  "message": "PTE Essay Marker API"
}
```

### `GET /health`

Returns a lightweight health payload.

Example response:

```json
{
  "status": "ok",
  "phase": "backend_api"
}
```

### `POST /api/grade-essay`

Grades a PTE essay using the hybrid scoring pipeline:

- deterministic baseline scoring for measurable features
- LLM-generated grading and feedback
- bounded score merging
- detailed category-by-category explanations

Request body:

```json
{
  "question": "Some people believe that university students should be required to attend classes...",
  "essay": "University students should generally be required to attend classes..."
}
```

Successful response body:

```json
{
  "scores": {
    "content": { "score": 6, "max": 6 },
    "development_structure_coherence": { "score": 6, "max": 6 },
    "form": { "score": 2, "max": 2 },
    "grammar": { "score": 2, "max": 2 },
    "linguistic_range": { "score": 6, "max": 6 },
    "spelling": { "score": 2, "max": 2 },
    "vocabulary": { "score": 2, "max": 2 }
  },
  "feedback": {
    "form": "Length is within the official PTE target band of 200-300 words.",
    "grammar": "Grammar shows strong control, with accurate sentences and some complexity.",
    "spelling": "No spelling errors were detected at token level."
  },
  "good_points": [
    "Answers the question directly and maintains focus throughout."
  ],
  "improvements": [
    "A brief real-world example could make the argument even more persuasive."
  ],
  "details": {
    "content": {
      "analysis": "Content was judged against prompt relevance and task coverage...",
      "deductions": [
        "The response does not fully cover every aspect of the prompt, so content credit was reduced."
      ]
    },
    "development_structure_coherence": {
      "analysis": "Development, structure, and coherence were judged from paragraphing, progression, and linking...",
      "deductions": []
    },
    "form": {
      "analysis": "Form was judged using official PTE-style length and presentation checks...",
      "deductions": []
    },
    "grammar": {
      "analysis": "Grammar was judged from sentence-level error patterns and control of structure...",
      "deductions": []
    },
    "linguistic_range": {
      "analysis": "Linguistic range was judged from sentence variety and language flexibility...",
      "deductions": []
    },
    "spelling": {
      "analysis": "Spelling was judged at token level using the vendored dictionary and explicit misspelling checks...",
      "deductions": []
    },
    "vocabulary": {
      "analysis": "Vocabulary was judged from lexical variety, appropriateness, and precision...",
      "deductions": []
    }
  }
}
```

Example frontend-facing interpretation:

```text
Results

Overall score: 21 / 26

Detail -> Content
Analysis: Content was judged against prompt relevance and task coverage...
Why marks were deducted:
- The response does not fully cover every aspect of the prompt.
```

## Error behavior

- `422`: invalid request body
- `502`: LM Studio is unavailable, returned an empty response, or returned malformed JSON
- `500`: unexpected backend error

Example error response:

```json
{
  "detail": "Failed to contact the local LLM server: ..."
}
```

## Example cURL

```bash
curl -X POST http://localhost:8000/api/grade-essay \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Some people believe that university students should be required to attend classes.",
    "essay": "University students should generally be required to attend classes because..."
  }'
```

### `POST /api/analyze-deterministic`

Runs the deterministic scoring layer without calling the LLM.

This endpoint now uses:

- prompt-aware content relevance
- Pearson-style raw trait scoring before rubric mapping
- token-level spelling detection backed by the vendored dictionary in `data/words.txt`
- sentence-level grammar and discourse signals

Example response body:

```json
{
  "scores": {
    "content": { "score": 4, "max": 6 },
    "development_structure_coherence": { "score": 6, "max": 6 },
    "form": { "score": 2, "max": 2 },
    "grammar": { "score": 2, "max": 2 },
    "linguistic_range": { "score": 6, "max": 6 },
    "spelling": { "score": 2, "max": 2 },
    "vocabulary": { "score": 2, "max": 2 }
  },
  "feedback": {
    "form": "The response addresses the prompt directly and covers the task adequately. Length is within the official PTE target band of 200-300 words.",
    "grammar": "Grammar shows strong control, with accurate sentences and some complexity.",
    "spelling": "No spelling errors were detected at token level."
  },
  "signals": {
    "word_count": 291,
    "paragraph_count": 5,
    "sentence_count": 18,
    "transition_hits": 4,
    "typo_hits": 0,
    "grammar_pattern_hits": 0,
    "generic_phrase_hits": 0,
    "prompt_keyword_overlap": 6,
    "prompt_coverage_ratio": 0.75,
    "all_caps_ratio": 0.02,
    "bullet_line_count": 0,
    "punctuation_count": 24,
    "spelling_error_count": 0,
    "grammar_error_count": 0,
    "complex_sentence_count": 7,
    "lexical_diversity": 0.54,
    "academic_word_ratio": 0.21,
    "raw_content": 3,
    "raw_development_structure_coherence": 2,
    "raw_form": 2,
    "raw_grammar": 2,
    "raw_linguistic_range": 2,
    "raw_spelling": 2,
    "raw_vocabulary": 2
  },
  "summary": "Deterministic baseline completed using prompt relevance, token-level spelling, sentence-level grammar signals, and Pearson-style raw trait mapping."
}
```
