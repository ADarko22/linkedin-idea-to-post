import pytest
from crewai import BaseLLM
from pydantic import SecretStr

from linkedin_idea_to_post.adapters.ai_workflow.llm_factory import (
    PromptEchoLLM,
    build_llm,
)
from linkedin_idea_to_post.config import ConfigurationError, LlmSettings


@pytest.fixture
def sample_llm_settings() -> LlmSettings:
    return LlmSettings(
        model="gpt-40-mini",
        api_key=SecretStr("sk_test_secret-123"),
        temperature=0.7,
        max_tokens=1024,
    )


def test_build_llm_offline_without_settings_returns_prompt_echo_llm():
    llm = build_llm(llm_settings=None, offline=True)
    assert isinstance(llm, PromptEchoLLM)


def test_build_llm_offline_ignores_provided_settings(sample_llm_settings: LlmSettings):
    llm = build_llm(llm_settings=sample_llm_settings, offline=True)
    assert isinstance(llm, PromptEchoLLM)


def test_build_llm_online_without_settings_raises_configuration_error():
    with pytest.raises(
        ConfigurationError, match="LlmSettings not configured in 'online' mode."
    ):
        build_llm(llm_settings=None, offline=False)


def test_build_llm_online_without_api_key_raises_configuration_error():
    default_llm_settings = LlmSettings()
    with pytest.raises(ConfigurationError, match="LLM API key is missing."):
        build_llm(llm_settings=default_llm_settings, offline=False)


def test_build_llm_online_build_configured_llm(sample_llm_settings: LlmSettings):
    llm = build_llm(llm_settings=sample_llm_settings, offline=False)
    assert isinstance(llm, BaseLLM)
