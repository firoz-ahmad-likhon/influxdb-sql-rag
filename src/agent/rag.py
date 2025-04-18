from src.agent.workflow import dag

try:
    rag = dag()
except Exception as e:
    raise RuntimeError("Error: ", e) from e
