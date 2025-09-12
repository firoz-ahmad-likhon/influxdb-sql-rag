import json
import pytest
from pathlib import Path
from pytest_mock import MockerFixture
from src.utils.data_provider import DataProvider


class TestDataProvider:
    """Test DataProvider class."""

    @pytest.fixture(autouse=True)
    def setup(self, monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture) -> None:
        """Initialize test setup."""
        self.mock_catalog_data = {"items": ["item1", "item2"]}
        self.mock_glossary_data = {"terms": ["term1", "term2"]}
        self.mock_base_path = Path("test/resources/data")

        # Set BASE_PATH once for all tests
        monkeypatch.setattr(
            "src.utils.data_provider.DataProvider.BASE_PATH",
            self.mock_base_path,
        )

        # Store mocker for use in individual tests
        self.mocker = mocker

    def test_catalog(self) -> None:
        """Test catalog method."""
        # Mock Path.open for catalog.json
        mock_file = self.mocker.mock_open(read_data=json.dumps(self.mock_catalog_data))
        self.mocker.patch("src.utils.data_provider.Path.open", mock_file)

        result = DataProvider.catalog()
        assert result == self.mock_catalog_data

        # Verify the correct file was opened
        mock_file.assert_called_once_with("r", encoding="utf-8")

    def test_glossary(self) -> None:
        """Test glossary method."""
        # Mock Path.open for glossary.json
        mock_file = self.mocker.mock_open(read_data=json.dumps(self.mock_glossary_data))
        self.mocker.patch("src.utils.data_provider.Path.open", mock_file)

        result = DataProvider.glossary()
        assert result == self.mock_glossary_data

        # Verify the correct file was opened
        mock_file.assert_called_once_with("r", encoding="utf-8")
