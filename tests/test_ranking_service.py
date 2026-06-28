from ai_hiring_intelligence.services.ranking_service import CandidateRanker


REQUIREMENTS = {
    "skills": ["Python", "LLMs", "RAG", "FAISS"],
    "experience": ["5-9 years", "production AI systems"],
    "behavior_traits": ["ownership", "comfortable with ambiguity"],
    "leadership_requirements": ["mentor engineers", "cross-functional influence"],
}


def candidate(candidate_id: str, years: float, skill_name: str, response_rate: float) -> dict:
    return {
        "candidate_id": candidate_id,
        "profile": {
            "headline": "Senior AI Engineer",
            "summary": "Owns production AI systems.",
            "years_of_experience": years,
            "current_title": "Senior AI Engineer",
            "current_industry": "Software",
        },
        "career_history": [
            {
                "title": "Senior AI Engineer",
                "industry": "Software",
                "duration_months": 36,
                "is_current": True,
                "description": "Built LLM applications and mentored engineers.",
            }
        ],
        "skills": [
            {
                "name": skill_name,
                "proficiency": "expert",
                "endorsements": 50,
                "duration_months": 72,
            }
        ],
        "redrob_signals": {
            "profile_completeness_score": 95,
            "recruiter_response_rate": response_rate,
            "avg_response_time_hours": 12,
            "interview_completion_rate": 0.95,
            "offer_acceptance_rate": 0.8,
            "connection_count": 400,
            "endorsements_received": 70,
            "github_activity_score": 85,
            "open_to_work_flag": True,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
            "skill_assessment_scores": {"LLMs": 88},
        },
    }


def test_rank_candidates_orders_by_composite_score() -> None:
    ranker = CandidateRanker()
    ranked = ranker.rank_candidates(
        [
            candidate("CAND_0001", 6.5, "Python", 0.9),
            candidate("CAND_0002", 2.0, "SQL", 0.3),
        ],
        REQUIREMENTS,
    )

    assert [item.candidate_id for item in ranked] == ["CAND_0001", "CAND_0002"]
    assert [item.rank for item in ranked] == [1, 2]
    assert ranked[0].score > ranked[1].score


def test_rank_candidates_dicts_respect_top_k() -> None:
    ranker = CandidateRanker()
    ranked = ranker.rank_candidates_dicts(
        [
            candidate("CAND_0001", 6.5, "Python", 0.9),
            candidate("CAND_0002", 6.2, "Python", 0.8),
        ],
        REQUIREMENTS,
        top_k=1,
    )

    assert len(ranked) == 1
    assert ranked[0]["rank"] == 1
    assert ranked[0]["candidate_id"] == "CAND_0001"


def test_ranker_rejects_invalid_weights() -> None:
    try:
        CandidateRanker(skill_weight=0, behavior_weight=0, career_weight=0, experience_weight=0)
    except ValueError as exc:
        assert "positive" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
