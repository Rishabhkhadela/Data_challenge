"""LLM-backed job description parser."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any, Protocol


class JobParserLLMClient(Protocol):
    """Minimal protocol for an injectable LLM client."""

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        """Return a JSON string from an LLM."""


@dataclass(frozen=True)
class ParsedJobRequirements:
    """Structured job requirements extracted from a job description."""

    skills: list[str]
    experience: list[str]
    behavior_traits: list[str]
    leadership_requirements: list[str]

    def to_dict(self) -> dict[str, list[str]]:
        """Return JSON-serializable parsed requirements."""

        return asdict(self)

    def to_json(self) -> str:
        """Return parsed requirements as a JSON string."""

        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


class JobParser:
    """Parse job descriptions into semantic-search requirements using an LLM."""

    def __init__(self, llm_client: JobParserLLMClient) -> None:
        self.llm_client = llm_client

    def parse(self, job_description: str) -> dict[str, list[str]]:
        """Extract skills, experience, behavior traits, and leadership requirements."""

        if not job_description.strip():
            raise ValueError("job_description cannot be empty")

        raw_response = self.llm_client.complete_json(
            _system_prompt(),
            _user_prompt(job_description),
        )
        parsed = parse_job_requirements_json(raw_response)
        return parsed.to_dict()

    def parse_json(self, job_description: str) -> str:
        """Parse a job description and return a JSON string."""

        return json.dumps(self.parse(job_description), ensure_ascii=False, indent=2)


def parse_job_requirements_json(raw_response: str) -> ParsedJobRequirements:
    """Validate and normalize an LLM JSON response."""

    payload = _load_json_object(raw_response)
    return ParsedJobRequirements(
        skills=_string_list(payload, "skills"),
        experience=_string_list(payload, "experience"),
        behavior_traits=_string_list(payload, "behavior_traits"),
        leadership_requirements=_string_list(payload, "leadership_requirements"),
    )


def _system_prompt() -> str:
    return (
        "You are a precise hiring-intelligence job parser. "
        "Extract only requirements supported by the job description. "
        "Return strict JSON with exactly these keys: skills, experience, "
        "behavior_traits, leadership_requirements. Each value must be an array of strings. "
        "Do not include markdown, commentary, scores, or extra keys."
    )


def _user_prompt(job_description: str) -> str:
    return (
        "Parse this job description into structured hiring requirements.\n\n"
        "Extraction guidance:\n"
        "- skills: technical skills, tools, frameworks, domains, methods, and required knowledge.\n"
        "- experience: years, role history, company-stage context, project types, and domain exposure.\n"
        "- behavior_traits: working style, collaboration, ownership, ambiguity tolerance, communication, "
        "and availability traits.\n"
        "- leadership_requirements: team leadership, founding-team expectations, mentoring, strategy, "
        "cross-functional influence, and decision ownership.\n\n"
        f"Job description:\n{job_description.strip()}"
    )


def _load_json_object(raw_response: str) -> Mapping[str, Any]:
    cleaned = _strip_json_fence(raw_response)
    try:
        payload = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError("LLM response was not valid JSON") from exc

    if not isinstance(payload, Mapping):
        raise ValueError("LLM response must be a JSON object")
    return payload


def _strip_json_fence(raw_response: str) -> str:
    text = raw_response.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def _string_list(payload: Mapping[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if value is None:
        return []
    if not isinstance(value, Sequence) or isinstance(value, str | bytes):
        raise ValueError(f"{key} must be an array of strings")

    normalized = []
    for item in value:
        if not isinstance(item, str):
            raise ValueError(f"{key} must contain only strings")
        item_text = item.strip()
        if item_text:
            normalized.append(item_text)
    return _dedupe_preserve_order(normalized)


def _dedupe_preserve_order(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        key = value.casefold()
        if key not in seen:
            seen.add(key)
            output.append(value)
    return output
