import csv
import unicodedata
from enum import StrEnum

from linkedin_idea_to_post.linkedin.csv_post_parser_result import CSVPostParserResult
from linkedin_idea_to_post.linkedin.raw_post import RawPost


class CSVPostHeader(StrEnum):
    DATE = "Date"
    SHARE_LINK = "ShareLink"
    SHARE_COMMENTARY = "ShareCommentary"

    @classmethod
    def value_to_enum_dict(cls) -> dict[str, "CSVPostHeader"]:
        """Returns a dictionary mapping the string value to the enum member."""
        return {member.value: member for member in cls}


def verify_headers(headers: set[str]):
    """
    Verifies that the headers are present in the CSV file.
    """
    missing_headers = []
    for header in CSVPostHeader.value_to_enum_dict().keys():
        if header not in headers:
            missing_headers.append(header)
    if len(missing_headers) > 0:
        raise Exception(
            f"Expected headers not found in CSV file: {str(missing_headers)}."
        )


def verify_row(row: dict) -> list[str]:
    """
    Verifies that the row is in the expected format. Returns the missing fields.
    """
    missing_fields = []
    for field in CSVPostHeader.value_to_enum_dict().keys():
        if row[field] == "":
            missing_fields.append(field)
    return missing_fields


def parse_row(
    row_num: int, row: dict, csv_post_parser_result: CSVPostParserResult
) -> None:
    """
    Parses a single row of the CSV file, by updating (as side effect) the csv_post_parser_result.
    It verifies and reports any missing fields in the row.
    It performs NFKC (Normalization Form Compatibility Composition) on the 'ShareCommentary' field,
    to clean up the look-alike UNICODE formatting, before creating a RawPost object.
    """
    missing_fields = verify_row(row)
    if len(missing_fields) > 0:
        for missing_field in missing_fields:
            error_message = f"Row #{row_num + 1}: '{missing_field}' is empty."
            csv_post_parser_result.add_error(error_message)
    else:
        normalized_share_commentary = unicodedata.normalize(
            "NFKD", row[CSVPostHeader.SHARE_COMMENTARY.value]
        )

        raw_post = RawPost(
            date=row[CSVPostHeader.DATE.value],
            share_link=row[CSVPostHeader.SHARE_LINK.value],
            shareCommentary=normalized_share_commentary,
        )
        csv_post_parser_result.raw_posts.append(raw_post)


class CSVPostParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_raw_posts(self) -> CSVPostParserResult:
        """
        Parses the CSV file and returns a CSVPostParserResult object.

        """
        with open(self.file_path, newline="", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)

            headers = set(reader.fieldnames) if reader.fieldnames else set()
            verify_headers(headers)

            rows = list(reader)

        csv_post_parser_result = CSVPostParserResult()
        for row_num in range(len(rows)):
            row = rows[row_num]
            parse_row(row_num, row, csv_post_parser_result)

        return csv_post_parser_result
