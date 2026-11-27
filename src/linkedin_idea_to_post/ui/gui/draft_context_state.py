from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal
from uuid import UUID

from linkedin_idea_to_post.domain.drafting import (
    DraftContext,
    KnowledgeSelection,
    KnowledgeStance,
    VoiceSelection,
    VoiceTuning,
)
from linkedin_idea_to_post.domain.post import Post

MAX_SEARCH = 15
Role = Literal["voice", "knowledge"]
Source = Literal["auto", "manual"]


@dataclass
class ContextItem:
    post: Post
    role: Role
    source: Source
    selected: bool
    tuning: VoiceTuning = VoiceTuning.MATCH_STYLE
    stance: KnowledgeStance = KnowledgeStance.NEUTRAL


@dataclass
class DraftContextState:
    voice_limit: int
    knowledge_limit: int
    context: DraftContext = field(default_factory=DraftContext)
    voice: list[ContextItem] = field(default_factory=list)
    knowledge: list[ContextItem] = field(default_factory=list)

    def items_for(self, role: Role) -> list[ContextItem]:
        return self.voice if role == "voice" else self.knowledge

    def set_items(self, role: Role, items: list[ContextItem]) -> None:
        if role == "voice":
            self.voice = items
        else:
            self.knowledge = items

    def limit_for(self, role: Role) -> int:
        return self.voice_limit if role == "voice" else self.knowledge_limit

    def selected_count(self, role: Role) -> int:
        return sum(1 for item in self.items_for(role) if item.selected)

    def toggle_selection(self, item: ContextItem, checked: bool) -> bool:
        if item.selected == checked:
            return True
        if checked and self.selected_count(item.role) >= self.limit_for(item.role):
            return False
        item.selected = checked
        return True

    def remove_item(self, item: ContextItem) -> None:
        self.set_items(
            item.role, [x for x in self.items_for(item.role) if x is not item]
        )

    def add_manual(self, post: Post, role: Role) -> bool:
        self.context.relevant_posts[post.id] = post
        items = self.items_for(role)
        existing = next((x for x in items if x.post.id == post.id), None)
        can_select = self.selected_count(role) < self.limit_for(role)
        if existing is not None:
            existing.source = "manual"
            if not existing.selected and can_select:
                existing.selected = True
            return existing.selected
        items.append(
            ContextItem(post=post, role=role, source="manual", selected=can_select)
        )
        return can_select

    def merge_auto(self, draft_ctx: DraftContext) -> None:
        self.context = draft_ctx
        role_selections: tuple[
            tuple[Role, list[VoiceSelection] | list[KnowledgeSelection]], ...
        ] = (
            ("voice", draft_ctx.voice_selections),
            ("knowledge", draft_ctx.knowledge_selections),
        )
        for role, selections in role_selections:
            manual = [x for x in self.items_for(role) if x.source == "manual"]
            manual_ids = {x.post.id for x in manual}
            slots = max(0, self.limit_for(role) - sum(1 for x in manual if x.selected))
            auto: list[ContextItem] = []
            for sel in selections:
                if sel.post_id in manual_ids:
                    continue
                post = draft_ctx.relevant_posts.get(sel.post_id)
                if post is None:
                    continue
                tuning = (
                    sel.tuning
                    if isinstance(sel, VoiceSelection)
                    else VoiceTuning.MATCH_STYLE
                )
                stance = (
                    sel.stance
                    if isinstance(sel, KnowledgeSelection)
                    else KnowledgeStance.NEUTRAL
                )
                auto.append(
                    ContextItem(
                        post=post,
                        role=role,
                        source="auto",
                        selected=len(auto) < slots,
                        tuning=tuning,
                        stance=stance,
                    )
                )
            self.set_items(role, manual + auto)

    def build_draft_context(self, target_word_count: int) -> DraftContext:
        relevant: dict[UUID, Post] = dict(self.context.relevant_posts)
        for item in self.voice + self.knowledge:
            relevant[item.post.id] = item.post
        return DraftContext(
            relevant_posts=relevant,
            voice_selections=[
                VoiceSelection(post_id=x.post.id, tuning=x.tuning)
                for x in self.voice
                if x.selected
            ][: self.voice_limit],
            knowledge_selections=[
                KnowledgeSelection(post_id=x.post.id, stance=x.stance)
                for x in self.knowledge
                if x.selected
            ][: self.knowledge_limit],
            target_word_count=target_word_count,
        )

    def restore_context(self, draft_ctx: DraftContext) -> None:
        self.context = draft_ctx.model_copy(deep=True)
        self.voice = [
            ContextItem(
                post=self.context.relevant_posts[sel.post_id],
                role="voice",
                source="manual",
                selected=True,
                tuning=sel.tuning,
            )
            for sel in self.context.voice_selections
            if sel.post_id in self.context.relevant_posts
        ]
        self.knowledge = [
            ContextItem(
                post=self.context.relevant_posts[sel.post_id],
                role="knowledge",
                source="manual",
                selected=True,
                stance=sel.stance,
            )
            for sel in self.context.knowledge_selections
            if sel.post_id in self.context.relevant_posts
        ]


def filter_search_matches(posts: list[Post], query: str) -> list[Post]:
    needle = query.strip().lower()
    if not needle:
        return []
    return [
        p
        for p in posts
        if needle in p.body.lower() or any(needle in tag.lower() for tag in p.hashtags)
    ][:MAX_SEARCH]
