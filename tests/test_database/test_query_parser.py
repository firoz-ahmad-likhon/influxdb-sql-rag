import pytest
from src.database.query_parser import QueryParser


class TestQueryParser:
    """Test QueryParser class."""

    @pytest.mark.parametrize(
        ("query", "expected_table"),
        [
            ("SELECT * FROM my_table;", "my_table"),
            ("select id, name from users;", "users"),
            ("SELECT COUNT(*) FROM orders WHERE id > 10;", "orders"),
            ("SELECT * FROM `quoted_table`;", "quoted_table"),
            ('SELECT * FROM "double_quoted";', "double_quoted"),
            ("SELECT * FROM 'single_quoted';", "single_quoted"),
            ("SELECT * FROM complex.table;", "complex.table"),
        ],
    )
    def test_extract_table_name_valid_queries(
        self,
        query: str,
        expected_table: str,
    ) -> None:
        """Test extract_table_name() method with valid queries."""
        parser = QueryParser(query)
        assert parser.extract_table_name() == expected_table

    @pytest.mark.parametrize(
        "query",
        [
            "SELECT 1;",
            "SELECT NOW()",
            "UPDATE table SET col = 1;",
            "",
        ],
    )
    def test_extract_table_name_invalid_queries(self, query: str) -> None:
        """Test extract_table_name() method with invalid queries."""
        parser = QueryParser(query)
        assert parser.extract_table_name() is None
