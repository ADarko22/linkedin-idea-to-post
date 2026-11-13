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
    field: str
    code: ParsingErrorCode
    message: str

    def to_str_tuple(self) -> tuple[str, str, str, str]:
        return (
            str(self.row),
            str(self.field),
            str(self.code.value if hasattr(self.code, "value") else self.code),
            self.message,
        )


class FieldError(BaseModel):
    field: str
    code: MappingErrorCode
    message: str

    def to_str_tuple(self) -> tuple[str, str, str]:
        return (
            str(self.field),
            str(self.code.value if hasattr(self.code, "value") else self.code),
            self.message,
        )


class CsvMappingError(BaseModel):
    raw_post: "RawPost"
    errors: list[FieldError] = []


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


class CsvImporterPrepareResult(BaseModel):
    posts: list[Post] = []
    parsing_errors: list[CsvParsingError] = []
    mapping_errors: list[CsvMappingError] = []


class CsvImporterCommitResult(BaseModel):
    committed_count: int = 0
    # todo enrich with a status enum to cover:
    #  if commit succeeds,
    #  if there are unresolved error (i.e. user validating the CsvImporterPrepareResult)
    #  if there is nothing new to commit (i.e. re-importing same file changes nothing)
