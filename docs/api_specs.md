# API Specifications

## Planned endpoint

### `POST /api/grade-essay`

Request body:

```json
{
  "question": "Essay prompt text",
  "essay": "Essay body text"
}
```

Planned response shape:

```json
{
  "scores": {
    "content": { "score": 0, "max": 6 },
    "development_structure_coherence": { "score": 0, "max": 6 },
    "form": { "score": 0, "max": 2 },
    "grammar": { "score": 0, "max": 2 },
    "linguistic_range": { "score": 0, "max": 6 },
    "spelling": { "score": 0, "max": 2 },
    "vocabulary": { "score": 0, "max": 2 }
  },
  "feedback": {
    "form": "string",
    "grammar": "string",
    "spelling": "string"
  },
  "good_points": ["string"],
  "improvements": ["string"]
}
```

## Phase 1 note

The API module exists as a scaffold only. Production grading behavior will be implemented in a later phase.
