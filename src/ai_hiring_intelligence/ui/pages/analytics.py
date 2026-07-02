import streamlit as st
import pandas as pd
import plotly.express as px
from ai_hiring_intelligence.ui.utils import get_candidate_ranker

def render_analytics(candidates: list, weights: dict):
    st.header("Advanced Analytics")
    st.subheader("Deep dive candidate pool analysis and scatter profiles")
    
    if not candidates:
        st.warning("No candidates loaded. Please configure the dataset path in Settings.")
        return

    # Check for active requirements
    requirements = st.session_state.get("active_requirements") or {
        "skills": [],
        "experience": [],
        "behavior_traits": [],
        "leadership_requirements": []
    }

    # Recalculate ranks to build dataframe
    ranker = get_candidate_ranker(weights)
    scored = [ranker.score_candidate(c, requirements) for c in candidates]
    
    df = pd.DataFrame([
        {
            "candidate_id": item.candidate_id,
            "score": item.score * 100,
            "skill_score": item.skill_score * 100,
            "behavior_score": item.behavior_score * 100,
            "career_score": item.career_score * 100,
            "experience_score": item.experience_score * 100,
            "years_of_experience": item.metadata.get("years_of_experience", 0),
            "salary_min": next(c for c in candidates if c.get("candidate_id") == item.candidate_id).get("redrob_signals", {}).get("expected_salary_range_inr_lpa", {}).get("min", 0),
            "salary_max": next(c for c in candidates if c.get("candidate_id") == item.candidate_id).get("redrob_signals", {}).get("expected_salary_range_inr_lpa", {}).get("max", 0),
            "github_score": next(c for c in candidates if c.get("candidate_id") == item.candidate_id).get("redrob_signals", {}).get("github_activity_score", -1),
            "completeness": next(c for c in candidates if c.get("candidate_id") == item.candidate_id).get("redrob_signals", {}).get("profile_completeness_score", 0),
        }
        for item in scored
    ])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Match Score vs. Experience")
        fig_scatter = px.scatter(
            df, 
            x="years_of_experience", 
            y="score",
            hover_data=["candidate_id", "salary_min"],
            labels={"years_of_experience": "Years of Experience", "score": "Match Score (%)"},
            color="score",
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            xaxis=dict(showgrid=True, gridcolor="#334155"),
            yaxis=dict(showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.markdown("### Salary Expectations Spread (LPA)")
        # filter out zero salary
        df_sal = df[df["salary_min"] > 0]
        if not df_sal.empty:
            fig_sal = px.box(
                df_sal,
                y=["salary_min", "salary_max"],
                labels={"value": "Expected Salary (INR LPA)", "variable": "Salary Dimension"},
                color_discrete_sequence=["#38BDF8"]
            )
            fig_sal.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#F8FAFC",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#334155")
            )
            st.plotly_chart(fig_sal, use_container_width=True)
        else:
            st.info("No salary details available in current dataset.")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### GitHub Score vs. Profile Completeness")
        # filter out missing github (-1)
        df_git = df[df["github_score"] >= 0]
        if not df_git.empty:
            fig_git = px.scatter(
                df_git,
                x="completeness",
                y="github_score",
                color="score",
                labels={"completeness": "Profile Completeness Score (%)", "github_score": "GitHub Activity Score"},
                color_continuous_scale=px.colors.sequential.Plasma
            )
            fig_git.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#F8FAFC",
                xaxis=dict(showgrid=True, gridcolor="#334155"),
                yaxis=dict(showgrid=True, gridcolor="#334155")
            )
            st.plotly_chart(fig_git, use_container_width=True)
        else:
            st.info("No candidate records have linked GitHub profiles.")

    with col4:
        st.markdown("### Component Scores Correlation")
        corr = df[["score", "skill_score", "behavior_score", "career_score", "experience_score"]].corr()
        fig_heat = px.imshow(
            corr,
            text_auto=True,
            aspect="auto",
            color_continuous_scale=px.colors.diverging.RdBu,
            zmin=-1, zmax=1
        )
        fig_heat.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC"
        )
        st.plotly_chart(fig_heat, use_container_width=True)
