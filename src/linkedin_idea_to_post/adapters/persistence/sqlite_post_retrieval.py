import re
import sqlite3

from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.domain.retrieval import PostRetriever, PostSearchQuery

_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "but",
        "by",
        "for",
        "from",
        "has",
        "have",
        "i",
        "if",
        "in",
        "is",
        "it",
        "me",
        "my",
        "no",
        "not",
        "of",
        "on",
        "or",
        "so",
        "that",
        "the",
        "this",
        "to",
        "was",
        "we",
        "with",
        "yet",
    }
)


def _prepare_fts_expression(text: str) -> str:
    """
    Escapes quotes and joins tokens by OR and wrapping then in quotes to avoid FTS5 syntax errors,
    due to some reserved character being present in the token.
    """
    # Extract alphanumeric word tokens (splits "self-growth" -> ["self", "growth"], strips punctuation/apostrophes)
    raw_tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())

    # Deduplicate while preserving order and dropping noise/stop words
    unique_tokens = list(
        dict.fromkeys(t for t in raw_tokens if len(t) > 1 and t not in _STOP_WORDS)
    )

    return " OR ".join(f'"{t}"' for t in unique_tokens)


class SqlitePostRetriever(PostRetriever):
    def __init__(self, db_connection: sqlite3.Connection) -> None:
        self._db_connection = db_connection

    def full_text_search(self, query: PostSearchQuery) -> list[Post]:
        scored_posts = self._full_text_search(query)
        return [post for post, _ in scored_posts]

    def _full_text_search(self, query: PostSearchQuery) -> list[tuple[Post, float]]:
        fts_expression = _prepare_fts_expression(query.text)
        if not fts_expression:
            return []

        clauses = ["posts_fts MATCH ?"]
        params: list[object] = [fts_expression]

        if query.statuses:
            placeholders = ",".join("?" for _ in query.statuses)
            clauses.append(f"json_extract(posts.doc, '$.status') IN ({placeholders})")
            params.extend(s.value for s in query.statuses)

        if query.origins:
            placeholders = ",".join("?" for _ in query.origins)
            clauses.append(f"json_extract(posts.doc, '$.origin') IN ({placeholders})")
            params.extend(o.value for o in query.origins)

        sql = f"""
            SELECT posts.doc, bm25(posts_fts) AS score
            FROM posts_fts
            JOIN posts ON posts.rowid = posts_fts.rowid
            WHERE {" AND ".join(clauses)}
            ORDER BY score
            LIMIT ?
        """
        params.append(query.limit)

        rows = self._db_connection.execute(sql, params).fetchall()
        return [(Post.model_validate_json(row["doc"]), row["score"]) for row in rows]
