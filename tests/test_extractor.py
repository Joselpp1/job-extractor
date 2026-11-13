import json

import pytest

from app.extractor import extract_job
from app.providers.base import LLMProviderError
from tests.fakes import FakeProvider

TEXT = "Cargo: Desarrollador Python. Empresa: TechNova SAS. Modalidad: remoto. Requisitos: Python y SQL."


def ai_response(**fields) -> str:
    """Build the JSON text the fake AI will return."""
    return json.dumps(fields)


def test_returns_verified_posting():
    provider = FakeProvider(
        ai_response(
            title="Desarrollador Python",
            company="TechNova SAS",
            modality="remote",
            modality_source="Modalidad: remoto",
            required_skills=[{"name": "Python", "source": "Python y SQL"}],
        )
    )

    result = extract_job(TEXT, provider)

    assert result.title == "Desarrollador Python"
    assert result.company == "TechNova SAS"
    assert result.modality == "remote"
    assert [s.name for s in result.required_skills] == ["Python"]


def test_removes_invented_data_from_ai_response():
    provider = FakeProvider(
        ai_response(
            company="Google",
            salary="$5.000.000",
            required_skills=[{"name": "Kubernetes", "source": "Kubernetes avanzado"}],
        )
    )

    result = extract_job(TEXT, provider)

    assert result.company is None
    assert result.salary is None
    assert result.required_skills == []


def test_invalid_json_raises_provider_error():
    with pytest.raises(LLMProviderError):
        extract_job(TEXT, FakeProvider("this is not json"))


def test_json_with_wrong_values_raises_provider_error():
    # "remoto" is not one of the allowed modality values.
    with pytest.raises(LLMProviderError):
        extract_job(TEXT, FakeProvider(ai_response(modality="remoto")))


def test_provider_error_is_propagated():
    provider = FakeProvider(error=LLMProviderError("service unavailable"))
    with pytest.raises(LLMProviderError):
        extract_job(TEXT, provider)


def test_prompt_wraps_posting_in_tags():
    provider = FakeProvider()

    extract_job(TEXT, provider)

    assert f"<posting>\n{TEXT}\n</posting>" in provider.prompts[0]