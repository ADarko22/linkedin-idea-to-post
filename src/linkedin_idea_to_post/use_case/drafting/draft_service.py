from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter


class DraftService:
    def __init__(self, writer: DraftWriter) -> None:
        self.writer = writer

    def compose(self, draft_request: DraftRequest) -> Draft:
        return self.writer.write(draft_request)
