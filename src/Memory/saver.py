import os
from abc import ABC, abstractmethod
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from psycopg_pool import ConnectionPool
from src.utils.config import Config

Config.load_env()  # Load environment variables


class SaverStrategyInterface(ABC):
    """Interface for saver strategies."""

    @abstractmethod
    def get_saver(self) -> None:
        """Get the checkpointer."""
        pass


class MemorySaverStrategy(SaverStrategyInterface):
    """Memory saver strategy."""

    def get_saver(self) -> MemorySaver:
        """Get the memory checkpointer."""
        return MemorySaver()


class PostgresSaverStrategy(SaverStrategyInterface):
    """Postgres saver strategy."""

    def get_saver(self) -> PostgresSaver:
        """Get the postgres checkpointer."""
        pool = ConnectionPool(
            conninfo=os.getenv("POSTGRES_URI"),
            max_size=20,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        )
        saver = PostgresSaver(pool)
        saver.setup()
        return saver


STRATEGIES = {
    "memory": MemorySaverStrategy,
    "postgres": PostgresSaverStrategy,
}


class SaverStrategy:
    """Saver strategy."""

    def __init__(self) -> None:
        """Initialize the saver strategy."""
        strategy = os.getenv("CHECKPOINTER", "memory")
        if strategy not in STRATEGIES:
            raise ValueError(f"Unknown saver strategy: {strategy}")
        self._impl = STRATEGIES[strategy]()  # Initialize the actual strategy

    def get_saver(self) -> BaseCheckpointSaver:
        """Get the checkpoint saver."""
        return self._impl.get_saver()
