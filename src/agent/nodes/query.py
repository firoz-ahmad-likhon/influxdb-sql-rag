from typing import cast, Any
from src.utils.database_decision import Decisive
from src.agent.state import State
from src.agent.few_shot import InfluxDBFewShot
from langchain_ollama import ChatOllama
from src.agent.prompt import Prompt
from src.agent.parser import QueryOutput
from langchain_core.prompts import ChatPromptTemplate


class Quarify:
    """Generate SQL query from user input question or handle follow-up questions."""

    def __init__(
        self,
        llm: ChatOllama,
        decision: Decisive,
        tables: list[str],
        columns: dict[str, list[dict[str, str]]],
        data: dict[str, dict[Any, Any]],
    ) -> None:
        """Initialize the class."""
        self.llm = llm
        self.decision = decision
        self.tables = tables
        self.columns = columns
        self.data = data

    def __call__(self, state: State) -> State:
        """Call the class."""
        question = state["question"]

        if not self.decision.database_usability(question, state):
            return {"question": question, "use_chat": True}

        if Decisive.follow_up(question, state):
            return {
                **state,
                "question": question,
                "use_chat": False,
                "is_followup": True,
            }

        prompt_template = ChatPromptTemplate(
            [
                ("system", "{instruction}"),
                InfluxDBFewShot.sql_generation_train(),
                ("human", "Question: {question}"),
            ],
        )

        prompt = prompt_template.invoke(
            {
                "instruction": Prompt.sql_query_generation().format(
                    top_k=10,
                    table_info=self.tables,
                    column_info=self.columns,
                    sample_data=self.data,
                    error_list="",
                ),
                "question": question,
            },
        )

        try:
            response = (
                self.llm.with_structured_output(schema=QueryOutput)
                .with_config(run_name="Query Generation")
                .invoke(
                    prompt,
                )
            )
            query_output = cast(dict[str, Any], response.model_dump())
            table_name = self.decision.extract_table_name(query_output["query"])

            if table_name and not self.decision.validate_table_exists(table_name):
                error_msg = f"Table '{table_name}' does not exist."
                suggested_table = self.decision.suggest_similar_table(
                    self.decision.extract_table_name(state["query"]),
                )
                if suggested_table:
                    error_msg += f" Did you mean '{suggested_table}'?"
                return {
                    "question": question,
                    "use_chat": True,
                    "error": error_msg,
                }

            return {
                **cast(State, query_output),
                "use_chat": False,
                "is_followup": False,
            }
        except Exception as e:
            return {
                "question": question,
                "use_chat": False,
                "is_followup": False,
                "error": str(e),
            }
