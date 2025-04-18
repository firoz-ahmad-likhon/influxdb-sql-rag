from typing import cast, Any
from src.utils.influxdb import InfluxDB
from src.utils.database_decision import Decisive
from src.utils.config import Config
from src.agent.state import State
from src.agent.few_shot import InfluxDBFewShot
from influxdb_client_3 import InfluxDBClient3
from langchain_ollama import ChatOllama
from langgraph.graph.state import CompiledStateGraph
from src.agent.prompt import Prompt
from src.agent.parser import QueryOutput, AnswerOutput
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, END, StateGraph
import os

Config.load_env()

llm = ChatOllama(
    model=os.getenv("LLM_MODEL"),
    temperature=0,
    base_url=os.getenv("OLLAMA_URL"),
)  # Initialize the model

# Initialize the client
client = InfluxDBClient3(
    token=os.getenv("INFLUXDB_TOKEN"),
    host=os.getenv("INFLUXDB_HOST"),
    org=os.getenv("INFLUXDB_ORG"),
    database=os.getenv("INFLUXDB_DB"),
)

decision = Decisive(client, llm)  # Initialize the database utility object

# Get the tables, columns, and data from InfluxDB
tables = InfluxDB.tables(client)
columns = InfluxDB.columns(client, tables)
data = InfluxDB.data(client, tables)


def quarify(state: State) -> State:
    """Generate SQL query from user input question or handle follow-up questions."""
    question = state["question"]

    # First check if this is a database-related question
    if not decision.database_usability(question):
        return {"question": question, "use_chat": True}

    # Check if this is a follow-up question about previous results
    # We need to look for indicators in the question text since we don't have global state
    question_lower = question.lower()
    followup_indicators = [
        "give me the result",
        "show the data",
        "display the table",
        "show me what you have",
        "show it in table",
        "in tabular format",
        "tabular form",
        "you already have",
        "previous result",
        "the same data",
    ]

    is_followup = any(indicator in question_lower for indicator in followup_indicators)

    # If this is a follow-up, and we have previous results in the state
    if is_followup and state.get("result") is not None:
        # Keep the existing query and result, just update for formatting
        return {
            **state,
            "question": question,
            "use_chat": False,
            "is_followup": True,  # Mark as follow-up to skip query execution
        }

    # For new database questions, generate a query
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
                table_info=tables,
                column_info=columns,
                sample_data=data,
                error_list="",
            ),
            "question": question,
        },
    )

    try:
        response = llm.with_structured_output(schema=QueryOutput).invoke(prompt)
        query_output = cast(dict[str, Any], response.model_dump())

        # Extract table name from query for validation
        table_name = Decisive.extract_table_name(query_output["query"])
        if table_name and not decision.validate_table_exists(table_name):
            return {
                "question": question,
                "use_chat": True,
                "error": f"Table '{table_name}' does not exist",
            }

        return {**cast(State, query_output), "use_chat": False}
    except Exception as e:
        return {"question": question, "use_chat": True, "error": str(e)}


def execute(state: State) -> State:
    """Execute the SQL query using InfluxDB client."""
    # If we're using chat instead of database, skip execution
    if state.get("use_chat", False):
        return state

    # If this is a follow-up question and we already have results, skip execution
    if state.get("is_followup", False) and state.get("result") is not None:
        return state

    try:
        result = InfluxDB.execute_query(client, state["query"])
        return {**state, "result": result, "error": None}
    except Exception as e:
        error_msg = str(e)

        # If there's a table reference error, try to extract the correct table name
        if "table" in error_msg.lower() and "not found" in error_msg.lower():
            # Try to suggest a similar table
            suggested_table = decision.suggest_similar_table(
                Decisive.extract_table_name(state["query"]),
            )
            if suggested_table:
                error_msg += f" Did you mean '{suggested_table}'?"

        return {**state, "result": None, "error": error_msg}


def normal_chat(state: State) -> State:
    """Handle non-database related questions with a normal chat response."""
    prompt_template = ChatPromptTemplate(
        [
            ("system", "{instruction}"),
            ("human", "Please respond accordingly."),
        ],
    )

    prompt = prompt_template.with_config(run_name="Normal Chat Prompt").invoke(
        {
            "instruction": Prompt.normal_chat().format(
                question=state["question"],
                error=state.get("error", "None"),
            ),
        },
    )

    try:
        response = llm.with_config(run_name="Normal Chat").invoke(prompt)
        return {**state, "answer": str(response.content)}
    except Exception as e:
        return {
            **state,
            "answer": f"Sorry, I encountered an error while answering your question: {str(e)}",
        }


def answer_up(state: State) -> State:
    """Answer question using retrieved information as context."""
    # If we're using chat instead of database
    if state.get("use_chat", False):
        return normal_chat(state)

    if state.get("error"):
        return {
            **state,
            "answer": f"Sorry, I could not find any information regarding your question. Error: {state['error']}",
        }

    # Special handling for follow-up questions about existing results
    if state.get("is_followup", False):
        prompt_template = ChatPromptTemplate(
            [
                ("system", "{instruction}"),
                ("human", "Please respond accordingly."),
            ],
        )

        prompt = prompt_template.with_config(run_name="Followup Prompt").invoke(
            {
                "instruction": Prompt.follow_up().format(
                    question=state["question"],
                    query=state.get("query", "Unknown"),
                    result=state.get("result"),
                ),
            },
        )

        try:
            response = llm.with_config(run_name="Followup").invoke(prompt)
            return {**state, "answer": str(response.content)}
        except Exception as e:
            return {
                **state,
                "answer": f"Sorry, I encountered an error while answering your question: {str(e)}",
            }

    # Normal processing for regular queries
    prompt_template = ChatPromptTemplate(
        [
            ("system", "{instruction}"),
            ("human", "Please respond accordingly."),
        ],
    )

    prompt = prompt_template.with_config(run_name="Answer Prompt").invoke(
        {
            "instruction": Prompt.answer_machine().format(
                question=state["question"],
                query=state.get("query"),
                result=state.get("result"),
            ),
        },
    )

    try:
        response = (
            llm.with_structured_output(schema=AnswerOutput)
            .with_config(run_name="Answer Up")
            .invoke(prompt)
        )
        return {**state, **response.model_dump()}
    except Exception as e:
        return {
            **state,
            "answer": f"Sorry, I encountered an error while answering your question: {str(e)}",
        }


def router(state: State) -> str:
    """Route the workflow based on whether we need database or chat."""
    # If this is a follow-up question with existing results, skip directly to answer
    if state.get("is_followup", False) and state.get("result") is not None:
        return "answer_up"

    if state.get("use_chat", False):
        return "answer_up"
    return "execute"


def dag() -> CompiledStateGraph:
    """Create and compile the state graph."""
    workflow = StateGraph(State)
    workflow.add_node("quarify", quarify)
    workflow.add_node("execute", execute)
    workflow.add_node("answer_up", answer_up)
    # Start always goes to query analysis
    workflow.add_edge(START, "quarify")
    # After query analysis, conditionally route to execute or answer
    workflow.add_conditional_edges(
        "quarify",
        router,
        {"execute": "execute", "answer_up": "answer_up"},
    )
    # Execute always goes to answer
    workflow.add_edge("execute", "answer_up")
    # Answer always goes to end
    workflow.add_edge("answer_up", END)

    return workflow.compile(name="InfluxDB RAG with Fallback")
