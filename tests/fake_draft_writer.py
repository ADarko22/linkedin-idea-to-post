from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter


class FakeDraftWriter(DraftWriter):
    def write(self, request: DraftRequest) -> Draft:
        body = f"{request.idea}\n\nVoice examples ({len(request.context.voice_selections)}):\n"
        for idx, voice_selection in enumerate(request.context.voice_selections):
            post_id = voice_selection.post_id
            post_body = request.context.relevant_posts[post_id].body
            body += f"Example #{idx + 1} tuning={voice_selection.tuning.value}:\n{post_body}\n\n"

        body += f"Knowledge posts ({len(request.context.knowledge_selections)}):\n"
        for idx, knowledge_selection in enumerate(request.context.knowledge_selections):
            post_id = knowledge_selection.post_id
            post_body = request.context.relevant_posts[post_id].body
            body += f"Post #{idx + 1} stance={knowledge_selection.stance.value}:\n{post_body}\n\n"

        return Draft(idea=request.idea, generated_content=body)
