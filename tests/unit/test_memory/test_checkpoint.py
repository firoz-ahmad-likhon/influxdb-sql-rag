import pytest
from pytest_mock import MockerFixture
from src.memory.checkpoint import CheckpointSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver


class TestCheckpointSaver:
    """Test the checkpoint."""

    def test_checkpoint_saver_memory(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test the saver for inmemory."""
        monkeypatch.setenv("CHECKPOINTER", "memory")

        saver = CheckpointSaver().saver()

        assert saver is not None
        assert isinstance(saver, BaseCheckpointSaver)
        assert isinstance(saver, InMemorySaver)

    def test_checkpoint_saver_postgres(
        self,
        monkeypatch: pytest.MonkeyPatch,
        mocker: MockerFixture,
    ) -> None:
        """Test the saver for postgres."""
        mock_postgres_saver = mocker.Mock(spec=PostgresSaver)
        mocker.patch(
            "src.memory.checkpoint.PostgresSaver",
            return_value=mock_postgres_saver,
        )

        monkeypatch.setenv("CHECKPOINTER", "postgres")

        saver = CheckpointSaver().saver()

        assert saver is not None
        assert isinstance(saver, BaseCheckpointSaver)
        assert isinstance(saver, PostgresSaver)
        mock_postgres_saver.setup.assert_called_once()

    def test_checkpoint_saver_default_strategy(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test default strategy."""
        monkeypatch.delenv("CHECKPOINTER", raising=False)

        saver = CheckpointSaver().saver()

        assert saver is not None
        assert isinstance(saver, BaseCheckpointSaver)
        assert isinstance(saver, InMemorySaver)

    def test_checkpoint_saver_invalid_strategy(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test invalid strategy."""
        monkeypatch.setenv("CHECKPOINTER", "invalid_strategy")

        with pytest.raises(
            ValueError,
            match="Unknown saver strategy: invalid_strategy",
        ):
            CheckpointSaver()
