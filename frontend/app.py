"""Streamlit frontend for the PTE essay marker."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import error, request

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[1]

CRITERIA_LABELS = {
    "content": "Content",
    "development_structure_coherence": "Development, Structure & Coherence",
    "form": "Form",
    "grammar": "Grammar",
    "linguistic_range": "Linguistic Range",
    "spelling": "Spelling",
    "vocabulary": "Vocabulary",
}


def load_styles() -> None:
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def load_local_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = ROOT_DIR / ".env.local"
    if not env_path.exists():
        return values

    for line in env_path.read_text().splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#") or "=" not in cleaned:
            continue
        key, value = cleaned.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def get_backend_url() -> str:
    env_values = load_local_env()
    host = os.getenv("BACKEND_HOST") or env_values.get("BACKEND_HOST", "0.0.0.0")
    port = os.getenv("BACKEND_PORT") or env_values.get("BACKEND_PORT", "8000")
    if host == "0.0.0.0":
        host = "localhost"
    return f"http://{host}:{port}"


def load_sample_data() -> tuple[list[dict], list[dict]]:
    questions_path = ROOT_DIR / "data" / "sample_questions.json"
    essays_path = ROOT_DIR / "data" / "sample_essays.json"
    questions = json.loads(questions_path.read_text()) if questions_path.exists() else []
    essays = json.loads(essays_path.read_text()) if essays_path.exists() else []
    return questions, essays


def build_sample_options() -> dict[str, tuple[str, str]]:
    questions, essays = load_sample_data()
    question_lookup = {item["id"]: item["question"] for item in questions}
    options: dict[str, tuple[str, str]] = {}
    for essay in essays:
        label = f"Sample {essay['id']} - {essay['quality_level'].replace('_', ' ').title()}"
        options[label] = (question_lookup.get(essay["question_id"], ""), essay["text"])
    return options


def count_words(text: str) -> int:
    return len(text.split())


def submit_for_grading(question: str, essay: str) -> dict:
    payload = json.dumps({"question": question, "essay": essay}).encode("utf-8")
    endpoint = f"{get_backend_url()}/api/grade-essay"
    http_request = request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        try:
            body = json.loads(exc.read().decode("utf-8"))
            detail = body.get("detail", str(exc))
        except json.JSONDecodeError:
            detail = str(exc)
        raise RuntimeError(f"Backend request failed: {detail}") from exc
    except error.URLError as exc:
        raise RuntimeError(
            f"Could not reach the backend at {get_backend_url()}. Start the FastAPI server and try again."
        ) from exc


def render_scores(scores: dict) -> None:
    rows = []
    total = 0
    total_max = 0
    for key, label in CRITERIA_LABELS.items():
        item = scores[key]
        total += item["score"]
        total_max += item["max"]
        rows.append({"Criterion": label, "Score": f"{item['score']} / {item['max']}"})

    st.markdown(f"**Overall score:** `{total} / {total_max}`")
    st.table(rows)


def render_feedback(feedback: dict) -> None:
    rows = [{"Area": area.title(), "Details": details} for area, details in feedback.items()]
    st.table(rows)


def render_points(title: str, points: list[str]) -> None:
    st.markdown(f"**{title}**")
    for point in points:
        st.write(f"- {point}")


st.set_page_config(page_title="PTE Essay Marker", layout="wide")
load_styles()

if "question" not in st.session_state:
    st.session_state.question = ""
if "essay" not in st.session_state:
    st.session_state.essay = ""
if "result" not in st.session_state:
    st.session_state.result = None

st.title("PTE Essay Marker")
st.caption("Submit a PTE essay question and response to receive structured grading feedback from the backend.")

sample_options = build_sample_options()
selected_sample = st.selectbox(
    "Load a sample response",
    ["Custom entry", *sample_options.keys()],
    index=0,
)

if selected_sample != "Custom entry":
    sample_question, sample_essay = sample_options[selected_sample]
    st.session_state.question = sample_question
    st.session_state.essay = sample_essay

question = st.text_area(
    "Essay question",
    height=120,
    key="question",
    placeholder="Paste the PTE prompt here...",
)
essay = st.text_area(
    "Essay response",
    height=320,
    key="essay",
    placeholder="Write or paste the essay here...",
)

word_count = count_words(essay)
st.caption(f"Essay word count: {word_count}")
if essay and word_count < 200:
    st.warning("PTE essays are typically stronger at 200+ words. You can still submit, but the response may score lower on form and development.")

if st.button("Submit for grading", type="primary"):
    if not question.strip() or not essay.strip():
        st.error("Please provide both the essay question and essay text.")
    else:
        with st.spinner("Sending essay to the grading API..."):
            try:
                st.session_state.result = submit_for_grading(question.strip(), essay.strip())
            except RuntimeError as exc:
                st.session_state.result = None
                st.error(str(exc))

result = st.session_state.result
if result:
    st.subheader("Results")
    left_col, right_col = st.columns([1.1, 1])
    with left_col:
        st.markdown("**Score breakdown**")
        render_scores(result["scores"])
    with right_col:
        st.markdown("**Feedback**")
        render_feedback(result["feedback"])

    render_points("Good points", result["good_points"])
    render_points("Improvements", result["improvements"])
else:
    st.subheader("Results")
    st.info("Submit an essay to see score breakdowns, targeted feedback, and improvement suggestions.")
