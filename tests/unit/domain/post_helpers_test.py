import pytest

from linkedin_idea_to_post.domain.post_helpers import extract_hashtags


###############################################################################################################
# Extract Topics from hashtags
@pytest.mark.parametrize(
    "raw_body, expected_hashtags_set",
    [
        ("#python", {"python"}),
        (
            "#python #coding,#pytest;#unit_test",
            {"python", "coding", "pytest", "unit_test"},
        ),
        (
            """
                    Some formatted text.
                    With some valid and invalid hashtags. #python.#coding #unit-test #unit_test
                    """,
            {"python", "coding", "unit_test"},
        ),
        ("no hashtags", set()),
        (
            "not/#hashtags #1 #100 #b2b!#Python #PYTHON? #LoveCoding!",
            {"b2b", "python", "lovecoding"},
        ),
        ("#Python #PYTHON? #python!", {"python"}),
    ],
)
def test_extract_hashtags(raw_body: str, expected_hashtags_set: set[str]) -> None:
    assert extract_hashtags(raw_body) == expected_hashtags_set
