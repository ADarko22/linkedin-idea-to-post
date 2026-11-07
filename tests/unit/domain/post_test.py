from linkedin_idea_to_post.domain.post import Post


def test_post_survives_a_json_round_trip(sample_post: Post) -> None:
    data = sample_post.model_dump(mode="json")
    assert data["origin"] == "HUMAN"
    assert data["status"] == "DRAFT"
    assert Post.model_validate(data) == sample_post
