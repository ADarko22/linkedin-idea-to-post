from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from linkedin_idea_to_post.domain.drafting import (
    Draft,
    DraftContext,
    KnowledgeSelection,
    KnowledgeStance,
    VoiceSelection,
    VoiceTuning,
)
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.ui.gui.draft_history_state import (
    DEFAULT_MAX_HISTORY,
    DraftHistoryState,
)


def _make_post(idx: int, *, body: str = "Post body") -> Post:
    return Post(
        id=UUID(int=idx),
        url=None,
        body=body,
        hashtags=set(),
        origin=PostOrigin.HUMAN,
        status=PostStatus.PUBLISHED,
        created_at=datetime(2026, 3, 15, 14, 30, tzinfo=UTC),
        updated_at=datetime(2026, 3, 15, 14, 30, tzinfo=UTC),
    )


def _make_draft(content: str = "Generated draft") -> Draft:
    return Draft(
        idea="My idea",
        generated_content=content,
    )


def test_draft_history_state_and_save_preparation() -> None:
    state = DraftHistoryState()
    assert state.max_history == DEFAULT_MAX_HISTORY

    p1 = _make_post(1, body="Voice 1")
    p2 = _make_post(2, body="Knowledge 2")
    for i in range(DEFAULT_MAX_HISTORY + 1):
        ctx = DraftContext(
            relevant_posts={p1.id: p1, p2.id: p2} if i == 1 else {},
            voice_selections=(
                [VoiceSelection(post_id=p1.id, tuning=VoiceTuning.MORE_CONCISE)]
                if i == 1
                else []
            ),
            knowledge_selections=(
                [KnowledgeSelection(post_id=p2.id, stance=KnowledgeStance.CONTRARY)]
                if i == 1
                else []
            ),
            target_word_count=100 + i,
        )
        state.record_draft(_make_draft(f"Draft {i}"), ctx)

    # 11th draft drops the 1st (Draft 0)
    assert len(state.history) == DEFAULT_MAX_HISTORY
    assert state.history[0].draft.generated_content == "Draft 1"
    assert state.active == DEFAULT_MAX_HISTORY - 1

    # Selecting index 0 (Draft 1) preserves active edits and returns its saved context
    entry_0 = state.select_history(0, "Edited latest")
    assert entry_0.text == "Draft 1"
    assert state.history[-1].text == "Edited latest"
    assert entry_0.context.target_word_count == 101

    assert "AI_DRAFT" in state.active_status_text("Draft 1")
    assert "AI_EDIT" in state.active_status_text("Modified Draft 1")

    prepared = state.prepare_post_for_save("Modified Draft 1", PostStatus.DRAFT)
    assert prepared is not None
    post, label = prepared
    assert post.origin == PostOrigin.AI_EDIT
    assert post.status == PostStatus.DRAFT
    assert label == "AI_EDIT · DRAFT"

    state.mark_active_saved(label)
    assert label in state.active_status_text("Modified Draft 1")

    with pytest.raises(ValueError, match="cannot be empty"):
        state.prepare_post_for_save("   ", PostStatus.DRAFT)


def test_draft_history_state_custom_limit() -> None:
    state = DraftHistoryState(max_history=3)
    for i in range(4):
        state.record_draft(
            _make_draft(f"Draft {i}"), DraftContext(target_word_count=200)
        )

    assert [e.draft.generated_content for e in state.history] == [
        "Draft 1",
        "Draft 2",
        "Draft 3",
    ]
