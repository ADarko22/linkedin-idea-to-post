import csv
from collections.abc import Callable, Sequence
from datetime import datetime
from pathlib import Path
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
