from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter


class DryRunDraftWriter(DraftWriter):
    def write(self, request: DraftRequest) -> Draft:
        pass
        return Draft(body="")
