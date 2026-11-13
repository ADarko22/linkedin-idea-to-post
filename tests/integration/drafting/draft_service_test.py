from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.domain.drafting import Draft, DraftRequest, DraftWriter
from linkedin_idea_to_post.drafting.draft_service import DraftService


class MockDraftWriter(DraftWriter):
    def write(self, request: DraftRequest) -> Draft:
        return Draft(body=request.idea)


def test_draft_service_saves_a_draft():
    writer = MockDraftWriter()
    archive = SqliteArchive()
    draft_service = DraftService(writer, archive)

    assert len(archive.get_all()) == 0

    request = "My idea"
    draft_post = draft_service.draft(request)

    post = archive.get(draft_post.id)
    assert post is not None
    assert post == draft_post
