from typing import Any

from crewai import BaseLLM, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tools import BaseTool
from crewai.utilities.types import LLMMessage
from pydantic import BaseModel


class PromptEchoLLM(BaseLLM):
    def __init__(self, model: str = "fake-model"):
        super().__init__(model=model, temperature=0)

    def call(
        self,
        messages: str | list[LLMMessage],
        tools: list[dict[str, BaseTool]] | None = None,
        callbacks: list[Any] | None = None,
        available_functions: dict[str, Any] | None = None,
        from_task: Task | None = None,
        from_agent: BaseAgent | None = None,
        response_model: type[BaseModel] | None = None,
    ) -> str | Any:

        if isinstance(messages, str):
            captured_call = [f"Prompt #1 - role: user\n{messages}"]
        else:
            captured_call = [
                f"Prompt #{idx + 1} - role: {msg.get('role')}\n{msg.get('content')}"
                for idx, msg in enumerate(messages)
            ]

        echo_response = "\n\n".join(captured_call)

        return echo_response

    def get_context_window_size(self) -> int:
        return 8192
