from __future__ import annotations

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.drafting import (
    Draft,
    DraftGenerationError,
    DraftRequest,
)
from linkedin_idea_to_post.domain.post import PostStatus
from linkedin_idea_to_post.ui.gui import components, layout, primitives
from linkedin_idea_to_post.ui.gui.draft_context_dialog import DraftContextDialog
from linkedin_idea_to_post.ui.gui.draft_context_state import DraftContextState
from linkedin_idea_to_post.ui.gui.draft_history_state import (
    DEFAULT_TARGET_WORDS,
    MAX_TARGET_WORDS,
    MIN_TARGET_WORDS,
    WORD_COUNT_STEP,
    DraftHistoryState,
)
from linkedin_idea_to_post.ui.gui.helpers import run_blocking


def build_draft_tab(ctx: AppContext) -> None:
    ctx_state = DraftContextState(
        voice_limit=int(ctx.config.drafting.voice_examples_count),
        knowledge_limit=int(ctx.config.drafting.knowledge_examples_count),
    )
    hist_state = DraftHistoryState(
        max_history=int(ctx.config.drafting.draft_history_limit),
    )

    def sync_chip() -> None:
        vs = ctx_state.selected_count("voice")
        ks = ctx_state.selected_count("knowledge")
        ctx_chip.set_text(
            f"{vs}/{ctx_state.voice_limit} V · {ks}/{ctx_state.knowledge_limit} K"
        )
        primitives.set_badge_color(ctx_chip, "primary" if (vs + ks) else "blue-grey")

    with layout.page_container(), layout.split_workspace(ratio="2:3"):
        with layout.panel_card(size="fill"):
            with primitives.row(justify="between", shrink=True):
                primitives.heading("Idea", level=1)
                with primitives.row(full_width=False, gap="xs", shrink=True):
                    ctx_chip = primitives.badge(
                        f"0/{ctx_state.voice_limit} V · 0/{ctx_state.knowledge_limit} K",
                        color="blue-grey",
                        clickable=True,
                    )
                    tune_btn = primitives.icon_button(
                        "tune", color="primary", tooltip="Tune Context"
                    )

            ctx_dialog = DraftContextDialog(ctx, ctx_state, on_change=sync_chip)
            ctx_chip.on("click", ctx_dialog.open)
            tune_btn.on_click(ctx_dialog.open)
            sync_chip()

            idea_area = primitives.textarea(
                placeholder="Write your idea or angle...", fill=True
            )

            with primitives.row(justify="between", wrap=True, shrink=True):
                words_input = primitives.number_input(
                    "Words",
                    value=DEFAULT_TARGET_WORDS,
                    min_val=MIN_TARGET_WORDS,
                    max_val=MAX_TARGET_WORDS,
                    step=WORD_COUNT_STEP,
                    width="xs",
                )
                with primitives.row(full_width=False, gap="xs", shrink=True):
                    build_btn = primitives.button(
                        "Build Context", icon="auto_awesome", variant="outline"
                    )
                    gen_btn = primitives.button(
                        "Generate", icon="edit_note", variant="primary"
                    )

        with layout.panel_card(size="fill"):
            with primitives.row(justify="between", shrink=True):
                primitives.heading("Draft", level=1)
                status_lbl = primitives.text("", tone="mono")

            history_row = primitives.row(wrap=True, gap="xs", shrink=True)
            history_row.set_visibility(False)

            editor = primitives.textarea(
                placeholder="Generated draft appears here...", fill=True
            )

            with primitives.row(justify="between", wrap=True, shrink=True):
                use_idea_btn = primitives.button(
                    "Use as Idea", icon="north_west", variant="flat"
                )
                use_idea_btn.set_enabled(False)
                with primitives.row(full_width=False, gap="xs", shrink=True):
                    save_draft_btn = primitives.button(
                        "Save Draft", icon="save", variant="outline"
                    )
                    save_pub_btn = primitives.button(
                        "Publish", icon="publish", variant="positive"
                    )
                    save_draft_btn.set_enabled(False)
                    save_pub_btn.set_enabled(False)

    def sync_status() -> None:
        status_lbl.set_text(hist_state.active_status_text(editor.value or ""))

    def render_history() -> None:
        history_row.clear()
        if not hist_state.history:
            history_row.set_visibility(False)
            return
        history_row.set_visibility(True)
        with history_row:
            primitives.text("History:", tone="muted", shrink=True)
            for idx, entry in enumerate(hist_state.history):
                active = idx == hist_state.active
                lbl = f"#{idx + 1}" + (" ✓" if entry.saved else "")

                def pick(i: int = idx) -> None:
                    selected_entry = hist_state.select_history(i, editor.value or "")
                    ctx_state.restore_context(selected_entry.context)
                    editor.set_value(selected_entry.text)
                    if selected_entry.context.target_word_count > 0:
                        words_input.set_value(selected_entry.context.target_word_count)
                    ctx_dialog.refresh()
                    render_history()
                    sync_status()

                btn = primitives.button(
                    lbl,
                    variant="primary" if active else "outline",
                    size="xs",
                    on_click=pick,
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
            ctx_state.merge_auto(draft_ctx)
            ctx_dialog.refresh()
            ctx_dialog.open()

        await components.run_with_disabled([build_btn], _build)

    async def on_generate() -> None:
        idea = (idea_area.value or "").strip()
        if not idea:
            ui.notify("Write an idea first.", type="warning")
            return
        hist_state.sync_active_text(editor.value or "")

        async def _generate() -> None:
            try:
                draft_ctx = ctx_state.build_draft_context(
                    int(words_input.value or DEFAULT_TARGET_WORDS)
                )
                draft: Draft = await run_blocking(
                    lambda: ctx.draft_service.compose(
                        DraftRequest(idea=idea, context=draft_ctx)
                    )
                )
                hist_state.record_draft(draft, draft_ctx)
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
            prepared = hist_state.prepare_post_for_save(editor.value or "", status)
        except ValueError as exc:
            ui.notify(str(exc), type="warning")
            return
        if prepared is None:
            return
        post, saved_label = prepared

        async def _save() -> None:
            await run_blocking(lambda: ctx.post_store_manager.save_post(post))
            hist_state.mark_active_saved(saved_label)
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
