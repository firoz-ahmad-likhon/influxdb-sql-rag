import pytest
from src.agent.state import State


@pytest.fixture
def mock_state() -> State:
    """Fixture for mocking state."""
    return State(result=[{"id": 1, "value": 10}], type="query")
