from http import HTTPStatus
from fastapi.testclient import TestClient
import pytest


class TestEntry:
    """Test entry point routes."""

    @pytest.fixture(autouse=True)
    def setup_method(self, client: TestClient) -> None:
        """Initialize."""
        self.client = client

    def test_root(self) -> None:
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == HTTPStatus.OK

    def test_health_check(self) -> None:
        """Test health check."""
        response = self.client.get("health")
        assert response.status_code == HTTPStatus.OK
