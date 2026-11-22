import re

_HASHTAG_REGEX = re.compile(r"(?<![^\s.,;!?)(])#([^\W\d_]\w*)(?=[\s.,;!?)(]|$)")


def extract_hashtags(raw_body: str) -> set[str]:
    hashtags = _HASHTAG_REGEX.findall(raw_body)
    return {hashtag.lower() for hashtag in hashtags}
