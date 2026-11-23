from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from functools import cached_property

from linkedin_idea_to_post.adapters.ai_workflow.crewai_draft_writer import (
    CrewaiDraftWriter,
)
from linkedin_idea_to_post.adapters.ai_workflow.llm_factory import build_llm
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
from linkedin_idea_to_post.config import AppConfig, ensure_app_dirs
from linkedin_idea_to_post.use_case.drafting.draft_context_service import (
    DraftContextService,
)
from linkedin_idea_to_post.use_case.drafting.draft_service import DraftService
from linkedin_idea_to_post.use_case.linkedin_ingestion.csv_importer import CsvImporter
from linkedin_idea_to_post.use_case.linkedin_ingestion.csv_parser import CsvParser
from linkedin_idea_to_post.use_case.post_management.post_post_management_service import (
    PostStoreManagementService,
)

_CACHED_SERVICE_ATTRS: tuple[str, ...] = (
    "unit_of_work",
    "post_storage",
    "embedding_storage",
    "retriever",
    "embedding_generator",
    "post_store_manager",
    "draft_context_service",
    "draft_service",
    "csv_importer",
)


@dataclass
class AppContext:
    """Resolved application services and adapters shared across CLI, GUI, and MCP."""

    config: AppConfig
    offline: bool = False
    _db_connection: sqlite3.Connection | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        ensure_app_dirs(self.config)

    @property
    def db_connection(self) -> sqlite3.Connection:
        # Note: for a long-lived server with concurrent requests (i.e. mcp) should become a per-thread connection
        if self._db_connection is None:
            self._db_connection = create_sqlite_connection(settings=self.config.storage)
        return self._db_connection

    @cached_property
    def unit_of_work(self) -> SqliteUnitOfWork:
        return SqliteUnitOfWork(db_connection=self.db_connection)

    @cached_property
    def post_storage(self) -> SqlitePostStorage:
        return SqlitePostStorage(db_connection=self.db_connection)

    @cached_property
    def embedding_storage(self) -> SQLitePostEmbeddingStorage:
        return SQLitePostEmbeddingStorage(db_connection=self.db_connection)

    @cached_property
    def retriever(self) -> SqlitePostRetriever:
        return SqlitePostRetriever(db_connection=self.db_connection)

    @cached_property
    def embedding_generator(self) -> PyTorchEmbeddingGenerator:
        return PyTorchEmbeddingGenerator(self.config.embedding)

    @cached_property
    def post_store_manager(self) -> PostStoreManagementService:
        return PostStoreManagementService(
            embedding_generator=self.embedding_generator,
            unit_of_work=self.unit_of_work,
            post_storage=self.post_storage,
            embedding_storage=self.embedding_storage,
        )

    @cached_property
    def draft_context_service(self) -> DraftContextService:
        return DraftContextService(
            settings=self.config.drafting,
            retriever=self.retriever,
            embedding_generator=self.embedding_generator,
        )

    @cached_property
    def draft_service(self) -> DraftService:
        llm = build_llm(llm_settings=self.config.writer_llm, offline=self.offline)
        writer = CrewaiDraftWriter(llm=llm)
        return DraftService(
            writer=writer,
        )

    @cached_property
    def csv_importer(self) -> CsvImporter:
        return CsvImporter(
            parser=CsvParser(),
            post_store_manager=self.post_store_manager,
        )

    def _invalidate_cached_services(self) -> None:
        for attr in _CACHED_SERVICE_ATTRS:
            self.__dict__.pop(attr, None)

    def close(self) -> None:
        if self._db_connection is not None:
            try:
                self._db_connection.close()
            except sqlite3.ProgrammingError:
                # Connection belongs to another thread; drop reference so GC/owner handles cleanup
                pass
            finally:
                self._db_connection = None
        self._invalidate_cached_services()

    def reload_config(self, new_config: AppConfig) -> None:
        if self._db_connection is not None:
            try:
                self._db_connection.close()
            except sqlite3.ProgrammingError:
                pass
            finally:
                self._db_connection = None
        self._invalidate_cached_services()
        ensure_app_dirs(new_config)
        self.config = new_config


def build_app_context(*, offline: bool = False) -> AppContext:
    """Load configuration and construct the application context."""
    config = AppConfig()
    return AppContext(config=config, offline=offline)
