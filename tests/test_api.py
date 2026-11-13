import json

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_provider
from app.providers.base import LLMProviderError
from tests.fakes import FakeProvider

TEXT = "Cargo: Desarrollador Python. Requisitos: Python."
GENERIC_ERROR = "The AI service could not process the request. Please try again in a moment."


@pytest.fixture
def client_with():
    """Return a function that builds a test client using the given provider."""

    def _make(provider: FakeProvider) -> TestClient:
        app.dependency_overrides[get_provider] = lambda: provider
        return TestClient(app)

    yield _make
    app.dependency_overrides.clear()


def test_health():
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_extract_job_returns_verified_posting(client_with):
    provider = FakeProvider(
        json.dumps(
            {
                "title": "Desarrollador Python",
                "required_skills": [{"name": "Python", "source": "Requisitos: Python"}],
            }
        )
    )

    response = client_with(provider).post("/extract-job", json={"text": TEXT})

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Desarrollador Python"
    assert body["company"] is None
    assert [s["name"] for s in body["required_skills"]] == ["Python"]


def test_blank_text_returns_422_without_calling_provider(client_with):
    provider = FakeProvider()

    response = client_with(provider).post("/extract-job", json={"text": "   "})

    assert response.status_code == 422
    assert provider.prompts == []


def test_too_long_text_returns_422(client_with):
    response = client_with(FakeProvider()).post("/extract-job", json={"text": "a" * 20_001})
    assert response.status_code == 422


def test_missing_text_field_returns_422(client_with):
    response = client_with(FakeProvider()).post("/extract-job", json={})
    assert response.status_code == 422


def test_provider_failure_returns_502_without_internal_details(client_with):
    provider = FakeProvider(error=LLMProviderError("internal detail: quota exceeded"))

    response = client_with(provider).post("/extract-job", json={"text": TEXT})

    assert response.status_code == 502
    assert response.json() == {"detail": GENERIC_ERROR}
    assert "internal detail" not in response.text