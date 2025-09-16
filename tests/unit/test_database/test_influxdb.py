import pytest
from pytest_mock import MockerFixture
from src.database.influxdb import InfluxDB
from influxdb_client_3 import InfluxDBClient3
import pandas as pd


class TestInfluxDB:
    """Test InfluxDB class."""

    @pytest.fixture(autouse=True)
    def setup_method(self, mocker: MockerFixture) -> None:
        """Initialize test method."""
        self.client = mocker.MagicMock(spec=InfluxDBClient3)
        self.influxdb = InfluxDB(self.client)

    def test_tables(self) -> None:
        """Test influxdb.tables() method."""
        mock_df = pd.DataFrame({"table_name": ["table1", "table2"]})
        self.client.query.return_value = mock_df

        result = self.influxdb.tables()

        assert result == ["table1", "table2"]
        self.client.query.assert_called_once_with(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'iox';",
            mode="pandas",
        )

    def test_columns(self) -> None:
        """Test influxdb.columns() method."""
        table_name = "table1"
        mock_df = pd.DataFrame(
            {
                "column_name": ["id", "value"],
                "data_type": ["integer", "float"],
            },
        )
        self.client.query.return_value = mock_df

        result = self.influxdb.columns([table_name])

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

    def test_columns_raises_exception(self, mocker: MockerFixture) -> None:
        """Test influxdb.columns() method raises exception when query fails."""
        mocker.patch.object(self.client, "query", side_effect=Exception("query error"))

        with pytest.raises(
            Exception,
            match="Failed to fetch column info for table1: query error",
        ):
            self.influxdb.columns(["table1"])

    def test_data(self, mocker: MockerFixture) -> None:
        """Test influxdb.data() method."""
        mock_df = pd.DataFrame({"id": [1, 2], "value": [10.5, 20.5]})
        mock_query_result = mocker.MagicMock()
        mock_query_result.to_pandas.return_value = mock_df
        self.client.query.return_value = mock_query_result

        result = self.influxdb.data(["table1"])

        expected = {
            "table1": [
                {"id": 1, "value": 10.5},
                {"id": 2, "value": 20.5},
            ],
        }
        assert result == expected
        self.client.query.assert_called_once_with("SELECT * FROM table1 LIMIT 5")

    def test_data_raises_exception(self, mocker: MockerFixture) -> None:
        """Test influxdb.data() method raises exception when query fails."""
        mocker.patch.object(self.client, "query", side_effect=Exception("query error"))

        with pytest.raises(Exception, match="Failed to query table1: query error"):
            self.influxdb.data(["table1"])

    def test_execute_query(self, mocker: MockerFixture) -> None:
        """Test influxdb.execute_query() method."""
        expected_result = [{"id": 1, "value": 10}]
        mock_query_result = mocker.MagicMock()
        mock_query_result.to_pylist.return_value = expected_result
        self.client.query.return_value = mock_query_result

        query = "SELECT * FROM table1"
        result = self.influxdb.execute_query(query)

        assert result == expected_result
        self.client.query.assert_called_once_with(query)
