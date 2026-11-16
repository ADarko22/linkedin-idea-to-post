from datetime import datetime, timedelta
from uuid import UUID

import pytest

from linkedin_idea_to_post.config import PersistenceSettings
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.persistence.database import create_sqlite_connection
from linkedin_idea_to_post.persistence.sqlite_post_storage import SqlitePostStorage


def test_get_unknown_post_id_returns_none(in_memory_storage, sample_post) -> None:
    no_post = in_memory_storage.get(UUID(int=0))
    assert no_post is None


def test_save_then_get_returns_an_equal_post(in_memory_storage, sample_post) -> None:
    in_memory_storage.save(sample_post)
    post = in_memory_storage.get(sample_post.id)
    assert post == sample_post


def test_save_then_delete_removes_existing_post(in_memory_storage, sample_post) -> None:
    in_memory_storage.save(sample_post)
    post = in_memory_storage.get(sample_post.id)
    assert post == sample_post
    in_memory_storage.delete(sample_post.id)
    assert in_memory_storage.get(sample_post.id) is None


def test_save_same_id_twice_updates_the_post(in_memory_storage, sample_post) -> None:
    in_memory_storage.save(sample_post)
    updated_post = sample_post.model_copy(update={"title": "Updated Title"})
    in_memory_storage.save(updated_post)
    post = in_memory_storage.get(sample_post.id)
    assert post == updated_post


def test_save_and_get_post_across_multiple_instances(
    tmp_path, sample_post: Post
) -> None:
    db_path = tmp_path / "test.db"
    storage_settings = PersistenceSettings(db_path=db_path)
    db_connection = create_sqlite_connection(storage_settings)

    storage1 = SqlitePostStorage(db_connection)
    storage1.save(sample_post)

    storage2 = SqlitePostStorage(db_connection)
    post = storage2.get(sample_post.id)
    assert post == sample_post


def test_save_get_all_posts_raises_error_on_invalid_pagination(
    post_factory, in_memory_storage
):
    posts_count = 12
    # all posts with same created_at
    posts = [post_factory() for _ in range(posts_count)]

    for post in posts:
        in_memory_storage.save(post)

    with pytest.raises(ValueError):
        in_memory_storage.get_all(PostGetQuery(limit=0))

    with pytest.raises(ValueError):
        in_memory_storage.get_all(PostGetQuery(page=0))


def test_save_and_get_all_posts_with_pagination(
    post_factory, in_memory_storage
) -> None:
    posts_count = 12
    base_date = datetime.fromisoformat("2023-01-01T00:00:00Z")
    posts = [
        post_factory(created_at=base_date + timedelta(minutes=i))
        for i in range(posts_count)
    ]

    for post in posts:
        in_memory_storage.save(post)

    expected_ids = [
        p.id for p in sorted(posts, key=lambda p: p.created_at, reverse=True)
    ]
    page_size = posts_count // 2

    # first half posts are retrieved and is sorted by created_at
    page_1 = in_memory_storage.get_all(PostGetQuery(limit=page_size, page=1))
    assert [p.id for p in page_1] == expected_ids[:page_size]

    # second half posts are retrieved and is sorted by created_at
    page_2 = in_memory_storage.get_all(PostGetQuery(limit=page_size, page=2))
    assert [p.id for p in page_2] == expected_ids[page_size:]


def test_save_and_get_all_posts_with_pagination_tiebreak_on_ids(
    post_factory, in_memory_storage
) -> None:
    posts_count = 12
    # all posts with same created_at
    posts = [post_factory() for _ in range(posts_count)]

    for post in posts:
        in_memory_storage.save(post)

    expected_ids = [p.id for p in sorted(posts, key=lambda p: p.id, reverse=True)]

    # all posts are sorted by id desc
    all_posts = in_memory_storage.get_all(PostGetQuery(limit=posts_count, page=1))
    assert [p.id for p in all_posts] == expected_ids


def test_save_and_get_all_posts_with_draft_status(
    post_factory, in_memory_storage
) -> None:
    posts_count = 12
    statuses = [PostStatus.DRAFT, PostStatus.PUBLISHED]
    posts = [
        post_factory(status=statuses[i % len(statuses)]) for i in range(posts_count)
    ]

    for post in posts:
        in_memory_storage.save(post)

    # retrieve all posts with PostStatus.DRAFT
    query = PostGetQuery(limit=len(posts), page=1, statuses=[PostStatus.DRAFT])
    all_posts = in_memory_storage.get_all(query)

    expected_ids = {p.id for p in posts if p.status == PostStatus.DRAFT}
    assert {p.id for p in all_posts} == expected_ids


def test_save_and_get_all_posts_with_ai_origin(post_factory, in_memory_storage) -> None:
    posts_count = 12
    origins = [PostOrigin.HUMAN, PostOrigin.AI_DRAFT, PostOrigin.AI_EDIT]
    posts = [post_factory(origin=origins[i % len(origins)]) for i in range(posts_count)]

    for post in posts:
        in_memory_storage.save(post)

    # retrieve all posts with PostOrigin.AI_DRAFT or PostOrigin.AI_EDIT
    query = PostGetQuery(
        limit=len(posts), page=1, origins=[PostOrigin.AI_DRAFT, PostOrigin.AI_EDIT]
    )
    all_posts = in_memory_storage.get_all(query)

    expected_ids = {
        p.id
        for p in posts
        if p.origin == PostOrigin.AI_DRAFT or p.origin == PostOrigin.AI_EDIT
    }
    assert {p.id for p in all_posts} == expected_ids
