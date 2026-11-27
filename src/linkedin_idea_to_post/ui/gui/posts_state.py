from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import extract_hashtags
from linkedin_idea_to_post.domain.storage import PostGetQuery


@dataclass
class PostsState:
    limit: int = 20
    page: int = 1
    search_term: str = ""
    origins: list[str] = field(default_factory=list)
    statuses: list[str] = field(default_factory=list)
    active_post: Post | None = None

    def set_limit(self, raw_limit: int | float | None) -> int:
        self.limit = max(1, int(raw_limit or 20))
        return self.limit

    def reset_page(self) -> None:
        self.page = 1

    def can_go_prev(self) -> bool:
        return self.page > 1

    def can_go_next(self, visible_count: int) -> bool:
        return visible_count >= self.limit

    def prev_page(self) -> bool:
        if self.page <= 1:
            return False
        self.page -= 1
        return True

    def next_page(self) -> None:
        self.page += 1

    def build_query(self) -> PostGetQuery:
        return PostGetQuery(
            origins=[PostOrigin(v) for v in self.origins],
            statuses=[PostStatus(v) for v in self.statuses],
            limit=self.limit,
            page=self.page,
        )

    def filter_posts(self, posts: list[Post]) -> list[Post]:
        needle = self.search_term.strip().lower()
        if not needle:
            return posts
        return [
            p
            for p in posts
            if needle in p.body.lower()
            or any(needle in tag.lower() for tag in p.hashtags)
        ]

    def build_updated_post(self, raw_body: str) -> Post | None:
        if self.active_post is None:
            return None
        updated_body = raw_body.strip()
        if not updated_body:
            raise ValueError("Post body cannot be empty.")

        post_origin = (
            PostOrigin.AI_EDIT
            if self.active_post.origin == PostOrigin.AI_DRAFT
            else self.active_post.origin
        )
        return self.active_post.model_copy(
            update={
                "body": updated_body,
                "hashtags": extract_hashtags(updated_body),
                "origin": post_origin,
                "updated_at": datetime.now(UTC),
            }
        )
