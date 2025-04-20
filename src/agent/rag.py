from src.agent.graph import Workflow

try:
    rag = Workflow().build()
except Exception as e:
    raise RuntimeError("Error: ", e) from e
