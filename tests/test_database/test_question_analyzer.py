import pytest
from src.agent.parser import TruthOutput
from src.database.question_analyzer import QuestionAnalyzer
from unittest.mock import MagicMock


class TestQuestionAnalyzer:
    """Test the QuestionAnalyzer class."""

    @pytest.fixture(autouse=True)
    def setup_method(
        self,
        mock_client: MagicMock,
        mock_llm: MagicMock,
        mock_state: MagicMock,
    ) -> None:
        """Initialize test method."""
        self.client = mock_client
        self.client.tables.return_value = ["sensor_1", "sensor_2"]
        self.client.columns.return_value = {
            "sensor_1": [
                {"column_name": "time", "data_type": "datetime"},
                {"column_name": "temperature", "data_type": "float"},
            ],
            "sensor_2": [
                {"column_name": "time", "data_type": "datetime"},
                {"column_name": "humidity", "data_type": "float"},
            ],
        }
        self.llm = mock_llm
        self.state = mock_state
        self.question_analyzer = QuestionAnalyzer(
            question="What is the average temperature?",
            client=self.client,
            llm=self.llm,
            state=self.state,
        )

    def test_extract_db_terms(self) -> None:
        """Test the _extract_db_terms() method."""
        terms = self.question_analyzer._extract_db_terms()
        assert "sensor_1" in terms
        assert "temperature" in terms
        assert "sensor_2" in terms
        assert "humidity" in terms

    def test_contains_db_terms(self) -> None:
        """Test the contains_db_terms() method."""
        # Question contains a database term
        self.question_analyzer.question = (
            "What is the average temperature from the sensor_data?"
        )
        assert self.question_analyzer.contains_db_terms() is True

        # Question does not contain any database terms
        self.question_analyzer.question = "How is the weather today?"
        assert self.question_analyzer.contains_db_terms() is False

    def test_is_follow_up(self) -> None:
        """Test the is_follow_up() method."""
        # Test follow-up question with result in state
        self.question_analyzer.question = "What was the previous query?"
        assert self.question_analyzer.is_follow_up() is True

        # Test not a follow-up question
        self.state["result"] = None
        self.question_analyzer.question = "What is the current temperature?"
        assert self.question_analyzer.is_follow_up() is False

    def test_is_db_question(self) -> None:
        """Test the is_db_question() method."""
        # Simulate successful LLM response
        self.llm.with_structured_output.return_value.with_config.return_value.invoke.return_value = TruthOutput(
            truth=True,
        )
        assert self.question_analyzer.is_db_question() is True

        # Simulate failed LLM response
        self.llm.with_structured_output.return_value.with_config.return_value.invoke.side_effect = Exception(
            "Boom",
        )
        assert self.question_analyzer.is_db_question() is False
