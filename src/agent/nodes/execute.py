from src.utils.influxdb import InfluxDB
from src.utils.database_decision import Decisive
from src.agent.state import State
from influxdb_client_3 import InfluxDBClient3


class Execute:
    """Execute the SQL query using InfluxDB client."""

    def __init__(self, client: InfluxDBClient3, decision: Decisive):
        """Initialize the Execute class."""
        self.client = client
        self.decision = decision

    def __call__(self, state: State) -> State:
        """Call the Execute class."""
        try:
            result = InfluxDB.execute_query(self.client, state["query"])
            return {"result": result, "error": None}
        except Exception as e:
            error_msg = str(e)
            if "table" in error_msg.lower() and "not found" in error_msg.lower():
                suggested_table = self.decision.suggest_similar_table(
                    self.decision.extract_table_name(state["query"]),
                )
                if suggested_table:
                    error_msg += f" Did you mean '{suggested_table}'?"

            return {"result": None, "error": error_msg}
