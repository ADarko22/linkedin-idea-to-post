from uuid import UUID

import pytest

from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.domain.post import Post


@pytest.fixture
def archive() -> SqliteArchive:
    return SqliteArchive(":memory:")


def test_get_unknown_post_id_returns_none(archive: SqliteArchive, sample_post: Post) -> None:
    no_post = archive.get(UUID(int=0))
    assert no_post is None


def test_save_then_get_returns_an_equal_post(archive: SqliteArchive, sample_post: Post) -> None:
    archive.save(sample_post)
    post = archive.get(sample_post.id)
    assert post == sample_post


def test_save_same_id_twice_updates_the_post(archive: SqliteArchive, sample_post: Post) -> None:
    archive.save(sample_post)
    updated_post = sample_post.model_copy(update={"title": "Updated Title"})
    archive.save(updated_post)
    post = archive.get(sample_post.id)
    assert post == updated_post

def test_save_and_det_across_multiple_instances(tmp_path, sample_post: Post) -> None:
    db_path = tmp_path / "test.db"
    archive1 = SqliteArchive(db_path)
    archive1.save(sample_post)

    archive2 = SqliteArchive(db_path)
    post = archive2.get(sample_post.id)
    assert post == sample_post