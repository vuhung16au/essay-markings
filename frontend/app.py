"""Phase 1 placeholder Streamlit application."""

from pathlib import Path

import streamlit as st


def load_styles() -> None:
    css_path = Path(__file__).parent / "assets" / "styles.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


st.set_page_config(page_title="PTE Essay Marker", layout="wide")
load_styles()

st.title("PTE Essay Marker")
st.caption("Phase 1 scaffold: UI layout only, grading workflow pending.")

question = st.text_area("Essay question", height=120, placeholder="Paste the PTE prompt here...")
essay = st.text_area("Essay response", height=320, placeholder="Write or paste the essay here...")

if st.button("Submit for grading", type="primary"):
    if not question.strip() or not essay.strip():
        st.error("Please provide both the essay question and essay text.")
    else:
        st.info("Phase 1 scaffold complete. Live grading will be added in a later phase.")

st.subheader("Planned result layout")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Score breakdown**")
    st.table(
        {
            "Criterion": [
                "Content",
                "Development, Structure & Coherence",
                "Form",
                "Grammar",
                "Linguistic Range",
                "Spelling",
                "Vocabulary",
            ],
            "Score": ["-", "-", "-", "-", "-", "-", "-"],
        }
    )

with col2:
    st.markdown("**Feedback**")
    st.table(
        {
            "Area": ["Form", "Grammar", "Spelling"],
            "Details": ["Pending implementation", "Pending implementation", "Pending implementation"],
        }
    )

st.markdown("**Good points**")
st.write("- Placeholder for positive feedback")

st.markdown("**Improvements**")
st.write("- Placeholder for improvement suggestions")
