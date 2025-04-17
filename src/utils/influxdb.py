from typing import Any, cast
from influxdb_client_3 import InfluxDBClient3


class InfluxDB:
    """InfluxDB helper class."""

    @staticmethod
    def tables(client: InfluxDBClient3) -> list[str]:
        """List all tables in the database."""
        return cast(
            list[str],
            client.query(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'iox';",
                mode="pandas",
            )["table_name"].tolist(),
        )

    @staticmethod
    def columns(
        client: InfluxDBClient3,
        tables: list[str],
    ) -> dict[str, list[dict[str, str]]]:
        """Return all columns and their data types for the given tables."""
        schema_info = {}
        for table in tables:
            try:
                result = client.query(
                    f"""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = '{table}';
                    """,
                    mode="pandas",
                )
                df = result
                schema_info[table] = df.to_dict(orient="records")
            except Exception as e:
                raise Exception(
                    f"Failed to fetch column info for {table}: {e}",
                ) from e

        return schema_info

    @staticmethod
    def data(client: InfluxDBClient3, tables: list[str]) -> dict[str, dict[Any, Any]]:
        """Return the first 5 rows from each table as JSON."""
        table_data = {}
        for table in tables:
            try:
                result = client.query(f"SELECT * FROM {table} LIMIT 5")
                df = result.to_pandas()
                # Convert DataFrame to a dictionary (list of dictionaries for each row)
                table_data[table] = df.to_dict(orient="records")
            except Exception as e:
                raise Exception(
                    f"Failed to query {table}: {e}",
                ) from e

        return table_data

    @staticmethod
    def execute_query(client: InfluxDBClient3, query: str) -> list[Any]:
        """Execute the SQL query using InfluxDB client."""
        return cast(list[Any], client.query(query).to_pylist())
