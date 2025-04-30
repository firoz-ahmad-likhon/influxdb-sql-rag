import os
from unittest.mock import patch, MagicMock
from src.utils.config import Config


class TestConfig:
    """Test the Config class."""

    @patch("src.utils.config.load_dotenv")
    def test_load_env_not_loaded(self, mock_load_dotenv: MagicMock) -> None:
        """Test load_env() when LLM_MODEL is not set."""
        if "LLM_MODEL" in os.environ:
            del os.environ["LLM_MODEL"]

        Config.load_env()

        mock_load_dotenv.assert_called_once()

    @patch("src.utils.config.load_dotenv")
    def test_load_env_already_loaded(self, mock_load_dotenv: MagicMock) -> None:
        """Test load_env() when LLM_MODEL is already set."""
        os.environ["LLM_MODEL"] = "test-model"

        Config.load_env()

        mock_load_dotenv.assert_not_called()

        del os.environ["LLM_MODEL"]
