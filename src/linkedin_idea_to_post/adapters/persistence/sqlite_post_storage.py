import sqlite3
from uuid import UUID

from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.domain.storage import PostGetQuery, PostStorage

_UPSERT_POST = """
    INSERT INTO posts (id, doc)
    VALUES (?, ?)
    ON CONFLICT (id) DO UPDATE SET
        id = excluded.id,
        doc = excluded.doc
    """

_DELETE_POST = """
    DELETE FROM posts WHERE id = ?"""

_GET_POST = """
    SELECT doc
    FROM posts
    WHERE id = ?
    """


class SqlitePostStorage(PostStorage):
    def __init__(self, db_connection: sqlite3.Connection) -> None:
        self._db_connection = db_connection

    def save(self, post: Post) -> None:
        with self._db_connection:
            json_post = post.model_dump_json()
            parameters = (str(post.id), json_post)
            self._db_connection.execute(_UPSERT_POST, parameters)

    def delete(self, post_id: UUID) -> None:
        with self._db_connection:
            parameters = (str(post_id),)
            self._db_connection.execute(_DELETE_POST, parameters)

    def get(self, post_id: UUID) -> Post | None:
        with self._db_connection:
            parameters = (str(post_id),)
            row = self._db_connection.execute(_GET_POST, parameters).fetchone()
            if row is None:
                return None
            return Post.model_validate_json(row["doc"])

    def get_all(self, query: PostGetQuery) -> list[Post]:
        get_all_with_filter = SqlitePostStorage.build_get_all_with_filter_query(query)

        with self._db_connection:
            rows = self._db_connection.execute(get_all_with_filter).fetchall()
        return [Post.model_validate_json(row["doc"]) for row in rows]

    @staticmethod
    def build_get_all_with_filter_query(query: PostGetQuery):
        if query.limit < 1 or query.page < 1:
            raise ValueError("limit or page must be positive")

        query_parts = ["SELECT doc", "FROM posts"]

        clauses: list[str] = []
        if query.statuses:
            status_list = ",".join(
                ["'" + str(status) + "'" for status in query.statuses]
            )
            clauses.append("json_extract(doc, '$.status') IN (" + status_list + ")")
        if query.origins:
            origin_list = ",".join(
                ["'" + str(origin) + "'" for origin in query.origins]
            )
            clauses.append("json_extract(doc, '$.origin') IN (" + origin_list + ")")

        where_clause = "WHERE " + " AND ".join(clauses) if len(clauses) > 0 else ""

        query_parts += [where_clause]

        # order by breaks equality on created_at by id
        query_parts += ["ORDER BY json_extract(doc, '$.created_at') DESC, id DESC"]

        offset = (query.page - 1) * query.limit
        query_parts += [f"LIMIT {query.limit} OFFSET {offset}"]

        return "\n".join(query_parts)
