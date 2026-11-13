from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter


# todo temporary class; to be replaced with a CrewaiDraftWriter with a PromptEchoLLM
class DryRunDraftWriter(DraftWriter):
    def write(self, request: DraftRequest) -> Draft:
        body = f"DRY RUN: {request.idea}\n\nNo model was called. Voice examples received ({len(request.voice_examples)}):\n"
        for idx, example in enumerate(request.voice_examples):
            body += f"{idx + 1}. {example}\n\n"
        return Draft(body=body)
