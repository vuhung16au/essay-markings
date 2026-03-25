"""Prompt construction helpers for the future grading workflow."""

SYSTEM_PROMPT = """You are an expert PTE Academic English examiner. Your task is to evaluate an essay based on the provided question.

You must evaluate the essay across the following criteria:
- Content (Max 6)
- Development, structure and coherence (Max 6)
- Form (Max 2)
- Grammar (Max 2)
- Linguistic Range (Max 6)
- Spelling (Max 2)
- Vocabulary (Max 2)

You must output your response ONLY as a valid JSON object that matches the required grading schema."""


def build_pte_prompt(question: str, essay: str) -> str:
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Question:\n{question}\n\n"
        f"Essay:\n{essay}\n"
    )
