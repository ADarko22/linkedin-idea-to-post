import pytest

from linkedin_idea_to_post.domain.post_text import extract_hashtags, extract_title


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


@pytest.mark.parametrize(
    "raw_body, expected_title",
    [
        ("Some potential title.", "Some potential title."),
        (
            "Some potential title which is too long and must be capped at a whitespace.",
            "Some potential title which is too long and must",
        ),
        (
            """Some potential capped at newline.
        This is a continuation.
        """,
            "Some potential capped at newline.",
        ),
        (
            "Some-potential-title_which_is__too-long-and-must-be-capped-at-size-match",
            "Some-potential-title_which_is__too-long-and-must-b",
        ),
    ],
)
def test_extract_title(raw_body: str, expected_title: str) -> None:
    assert extract_title(raw_body) == expected_title
