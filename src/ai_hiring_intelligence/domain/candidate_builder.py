"""Build rich text candidate profiles for semantic search."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


CandidateRecord = Mapping[str, Any]


def build_candidate_profile(candidate: CandidateRecord) -> str:
    """Convert one raw Redrob candidate record into rich semantic-search text."""

    candidate_id = _as_text(candidate.get("candidate_id"))
    profile = _mapping(candidate.get("profile"))
    career_history = _list_of_mappings(candidate.get("career_history"))
    education = _list_of_mappings(candidate.get("education"))
    skills = _list_of_mappings(candidate.get("skills"))
    certifications = _list_of_mappings(candidate.get("certifications"))
    languages = _list_of_mappings(candidate.get("languages"))
    signals = _mapping(candidate.get("redrob_signals"))

    sections = [
        _candidate_overview(candidate_id, profile),
        _experience_section(profile, career_history),
        _skills_section(skills, signals),
        _education_section(education),
        _certifications_section(certifications),
        _languages_section(languages),
        _behavior_section(signals),
    ]
    return "\n\n".join(section for section in sections if section)


def build_candidate_documents(candidates: Iterable[CandidateRecord]) -> list[dict[str, Any]]:
    """Build semantic-search documents with stable IDs and source metadata."""

    documents: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_id = _as_text(candidate.get("candidate_id"))
        documents.append(
            {
                "candidate_id": candidate_id,
                "text": build_candidate_profile(candidate),
                "metadata": {
                    "candidate_id": candidate_id,
                    "current_title": _nested_text(candidate, "profile", "current_title"),
                    "country": _nested_text(candidate, "profile", "country"),
                    "years_of_experience": _nested_value(
                        candidate, "profile", "years_of_experience"
                    ),
                },
            }
        )
    return documents


def _candidate_overview(candidate_id: str, profile: CandidateRecord) -> str:
    lines = [
        _line("Candidate ID", candidate_id),
        _line("Name", profile.get("anonymized_name")),
        _line("Headline", profile.get("headline")),
        _line("Summary", profile.get("summary")),
        _line(
            "Current role",
            _join_nonempty(
                [
                    profile.get("current_title"),
                    profile.get("current_company"),
                    profile.get("current_industry"),
                    _format_company_size(profile.get("current_company_size")),
                ],
                separator=" | ",
            ),
        ),
        _line(
            "Location",
            _join_nonempty([profile.get("location"), profile.get("country")], separator=", "),
        ),
    ]
    return _section("Candidate Overview", lines)


def _experience_section(profile: CandidateRecord, career_history: list[CandidateRecord]) -> str:
    lines = [
        _line("Total experience", _format_years(profile.get("years_of_experience"))),
    ]

    for index, role in enumerate(career_history, start=1):
        status = "current" if role.get("is_current") is True else "previous"
        title = _join_nonempty(
            [
                role.get("title"),
                role.get("company"),
                role.get("industry"),
                _format_company_size(role.get("company_size")),
            ],
            separator=" | ",
        )
        dates = _join_nonempty(
            [
                role.get("start_date"),
                "present" if role.get("end_date") in (None, "") else role.get("end_date"),
                _format_months(role.get("duration_months")),
            ],
            separator=" to ",
        )
        details = _join_nonempty([f"{status} role", dates, role.get("description")], separator=". ")
        lines.append(_line(f"Role {index}", title))
        lines.append(_line(f"Role {index} details", details))

    return _section("Experience", lines)


def _skills_section(skills: list[CandidateRecord], signals: CandidateRecord) -> str:
    lines: list[str] = []
    if skills:
        skill_phrases = []
        for skill in skills:
            phrase = _join_nonempty(
                [
                    skill.get("name"),
                    skill.get("proficiency"),
                    _format_count(skill.get("endorsements"), "endorsement"),
                    _format_months(skill.get("duration_months")),
                ],
                separator=" | ",
            )
            if phrase:
                skill_phrases.append(phrase)
        lines.append(_line("Profile skills", "; ".join(skill_phrases)))

    assessment_scores = _mapping(signals.get("skill_assessment_scores"))
    if assessment_scores:
        scores = [
            f"{skill}: {_format_number(score)}/100"
            for skill, score in sorted(assessment_scores.items())
            if _has_value(skill) and _has_value(score)
        ]
        lines.append(_line("Redrob skill assessments", "; ".join(scores)))

    return _section("Skills", lines)


def _education_section(education: list[CandidateRecord]) -> str:
    lines = []
    for index, item in enumerate(education, start=1):
        degree = _join_nonempty(
            [
                item.get("degree"),
                item.get("field_of_study"),
                item.get("institution"),
                item.get("tier"),
            ],
            separator=" | ",
        )
        details = _join_nonempty(
            [
                _format_year_range(item.get("start_year"), item.get("end_year")),
                item.get("grade"),
            ],
            separator=" | ",
        )
        lines.append(_line(f"Education {index}", degree))
        lines.append(_line(f"Education {index} details", details))
    return _section("Education", lines)


def _certifications_section(certifications: list[CandidateRecord]) -> str:
    lines = []
    for index, certification in enumerate(certifications, start=1):
        lines.append(
            _line(
                f"Certification {index}",
                _join_nonempty(
                    [
                        certification.get("name"),
                        certification.get("issuer"),
                        certification.get("year"),
                    ],
                    separator=" | ",
                ),
            )
        )
    return _section("Certifications", lines)


def _languages_section(languages: list[CandidateRecord]) -> str:
    if not languages:
        return ""

    language_text = "; ".join(
        _join_nonempty([item.get("language"), item.get("proficiency")], separator=" | ")
        for item in languages
    )
    return _section("Languages", [_line("Languages", language_text)])


def _behavior_section(signals: CandidateRecord) -> str:
    if not signals:
        return ""

    salary = _mapping(signals.get("expected_salary_range_inr_lpa"))
    lines = [
        _line("Profile completeness", _format_percent(signals.get("profile_completeness_score"))),
        _line("Signup date", signals.get("signup_date")),
        _line("Last active date", signals.get("last_active_date")),
        _line("Open to work", _format_bool(signals.get("open_to_work_flag"))),
        _line("Preferred work mode", signals.get("preferred_work_mode")),
        _line("Willing to relocate", _format_bool(signals.get("willing_to_relocate"))),
        _line("Notice period", _format_days(signals.get("notice_period_days"))),
        _line(
            "Expected salary",
            _format_salary_range(salary.get("min"), salary.get("max")),
        ),
        _line("Profile views in last 30 days", signals.get("profile_views_received_30d")),
        _line("Search appearances in last 30 days", signals.get("search_appearance_30d")),
        _line("Saved by recruiters in last 30 days", signals.get("saved_by_recruiters_30d")),
        _line("Applications submitted in last 30 days", signals.get("applications_submitted_30d")),
        _line("Recruiter response rate", _format_rate(signals.get("recruiter_response_rate"))),
        _line("Average response time", _format_hours(signals.get("avg_response_time_hours"))),
        _line("Interview completion rate", _format_rate(signals.get("interview_completion_rate"))),
        _line("Offer acceptance rate", _format_offer_rate(signals.get("offer_acceptance_rate"))),
        _line("Connection count", signals.get("connection_count")),
        _line("Endorsements received", signals.get("endorsements_received")),
        _line("GitHub activity", _format_github_activity(signals.get("github_activity_score"))),
        _line("Verified email", _format_bool(signals.get("verified_email"))),
        _line("Verified phone", _format_bool(signals.get("verified_phone"))),
        _line("LinkedIn connected", _format_bool(signals.get("linkedin_connected"))),
    ]
    return _section("Behavior Signals", lines)


def _section(title: str, lines: list[str]) -> str:
    body = [line for line in lines if line]
    if not body:
        return ""
    return "\n".join([f"## {title}", *body])


def _line(label: str, value: Any) -> str:
    if not _has_value(value):
        return ""
    return f"{label}: {_as_text(value)}"


def _mapping(value: Any) -> CandidateRecord:
    return value if isinstance(value, Mapping) else {}


def _list_of_mappings(value: Any) -> list[CandidateRecord]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _nested_value(candidate: CandidateRecord, section: str, key: str) -> Any:
    return _mapping(candidate.get(section)).get(key)


def _nested_text(candidate: CandidateRecord, section: str, key: str) -> str:
    return _as_text(_nested_value(candidate, section, key))


def _join_nonempty(values: Iterable[Any], separator: str) -> str:
    return separator.join(_as_text(value) for value in values if _has_value(value))


def _has_value(value: Any) -> bool:
    return value is not None and value != ""


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    return str(value).strip()


def _format_number(value: Any) -> str:
    if not isinstance(value, int | float):
        return _as_text(value)
    return f"{value:g}"


def _format_years(value: Any) -> str:
    if not _has_value(value):
        return ""
    return f"{_format_number(value)} years"


def _format_months(value: Any) -> str:
    if not _has_value(value):
        return ""
    return f"{_format_number(value)} months"


def _format_days(value: Any) -> str:
    if not _has_value(value):
        return ""
    return f"{_format_number(value)} days"


def _format_hours(value: Any) -> str:
    if not _has_value(value):
        return ""
    return f"{_format_number(value)} hours"


def _format_count(value: Any, noun: str) -> str:
    if not _has_value(value):
        return ""
    count_text = _format_number(value)
    suffix = noun if count_text == "1" else f"{noun}s"
    return f"{count_text} {suffix}"


def _format_percent(value: Any) -> str:
    if not _has_value(value):
        return ""
    return f"{_format_number(value)}%"


def _format_rate(value: Any) -> str:
    if not _has_value(value):
        return ""
    if isinstance(value, int | float):
        return f"{value * 100:g}%"
    return _as_text(value)


def _format_offer_rate(value: Any) -> str:
    if value == -1:
        return "no offer history"
    return _format_rate(value)


def _format_github_activity(value: Any) -> str:
    if value == -1:
        return "no GitHub linked"
    if not _has_value(value):
        return ""
    return f"{_format_number(value)}/100"


def _format_bool(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    return _as_text(value)


def _format_company_size(value: Any) -> str:
    if not _has_value(value):
        return ""
    return f"company size {value}"


def _format_year_range(start_year: Any, end_year: Any) -> str:
    if not _has_value(start_year) and not _has_value(end_year):
        return ""
    return f"{_as_text(start_year)}-{_as_text(end_year)}"


def _format_salary_range(minimum: Any, maximum: Any) -> str:
    if not _has_value(minimum) and not _has_value(maximum):
        return ""
    if _has_value(minimum) and _has_value(maximum):
        return f"{_format_number(minimum)}-{_format_number(maximum)} INR LPA"
    if _has_value(minimum):
        return f"at least {_format_number(minimum)} INR LPA"
    return f"up to {_format_number(maximum)} INR LPA"
