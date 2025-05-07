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
                "input": "List all sensors.",
                "output": "SELECT sensor_id FROM sensor_meta",
            },
            {
                "input": "What is the average temperature in Main Lobby?",
                "output": "SELECT avg(temperature) FROM air_sensors LEFT JOIN sensor_meta ON air_sensors.sensor_id = sensor_meta.sensor_id WHERE location = 'Main Lobby'",
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
