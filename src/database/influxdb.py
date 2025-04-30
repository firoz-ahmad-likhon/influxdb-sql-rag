from typing import Any, cast
from influxdb_client_3 import InfluxDBClient3


class InfluxDB:
    """InfluxDB helper class."""

    def __init__(self, client: InfluxDBClient3):
        """Initialize the InfluxDB helper class."""
        self.client = client

    def tables(self) -> list[str]:
        """List all tables in the database."""
        return cast(
            list[str],
            self.client.query(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'iox';",
                mode="pandas",
            )["table_name"].tolist(),
        )

    def columns(self, tables: list[str]) -> dict[str, list[dict[str, str]]]:
        """Return all columns and their data types for the given tables."""
        schema_info = {}
        for table in tables:
            try:
                df = self.client.query(
                    f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table}';
                    """,
                    mode="pandas",
                )
                schema_info[table] = df.to_dict(orient="records")
            except Exception as e:
                raise Exception(
                    f"Failed to fetch column info for {table}: {e}",
                ) from e

        return schema_info

    def data(self, tables: list[str]) -> dict[str, list[dict[str, Any]]]:
        """Return the first 5 rows from each table as JSON."""
        table_data = {}
        for table in tables:
            try:
                df = self.client.query(f"SELECT * FROM {table} LIMIT 5").to_pandas()
                # Convert DataFrame to a dictionary (list of dictionaries for each row)
                table_data[table] = df.to_dict(orient="records")
            except Exception as e:
                raise Exception(
                    f"Failed to query {table}: {e}",
                ) from e

        return table_data

    def execute_query(self, query: str) -> list[Any]:
        """Execute the SQL query using InfluxDB client."""
        return cast(list[Any], self.client.query(query).to_pylist())
