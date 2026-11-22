from datetime import UTC, datetime
from uuid import UUID

import pydantic
import pytest

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus


def test_post_survives_a_json_round_trip(sample_post: Post) -> None:
    data = sample_post.model_dump(mode="json")
    assert data["origin"] == "HUMAN"
    assert data["status"] == "PUBLISHED"
    assert Post.model_validate(data) == sample_post


def test_utc_time_conversion_success() -> None:
    post = Post(
        id=UUID(int=2),
        url="https://www.linkedin.com/test_url",
        body="This is a test post.",
        topics={"test", "post"},
        origin=PostOrigin.HUMAN,
        status=PostStatus.DRAFT,
        # 00:00:00+02:00 means it is 2 hours ahead of UTC
        created_at=datetime.fromisoformat("2026-01-01T00:00:00+02:00"),
        updated_at=datetime.fromisoformat("2026-01-01T00:00:00+02:00"),
    )

    # field_validator shifts it to UTC (+00:00)
    assert post.created_at.tzinfo == UTC
    assert post.updated_at.tzinfo == UTC

    # Mathematical adjustment (00:00 - 2 hours = 22:00 the previous day, which is previous month and year)
    assert post.created_at.hour == 22
    assert post.created_at.year == 2025
    assert post.created_at.month == 12
    assert post.created_at.day == 31


def test_utc_time_conversion_rejects_naive() -> None:
    with pytest.raises(pydantic.ValidationError, match="timezone_aware"):
        Post(
            id=UUID(int=2),
            url="https://www.linkedin.com/test_url",
            body="This is a test post.",
            topics={"test", "post"},
            origin=PostOrigin.HUMAN,
            status=PostStatus.DRAFT,
            # Missing any 'Z' or '+00:00' timezone suffix
            created_at=datetime.fromisoformat("2026-01-01T00:00:00"),
            updated_at=datetime.fromisoformat("2026-01-01T00:00:00"),
        )
