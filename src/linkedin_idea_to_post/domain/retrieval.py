from typing import Protocol

from pydantic import BaseModel, Field

from linkedin_idea_to_post.domain.post import PostOrigin, PostStatus, ScoredPost

DEFAULT_MAX_RESULTS = 10


class BasePostSearchQuery(BaseModel):
    origins: list[PostOrigin] = Field(default_factory=list)
    statuses: list[PostStatus] = Field(default_factory=list)
    limit: int = DEFAULT_MAX_RESULTS


class FullTextPostSearchQuery(BasePostSearchQuery):
    search_text: str


class VectorPostSearchQuery(BasePostSearchQuery):
    embedding_vector: list[float]
    embedding_model: str
    dimensions: int


class PostRetriever(Protocol):
    def full_text_search(self, query: FullTextPostSearchQuery) -> list[ScoredPost]: ...

    def semantic_search(self, query: VectorPostSearchQuery) -> list[ScoredPost]: ...
