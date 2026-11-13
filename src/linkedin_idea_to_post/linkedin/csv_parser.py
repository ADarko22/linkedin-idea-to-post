import csv
from enum import StrEnum

from linkedin_idea_to_post.linkedin.model import (
    CsvParserResult,
    CsvParsingError,
    ParsingErrorCode,
    ParsingFailure,
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


def verify_headers(headers: set[str]):
    """
    Verifies that the headers are present in the CSV file. Raises a ParsingFailure exception if not.
    """
    missing_headers = []
    for header in CsvPostHeader.value_to_enum_dict().keys():
        if header not in headers:
            missing_headers.append(header)

    if len(missing_headers) > 0:
        parsing_errors = [
            CsvParsingError(
                row=0,
                field=header,
                code=ParsingErrorCode.INVALID_HEADER,
                message=f"Missing header: '{header}'.",
            )
            for header in missing_headers
        ]
        raise ParsingFailure(parsing_errors)


def verify_row(row: dict) -> dict[str, ParsingErrorCode]:
    """
    Verifies that the row is in the expected format, and returns the error code by field found.
    """
    parsing_error_codes = {}
    for field in CsvPostHeader.value_to_enum_dict().keys():
        if row[field] == "":
            parsing_error_codes.update({field: ParsingErrorCode.EMPTY_FIELD})
    return parsing_error_codes


def build_parsing_failure(
    row_num: int, parsing_error_codes: dict[str, ParsingErrorCode]
) -> ParsingFailure:
    """
    Builds a ParsingFailure object from the parsing error codes.
    """
    parsing_errors = []
    for field, parsing_error_code in parsing_error_codes.items():
        error_message = f"'{field}' is empty."
        parsing_error = CsvParsingError(
            row=row_num, field=field, code=parsing_error_code, message=error_message
        )
        parsing_errors.append(parsing_error)
    return ParsingFailure(parsing_errors)


def parse_row(row_num: int, row: dict) -> RawPost:
    """
    Parses a single row of the CSV file, by returning a RawPost object or raising a ParsingFailure exception.
    It verifies and reports any missing fields in the row.
    """
    parsing_error_codes = verify_row(row)
    if len(parsing_error_codes) > 0:
        raise build_parsing_failure(row_num, parsing_error_codes)
    else:
        return RawPost(
            row=row_num,
            date=row[CsvPostHeader.DATE.value],
            share_link=row[CsvPostHeader.SHARE_LINK.value],
            share_commentary=row[CsvPostHeader.SHARE_COMMENTARY.value],
        )


class CsvParser:
    def parse_raw_posts(self, file_path) -> CsvParserResult:
        """
        Parses the CSV file and returns a CSVPostParserResult object.
        """
        csv_parser_result = CsvParserResult()

        with open(file_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            headers = set(reader.fieldnames) if reader.fieldnames else set()
            try:
                verify_headers(headers)
            except ParsingFailure as failure:
                csv_parser_result.parsing_errors.extend(failure.errors)
                return csv_parser_result

            rows = list(reader)

        for row_num in range(len(rows)):
            row = rows[row_num]
            try:
                # passing row_num + 1 to account for the header
                raw_post = parse_row(row_num + 1, row)
                csv_parser_result.raw_posts.append(raw_post)
            except ParsingFailure as failure:
                csv_parser_result.parsing_errors.extend(failure.errors)

        return csv_parser_result
