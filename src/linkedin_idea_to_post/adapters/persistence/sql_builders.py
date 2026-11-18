import re
from typing import Any

from linkedin_idea_to_post.domain.retrieval import (
    FullTextPostSearchQuery,
    VectorPostSearchQuery,
)
from linkedin_idea_to_post.domain.storage import PostGetQuery

_STOP_WORDS = frozenset(
    "a an and are as at be but by for from has have i if in is it me my no not "
    "of on or so that the this to was we with yet".split()
)

# SQL Statements for Storage
UPSERT_POST_SQL = """
    INSERT INTO posts (id, doc)
    VALUES (?, ?)
    ON CONFLICT (id) DO UPDATE SET
        id = excluded.id,
        doc = excluded.doc
"""

DELETE_POST_SQL = "DELETE FROM posts WHERE id = ?"
GET_POST_SQL = "SELECT doc FROM posts WHERE id = ?"


def prepare_fts_expression(text: str) -> str:
    raw_tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    unique_tokens = list(
        dict.fromkeys(t for t in raw_tokens if len(t) > 1 and t not in _STOP_WORDS)
    )
    return " OR ".join(f'"{t}"' for t in unique_tokens)


def build_full_text_search_sql(
    query: FullTextPostSearchQuery,
) -> tuple[str | None, list[Any]]:
    if query.limit < 1:
        raise ValueError("limit must be positive")

    fts_expression = prepare_fts_expression(query.search_text)
    if not fts_expression:
        return None, []

    clauses = ["posts_fts MATCH ?"]
    params: list[Any] = [fts_expression]

    if query.statuses:
        placeholders = ",".join("?" for _ in query.statuses)
        clauses.append(f"json_extract(posts.doc, '$.status') IN ({placeholders})")
        params.extend([s.value for s in query.statuses])

    if query.origins:
        placeholders = ",".join("?" for _ in query.origins)
        clauses.append(f"json_extract(posts.doc, '$.origin') IN ({placeholders})")
        params.extend([o.value for o in query.origins])

    sql = f"""
        SELECT posts.doc, bm25(posts_fts) AS score
        FROM posts_fts
        JOIN posts ON posts.rowid = posts_fts.rowid
        WHERE {" AND ".join(clauses)}
        ORDER BY score
        LIMIT ?
    """.strip()
    params.append(query.limit)
    return sql, params


def build_embedding_search_sql(
    query: VectorPostSearchQuery,
) -> tuple[str, list[Any]]:
    clauses = ["post_embeddings.model_name = ?", "post_embeddings.dimensions = ?"]
    params: list[Any] = [query.embedding_model, query.dimensions]

    if query.statuses:
        placeholders = ",".join("?" for _ in query.statuses)
        clauses.append(f"json_extract(posts.doc, '$.status') IN ({placeholders})")
        params.extend([s.value for s in query.statuses])

    if query.origins:
        placeholders = ",".join("?" for _ in query.origins)
        clauses.append(f"json_extract(posts.doc, '$.origin') IN ({placeholders})")
        params.extend([o.value for o in query.origins])

    sql = f"""
        SELECT posts.doc, post_embeddings.vector
        FROM posts
        JOIN post_embeddings ON posts.id = post_embeddings.post_id
        WHERE {" AND ".join(clauses)}
    """.strip()
    return sql, params


def build_get_all_posts_sql(query: PostGetQuery) -> tuple[str, list[Any]]:
    if query.limit < 1 or query.page < 1:
        raise ValueError("limit or page must be positive")

    clauses: list[str] = []
    params: list[Any] = []

    if query.statuses:
        placeholders = ",".join("?" for _ in query.statuses)
        clauses.append(f"json_extract(doc, '$.status') IN ({placeholders})")
        params.extend([s.value for s in query.statuses])

    if query.origins:
        placeholders = ",".join("?" for _ in query.origins)
        clauses.append(f"json_extract(doc, '$.origin') IN ({placeholders})")
        params.extend([o.value for o in query.origins])

    where_clause = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    offset = (query.page - 1) * query.limit

    sql = f"""
        SELECT doc
        FROM posts
        {where_clause}
        ORDER BY json_extract(doc, '$.created_at') DESC, id DESC
        LIMIT ? OFFSET ?
    """.strip()
    params.extend([query.limit, offset])
    return sql, params
