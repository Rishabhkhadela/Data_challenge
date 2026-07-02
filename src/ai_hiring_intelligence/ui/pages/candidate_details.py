import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ai_hiring_intelligence.ui.utils import get_candidate_ranker

def render_candidate_details(candidates: list, weights: dict):
    st.header("Candidate Profile & Insights")
    
    if not candidates:
        st.warning("No candidates loaded. Please configure the dataset path in Settings.")
        return

    # Select Candidate
    candidate_ids = [c.get("candidate_id") for c in candidates]
    selected_id = st.session_state.get("selected_candidate_id")
    if not selected_id or selected_id not in candidate_ids:
        selected_id = candidate_ids[0]
        
    selected_id = st.selectbox("Select Candidate ID", candidate_ids, index=candidate_ids.index(selected_id))
    st.session_state.selected_candidate_id = selected_id

    # Load candidate record
    candidate = next(c for c in candidates if c.get("candidate_id") == selected_id)
    profile = candidate.get("profile", {})
    career_history = candidate.get("career_history", []) or []
    education = candidate.get("education", []) or []
    skills = candidate.get("skills", []) or []
    certs = candidate.get("certifications", []) or []
    languages = candidate.get("languages", []) or []
    signals = candidate.get("redrob_signals", {}) or {}

    # Calculate current score details against requirements
    requirements = st.session_state.get("active_requirements") or {
        "skills": ["Python", "Machine Learning", "SQL", "FastAPI"],
        "experience": ["3-5 years"],
        "behavior_traits": ["ownership", "ambiguity"],
        "leadership_requirements": []
    }
    
    ranker = get_candidate_ranker(weights)
    score_details = ranker.score_candidate(candidate, requirements)

    # 1. Headline Banner
    st.markdown(f"""
    <div style="background-color: #1E293B; padding: 1.5rem; border-radius: 12px; border-left: 6px solid #38BDF8; margin-bottom: 1.5rem;">
        <h2 style="margin:0; font-size:1.5rem;">{profile.get("anonymized_name", "Anonymized Candidate")} ({selected_id})</h2>
        <h4 style="margin:0.25rem 0; color:#38BDF8; font-weight:500;">{profile.get("headline", "Professional")}</h4>
        <p style="margin:0.5rem 0 0 0; font-size:0.9rem; color:#94A3B8;">📍 {profile.get("location", "Unknown")}, {profile.get("country", "Unknown")} | 💼 {profile.get("years_of_experience", 0)} Years of Experience</p>
    </div>
    """, unsafe_allow_html=True)

    # 2. Visual Scores & Radar Chart
    col_metrics, col_radar = st.columns([1, 1])
    
    with col_metrics:
        st.markdown("### Profile Score Breakdown")
        
        # Display overall and component match scores
        st.metric("Overall Suitability Match", f"{score_details.score * 100:.1f}%")
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.metric("Skill Score", f"{score_details.skill_score * 100:.0f}%")
            st.metric("Career Alignment", f"{score_details.career_score * 100:.0f}%")
        with m_col2:
            st.metric("Behavior Score", f"{score_details.behavior_score * 100:.0f}%")
            st.metric("Experience Score", f"{score_details.experience_score * 100:.0f}%")

    with col_radar:
        # Radar Chart
        categories = ['Skill Score', 'Behavior Score', 'Career Score', 'Experience Score']
        values = [score_details.skill_score, score_details.behavior_score, score_details.career_score, score_details.experience_score]
        # Close the loop
        categories_close = categories + [categories[0]]
        values_close = values + [values[0]]
        
        fig = go.Figure(data=go.Scatterpolar(
            r=[v*100 for v in values_close],
            theta=categories_close,
            fill='toself',
            fillcolor='rgba(56, 189, 248, 0.3)',
            line=dict(color='#38BDF8', width=2),
            marker=dict(color='#38BDF8', size=6)
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], gridcolor='#334155'),
                angularaxis=dict(gridcolor='#334155'),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#E2E8F0',
            height=300,
            margin=dict(l=40, r=40, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    # 3. Explainable AI section (Strengths, Weaknesses, Recruiter Recommendations)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🧠 Explainable AI Insights")
    
    col_ai1, col_ai2 = st.columns(2)
    
    # Analyze strengths and gaps
    candidate_skills_lower = [s.get("name", "").lower() for s in skills] + [s.lower() for s in signals.get("skill_assessment_scores", {}).keys()]
    required_skills = requirements.get("skills", [])
    matched_skills = [s for s in required_skills if s.lower() in candidate_skills_lower]
    missing_skills = [s for s in required_skills if s.lower() not in candidate_skills_lower]
    
    with col_ai1:
        st.markdown("#### 🌟 Key Strengths")
        st.markdown(f"- **Matching Core Skills**: Matched required skills: `{', '.join(matched_skills) if matched_skills else 'None'}`.")
        if score_details.behavior_score > 0.6:
            st.markdown(f"- **High Engagement**: Strong behavioral profile completeness ({signals.get('profile_completeness_score') or 0}%) and responsiveness.")
        if score_details.experience_score > 0.7:
            st.markdown(f"- **Aligned Tenure**: Years of experience ({profile.get('years_of_experience')} yrs) fits target profile requirements.")
        if signals.get("github_activity_score", 0) > 40:
            st.markdown(f"- **Active Developer**: High GitHub activity index of `{signals.get('github_activity_score')}/100`.")
            
    with col_ai2:
        st.markdown("#### ⚠️ Risks & Skill Gaps")
        if missing_skills:
            st.markdown(f"- **Missing Requirements**: Absent keywords: `{', '.join(missing_skills)}`.")
        if signals.get("notice_period_days", 0) > 60:
            st.markdown(f"- **Long Onboarding**: High notice period of `{signals.get('notice_period_days')} days` could delay team ramp-up.")
        
        # Expected vs Average salary check
        salary_min = signals.get("expected_salary_range_inr_lpa", {}).get("min")
        if salary_min and salary_min > 25:
            st.markdown(f"- **High Compensation Bracket**: Expected salary min is `{salary_min} LPA`.")
            
        if not missing_skills and signals.get("notice_period_days", 0) <= 60 and salary_min and salary_min <= 25:
            st.markdown("- **Minimal Risk**: Profile matches key requirements without clear salary or timeline anomalies.")

    # Recommendation
    rec_rating = "HOLD"
    rec_color = "#EAB308"
    if score_details.score > 0.75:
        rec_rating = "STRONG BUY / PROCEDE TO INTERVIEW"
        rec_color = "#22C55E"
    elif score_details.score > 0.55:
        rec_rating = "INTERVIEW / DISCUSS CONTEXT"
        rec_color = "#3B82F6"
        
    st.markdown(f"""
    <div style="background-color: #1E293B; padding: 1rem; border-radius: 8px; margin-top: 1rem; border: 1px solid {rec_color}; text-align:center;">
        <h4 style="margin:0; color:{rec_color}; font-size:1.1rem; font-weight:700;">Hiring Recommendation: {rec_rating}</h4>
    </div>
    """, unsafe_allow_html=True)

    # 4. Details (Timeline, Skills, Education, Certs)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### Profile Biography")
    
    col_bio1, col_bio2 = st.columns(2)
    with col_bio1:
        st.markdown("#### 💼 Experience Timeline")
        for i, role in enumerate(career_history):
            is_curr = "Current" if role.get("is_current") else "Past"
            st.markdown(f"""
            **{role.get('title')}** @ {role.get('company')}  
            *{role.get('start_date')} to {role.get('end_date') or 'Present'} ({role.get('duration_months', 0)} Months | {is_curr})*  
            {role.get('description', '')}
            """)
            st.markdown("---")
            
        st.markdown("#### 🎓 Education")
        for edu in education:
            st.markdown(f"""
            **{edu.get('degree')}** in {edu.get('field_of_study')}  
            {edu.get('institution')} ({edu.get('start_year')} - {edu.get('end_year')}) | **Grade**: {edu.get('grade')} | **Tier**: {edu.get('tier')}
            """)
            st.markdown("---")

    with col_bio2:
        st.markdown("#### 🛠️ Skills & Certifications")
        # Skills
        st.markdown("##### Endorsed Skills")
        for s in skills:
            st.markdown(f"- **{s.get('name')}**: {s.get('proficiency')} ({s.get('endorsements')} endorsements, {s.get('duration_months')} months)")
            
        # Assessments
        st.markdown("##### Platform Assessments")
        assessments = signals.get("skill_assessment_scores", {})
        if assessments:
            for sname, sscore in assessments.items():
                st.markdown(f"- **{sname}**: `{sscore}/100` score")
        else:
            st.info("No completed assessments found.")
            
        # Certifications
        st.markdown("##### Certifications")
        for cert in certs:
            st.markdown(f"- **{cert.get('name')}** issued by {cert.get('issuer')} ({cert.get('year')})")
            
        # Languages
        st.markdown("##### Languages")
        for lang in languages:
            st.markdown(f"- **{lang.get('language')}**: {lang.get('proficiency')}")
