from pydantic import BaseModel, Field


class QueryOutput(BaseModel):
    """Generated SQL query for InfluxDB 3."""

    query: str = Field(description="Syntactically valid SQL query for InfluxDB 3.")


class AnswerOutput(BaseModel):
    """Generated answer using query in InfluxDB 3."""

    answer: str = Field(
        description="Natural answer from result of executed SQL query in InfluxDB 3.",
    )
