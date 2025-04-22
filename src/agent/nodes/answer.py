from typing import cast
from src.agent.state import State
from langchain_ollama import ChatOllama
from src.agent.prompt import Prompt
from src.agent.parser import AnswerOutput
from langchain_core.prompts import ChatPromptTemplate


class Answer:
    """Answer question using retrieved information as context."""

    def __init__(self, llm: ChatOllama):
        """Initialize the answer class."""
        self.llm = llm

    def __call__(self, state: State) -> State:
        """Call the answer class."""
        if state.get("type") == "chat":
            return self.normal_chat(state)

        if state.get("error"):
            return {
                "answer": f"Sorry, I could not find any information regarding your question. Error: {state['error']}",
            }

        if state.get("type") == "follow-up":
            template = ChatPromptTemplate(
                [
                    ("system", "{instruction}"),
                    ("human", "Please respond accordingly."),
                ],
            )

            prompt = template.invoke(
                {
                    "instruction": Prompt.follow_up().format(
                        question=state["question"],
                        query=state.get("query"),
                        result=state.get("result"),
                    ),
                },
            )

            try:
                response = self.llm.invoke(prompt)
                return {"answer": str(response.content)}
            except Exception as e:
                return {
                    "answer": f"Sorry, I encountered an error while answering your question: {str(e)}",
                }

        template = ChatPromptTemplate(
            [
                ("system", "{instruction}"),
                ("human", "Please respond accordingly."),
            ],
        )

        prompt = template.invoke(
            {
                "instruction": Prompt.answer_machine().format(
                    question=state["question"],
                    query=state.get("query"),
                    result=state.get("result"),
                ),
            },
        )

        try:
            response = self.llm.with_structured_output(schema=AnswerOutput).invoke(
                prompt,
            )
            return cast(State, {**response.model_dump()})
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error while answering your question: {str(e)}",
            }

    def normal_chat(self, state: State) -> State:
        """Handle non-database related questions with a normal chat response."""
        template = ChatPromptTemplate(
            [
                ("system", "{instruction}"),
                ("human", "Please respond accordingly."),
            ],
        )

        prompt = template.invoke(
            {
                "instruction": Prompt.normal_chat().format(
                    question=state["question"],
                    error=state.get("error", None),
                ),
            },
        )

        try:
            response = self.llm.invoke(prompt)
            return {"answer": str(response.content)}
        except Exception as e:
            return {
                "answer": f"Sorry, I encountered an error while answering your question: {str(e)}",
            }
