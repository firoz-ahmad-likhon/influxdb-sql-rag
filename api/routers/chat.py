from typing import Annotated
from fastapi import APIRouter, Depends
from api.dependencies import get_graph, get_config
from langgraph.graph.state import CompiledStateGraph
from langchain_core.runnables.config import RunnableConfig
from api.schemas.answer import AnswerSuccess, AnswerError
from api.schemas.question import Question

router = APIRouter()


@router.post("/chat", response_model=AnswerSuccess | AnswerError)
def chat(
    payload: Question,
    rag: Annotated[CompiledStateGraph, Depends(get_graph)],
    config: Annotated[RunnableConfig, Depends(get_config)],
) -> AnswerSuccess | AnswerError:
    """Chat endpoint."""
    try:
        response = rag.invoke({"question": payload.question}, config=config)
        return AnswerSuccess(answer=response.get("answer", "Sorry, I have no answer."))
    except Exception as e:
        return AnswerError(error=str(e))
