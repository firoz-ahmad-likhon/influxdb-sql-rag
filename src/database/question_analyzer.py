from langchain_core.prompts import ChatPromptTemplate
from src.agent.parser import TruthOutput
from src.agent.prompt import Prompt
from src.agent.state import State
from src.database.influxdb import InfluxDB
from langchain_ollama import ChatOllama


class QuestionAnalyzer:
    """Analyze the user questions."""

    def __init__(self, question: str, client: InfluxDB, llm: ChatOllama, state: State):
        """Initialize with database schema information."""
        self.client = client
        self.llm = llm
        self.state = state
        self.question = question.lower()

        self.tables = self.client.tables()
        self.columns = self.client.columns(self.tables)
        self.data = self.client.data(self.tables)

    def _extract_db_terms(self) -> list[str]:
        """Extract all database terms for keyword matching."""
        terms = list(self.tables)
        for table_cols in self.columns.values():
            for col in table_cols:
                terms.append(col["column_name"])
        return terms

    def contains_db_terms(self) -> bool:
        """Check if question contains any database terms."""
        return any(term.lower() in self.question for term in self._extract_db_terms())

    def is_follow_up(self) -> bool:
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

        has_indicator = any(
            indicator in self.question for indicator in followup_indicators
        )
        has_result = self.state.get("result", None) is not None

        return has_indicator and has_result

    def is_db_question(self) -> bool:
        """Determine if a question should be answered using database queries."""
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
                    state_result=self.state.get("result"),
                ),
                "question": self.question,
            },
        )

        try:
            response = (
                self.llm.with_structured_output(schema=TruthOutput)
                .with_config(run_name="Database Usability")
                .invoke(prompt)
            )
            return response.truth is True
        except Exception:
            return False
