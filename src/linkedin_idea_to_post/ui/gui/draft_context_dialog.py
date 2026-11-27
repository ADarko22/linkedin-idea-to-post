from __future__ import annotations

from collections.abc import Callable

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.drafting import KnowledgeStance, VoiceTuning
from linkedin_idea_to_post.domain.post import Post
from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.ui.gui import components, templates, theme
from linkedin_idea_to_post.ui.gui.draft_state import (
    MAX_SEARCH,
    ContextItem,
    DraftTabState,
    Role,
    filter_search_matches,
)
from linkedin_idea_to_post.ui.gui.helpers import run_blocking


class DraftContextDialog:
    """Modal for inspecting, searching, and tuning Voice & Knowledge context."""

    def __init__(
        self,
        ctx: AppContext,
        state: DraftTabState,
        *,
        on_change: Callable[[], None],
    ) -> None:
        self._ctx = ctx
        self._state = state
        self._on_change = on_change
        self._reader = components.PostReaderModal(
            title="Post Content",
            width_classes="max-w-2xl",
            blur="blur(3px)",
            body_height="h-72",
        )

        with templates.modal_dialog("max-w-5xl") as (dialog, _):
            self._dialog = dialog
            with theme.row_between("gap-2 flex-wrap"):
                with theme.row_gap_2():
                    ui.icon("tune", size="md", color="primary")
                    theme.section_title("Context & Tuning")
                with theme.row_gap_2():
                    self._v_badge = theme.badge(
                        f"Voice 0/{state.voice_limit}", color="blue-grey"
                    )
                    self._k_badge = theme.badge(
                        f"Knowledge 0/{state.knowledge_limit}", color="blue-grey"
                    )
                    theme.positive_button(
                        "Apply & Close",
                        icon="check_circle",
                        on_click=dialog.close,
                        unelevated=True,
                    )

            self._search_input = theme.outlined_input(
                f"Search archive (up to {MAX_SEARCH})",
                placeholder="Keywords or #hashtags...",
            )
            with self._search_input.add_slot("prepend"):
                ui.icon("search", color="primary")

            self._search_panel, self._search_info, self._search_box = (
                templates.search_results_panel()
            )

            with (
                theme.scroll_box("h-[72vh]", "min-h-80 overflow-x-hidden"),
                theme.stack("gap-3", "overflow-x-hidden"),
            ):
                theme.section_title("Voices", small=True)
                self._voices_box = theme.stack()
                ui.separator()
                theme.section_title("Knowledge", small=True)
                self._knowledge_box = theme.stack()

        self._search_input.on_value_change(self._on_search)
        self._search_input.on("focus", self._on_search)
        self.refresh()

    def open(self) -> None:
        self._dialog.open()

    def refresh(self) -> None:
        self._render_role("voice")
        self._render_role("knowledge")
        self._sync_badges()

    def _sync_badges(self) -> None:
        vs = self._state.selected_count("voice")
        ks = self._state.selected_count("knowledge")
        self._v_badge.set_text(f"Voice {vs}/{self._state.voice_limit}")
        self._k_badge.set_text(f"Knowledge {ks}/{self._state.knowledge_limit}")
        theme.set_badge_color(
            self._v_badge, "warning" if vs >= self._state.voice_limit else "blue-grey"
        )
        theme.set_badge_color(
            self._k_badge,
            "warning" if ks >= self._state.knowledge_limit else "blue-grey",
        )
        self._on_change()

    def _on_toggle_item(
        self, item: ContextItem, checked: bool, cb: ui.checkbox
    ) -> None:
        if not self._state.toggle_selection(item, checked):
            ui.notify(
                f"Limit: max {self._state.limit_for(item.role)} {item.role}.",
                type="warning",
            )
            cb.set_value(False)
            return
        self._sync_badges()

    def _on_remove_item(self, item: ContextItem) -> None:
        self._state.remove_item(item)
        self._render_role(item.role)
        self._sync_badges()

    def _render_role(self, role: Role) -> None:
        box = self._voices_box if role == "voice" else self._knowledge_box
        items = self._state.items_for(role)
        box.clear()
        with box:
            if not items:
                theme.muted_caption(f"No {role} posts.", "text-grey")
                return
            for item in items:
                manual = item.source == "manual"

                def _toggle(
                    checked: bool, cb: ui.checkbox, target: ContextItem = item
                ) -> None:
                    self._on_toggle_item(target, checked, cb)

                def _trailing(
                    target: ContextItem = item, item_role: Role = role
                ) -> None:
                    opts = (
                        [t.value for t in VoiceTuning]
                        if item_role == "voice"
                        else [s.value for s in KnowledgeStance]
                    )
                    val = (
                        target.tuning.value
                        if item_role == "voice"
                        else target.stance.value
                    )
                    sel = theme.outlined_select(
                        opts,
                        value=val,
                        label="Tuning" if item_role == "voice" else "Stance",
                        extra_classes="w-44 shrink-0",
                    )

                    def _on_enum_change(
                        e: object, t: ContextItem = target, r: Role = item_role
                    ) -> None:
                        raw = str(getattr(e, "value", ""))
                        if r == "voice":
                            t.tuning = VoiceTuning(raw)
                        else:
                            t.stance = KnowledgeStance(raw)

                    sel.on_value_change(_on_enum_change)
                    theme.icon_button(
                        "delete",
                        color="negative",
                        tooltip="Remove",
                        extra_classes="shrink-0 mt-1",
                        on_click=lambda _, t=target: self._on_remove_item(t),
                    )

                components.expandable_post_card(
                    item.post,
                    selected=item.selected,
                    on_toggle=_toggle,
                    badge_text="Added" if manual else "Suggested",
                    badge_color="teal" if manual else "grey-7",
                    accent="manual" if manual else "suggested",
                    trailing_controls=_trailing,
                )

    def _add_manual(self, post: Post, role: Role) -> None:
        selected = self._state.add_manual(post, role)
        self._render_role(role)
        self._sync_badges()
        ui.notify(
            f"Added to {role}" + ("" if selected else " (unchecked: limit reached)"),
            type="positive" if selected else "warning",
        )

    def _add_and_close_reader(self, post: Post, role: Role) -> None:
        self._add_manual(post, role)
        self._reader.close()

    def _open_reader(self, post: Post) -> None:
        def _render_footer(target: Post) -> None:
            theme.action_button(
                "+ Voice",
                icon="record_voice_over",
                color="primary",
                unelevated=True,
                on_click=lambda _, p=target: self._add_and_close_reader(p, "voice"),
            )
            theme.action_button(
                "+ Knowledge",
                icon="menu_book",
                color="teal",
                unelevated=True,
                on_click=lambda _, p=target: self._add_and_close_reader(p, "knowledge"),
            )

        self._reader.open(post, render_footer=_render_footer)

    async def _on_search(self) -> None:
        query = (self._search_input.value or "").strip()
        if not query:
            self._search_panel.set_visibility(False)
            self._search_box.clear()
            return

        posts = await run_blocking(
            lambda: self._ctx.post_storage.get_all(
                PostGetQuery(
                    limit=self._ctx.config.storage.post_get_all_page_size, page=1
                )
            )
        )
        matches = filter_search_matches(posts, query)

        self._search_box.clear()
        self._search_panel.set_visibility(True)
        self._search_info.set_text(
            f"{len(matches)} result(s) (max {MAX_SEARCH}) — click to open preview"
            if matches
            else "No matching posts."
        )
        with self._search_box:
            for post in matches:
                components.search_result_card(
                    post,
                    on_preview=self._open_reader,
                    on_add_voice=lambda p: self._add_manual(p, "voice"),
                    on_add_knowledge=lambda p: self._add_manual(p, "knowledge"),
                )
