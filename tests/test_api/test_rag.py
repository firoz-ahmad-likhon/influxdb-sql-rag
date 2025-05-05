from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient
from api.rag import app, rag
from langchain_core.runnables.config import RunnableConfig
from http import HTTPStatus


class TestRAGAPI:
    """Test RAG API."""

    @pytest.fixture(autouse=True)
    def setup_method(self) -> None:
        """Initialize test."""
        self.client = TestClient(app)

    def test_root(self) -> None:
        """Test root endpoint."""
        response = self.client.get("/api/")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"message": "Welcome to the InfluxDB RAG API."}

    def test_chat_success(self, monkeypatch: Generator[pytest.MonkeyPatch]) -> None:
        """Test chat endpoint with successful response."""

        # Mock RAG response
        class MockResponse:
            """Mock response class."""

            def get(self, key: str, default: str | None = None) -> str | None:
                """Mock get method."""
                if key == "answer":
                    return "Mocked answer"
                return default

        def mock_invoke(
            inputs: dict[str, str],
            config: RunnableConfig = None,
        ) -> MockResponse:
            """Mock function for invoke."""
            assert (
                inputs["question"] == "What is the average temperature?"
            )  # Assert correct input
            return MockResponse()

        # Monkeypatch the invoke method to return the mocked response
        monkeypatch.setattr(rag, "invoke", mock_invoke)

        # Make the API call
        response = self.client.post(
            "/api/chat",
            json={"question": "What is the average temperature?"},
        )

        # Check that the status code and the response match the expected output
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"answer": "Mocked answer"}

    def test_chat_failure(self, monkeypatch: Generator[pytest.MonkeyPatch]) -> None:
        """Test chat endpoint with failure response."""

        def mock_invoke(inputs: dict[str, str], config: RunnableConfig = None) -> None:
            """Mock function for invoke that raises an exception."""
            raise ValueError("Simulated failure")

        # Monkeypatch the invoke method to simulate an error
        monkeypatch.setattr(rag, "invoke", mock_invoke)

        # Make the API call
        response = self.client.post("/api/chat", json={"question": "Trigger error"})

        assert response.status_code == HTTPStatus.OK
        assert "error" in response.json()
        assert response.json()["error"] == "Simulated failure"
