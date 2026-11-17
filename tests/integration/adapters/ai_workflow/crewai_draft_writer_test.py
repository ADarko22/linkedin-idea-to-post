import pytest

from linkedin_idea_to_post.adapters.ai_workflow.crewai_draft_writer import (
    CrewaiDraftWriter,
)
from linkedin_idea_to_post.domain.drafting import DraftRequest
from tests.fake_llm import FakeLLM


@pytest.mark.slow
def test_write_with_voice_examples() -> None:
    fake_llm = FakeLLM()
    draft_writer = CrewaiDraftWriter(fake_llm)

    voice_examples = ["Post 1", "Post 2"]
    request = DraftRequest(idea="My idea", voice_examples=voice_examples)

    draft = draft_writer.write(request)
    assert (
        "POST STYLE EXAMPLES:\nExample #1:\nPost 1\n\nExample #2:\nPost 2" in draft.body
    )


@pytest.mark.slow
def test_write_without_voice_examples() -> None:
    fake_llm = FakeLLM()
    draft_writer = CrewaiDraftWriter(fake_llm)

    request = DraftRequest(idea="My idea", voice_examples=[])

    draft = draft_writer.write(request)
    assert "POST STYLE EXAMPLES:\n\n" in draft.body
