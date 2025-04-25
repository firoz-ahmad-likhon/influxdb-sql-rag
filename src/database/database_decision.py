from langchain_ollama import ChatOllama
from src.database.influxdb import InfluxDB
from src.database.question_analyzer import QuestionAnalyzer
from src.agent.state import State


class Decisive(QuestionAnalyzer):
    """Database decision service for analyzing questions and queries."""

    def __init__(
        self,
        question: str,
        client: InfluxDB,
        llm: ChatOllama,
        state: State,
    ) -> None:
        """Initialize the decision service."""
        super().__init__(question=question, client=client, llm=llm, state=state)

    def database_usability(self) -> bool:
        """Determine if the question is related to database content."""
        # First, try simple heuristics
        if self.contains_db_terms():
            return True

        # Second, identify if the question is a follow-up
        if self.is_follow_up():
            return True

        # Finally, if no direct match, use LLM as a fallback
        return self.is_db_question()

    def validate_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        return table_name in self.tables
