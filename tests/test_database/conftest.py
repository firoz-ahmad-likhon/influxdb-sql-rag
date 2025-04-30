import pytest
from unittest.mock import MagicMock
from src.agent.state import State


@pytest.fixture
def mock_client() -> MagicMock:
    """Fixture for mocking InfluxDBClient3."""
    return MagicMock()


@pytest.fixture
def mock_llm() -> MagicMock:
    """Fixture for mocking ChatOllama."""
    return MagicMock()


@pytest.fixture
def mock_state() -> State:
    """Fixture for mocking state."""
    return State(result=[{"id": 1, "value": 10}], type="query")
