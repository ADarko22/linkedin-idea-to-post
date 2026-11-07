import sqlite3
from pathlib import Path
from uuid import UUID

from linkedin_idea_to_post.domain.post import Post

CREATE_SCHEMA = """
    CREATE TABLE IF NOT EXISTS post (
        id TEXT PRIMARY KEY,
        doc TEXT NOT NULL
    );
    """

UPSERT_POST = """
    INSERT INTO post (id, doc)
    VALUES (?, ?)
    ON CONFLICT (id) DO UPDATE SET
        id = excluded.id,
        doc = excluded.doc
    """

GET_POST = """
    SELECT doc
    FROM post
    WHERE id = ?
    """


class SqliteArchive:
    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        # create the table here if it doesn't exist
        self._conn.executescript(CREATE_SCHEMA)

    def save(self, post: Post) -> None:
        with self._conn:
            json_post = post.model_dump_json()
            parameters = (str(post.id), json_post)
            self._conn.execute(UPSERT_POST, parameters)

    def get(self, post_id: UUID) -> Post | None:
        with self._conn:
            parameters = (str(post_id),)
            row = self._conn.execute(GET_POST, parameters).fetchone()
            if row is None:
                return None
            return Post.model_validate_json(row["doc"])
