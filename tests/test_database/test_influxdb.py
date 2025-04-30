from unittest.mock import MagicMock
import pytest
from src.database.influxdb import InfluxDB
import pandas as pd


class TestInfluxDB:
    """Test InfluxDB class."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mock_client: MagicMock) -> None:
        """Initialize test method."""
        self.client = mock_client
        self.influxdb = InfluxDB(self.client)

    def test_tables(self) -> None:
        """Test influxdb.tables() method."""
        # Arrange
        mock_df = pd.DataFrame({"table_name": ["table1", "table2"]})
        self.client.query.return_value = mock_df
        # Act
        result = self.influxdb.tables()
        # Assert
        assert result == ["table1", "table2"]
        self.client.query.assert_called_once_with(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'iox';",
            mode="pandas",
        )

    def test_columns(self) -> None:
        """Test influxdb.columns() method."""
        # Arrange
        table_name = "table1"
        mock_df = pd.DataFrame(
            {
                "column_name": ["id", "value"],
                "data_type": ["integer", "float"],
            },
        )
        self.client.query.return_value = mock_df
        # Act
        result = self.influxdb.columns([table_name])
        # Assert
        expected = {
            table_name: [
                {"column_name": "id", "data_type": "integer"},
                {"column_name": "value", "data_type": "float"},
            ],
        }
        assert result == expected
        self.client.query.assert_called_once_with(
            f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}';
                    """,
            mode="pandas",
        )

    def test_columns_raises_exception(self) -> None:
        """Test influxdb.columns() method raises exception when query fails."""
        self.client.query.side_effect = Exception("query error")

        with pytest.raises(
            Exception,
            match="Failed to fetch column info for table1: query error",
        ):
            self.influxdb.columns(["table1"])

    def test_data(self) -> None:
        """Test influxdb.data() method."""
        # Arrange
        mock_df = pd.DataFrame({"id": [1, 2], "value": [10.5, 20.5]})
        mock_query_result = MagicMock()
        mock_query_result.to_pandas.return_value = mock_df
        self.client.query.return_value = mock_query_result
        # Act
        result = self.influxdb.data(["table1"])
        # Assert
        expected = {
            "table1": [
                {"id": 1, "value": 10.5},
                {"id": 2, "value": 20.5},
            ],
        }
        assert result == expected
        self.client.query.assert_called_once_with("SELECT * FROM table1 LIMIT 5")

    def test_data_raises_exception(self) -> None:
        """Test influxdb.data() method raises exception when query fails."""
        self.client.query.side_effect = Exception("query error")

        with pytest.raises(Exception, match="Failed to query table1: query error"):
            self.influxdb.data(["table1"])

    def test_execute_query(self) -> None:
        """Test influxdb.execute_query() method."""
        # Arrange
        expected_result = [{"id": 1, "value": 10}]
        mock_query_result = MagicMock()
        mock_query_result.to_pylist.return_value = expected_result
        self.client.query.return_value = mock_query_result
        # Act
        query = "SELECT * FROM table1"
        result = self.influxdb.execute_query(query)
        # Assert
        assert result == expected_result
        self.client.query.assert_called_once_with(query)
