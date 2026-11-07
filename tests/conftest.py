from datetime import datetime
from uuid import UUID

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
        created_at=datetime.fromisoformat("2023-01-01T00:00:00"),
        updated_at=datetime.fromisoformat("2023-01-01T00:00:00"),
    )
