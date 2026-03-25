# Secure Coding Policy

## Goals

- Protect local data and user input.
- Avoid unsafe handling of backend requests and generated content.

## Rules

- Validate request and response payloads with schemas.
- Treat LLM output as untrusted until validated.
- Avoid executing user-provided content.
- Avoid writing files outside expected project paths.
- Keep environment-variable usage explicit and documented.
- Do not expose secrets or local tokens in logs or docs.

## LLM-specific guidance

- Validate JSON from the LLM before use.
- Fail safely when the LLM response is malformed.
- Avoid granting the LLM authority over unchecked system behavior.
