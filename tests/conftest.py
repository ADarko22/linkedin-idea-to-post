import csv
import sqlite3
from collections.abc import Callable, Iterator, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import pytest

from linkedin_idea_to_post.adapters.embedding.embedding_generator import (
    PyTorchEmbeddingGenerator,
)
from linkedin_idea_to_post.adapters.persistence.database import create_sqlite_connection
from linkedin_idea_to_post.adapters.persistence.sqlite_post_embedding_storage import (
    SQLitePostEmbeddingStorage,
)
from linkedin_idea_to_post.adapters.persistence.sqlite_post_retrieval import (
    SqlitePostRetriever,
)
from linkedin_idea_to_post.adapters.persistence.sqlite_post_storage import (
    SqlitePostStorage,
)
from linkedin_idea_to_post.adapters.persistence.sqllite_unit_of_work import (
    SqliteUnitOfWork,
)
from linkedin_idea_to_post.config import EmbeddingSettings, PersistenceSettings
from linkedin_idea_to_post.domain.embedding import EmbeddingGenerator
from linkedin_idea_to_post.domain.post import (
    Post,
    PostEmbedding,
    PostOrigin,
    PostStatus,
)
from linkedin_idea_to_post.domain.retrieval import PostRetriever
from linkedin_idea_to_post.domain.storage import PostEmbeddingStorage, PostStorage
from linkedin_idea_to_post.use_case.linkedin_ingestion.model import RawPost
from linkedin_idea_to_post.use_case.post_management.post_write_management_service import (
    UnitOfWork,
)


####################################################################################
# Persistence
# In-Memory DB Connection being shared by in_memory_storage and in_memory_retriever
@pytest.fixture
def in_memory_db_connection() -> Iterator[sqlite3.Connection]:
    settings = PersistenceSettings(db_path=":memory:")
    conn = create_sqlite_connection(settings)
    yield conn
    conn.close()


####################################################################################
# Raw Post
@pytest.fixture
def sample_raw_post() -> RawPost:
    return RawPost(
        row=1,
        date="2023-01-01 00:00:00",
        share_link="https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A6457",
        share_commentary="""This is a test post.
        #test #post""",
    )


@pytest.fixture
def raw_post_factory(sample_raw_post: RawPost) -> Callable[..., RawPost]:
    def make(**overrides: Any) -> RawPost:
        return sample_raw_post.model_copy(update={**overrides})

    return make


####################################################################################
# Post
@pytest.fixture
def sample_post() -> Post:
    return Post(
        id=UUID("9266cfeb-93f8-5593-823a-f6b81f3f6d75"),
        url="https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A6457",
        title="This is a test post.",
        body="""This is a test post.\n#test #post""",
        topics={"test", "post"},
        origin=PostOrigin.HUMAN,
        status=PostStatus.PUBLISHED,
        created_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
        updated_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
    )


@pytest.fixture
def post_factory(sample_post: Post) -> Callable[..., Post]:
    def make(**overrides: Any) -> Post:
        return sample_post.model_copy(update={"id": uuid4(), **overrides})

    return make


CSVFactory = Callable[[Sequence[Sequence[str]]], Path]


@pytest.fixture
def create_csv_post_file(tmp_path: Path) -> CSVFactory:
    """A factory fixture that generates a temporary CSV file from a list of rows."""

    def _create_file(rows: Sequence[Sequence[str]]) -> Path:
        # Create a unique file path inside pytest's managed temp directory
        csv_file = tmp_path / "test_data.csv"

        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for row in rows:
                writer.writerow(row)

        return csv_file

    return _create_file


@pytest.fixture
def in_memory_storage(in_memory_db_connection: sqlite3.Connection) -> PostStorage:
    return SqlitePostStorage(in_memory_db_connection)


@pytest.fixture
def in_memory_retriever(in_memory_db_connection: sqlite3.Connection) -> PostRetriever:
    return SqlitePostRetriever(in_memory_db_connection)


####################################################################################
# Post Embedding
@pytest.fixture(scope="session")
def embedding_generator() -> EmbeddingGenerator:
    # Use a lightweight model for fast testing
    settings = EmbeddingSettings(
        model_name="all-MiniLM-L6-v2",
        local_model_path=Path("./data/models/all-MiniLM-L6-v2"),
        device="cpu",
    )
    return PyTorchEmbeddingGenerator(settings)


@pytest.fixture
def sample_embedding() -> PostEmbedding:
    return PostEmbedding(
        post_id=UUID("9266cfeb-93f8-5593-823a-f6b81f3f6d75"),
        embedding_model="test_model",
        vector=[1.0, 1.0],
        dimensions=2,
        created_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
        updated_at=datetime.fromisoformat("2023-01-01T00:00:00Z"),
    )


@pytest.fixture
def embedding_factory(sample_embedding: PostEmbedding) -> Callable[..., PostEmbedding]:
    def make(**overrides: Any) -> PostEmbedding:
        return sample_embedding.model_copy(update={"post_id": uuid4(), **overrides})

    return make


@pytest.fixture
def in_memory_embedding_storage(
    in_memory_db_connection: sqlite3.Connection,
) -> PostEmbeddingStorage:
    return SQLitePostEmbeddingStorage(in_memory_db_connection)


class FailingPostEmbeddingStorage:
    """Test double that fails on save() or delete() to verify atomic transaction rollback."""

    def __init__(self, error: BaseException | None = None) -> None:
        self._error = error or RuntimeError("Simulated embedding persistence failure")
        self.save_calls: list[PostEmbedding] = []
        self.delete_calls: list[UUID] = []

    def save(self, post_embedding: PostEmbedding) -> None:
        self.save_calls.append(post_embedding)
        raise self._error

    def delete(self, post_id: UUID) -> None:
        self.delete_calls.append(post_id)
        raise self._error

    def get(self, post_id: UUID) -> PostEmbedding | None:
        raise NotImplementedError


@pytest.fixture
def failing_embedding_storage() -> PostEmbeddingStorage:
    return FailingPostEmbeddingStorage()


class MockEmbeddingGenerator(EmbeddingGenerator):
    def generate(self, post: Post) -> PostEmbedding:
        return PostEmbedding(
            post_id=post.id,
            embedding_model="fake",
            dimensions=2,
            vector=[1.0, 2.0],
            created_at=post.created_at,
            updated_at=post.updated_at,
        )


@pytest.fixture
def mock_embedding_generator() -> EmbeddingGenerator:
    return MockEmbeddingGenerator()


####################################################################################
# Post Management
@pytest.fixture
def unit_of_work(in_memory_db_connection) -> UnitOfWork:
    return SqliteUnitOfWork(in_memory_db_connection)
