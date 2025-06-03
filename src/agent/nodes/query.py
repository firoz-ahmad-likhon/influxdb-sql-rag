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
from src.utils.data_provider import DataProvider


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
                "instruction": Prompt.sql_query_generation_using_catalog().format(
                    top_k=10,
                    catalog=DataProvider.catalog(),
                    glossary=DataProvider.glossary(),
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
            table_names = query_parser.extract_table_names()

            missing_tables = [
                name for name in table_names if not decision.validate_table_exists(name)
            ]

            if missing_tables:
                error_msg = f"Table(s) {', '.join(missing_tables)} do not exist."

                suggestions = [
                    Helper.find_similar_item(name, decision.tables)
                    for name in missing_tables
                ]

                suggestions = [s for s in suggestions if s]  # Exclude None

                if suggestions:
                    suggestion_text = ", ".join(f"'{s}'" for s in suggestions)
                    error_msg += f" Did you mean {suggestion_text}?"

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
