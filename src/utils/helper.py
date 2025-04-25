from src.memory.checkpoint import CheckpointSaver
from langgraph.checkpoint.base import BaseCheckpointSaver


class Helper:
    """Common helper functions."""

    @staticmethod
    def checkpoint() -> BaseCheckpointSaver:
        """Return the checkpointer based on the environment variable."""
        return CheckpointSaver().saver()

    @staticmethod
    def find_similar_item(
        target: str,
        candidates: list[str],
        threshold: float = 0.5,
    ) -> str | None:
        """Find the most similar item from a list of candidates."""
        if not target or not candidates:
            return None

        best_match = None
        best_score = 0

        for candidate in candidates:
            # Count matching characters
            score = sum(
                c1 == c2
                for c1, c2 in zip(target.lower(), candidate.lower(), strict=True)
            )
            if score > best_score:
                best_score = score
                best_match = candidate

        # Only suggest if somewhat similar
        if best_score >= len(target) * threshold:
            return best_match
        return None
