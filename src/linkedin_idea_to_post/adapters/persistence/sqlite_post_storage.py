import sqlite3
from uuid import UUID

from linkedin_idea_to_post.adapters.persistence.sql_builders import (
    build_get_all_posts_sql,
)
from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.domain.storage import (
    PostGetQuery,
    PostStorage,
)

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
        sql_query, params = build_get_all_posts_sql(query)

        with self._db_connection:
            rows = self._db_connection.execute(sql_query, params).fetchall()
        return [Post.model_validate_json(row["doc"]) for row in rows]
