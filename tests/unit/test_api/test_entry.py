from http import HTTPStatus
from fastapi.testclient import TestClient


class TestEntry:
    """Test entry point routes."""

    def test_root(self, client: TestClient) -> None:
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == HTTPStatus.OK

    def test_health_check(self, client: TestClient) -> None:
        """Test health check."""
        response = client.get("health")
        assert response.status_code == HTTPStatus.OK
