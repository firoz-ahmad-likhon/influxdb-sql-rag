from src.database.influxdb import InfluxDB
from src.utils.config import Config
from src.agent.state import State
from influxdb_client_3 import InfluxDBClient3
from langchain_ollama import ChatOllama
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph import START, END, StateGraph
from src.agent.nodes.query import Quarify
from src.agent.nodes.execute import Execute
from src.agent.nodes.answer import Answer
from src.agent.nodes.router import Router
from langgraph.checkpoint.base import BaseCheckpointSaver
import os


class Workflow:
    """Define the workflow of the agent."""

    def __init__(self) -> None:
        """Initialize the workflow."""
        Config.load_env()

        self.llm = ChatOllama(
            model=os.getenv("LLM_MODEL"),
            temperature=0,
            base_url=os.getenv("OLLAMA_URL"),
        )

        self.client = InfluxDB(
            InfluxDBClient3(
                token=os.getenv("INFLUXDB_TOKEN"),
                host=os.getenv("INFLUXDB_HOST"),
                database=os.getenv("INFLUXDB_DB"),
            ),
        )

        self.quarify = Quarify(self.client, self.llm)
        self.execute = Execute(self.client)
        self.answer_up = Answer(self.llm)
        self.router = Router()

    def build(
        self,
        checkpointer: BaseCheckpointSaver | None = None,
    ) -> CompiledStateGraph:
        """Create and compile the state graph."""
        graph = StateGraph(State)
        graph.add_node("quarify", self.quarify)
        graph.add_node("execute", self.execute)
        graph.add_node("answer_up", self.answer_up)
        graph.add_edge(START, "quarify")
        graph.add_conditional_edges(
            "quarify",
            self.router,
            {"execute": "execute", "answer_up": "answer_up"},
        )
        graph.add_edge("execute", "answer_up")
        graph.add_edge("answer_up", END)
        return graph.compile(name="InfluxDB RAG", checkpointer=checkpointer)
