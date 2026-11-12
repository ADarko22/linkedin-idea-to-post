from pathlib import Path

from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.linkedin.csv_importer import CsvImporter
from linkedin_idea_to_post.linkedin.csv_parser import CsvParser


def main():
    share_filename = "/Users/angelo.buono/PycharmProjects/linkedin-idea-to-post/data/imports/LinkedIn-Shares-DataExport.csv"
    share_path = Path(share_filename)

    csv_parser = CsvParser()
    archive_db_filename = "/Users/angelo.buono/PycharmProjects/linkedin-idea-to-post/data/archive/db.sqlite"
    archive_db_path = Path(archive_db_filename)
    archive = SqliteArchive(db_path=archive_db_path)
    csv_importer = CsvImporter(parser=csv_parser, archive=archive)

    importer_result = csv_importer.prepare(share_path)

    print("Parsing Errors Found:")
    print(importer_result.parsing_errors)
    print("Mapping Errors Found:")
    print(importer_result.mapping_errors)
    print("Posts:")
    for post in importer_result.posts:
        print(post)

    csv_importer.commit(importer_result)
    print(f"Imported to SQLite DB at {archive_db_filename}.")


if __name__ == "__main__":
    main()
