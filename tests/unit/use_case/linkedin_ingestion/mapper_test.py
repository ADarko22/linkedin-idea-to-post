import re

import pytest

from linkedin_idea_to_post.use_case.linkedin_ingestion.mapper import (
    ErrorCollector,
    extract_post_uuid,
    extract_sanitized_body,
    extract_utc_datetime,
    raw_post_to_post,
)
from linkedin_idea_to_post.use_case.linkedin_ingestion.model import (
    FieldError,
    MappingErrorCode,
    MappingFailure,
)


###############################################################################################################
# Extract Deterministic UUID from url
@pytest.mark.parametrize(
    "share_link, expected_post_uuid",
    [
        (
            "https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A7523857626154266624",
            "bb24370c-1206-5848-adcb-a31574b52974",
        ),
        (
            "https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A7523857626154266624",
            "bb24370c-1206-5848-adcb-a31574b52974",
        ),
        (
            "https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A7519088365242253312",
            "2fd86ac3-19e3-52c5-83db-ee5ab27052d8",
        ),
        (
            "https://www.linkedin.com/feed/update/urn%3Ali%3AugcPost%3A6781119234220032000",
            "24f4b464-142c-50f0-b7f6-cc499613d5a3",
        ),
    ],
)
def test_extract_post_uuid_deterministic(
    share_link: str, expected_post_uuid: str
) -> None:
    assert str(extract_post_uuid(share_link)) == expected_post_uuid


def test_extract_post_uuid_invalid_urn_id() -> None:
    field_error = FieldError(
        field="share_link",
        code=MappingErrorCode.INVALID_URL,
        message="Cannot extract URN ID.",
    )
    mapping_failure = MappingFailure([field_error])

    with pytest.raises(MappingFailure, match=re.escape(str(mapping_failure))):
        extract_post_uuid("https://www.linkedin.com")

    with pytest.raises(MappingFailure, match=re.escape(str(mapping_failure))):
        extract_post_uuid(
            "http://www.linkedin.com/feed/update/urn%3Ali%3AugcPost%3A6781119234220032000"
        )


def test_extract_post_uuid_missing_url() -> None:
    field_error = FieldError(
        field="share_link", code=MappingErrorCode.INVALID_URL, message="Empty URL."
    )
    mapping_failure = MappingFailure([field_error])
    with pytest.raises(MappingFailure, match=re.escape(str(mapping_failure))):
        extract_post_uuid("")


###############################################################################################################
# Extract Sanitized body
def test_extract_sanitized_body():
    assert extract_sanitized_body(" 1. 𝘾𝙤𝙢𝙥𝙡𝙚𝙭𝙞𝙩𝙮") == "1. Complexity"
    assert (
        extract_sanitized_body("📖 𝙪𝙣𝙞𝙣𝙩𝙚𝙣𝙙𝙚𝙙 𝙘𝙤𝙣𝙨𝙚𝙦𝙪𝙚𝙣𝙘𝙚𝙨")
        == "📖 unintended consequences"
    )

    # Corner Case 1: Multi-layered wrapping quotes & CSV escaped quotes
    assert extract_sanitized_body('"""Hello ""World""!"""') == 'Hello "World"!'

    # Corner Case 2: Multi-line text with dangling leading/trailing quotes on internal split lines
    multiline_input = (
        '"""First line with quote"\n'
        '""Second line with dangling start and end quote"\n'
        '""Final line"""'
    )
    expected_multiline = (
        "First line with quote\n"
        "Second line with dangling start and end quote\n"
        "Final line"
    )
    assert extract_sanitized_body(multiline_input) == expected_multiline

    # Corner Case 3: Empty or whitespace-only inputs
    assert extract_sanitized_body("") == ""
    assert extract_sanitized_body("   ") == ""


###############################################################################################################
# Extract UTC Datetime
def test_extract_utc_datetime_empty_date() -> None:
    field_error = FieldError(
        field="date",
        code=MappingErrorCode.INVALID_DATE_FORMAT,
        message="Empty Date.",
    )
    mapping_failure = MappingFailure([field_error])

    with pytest.raises(MappingFailure, match=re.escape(str(mapping_failure))):
        extract_utc_datetime("")


def test_extract_utc_datetime_invalid_format() -> None:
    field_error = FieldError(
        field="date",
        code=MappingErrorCode.INVALID_DATE_FORMAT,
        message="Invalid Date format: time data '01-01-2026 10:10:11' does not match format '%Y-%m-%d %H:%M:%S'.",
    )
    mapping_failure = MappingFailure([field_error])

    with pytest.raises(MappingFailure, match=re.escape(str(mapping_failure))):
        extract_utc_datetime("01-01-2026 10:10:11")


###############################################################################################################
# MAPPER
###############################################################################################################
def test_error_collector():
    error_collector = ErrorCollector()
    error_collector.capture(function=extract_post_uuid, share_link="")
    error_collector.capture(function=extract_utc_datetime, date="01-01-2026 10:10:11")

    with pytest.raises(MappingFailure):
        error_collector.raise_if_any()


def test_raw_post_to_post_success(sample_raw_post, sample_post):
    assert raw_post_to_post(sample_raw_post) == sample_post


def test_raw_post_to_post_failure(raw_post_factory):
    malformed_raw_post = raw_post_factory(date="01-01-2026 10:10:11")
    with pytest.raises(MappingFailure):
        raw_post_to_post(malformed_raw_post)
