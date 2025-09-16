from pydantic import BaseModel, Field


class AnswerSuccess(BaseModel):
    """Answer output."""

    answer: str = Field(description="Natural language answer from LLM.")


class AnswerError(BaseModel):
    """Answer output."""

    error: str = Field(description="Error message.")
