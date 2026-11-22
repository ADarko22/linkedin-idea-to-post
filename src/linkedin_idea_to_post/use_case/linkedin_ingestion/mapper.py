import re
import unicodedata
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import ParamSpec, TypeVar

from linkedin_idea_to_post.domain.post import Post, PostOrigin, PostStatus
from linkedin_idea_to_post.domain.post_helpers import extract_hashtags
from linkedin_idea_to_post.use_case.linkedin_ingestion.model import (
    FieldError,
    MappingErrorCode,
    MappingFailure,
    RawPost,
)

###############################################################################################################
# Extract Deterministic UUID from url
# Matches the urn id after the string '<something>urn:li:<type>:'
_SHARE_LINK_SHA_REGEX = re.compile(
    r"^https://www\.linkedin\.com/feed/update/urn(?::|%3A)li(?::|%3A)[a-zA-Z]+(?::|%3A)(\d+)"
)


def extract_post_uuid(share_link: str) -> uuid.UUID:
    if not share_link.strip():
        field_error = FieldError(
            field="share_link", code=MappingErrorCode.INVALID_URL, message="Empty URL."
        )
        raise MappingFailure([field_error])

    match = _SHARE_LINK_SHA_REGEX.search(share_link)
    if not match:
        field_error = FieldError(
            field="share_link",
            code=MappingErrorCode.INVALID_URL,
            message="Cannot extract URN ID.",
        )
        raise MappingFailure([field_error])

    share_link_sha = match.groups()[0]
    return uuid.uuid5(uuid.NAMESPACE_URL, share_link_sha)


###############################################################################################################
# Extract Sanitized body
def extract_sanitized_body(share_commentary: str) -> str:
    """
    Normalizes unicode, strips multi-layered LinkedIn CSV quote artifacts,
    and cleans up redundant quotation marks and spacing.
    """
    if not share_commentary:
        return ""

    # 1. Normalize Unicode look-alikes (NFKD)
    normalized = unicodedata.normalize("NFKD", share_commentary)

    # 2. Clean up CSV double-quote escaping ("" -> ")
    cleaned = normalized.replace('""', '"')

    # 3. Strip leading/trailing whitespaces
    cleaned = cleaned.strip()

    # 4. Remove quotes from start and end of lines
    lines = cleaned.splitlines()
    processed_lines = []
    for line in lines:
        line = line.strip()

        # Strip leading quotes
        line = re.sub(r'^["“”]+', "", line).strip()

        # Strip trailing quotes
        line = re.sub(r'["“”]+$', "", line).strip()

        if line:
            processed_lines.append(line)

    return "\n".join(processed_lines)


###############################################################################################################
# Extract UTC Datetime
def extract_utc_datetime(date: str) -> datetime:
    if not date.strip():
        field_error = FieldError(
            field="date",
            code=MappingErrorCode.INVALID_DATE_FORMAT,
            message="Empty Date.",
        )
        raise MappingFailure([field_error])

    try:
        return datetime.strptime(date.strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
    except ValueError as exc:
        field_error = FieldError(
            field="date",
            code=MappingErrorCode.INVALID_DATE_FORMAT,
            message=f"Invalid Date format: {exc}.",
        )
        raise MappingFailure([field_error]) from exc


###############################################################################################################
# MAPPER
###############################################################################################################
P = ParamSpec("P")
T = TypeVar("T")


class ErrorCollector:
    def __init__(self) -> None:
        self.errors: list[FieldError] = []

    def capture(
        self, function: Callable[P, T], *args: P.args, **kwargs: P.kwargs
    ) -> T | None:
        try:
            return function(*args, **kwargs)
        except MappingFailure as failure:
            self.errors.extend(failure.errors)
            return None

    def raise_if_any(self) -> None:
        if self.errors:
            raise MappingFailure(self.errors)


def raw_post_to_post(raw_post: RawPost) -> Post:
    collector = ErrorCollector()

    post_uuid = collector.capture(
        function=extract_post_uuid, share_link=raw_post.share_link
    )
    post_datetime = collector.capture(function=extract_utc_datetime, date=raw_post.date)
    body = collector.capture(
        function=extract_sanitized_body, share_commentary=raw_post.share_commentary
    )

    hashtags = (
        collector.capture(function=extract_hashtags, raw_body=body)
        if body is not None
        else None
    )

    collector.raise_if_any()

    assert (
        post_uuid is not None
        and post_datetime is not None
        and body is not None
        and hashtags is not None
    )

    return Post(
        id=post_uuid,
        url=raw_post.share_link,
        body=body,
        hashtags=hashtags,
        origin=PostOrigin.HUMAN,
        status=PostStatus.PUBLISHED,
        created_at=post_datetime,
        updated_at=post_datetime,
    )
