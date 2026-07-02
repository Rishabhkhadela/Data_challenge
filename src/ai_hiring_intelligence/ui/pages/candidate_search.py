import streamlit as st
import pandas as pd
from ai_hiring_intelligence.ui.utils import build_retriever_index, get_candidate_ranker

def render_candidate_search(candidates: list, embedding_service, weights: dict):
    st.header("Semantic Candidate Search")
    st.subheader("Query your talent pool using natural language and filters")
    
    if not candidates:
        st.warning("No candidates loaded. Please configure the dataset path in Settings.")
        return

    # Check for active requirements
    requirements = st.session_state.get("active_requirements")
    if not requirements:
        st.info("💡 Note: No job description has been parsed yet. Go to 'Job Description' to set search requirements, or we will use default parameters.")
        requirements = {
            "skills": [],
            "experience": [],
            "behavior_traits": [],
            "leadership_requirements": []
        }

    # 1. FAISS Vector Indexing
    with st.spinner("Building retrieval index..."):
        retriever = build_retriever_index(candidates, embedding_service)
    
    # 2. Search Panel & Filters
    col_search, col_filter = st.columns([2, 1])
    
    with col_search:
        query = st.text_input("🔍 Semantic search query", placeholder="e.g. Python backend developer with experience in Kubernetes and RAG")
        
    # Get metadata lists for filters
    countries = sorted(list(set(c.get("profile", {}).get("country", "Unknown") for c in candidates)))
    work_modes = ["hybrid", "onsite", "remote", "flexible"]
    
    with col_filter:
        with st.expander("Filter Options"):
            min_exp, max_exp = st.slider("Years of Experience", 0, 20, (0, 20))
            selected_countries = st.multiselect("Country", options=countries, default=[])
            selected_modes = st.multiselect("Preferred Work Mode", options=work_modes, default=[])
            max_notice = st.slider("Max Notice Period (Days)", 0, 180, 180)

    # 3. Retrieval
    results = []
    if query.strip():
        # Retrieve using FAISS retriever
        with st.spinner("Searching vectors..."):
            ret_results = retriever.search_text(query, embedding_service, top_k=len(candidates))
            
            # Map retrieval results back to candidate records
            candidate_dict = {c.get("candidate_id"): c for c in candidates}
            for res in ret_results:
                record = candidate_dict.get(res.candidate_id)
                if record:
                    results.append((record, res.score))
    else:
        # Fallback to ranking all candidates by active ranker if no search query
        ranker = get_candidate_ranker(weights)
        ranked = ranker.rank_candidates(candidates, requirements)
        candidate_dict = {c.get("candidate_id"): c for c in candidates}
        for item in ranked:
            record = candidate_dict.get(item.candidate_id)
            if record:
                results.append((record, item.score))

    # 4. Apply filters
    filtered_results = []
    for record, score in results:
        profile = record.get("profile", {})
        signals = record.get("redrob_signals", {})
        
        # Exp filter
        exp = profile.get("years_of_experience", 0) or 0
        if not (min_exp <= exp <= max_exp):
            continue
            
        # Country filter
        country = profile.get("country", "Unknown")
        if selected_countries and country not in selected_countries:
            continue
            
        # Work mode filter
        mode = signals.get("preferred_work_mode", "hybrid")
        if selected_modes and mode not in selected_modes:
            continue
            
        # Notice period filter
        notice = signals.get("notice_period_days", 90) or 90
        if notice > max_notice:
            continue
            
        filtered_results.append((record, score))

    # 5. Display Count
    st.write(f"Showing **{len(filtered_results)}** candidates matching criteria")
    
    if not filtered_results:
        st.info("No candidates match your current search and filter settings.")
        return

    # 6. Pagination
    st.markdown("<hr>", unsafe_allow_html=True)
    items_per_page = 5
    total_pages = max(1, (len(filtered_results) + items_per_page - 1) // items_per_page)
    
    col_p1, col_p2 = st.columns([5, 1])
    with col_p2:
        current_page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
        
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(filtered_results))
    
    # 7. Render paginated cards
    ranker = get_candidate_ranker(weights)
    for i in range(start_idx, end_idx):
        record, score = filtered_results[i]
        candidate_id = record.get("candidate_id")
        
        # Recalculate ranking score details
        score_details = ranker.score_candidate(record, requirements)
        
        profile = record.get("profile", {})
        signals = record.get("redrob_signals", {})
        
        # Build candidate card HTML/Streamlit
        with st.container():
            st.markdown(f"""
            <div class="candidate-card">
                <table style="width:100%; border:none; border-collapse:collapse;">
                    <tr style="background:transparent; border:none;">
                        <td style="width:70%; vertical-align:top; border:none;">
                            <h3 style="margin:0; font-size:1.2rem;">{profile.get("anonymized_name", "Anonymized Candidate")} <span style="font-size:0.8rem; color:#94A3B8;">({candidate_id})</span></h3>
                            <p style="margin:0.25rem 0; font-weight:500; color:#38BDF8;">{profile.get("headline", "Candidate")}</p>
                            <p style="margin:0.5rem 0; font-size:0.85rem; color:#CBD5E1;">{profile.get("summary", "")}</p>
                            <div style="margin-top:0.5rem;">
                                <span class="skill-chip">💼 {profile.get("years_of_experience", 0)} yrs exp</span>
                                <span class="skill-chip">📍 {profile.get("location")}, {profile.get("country")}</span>
                                <span class="skill-chip">⏱️ {signals.get("notice_period_days")}d notice</span>
                                <span class="skill-chip">🏢 {signals.get("preferred_work_mode", "hybrid").title()}</span>
                            </div>
                        </td>
                        <td style="width:30%; text-align:right; vertical-align:top; border:none;">
                            <div style="margin-bottom:0.5rem;">
                                <span class="match-badge">Match: {score_details.score*100:.1f}%</span>
                            </div>
                            <div style="font-size:0.8rem; color:#94A3B8; margin-top:0.25rem;">
                                <div>Skill Score: {score_details.skill_score*100:.1f}%</div>
                                <div>Behavior Score: {score_details.behavior_score*100:.1f}%</div>
                                <div>Career Score: {score_details.career_score*100:.1f}%</div>
                                <div>Experience Score: {score_details.experience_score*100:.1f}%</div>
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col_b1, col_b2, col_b3, col_b4 = st.columns([1, 1, 1, 3])
            with col_b1:
                if st.button("View Details", key=f"view_{candidate_id}"):
                    st.session_state.selected_candidate_id = candidate_id
                    st.session_state.navigation = "Candidate Details"
                    st.rerun()
            with col_b2:
                # Add to compare list
                compare_list = st.session_state.setdefault("compare_candidates", [])
                is_selected = candidate_id in compare_list
                label = "Remove Compare" if is_selected else "Add Compare"
                if st.button(label, key=f"comp_{candidate_id}"):
                    if is_selected:
                        compare_list.remove(candidate_id)
                        st.toast(f"Removed {candidate_id} from comparison.")
                    else:
                        if len(compare_list) >= 2:
                            compare_list.pop(0) # Keep max 2
                        compare_list.append(candidate_id)
                        st.toast(f"Added {candidate_id} to comparison.")
                    st.rerun()
            with col_b3:
                # Export single candidate ranking row
                if st.button("Export CSV", key=f"export_{candidate_id}"):
                    csv_data = f"candidate_id,rank,score,reasoning\n{candidate_id},1,{score_details.score:.4f},Matched based on experience and skills\n"
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"{candidate_id}_ranking.csv",
                        mime="text/csv",
                        key=f"dl_{candidate_id}"
                    )
            st.markdown("<br>", unsafe_allow_html=True)
