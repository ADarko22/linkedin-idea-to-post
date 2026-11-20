from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.use_case.drafting.draft_service import DraftService
from tests.fake_draft_writer import FakeDraftWriter


def test_compose_creates_draft(
    in_memory_post_store_manager,
    in_memory_post_storage,
    in_memory_post_retriever,
    sample_draft_request,
):
    writer = FakeDraftWriter()
    draft_service = DraftService(
        writer=writer,
        post_store_manager=in_memory_post_store_manager,
    )

    draft = draft_service.compose(sample_draft_request)
    voice_post = sample_draft_request.relevant_posts[
        sample_draft_request.context.voice_selections[0].post_id
    ]

    # nothing is saved to storage
    assert len(in_memory_post_storage.get_all(PostGetQuery())) == 0

    expected_body = f"{sample_draft_request.idea}\n\nVoice examples received (1):\nExample #1:\n{voice_post.body}\n\n"
    assert draft.generated_content == expected_body


def test_draft_saves_drafted_post(
    in_memory_post_store_manager,
    in_memory_post_storage,
    sample_draft_request,
):
    writer = FakeDraftWriter()
    draft_service = DraftService(
        writer=writer,
        post_store_manager=in_memory_post_store_manager,
    )

    draft_post = draft_service.draft(sample_draft_request)
    voice_post = sample_draft_request.relevant_posts[
        sample_draft_request.context.voice_selections[0].post_id
    ]

    # post is saved to storage
    post = in_memory_post_storage.get(draft_post.id)
    assert post == draft_post
    expected_body = f"{sample_draft_request.idea}\n\nVoice examples received (1):\nExample #1:\n{voice_post.body}\n\n"
    assert post.body == expected_body
