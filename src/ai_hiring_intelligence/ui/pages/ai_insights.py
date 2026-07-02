import streamlit as st
import pandas as pd
from ai_hiring_intelligence.ui.utils import get_candidate_ranker

def render_ai_insights(candidates: list, weights: dict):
    st.header("AI Talent Insights")
    st.subheader("Automated recruiter feedback and hiring suggestions")
    
    if not candidates:
        st.warning("No candidates loaded. Please configure the dataset path in Settings.")
        return

    requirements = st.session_state.get("active_requirements")
    if not requirements or not requirements.get("skills"):
        st.info("💡 Parse a job description on the 'Job Description' page to unlock custom talent insights matched against active requirements.")
        requirements = {
            "skills": ["Python", "Machine Learning", "FastAPI", "SQL"],
            "experience": ["3-5 years"],
            "behavior_traits": ["ownership"],
            "leadership_requirements": []
        }

    # Rank all candidates
    ranker = get_candidate_ranker(weights)
    with st.spinner("Processing AI analytics pipeline..."):
        ranked = ranker.rank_candidates(candidates, requirements)

    if not ranked:
        st.info("Talent pool is empty.")
        return

    # 1. Pipeline Orders
    st.markdown("### 📅 Proposed Interview Scheduling Order")
    st.markdown("Recommended candidates sorted by suitability match. Click on a candidate to view their details.")
    
    top_candidates = ranked[:5]
    for idx, item in enumerate(top_candidates, start=1):
        name = item.metadata.get("anonymized_name", "Anonymized Candidate")
        headline = item.metadata.get("headline", "Professional")
        score = item.score * 100
        
        st.markdown(f"""
        <div style="background-color: #1E293B; padding: 1rem; border-radius: 8px; border-left: 4px solid #22C55E; margin-bottom: 0.75rem;">
            <table style="width:100%; border:none; border-collapse:collapse; margin:0;">
                <tr style="background:transparent; border:none;">
                    <td style="width:8%; font-size:1.4rem; font-weight:700; color:#22C55E; border:none; text-align:center;">#{idx}</td>
                    <td style="width:67%; border:none;">
                        <h4 style="margin:0; font-size:1rem;">{name} ({item.candidate_id})</h4>
                        <p style="margin:0.2rem 0 0 0; font-size:0.8rem; color:#94A3B8;">{headline}</p>
                    </td>
                    <td style="width:25%; border:none; text-align:right; font-weight:700; color:#22C55E; font-size:1.1rem;">
                        {score:.1f}% Match
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # 2. Missing Skills Analysis
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🔍 Talent Pool Skill Gap Analysis")
    st.markdown("Aggregated required skills that are most commonly **missing** across your candidate pool:")
    
    required_skills = requirements.get("skills", [])
    if required_skills:
        skill_gaps = {skill: 0 for skill in required_skills}
        for c in candidates:
            c_skills = [s.get("name", "").lower() for s in c.get("skills", []) or []]
            c_ass = [s.lower() for s in c.get("redrob_signals", {}).get("skill_assessment_scores", {}).keys()]
            c_all = c_skills + c_ass
            for r_skill in required_skills:
                if r_skill.lower() not in c_all:
                    skill_gaps[r_skill] += 1
                    
        # Calculate percentage
        df_gaps = pd.DataFrame([
            {"Skill": skill, "Gaps Count": count, "Missing Ratio (%)": (count / len(candidates)) * 100}
            for skill, count in skill_gaps.items()
        ]).sort_values(by="Missing Ratio (%)", ascending=False)
        
        st.table(df_gaps.set_index("Skill"))
        st.caption("💡 High missing ratio indicates a restrictive skill requirement that limits your talent pool.")
    else:
        st.info("No active skill requirements configured.")

    # 3. High-Potential behavioral outliers
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### ⚡ Fast-Track Candidates (Low Notice & High Responsiveness)")
    st.markdown("These candidates have a notice period of ≤ 30 days and response rate of ≥ 70%. Excellent for urgent hiring needs.")
    
    fast_track = []
    for c in candidates:
        sig = c.get("redrob_signals", {}) or {}
        np_days = sig.get("notice_period_days", 90) or 90
        resp_rate = sig.get("recruiter_response_rate", 0) or 0
        if np_days <= 30 and resp_rate >= 0.70:
            score_details = ranker.score_candidate(c, requirements)
            fast_track.append((c, score_details.score))
            
    fast_track.sort(key=lambda x: x[1], reverse=True)
    
    if fast_track:
        for idx, (c, score) in enumerate(fast_track[:3], start=1):
            prof = c.get("profile", {})
            st.markdown(f"- **{prof.get('anonymized_name')}** ({c.get('candidate_id')}) - **Match**: `{score*100:.1f}%` | **Notice**: `{c.get('redrob_signals', {}).get('notice_period_days')} days` | **Resp Rate**: `{c.get('redrob_signals', {}).get('recruiter_response_rate')*100:.0f}%`")
    else:
        st.info("No candidates fit the urgent notice and response criteria in the loaded slice.")
