from fastapi.testclient import TestClient
from ai_hiring_intelligence.api.main import create_app

def test_hiring_endpoints() -> None:
    client = TestClient(create_app())

    # 1. Test settings GET
    res = client.get("/api/settings")
    assert res.status_code == 200
    settings = res.json()
    assert "weights" in settings
    assert "dataset_mode" in settings
    assert "jd_text" in settings

    # 2. Test settings POST (Update weights)
    res = client.post("/api/settings", json={
        "weights": {
            "skill": 0.4,
            "behavior": 0.2,
            "career": 0.2,
            "experience": 0.2
        }
    })
    assert res.status_code == 200
    updated_settings = res.json()
    # Normalized: 0.4/1 = 0.4
    assert updated_settings["weights"]["skill"] == 0.4

    # 3. Test job requirements GET
    res = client.get("/api/job/requirements")
    assert res.status_code == 200
    reqs = res.json()
    assert "skills" in reqs

    # 4. Test job description parse POST
    res = client.post("/api/job/parse", json={"jd_text": "Need python developer with 5 years experience and great leadership"})
    assert res.status_code == 200
    parsed = res.json()
    assert "skills" in parsed
    assert len(parsed["skills"]) > 0

    # 5. Test candidates list GET
    res = client.get("/api/candidates?limit=2")
    assert res.status_code == 200
    data = res.json()
    assert "candidates" in data
    assert "total_count" in data
    assert len(data["candidates"]) <= 2

    # 6. Test single candidate details
    if len(data["candidates"]) > 0:
        c_id = data["candidates"][0]["candidate_id"]
        res = client.get(f"/api/candidates/{c_id}")
        assert res.status_code == 200
        details = res.json()
        assert details["candidate_id"] == c_id
        assert "key_strengths" in details
        assert "risks_gaps" in details
        assert "recommendation" in details

        # 7. Test compare candidates
        res = client.get(f"/api/compare?c1_id={c_id}&c2_id={c_id}")
        assert res.status_code == 200
        comp = res.json()
        assert comp["c1"]["candidate_id"] == c_id
        assert comp["c2"]["candidate_id"] == c_id

    # 8. Test rankings GET
    res = client.get("/api/rankings?limit=5")
    assert res.status_code == 200
    rankings = res.json()
    assert "rankings" in rankings
    assert len(rankings["rankings"]) <= 5

    # 9. Test analytics GET
    res = client.get("/api/analytics")
    assert res.status_code == 200
    analytics = res.json()
    assert "kpis" in analytics
    assert "experience_distribution" in analytics
    assert "work_mode_distribution" in analytics

    # 10. Test insights GET
    res = client.get("/api/insights")
    assert res.status_code == 200
    insights = res.json()
    assert "interview_order" in insights
    assert "skill_gaps" in insights
    assert "fast_track" in insights

    # 11. Test export CSV stream
    res = client.get("/api/export")
    assert res.status_code == 200
    assert res.headers["content-type"] == "text/csv; charset=utf-8"
    assert "team_submission.csv" in res.headers["content-disposition"]
