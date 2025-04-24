from src.memory.checkpoint import CheckpointSaver
from langgraph.checkpoint.base import BaseCheckpointSaver


class Helper:
    """Common helper functions."""

    @staticmethod
    def checkpoint() -> BaseCheckpointSaver:
        """Return the checkpointer based on the environment variable."""
        return CheckpointSaver().saver()
