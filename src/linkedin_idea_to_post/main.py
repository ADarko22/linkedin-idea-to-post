from pathlib import Path

from linkedin_idea_to_post.archive.sqlite_archive import SqliteArchive
from linkedin_idea_to_post.linkedin.csv_importer import CsvImporter


def main():
    share_filename = "/Users/angelo.buono/PycharmProjects/linkedin-idea-to-post/data/imports/LinkedIn-Shares-DataExport.csv"
    share_path = Path(share_filename)

    archive = SqliteArchive()
    csv_post_importer = CsvImporter(archive)

    importer_result = csv_post_importer.prepare(share_path)

    print("Parsing Errors Found:")
    print(importer_result.parsing_errors)
    print("Mapping Errors Found:")
    print(importer_result.mapping_errors)
    print("Posts:")
    for post in importer_result.posts:
        print(post)


if __name__ == "__main__":
    main()
