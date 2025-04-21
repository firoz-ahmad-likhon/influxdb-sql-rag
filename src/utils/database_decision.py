import re
from langchain_core.prompts import ChatPromptTemplate
from src.agent.parser import TruthOutput
from src.agent.prompt import Prompt
from influxdb_client_3 import InfluxDBClient3
from langchain_ollama import ChatOllama
from src.utils.influxdb import InfluxDB
from src.agent.state import State


class Decisive:
    """Database related class for making decisions by analyzing the question."""

    def __init__(self, client: InfluxDBClient3, llm: ChatOllama) -> None:
        """Initialize the class."""
        self.client = client
        self.llm = llm
        self.initialize()

    def initialize(self) -> None:
        """Initialize the table and column information."""
        self.tables = InfluxDB.tables(self.client)
        self.columns = InfluxDB.columns(self.client, self.tables)

    def database_usability(self, question: str, state: State) -> bool:
        """Determine if the question is related to database content."""
        if self.exist_in_db(question):
            return True
        if Decisive.follow_up(question, state):
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
                "instruction": Prompt.database_usability().format(
                    columns=self.columns,
                    state_result=state.get("result", None),
                ),
                "question": question,
            },
        )

        try:
            response = (
                self.llm.with_structured_output(schema=TruthOutput)
                .with_config(run_name="Database Usability")
                .invoke(
                    prompt,
                )
            )
            return response.query is True
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

    @staticmethod
    def follow_up(question: str, state: State) -> bool:
        """Check if this is a follow-up question about previous results."""
        followup_indicators = [
            "previous data",
            "previous result",
            "previous query",
            "previous question",
            "already have",
            "what you found",
            "prior data",
            "prior result",
            "prior query",
            "prior question",
        ]

        question_lower = question.lower()
        for indicator in followup_indicators:
            if indicator in question_lower and state.get("result", None):
                return True

        return False

    def exist_in_db(self, question: str) -> bool:
        """Check any keyword match with database schema."""
        db_specific_terms = list(self.tables) + [
            col["column_name"]
            for table_cols in self.columns.values()
            for col in table_cols
        ]

        question_lower = question.lower()

        for term in db_specific_terms:
            if term.lower() in question_lower:
                return True

        return False
