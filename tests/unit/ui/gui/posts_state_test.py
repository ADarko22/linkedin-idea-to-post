from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui.posts_state import PostsState


def _make_post(
    idx: int,
    *,
    body: str = "Post body",
    hashtags: set[str] | None = None,
    origin: PostOrigin = PostOrigin.HUMAN,
    status: PostStatus = PostStatus.PUBLISHED,
) -> Post:
    return Post(
        id=UUID(int=idx),
        url=None,
        body=body,
        hashtags=hashtags if hashtags is not None else set(),
        origin=origin,
        status=status,
        created_at=datetime(2026, 3, 15, 14, 30, tzinfo=UTC),
        updated_at=datetime(2026, 3, 15, 14, 30, tzinfo=UTC),
    )


def test_posts_state_pagination_and_query() -> None:
    state = PostsState(limit=10, origins=["HUMAN"], statuses=["PUBLISHED"])
    assert state.can_go_prev() is False
    assert state.prev_page() is False
    assert state.can_go_next(10) is True
    assert state.can_go_next(9) is False

    state.next_page()
    assert state.page == 2
    assert state.can_go_prev() is True

    query = state.build_query()
    assert query.page == 2
    assert query.limit == 10
    assert query.origins == [PostOrigin.HUMAN]
    assert query.statuses == [PostStatus.PUBLISHED]

    state.reset_page()
    assert state.page == 1


def test_posts_state_filter_posts_matches_body_and_hashtags() -> None:
    p1 = _make_post(1, body="Clean architecture in Python", hashtags={"python"})
    p2 = _make_post(2, body="Leadership notes", hashtags={"management"})

    state = PostsState(search_term="python")
    assert state.filter_posts([p1, p2]) == [p1]

    state.search_term = "manage"
    assert state.filter_posts([p1, p2]) == [p2]

    state.search_term = ""
    assert state.filter_posts([p1, p2]) == [p1, p2]


def test_posts_state_build_updated_post_transitions_ai_draft_to_ai_edit() -> None:
    draft = _make_post(
        1,
        body="Old text",
        origin=PostOrigin.AI_DRAFT,
        status=PostStatus.DRAFT,
    )
    state = PostsState(active_post=draft)

    updated = state.build_updated_post("New body with #testing #python")
    assert updated is not None
    assert updated.body == "New body with #testing #python"
    assert updated.origin == PostOrigin.AI_EDIT
    assert updated.hashtags == {"testing", "python"}

    with pytest.raises(ValueError, match="cannot be empty"):
        state.build_updated_post("   ")
