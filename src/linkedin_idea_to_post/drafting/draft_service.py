import uuid
from datetime import UTC, datetime

from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.domain.drafting import DraftRequest, DraftWriter
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import extract_hashtags, extract_title


class DraftService:
    def __init__(self, writer: DraftWriter, archive: SqliteArchive) -> None:
        self.writer = writer
        self.archive = archive

    def draft(self, idea: str) -> Post:
        related_posts = (
            self._find_related_posts()
        )  # this should be used as "voice" for the writer
        voice_examples = [post.body for post in related_posts]
        draft_request = DraftRequest(idea=idea, voice_examples=voice_examples)
        draft = self.writer.write(draft_request)

        post_title = extract_title(draft.body)
        post_id = uuid.uuid5(uuid.NAMESPACE_URL, post_title)

        # todo add a semantic/intent search to extract topics from the draft
        topics = extract_hashtags(draft.body)

        now = datetime.now(UTC)

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

    def _find_related_posts(self) -> list[Post]:
        # todo improve with semantic search, topic similarity, etc..
        #  for now only returns latest 2 posts
        posts = self.archive.get_all(
            limit=2, origins=[PostOrigin.HUMAN], statuses=[PostStatus.PUBLISHED]
        )
        return posts
