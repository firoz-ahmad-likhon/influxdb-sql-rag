from sqlglot import parse_one, exp


class QueryParser:
    """Parse SQL queries."""

    def __init__(self, query: str):
        """Initialize the QueryParser object."""
        self.query = query

    def extract_table_names(self) -> list[str]:
        """Extract the table name from a SQL query."""
        try:
            expression = parse_one(self.query)

            # Get names of Common Table Expressions (CTEs) to exclude them
            cte_names = {cte.alias_or_name for cte in expression.find_all(exp.CTE)}

            tables = {
                table.name
                for table in expression.find_all(exp.Table)
                if table.name not in cte_names
            }

            return list(tables)
        except Exception:
            return []
