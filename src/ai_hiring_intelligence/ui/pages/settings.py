import streamlit as st

def render_settings():
    st.header("System Settings")
    st.subheader("Configure scoring weights and dataset profiles")

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 1. Weights configuration
    st.markdown("### 🎚️ Candidate Scoring Weights")
    st.markdown("Adjust the weight factors for each scoring component. Component scores are normalized to sum to 100%.")

    # Get current weights from state
    weights = st.session_state.setdefault("ranking_weights", {
        "skill": 0.35,
        "behavior": 0.20,
        "career": 0.20,
        "experience": 0.25
    })

    w_skill = st.slider("Skills Weight (Core skills & platform assessments)", 0.0, 1.0, weights["skill"], step=0.05)
    w_behavior = st.slider("Behavior Weight (Completeness, responsiveness, connections)", 0.0, 1.0, weights["behavior"], step=0.05)
    w_career = st.slider("Career Weight (Role progression & industry alignment)", 0.0, 1.0, weights["career"], step=0.05)
    w_experience = st.slider("Experience Weight (Tenure match against target range)", 0.0, 1.0, weights["experience"], step=0.05)

    total_w = w_skill + w_behavior + w_career + w_experience
    if total_w <= 0:
        st.error("At least one weight must be positive.")
    else:
        # Normalize weights
        weights["skill"] = w_skill / total_w
        weights["behavior"] = w_behavior / total_w
        weights["career"] = w_career / total_w
        weights["experience"] = w_experience / total_w
        st.session_state.ranking_weights = weights

    st.markdown(f"""
    **Active normalized weights distribution:**
    * **Skills**: {weights['skill']*100:.1f}%
    * **Behavior**: {weights['behavior']*100:.1f}%
    * **Career Alignment**: {weights['career']*100:.1f}%
    * **Experience Fit**: {weights['experience']*100:.1f}%
    """)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 2. Dataset profile selection
    st.markdown("### 📂 Dataset Profile")
    st.markdown("Select which database slice to load into memory.")

    dataset_mode = st.radio(
        "Talent Pool Size",
        ["Sample Dataset (50 candidates - instant)", "Full Dataset (100,000 candidates - heavy processing)"],
        index=0 if st.session_state.get("dataset_mode") == "sample" else 1
    )

    if "Sample Dataset" in dataset_mode:
        st.session_state.dataset_mode = "sample"
        st.session_state.dataset_path = "[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/sample_candidates.json"
    else:
        st.session_state.dataset_mode = "full"
        st.session_state.dataset_path = "[PUB] India_runs_data_and_ai_challenge/[PUB] India_runs_data_and_ai_challenge/India_runs_data_and_ai_challenge/candidates.jsonl"
        st.warning("⚠️ Warning: The full dataset is 487MB (100,000 rows). Loading, embedding, and indexing all candidates will take significant memory and CPU processing time on startup. We recommend using the Sample Dataset for real-time hackathon review.")
        
    st.info("💡 Changes to weights or datasets will dynamically refresh the dashboard, search query index, and ranking directory.")
