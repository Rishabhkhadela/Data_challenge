import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

def render_dashboard(candidates: list):
    st.header("Executive Dashboard")
    st.subheader("High-level candidate metrics and distribution profiles")
    
    if not candidates:
        st.warning("No candidates loaded. Please configure the dataset path in Settings.")
        return

    # Process metrics using pandas for performance
    df = pd.DataFrame([
        {
            "years_of_experience": r.get("profile", {}).get("years_of_experience", 0) or 0,
            "completeness": r.get("redrob_signals", {}).get("profile_completeness_score", 0) or 0,
            "response_rate": r.get("redrob_signals", {}).get("recruiter_response_rate", 0) or 0,
            "notice_period": r.get("redrob_signals", {}).get("notice_period_days", 90) or 90,
            "work_mode": r.get("redrob_signals", {}).get("preferred_work_mode", "hybrid") or "hybrid",
            "country": r.get("profile", {}).get("country", "Unknown") or "Unknown",
        }
        for r in candidates
    ])
    
    # 1. KPI Metric Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Candidates", f"{len(candidates):,}")
    with col2:
        avg_exp = df["years_of_experience"].mean()
        st.metric("Average Experience", f"{avg_exp:.1f} Yrs")
    with col3:
        avg_complete = df["completeness"].mean()
        st.metric("Avg Profile Match Score", f"{avg_complete:.1f}%")
    with col4:
        active_ratio = (df["response_rate"] > 0.5).mean() * 100
        st.metric("Highly Responsive", f"{active_ratio:.1f}%")
        
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # 2. Charts section
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("### Experience Distribution")
        fig_exp = px.histogram(
            df, 
            x="years_of_experience", 
            nbins=20,
            labels={"years_of_experience": "Years of Experience"},
            color_discrete_sequence=["#38BDF8"]
        )
        fig_exp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig_exp, use_container_width=True)
        
    with row1_col2:
        st.markdown("### Preferred Work Mode")
        work_counts = df["work_mode"].value_counts().reset_index()
        fig_work = px.pie(
            work_counts, 
            values="count", 
            names="work_mode",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_work.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_work, use_container_width=True)
        
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        st.markdown("### Geographic Distribution")
        country_counts = df["country"].value_counts().head(10).reset_index()
        fig_geo = px.bar(
            country_counts,
            y="country",
            x="count",
            orientation="h",
            labels={"country": "Country", "count": "Candidates"},
            color_discrete_sequence=["#2DD4BF"]
        )
        fig_geo.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            xaxis=dict(showgrid=True, gridcolor="#334155"),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_geo, use_container_width=True)
        
    with row2_col2:
        st.markdown("### Notice Period Breakdown")
        notice_counts = df["notice_period"].value_counts().reset_index()
        fig_notice = px.bar(
            notice_counts,
            x="notice_period",
            y="count",
            labels={"notice_period": "Notice Period (Days)", "count": "Candidates"},
            color_discrete_sequence=["#818CF8"]
        )
        fig_notice.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#F8FAFC",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#334155")
        )
        st.plotly_chart(fig_notice, use_container_width=True)
