import pytest

from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.domain.post import PostOrigin, PostStatus


def test_build_get_all_with_filter_query_on_pagination():
    sql_query = SqliteArchive.build_get_all_with_filter_query(limit=10, page=2)
    expected_query = """
        SELECT doc
        FROM posts
        ORDER BY json_extract(doc, '$.created_at') DESC, id DESC
        LIMIT 10 OFFSET 10
    """
    assert " ".join(sql_query.split()) == " ".join(expected_query.split())


def test_build_get_all_with_filter_query_on_filter_status():
    sql_query = SqliteArchive.build_get_all_with_filter_query(
        statuses=[PostStatus.DRAFT]
    )
    expected_query = """
        SELECT doc
        FROM posts
        WHERE json_extract(doc, '$.status') IN ('DRAFT')
        ORDER BY json_extract(doc, '$.created_at') DESC, id DESC
        LIMIT 50 OFFSET 0
    """
    assert " ".join(sql_query.split()) == " ".join(expected_query.split())


def test_build_get_all_with_filter_query_on_filter_origins():
    sql_query = SqliteArchive.build_get_all_with_filter_query(
        origins=[PostOrigin.AI_DRAFT, PostOrigin.AI_EDIT]
    )
    expected_query = """
        SELECT doc
        FROM posts
        WHERE json_extract(doc, '$.origin') IN ('AI_DRAFT','AI_EDIT')
        ORDER BY json_extract(doc, '$.created_at') DESC, id DESC
        LIMIT 50 OFFSET 0
    """
    assert " ".join(sql_query.split()) == " ".join(expected_query.split())


def test_build_get_all_with_filter_query_on_filter_statuses_and_origins_and_pagination():
    sql_query = SqliteArchive.build_get_all_with_filter_query(
        statuses=[PostStatus.DRAFT, PostStatus.PUBLISHED],
        origins=[PostOrigin.AI_DRAFT, PostOrigin.AI_EDIT],
        limit=5,
        page=10,
    )
    expected_query = """
        SELECT doc
        FROM posts
        WHERE json_extract(doc, '$.status') IN ('DRAFT','PUBLISHED')
        AND json_extract(doc, '$.origin') IN ('AI_DRAFT','AI_EDIT')
        ORDER BY json_extract(doc, '$.created_at') DESC, id DESC
        LIMIT 5 OFFSET 45
    """
    assert " ".join(sql_query.split()) == " ".join(expected_query.split())


def test_build_get_all_with_filter_query_on_invalid_limit_raises_error():
    with pytest.raises(ValueError):
        SqliteArchive.build_get_all_with_filter_query(limit=0, page=1)


def test_build_get_all_with_filter_query_on_invalid_page_raises_error():
    with pytest.raises(ValueError):
        SqliteArchive.build_get_all_with_filter_query(page=0)
