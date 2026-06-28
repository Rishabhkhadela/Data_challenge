from ai_hiring_intelligence.domain.candidate_builder import (
    build_candidate_documents,
    build_candidate_profile,
)


def test_build_candidate_profile_includes_core_semantic_sections() -> None:
    candidate = {
        "candidate_id": "CAND_0000001",
        "profile": {
            "anonymized_name": "Ira Vora",
            "headline": "Backend Engineer | SQL, Spark, Cloud",
            "summary": "Builds data pipelines and ML-adjacent systems.",
            "location": "Toronto",
            "country": "Canada",
            "years_of_experience": 6.9,
            "current_title": "Backend Engineer",
            "current_company": "Mindtree",
            "current_company_size": "10001+",
            "current_industry": "IT Services",
        },
        "career_history": [
            {
                "company": "Mindtree",
                "title": "Backend Engineer",
                "start_date": "2024-03-08",
                "end_date": None,
                "duration_months": 27,
                "is_current": True,
                "industry": "IT Services",
                "company_size": "10001+",
                "description": "Implemented Kafka and Spark Streaming pipelines.",
            }
        ],
        "education": [
            {
                "institution": "Lovely Professional University",
                "degree": "B.E.",
                "field_of_study": "Computer Science",
                "start_year": 2017,
                "end_year": 2020,
                "grade": "8.24 CGPA",
                "tier": "tier_3",
            }
        ],
        "skills": [
            {
                "name": "Spark",
                "proficiency": "advanced",
                "endorsements": 12,
                "duration_months": 40,
            }
        ],
        "certifications": [
            {"name": "AWS Certified Developer", "issuer": "AWS", "year": 2023}
        ],
        "languages": [{"language": "English", "proficiency": "professional"}],
        "redrob_signals": {
            "profile_completeness_score": 86.9,
            "signup_date": "2025-10-16",
            "last_active_date": "2026-05-20",
            "open_to_work_flag": True,
            "profile_views_received_30d": 23,
            "applications_submitted_30d": 2,
            "recruiter_response_rate": 0.34,
            "avg_response_time_hours": 177.8,
            "skill_assessment_scores": {"Spark": 74.5},
            "connection_count": 356,
            "endorsements_received": 35,
            "notice_period_days": 60,
            "expected_salary_range_inr_lpa": {"min": 18.7, "max": 36.1},
            "preferred_work_mode": "onsite",
            "willing_to_relocate": False,
            "github_activity_score": 9.2,
            "search_appearance_30d": 249,
            "saved_by_recruiters_30d": 4,
            "interview_completion_rate": 0.71,
            "offer_acceptance_rate": 0.58,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": False,
        },
    }

    text = build_candidate_profile(candidate)

    assert "## Candidate Overview" in text
    assert "## Experience" in text
    assert "## Skills" in text
    assert "## Education" in text
    assert "## Certifications" in text
    assert "## Behavior Signals" in text
    assert "Backend Engineer" in text
    assert "Spark | advanced | 12 endorsements | 40 months" in text
    assert "Redrob skill assessments: Spark: 74.5/100" in text
    assert "Recruiter response rate: 34%" in text


def test_build_candidate_profile_renders_behavior_sentinels_as_meaning() -> None:
    candidate = {
        "candidate_id": "CAND_0000002",
        "profile": {},
        "redrob_signals": {
            "github_activity_score": -1,
            "offer_acceptance_rate": -1,
        },
    }

    text = build_candidate_profile(candidate)

    assert "GitHub activity: no GitHub linked" in text
    assert "Offer acceptance rate: no offer history" in text


def test_build_candidate_documents_adds_metadata() -> None:
    documents = build_candidate_documents(
        [
            {
                "candidate_id": "CAND_0000003",
                "profile": {
                    "current_title": "ML Engineer",
                    "country": "India",
                    "years_of_experience": 5.5,
                },
            }
        ]
    )

    assert documents == [
        {
            "candidate_id": "CAND_0000003",
            "text": build_candidate_profile(
                {
                    "candidate_id": "CAND_0000003",
                    "profile": {
                        "current_title": "ML Engineer",
                        "country": "India",
                        "years_of_experience": 5.5,
                    },
                }
            ),
            "metadata": {
                "candidate_id": "CAND_0000003",
                "current_title": "ML Engineer",
                "country": "India",
                "years_of_experience": 5.5,
            },
        }
    ]
