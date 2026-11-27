from __future__ import annotations

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.drafting import (
    Draft,
    DraftGenerationError,
    DraftRequest,
)
from linkedin_idea_to_post.domain.post import PostStatus
from linkedin_idea_to_post.ui.gui import components, templates, theme
from linkedin_idea_to_post.ui.gui.draft_context_dialog import DraftContextDialog
from linkedin_idea_to_post.ui.gui.draft_state import (
    DEFAULT_TARGET_WORDS,
    MAX_TARGET_WORDS,
    MIN_TARGET_WORDS,
    WORD_COUNT_STEP,
    DraftTabState,
)
from linkedin_idea_to_post.ui.gui.helpers import run_blocking


def build_draft_tab(ctx: AppContext) -> None:
    state = DraftTabState(
        voice_limit=int(ctx.config.drafting.voice_examples_count),
        knowledge_limit=int(ctx.config.drafting.knowledge_examples_count),
        max_history=int(ctx.config.drafting.draft_history_limit),
    )

    def sync_chip() -> None:
        vs = state.selected_count("voice")
        ks = state.selected_count("knowledge")
        ctx_chip.set_text(
            f"Context: {vs}/{state.voice_limit} V · {ks}/{state.knowledge_limit} K"
        )
        theme.set_badge_color(ctx_chip, "primary" if (vs + ks) else "blue-grey")

    with (
        templates.narrow_page("overflow-x-hidden"),
        templates.card_panel("overflow-x-hidden"),
    ):
        with theme.row_between("gap-2 flex-wrap"):
            theme.section_title("Idea & Draft")
            with theme.row_gap_2():
                status_lbl = theme.muted_caption("")
                ctx_chip = theme.badge(
                    f"Context: 0/{state.voice_limit} V · 0/{state.knowledge_limit} K",
                    color="blue-grey",
                    clickable=True,
                )
                tune_btn = theme.icon_button(
                    "tune", color="primary", tooltip="Tune Context"
                )

        ctx_dialog = DraftContextDialog(ctx, state, on_change=sync_chip)
        ctx_chip.on("click", ctx_dialog.open)
        tune_btn.on_click(ctx_dialog.open)
        sync_chip()

        idea_area = theme.outlined_textarea(
            "Idea", placeholder="Write your idea or angle...", rows=3
        )

        with theme.row_between("flex-wrap"):
            words_input = theme.outlined_number(
                "Target words",
                value=DEFAULT_TARGET_WORDS,
                min=MIN_TARGET_WORDS,
                max=MAX_TARGET_WORDS,
                step=WORD_COUNT_STEP,
                extra_classes="w-36",
            )
            with theme.row_gap_2("flex-wrap"):
                build_btn = theme.primary_button("Build Context", icon="auto_awesome")
                gen_btn = theme.action_button(
                    "Generate Draft",
                    icon="edit_note",
                    color="secondary",
                    dense=False,
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
                    ctx_dialog.refresh()
                    render_history()
                    sync_status()

                btn = theme.action_button(
                    lbl,
                    on_click=pick,
                    color="primary" if active else None,
                    unelevated=active,
                    outline=not active,
                )
                v_cnt = len(entry.context.voice_selections)
                k_cnt = len(entry.context.knowledge_selections)
                btn.tooltip(
                    f"Context: {v_cnt}V · {k_cnt}K · {entry.context.target_word_count}w"
                )

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
            ctx_dialog.refresh()
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
