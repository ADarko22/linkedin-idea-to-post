from __future__ import annotations

from dataclasses import dataclass, field

from linkedin_idea_to_post.domain.drafting import Draft, DraftContext
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import post_from_draft

DEFAULT_MAX_HISTORY = 10
DEFAULT_TARGET_WORDS = 220
MIN_TARGET_WORDS = 50
MAX_TARGET_WORDS = 1500
WORD_COUNT_STEP = 25


@dataclass
class DraftEntry:
    draft: Draft
    context: DraftContext
    text: str
    saved: str | None = None


@dataclass
class DraftHistoryState:
    max_history: int = DEFAULT_MAX_HISTORY
    history: list[DraftEntry] = field(default_factory=list)
    active: int = -1

    def sync_active_text(self, text: str) -> None:
        if 0 <= self.active < len(self.history):
            self.history[self.active].text = text

    def record_draft(self, draft: Draft, context: DraftContext) -> None:
        used_ctx = context.model_copy(deep=True)
        self.history.append(
            DraftEntry(
                draft=draft,
                context=used_ctx,
                text=draft.generated_content,
            )
        )
        limit = max(1, self.max_history)
        if len(self.history) > limit:
            self.history = self.history[-limit:]
        self.active = len(self.history) - 1

    def select_history(self, idx: int, current_editor_text: str) -> DraftEntry:
        self.sync_active_text(current_editor_text)
        self.active = idx
        return self.history[idx]

    def active_status_text(self, current_editor_text: str) -> str:
        if not (0 <= self.active < len(self.history)):
            return ""
        entry = self.history[self.active]
        edited = current_editor_text.strip() != entry.draft.generated_content.strip()
        origin = PostOrigin.AI_EDIT.value if edited else PostOrigin.AI_DRAFT.value
        saved = f" · {entry.saved}" if entry.saved else ""
        return f"#{self.active + 1}/{len(self.history)} · {origin}{saved}"

    def prepare_post_for_save(
        self, current_editor_text: str, status: PostStatus
    ) -> tuple[Post, str] | None:
        if not (0 <= self.active < len(self.history)):
            return None
        txt = current_editor_text.strip()
        if not txt:
            raise ValueError("Draft cannot be empty.")
        entry = self.history[self.active]
        edited = txt != entry.draft.generated_content.strip()
        origin = PostOrigin.AI_EDIT if edited else PostOrigin.AI_DRAFT
        post = post_from_draft(
            entry.draft,
            body_override=txt if edited else None,
            origin=origin,
            status=status,
        )
        saved_label = f"{origin.value} · {status.value}"
        return post, saved_label

    def mark_active_saved(self, saved_label: str) -> None:
        if 0 <= self.active < len(self.history):
            self.history[self.active].saved = saved_label
