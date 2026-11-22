from linkedin_idea_to_post.adapters.ai_workflow.prompt_helpers import (
    format_knowledge_examples,
    format_voice_examples,
)
from linkedin_idea_to_post.domain.drafting import (
    DraftContext,
    DraftRequest,
    KnowledgeSelection,
    KnowledgeStance,
    VoiceSelection,
    VoiceTuning,
)


def test_format_voice_examples_with_no_examples() -> None:
    context = DraftContext()
    request = DraftRequest(idea="", context=context)
    expected_formatted_voices = "No specific style examples provided. Use a clear, authentic, professional LinkedIn voice."
    assert format_voice_examples(request) == expected_formatted_voices


def test_format_voice_examples(post_factory) -> None:
    post1 = post_factory()
    post2 = post_factory()
    relevant_posts = {post.id: post for post in [post1, post2]}
    voice_selection1 = VoiceSelection(post_id=post1.id, tuning=VoiceTuning.MATCH_STYLE)
    voice_selection2 = VoiceSelection(
        post_id=post2.id, tuning=VoiceTuning.PUNCHY_HOOK_ONLY
    )
    context = DraftContext(
        relevant_posts=relevant_posts,
        voice_selections=[voice_selection1, voice_selection2],
    )

    request = DraftRequest(idea="", context=context)

    expected_formatted_voices = f"""<example index="1" tuning="{voice_selection1.tuning.value}">
How to apply this example: {voice_selection1.tuning.instruction}
Example text:
{post1.body.strip()}
</example>

<example index="2" tuning="{voice_selection2.tuning.value}">
How to apply this example: {voice_selection2.tuning.instruction}
Example text:
{post2.body.strip()}
</example>"""
    assert format_voice_examples(request) == expected_formatted_voices


def test_format_knowledge_examples_with_no_examples() -> None:
    context = DraftContext()
    request = DraftRequest(idea="", context=context)
    expected_formatted_knowledge = (
        "No prior posts provided for knowledge context. Rely on the core idea."
    )
    assert format_knowledge_examples(request) == expected_formatted_knowledge


def test_format_knowledge_examples(post_factory) -> None:
    post1 = post_factory()
    post2 = post_factory()
    relevant_posts = {post.id: post for post in [post1, post2]}
    knowledge_selection1 = KnowledgeSelection(
        post_id=post1.id, stance=KnowledgeStance.NEUTRAL
    )
    knowledge_selection2 = KnowledgeSelection(
        post_id=post2.id, stance=KnowledgeStance.EVOLVED_VIEW
    )
    context = DraftContext(
        relevant_posts=relevant_posts,
        knowledge_selections=[knowledge_selection1, knowledge_selection2],
    )

    request = DraftRequest(idea="", context=context)

    expected_formatted_knowledge = f"""<reference index="1" stance="{knowledge_selection1.stance.value}">
How to treat this post: {knowledge_selection1.stance.instruction}
Content:
{post1.body.strip()}
</reference>

<reference index="2" stance="{knowledge_selection2.stance.value}">
How to treat this post: {knowledge_selection2.stance.instruction}
Content:
{post2.body.strip()}
</reference>"""
    assert format_knowledge_examples(request) == expected_formatted_knowledge
