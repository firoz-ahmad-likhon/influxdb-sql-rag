import pytest
from src.utils.helper import Helper
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver


class TestHelper:
    """Test Helper class."""

    def test_checkpoint_returns_saver(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test checkpoint function."""
        monkeypatch.setenv("CHECKPOINTER", "memory")

        checkpointer = Helper.checkpoint()
        assert isinstance(checkpointer, BaseCheckpointSaver)
        assert isinstance(checkpointer, MemorySaver)

    @pytest.mark.parametrize(
        ("target", "candidates", "expected"),
        [
            ("sensor", ["sensor_data", "temperature", "humidity"], "sensor_data"),
            ("temp", ["sensor_data", "temperature", "humidity"], "temperature"),
            ("hum", ["sensor_data", "temperature", "humidity"], "humidity"),
            ("xyz", ["sensor_data", "temperature", "humidity"], None),
            ("", ["sensor_data"], None),
            ("sensor", [], None),
        ],
    )
    def test_find_similar_item(
        self,
        target: str,
        candidates: list[str],
        expected: str | None,
    ) -> None:
        """Test find_similar_item function."""
        result = Helper.find_similar_item(target, candidates)
        assert result == expected
