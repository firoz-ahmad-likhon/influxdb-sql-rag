from langchain_core.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate
from langsmith import traceable


class InfluxDBFewShot:
    """Few shot prompt for InfluxDB."""

    @staticmethod
    @traceable(name="SQL few shot", run_type="prompt")
    def sql_generation_train() -> FewShotChatMessagePromptTemplate:
        """Generate few shot training prompt for SQL generation."""
        examples = [
            {
                "input": "List all students who were present yesterday.",
                "output": "SELECT name FROM attendance WHERE present = 1 AND time = '2025-03-20'",
            },
            {
                "input": "How many students were absent last Tuesday?",
                "output": "SELECT COUNT(*) FROM attendance WHERE present = 0 AND time = '2025-03-18'",
            },
        ]

        example_prompt = ChatPromptTemplate(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ],
        )

        return FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )
