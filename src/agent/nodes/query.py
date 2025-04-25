from typing import cast, Any
from src.database.database_decision import Decisive
from src.agent.state import State
from src.agent.few_shot import InfluxDBFewShot
from langchain_ollama import ChatOllama
from src.agent.prompt import Prompt
from src.agent.parser import QueryOutput
from langchain_core.prompts import ChatPromptTemplate
from src.database.influxdb import InfluxDB
from src.database.query_parser import QueryParser
from src.utils.helper import Helper


class Quarify:
    """Generate SQL query from user input question or handle follow-up questions."""

    def __init__(
        self,
        client: InfluxDB,
        llm: ChatOllama,
    ) -> None:
        """Initialize the class."""
        self.client = client
        self.llm = llm

    def __call__(self, state: State) -> State:
        """Call the class."""
        question = state["question"]

        decision = Decisive(question, self.client, self.llm, state)

        if not decision.database_usability():
            return {"question": question, "type": "chat"}

        if decision.is_follow_up():
            return {
                "question": question,
                "type": "follow-up",
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
                    table_info=decision.tables,
                    column_info=decision.columns,
                    sample_data=decision.data,
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
            query_parser = QueryParser(query_output["query"])
            table_name = query_parser.extract_table_name()

            if table_name and not decision.validate_table_exists(table_name):
                error_msg = f"Table '{table_name}' does not exist."
                suggested_table = Helper.find_similar_item(table_name, decision.tables)

                if suggested_table:
                    error_msg += f" Did you mean '{suggested_table}'?"
                return {
                    "question": question,
                    "type": "chat",
                    "error": error_msg,
                }

            return cast(
                State,
                {
                    **query_output,
                    "type": "query",
                },
            )
        except Exception as e:
            return {
                "question": question,
                "type": "query",
                "error": str(e),
            }
