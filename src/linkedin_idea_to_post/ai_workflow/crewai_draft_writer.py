from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter


class CrewaiDraftWriter(DraftWriter):
    def write(self, request: DraftRequest) -> Draft:
        voices = [voice[:5] for voice in request.voice_examples]
        body = f"{request.idea}\n{'\n'.join(voices)}"
        return Draft(body=body)
