from linkedin_idea_to_post.domain.drafting import DraftRequest


def format_voice_examples(request: DraftRequest) -> str:
    if not request.context.voice_selections:
        return "No specific style examples provided. Use a clear, authentic, professional LinkedIn voice."

    blocks: list[str] = []
    for idx, selection in enumerate(request.context.voice_selections, start=1):
        post = request.context.relevant_posts[selection.post_id]
        blocks.append(
            f'<example index="{idx}" tuning="{selection.tuning.value}">\n'
            f"How to apply this example: {selection.tuning.instruction}\n"
            f"Example text:\n{post.body.strip()}\n"
            "</example>"
        )
    return "\n\n".join(blocks)


def format_knowledge_examples(request: DraftRequest) -> str:
    if not request.context.knowledge_selections:
        return "No prior posts provided for knowledge context. Rely on the core idea."

    blocks: list[str] = []
    for idx, selection in enumerate(request.context.knowledge_selections, start=1):
        post = request.context.relevant_posts[selection.post_id]
        blocks.append(
            f'<reference index="{idx}" stance="{selection.stance.value}">\n'
            f"How to treat this post: {selection.stance.instruction}\n"
            f"Content:\n{post.body.strip()}\n"
            "</reference>"
        )
    return "\n\n".join(blocks)
