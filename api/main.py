from fastapi import FastAPI
from api.routers import entry
from api.routers import chat


app = FastAPI(
    title="InfluxDB RAG API",
    description="A question answering InfluxDB sql rag in langgraph.",
    version="1.0",
    root_path="/api",
    debug=True,
)


# Include routers
app.include_router(entry.router)
app.include_router(chat.router)
