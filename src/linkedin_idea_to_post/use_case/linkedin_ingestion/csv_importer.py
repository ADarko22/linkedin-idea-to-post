from pathlib import Path

from linkedin_idea_to_post.use_case.linkedin_ingestion.csv_parser import CsvParser
from linkedin_idea_to_post.use_case.linkedin_ingestion.mapper import (
    raw_post_to_post,
)
from linkedin_idea_to_post.use_case.linkedin_ingestion.model import (
    CsvImporterCommitResult,
    CsvImporterPrepareResult,
    CsvMappingError,
    CsvParserResult,
    MappingFailure,
)
from linkedin_idea_to_post.use_case.post_management.post_post_management_service import (
    PostStoreManagementService,
)


def process_parser_result(parser_result: CsvParserResult) -> CsvImporterPrepareResult:
    importer_result = CsvImporterPrepareResult(
        parsing_errors=parser_result.parsing_errors
    )

    for raw_post in parser_result.raw_posts:
        try:
            post = raw_post_to_post(raw_post)
            importer_result.posts.append(post)
        except MappingFailure as failure:
            mapping_error = CsvMappingError(raw_post=raw_post, errors=failure.errors)
            importer_result.mapping_errors.append(mapping_error)

    return importer_result


class CsvImporter:
    def __init__(
        self, parser: CsvParser, post_store_manager: PostStoreManagementService
    ):
        self.csv_parser = parser
        self.post_store_manager = post_store_manager

    def prepare(self, file_path: Path) -> CsvImporterPrepareResult:
        """
        Prepares the import of the posts contained in the CSV file, by parsing the raw data,
        mapping it to Post objects, and collecting eventual errors.
        """
        parser_result = self.csv_parser.parse_raw_posts(file_path)
        prepare_result = process_parser_result(parser_result)
        return prepare_result

    def commit(
        self, prepare_result: CsvImporterPrepareResult
    ) -> CsvImporterCommitResult:
        """
        Commits the import of the posts extracted from the CSV file, by persisting to the application persistence.
        """
        for post in prepare_result.posts:
            self.post_store_manager.save_post(post)

        committed_count = len(prepare_result.posts)
        return CsvImporterCommitResult(committed_count=committed_count)
