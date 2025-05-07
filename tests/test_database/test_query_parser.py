import pytest
from src.database.query_parser import QueryParser


class TestQueryParser:
    """Test QueryParser class."""

    @pytest.mark.parametrize(
        ("query", "expected_tables"),
        [
            ("select id, name from users;", ["users"]),
            ("SELECT COUNT(*) FROM orders WHERE id > 10;", ["orders"]),
            ('SELECT * FROM "double_quoted";', ["double_quoted"]),
            ("SELECT * FROM 'single_quoted';", ["single_quoted"]),
            ("SELECT * FROM complex.table;", ["table"]),
            (
                "SELECT u.id, o.amount FROM users u JOIN orders o ON u.id = o.user_id;",
                ["users", "orders"],
            ),
            (
                "SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);",
                ["customers", "orders"],
            ),
            (
                "WITH recent_orders AS (SELECT * FROM orders) SELECT * FROM recent_orders ro JOIN users u ON ro.user_id = u.id;",
                ["orders", "users"],
            ),
            (
                "SELECT * FROM (SELECT * FROM sales) s JOIN employees e ON s.emp_id = e.id;",
                ["sales", "employees"],
            ),
            (
                "SELECT * FROM analytics.sales_data sd JOIN finance.budget b ON sd.year = b.year;",
                ["sales_data", "budget"],
            ),
            (
                """
                SELECT * FROM (
                    SELECT * FROM (
                        SELECT * FROM nested_table
                    ) AS inner_alias
                ) AS outer_alias;
                """,
                ["nested_table"],
            ),
        ],
    )
    def test_extract_table_names_valid_queries(
        self,
        query: str,
        expected_tables: list[str],
    ) -> None:
        """Test extract_table_names() method with valid queries, including aliases."""
        parser = QueryParser(query)
        actual_tables = sorted(parser.extract_table_names())
        assert actual_tables == sorted(expected_tables)

    @pytest.mark.parametrize(
        "query",
        [
            "SELECT 1;",
            "SELECT NOW()",
        ],
    )
    def test_extract_table_names_invalid_queries(self, query: str) -> None:
        """Test extract_table_names() method with queries without table references."""
        parser = QueryParser(query)
        assert parser.extract_table_names() == []
