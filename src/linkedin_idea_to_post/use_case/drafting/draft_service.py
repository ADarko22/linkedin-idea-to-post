import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import extract_hashtags
from linkedin_idea_to_post.use_case.post_management.post_post_management_service import (
    PostStoreManagementService,
)


class DraftService:
    def __init__(
        self,
        writer: DraftWriter,
        post_store_manager: PostStoreManagementService,
        timestamp_provider: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.writer = writer
        self.post_store_manager = post_store_manager
        self.timestamp_provider = timestamp_provider

    def compose(self, draft_request: DraftRequest) -> Draft:
        return self.writer.write(draft_request)

    def draft(self, draft_request: DraftRequest) -> Post:
        draft = self.compose(draft_request)

        post_id = uuid.uuid5(uuid.NAMESPACE_URL, draft_request.idea)
        topics = extract_hashtags(draft.generated_content)
        now = self.timestamp_provider()

        draft_post = Post(
            id=post_id,
            url=None,
            body=draft.generated_content,
            topics=topics,
            status=PostStatus.DRAFT,
            origin=PostOrigin.AI_DRAFT,
            created_at=now,
            updated_at=now,
        )

        self.post_store_manager.save_post(draft_post)

        return draft_post
