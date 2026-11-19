import sqlite3
from types import TracebackType
from typing import Self

from linkedin_idea_to_post.use_case.post_management.post_write_management_service import (
    UnitOfWork,
)


class SqliteUnitOfWork(UnitOfWork):
    def __init__(self, db_connection: sqlite3.Connection) -> None:
        self._conn = db_connection

    def __enter__(self) -> Self:
        self._conn.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool | None:
        return self._conn.__exit__(exc_type, exc_val, exc_tb)
