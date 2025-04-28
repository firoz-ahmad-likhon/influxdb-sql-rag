from src.database.influxdb import InfluxDB
from src.agent.state import State


class Execute:
    """Execute the SQL query using InfluxDB client."""

    def __init__(self, client: InfluxDB):
        """Initialize the Execute class."""
        self.client = client

    def __call__(self, state: State) -> State:
        """Call the Execute class."""
        try:
            result = InfluxDB.execute_query(self.client, state["query"])
            return {"result": result, "error": None}
        except Exception as e:
            return {"result": None, "error": str(e)}
