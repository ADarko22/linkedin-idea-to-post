import sqlite3

import pytest

from linkedin_idea_to_post.adapters.persistence.sql_builders import (
    build_embedding_search_sql,
    build_full_text_search_sql,
    build_get_all_posts_sql,
    prepare_fts_expression,
)
from linkedin_idea_to_post.domain.embedding import TextEmbedding
from linkedin_idea_to_post.domain.post import PostOrigin, PostStatus
from linkedin_idea_to_post.domain.retrieval import (
    FullTextPostSearchQuery,
    VectorPostSearchQuery,
)
from linkedin_idea_to_post.domain.storage import PostGetQuery


@pytest.mark.parametrize(
    ("raw_text", "expected"),
    [
        # Lowercasing & basic OR joining
        ("Kafka Streams Architecture", '"kafka" OR "streams" OR "architecture"'),
        # Stop-word removal & single-character filtering
        ("I am in a rush to be at the top", '"am" OR "rush" OR "top"'),
        # Order-preserving deduplication
        ("Java java JAVA and Kotlin kotlin", '"java" OR "kotlin"'),
        # Hyphenated words & contractions split into clean alphanumeric tokens
        (
            "I'm building self-growth habits",
            '"building" OR "self" OR "growth" OR "habits"',
        ),
        # FTS5 reserved keywords & column-filter syntax neutralized
        ('title:Kafka NOT (NEAR OR "AND*")', '"title" OR "kafka" OR "near"'),
        # Numeric tokens preserved
        ("Java 21 and Spring Boot 3", '"java" OR "21" OR "spring" OR "boot"'),
        # Empty, whitespace-only, punctuation-only, or stop-word-only inputs
        ("", ""),
        ("   \t\n  ", ""),
        ("??? --- *** !!!", ""),
        ("a I to the and of", ""),
    ],
)
def test_prepare_fts_expression(raw_text: str, expected: str) -> None:
    assert prepare_fts_expression(raw_text) == expected


@pytest.mark.parametrize(
    "adversarial_input",
    [
        '"""unbalanced quotes"""',
        "C++ & C# vs. F# (2026)!",
        "title:hack OR body:hack^2",
        "NEAR(foo bar, 10) -baz +qux*",
        "Line 1\nLine 2\x00NullByte",
        "100% of users don't know why—really?",
    ],
)
def test_prepare_fts_expression_never_causes_fts5_syntax_error(
    adversarial_input: str,
) -> None:
    """Validates generated expressions directly against SQLite's FTS5 MATCH parser."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE VIRTUAL TABLE docs USING fts5(content);")
    conn.execute("INSERT INTO docs(content) VALUES ('sample document text');")

    expr = prepare_fts_expression(adversarial_input)
    if expr:
        # Must execute cleanly without raising sqlite3.OperationalError
        rows = conn.execute(
            "SELECT rowid FROM docs WHERE docs MATCH ?", (expr,)
        ).fetchall()
        assert isinstance(rows, list)


@pytest.mark.parametrize(
    "query, expected_params",
    [
        (FullTextPostSearchQuery(search_text="I'm the best"), ['"best"', 10]),
        (
            FullTextPostSearchQuery(search_text="A long text.", limit=5),
            ['"long" OR "text"', 5],
        ),
    ],
)
def test_build_full_text_search_sql(
    query: FullTextPostSearchQuery, expected_params: list
) -> None:
    expected_sql = "SELECT posts.doc, bm25(posts_fts) AS score\n        FROM posts_fts\n        JOIN posts ON posts.rowid = posts_fts.rowid\n        WHERE posts_fts MATCH ?\n        ORDER BY score\n        LIMIT ?"
    assert build_full_text_search_sql(query) == (expected_sql, expected_params)


def test_build_full_text_search_sql_with_empty_search_text():
    query = FullTextPostSearchQuery(search_text="")
    assert build_full_text_search_sql(query) == (None, [])


def test_build_full_text_search_sql_with_invalid_limit():
    query = FullTextPostSearchQuery(search_text="", limit=0)
    with pytest.raises(ValueError):
        build_full_text_search_sql(query)


@pytest.mark.parametrize(
    "query, expected_params",
    [
        (
            VectorPostSearchQuery(
                search_text_embedding=TextEmbedding(
                    vector=[1.0, -1.0], embedding_model="model", dimensions=2
                )
            ),
            [
                "model",
                2,
            ],
        ),
        (
            VectorPostSearchQuery(
                search_text_embedding=TextEmbedding(
                    vector=[1.0, -1.0], embedding_model="model", dimensions=2
                ),
                origins=[PostOrigin.HUMAN],
                statuses=[PostStatus.PUBLISHED],
                limit=5,
            ),
            ["model", 2, "PUBLISHED", "HUMAN"],
        ),
    ],
)
def test_build_embedding_search_sql(
    query: VectorPostSearchQuery, expected_params: list
) -> None:
    query = VectorPostSearchQuery(
        search_text_embedding=TextEmbedding(
            vector=[1.0, -1.0], embedding_model="model", dimensions=2
        ),
        origins=[PostOrigin.HUMAN],
        statuses=[PostStatus.PUBLISHED],
        limit=5,
    )
    expected_sql = "SELECT posts.doc, post_embeddings.vector\n        FROM posts\n        JOIN post_embeddings ON posts.id = post_embeddings.post_id\n        WHERE post_embeddings.model_name = ? AND post_embeddings.dimensions = ? AND json_extract(posts.doc, '$.status') IN (?) AND json_extract(posts.doc, '$.origin') IN (?)"
    expected_params = ["model", 2, "PUBLISHED", "HUMAN"]
    assert build_embedding_search_sql(query) == (expected_sql, expected_params)


def test_build_embedding_search_sql_without_origins_and_statuses() -> None:
    query = VectorPostSearchQuery(
        search_text_embedding=TextEmbedding(
            vector=[1.0, -1.0], embedding_model="model", dimensions=2
        )
    )
    expected_sql = "SELECT posts.doc, post_embeddings.vector\n        FROM posts\n        JOIN post_embeddings ON posts.id = post_embeddings.post_id\n        WHERE post_embeddings.model_name = ? AND post_embeddings.dimensions = ?"
    expected_params = [
        "model",
        2,
    ]
    assert build_embedding_search_sql(query) == (expected_sql, expected_params)


def test_build_get_all_posts_sql() -> None:
    query = PostGetQuery(
        origins=[PostOrigin.HUMAN], statuses=[PostStatus.PUBLISHED], limit=5, page=1
    )
    expected_sql = "SELECT doc\n        FROM posts\n        WHERE json_extract(doc, '$.status') IN (?) AND json_extract(doc, '$.origin') IN (?)\n        ORDER BY json_extract(doc, '$.created_at') DESC, id DESC\n        LIMIT ? OFFSET ?"
    expected_params = ["PUBLISHED", "HUMAN", 5, 0]
    assert build_get_all_posts_sql(query) == (expected_sql, expected_params)


def test_build_get_all_posts_sql_without_origins_and_statuses() -> None:
    query = PostGetQuery()
    expected_sql = "SELECT doc\n        FROM posts\n        \n        ORDER BY json_extract(doc, '$.created_at') DESC, id DESC\n        LIMIT ? OFFSET ?"
    expected_params = [50, 0]
    assert build_get_all_posts_sql(query) == (expected_sql, expected_params)


def test_build_get_all_posts_sql_with_invalid_limit():
    query = PostGetQuery(limit=0)
    with pytest.raises(ValueError):
        build_get_all_posts_sql(query)


def test_build_get_all_with_filter_query_on_invalid_limit_raises_error():
    with pytest.raises(ValueError):
        build_get_all_posts_sql(PostGetQuery(limit=0, page=1))


def test_build_get_all_with_filter_query_on_invalid_page_raises_error():
    with pytest.raises(ValueError):
        build_get_all_posts_sql(PostGetQuery(page=0))
