import re

import pytest

from linkedin_idea_to_post.linkedin.csv_parser import (
    CsvParser,
    parse_row,
    verify_headers,
    verify_row,
)
from linkedin_idea_to_post.linkedin.model import (
    CsvParsingError,
    ParsingErrorCode,
    ParsingFailure,
    RawPost,
)


def test_verify_valid_headers(create_csv_post_file) -> None:
    # No exception raised
    verify_headers({"Date", "ShareLink", "ShareCommentary", "xDate"})


def test_verify_invalid_headers(create_csv_post_file) -> None:
    expected_parsing_error = CsvParsingError(
        row=0,
        field="Date",
        code=ParsingErrorCode.INVALID_HEADER,
        message="Missing header: 'Date'.",
    )
    expected_failure = ParsingFailure([expected_parsing_error])

    with pytest.raises(ParsingFailure, match=re.escape(str(expected_failure))):
        verify_headers({"xDate", "ShareLink", "ShareCommentary"})


def test_verify_invalid_row(create_csv_post_file) -> None:
    dict_row = {"Date": "", "ShareLink": "", "ShareCommentary": ""}
    parsing_errors = verify_row(dict_row)
    assert len(parsing_errors) == 3
    assert parsing_errors == {
        "Date": ParsingErrorCode.EMPTY_FIELD,
        "ShareLink": ParsingErrorCode.EMPTY_FIELD,
        "ShareCommentary": ParsingErrorCode.EMPTY_FIELD,
    }


def test_verify_valid_row(create_csv_post_file) -> None:
    # Currently no logic on the meaning of fields
    dict_row = {"Date": "xxx", "ShareLink": "xxx", "ShareCommentary": "xxx"}
    parsing_errors = verify_row(dict_row)
    assert len(parsing_errors) == 0


def test_parse_valid_row():
    expected_raw_post = RawPost(
        row=1, date="xxx", share_link="xxx", share_commentary="xxx"
    )
    dict_row = {"Date": "xxx", "ShareLink": "xxx", "ShareCommentary": "xxx"}
    raw_post = parse_row(1, dict_row)
    assert raw_post == expected_raw_post


def test_parse_invalid_row():
    expected_parsing_error = CsvParsingError(
        row=1,
        field="ShareLink",
        code=ParsingErrorCode.EMPTY_FIELD,
        message="'ShareLink' is empty.",
    )
    expected_failure = ParsingFailure([expected_parsing_error])

    with pytest.raises(ParsingFailure, match=re.escape(str(expected_failure))):
        dict_row = {"Date": "xxx", "ShareLink": "", "ShareCommentary": "xxx"}
        parse_row(1, dict_row)


def test_parsing_csv_post_with_missing_headers(create_csv_post_file) -> None:
    mock_rows = [
        ["xDate", "Other", "ShareCommentary"],  # Missing fields
    ]
    csv_file_path = create_csv_post_file(mock_rows)

    parser = CsvParser()
    result = parser.parse_raw_posts(csv_file_path)

    expected_parsing_errors = [
        CsvParsingError(
            row=0,
            field="Date",
            code=ParsingErrorCode.INVALID_HEADER,
            message="Missing header: 'Date'.",
        ),
        CsvParsingError(
            row=0,
            field="ShareLink",
            code=ParsingErrorCode.INVALID_HEADER,
            message="Missing header: 'ShareLink'.",
        ),
    ]
    assert result.raw_posts == []
    assert result.parsing_errors == expected_parsing_errors


def test_parsing_csv_post_with_missing_data(create_csv_post_file) -> None:
    mock_rows = [
        ["Date", "ShareLink", "ShareCommentary"],
        ["", "", ""],
        [
            "2025-01-01 23:59:59",
            "https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%HappyNewYear",
            "",
        ],
    ]
    csv_file_path = create_csv_post_file(mock_rows)

    parser = CsvParser()
    result = parser.parse_raw_posts(csv_file_path)

    expected_parsing_errors = [
        CsvParsingError(
            row=1,
            field="Date",
            code=ParsingErrorCode.EMPTY_FIELD,
            message="'Date' is empty.",
        ),
        CsvParsingError(
            row=1,
            field="ShareLink",
            code=ParsingErrorCode.EMPTY_FIELD,
            message="'ShareLink' is empty.",
        ),
        CsvParsingError(
            row=1,
            field="ShareCommentary",
            code=ParsingErrorCode.EMPTY_FIELD,
            message="'ShareCommentary' is empty.",
        ),
        CsvParsingError(
            row=2,
            field="ShareCommentary",
            code=ParsingErrorCode.EMPTY_FIELD,
            message="'ShareCommentary' is empty.",
        ),
    ]
    assert result.raw_posts == []
    assert result.parsing_errors == expected_parsing_errors


def test_parsing_csv_post_with_data(create_csv_post_file) -> None:
    mock_rows = [
        ["Date", "ShareLink", "ShareCommentary"],
        [
            "2026-11-04 21:24:04",
            "https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A7523857626154266624",
            """𝙀𝙫𝙚𝙧𝙮 𝙨𝙮𝙨𝙩𝙚𝙢 𝙞𝙨 𝙗𝙪𝙞𝙡𝙩 𝙛𝙤𝙧 𝙖 𝙥𝙪𝙧𝙥𝙤𝙨𝙚; 𝙚𝙫𝙚𝙧𝙮 𝙖𝙘𝙩𝙞𝙤𝙣 𝙬𝙚 𝙩𝙖𝙠𝙚 𝙝𝙖𝙨 𝙗𝙤𝙩𝙝 𝙞𝙣𝙩𝙚𝙣𝙙𝙚𝙙 𝙖𝙣𝙙 𝙪𝙣𝙞𝙣𝙩𝙚𝙣𝙙𝙚𝙙 𝙘𝙤𝙣𝙨𝙚𝙦𝙪𝙚𝙣𝙘𝙚𝙨.
         #WorkCulture #ThePhoenixProject #DevOps #SoftwareEngineering
         Content with strange characters: 📖 https://lnkd.in/eDJSJv8y
        "" 1. 𝘾𝙤𝙢𝙥𝙡𝙚𝙭𝙞𝙩𝙮: too many possible states.""
        "" 2. 𝗖𝗼𝗻𝗳𝗼𝗿𝗺𝗶𝘁𝘆: forced to fit ""non-logical"" realities."""
            "",
        ],
    ]
    csv_file_path = create_csv_post_file(mock_rows)

    parser = CsvParser()
    result = parser.parse_raw_posts(csv_file_path)

    expected_raw_post = RawPost(
        row=1,
        date=mock_rows[1][0],
        share_link=mock_rows[1][1],
        share_commentary=mock_rows[1][2],
    )
    assert result.raw_posts == [expected_raw_post]
    assert result.parsing_errors == []
