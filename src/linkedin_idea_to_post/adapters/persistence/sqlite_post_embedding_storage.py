import sqlite3
from uuid import UUID

import numpy as np

from linkedin_idea_to_post.domain.post import PostEmbedding
from linkedin_idea_to_post.domain.storage import (
    PostEmbeddingStorage,
)

_UPSERT_POST_EMBEDDING = """
    INSERT INTO post_embeddings (post_id, model_name, dimensions, vector, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT (post_id) DO UPDATE SET
        post_id = excluded.post_id,
        model_name = excluded.model_name,
        dimensions = excluded.dimensions,
        vector = excluded.vector,
        created_at = excluded.created_at,
        updated_at = excluded.updated_at
    """

_DELETE_POST_EMBEDDING = """
    DELETE FROM post_embeddings WHERE post_id = ?"""

_GET_POST_EMBEDDING = """
    SELECT *
    FROM post_embeddings
    WHERE post_id = ?
    """


class SQLitePostEmbeddingStorage(PostEmbeddingStorage):
    def __init__(self, db_connection: sqlite3.Connection) -> None:
        self._db_connection = db_connection

    def save(self, post_embedding: PostEmbedding) -> None:
        with self._db_connection:
            vector_bytes = np.asarray(post_embedding.vector, dtype=np.float32).tobytes()
            params = (
                str(post_embedding.post_id),
                post_embedding.embedding_model,
                post_embedding.dimensions,
                vector_bytes,
                post_embedding.created_at,
                post_embedding.updated_at,
            )
            self._db_connection.execute(_UPSERT_POST_EMBEDDING, params)

    def delete(self, post_id: UUID) -> None:
        with self._db_connection:
            params = (str(post_id),)
            self._db_connection.execute(_DELETE_POST_EMBEDDING, params)

    def get(self, post_id: UUID) -> PostEmbedding | None:
        with self._db_connection:
            parameters = (str(post_id),)
            row = self._db_connection.execute(
                _GET_POST_EMBEDDING, parameters
            ).fetchone()
            if row is None:
                return None
            vector = np.frombuffer(row[3], dtype=np.float32).tolist()
            return PostEmbedding(
                post_id=row[0],
                embedding_model=row[1],
                dimensions=row[2],
                vector=vector,
                created_at=row[4],
                updated_at=row[5],
            )
