import re
import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from linkedin_idea_to_post.domain.drafting import Draft
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus

_HASHTAG_REGEX = re.compile(r"(?<![^\s.,;!?)(])#([^\W\d_]\w*)(?=[\s.,;!?)(]|$)")


def extract_hashtags(raw_body: str) -> set[str]:
    hashtags = _HASHTAG_REGEX.findall(raw_body)
    return {hashtag.lower() for hashtag in hashtags}


def post_from_draft(
    draft: Draft,
    body_override: str | None = None,
    origin: PostOrigin = PostOrigin.AI_DRAFT,
    status: PostStatus = PostStatus.DRAFT,
    timestamp_provider: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> Post:
    """Convert a Draft (optionally edited in the UI) into a new Post entity."""
    content = body_override if body_override is not None else draft.generated_content
    now = timestamp_provider().astimezone(UTC)
    return Post(
        id=uuid.uuid4(),
        url=None,
        body=content,
        hashtags=extract_hashtags(content),
        origin=origin,
        status=status,
        created_at=now,
        updated_at=now,
    )
