from typing import Protocol
from uuid import UUID

from pydantic import BaseModel, Field

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus

DEFAULT_PAGE_SIZE = 50


class PostGetQuery(BaseModel):
    origins: list[PostOrigin] = Field(default_factory=list)
    statuses: list[PostStatus] = Field(default_factory=list)
    limit: int = DEFAULT_PAGE_SIZE
    page: int = 1


class PostStorage(Protocol):
    def save(self, post: Post) -> None: ...

    def get(self, post_id: UUID) -> Post | None: ...

    def get_all(self, query: PostGetQuery) -> list[Post]: ...
