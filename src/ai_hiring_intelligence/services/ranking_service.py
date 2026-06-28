"""Composite candidate ranking service."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from ai_hiring_intelligence.domain.ranking import (
    behavior_score,
    career_score,
    experience_score,
    skill_score,
)


CandidateRecord = Mapping[str, Any]
Requirements = Mapping[str, Sequence[str]]


@dataclass(frozen=True)
class CandidateRanking:
    """One ranked candidate with component scores."""

    candidate_id: str
    rank: int
    score: float
    skill_score: float
    behavior_score: float
    career_score: float
    experience_score: float
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "rank": self.rank,
            "score": self.score,
            "skill_score": self.skill_score,
            "behavior_score": self.behavior_score,
            "career_score": self.career_score,
            "experience_score": self.experience_score,
            "metadata": self.metadata,
        }


class CandidateRanker:
    """Score and rank candidate records against parsed job requirements."""

    def __init__(
        self,
        *,
        skill_weight: float = 0.35,
        behavior_weight: float = 0.2,
        career_weight: float = 0.2,
        experience_weight: float = 0.25,
    ) -> None:
        weights = {
            "skill_weight": skill_weight,
            "behavior_weight": behavior_weight,
            "career_weight": career_weight,
            "experience_weight": experience_weight,
        }
        if any(weight < 0 for weight in weights.values()):
            raise ValueError("weights must be non-negative")

        total = sum(weights.values())
        if total <= 0:
            raise ValueError("at least one weight must be positive")

        self.skill_weight = skill_weight / total
        self.behavior_weight = behavior_weight / total
        self.career_weight = career_weight / total
        self.experience_weight = experience_weight / total

    def score_candidate(self, candidate: CandidateRecord, requirements: Requirements) -> CandidateRanking:
        """Compute the component and composite scores for a single candidate."""

        skill = skill_score(candidate, requirements)
        behavior = behavior_score(candidate, requirements)
        career = career_score(candidate, requirements)
        experience = experience_score(candidate, requirements)
        score = (
            (skill * self.skill_weight)
            + (behavior * self.behavior_weight)
            + (career * self.career_weight)
            + (experience * self.experience_weight)
        )
        candidate_id = _candidate_id(candidate)
        metadata = _candidate_metadata(candidate)

        return CandidateRanking(
            candidate_id=candidate_id,
            rank=0,
            score=_clamp01(score),
            skill_score=skill,
            behavior_score=behavior,
            career_score=career,
            experience_score=experience,
            metadata=metadata,
        )

    def rank_candidates(
        self,
        candidates: Iterable[CandidateRecord],
        requirements: Requirements,
        *,
        top_k: int | None = None,
    ) -> list[CandidateRanking]:
        """Return ranked candidates sorted by composite score."""

        scored = [self.score_candidate(candidate, requirements) for candidate in candidates]
        scored.sort(key=lambda item: item.score, reverse=True)

        ranked: list[CandidateRanking] = []
        for index, item in enumerate(scored, start=1):
            ranked.append(
                CandidateRanking(
                    candidate_id=item.candidate_id,
                    rank=index,
                    score=item.score,
                    skill_score=item.skill_score,
                    behavior_score=item.behavior_score,
                    career_score=item.career_score,
                    experience_score=item.experience_score,
                    metadata=item.metadata,
                )
            )
            if top_k is not None and len(ranked) >= top_k:
                break
        return ranked

    def rank_candidates_dicts(
        self,
        candidates: Iterable[CandidateRecord],
        requirements: Requirements,
        *,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return ranked candidates as JSON-friendly dictionaries."""

        return [item.to_dict() for item in self.rank_candidates(candidates, requirements, top_k=top_k)]


def _candidate_id(candidate: CandidateRecord) -> str:
    value = candidate.get("candidate_id")
    return str(value) if value is not None else ""


def _candidate_metadata(candidate: CandidateRecord) -> dict[str, Any]:
    profile = candidate.get("profile")
    if isinstance(profile, Mapping):
        profile = dict(profile)
    else:
        profile = {}
    career_history = candidate.get("career_history")
    if isinstance(career_history, list):
        profile["career_history_count"] = len(career_history)
    return profile


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
