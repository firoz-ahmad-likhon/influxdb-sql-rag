import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.agent.graph import Workflow
from src.utils.helper import Helper

app = FastAPI(
    title="InfluxDB RAG API",
    description="A question answering InfluxDB sql rag in langgraph.",
)

# CORS for frontend access (Streamlit, browser, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG
rag = Workflow().build(checkpointer=Helper.checkpoint())
config = {"configurable": {"thread_id": str(uuid.uuid4())}}


class Question(BaseModel):
    """Input validator."""

    question: str


@app.get("/api/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to the InfluxDB RAG API."}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}


@app.post("/api/chat")
def chat(payload: Question) -> dict[str, str]:
    """Chat endpoint."""
    try:
        response = rag.invoke({"question": payload.question}, config=config)
        return {"answer": response.get("answer", "Sorry, I have no answer.")}
    except Exception as e:
        return {"error": str(e)}
