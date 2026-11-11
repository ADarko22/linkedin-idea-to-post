import csv
import unicodedata
from enum import StrEnum

from linkedin_idea_to_post.linkedin.model import (
    CsvParserResult,
    CsvParsingError,
    ParsingErrorCode,
    RawPost,
)


class CsvPostHeader(StrEnum):
    DATE = "Date"
    SHARE_LINK = "ShareLink"
    SHARE_COMMENTARY = "ShareCommentary"

    @classmethod
    def value_to_enum_dict(cls) -> dict[str, "CsvPostHeader"]:
        """Returns a dictionary mapping the string value to the enum member."""
        return {member.value: member for member in cls}


def verify_headers(headers: set[str]) -> CsvParsingError | None:
    """
    Verifies that the headers are present in the CSV file.
    """
    missing_headers = []
    for header in CsvPostHeader.value_to_enum_dict().keys():
        if header not in headers:
            missing_headers.append(header)

    if len(missing_headers) > 0:
        error_message = f"Missing headers: {missing_headers}."
        return CsvParsingError(
            row=0, code=ParsingErrorCode.INVALID_HEADER, message=error_message
        )

    return None


def verify_row(row: dict) -> dict[str, ParsingErrorCode]:
    """
    Verifies that the row is in the expected format. Returns the missing fields.
    """
    parsing_errors = {}
    for field in CsvPostHeader.value_to_enum_dict().keys():
        if row[field] == "":
            parsing_errors.update({field: ParsingErrorCode.EMPTY_FIELD})
    return parsing_errors


def parse_row(row_num: int, row: dict, csv_parser_result: CsvParserResult) -> None:
    """
    Parses a single row of the CSV file, by updating (as side effect) the csv_parser_result.
    It verifies and reports any missing fields in the row.
    It performs NFKC (Normalization Form Compatibility Composition) on the 'ShareCommentary' field,
    to clean up the look-alike UNICODE formatting, before creating a RawPost object.
    """
    parsing_errors = verify_row(row)
    if len(parsing_errors) > 0:
        for field, parsing_error_code in parsing_errors.items():
            error_message = f"'{field}' is empty."
            parsing_error = CsvParsingError(
                row=row_num, code=parsing_error_code, message=error_message
            )
            csv_parser_result.parsing_errors.append(parsing_error)
    else:
        normalized_share_commentary = unicodedata.normalize(
            "NFKD", row[CsvPostHeader.SHARE_COMMENTARY.value]
        )

        raw_post = RawPost(
            row=row_num,
            date=row[CsvPostHeader.DATE.value],
            share_link=row[CsvPostHeader.SHARE_LINK.value],
            share_commentary=normalized_share_commentary,
        )
        csv_parser_result.raw_posts.append(raw_post)


class CsvParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_raw_posts(self) -> CsvParserResult:
        """
        Parses the CSV file and returns a CSVPostParserResult object.
        """
        csv_parser_result = CsvParserResult()

        with open(self.file_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            headers = set(reader.fieldnames) if reader.fieldnames else set()
            parsing_header_error = verify_headers(headers)

            if parsing_header_error is not None:
                csv_parser_result.parsing_errors.append(parsing_header_error)
                return csv_parser_result

            rows = list(reader)

        for row_num in range(len(rows)):
            row = rows[row_num]
            # passing row_num + 1 to account for the header
            parse_row(row_num + 1, row, csv_parser_result)

        return csv_parser_result
