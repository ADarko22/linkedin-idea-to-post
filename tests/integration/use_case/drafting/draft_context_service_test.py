from linkedin_idea_to_post.config import DraftingSettings
from linkedin_idea_to_post.domain.drafting import (
    DraftContext,
    KnowledgeSelection,
    VoiceSelection,
)
from linkedin_idea_to_post.domain.post import PostOrigin, PostStatus
from linkedin_idea_to_post.use_case.drafting.draft_context_service import (
    DraftContextService,
)


def test_create_draft_context(
    embedding_generator,
    in_memory_post_retriever,
    post_factory,
    in_memory_post_store_manager,
):
    idea = "cats demanding 5am breakfast and yelling like furry bosses"

    # exact match of 10 word count
    published_human_post1 = post_factory(
        body="Cats demanding 5am breakfast yell like tiny furry neighborhood bosses",
        origin=PostOrigin.HUMAN,
        status=PostStatus.PUBLISHED,
    )
    # exact match of 10 word count
    published_human_post2 = post_factory(
        body="Half-asleep mornings start fast when cats scream for tuna breakfast",
        origin=PostOrigin.HUMAN,
        status=PostStatus.PUBLISHED,
    )
    # longer post with word count of 46
    published_human_post3 = post_factory(
        body="Living with indoor cats means accepting that your alarm clock now has whiskers, four paws, and zero respect for weekends because once the hallway lights flicker or the kitchen door creaks even slightly, dramatic meowing echoes through the apartment until someone negotiates a bowl of kibble",
        origin=PostOrigin.HUMAN,
        status=PostStatus.PUBLISHED,
    )
    # strong match for knowledge
    published_ai_drafted_post = post_factory(
        body="Cats demanding 5am breakfast and yelling like furry bosses will always win morning negotiations",
        origin=PostOrigin.AI_DRAFT,
        status=PostStatus.PUBLISHED,
    )
    # unpublished post is not taken into account even if it's a strong match
    draft_human_post = post_factory(
        body="Cats demanding 5am breakfast and yelling like furry bosses again",
        origin=PostOrigin.HUMAN,
        status=PostStatus.DRAFT,
    )

    for post in [
        published_human_post1,
        published_human_post2,
        published_human_post3,
        published_ai_drafted_post,
        draft_human_post,
    ]:
        in_memory_post_store_manager.save_post(post)

    expected_draft_context = DraftContext(
        voice_selections=[
            VoiceSelection(post_id=published_human_post1.id),
            VoiceSelection(post_id=published_human_post2.id),
        ],
        knowledge_selections=[
            KnowledgeSelection(post_id=published_human_post1.id),
            KnowledgeSelection(post_id=published_ai_drafted_post.id),
        ],
    )

    settings = DraftingSettings(voice_examples_count=2, knowledge_examples_count=2)
    service = DraftContextService(
        settings=settings,
        embedding_generator=embedding_generator,
        retriever=in_memory_post_retriever,
    )

    target_word_count = 10
    draft_context = service.create_context(idea, target_word_count=target_word_count)

    assert draft_context == expected_draft_context
