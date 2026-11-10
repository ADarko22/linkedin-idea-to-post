# LinkedIn Idea to Post Linkedin

This directory contains the LinkedIn-specific components and logic.

## Content

1. [raw_post.py](raw_post.py): Contains the `RawPost` class, which represents the content of LinkedIn `Shares.csv`
   files, downloaded from https://www.linkedin.com/mypreferences/d/download-my-data.
2. [csv_post_parser.py](csv_post_parser.py): Contains the `CSVPostReader` class, which is responsible for reading and
   parsing the `Shares.csv` file into `CSVPostParserResult` object. It collects the raw posts and errors encountered
   during parsing, namely empty fields (for now).
3. [csv_post_parser_result.py](csv_post_parser_result.py): Contains the `CSVPostParserResult` class, which holds the
   result of parsing the `Shares.csv` file, including a list of `RawPost` objects and any parsing errors.
4. [raw_posts_importer.py](raw_posts_importer.py): Contains the `RawPostsImporter` class, which is responsible for
   importing `RawPost` objects as `domain/Post` objects, from `CSVPostParserResult` into the application archive.

