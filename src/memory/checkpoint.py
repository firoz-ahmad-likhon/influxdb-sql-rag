import os
from abc import ABC, abstractmethod
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from psycopg_pool import ConnectionPool


class CheckpointStrategyInterface(ABC):
    """Interface for checkpoint strategies."""

    @abstractmethod
    def saver(self) -> None:
        """Get the checkpointer."""
        pass


class InMemoryCheckpoint(CheckpointStrategyInterface):
    """Memory saver strategy."""

    def saver(self) -> InMemorySaver:
        """Get the memory checkpointer."""
        return InMemorySaver()


class PostgresCheckpoint(CheckpointStrategyInterface):
    """Postgres saver strategy."""

    def saver(self) -> PostgresSaver:
        """Get the postgres checkpointer."""
        pool = ConnectionPool(
            conninfo=os.getenv("POSTGRES_URI"),
            max_size=20,
            open=True,
            kwargs={"autocommit": True, "prepare_threshold": 0},
        )
        saver = PostgresSaver(pool)
        saver.setup()
        return saver


STRATEGIES = {
    "memory": InMemoryCheckpoint,
    "postgres": PostgresCheckpoint,
}


class CheckpointSaver:
    """Saver strategy."""

    def __init__(self) -> None:
        """Initialize the saver strategy."""
        strategy = os.getenv("CHECKPOINTER", "memory")
        if strategy not in STRATEGIES:
            raise ValueError(f"Unknown saver strategy: {strategy}")
        self._impl = STRATEGIES[strategy]()  # Initialize the actual strategy

    def saver(self) -> BaseCheckpointSaver:
        """Get the checkpoint saver."""
        return self._impl.saver()
