import re
from langchain_core.prompts import ChatPromptTemplate
from src.agent.prompt import Prompt
from influxdb_client_3 import InfluxDBClient3
from langchain_ollama import ChatOllama
from src.utils.influxdb import InfluxDB


class Decisive:
    """Database related class for making decisions."""

    def __init__(self, client: InfluxDBClient3, llm: ChatOllama) -> None:
        """Initialize the class."""
        self.client = client
        self.llm = llm
        self.initialize()

    def initialize(self) -> None:
        """Initialize the table and column information."""
        self.tables = InfluxDB.tables(self.client)
        self.columns = InfluxDB.columns(self.client, self.tables)

    def database_usability(self, question: str) -> bool:
        """Determine if the question is related to database content."""
        # Check for common time series metrics or keywords in the question
        time_series_keywords = [
            "temperature",
            "humidity",
            "pressure",
            "sensor",
            "reading",
            "average",
            "measurement",
            "data point",
            "time series",
            "metric",
            "statistics",
            "min",
            "max",
            "mean",
            "median",
            "trend",
            "record",
            "log",
            "monitor",
        ]

        # Get database-specific terms (tables and columns)
        db_specific_terms = list(self.tables) + [
            col["column_name"]
            for table_cols in self.columns.values()
            for col in table_cols
        ]

        # Check if any database term or time series keyword is in the question
        question_lower = question.lower()

        # First check if this is a follow-up question about previous results
        followup_indicators = [
            "show me",
            "give me",
            "display",
            "the result",
            "that data",
            "previous result",
            "same data",
            "in tabular",
            "table format",
            "you already have",
            "what you found",
            "the records",
            "previous query",
            "those rows",
            "the data again",
            "full results",
            "show all",
            "raw data",
            "original data",
            "complete data",
            "the same",
        ]

        # If it's likely a follow-up, treat it as database-related
        for indicator in followup_indicators:
            if indicator in question_lower:
                return True

        for term in db_specific_terms:
            if term.lower() in question_lower:
                return True

        for keyword in time_series_keywords:
            if keyword.lower() in question_lower:
                return True

        # If no direct match, use LLM as a fallback with improved prompt
        prompt_template = ChatPromptTemplate(
            [
                ("system", "{instruction}"),
                ("human", "Question: {question}"),
                (
                    "human",
                    "Should this question be answered using a database query or is it referring to previous query results? Answer only TRUE or FALSE.",
                ),
            ],
        )

        prompt = prompt_template.with_config(
            run_name="Database Usability Prompt",
        ).invoke(
            {
                "instruction": Prompt.database_usability().format(columns=self.columns),
                "question": question,
            },
        )

        try:
            response = self.llm.with_config(run_name="Database Usability").invoke(
                prompt,
            )
            return "TRUE" in response.content.upper()
        except Exception:
            return False

    def validate_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        return table_name in self.tables

    @staticmethod
    def extract_table_name(query: str) -> str | None:
        """Extract the table name from a SQL query.

        This is a simple implementation and might need improvement for complex queries.
        """
        query = query.lower()
        if "from" not in query:
            return None

        # Get the part after FROM
        from_part = query.split("from")[1].strip()
        # Get the first word after FROM, which should be the table name
        table_name = from_part.split()[0].strip(";").strip()

        # Remove any quotes or backticks
        table_name = re.sub(r'[`"\']', "", table_name)

        return table_name

    def suggest_similar_table(self, table_name: str | None) -> str | None:
        """Suggest a similar table name if available."""
        if not table_name:
            return None

        # Simple string similarity - could be improved
        best_match = None
        best_score = 0

        for t in self.tables:
            # Count matching characters
            score = sum(
                c1 == c2 for c1, c2 in zip(table_name.lower(), t.lower(), strict=True)
            )
            if score > best_score:
                best_score = score
                best_match = t

        # Only suggest if somewhat similar
        if best_score >= len(table_name) / 2:
            return best_match
        return None
