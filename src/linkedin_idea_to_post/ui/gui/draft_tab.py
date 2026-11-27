from __future__ import annotations

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.drafting import (
    Draft,
    DraftGenerationError,
    DraftRequest,
    KnowledgeStance,
    VoiceTuning,
)
from linkedin_idea_to_post.domain.post import Post, PostStatus
from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.ui.gui import components, templates, theme
from linkedin_idea_to_post.ui.gui.draft_state import (
    DEFAULT_TARGET_WORDS,
    MAX_SEARCH,
    MAX_TARGET_WORDS,
    MIN_TARGET_WORDS,
    WORD_COUNT_STEP,
    ContextItem,
    DraftTabState,
    Role,
    filter_search_matches,
)
from linkedin_idea_to_post.ui.gui.helpers import (
    format_hashtags,
    post_short_preview,
    run_blocking,
)


def build_draft_tab(ctx: AppContext) -> None:
    state = DraftTabState(
        voice_limit=int(ctx.config.drafting.voice_examples_count),
        knowledge_limit=int(ctx.config.drafting.knowledge_examples_count),
        max_history=int(ctx.config.drafting.draft_history_limit),
    )

    with templates.modal_dialog("max-w-2xl", blur="blur(3px)") as (read_dialog, _):
        templates.modal_header("Post Content", read_dialog.close)
        read_tags = theme.tags_label("")
        with theme.scroll_box("h-72", "overflow-x-hidden"):
            read_body = theme.post_body_label("")
        read_actions = ui.row().classes("w-full justify-end gap-2")

    with templates.modal_dialog("max-w-5xl") as (ctx_dialog, _):
        with theme.row_between("gap-2 flex-wrap"):
            with theme.row_gap_2():
                ui.icon("tune", size="md", color="primary")
                theme.section_title("Context & Tuning")
            with theme.row_gap_2():
                v_badge = ui.badge(f"Voice 0/{state.voice_limit}", color="blue-grey")
                k_badge = ui.badge(
                    f"Knowledge 0/{state.knowledge_limit}", color="blue-grey"
                )
                theme.positive_button(
                    "Apply & Close",
                    icon="check_circle",
                    on_click=ctx_dialog.close,
                    unelevated=True,
                )

        search_input = theme.outlined_input(
            f"Search archive (up to {MAX_SEARCH})",
            placeholder="Keywords or #hashtags...",
        )
        with search_input.add_slot("prepend"):
            ui.icon("search", color="primary")

        search_panel = ui.column().classes(
            "w-full border rounded bg-grey-1 q-pa-xs gap-1"
        )
        search_panel.set_visibility(False)
        with search_panel:
            search_info = theme.muted_caption("", "text-grey-8 px-1")
            search_box = ui.column().classes(
                "w-full max-h-60 overflow-y-auto gap-1.5 pr-1"
            )

        with (
            theme.scroll_box("h-[72vh]", "min-h-80 overflow-x-hidden"),
            ui.column().classes("w-full gap-3 overflow-x-hidden"),
        ):
            theme.section_title("Voices", small=True)
            voices_box = ui.column().classes("w-full gap-2")
            ui.separator()
            theme.section_title("Knowledge", small=True)
            knowledge_box = ui.column().classes("w-full gap-2")

    with (
        templates.narrow_page("overflow-x-hidden"),
        templates.card_panel("overflow-x-hidden"),
    ):
        with theme.row_between("gap-2 flex-wrap"):
            theme.section_title("Idea & Draft")
            with theme.row_gap_2():
                status_lbl = theme.muted_caption("")
                ctx_chip = ui.badge(
                    f"Context: 0/{state.voice_limit} V · 0/{state.knowledge_limit} K",
                    color="blue-grey",
                ).classes("cursor-pointer")
                ctx_chip.on("click", ctx_dialog.open)
                theme.flat_button(
                    icon="tune",
                    on_click=ctx_dialog.open,
                    extra_props="round size=sm color=primary",
                ).tooltip("Tune Context")

        idea_area = theme.outlined_textarea(
            "Idea", placeholder="Write your idea or angle...", rows=3
        )

        with theme.row_between("flex-wrap"):
            words_input = (
                ui.number(
                    "Target words",
                    value=DEFAULT_TARGET_WORDS,
                    min=MIN_TARGET_WORDS,
                    max=MAX_TARGET_WORDS,
                    step=WORD_COUNT_STEP,
                )
                .props(theme.PROPS_OUTLINED_DENSE)
                .classes("w-36")
            )
            with theme.row_gap_2("flex-wrap"):
                build_btn = theme.primary_button("Build Context", icon="auto_awesome")
                gen_btn = ui.button(
                    "Generate Draft", icon="edit_note", color="secondary"
                )

        history_row = theme.row_gap_2("w-full flex-wrap")
        history_row.set_visibility(False)
        ui.separator()

        editor = theme.outlined_textarea(
            "Draft", placeholder="Generated draft appears here...", rows=10
        )

        with theme.row_between("gap-2 flex-wrap"):
            use_idea_btn = theme.outline_button("Use Draft as Idea", icon="north_west")
            use_idea_btn.set_enabled(False)
            with theme.row_gap_2("flex-wrap"):
                save_draft_btn = theme.outline_button(
                    "Save as DRAFT", icon="save", dense=False
                )
                save_pub_btn = theme.positive_button(
                    "Save as PUBLISHED", icon="publish"
                )
                save_draft_btn.set_enabled(False)
                save_pub_btn.set_enabled(False)

    def sync_badges() -> None:
        vs = state.selected_count("voice")
        ks = state.selected_count("knowledge")
        v_badge.set_text(f"Voice {vs}/{state.voice_limit}")
        k_badge.set_text(f"Knowledge {ks}/{state.knowledge_limit}")
        v_badge.props(f"color={'warning' if vs >= state.voice_limit else 'blue-grey'}")
        k_badge.props(
            f"color={'warning' if ks >= state.knowledge_limit else 'blue-grey'}"
        )
        ctx_chip.set_text(
            f"Context: {vs}/{state.voice_limit} V · {ks}/{state.knowledge_limit} K"
        )
        ctx_chip.props(f"color={'primary' if (vs + ks) else 'blue-grey'}")

    def sync_status() -> None:
        status_lbl.set_text(state.active_status_text(editor.value or ""))

    def render_history() -> None:
        history_row.clear()
        if not state.history:
            history_row.set_visibility(False)
            return
        history_row.set_visibility(True)
        with history_row:
            theme.muted_caption("History:", "q-mr-xs")
            for idx, entry in enumerate(state.history):
                active = idx == state.active
                lbl = f"#{idx + 1}" + (" ✓" if entry.saved else "")

                def pick(i: int = idx) -> None:
                    selected_entry = state.select_history(i, editor.value or "")
                    editor.set_value(selected_entry.text)
                    if selected_entry.context.target_word_count > 0:
                        words_input.set_value(selected_entry.context.target_word_count)
                    render_role("voice")
                    render_role("knowledge")
                    sync_badges()
                    render_history()
                    sync_status()

                btn = ui.button(
                    lbl, on_click=pick, color="primary" if active else None
                ).props(
                    theme.PROPS_UNELEVATED_DENSE
                    if active
                    else theme.PROPS_OUTLINE_DENSE
                )
                v_cnt = len(entry.context.voice_selections)
                k_cnt = len(entry.context.knowledge_selections)
                btn.tooltip(
                    f"Context: {v_cnt}V · {k_cnt}K · {entry.context.target_word_count}w"
                )

    def on_toggle_item(item: ContextItem, checked: bool, cb: ui.checkbox) -> None:
        if not state.toggle_selection(item, checked):
            ui.notify(
                f"Limit: max {state.limit_for(item.role)} {item.role}.",
                type="warning",
            )
            cb.set_value(False)
            return
        sync_badges()

    def on_remove_item(item: ContextItem) -> None:
        state.remove_item(item)
        render_role(item.role)
        sync_badges()

    def render_role(role: Role) -> None:
        box = voices_box if role == "voice" else knowledge_box
        items = state.items_for(role)
        box.clear()
        with box:
            if not items:
                ui.label(f"No {role} posts.").classes("text-caption text-grey")
                return
            for item in items:
                manual = item.source == "manual"
                accent = (
                    "border-l-4 border-teal-6 bg-teal-1"
                    if manual
                    else "border-l-4 border-grey-5"
                )

                def _toggle(
                    checked: bool, cb: ui.checkbox, target: ContextItem = item
                ) -> None:
                    on_toggle_item(target, checked, cb)

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
                    sel = (
                        ui.select(
                            opts,
                            value=val,
                            label="Tuning" if item_role == "voice" else "Stance",
                        )
                        .props(theme.PROPS_OUTLINED_DENSE)
                        .classes("w-44 shrink-0")
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
                    theme.flat_button(
                        icon="delete",
                        on_click=lambda _, t=target: on_remove_item(t),
                        extra_props="round size=sm color=negative",
                    ).tooltip("Remove").classes("shrink-0 mt-1")

                components.expandable_post_card(
                    item.post,
                    selected=item.selected,
                    on_toggle=_toggle,
                    badge_text="Added" if manual else "Suggested",
                    badge_color="teal" if manual else "grey-7",
                    card_classes=f"w-full q-pa-xs overflow-x-hidden {accent}",
                    trailing_controls=_trailing,
                )

    def add_manual(post: Post, role: Role) -> None:
        selected = state.add_manual(post, role)
        render_role(role)
        sync_badges()
        ui.notify(
            f"Added to {role}" + ("" if selected else " (unchecked: limit reached)"),
            type="positive" if selected else "warning",
        )

    def _add_and_close(post: Post, role: Role) -> None:
        add_manual(post, role)
        read_dialog.close()

    def open_reader(post: Post) -> None:
        tags = format_hashtags(post)
        read_tags.set_text(tags)
        read_tags.set_visibility(bool(tags))
        read_body.set_text(post.body)
        read_actions.clear()
        with read_actions:
            ui.button(
                "+ Voice",
                icon="record_voice_over",
                color="primary",
                on_click=lambda _, p=post: _add_and_close(p, "voice"),
            ).props(theme.PROPS_UNELEVATED_DENSE)
            ui.button(
                "+ Knowledge",
                icon="menu_book",
                color="teal",
                on_click=lambda _, p=post: _add_and_close(p, "knowledge"),
            ).props(theme.PROPS_UNELEVATED_DENSE)
        read_dialog.open()

    async def on_search() -> None:
        query = (search_input.value or "").strip()
        if not query:
            search_panel.set_visibility(False)
            search_box.clear()
            return

        posts = await run_blocking(
            lambda: ctx.post_storage.get_all(
                PostGetQuery(limit=ctx.config.storage.post_get_all_page_size, page=1)
            )
        )
        matches = filter_search_matches(posts, query)

        search_box.clear()
        search_panel.set_visibility(True)
        search_info.set_text(
            f"{len(matches)} result(s) (max {MAX_SEARCH}) — click to open preview"
            if matches
            else "No matching posts."
        )
        with search_box:
            for post in matches:
                with (
                    ui.card().classes(
                        "w-full shrink-0 q-px-sm q-py-xs bg-white overflow-visible"
                    ),
                    theme.row_between("gap-2 flex-wrap overflow-visible"),
                ):
                    preview = theme.post_preview_label(
                        post_short_preview(post),
                        "text-grey-10 cursor-pointer hover:text-primary whitespace-normal overflow-visible flex-1 min-w-[240px]",
                    )
                    preview.on("click", lambda _, p=post: open_reader(p))
                    with theme.row_gap_2("gap-1.5 shrink-0"):
                        ui.button(
                            "Voice",
                            icon="add_circle",
                            on_click=lambda _, p=post: add_manual(p, "voice"),
                        ).props("dense outline size=sm color=primary")
                        ui.button(
                            "Knowledge",
                            icon="add_circle",
                            on_click=lambda _, p=post: add_manual(p, "knowledge"),
                        ).props("dense outline size=sm color=teal")

    async def on_build() -> None:
        idea = (idea_area.value or "").strip()
        if not idea:
            ui.notify("Write an idea first.", type="warning")
            return

        async def _build() -> None:
            draft_ctx = await run_blocking(
                lambda: ctx.draft_context_service.create_context(
                    idea=idea,
                    target_word_count=int(words_input.value or DEFAULT_TARGET_WORDS),
                )
            )
            state.merge_auto(draft_ctx)
            render_role("voice")
            render_role("knowledge")
            sync_badges()
            ctx_dialog.open()

        await components.run_with_disabled([build_btn], _build)

    async def on_generate() -> None:
        idea = (idea_area.value or "").strip()
        if not idea:
            ui.notify("Write an idea first.", type="warning")
            return
        state.sync_active_text(editor.value or "")

        async def _generate() -> None:
            try:
                draft_ctx = state.build_draft_context(
                    int(words_input.value or DEFAULT_TARGET_WORDS)
                )
                draft: Draft = await run_blocking(
                    lambda: ctx.draft_service.compose(
                        DraftRequest(idea=idea, context=draft_ctx)
                    )
                )
                state.record_draft(draft, draft_ctx)
                editor.set_value(draft.generated_content)
                for btn in (save_draft_btn, save_pub_btn, use_idea_btn):
                    btn.set_enabled(True)
                render_history()
                sync_status()
                ui.notify("Draft generated.", type="positive")
            except DraftGenerationError as exc:
                message = (
                    exc.message
                    or str(exc)
                    or "Draft generation failed. Please try again."
                )
                sync_status()
                ui.notify(message, type="negative")
            except Exception as exc:
                sync_status()
                ui.notify(f"Unexpected error: {exc}", type="negative")

        await components.run_with_disabled([gen_btn, build_btn], _generate)

    def on_use_idea() -> None:
        txt = (editor.value or "").strip()
        if not txt:
            ui.notify("No draft text.", type="warning")
            return
        idea_area.set_value(txt)
        ui.notify("Copied draft to Idea.", type="info")

    async def on_save(status: PostStatus) -> None:
        try:
            prepared = state.prepare_post_for_save(editor.value or "", status)
        except ValueError as exc:
            ui.notify(str(exc), type="warning")
            return
        if prepared is None:
            return
        post, saved_label = prepared

        async def _save() -> None:
            await run_blocking(lambda: ctx.post_store_manager.save_post(post))
            state.mark_active_saved(saved_label)
            render_history()
            sync_status()
            ui.notify(f"Saved ({saved_label}).", type="positive")

        await components.run_with_disabled([save_draft_btn, save_pub_btn], _save)

    build_btn.on_click(on_build)
    gen_btn.on_click(on_generate)
    use_idea_btn.on_click(on_use_idea)
    save_draft_btn.on_click(lambda: on_save(PostStatus.DRAFT))
    save_pub_btn.on_click(lambda: on_save(PostStatus.PUBLISHED))
    editor.on_value_change(lambda _: sync_status())
    search_input.on_value_change(on_search)
    search_input.on("focus", on_search)

    render_role("voice")
    render_role("knowledge")
    sync_badges()
