import pytest
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client() -> TestClient:
    """Fastapi test client."""
    return TestClient(app)
