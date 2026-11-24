from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal
from uuid import UUID

from nicegui import ui

from linkedin_idea_to_post.app_context import AppContext
from linkedin_idea_to_post.domain.drafting import (
    Draft,
    DraftContext,
    DraftGenerationError,
    DraftRequest,
    KnowledgeSelection,
    KnowledgeStance,
    VoiceSelection,
    VoiceTuning,
)
from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import post_from_draft
from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.ui.gui import styles
from linkedin_idea_to_post.ui.gui.helpers import (
    format_hashtags,
    post_short_preview,
    run_blocking,
)

MAX_HISTORY = 10
MAX_SEARCH = 15
Role = Literal["voice", "knowledge"]
Source = Literal["auto", "manual"]


@dataclass
class _CtxItem:
    post: Post
    role: Role
    source: Source
    selected: bool
    tuning: VoiceTuning = VoiceTuning.MATCH_STYLE
    stance: KnowledgeStance = KnowledgeStance.NEUTRAL


@dataclass
class _DraftEntry:
    draft: Draft
    text: str
    saved: str | None = None


@dataclass
class _State:
    context: DraftContext = field(default_factory=DraftContext)
    voice: list[_CtxItem] = field(default_factory=list)
    knowledge: list[_CtxItem] = field(default_factory=list)
    history: list[_DraftEntry] = field(default_factory=list)
    active: int = -1


def _limits(ctx: AppContext) -> tuple[int, int]:
    return (
        int(ctx.config.drafting.voice_examples_count),
        int(ctx.config.drafting.knowledge_examples_count),
    )


def build_draft_tab(ctx: AppContext) -> None:
    st = _State()
    v_lim, k_lim = _limits(ctx)

    read_dialog = ui.dialog().props("backdrop-filter='blur(3px)'")
    with read_dialog, styles.dialog_card("max-w-2xl"):
        styles.modal_header("Post Content", read_dialog.close)
        read_tags = styles.tags_label("")
        with styles.scroll_box("h-72", "overflow-x-hidden"):
            read_body = styles.post_body_label("")
        read_actions = ui.row().classes("w-full justify-end gap-2")

    ctx_dialog = ui.dialog().props("backdrop-filter='blur(2px)'")
    with ctx_dialog, styles.dialog_card("max-w-5xl"):
        with styles.row_between("gap-2 flex-wrap"):
            with styles.row_gap_2():
                ui.icon("tune", size="md", color="primary")
                styles.section_title("Context & Tuning")
            with styles.row_gap_2():
                v_badge = ui.badge(f"Voice 0/{v_lim}", color="blue-grey")
                k_badge = ui.badge(f"Knowledge 0/{k_lim}", color="blue-grey")
                styles.positive_button(
                    "Apply & Close",
                    icon="check_circle",
                    on_click=ctx_dialog.close,
                    unelevated=True,
                )

        search_input = styles.outlined_input(
            "Search archive (up to 15)", placeholder="Keywords or #hashtags..."
        )
        with search_input.add_slot("prepend"):
            ui.icon("search", color="primary")

        search_panel = ui.column().classes(
            "w-full border rounded bg-grey-1 q-pa-xs gap-1"
        )
        search_panel.set_visibility(False)
        with search_panel:
            search_info = styles.muted_caption("", "text-grey-8 px-1")
            search_box = ui.column().classes(
                "w-full max-h-60 overflow-y-auto gap-1.5 pr-1"
            )

        with (
            styles.scroll_box("h-[72vh]", "min-h-80 overflow-x-hidden"),
            ui.column().classes("w-full gap-3 overflow-x-hidden"),
        ):
            styles.section_title("Voices", small=True)
            voices_box = ui.column().classes("w-full gap-2")
            ui.separator()
            styles.section_title("Knowledge", small=True)
            knowledge_box = ui.column().classes("w-full gap-2")

    with (
        styles.narrow_column("overflow-x-hidden"),
        styles.card_panel("overflow-x-hidden"),
    ):
        with styles.row_between("gap-2 flex-wrap"):
            styles.section_title("Idea & Draft")
            with styles.row_gap_2():
                status_lbl = styles.muted_caption("")
                ctx_chip = ui.badge(
                    f"Context: 0/{v_lim} V · 0/{k_lim} K", color="blue-grey"
                ).classes("cursor-pointer")
                ctx_chip.on("click", ctx_dialog.open)
                styles.flat_button(
                    icon="tune",
                    on_click=ctx_dialog.open,
                    extra_props="round size=sm color=primary",
                ).tooltip("Tune Context")

        idea_area = styles.outlined_textarea(
            "Idea", placeholder="Write your idea or angle...", rows=3
        )

        with styles.row_between("flex-wrap"):
            words_input = (
                ui.number("Target words", value=220, min=50, max=1500, step=25)
                .props("outlined dense")
                .classes("w-36")
            )
            with styles.row_gap_2("flex-wrap"):
                build_btn = styles.primary_button("Build Context", icon="auto_awesome")
                gen_btn = ui.button(
                    "Generate Draft", icon="edit_note", color="secondary"
                )

        history_row = styles.row_gap_2("w-full flex-wrap")
        history_row.set_visibility(False)
        ui.separator()

        editor = styles.outlined_textarea(
            "Draft", placeholder="Generated draft appears here...", rows=10
        )

        with styles.row_between("gap-2 flex-wrap"):
            use_idea_btn = styles.outline_button("Use Draft as Idea", icon="north_west")
            use_idea_btn.set_enabled(False)
            with styles.row_gap_2("flex-wrap"):
                save_draft_btn = styles.outline_button(
                    "Save as DRAFT", icon="save", dense=False
                )
                save_pub_btn = styles.positive_button(
                    "Save as PUBLISHED", icon="publish"
                )
                save_draft_btn.set_enabled(False)
                save_pub_btn.set_enabled(False)

    def items_for(role: Role) -> list[_CtxItem]:
        return st.voice if role == "voice" else st.knowledge

    def set_items(role: Role, items: list[_CtxItem]) -> None:
        if role == "voice":
            st.voice = items
        else:
            st.knowledge = items

    def limit_for(role: Role) -> int:
        return v_lim if role == "voice" else k_lim

    def selected_count(role: Role) -> int:
        return sum(1 for x in items_for(role) if x.selected)

    def sync_badges() -> None:
        vs, ks = selected_count("voice"), selected_count("knowledge")
        v_badge.set_text(f"Voice {vs}/{v_lim}")
        k_badge.set_text(f"Knowledge {ks}/{k_lim}")
        v_badge.props(f"color={'warning' if vs >= v_lim else 'blue-grey'}")
        k_badge.props(f"color={'warning' if ks >= k_lim else 'blue-grey'}")
        ctx_chip.set_text(f"Context: {vs}/{v_lim} V · {ks}/{k_lim} K")
        ctx_chip.props(f"color={'primary' if (vs + ks) else 'blue-grey'}")

    def sync_text() -> None:
        if 0 <= st.active < len(st.history):
            st.history[st.active].text = editor.value or ""

    def sync_status() -> None:
        if not (0 <= st.active < len(st.history)):
            status_lbl.set_text("")
            return
        entry = st.history[st.active]
        edited = (editor.value or "").strip() != entry.draft.generated_content.strip()
        origin = PostOrigin.AI_EDIT.value if edited else PostOrigin.AI_DRAFT.value
        saved = f" · {entry.saved}" if entry.saved else ""
        status_lbl.set_text(f"#{st.active + 1}/{len(st.history)} · {origin}{saved}")

    def render_history() -> None:
        history_row.clear()
        if not st.history:
            history_row.set_visibility(False)
            return
        history_row.set_visibility(True)
        with history_row:
            styles.muted_caption("History:", "q-mr-xs")
            for idx, entry in enumerate(st.history):
                active = idx == st.active
                lbl = f"#{idx + 1}" + (" ✓" if entry.saved else "")

                def pick(i: int = idx) -> None:
                    sync_text()
                    st.active = i
                    editor.set_value(st.history[i].text)
                    render_history()
                    sync_status()

                ui.button(
                    lbl, on_click=pick, color="primary" if active else None
                ).props("dense unelevated" if active else "dense outline")

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
            ).props("dense unelevated")
            ui.button(
                "+ Knowledge",
                icon="menu_book",
                color="teal",
                on_click=lambda _, p=post: _add_and_close(p, "knowledge"),
            ).props("dense unelevated")
        read_dialog.open()

    def toggle_sel(item: _CtxItem, checked: bool, cb: ui.checkbox) -> None:
        if item.selected == checked:
            return
        if checked and selected_count(item.role) >= limit_for(item.role):
            ui.notify(f"Limit: max {limit_for(item.role)} {item.role}.", type="warning")
            cb.set_value(False)
            return
        item.selected = checked
        sync_badges()

    def remove_item(item: _CtxItem) -> None:
        set_items(item.role, [x for x in items_for(item.role) if x is not item])
        render_role(item.role)
        sync_badges()

    def render_role(role: Role) -> None:
        box = voices_box if role == "voice" else knowledge_box
        items = items_for(role)
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
                with (
                    ui.card().classes(f"w-full q-pa-xs overflow-x-hidden {accent}"),
                    ui.row().classes("w-full items-start gap-2 flex-nowrap"),
                ):
                    cb = ui.checkbox(value=item.selected).classes("shrink-0 mt-1")
                    cb.on_value_change(
                        lambda e, t=item, c=cb: toggle_sel(t, bool(e.value), c)
                    )
                    exp = ui.expansion().classes("col min-w-[200px]")
                    with exp.add_slot("header"), styles.row_between("gap-2 py-1"):
                        prev = styles.post_preview_label(
                            post_short_preview(item.post), "whitespace-normal col"
                        )
                        prev.bind_visibility_from(
                            exp, "value", backward=lambda v: not v
                        )
                        ui.badge(
                            "Added" if manual else "Suggested",
                            color="teal" if manual else "grey-7",
                        ).classes("shrink-0")

                    opts = (
                        [t.value for t in VoiceTuning]
                        if role == "voice"
                        else [s.value for s in KnowledgeStance]
                    )
                    val = item.tuning.value if role == "voice" else item.stance.value
                    sel = (
                        ui.select(
                            opts,
                            value=val,
                            label="Tuning" if role == "voice" else "Stance",
                        )
                        .props("dense outlined")
                        .classes("w-44 shrink-0")
                    )
                    attr = "tuning" if role == "voice" else "stance"
                    enum_cls = VoiceTuning if role == "voice" else KnowledgeStance
                    sel.on_value_change(
                        lambda e, t=item, a=attr, cls=enum_cls: setattr(
                            t, a, cls(str(e.value))
                        )
                    )

                    styles.flat_button(
                        icon="delete",
                        on_click=lambda _, t=item: remove_item(t),
                        extra_props="round size=sm color=negative",
                    ).tooltip("Remove").classes("shrink-0 mt-1")

                    with exp, ui.column().classes("w-full q-pa-sm pt-1 gap-1.5"):
                        ui.separator()
                        tags = format_hashtags(item.post)
                        if tags:
                            styles.tags_label(tags)
                        styles.post_body_label(item.post.body)

    def add_manual(post: Post, role: Role) -> None:
        st.context.relevant_posts[post.id] = post
        items = items_for(role)
        existing = next((x for x in items if x.post.id == post.id), None)
        can_sel = selected_count(role) < limit_for(role)
        if existing:
            existing.source = "manual"
            if not existing.selected and can_sel:
                existing.selected = True
        else:
            items.append(
                _CtxItem(post=post, role=role, source="manual", selected=can_sel)
            )
        render_role(role)
        sync_badges()
        ui.notify(
            f"Added to {role}" + ("" if can_sel else " (unchecked: limit reached)"),
            type="positive" if can_sel else "warning",
        )

    def merge_auto(draft_ctx: DraftContext) -> None:
        st.context = draft_ctx
        roles: tuple[tuple[Role, Any], ...] = (
            ("voice", draft_ctx.voice_selections),
            ("knowledge", draft_ctx.knowledge_selections),
        )
        for role, sels in roles:
            manual = [x for x in items_for(role) if x.source == "manual"]
            manual_ids = {x.post.id for x in manual}
            slots = max(0, limit_for(role) - sum(1 for x in manual if x.selected))
            auto: list[_CtxItem] = []
            for s in sels:
                if s.post_id in manual_ids:
                    continue
                post = draft_ctx.relevant_posts.get(s.post_id)
                if post:
                    auto.append(
                        _CtxItem(
                            post=post,
                            role=role,
                            source="auto",
                            selected=len(auto) < slots,
                            tuning=getattr(s, "tuning", VoiceTuning.MATCH_STYLE),
                            stance=getattr(s, "stance", KnowledgeStance.NEUTRAL),
                        )
                    )
            set_items(role, manual + auto)
            render_role(role)
        sync_badges()

    async def on_search() -> None:
        q = (search_input.value or "").strip().lower()
        if not q:
            search_panel.set_visibility(False)
            search_box.clear()
            return

        posts = await run_blocking(
            lambda: ctx.post_storage.get_all(
                PostGetQuery(limit=ctx.config.storage.post_get_all_page_size, page=1)
            )
        )
        matches = [
            p
            for p in posts
            if q in p.body.lower() or any(q in tag.lower() for tag in p.hashtags)
        ][:MAX_SEARCH]

        search_box.clear()
        search_panel.set_visibility(True)
        search_info.set_text(
            f"{len(matches)} result(s) (max {MAX_SEARCH}) — click to open preview"
            if matches
            else "No matching posts."
        )
        with search_box:
            for p in matches:
                with (
                    ui.card().classes(
                        "w-full shrink-0 q-px-sm q-py-xs bg-white overflow-visible"
                    ),
                    styles.row_between("gap-2 flex-wrap overflow-visible"),
                ):
                    preview = styles.post_preview_label(
                        post_short_preview(p),
                        "text-grey-10 cursor-pointer hover:text-primary whitespace-normal overflow-visible flex-1 min-w-[240px]",
                    )
                    preview.on("click", lambda _, post=p: open_reader(post))
                    with styles.row_gap_2("gap-1.5 shrink-0"):
                        ui.button(
                            "Voice",
                            icon="add_circle",
                            on_click=lambda _, post=p: add_manual(post, "voice"),
                        ).props("dense outline size=sm color=primary")
                        ui.button(
                            "Knowledge",
                            icon="add_circle",
                            on_click=lambda _, post=p: add_manual(post, "knowledge"),
                        ).props("dense outline size=sm color=teal")

    def collect_ctx() -> DraftContext:
        rel: dict[UUID, Post] = dict(st.context.relevant_posts if st.context else {})
        for x in st.voice + st.knowledge:
            rel[x.post.id] = x.post
        return DraftContext(
            relevant_posts=rel,
            voice_selections=[
                VoiceSelection(post_id=x.post.id, tuning=x.tuning)
                for x in st.voice
                if x.selected
            ][:v_lim],
            knowledge_selections=[
                KnowledgeSelection(post_id=x.post.id, stance=x.stance)
                for x in st.knowledge
                if x.selected
            ][:k_lim],
            target_word_count=int(words_input.value or 220),
        )

    async def on_build() -> None:
        idea = (idea_area.value or "").strip()
        if not idea:
            ui.notify("Write an idea first.", type="warning")
            return
        build_btn.disable()
        try:
            draft_ctx = await run_blocking(
                lambda: ctx.draft_context_service.create_context(
                    idea=idea, target_word_count=int(words_input.value or 220)
                )
            )
            merge_auto(draft_ctx)
            await ctx_dialog.open()
        finally:
            build_btn.enable()

    async def on_generate() -> None:
        idea = (idea_area.value or "").strip()
        if not idea:
            ui.notify("Write an idea first.", type="warning")
            return
        sync_text()
        gen_btn.disable()
        build_btn.disable()
        try:
            draft: Draft = await run_blocking(
                lambda: ctx.draft_service.compose(
                    DraftRequest(idea=idea, context=collect_ctx())
                )
            )
            st.history.append(_DraftEntry(draft=draft, text=draft.generated_content))
            if len(st.history) > MAX_HISTORY:
                st.history = st.history[-MAX_HISTORY:]
            st.active = len(st.history) - 1
            editor.set_value(draft.generated_content)
            for b in (save_draft_btn, save_pub_btn, use_idea_btn):
                b.set_enabled(True)
            render_history()
            sync_status()
            ui.notify("Draft generated.", type="positive")
        except DraftGenerationError as exc:
            message = (
                exc.message or str(exc) or "Draft generation failed. Please try again."
            )
            sync_status()
            ui.notify(message, type="negative")
        except Exception as exc:
            sync_status()
            ui.notify(f"Unexpected error: {exc}", type="negative")
        finally:
            gen_btn.enable()
            build_btn.enable()

    def on_use_idea() -> None:
        txt = (editor.value or "").strip()
        if not txt:
            ui.notify("No draft text.", type="warning")
            return
        idea_area.set_value(txt)
        ui.notify("Copied draft to Idea.", type="info")

    async def on_save(status: PostStatus) -> None:
        if not (0 <= st.active < len(st.history)):
            return
        entry = st.history[st.active]
        txt = (editor.value or "").strip()
        if not txt:
            ui.notify("Draft cannot be empty.", type="warning")
            return
        edited = txt != entry.draft.generated_content.strip()
        origin = PostOrigin.AI_EDIT if edited else PostOrigin.AI_DRAFT
        post = post_from_draft(
            entry.draft,
            body_override=txt if edited else None,
            origin=origin,
            status=status,
        )
        save_draft_btn.disable()
        save_pub_btn.disable()
        try:
            await run_blocking(lambda: ctx.post_store_manager.save_post(post))
            entry.saved = f"{origin.value} · {status.value}"
            render_history()
            sync_status()
            ui.notify(f"Saved ({entry.saved}).", type="positive")
        finally:
            save_draft_btn.enable()
            save_pub_btn.enable()

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
