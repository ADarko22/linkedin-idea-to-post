from pathlib import Path

from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.linkedin.csv_parser import CsvParser
from linkedin_idea_to_post.linkedin.mapper import (
    raw_post_to_post,
)
from linkedin_idea_to_post.linkedin.model import (
    CsvImporterResult,
    CsvMappingError,
    CsvParserResult,
    MappingFailure,
)


def process_parser_result(parser_result: CsvParserResult) -> CsvImporterResult:
    importer_result = CsvImporterResult(parsing_errors=parser_result.parsing_errors)

    for raw_post in parser_result.raw_posts:
        try:
            post = raw_post_to_post(raw_post)
            importer_result.posts.append(post)
        except MappingFailure as failure:
            mapping_error = CsvMappingError(raw_post=raw_post, errors=failure.errors)
            importer_result.mapping_errors.append(mapping_error)

    return importer_result


class CsvImporter:
    def __init__(self, archive: SqliteArchive):
        self.archive = archive

    def prepare(self, file_path: Path) -> CsvImporterResult:
        """
        Prepares the import of the posts contained in the CSV file, by parsing the raw data,
        mapping it to Post objects, and collecting eventual errors.
        """
        csv_parser = CsvParser(file_path)
        parser_result = csv_parser.parse_raw_posts()
        import_result = process_parser_result(parser_result)
        return import_result

    def commit(self, import_result: CsvImporterResult) -> bool:
        """
        Commits the import of the posts extracted from the CSV file, by persisting to the application archive.
        """
        # todo model appropriate return: errors when import is not prepared, or errors have not been "resolved"

        for post in import_result.posts:
            self.archive.save(post)
            # todo: improve with a save_all as a batch statement
        return True
