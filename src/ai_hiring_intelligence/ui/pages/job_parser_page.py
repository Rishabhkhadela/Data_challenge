import streamlit as st
from ai_hiring_intelligence.ui.utils import get_job_parser

DEFAULT_JD_TEXT = """Role: Senior AI Engineer (Founding Team)
Company: Redrob AI
Location: Bangalore / Hybrid

We are looking for a Senior AI Engineer to join our founding team. You will lead the development of our candidate search, dense vector retrieval, and LLM-based ranking engines.

Requirements:
- 5-9 years of production software engineering experience, specifically building AI/ML systems.
- Strong proficiency in Python, PyTorch, HuggingFace transformers, and vector databases (FAISS, Milvus, or Qdrant).
- Experience with RAG (Retrieval-Augmented Generation), fine-tuning LLMs, and prompt engineering.
- Excellent behavior traits: absolute ownership, comfort with ambiguity, and product-mindedness.
- Leadership: mentoring junior engineers, driving strategy, and influencing cross-functional decisions.
"""

def render_job_parser():
    st.header("Job Description Parsing")
    st.subheader("Extract structured requirements using our LLM engine")
    
    st.markdown("""
    Paste your unstructured job description text below. Our parser will extract the key dimensions
    (Skills, Experience, Behavior Traits, and Leadership) to build the active scoring filter.
    """)

    # Job description text area
    jd_input = st.text_area("Job Description", value=st.session_state.get("jd_text", DEFAULT_JD_TEXT), height=250)
    st.session_state.jd_text = jd_input
    
    if st.button("Parse Job Description", type="primary"):
        if not jd_input.strip():
            st.error("Please enter a valid job description.")
            return

        with st.spinner("Analyzing job description text with LLM parser..."):
            try:
                parser = get_job_parser()
                parsed_dict = parser.parse(jd_input)
                st.session_state.active_requirements = parsed_dict
                st.success("Successfully parsed job description!")
            except Exception as e:
                st.error(f"Failed to parse job description: {e}")
                return

    # Display parsed requirements if present
    if "active_requirements" in st.session_state:
        reqs = st.session_state.active_requirements
        
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### Extracted Requirements Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Technical Skills")
            skills = reqs.get("skills", [])
            if skills:
                # Render as modern tags
                tags_html = "".join([f'<span class="skill-chip" style="background-color:#1E3A8A; color:#93C5FD; border-color:#2563EB;">{s}</span>' for s in skills])
                st.markdown(tags_html, unsafe_allow_html=True)
            else:
                st.info("No explicit skills extracted.")
                
            st.markdown("#### 💼 Experience Profile")
            exp = reqs.get("experience", [])
            for item in exp:
                st.markdown(f"- **{item}**")
            if not exp:
                st.info("No experience profile extracted.")
                
        with col2:
            st.markdown("#### 🧠 Behavioral Traits")
            behavior = reqs.get("behavior_traits", [])
            for item in behavior:
                st.markdown(f"- {item}")
            if not behavior:
                st.info("No behavioral traits extracted.")
                
            st.markdown("#### 👑 Leadership Expectations")
            leadership = reqs.get("leadership_requirements", [])
            for item in leadership:
                st.markdown(f"- {item}")
            if not leadership:
                st.info("No leadership expectations extracted.")
                
        st.info("💡 These requirements are now active across the Candidate Search, Rankings, and Insights pages.")
