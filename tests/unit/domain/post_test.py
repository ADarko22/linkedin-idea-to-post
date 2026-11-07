from datetime import datetime

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus


def test_post_survives_a_json_round_trip() -> None:
    post = Post(
        created_at=datetime.fromisoformat("2023-01-01T00:00:00"),
        title="Test Post",
        body="This is a test post.",
        topics=["test", "post"],
        origin=PostOrigin.HUMAN,
        status=PostStatus.DRAFT,
    )
    data = post.model_dump(mode="json")  # what would be stored
    assert data["origin"] == "human"
    assert data["status"] == "draft"
    assert Post.model_validate(data) == post  # and it reads back identical
