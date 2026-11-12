from enum import StrEnum

from pydantic import BaseModel

from linkedin_idea_to_post.domain.post import Post


# Error categories
class ParsingErrorCode(StrEnum):
    INVALID_HEADER = "invalid_header"
    EMPTY_FIELD = "empty_field"


class MappingErrorCode(StrEnum):
    INVALID_DATE_FORMAT = "invalid_date_format"
    INVALID_URL = "invalid_url"


# Structured Error Models
class CsvParsingError(BaseModel):
    row: int
    code: ParsingErrorCode
    message: str


class FieldError(BaseModel):
    field: str
    code: MappingErrorCode
    message: str


class CsvMappingError(BaseModel):
    raw_post: "RawPost"
    errors: list[FieldError]


# Control Flow Exceptions
class ParsingFailure(Exception):
    def __init__(self, errors: list[CsvParsingError]):
        self.errors = errors


class MappingFailure(Exception):
    def __init__(self, errors: list[FieldError]):
        self.errors = errors


# Data & Result Models (Pydantic for easy JSON serialization)
class RawPost(BaseModel):
    row: int
    date: str
    share_link: str
    share_commentary: str


class CsvParserResult(BaseModel):
    raw_posts: list[RawPost] = []
    parsing_errors: list[CsvParsingError] = []

    @property
    def has_errors(self) -> bool:
        return bool(self.parsing_errors)


class CsvImporterResult(BaseModel):
    posts: list[Post] = []
    parsing_errors: list[CsvParsingError] = []
    mapping_errors: list[CsvMappingError] = []
