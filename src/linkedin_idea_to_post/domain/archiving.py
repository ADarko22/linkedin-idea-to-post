from typing import Protocol
from uuid import UUID

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus

DEFAULT_PAGE_SIZE = 50


class PostArchive(Protocol):
    def save(self, post: Post) -> None: ...

    def get(self, post_id: UUID) -> Post | None: ...

    def get_all(
        self,
        statuses: list[PostStatus] | None = None,
        origins: list[PostOrigin] | None = None,
        limit: int = DEFAULT_PAGE_SIZE,
        page: int = 1,
    ) -> list[Post]: ...
