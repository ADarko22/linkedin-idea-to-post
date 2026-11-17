from typing import Any

from crewai import LLM, BaseLLM, Task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tools import BaseTool
from crewai.utilities.types import LLMMessage
from pydantic import BaseModel

from linkedin_idea_to_post.config import ConfigurationError, LlmSettings


def build_llm(llm_settings: LlmSettings | None, offline: bool = False) -> BaseLLM:
    if offline:
        return PromptEchoLLM()

    if llm_settings is None:
        raise ConfigurationError(
            "LlmSettings not configured in 'online' mode.",
            hint="Add the appropriate section to config.toml.",
        )

    api_key = llm_settings.api_key.get_secret_value().strip()
    if not api_key:
        raise ConfigurationError(
            "LLM API key is missing.",
            hint="Set the appropriate LLM_API_KEY in your environment.",
        )

    return LLM(
        model=llm_settings.model,
        api_key=api_key,
        temperature=llm_settings.temperature,
        max_tokens=llm_settings.max_tokens,
    )


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
