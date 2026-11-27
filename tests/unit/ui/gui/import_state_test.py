from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock
from uuid import UUID

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui.import_state import (
    ImportState,
    save_posts,
    write_temp_file,
)
from linkedin_idea_to_post.use_case.linkedin_ingestion.model import (
    CsvImporterPrepareResult,
)


def _make_post(idx: int) -> Post:
    return Post(
        id=UUID(int=idx),
        url=None,
        body=f"Post body {idx}",
        hashtags=set(),
        origin=PostOrigin.HUMAN,
        status=PostStatus.PUBLISHED,
        created_at=datetime(2026, 3, 15, 14, 30, tzinfo=UTC),
        updated_at=datetime(2026, 3, 15, 14, 30, tzinfo=UTC),
    )


def test_import_state_selection_and_reset(tmp_path: Path) -> None:
    posts = [_make_post(1), _make_post(2), _make_post(3)]
    res = CsvImporterPrepareResult(posts=posts, parsing_errors=[], mapping_errors=[])

    state = ImportState()
    state.set_prepared(res)
    assert state.selected_indices == {0, 1, 2}
    assert state.selected_posts() == posts

    state.toggle(1, False)
    assert state.selected_posts() == [posts[0], posts[2]]

    state.select_none()
    assert state.selected_posts() == []

    state.select_all()
    assert state.selected_posts() == posts

    tmp_file = write_temp_file("col1\nval1\n", ".csv")
    state.set_temp_file(tmp_file)
    assert tmp_file.exists()

    state.reset()
    assert not tmp_file.exists()
    assert state.prepared is None
    assert state.selected_posts() == []


def test_save_posts_delegates_to_post_store_manager() -> None:
    ctx = MagicMock()
    posts = [_make_post(1), _make_post(2)]

    save_posts(ctx, posts)

    assert ctx.post_store_manager.save_post.call_count == 2
