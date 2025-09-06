from langchain_core.prompts import FewShotChatMessagePromptTemplate, ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain.prompts.example_selector import MaxMarginalRelevanceExampleSelector
from langsmith import traceable
import os


class InfluxDBFewShot:
    """Few shot prompt for InfluxDB with MMR example selection."""

    @staticmethod
    @traceable(name="SQL few shot", run_type="prompt")
    def sql_generation_train() -> FewShotChatMessagePromptTemplate:
        """Generate few shot training prompt for SQL generation."""
        examples = [
            {
                "question": "List all sensors.",
                "query": "SELECT sensor_meta.sensor_id FROM sensor_meta",
            },
            {
                "question": "How many sensors are there?",
                "query": "SELECT count(distinct sensor_meta.sensor_id) FROM sensor_meta",
            },
            {
                "question": "What is the average temperature in Main Lobby?",
                "query": "SELECT avg(air_sensors.temperature) FROM air_sensors LEFT JOIN sensor_meta ON air_sensors.sensor_id = sensor_meta.sensor_id WHERE sensor_meta.location = 'Main Lobby'",
            },
            {
                "question": "What is the latest temperature in Room 201?",
                "query": "SELECT air_sensors.temperature FROM air_sensors INNER JOIN sensor_meta ON air_sensors.sensor_id = sensor_meta.sensor_id WHERE sensor_meta.location = 'Room 201' ORDER BY air_sensors.time DESC LIMIT 1",
            },
            {
                "question": "What is the latest temperature in Room 2001?",
                "query": "SELECT air_sensors.temperature FROM air_sensors INNER JOIN sensor_meta ON air_sensors.sensor_id = sensor_meta.sensor_id WHERE sensor_meta.location = 'Room 2001' ORDER BY air_sensors.time DESC LIMIT 1",
            },
        ]

        chroma_dir = os.getenv("CHROMADB_LOC", "/app/resources/chromadb")
        collection_name = "few_shot"

        embedding_model = OllamaEmbeddings(
            model=os.getenv("EMBEDDER", "nomic-embed-text"),
            base_url=os.getenv("OLLAMA_URL"),
        )

        # Rebuild or load vector store
        if not os.path.exists(chroma_dir) or not os.listdir(chroma_dir):
            texts = [e["question"] for e in examples]
            Chroma.from_texts(
                texts=texts,
                embedding=embedding_model,
                metadatas=examples,
                collection_name=collection_name,
                persist_directory=chroma_dir,
            )

        example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
            examples=examples,
            embeddings=embedding_model,
            vectorstore_cls=Chroma,
            vectorstore_kwargs={
                "collection_name": collection_name,
                "persist_directory": chroma_dir,
            },
            input_keys=["question"],
            k=2,
            fetch_k=5,
        )

        example_prompt = ChatPromptTemplate(
            [
                ("human", "{question}"),
                ("ai", "{query}"),
            ],
        )

        return FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            example_selector=example_selector,
            input_variables=["question"],
        )
