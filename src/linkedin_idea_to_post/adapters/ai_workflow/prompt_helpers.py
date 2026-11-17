def format_voice_examples(voice_examples: list[str]) -> str:
    formatted_voice_examples = ""
    for idx, voice_example in enumerate(voice_examples):
        formatted_voice_examples += f"Example #{idx + 1}:\n{voice_example}\n\n"
    return formatted_voice_examples
