from typing import Protocol

from pydantic import BaseModel

from linkedin_idea_to_post.domain.post import Post, PostEmbedding


class TextEmbedding(BaseModel):
    vector: list[float]
    embedding_model: str
    dimensions: int


class EmbeddingGenerator(Protocol):
    def generate(self, post: Post) -> PostEmbedding: ...

    def embed_text(self, text: str) -> TextEmbedding: ...
