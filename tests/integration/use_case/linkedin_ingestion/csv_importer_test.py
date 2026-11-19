from linkedin_idea_to_post.domain.storage import PostGetQuery
from linkedin_idea_to_post.use_case.linkedin_ingestion.csv_importer import CsvImporter
from linkedin_idea_to_post.use_case.linkedin_ingestion.csv_parser import CsvParser


def test_prepare_and_commit_persists_valid_posts(
    create_csv_post_file, in_memory_post_store_manager, in_memory_post_storage
) -> None:
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
        [
            "2022-08-16 13:56:28",
            "https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%3A6965305280901324800",
            "“There may be people that have more talent than you, but there’s no excuse for anyone to work harder than you do.”",
        ],
        [
            "2022-38-36 13:56:28",
            "https://www.linkedin.com/feed/update/urn%3Ali%3Ashare%",
            "Raw Post with Mapping Errors.",
        ],
        ["", "", "Raw Post with Parsing Errors."],
    ]
    csv_file_path = create_csv_post_file(mock_rows)

    parser = CsvParser()
    importer = CsvImporter(parser, in_memory_post_store_manager)

    result = importer.prepare(csv_file_path)
    assert len(result.posts) == 2
    assert len(result.parsing_errors) == 2
    assert len(result.mapping_errors) == 1
    assert len(result.mapping_errors[0].errors) == 2

    stored_posts = in_memory_post_storage.get_all(PostGetQuery())
    assert len(stored_posts) == 0

    importer.commit(prepare_result=result)

    stored_posts = in_memory_post_storage.get_all(PostGetQuery())
    assert len(stored_posts) == 2
