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

Grades a PTE essay using the local LM Studio model and returns validated JSON.

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
    "form": "Good, no form errors detected.",
    "grammar": "Grammar is accurate and varied throughout the essay.",
    "spelling": "No spelling errors detected."
  },
  "good_points": [
    "Answers the question directly and maintains focus throughout."
  ],
  "improvements": [
    "A brief real-world example could make the argument even more persuasive."
  ]
}
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
