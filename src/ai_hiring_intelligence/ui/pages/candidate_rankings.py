import streamlit as st
import pandas as pd
from ai_hiring_intelligence.ui.utils import get_candidate_ranker

def render_candidate_rankings(candidates: list, weights: dict):
    st.header("Overall Candidate Rankings")
    st.subheader("Global ranked talent pool matched against active requirements")
    
    if not candidates:
        st.warning("No candidates loaded. Please configure the dataset path in Settings.")
        return

    # Check for active requirements
    requirements = st.session_state.get("active_requirements")
    if not requirements:
        st.info("💡 Note: No job description has been parsed yet. Go to 'Job Description' to set requirements. Currently using default parameters.")
        requirements = {
            "skills": [],
            "experience": [],
            "behavior_traits": [],
            "leadership_requirements": []
        }

    # 1. Rank Candidates
    ranker = get_candidate_ranker(weights)
    with st.spinner("Calculating composite scores for candidate pool..."):
        ranked_dicts = ranker.rank_candidates_dicts(candidates, requirements)

    # Convert to DataFrame for visualization and sorting
    df = pd.DataFrame([
        {
            "Rank": item["rank"],
            "Candidate ID": item["candidate_id"],
            "Name": item["metadata"].get("anonymized_name", "Anonymized"),
            "Headline": item["metadata"].get("headline", ""),
            "Score": f"{item['score']*100:.1f}%",
            "Skill": f"{item['skill_score']*100:.1f}%",
            "Behavior": f"{item['behavior_score']*100:.1f}%",
            "Career": f"{item['career_score']*100:.1f}%",
            "Experience": f"{item['experience_score']*100:.1f}%",
            "RawScore": item["score"],
            "RawSkill": item["skill_score"],
            "RawBehavior": item["behavior_score"],
            "RawCareer": item["career_score"],
            "RawExperience": item["experience_score"]
        }
        for item in ranked_dicts
    ])

    # Sorting
    st.markdown("### Ranking Directory")
    sort_by = st.selectbox("Sort table by", ["Score", "Rank", "Skill", "Behavior", "Career", "Experience"], index=0)
    
    ascending = False
    col_map = {
        "Score": "RawScore",
        "Rank": "Rank",
        "Skill": "RawSkill",
        "Behavior": "RawBehavior",
        "Career": "RawCareer",
        "Experience": "RawExperience"
    }
    if sort_by == "Rank":
        ascending = True
        
    df_sorted = df.sort_values(by=col_map[sort_by], ascending=ascending).reset_index(drop=True)
    # Recalculate rank display index
    for idx, row in df_sorted.iterrows():
        df_sorted.at[idx, "Display Rank"] = idx + 1
    
    # 2. Global Export Button (Hackathon specified format)
    col_exp1, col_exp2 = st.columns([4, 1])
    with col_exp2:
        # Build CSV file per validate_submission.py rules
        csv_header = "candidate_id,rank,score,reasoning\n"
        csv_rows = []
        for idx, item in enumerate(ranked_dicts[:100], start=1):
            cid = item["candidate_id"]
            score = item["score"]
            # Generate a nice reasoning string dynamically
            skills_met = ", ".join(requirements.get("skills", [])[:2])
            reason = f"Top-ranked profile scoring {score*100:.1f}% based on matching {skills_met} skills and {item['metadata'].get('years_of_experience', 0)} years experience."
            # Remove commas from reasoning
            reason = reason.replace(",", ";")
            csv_rows.append(f"{cid},{idx},{score:.6f},{reason}")
            
        csv_content = csv_header + "\n".join(csv_rows)
        
        st.download_button(
            label="📤 Export Top 100 CSV",
            data=csv_content,
            file_name="team_submission.csv",
            mime="text/csv",
            help="Generates submission CSV complying with challenge validate_submission.py spec."
        )

    # 3. Paginated Display
    items_per_page = 15
    total_pages = max(1, (len(df_sorted) + items_per_page - 1) // items_per_page)
    current_page = st.number_input("Page selector", min_value=1, max_value=total_pages, value=1, key="ranking_page")
    
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(df_sorted))
    
    display_df = df_sorted.iloc[start_idx:end_idx][["Display Rank", "Candidate ID", "Name", "Headline", "Score", "Skill", "Behavior", "Career", "Experience"]]
    st.table(display_df.set_index("Display Rank"))

    # Quick Jump to Profile Details
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### Inspect Candidate Profile")
    cand_ids = df_sorted["Candidate ID"].tolist()
    selected_id = st.selectbox("Select Candidate ID to open full profile", cand_ids)
    if st.button("Go to Profile Details"):
        st.session_state.selected_candidate_id = selected_id
        st.session_state.navigation = "Candidate Details"
        st.rerun()
