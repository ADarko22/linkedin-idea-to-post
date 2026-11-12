import csv
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.linkedin.model import RawPost


@pytest.fixture
def sample_raw_post() -> RawPost:
    return RawPost(
        row=1,
        date="2023-01-01 00:00:00",
        share_link="https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A6457",
        share_commentary="""This is a test post.
        #test #post""",
    )


@pytest.fixture
def raw_post_factory(sample_raw_post: RawPost) -> Callable[..., RawPost]:
    def make(**overrides: Any) -> RawPost:
        return sample_raw_post.model_copy(update={**overrides})

    return make


@pytest.fixture
def sample_post() -> Post:
    return Post(
        id=UUID("9266cfeb-93f8-5593-823a-f6b81f3f6d75"),
        url="https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A6457",
        title="This is a test post.",
        body="""This is a test post.\n#test #post""",
        topics={"test", "post"},
        origin=PostOrigin.HUMAN,
        status=PostStatus.PUBLISHED,
        created_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
        updated_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
    )


@pytest.fixture
def post_factory(sample_post: Post) -> Callable[..., Post]:
    def make(**overrides: Any) -> Post:
        return sample_post.model_copy(update={"id": uuid4(), **overrides})

    return make


CSVFactory = Callable[[Sequence[Sequence[str]]], Path]


@pytest.fixture
def create_csv_post_file(tmp_path: Path) -> CSVFactory:
    """A factory fixture that generates a temporary CSV file from a list of rows."""

    def _create_file(rows: Sequence[Sequence[str]]) -> Path:
        # Create a unique file path inside pytest's managed temp directory
        csv_file = tmp_path / "test_data.csv"

        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

        return csv_file

    return _create_file
