# LinkedIn Idea to Post Linkedin

This directory contains the LinkedIn-specific components and logic.

## Content

1. [model.py](model.py): Contains the modeling of parsing, mapping and importing errors, and the raw post.
    - `RawPost` class, which represents the content of a LinkedIn `Shares.csv` file, downloaded
      from https://www.linkedin.com/mypreferences/d/download-my-data.
    - `CsvParserResult` class, represents the main output from parsing the csv file into a list of `RawPost` objects and
      a list `CsvParsingError`, which are structured errors propagated to the user.
    - `CsvImporterResult` class is the cross-boundary contract. It represents the output of importing the csv file,
      containing a list of `Post` objects (from the [domain](../domain) module), a list of `CsvParsingError` and a
      list of `CsvMappingError`.

2. [csv_parser.py](csv_parser.py): Contains the `CsvParser` class, responsible for reading and parsing the `Shares.csv`
   file into a `CsvParserResult` object.

3. [csv_importer.py](csv_importer.py): Contains the`CsvImporter` class, responsible for importing the `Shares.csv` file
   into the application. It uses `CsvParser` for extracting `RawPost` objects, and maps those to `Post` objects (from
   the [domain](../domain) module), by producing a `CsvImporterResult` object. Once the `CsvImporterResult` object is
   validated, then the `Post` objects are stored within the application persistence layer, via `SqliteArchive` (from
   the [archive](../archive) module).

