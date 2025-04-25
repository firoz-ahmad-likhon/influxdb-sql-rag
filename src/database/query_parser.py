import re


class QueryParser:
    """Parse SQL queries."""

    def __init__(self, query: str):
        """Initialize the QueryParser object."""
        self.query = query.lower()

    def extract_table_name(self) -> str | None:
        """Extract the table name from a SQL query.

        This is a simple implementation and might need improvement for complex queries.
        """
        if "from" not in self.query:
            return None

        # Get the part after FROM
        from_part = self.query.split("from")[1].strip()
        # Get the first word after FROM, which should be the table name
        table_name = from_part.split()[0].strip(";").strip()

        # Remove any quotes or backticks
        table_name = re.sub(r'[`"\']', "", table_name)

        return table_name
