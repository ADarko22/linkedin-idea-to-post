from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter


class FakeDraftWriter(DraftWriter):
    def write(self, request: DraftRequest) -> Draft:
        body = f"{request.idea}\n\nVoice examples received ({len(request.voice_examples)}):\n"
        for idx, example in enumerate(request.voice_examples):
            body += f"Example #{idx + 1}:\n{example}\n\n"
        return Draft(body=body)
