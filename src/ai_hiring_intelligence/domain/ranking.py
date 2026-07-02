"""Candidate scoring utilities for ranking."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


CandidateRecord = Mapping[str, Any]
Requirements = Mapping[str, Sequence[str]]

PROFICIENCY_WEIGHTS = {
    "beginner": 0.35,
    "intermediate": 0.6,
    "advanced": 0.82,
    "expert": 1.0,
}


def skill_score(candidate: CandidateRecord, requirements: Requirements) -> float:
    """Score candidate skills against parsed job skill requirements."""

    required_skills = _normalized_terms(requirements.get("skills", []))
    if not required_skills:
        return 0.0

    candidate_skills = _candidate_skill_terms(candidate)
    assessment_scores = _assessment_scores(candidate)
    total = 0.0

    for required_skill in required_skills:
        best = 0.0
        for skill_name, skill_quality in candidate_skills.items():
            if _term_matches(required_skill, skill_name):
                best = max(best, skill_quality)

        for assessed_skill, assessment_score in assessment_scores.items():
            if _term_matches(required_skill, assessed_skill):
                best = max(best, 0.5 + (assessment_score / 100 * 0.5))

        total += best

    return _clamp01(total / len(required_skills))


def behavior_score(candidate: CandidateRecord, requirements: Requirements | None = None) -> float:
    """Score availability, responsiveness, platform trust, and work-style behavior."""

    signals = _mapping(candidate.get("redrob_signals"))
    if not signals:
        return 0.0

    components = [
        _scale(signals.get("profile_completeness_score"), 0, 100),
        _rate(signals.get("recruiter_response_rate")),
        1.0 - _scale(signals.get("avg_response_time_hours"), 0, 240),
        _scale(signals.get("profile_views_received_30d"), 0, 100),
        _scale(signals.get("search_appearance_30d"), 0, 300),
        _scale(signals.get("saved_by_recruiters_30d"), 0, 20),
        _rate(signals.get("interview_completion_rate")),
        _offer_acceptance_component(signals.get("offer_acceptance_rate")),
        _scale(signals.get("connection_count"), 0, 500),
        _scale(signals.get("endorsements_received"), 0, 100),
        _github_component(signals.get("github_activity_score")),
        1.0 if signals.get("open_to_work_flag") is True else 0.35,
        1.0 if signals.get("verified_email") is True else 0.0,
        1.0 if signals.get("verified_phone") is True else 0.0,
        1.0 if signals.get("linkedin_connected") is True else 0.0,
    ]

    score = _mean(components)
    behavior_traits = _normalized_terms((requirements or {}).get("behavior_traits", []))
    if behavior_traits:
        profile_text = _candidate_text(candidate)
        matched = sum(1 for trait in behavior_traits if trait in profile_text)
        score = 0.8 * score + 0.2 * (matched / len(behavior_traits))

    base_behavior_score = _clamp01(score)

    # -------------------------------------------------------------
    # JD Constraint 3: Notice Period Penalty (sub-30-day notice preferred)
    # -------------------------------------------------------------
    notice_days = signals.get("notice_period_days")
    if notice_days is not None:
        try:
            days = float(notice_days)
            if days > 60:
                base_behavior_score *= 0.7  # 30% penalty for long notice period (e.g. 90 days)
            elif days > 30:
                base_behavior_score *= 0.85 # 15% penalty for >30 days notice
        except (ValueError, TypeError):
            pass

    # -------------------------------------------------------------
    # JD Constraint 4: Inactivity Penalty (haven't logged in for 6+ months)
    # -------------------------------------------------------------
    last_active = signals.get("last_active_date")
    if last_active:
        try:
            from datetime import datetime
            active_date = datetime.strptime(str(last_active).strip()[:10], "%Y-%m-%d")
            # Current time of challenge/metadata is 2026-07-02
            current_date = datetime(2026, 7, 2)
            days_inactive = (current_date - active_date).days
            
            if days_inactive > 180:   # 6 months
                base_behavior_score *= 0.4  # 60% penalty
            elif days_inactive > 90:  # 3 months
                base_behavior_score *= 0.7  # 30% penalty
        except Exception:
            pass

    return _clamp01(base_behavior_score)


def career_score(candidate: CandidateRecord, requirements: Requirements) -> float:
    """Score career alignment with role, domain, leadership, and job-description context."""

    profile = _mapping(candidate.get("profile"))
    career_history = _list_of_mappings(candidate.get("career_history"))
    requirements_text = _requirements_text(requirements)
    candidate_text = _candidate_text(candidate)

    title_terms = _normalized_terms(
        [
            profile.get("current_title"),
            *(role.get("title") for role in career_history),
            profile.get("current_industry"),
            *(role.get("industry") for role in career_history),
        ]
    )
    title_overlap = _overlap_score(title_terms, _token_set(requirements_text))

    career_descriptions = " ".join(
        _normalize_text(role.get("description", "")) for role in career_history
    )
    requirement_phrases = [
        phrase
        for phrase in _normalized_terms(
            [
                *requirements.get("experience", []),
                *requirements.get("leadership_requirements", []),
            ]
        )
        if "year" not in phrase
    ]
    phrase_match = _phrase_match_score(requirement_phrases, candidate_text + " " + career_descriptions)

    current_role_bonus = 1.0 if any(role.get("is_current") is True for role in career_history) else 0.0
    industry_signal = _overlap_score(
        _normalized_terms([profile.get("current_industry")]),
        _token_set(requirements_text),
    )

    base_career_score = _clamp01(
        (0.15 * title_overlap)
        + (0.55 * phrase_match)
        + (0.1 * industry_signal)
        + (0.2 * current_role_bonus)
    )

    # -------------------------------------------------------------
    # JD Constraint 1: Marketing Manager/Non-Tech Title Penalty
    # -------------------------------------------------------------
    title = _normalize_text(profile.get("current_title", ""))
    non_tech_titles = {
        "marketing", "sales", "hr", "recruiter", "human resources", "operations", 
        "finance", "accountant", "accounting", "customer support", "customer success",
        "mechanical", "civil", "product manager", "project manager", "admin", "administrator"
    }
    title_tokens = _token_set(title)
    has_non_tech = any(kw in title or kw in title_tokens for kw in non_tech_titles)
    
    tech_keywords = {
        "engineer", "developer", "scientist", "programmer", "architect", "coding", "software", "tech"
    }
    has_tech = any(kw in title or kw in title_tokens for kw in tech_keywords)
    
    if has_non_tech and not has_tech:
        base_career_score *= 0.1  # 90% penalty for non-technical trap profiles
        
    # -------------------------------------------------------------
    # JD Constraint 2: Consulting Company Only Penalty (TCS, Infosys, etc.)
    # -------------------------------------------------------------
    if career_history:
        consulting_keywords = {
            "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
            "tata consultancy", "tata consultancy services"
        }
        companies = []
        for role in career_history:
            comp = _normalize_text(role.get("company", ""))
            if comp:
                companies.append(comp)
        
        if companies:
            all_consulting = True
            for comp in companies:
                comp_tokens = _token_set(comp)
                is_consulting = False
                for kw in consulting_keywords:
                    if kw in comp or any(kw in token for token in comp_tokens):
                        is_consulting = True
                        break
                if not is_consulting:
                    all_consulting = False
                    break
            if all_consulting:
                base_career_score *= 0.2  # 80% penalty if candidate has only worked at consulting firms

    return _clamp01(base_career_score)


def experience_score(candidate: CandidateRecord, requirements: Requirements) -> float:
    """Score years and depth of experience against parsed experience requirements."""

    profile = _mapping(candidate.get("profile"))
    years = _float(profile.get("years_of_experience"))
    min_years, max_years = _experience_range(requirements.get("experience", []))

    if min_years is None and max_years is None:
        years_component = _scale(years, 0, 12)
    elif min_years is not None and max_years is not None:
        if years < min_years:
            years_component = years / min_years if min_years > 0 else 1.0
        elif years <= max_years:
            years_component = 1.0
        else:
            years_component = max(0.65, 1.0 - ((years - max_years) / max(max_years, 1) * 0.25))
    elif min_years is not None:
        years_component = min(years / min_years, 1.0) if min_years > 0 else 1.0
    else:
        years_component = 1.0 if years <= max_years else max(0.0, 1.0 - ((years - max_years) / 10))

    career_history = _list_of_mappings(candidate.get("career_history"))
    depth_component = _clamp01(len(career_history) / 4)
    tenure_months = [_float(role.get("duration_months")) for role in career_history]
    tenure_component = _scale(sum(tenure_months), 0, 120)

    return _clamp01((0.65 * years_component) + (0.2 * tenure_component) + (0.15 * depth_component))


def _candidate_skill_terms(candidate: CandidateRecord) -> dict[str, float]:
    terms: dict[str, float] = {}
    for skill in _list_of_mappings(candidate.get("skills")):
        name = _normalize_text(skill.get("name", ""))
        if not name:
            continue
        proficiency = _normalize_text(skill.get("proficiency", ""))
        proficiency_score = PROFICIENCY_WEIGHTS.get(proficiency, 0.5)
        endorsement_score = _scale(skill.get("endorsements"), 0, 50)
        duration_score = _scale(skill.get("duration_months"), 0, 48)
        terms[name] = max(
            terms.get(name, 0.0),
            (0.55 * proficiency_score) + (0.25 * endorsement_score) + (0.2 * duration_score),
        )
    return terms


def _assessment_scores(candidate: CandidateRecord) -> dict[str, float]:
    signals = _mapping(candidate.get("redrob_signals"))
    scores = _mapping(signals.get("skill_assessment_scores"))
    return {
        _normalize_text(skill): _scale(score, 0, 100) * 100
        for skill, score in scores.items()
        if _normalize_text(skill)
    }


def _experience_range(experience_requirements: Sequence[str]) -> tuple[float | None, float | None]:
    import re

    text = " ".join(experience_requirements).lower()
    if not text:
        return None, None

    range_match = re.search(r"(\d+(?:\.\d+)?)\s*[-–to]+\s*(\d+(?:\.\d+)?)\s*\+?\s*years?", text)
    if range_match:
        return float(range_match.group(1)), float(range_match.group(2))

    plus_match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", text)
    if plus_match:
        return float(plus_match.group(1)), None

    return None, None


def _requirements_text(requirements: Requirements) -> str:
    values: list[str] = []
    for items in requirements.values():
        values.extend(str(item) for item in items)
    return _normalize_text(" ".join(values))


def _candidate_text(candidate: CandidateRecord) -> str:
    profile = _mapping(candidate.get("profile"))
    values = [
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_industry", ""),
    ]
    for role in _list_of_mappings(candidate.get("career_history")):
        values.extend([role.get("title", ""), role.get("industry", ""), role.get("description", "")])
    return _normalize_text(" ".join(str(value) for value in values))


def _phrase_match_score(phrases: Sequence[str], text: str) -> float:
    if not phrases:
        return 0.0
    matches = 0.0
    tokens = _token_set(text)
    for phrase in phrases:
        if phrase in text:
            matches += 1.0
        else:
            phrase_tokens = _token_set(phrase)
            matches += _overlap_score(list(phrase_tokens), tokens)
    return _clamp01(matches / len(phrases))


def _overlap_score(terms: Sequence[str], tokens: set[str]) -> float:
    term_tokens = {token for term in terms for token in _token_set(term)}
    if not term_tokens:
        return 0.0
    return len(term_tokens & tokens) / len(term_tokens)


def _term_matches(required: str, candidate: str) -> bool:
    return required in candidate or candidate in required or bool(_token_set(required) & _token_set(candidate))


def _normalized_terms(values: Sequence[Any]) -> list[str]:
    return [term for value in values if (term := _normalize_text(value))]


def _token_set(text: str) -> set[str]:
    return {token for token in _normalize_text(text).split() if len(token) > 1}


def _normalize_text(value: Any) -> str:
    return " ".join(str(value or "").casefold().replace("/", " ").replace("-", " ").split())


def _mapping(value: Any) -> CandidateRecord:
    return value if isinstance(value, Mapping) else {}


def _list_of_mappings(value: Any) -> list[CandidateRecord]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _rate(value: Any) -> float:
    return _scale(value, 0, 1)


def _github_component(value: Any) -> float:
    if value == -1:
        return 0.4
    return _scale(value, 0, 100)


def _offer_acceptance_component(value: Any) -> float:
    if value == -1:
        return 0.5
    return _rate(value)


def _scale(value: Any, minimum: float, maximum: float) -> float:
    numeric = _float(value)
    if maximum <= minimum:
        return 0.0
    return _clamp01((numeric - minimum) / (maximum - minimum))


def _mean(values: Sequence[float]) -> float:
    clean = [value for value in values if value == value]
    if not clean:
        return 0.0
    return sum(clean) / len(clean)


def _float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
