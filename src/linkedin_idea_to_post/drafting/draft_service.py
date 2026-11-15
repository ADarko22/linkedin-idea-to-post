import uuid
from collections.abc import Callable
from datetime import UTC, datetime

from linkedin_idea_to_post.config import DraftingSettings
from linkedin_idea_to_post.domain.archiving import PostArchive
from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import extract_hashtags, extract_title


class DraftService:
    def __init__(
        self,
        settings: DraftingSettings,
        writer: DraftWriter,
        archive: PostArchive,
        timestamp_provider: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.settings = settings
        self.writer = writer
        self.archive = archive
        self.timestamp_provider = timestamp_provider

    def compose(self, idea: str) -> Draft:
        voice_example_posts = self._find_voice_examples()

        voice_examples = [post.body for post in voice_example_posts]
        draft_request = DraftRequest(idea=idea, voice_examples=voice_examples)
        return self.writer.write(draft_request)

    def draft(self, idea: str) -> Post:
        draft = self.compose(idea)

        post_title = extract_title(draft.body)
        post_id = uuid.uuid5(uuid.NAMESPACE_URL, idea)

        # todo add a semantic/intent search to extract topics from the draft
        topics = extract_hashtags(draft.body)

        now = self.timestamp_provider()

        draft_post = Post(
            id=post_id,
            url=None,
            title=post_title,
            body=draft.body,
            topics=topics,
            status=PostStatus.DRAFT,
            origin=PostOrigin.AI_DRAFT,
            created_at=now,
            updated_at=now,
        )

        self.archive.save(draft_post)

        return draft_post

    def _find_voice_examples(self) -> list[Post]:
        posts = self.archive.get_all(
            limit=self.settings.voice_examples_count,
            origins=[PostOrigin.HUMAN],
            statuses=[PostStatus.PUBLISHED],
        )
        return posts
