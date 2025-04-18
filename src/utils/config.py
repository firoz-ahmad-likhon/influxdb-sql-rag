import os
from dotenv import load_dotenv


class Config:
    """Various configurations for the project."""

    @staticmethod
    def load_env() -> None:
        """Load environment variables.

        Load only if not already loaded (e.g., LangGraph Studio, Docker container, etc.)
        """
        if not os.getenv("LLM_MODEL"):
            load_dotenv()
