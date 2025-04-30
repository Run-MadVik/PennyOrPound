"""Tests for the health endpoint."""

from fastapi.testclient import TestClient
import pytest

from pennyorpound import app


@pytest.fixture(name="client")
def fixture_client() -> TestClient:
    """Test client fixture."""
    return TestClient(app)


def test_health_check(client: TestClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data
