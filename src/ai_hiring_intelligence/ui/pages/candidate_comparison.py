import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ai_hiring_intelligence.ui.utils import get_candidate_ranker

def render_candidate_comparison(candidates: list, weights: dict):
    st.header("Candidate Comparison")
    st.subheader("Side-by-side evaluations to select the top profile")
    
    if not candidates:
        st.warning("No candidates loaded. Please configure the dataset path in Settings.")
        return

    # 1. Selection
    candidate_ids = [c.get("candidate_id") for c in candidates]
    compare_list = st.session_state.get("compare_candidates", [])
    
    col_sel1, col_sel2 = st.columns(2)
    
    default_c1 = compare_list[0] if len(compare_list) > 0 and compare_list[0] in candidate_ids else candidate_ids[0]
    default_c2 = compare_list[1] if len(compare_list) > 1 and compare_list[1] in candidate_ids else (candidate_ids[1] if len(candidate_ids) > 1 else candidate_ids[0])
    
    with col_sel1:
        c1_id = st.selectbox("Candidate 1 ID", candidate_ids, index=candidate_ids.index(default_c1), key="comp_c1")
    with col_sel2:
        c2_id = st.selectbox("Candidate 2 ID", candidate_ids, index=candidate_ids.index(default_c2), key="comp_c2")

    # Save selection back
    st.session_state.compare_candidates = [c1_id, c2_id]

    if c1_id == c2_id:
        st.info("Select two different candidates to compare.")
        return

    # Load candidates
    cand1 = next(c for c in candidates if c.get("candidate_id") == c1_id)
    cand2 = next(c for c in candidates if c.get("candidate_id") == c2_id)
    
    profile1 = cand1.get("profile", {})
    profile2 = cand2.get("profile", {})
    signals1 = cand1.get("redrob_signals", {})
    signals2 = cand2.get("redrob_signals", {})

    # Scoring
    requirements = st.session_state.get("active_requirements") or {
        "skills": [],
        "experience": [],
        "behavior_traits": [],
        "leadership_requirements": []
    }
    ranker = get_candidate_ranker(weights)
    score1 = ranker.score_candidate(cand1, requirements)
    score2 = ranker.score_candidate(cand2, requirements)

    # 2. Score Match Progress Bars
    st.markdown("### Match Suitability Profile")
    
    # helper function
    def render_progress_comparison(label, v1, v2):
        col_l, col_v1, col_v2 = st.columns([2, 5, 5])
        with col_l:
            st.markdown(f"**{label}**")
        with col_v1:
            color = "#22C55E" if v1 >= v2 else "#64748B"
            winner_badge = " 🏆" if v1 > v2 else ""
            st.markdown(f'<div style="font-weight:600; color:{color};">{v1*100:.1f}%{winner_badge}</div>', unsafe_allow_html=True)
            st.progress(v1)
        with col_v2:
            color = "#22C55E" if v2 >= v1 else "#64748B"
            winner_badge = " 🏆" if v2 > v1 else ""
            st.markdown(f'<div style="font-weight:600; color:{color};">{v2*100:.1f}%{winner_badge}</div>', unsafe_allow_html=True)
            st.progress(v2)
            
    render_progress_comparison("Overall Score", score1.score, score2.score)
    render_progress_comparison("Skills Score", score1.skill_score, score2.skill_score)
    render_progress_comparison("Behavior Score", score1.behavior_score, score2.behavior_score)
    render_progress_comparison("Career Score", score1.career_score, score2.career_score)
    render_progress_comparison("Experience Score", score1.experience_score, score2.experience_score)

    st.markdown("<hr>", unsafe_allow_html=True)

    # 3. Sidebar Demographics Side-by-Side Table
    st.markdown("### Profile Comparison")
    
    comp_data = {
        "Attribute": [
            "Headline",
            "Location",
            "Years of Experience",
            "Notice Period",
            "Preferred Work Mode",
            "Willing to Relocate",
            "Expected Salary Min (LPA)",
            "Expected Salary Max (LPA)",
            "GitHub Activity Score",
            "Profile Completeness"
        ],
        c1_id: [
            profile1.get("headline"),
            f"{profile1.get('location')}, {profile1.get('country')}",
            f"{profile1.get('years_of_experience')} yrs",
            f"{signals1.get('notice_period_days')} days",
            signals1.get("preferred_work_mode", "hybrid").title(),
            "Yes" if signals1.get("willing_to_relocate") else "No",
            signals1.get("expected_salary_range_inr_lpa", {}).get("min"),
            signals1.get("expected_salary_range_inr_lpa", {}).get("max"),
            signals1.get("github_activity_score"),
            f"{signals1.get('profile_completeness_score')}%"
        ],
        c2_id: [
            profile2.get("headline"),
            f"{profile2.get('location')}, {profile2.get('country')}",
            f"{profile2.get('years_of_experience')} yrs",
            f"{signals2.get('notice_period_days')} days",
            signals2.get("preferred_work_mode", "hybrid").title(),
            "Yes" if signals2.get("willing_to_relocate") else "No",
            signals2.get("expected_salary_range_inr_lpa", {}).get("min"),
            signals2.get("expected_salary_range_inr_lpa", {}).get("max"),
            signals2.get("github_activity_score"),
            f"{signals2.get('profile_completeness_score')}%"
        ]
    }
    
    df_comp = pd.DataFrame(comp_data)
    st.table(df_comp.set_index("Attribute"))
