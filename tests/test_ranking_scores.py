from ai_hiring_intelligence.domain.ranking import (
    behavior_score,
    career_score,
    experience_score,
    skill_score,
)


REQUIREMENTS = {
    "skills": ["Python", "LLMs", "RAG", "FAISS"],
    "experience": ["5-9 years", "production AI systems"],
    "behavior_traits": ["ownership", "comfortable with ambiguity"],
    "leadership_requirements": ["mentor engineers", "cross-functional influence"],
}


def candidate_record() -> dict:
    return {
        "profile": {
            "headline": "Senior AI Engineer",
            "summary": "Owns production AI systems, RAG platforms, and cross-functional delivery.",
            "years_of_experience": 6.5,
            "current_title": "Senior AI Engineer",
            "current_industry": "Software",
        },
        "career_history": [
            {
                "title": "Senior AI Engineer",
                "industry": "Software",
                "duration_months": 36,
                "is_current": True,
                "description": "Built LLM applications, mentored engineers, and drove ownership.",
            },
            {
                "title": "ML Engineer",
                "industry": "Software",
                "duration_months": 42,
                "is_current": False,
                "description": "Shipped production AI systems.",
            },
        ],
        "skills": [
            {
                "name": "Python",
                "proficiency": "expert",
                "endorsements": 50,
                "duration_months": 72,
            },
            {
                "name": "RAG",
                "proficiency": "advanced",
                "endorsements": 24,
                "duration_months": 24,
            },
            {
                "name": "FAISS",
                "proficiency": "intermediate",
                "endorsements": 10,
                "duration_months": 12,
            },
        ],
        "redrob_signals": {
            "profile_completeness_score": 95,
            "recruiter_response_rate": 0.9,
            "avg_response_time_hours": 12,
            "profile_views_received_30d": 80,
            "search_appearance_30d": 240,
            "saved_by_recruiters_30d": 12,
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


def test_skill_score_matches_profile_skills_and_assessments() -> None:
    score = skill_score(candidate_record(), REQUIREMENTS)

    assert 0.7 <= score <= 1.0


def test_behavior_score_uses_platform_signals_and_traits() -> None:
    score = behavior_score(candidate_record(), REQUIREMENTS)

    assert 0.75 <= score <= 1.0


def test_career_score_uses_role_history_and_leadership_requirements() -> None:
    score = career_score(candidate_record(), REQUIREMENTS)

    assert 0.5 <= score <= 1.0


def test_experience_score_rewards_required_years_and_depth() -> None:
    score = experience_score(candidate_record(), REQUIREMENTS)

    assert 0.85 <= score <= 1.0


def test_scores_are_low_for_sparse_candidate() -> None:
    sparse = {"profile": {"years_of_experience": 1}, "skills": [], "redrob_signals": {}}

    assert skill_score(sparse, REQUIREMENTS) == 0.0
    assert behavior_score(sparse, REQUIREMENTS) == 0.0
    assert career_score(sparse, REQUIREMENTS) < 0.2
    assert experience_score(sparse, REQUIREMENTS) < 0.4
