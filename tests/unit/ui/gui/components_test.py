from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui.components import (
    format_created_at,
    format_post_badge,
    status_badge_color,
)
from linkedin_idea_to_post.ui.gui.helpers import format_hashtags, post_short_preview


def _make_post(
    *,
    body: str = "Hello LinkedIn world",
    hashtags: set[str] | None = None,
    origin: PostOrigin = PostOrigin.HUMAN,
    status: PostStatus = PostStatus.PUBLISHED,
) -> Post:
    return Post(
        id=UUID(int=1),
        url=None,
        body=body,
        hashtags=hashtags if hashtags is not None else set(),
        origin=origin,
        status=status,
        created_at=datetime(2026, 3, 15, 14, 30, tzinfo=UTC),
        updated_at=datetime(2026, 3, 15, 14, 30, tzinfo=UTC),
    )


def test_format_created_at_renders_utc_timestamp() -> None:
    post = _make_post()
    assert format_created_at(post) == "2026-03-15 14:30 UTC"


def test_status_badge_color() -> None:
    assert status_badge_color(PostStatus.PUBLISHED) == "positive"
    assert status_badge_color(PostStatus.DRAFT) == "warning"


def test_format_post_badge() -> None:
    assert (
        format_post_badge(PostOrigin.AI_DRAFT, PostStatus.DRAFT) == "AI_DRAFT · DRAFT"
    )


def test_post_short_preview_collapses_whitespace_and_truncates() -> None:
    short = _make_post(body="Line one\n\n   Line two")
    assert post_short_preview(short) == "Line one Line two"

    long_post = _make_post(body="word " * 30)
    preview = post_short_preview(long_post, max_chars=20)
    assert len(preview) <= 20
    assert preview.endswith("…")


def test_format_hashtags_sorts_and_prefixes() -> None:
    post = _make_post(hashtags={"python", "#ai"})
    assert format_hashtags(post) == "#ai #python"
    assert format_hashtags(_make_post(hashtags=set())) == ""
