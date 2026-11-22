import re

import pytest

from linkedin_idea_to_post.adapters.ai_workflow.crewai_draft_writer import (
    CrewaiDraftWriter,
)
from tests.fake_llm import FakeLLM


def _extract_tag(text: str, tag: str) -> str:
    match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
    assert match is not None, f"Missing <{tag}> block in prompt"
    return match.group(1)


@pytest.mark.slow
def test_write_draft_structure(sample_draft_request) -> None:
    # the FakeLLM is generating a content that contains merely the prompt that would be sent to the real LLM
    draft_writer = CrewaiDraftWriter(FakeLLM())

    draft = draft_writer.write(sample_draft_request)
    draft_content = draft.generated_content

    ctx = sample_draft_request.context
    voice_sel = ctx.voice_selections[0]
    k_sel1, k_sel2 = ctx.knowledge_selections[:2]

    # 1. Verify system & user message roles from CrewAI agent/task setup
    assert "Prompt #1 - role: system\nYou are Senior Content Writer." in draft_content
    assert "Prompt #2 - role: user" in draft_content

    # 2. Verify core idea block
    assert _extract_tag(draft_content, "core_idea").strip() == sample_draft_request.idea

    # 3. Verify voice_examples block in isolation
    voice_block = _extract_tag(draft_content, "voice_examples")
    assert f'<example index="1" tuning="{voice_sel.tuning.value}">' in voice_block
    assert ctx.relevant_posts[voice_sel.post_id].body in voice_block
    assert ctx.relevant_posts[k_sel2.post_id].body not in voice_block

    # 4. Verify knowledge_context block in isolation
    knowledge_block = _extract_tag(draft_content, "knowledge_context")
    assert f'<reference index="1" stance="{k_sel1.stance.value}">' in knowledge_block
    assert ctx.relevant_posts[k_sel1.post_id].body in knowledge_block
    assert f'<reference index="2" stance="{k_sel2.stance.value}">' in knowledge_block
    assert ctx.relevant_posts[k_sel2.post_id].body in knowledge_block
