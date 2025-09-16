from pydantic import BaseModel, Field


class Question(BaseModel):
    """Question validator."""

    question: str = Field(description="Database related question or normal chat.")
