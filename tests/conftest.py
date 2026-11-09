from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import pytest

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus


@pytest.fixture
def sample_post() -> Post:
    return Post(
        id=UUID(int=1),
        title="Test Post",
        body="This is a test post.",
        topics={"test", "post"},
        origin=PostOrigin.HUMAN,
        status=PostStatus.DRAFT,
        created_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
        updated_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
    )


@pytest.fixture
def post_factory(sample_post: Post) -> Callable[..., Post]:
    def make(**overrides: Any) -> Post:
        return sample_post.model_copy(update={"id": uuid4(), **overrides})

    return make
