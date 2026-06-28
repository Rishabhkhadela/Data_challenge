import json

import pytest

from ai_hiring_intelligence.services.job_parser import (
    JobParser,
    parse_job_requirements_json,
)


class FakeLLMClient:
    def __init__(self, response: str) -> None:
        self.response = response
        self.calls = []

    def complete_json(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        return self.response


def test_job_parser_returns_structured_json_dict() -> None:
    client = FakeLLMClient(
        json.dumps(
            {
                "skills": ["LLMs", "RAG", "Python"],
                "experience": ["5-9 years", "production AI systems"],
                "behavior_traits": ["comfortable with ambiguity", "product-minded"],
                "leadership_requirements": ["founding team ownership", "mentor engineers"],
            }
        )
    )
    parser = JobParser(client)

    result = parser.parse("Senior AI Engineer needed for LLM and RAG systems.")

    assert result == {
        "skills": ["LLMs", "RAG", "Python"],
        "experience": ["5-9 years", "production AI systems"],
        "behavior_traits": ["comfortable with ambiguity", "product-minded"],
        "leadership_requirements": ["founding team ownership", "mentor engineers"],
    }
    assert "strict JSON" in client.calls[0]["system_prompt"]
    assert "Senior AI Engineer" in client.calls[0]["user_prompt"]


def test_job_parser_parse_json_returns_json_string() -> None:
    parser = JobParser(
        FakeLLMClient(
            '{"skills":["Python"],"experience":[],"behavior_traits":[],"leadership_requirements":[]}'
        )
    )

    parsed = json.loads(parser.parse_json("Python role"))

    assert parsed["skills"] == ["Python"]


def test_parse_job_requirements_json_strips_markdown_fence_and_dedupes() -> None:
    parsed = parse_job_requirements_json(
        """```json
{
  "skills": ["Python", "python", "FAISS"],
  "experience": ["5+ years"],
  "behavior_traits": ["ownership"],
  "leadership_requirements": ["cross-functional influence"]
}
```"""
    )

    assert parsed.to_dict() == {
        "skills": ["Python", "FAISS"],
        "experience": ["5+ years"],
        "behavior_traits": ["ownership"],
        "leadership_requirements": ["cross-functional influence"],
    }


def test_parse_job_requirements_json_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError, match="skills must be an array"):
        parse_job_requirements_json(
            '{"skills":"Python","experience":[],"behavior_traits":[],"leadership_requirements":[]}'
        )


def test_job_parser_rejects_empty_job_description() -> None:
    parser = JobParser(
        FakeLLMClient(
            '{"skills":[],"experience":[],"behavior_traits":[],"leadership_requirements":[]}'
        )
    )

    with pytest.raises(ValueError, match="job_description cannot be empty"):
        parser.parse("   ")
