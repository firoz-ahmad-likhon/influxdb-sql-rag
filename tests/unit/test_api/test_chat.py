import http
import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables.config import RunnableConfig
from api.dependencies import get_graph, get_config


@pytest.fixture
def mock_dependencies(
    client: TestClient,
    mocker: MockerFixture,
) -> tuple[CompiledStateGraph, RunnableConfig]:
    """Fixture to mock and override dependencies."""
    mock_rag = mocker.Mock(spec=CompiledStateGraph)
    mock_config = mocker.Mock(spec=RunnableConfig)

    client.app.dependency_overrides[get_graph] = lambda: mock_rag
    client.app.dependency_overrides[get_config] = lambda: mock_config

    return mock_rag, mock_config


class TestChat:
    """Test chat route."""

    def test_chat_success(
        self,
        client: TestClient,
        mock_dependencies: tuple[CompiledStateGraph, RunnableConfig],
    ) -> None:
        """Test chat success."""
        mock_rag, mock_config = mock_dependencies
        mock_rag.invoke.return_value = {"answer": "Mocked Answer"}

        response = client.post("/chat", json={"question": "What is AI?"})

        assert response.status_code == http.HTTPStatus.OK
        assert response.json() == {"answer": "Mocked Answer"}
        mock_rag.invoke.assert_called_once_with(
            {"question": "What is AI?"},
            config=mock_config,
        )

    def test_chat_empty_payload(self, client: TestClient) -> None:
        """Test chat error when payload is invalid."""
        response = client.post("/chat", json={})
        assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY

    def test_chat_error(
        self,
        client: TestClient,
        mock_dependencies: tuple[CompiledStateGraph, RunnableConfig],
    ) -> None:
        """Test chat when a generic exception is raised."""
        mock_rag, mock_config = mock_dependencies
        error_message = "Something went terribly wrong"
        mock_rag.invoke.side_effect = Exception(error_message)

        response = client.post("/chat", json={"question": "What is AI?"})

        assert response.status_code == http.HTTPStatus.OK
        assert response.json() == {"error": error_message}
        mock_rag.invoke.assert_called_once_with(
            {"question": "What is AI?"},
            config=mock_config,
        )
