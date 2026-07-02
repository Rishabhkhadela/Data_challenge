import sys
from pathlib import Path

# Add src folder to PYTHONPATH dynamically
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st
import os

from ai_hiring_intelligence import __version__
from ai_hiring_intelligence.ui.utils import (
    load_candidates_data,
    get_embedding_service,
    inject_custom_css,
    DEFAULT_SAMPLE_PATH
)

# Page modules imports
from ai_hiring_intelligence.ui.pages.dashboard import render_dashboard
from ai_hiring_intelligence.ui.pages.job_parser_page import render_job_parser
from ai_hiring_intelligence.ui.pages.candidate_search import render_candidate_search
from ai_hiring_intelligence.ui.pages.candidate_rankings import render_candidate_rankings
from ai_hiring_intelligence.ui.pages.candidate_details import render_candidate_details
from ai_hiring_intelligence.ui.pages.candidate_comparison import render_candidate_comparison
from ai_hiring_intelligence.ui.pages.analytics import render_analytics
from ai_hiring_intelligence.ui.pages.ai_insights import render_ai_insights
from ai_hiring_intelligence.ui.pages.settings import render_settings

def initialize_session_state():
    """Setup default session states on application boot."""
    st.session_state.setdefault("dataset_mode", "sample")
    st.session_state.setdefault("dataset_path", DEFAULT_SAMPLE_PATH)
    
    st.session_state.setdefault("ranking_weights", {
        "skill": 0.35,
        "behavior": 0.20,
        "career": 0.20,
        "experience": 0.25
    })
    
    # Pre-parse default requirements so pages are immediately operational
    st.session_state.setdefault("active_requirements", {
        "skills": ["Python", "Machine Learning", "FastAPI", "SQL"],
        "experience": ["5-9 years", "Senior technical role history"],
        "behavior_traits": ["ownership", "comfortable with ambiguity"],
        "leadership_requirements": ["mentoring junior engineers", "cross-functional technical influence"]
    })

def main() -> None:
    st.set_page_config(
        page_title="Redrob AI Hiring Intelligence",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    initialize_session_state()
    inject_custom_css()

    # Load candidates pool
    candidates = load_candidates_data(st.session_state.dataset_path)
    embedding_service = get_embedding_service()
    weights = st.session_state.ranking_weights

    # Sidebar Sidebar Header
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <h2 style="margin: 0; color: #38BDF8; font-size: 1.5rem;">Redrob AI</h2>
        <p style="margin: 0; color: #64748B; font-size: 0.8rem;">Hiring Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar Navigation Menu
    menu_options = [
        "Dashboard",
        "Job Description",
        "Candidate Search",
        "Candidate Rankings",
        "Candidate Details",
        "Candidate Comparison",
        "Analytics",
        "AI Insights",
        "Settings"
    ]
    
    # Track selection via session state to allow programmatic redirection
    default_nav_idx = 0
    if "navigation" in st.session_state and st.session_state.navigation in menu_options:
        default_nav_idx = menu_options.index(st.session_state.navigation)
        
    nav_selection = st.sidebar.radio(
        "Navigation",
        options=menu_options,
        index=default_nav_idx,
        key="nav_selection_radio"
    )
    st.session_state.navigation = nav_selection

    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(f"""
    <div style="font-size:0.75rem; color:#64748B; text-align:center;">
        Version {__version__} | Environment: {st.session_state.dataset_mode.upper()}<br>
        India Runs Challenge 2026
    </div>
    """, unsafe_allow_html=True)

    # Page Dispatcher
    if nav_selection == "Dashboard":
        render_dashboard(candidates)
    elif nav_selection == "Job Description":
        render_job_parser()
    elif nav_selection == "Candidate Search":
        render_candidate_search(candidates, embedding_service, weights)
    elif nav_selection == "Candidate Rankings":
        render_candidate_rankings(candidates, weights)
    elif nav_selection == "Candidate Details":
        render_candidate_details(candidates, weights)
    elif nav_selection == "Candidate Comparison":
        render_candidate_comparison(candidates, weights)
    elif nav_selection == "Analytics":
        render_analytics(candidates, weights)
    elif nav_selection == "AI Insights":
        render_ai_insights(candidates, weights)
    elif nav_selection == "Settings":
        render_settings()

if __name__ == "__main__":
    main()
