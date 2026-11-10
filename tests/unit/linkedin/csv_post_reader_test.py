import re

import pytest

from linkedin_idea_to_post.linkedin.csv_post_parser import (
    CSVPostParser,
    parse_row,
    verify_headers,
    verify_row,
)
from linkedin_idea_to_post.linkedin.csv_post_parser_result import CSVPostParserResult
from linkedin_idea_to_post.linkedin.raw_post import RawPost


def test_verify_headers(create_csv_post_file) -> None:
    # no exception raised on valid headers
    verify_headers({"Date", "ShareLink", "ShareCommentary", "xDate"})

    escaped_expected_msg = re.escape(
        "Expected headers not found in CSV file: ['Date']."
    )
    with pytest.raises(Exception, match=escaped_expected_msg):
        verify_headers({"xDate", "ShareLink", "ShareCommentary"})


def test_verify_row(create_csv_post_file) -> None:
    dict_row = {"Date": "", "ShareLink": "", "ShareCommentary": ""}
    missing_fields = verify_row(dict_row)
    assert len(missing_fields) == 3
    assert missing_fields == ["Date", "ShareLink", "ShareCommentary"]

    # Currently no logic on the meaning of fields
    dict_row = {"Date": "xxx", "ShareLink": "xxx", "ShareCommentary": "xxx"}
    missing_fields = verify_row(dict_row)
    assert len(missing_fields) == 0


def test_parse_row():
    result = CSVPostParserResult()
    raw_post = RawPost(date="xxx", share_link="xxx", shareCommentary="xxx")

    dict_row = {"Date": "xxx", "ShareLink": "xxx", "ShareCommentary": "xxx"}
    parse_row(0, dict_row, csv_post_parser_result=result)
    assert result.raw_posts == [raw_post]
    assert result.errors == []

    dict_row = {"Date": "xxx", "ShareLink": "", "ShareCommentary": "xxx"}
    parse_row(0, dict_row, csv_post_parser_result=result)
    assert result.raw_posts == [raw_post]
    assert result.errors == ["Row #1: 'ShareLink' is empty."]


def test_parsing_csv_post_with_missing_headers(create_csv_post_file) -> None:
    mock_rows = [
        ["xDate", "Other", "ShareCommentary"],  # Missing fields
    ]
    csv_file_path = create_csv_post_file(mock_rows)

    escaped_expected_msg = re.escape(
        "Expected headers not found in CSV file: ['Date', 'ShareLink']."
    )
    with pytest.raises(Exception, match=escaped_expected_msg):
        parser = CSVPostParser(csv_file_path)
        parser.parse_raw_posts()


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

    parser = CSVPostParser(csv_file_path)
    result = parser.parse_raw_posts()

    expected_errors = [
        "Row #1: 'Date' is empty.",
        "Row #1: 'ShareLink' is empty.",
        "Row #1: 'ShareCommentary' is empty.",
        "Row #2: 'ShareCommentary' is empty.",
    ]
    assert result.raw_posts == []
    assert result.errors == expected_errors


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

    parser = CSVPostParser(csv_file_path)
    result = parser.parse_raw_posts()

    expected_raw_post = RawPost(
        date="2026-11-04 21:24:04",
        share_link="https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A7523857626154266624",
        shareCommentary="""Every system is built for a purpose; every action we take has both intended and unintended consequences.\n         #WorkCulture #ThePhoenixProject #DevOps #SoftwareEngineering\n         Content with strange characters: 📖 https://lnkd.in/eDJSJv8y\n        "" 1. Complexity: too many possible states.""\n        "" 2. Conformity: forced to fit ""non-logical"" realities."""
        "",
    )
    assert result.raw_posts == [expected_raw_post]
    assert result.errors == []
