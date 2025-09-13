from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to the InfluxDB RAG API."}


@router.get("/health")
def health_check() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}
