import pytest

from linkedin_idea_to_post.adapters.ai_workflow.crewai_draft_writer import (
    CrewaiDraftWriter,
)
from linkedin_idea_to_post.domain.drafting import DraftContext, DraftRequest
from tests.fake_llm import FakeLLM


@pytest.mark.slow
def test_write_with_voice_examples(sample_draft_request) -> None:
    fake_llm = FakeLLM()
    draft_writer = CrewaiDraftWriter(fake_llm)

    draft = draft_writer.write(sample_draft_request)
    assert "POST STYLE EXAMPLES:\nExample #1:\nPost 1" in draft.generated_content


@pytest.mark.slow
def test_write_without_voice_examples() -> None:
    fake_llm = FakeLLM()
    draft_writer = CrewaiDraftWriter(fake_llm)

    request = DraftRequest(idea="My idea", relevant_posts={}, context=DraftContext())

    draft = draft_writer.write(request)
    assert "POST STYLE EXAMPLES:\n\n" in draft.generated_content
