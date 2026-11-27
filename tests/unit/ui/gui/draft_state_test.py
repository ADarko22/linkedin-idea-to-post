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
from linkedin_idea_to_post.ui.gui.draft_state import (
    DEFAULT_MAX_HISTORY,
    DraftTabState,
    filter_search_matches,
)


def _make_post(
    idx: int, *, body: str = "Post body", hashtags: set[str] | None = None
) -> Post:
    return Post(
        id=UUID(int=idx),
        url=None,
        body=body,
        hashtags=hashtags if hashtags is not None else set(),
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


def test_draft_state_manual_add_and_limits() -> None:
    state = DraftTabState(voice_limit=1, knowledge_limit=1)
    p1, p2 = _make_post(1), _make_post(2)

    assert state.add_manual(p1, "voice") is True
    assert state.selected_count("voice") == 1
    assert state.add_manual(p2, "voice") is False
    assert state.selected_count("voice") == 1
    assert len(state.voice) == 2

    # Cannot toggle second item while limit is reached
    assert state.toggle_selection(state.voice[1], True) is False
    # Removing first frees a slot
    state.remove_item(state.voice[0])
    assert state.toggle_selection(state.voice[0], True) is True


def test_draft_state_merge_auto_preserves_manual_and_fills_slots() -> None:
    state = DraftTabState(voice_limit=2, knowledge_limit=1)
    manual_post = _make_post(1, body="Manual")
    auto_1 = _make_post(2, body="Auto 1")
    auto_2 = _make_post(3, body="Auto 2")

    state.add_manual(manual_post, "voice")
    ctx = DraftContext(
        relevant_posts={
            manual_post.id: manual_post,
            auto_1.id: auto_1,
            auto_2.id: auto_2,
        },
        voice_selections=[
            VoiceSelection(post_id=manual_post.id, tuning=VoiceTuning.PUNCHY_HOOK_ONLY),
            VoiceSelection(post_id=auto_1.id, tuning=VoiceTuning.MORE_CONCISE),
            VoiceSelection(post_id=auto_2.id, tuning=VoiceTuning.MATCH_STYLE),
        ],
        knowledge_selections=[
            KnowledgeSelection(post_id=auto_1.id, stance=KnowledgeStance.SUPPORTIVE),
        ],
    )

    state.merge_auto(ctx)
    assert [x.post.id for x in state.voice] == [manual_post.id, auto_1.id, auto_2.id]
    assert [x.selected for x in state.voice] == [True, True, False]
    assert state.voice[1].tuning == VoiceTuning.MORE_CONCISE
    assert len(state.knowledge) == 1
    assert state.knowledge[0].stance == KnowledgeStance.SUPPORTIVE

    built = state.build_draft_context(target_word_count=250)
    assert built.target_word_count == 250
    assert [s.post_id for s in built.voice_selections] == [manual_post.id, auto_1.id]


def test_draft_state_history_and_save_preparation() -> None:
    state = DraftTabState(voice_limit=2, knowledge_limit=2)
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

    # Selecting index 0 (Draft 1) restores its saved context
    entry_0 = state.select_history(0, "Edited latest")
    assert entry_0.text == "Draft 1"
    assert state.history[-1].text == "Edited latest"
    assert entry_0.context.target_word_count == 101
    assert [x.post.id for x in state.voice] == [p1.id]
    assert state.voice[0].tuning == VoiceTuning.MORE_CONCISE
    assert [x.post.id for x in state.knowledge] == [p2.id]
    assert state.knowledge[0].stance == KnowledgeStance.CONTRARY

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


def test_draft_state_custom_history_limit() -> None:
    state = DraftTabState(voice_limit=1, knowledge_limit=1, max_history=3)
    for i in range(4):
        state.record_draft(
            _make_draft(f"Draft {i}"), DraftContext(target_word_count=200)
        )

    assert [e.draft.generated_content for e in state.history] == [
        "Draft 1",
        "Draft 2",
        "Draft 3",
    ]


def test_filter_search_matches() -> None:
    p1 = _make_post(1, body="Testing nicegui", hashtags={"ui"})
    p2 = _make_post(2, body="Other", hashtags={"python"})
    assert filter_search_matches([p1, p2], "python") == [p2]
    assert filter_search_matches([p1, p2], "") == []
