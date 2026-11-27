from __future__ import annotations

import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.use_case.linkedin_ingestion.model import (
    CsvImporterPrepareResult,
)


def write_temp_file(data: bytes | str, suffix: str) -> Path:
    mode = "wb" if isinstance(data, bytes) else "w"
    encoding = None if isinstance(data, bytes) else "utf-8"
    with tempfile.NamedTemporaryFile(
        delete=False, suffix=suffix, mode=mode, encoding=encoding
    ) as tmp:
        tmp.write(data)
        return Path(tmp.name)


def save_posts(ctx: AppContext, posts: list[Post]) -> None:
    for post in posts:
        ctx.post_store_manager.save_post(post)


@dataclass
class ImportState:
    prepared: CsvImporterPrepareResult | None = None
    selected_indices: set[int] = field(default_factory=set)
    temp_file: Path | None = None

    def set_temp_file(self, path: Path) -> None:
        self.cleanup_temp_file()
        self.temp_file = path

    def cleanup_temp_file(self) -> None:
        if self.temp_file and self.temp_file.exists():
            self.temp_file.unlink(missing_ok=True)
        self.temp_file = None

    def set_prepared(self, res: CsvImporterPrepareResult) -> None:
        self.prepared = res
        self.selected_indices = set(range(len(res.posts)))

    def toggle(self, idx: int, selected: bool) -> None:
        if selected:
            self.selected_indices.add(idx)
        else:
            self.selected_indices.discard(idx)

    def select_all(self) -> None:
        if self.prepared is None:
            return
        self.selected_indices = set(range(len(self.prepared.posts)))

    def select_none(self) -> None:
        self.selected_indices.clear()

    def selected_posts(self) -> list[Post]:
        if self.prepared is None:
            return []
        return [
            post
            for idx, post in enumerate(self.prepared.posts)
            if idx in self.selected_indices
        ]

    def reset(self) -> None:
        self.cleanup_temp_file()
        self.prepared = None
        self.selected_indices.clear()
