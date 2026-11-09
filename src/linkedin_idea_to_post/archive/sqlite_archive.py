import sqlite3
from pathlib import Path
from uuid import UUID

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus

_CREATE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        doc TEXT NOT NULL
    );
    """

_UPSERT_POST = """
    INSERT INTO posts (id, doc)
    VALUES (?, ?)
    ON CONFLICT (id) DO UPDATE SET
        id = excluded.id,
        doc = excluded.doc
    """

_GET_POST = """
    SELECT doc
    FROM posts
    WHERE id = ?
    """

DEFAULT_PAGE_SIZE = 50


class SqliteArchive:
    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        # create the table here if it doesn't exist
        self._conn.executescript(_CREATE_SCHEMA)

    def save(self, post: Post) -> None:
        with self._conn:
            json_post = post.model_dump_json()
            parameters = (str(post.id), json_post)
            self._conn.execute(_UPSERT_POST, parameters)

    def get(self, post_id: UUID) -> Post | None:
        with self._conn:
            parameters = (str(post_id),)
            row = self._conn.execute(_GET_POST, parameters).fetchone()
            if row is None:
                return None
            return Post.model_validate_json(row["doc"])

    def get_all(
        self,
        statuses: list[PostStatus] | None = None,
        origins: list[PostOrigin] | None = None,
        limit=DEFAULT_PAGE_SIZE,
        page=1,
    ) -> list[Post]:
        get_all_with_filter = SqliteArchive.build_get_all_with_filter_query(
            statuses=statuses, origins=origins, limit=limit, page=page
        )

        with self._conn:
            rows = self._conn.execute(get_all_with_filter).fetchall()
        return [Post.model_validate_json(row["doc"]) for row in rows]

    @staticmethod
    def build_get_all_with_filter_query(
        statuses: list[PostStatus] | None = None,
        origins: list[PostOrigin] | None = None,
        limit=DEFAULT_PAGE_SIZE,
        page=1,
    ):
        if limit < 1 or page < 1:
            raise ValueError("limit or page must be positive")

        query_parts = ["SELECT doc", "FROM posts"]

        clauses: list[str] = []
        if statuses is not None:
            status_list = ",".join(["'" + str(status) + "'" for status in statuses])
            clauses.append("json_extract(doc, '$.status') IN (" + status_list + ")")
        if origins is not None:
            origin_list = ",".join(["'" + str(origin) + "'" for origin in origins])
            clauses.append("json_extract(doc, '$.origin') IN (" + origin_list + ")")

        where_clause = "WHERE " + " AND ".join(clauses) if len(clauses) > 0 else ""

        query_parts += [where_clause]

        # order by breaks equality on created_at by id
        query_parts += ["ORDER BY json_extract(doc, '$.created_at') DESC, id DESC"]

        offset = (page - 1) * limit
        query_parts += [f"LIMIT {limit} OFFSET {offset}"]

        return "\n".join(query_parts)
