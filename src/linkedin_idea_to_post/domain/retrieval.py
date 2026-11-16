from typing import Protocol

from pydantic import BaseModel, Field

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus

DEFAULT_MAX_RESULTS = 10


class PostSearchQuery(BaseModel):
    text: str
    origins: list[PostOrigin] = Field(default_factory=list)
    statuses: list[PostStatus] = Field(default_factory=list)
    limit: int = DEFAULT_MAX_RESULTS


class PostRetriever(Protocol):
    def full_text_search(self, query: PostSearchQuery) -> list[Post]: ...
