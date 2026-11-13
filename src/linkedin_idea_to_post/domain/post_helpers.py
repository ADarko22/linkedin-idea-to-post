###############################################################################################################
# Extract Title from sanitized body
import re

_TITLE_MAX_LENGTH = 50


def extract_title(raw_body: str, title_length=_TITLE_MAX_LENGTH) -> str:
    stripped_raw_body = raw_body.strip()

    first_new_line = stripped_raw_body[:title_length].find("\n")
    if first_new_line != -1:
        return stripped_raw_body[:first_new_line].strip()

    last_space = stripped_raw_body[:title_length].rfind(" ")
    if len(raw_body) > title_length and last_space != -1:
        return stripped_raw_body[:last_space].strip()

    return stripped_raw_body[:title_length].strip()


###############################################################################################################
# Extract Topics from hashtags
# REGEX accepts hashtags that are preceded and followed by: white-spaces, ',', ';', start of string, end of string.
_HASHTAG_REGEX = re.compile(r"(?<![^\s.,;!?)(])#([^\W\d_]\w*)(?=[\s.,;!?)(]|$)")


def extract_hashtags(raw_body: str) -> set[str]:
    hashtags = _HASHTAG_REGEX.findall(raw_body)
    return {hashtag.lower() for hashtag in hashtags}
