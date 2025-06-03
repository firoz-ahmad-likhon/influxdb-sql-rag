import json
import pytest
from unittest.mock import mock_open, patch, MagicMock
from src.utils.data_provider import DataProvider


class TestDataProvider:
    """Test DataProvider class."""

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        """Initialize test method."""
        self.mock_catalog_data = {"items": ["item1", "item2"]}
        self.mock_glossary_data = {"terms": ["term1", "term2"]}
        self.mock_env_path = "test/resources/data"

    @patch("src.utils.data_provider.os.getenv")
    @patch("src.utils.data_provider.Path.open")
    def test_catalog(self, mock_open_func: MagicMock, mock_getenv: MagicMock) -> None:
        """Test catalog method."""
        mock_getenv.return_value = self.mock_env_path
        mock_file = mock_open(read_data=json.dumps(self.mock_catalog_data))
        mock_open_func.side_effect = mock_file

        result = DataProvider.catalog()
        assert result == self.mock_catalog_data

    @patch("src.utils.data_provider.os.getenv")
    @patch("src.utils.data_provider.Path.open")
    def test_glossary(self, mock_open_func: MagicMock, mock_getenv: MagicMock) -> None:
        """Test glossary method."""
        mock_getenv.return_value = self.mock_env_path
        mock_file = mock_open(read_data=json.dumps(self.mock_glossary_data))
        mock_open_func.side_effect = mock_file

        result = DataProvider.glossary()
        assert result == self.mock_glossary_data
