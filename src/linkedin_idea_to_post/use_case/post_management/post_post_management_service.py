from types import TracebackType
from typing import Protocol, Self
from uuid import UUID

from linkedin_idea_to_post.domain.embedding import EmbeddingGenerator
from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.domain.storage import PostEmbeddingStorage, PostStorage


class UnitOfWork(Protocol):
    """
    Unit of Work object to coordinate a logical group of database changes: an "all-or-nothing" batch of work
    controls when those changes are committed (made permanent) or rolled back (discarded).

    Defined as a Context manager Protocol in order to be used in a with statement, and achieve atomic execution.
    The __enter__ and __exit__ are dunder (double-underscore) magic methods that define the context manager protocol.
    """

    def __enter__(self) -> Self: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None: ...


class PostStoreManagementService:
    """
    Use Case responsible for the atomicity of writes on PostStorage and PostEmbeddingStorage:
    updates to the posts and post_embeddings tables must happen as a single unit of work.
    """

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator,
        unit_of_work: UnitOfWork,
        post_storage: PostStorage,
        embedding_storage: PostEmbeddingStorage,
    ):
        self._embedding_generator = embedding_generator
        self._unit_of_work = unit_of_work
        self._post_storage = post_storage
        self._embedding_storage = embedding_storage

    def save_post(self, post: Post):
        post_embedding = self._embedding_generator.generate(post)

        with self._unit_of_work:
            self._post_storage.save(post)
            self._embedding_storage.save(post_embedding)

    def delete_post(self, post_id: UUID):
        with self._unit_of_work:
            self._embedding_storage.delete(post_id)
            self._post_storage.delete(post_id)
