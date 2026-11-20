from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter


class FakeDraftWriter(DraftWriter):
    def write(self, request: DraftRequest) -> Draft:
        body = f"{request.idea}\n\nVoice examples received ({len(request.context.voice_selections)}):\n"
        for idx, voice_selection in enumerate(request.context.voice_selections):
            post_id = voice_selection.post_id
            post_body = request.relevant_posts[post_id].body
            body += f"Example #{idx + 1}:\n{post_body}\n\n"
        return Draft(idea=request.idea, generated_content=body)
