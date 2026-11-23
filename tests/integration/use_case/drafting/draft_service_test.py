import pytest

from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.use_case.drafting.draft_service import DraftService
from tests.fake_draft_writer import FakeDraftWriter


@pytest.fixture
def draft_service(in_memory_post_store_manager):
    return DraftService(writer=FakeDraftWriter())


@pytest.fixture
def expected_body(sample_draft_request):
    ctx = sample_draft_request.context
    voice_sel = ctx.voice_selections[0]
    k_sel1, k_sel2 = ctx.knowledge_selections[:2]

    return (
        f"{sample_draft_request.idea}\n\n"
        f"Voice examples (1):\n"
        f"Example #1 tuning={voice_sel.tuning.value}:\n"
        f"{ctx.relevant_posts[voice_sel.post_id].body}\n\n"
        f"Knowledge posts (2):\n"
        f"Post #1 stance={k_sel1.stance}:\n"
        f"{ctx.relevant_posts[k_sel1.post_id].body}\n\n"
        f"Post #2 stance={k_sel2.stance}:\n"
        f"{ctx.relevant_posts[k_sel2.post_id].body}\n\n"
    )


def test_compose_creates_draft(
    draft_service,
    in_memory_post_storage,
    sample_draft_request,
    expected_body,
):
    draft = draft_service.compose(sample_draft_request)

    assert draft.generated_content == expected_body
    assert len(in_memory_post_storage.get_all(PostGetQuery())) == 0
