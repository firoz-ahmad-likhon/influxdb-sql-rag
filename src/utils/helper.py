from src.Memory.saver import SaverStrategy
from langgraph.checkpoint.base import BaseCheckpointSaver


class Helper:
    """Common helper functions."""

    @staticmethod
    def checkpointer() -> BaseCheckpointSaver:
        """Return the checkpointer based on the environment variable."""
        return SaverStrategy().get_saver()
