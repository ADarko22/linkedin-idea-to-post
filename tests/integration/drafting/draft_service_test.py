from uuid import UUID

from linkedin_idea_to_post.config import DraftingSettings
from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.drafting.draft_service import DraftService
from tests.fake_draft_writer import FakeDraftWriter


def test_compose_creates_draft(in_memory_storage, in_memory_retriever, post_factory):
    post1 = post_factory(id=UUID(int=1), body="Post 1 body.")
    post2 = post_factory(id=UUID(int=2), body="Post 2 body.")

    in_memory_storage.save(post1)
    in_memory_storage.save(post2)

    assert len(in_memory_storage.get_all(PostGetQuery())) == 2

    drafting_settings = DraftingSettings()
    writer = FakeDraftWriter()
    draft_service = DraftService(
        settings=drafting_settings,
        writer=writer,
        storage=in_memory_storage,
        retriever=in_memory_retriever,
    )

    request_idea = "My idea of post"
    draft = draft_service.compose(request_idea)

    # nothing is saved to storage
    assert len(in_memory_storage.get_all(PostGetQuery())) == 2

    expected_body = f"{request_idea}\n\nVoice examples received (2):\nExample #1:\n{post1.body}\n\nExample #2:\n{post2.body}\n\n"
    assert draft.body == expected_body


def test_draft_saves_drafted_post(in_memory_storage, in_memory_retriever, post_factory):
    post1 = post_factory(id=UUID(int=1), body="Post 1 body.")
    post2 = post_factory(id=UUID(int=2), body="Post 2 body.")

    in_memory_storage.save(post1)
    in_memory_storage.save(post2)

    drafting_settings = DraftingSettings()
    writer = FakeDraftWriter()
    draft_service = DraftService(
        settings=drafting_settings,
        writer=writer,
        storage=in_memory_storage,
        retriever=in_memory_retriever,
    )

    request_idea = "My idea of post"
    draft_post = draft_service.draft(request_idea)

    # post is saved to storage
    post = in_memory_storage.get(draft_post.id)
    assert post == draft_post
    expected_body = f"{request_idea}\n\nVoice examples received (2):\nExample #1:\n{post1.body}\n\nExample #2:\n{post2.body}\n\n"
    assert post.body == expected_body
