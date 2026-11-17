from linkedin_idea_to_post.adapters.ai_workflow.prompt_helpers import (
    format_voice_examples,
)


def test_format_voice_examples_with_no_examples() -> None:
    voice_examples = []
    assert format_voice_examples(voice_examples) == ""


def test_format_voice_examples() -> None:
    expected_voice_examples = (
        "Example #1:\nPost about tech and work.\nWhat an amazing world!\n#tech #work\n\n"
        "Example #2:\nPost about self development.\nHard but rewarding!\n#growth #nevergiveup\n\n"
    )

    voice_examples = [
        """Post about tech and work.\nWhat an amazing world!\n#tech #work""",
        """Post about self development.\nHard but rewarding!\n#growth #nevergiveup""",
    ]

    assert format_voice_examples(voice_examples) == expected_voice_examples
