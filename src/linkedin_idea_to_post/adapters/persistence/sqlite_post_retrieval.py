import sqlite3
from typing import Any

import numpy as np

from linkedin_idea_to_post.adapters.helpers.math import (
    matrix_vector_cosine_similarity,
    top_k_indices,
)
from linkedin_idea_to_post.adapters.persistence.sql_builders import (
    build_embedding_search_sql,
    build_full_text_search_sql,
)
from linkedin_idea_to_post.domain.post import Post, ScoredPost
from linkedin_idea_to_post.domain.retrieval import (
    FullTextPostSearchQuery,
    PostRetriever,
    VectorPostSearchQuery,
)


class SqlitePostRetriever(PostRetriever):
    def __init__(self, db_connection: sqlite3.Connection) -> None:
        self._db_connection = db_connection

    def full_text_search(self, query: FullTextPostSearchQuery) -> list[ScoredPost]:
        sql, params = build_full_text_search_sql(query)
        if not sql:
            return []

        rows = self._db_connection.execute(sql, params).fetchall()
        return [
            ScoredPost(post=Post.model_validate_json(row["doc"]), score=row["score"])
            for row in rows
        ]

    def semantic_search(self, query: VectorPostSearchQuery) -> list[ScoredPost]:
        sql, params = build_embedding_search_sql(query)
        rows = self._db_connection.execute(sql, params).fetchall()
        if not rows:
            return []

        return self._top_k_scored_posts(query, rows)

    @staticmethod
    def _top_k_scored_posts(
        query: VectorPostSearchQuery, rows: list[Any]
    ) -> list[ScoredPost]:
        query_vec = np.asarray(query.search_text_embedding.vector, dtype=np.float32)
        matrix = np.vstack(
            [np.frombuffer(row["vector"], dtype=np.float32) for row in rows]
        )

        scores = matrix_vector_cosine_similarity(matrix, query_vec)
        top_k_indices_arr = top_k_indices(scores, query.limit)

        results: list[ScoredPost] = []
        for idx in top_k_indices_arr:
            row = rows[int(idx)]
            post = Post.model_validate_json(row["doc"])
            results.append(ScoredPost(post=post, score=float(scores[idx])))
        return results
