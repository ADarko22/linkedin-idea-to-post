# LinkedIn Idea to Post

This directory contains the LinkedIn-specific components and logic for importing LinkedIn posts into the application.

## Content

### 1. [model.py](model.py)

Defines the data models used throughout the CSV parsing and importing process:

- **`RawPost`**: Represents a raw post extracted from LinkedIn's `Shares.csv` file, downloaded from [LinkedIn's data export page](https://www.linkedin.com/mypreferences/d/download-my-data).
- **`CsvParserResult`**: Represents the output of CSV parsing, containing:
  - A list of `RawPost` objects.
  - A list of `CsvParsingError` objects, representing structured parsing errors propagated to the user.
- **`CsvImporterResult`**: Defines the contract across the importing boundary, containing:
  - A list of `Post` objects from the [domain](../domain) module.
  - A list of `CsvParsingError` objects.
  - A list of `CsvMappingError` objects.

### 2. [csv_parser.py](csv_parser.py)

Defines the `CsvParser` class, responsible for reading and parsing the `Shares.csv` file into a `CsvParserResult`.

### 3. [csv_importer.py](csv_importer.py)

Defines the `CsvImporter` class, responsible for importing LinkedIn posts into the application.

The importer:

1. Uses `CsvParser` to extract `RawPost` objects from the CSV file.
2. Maps the extracted data into `Post` objects from the [domain](../domain) module.
3. Produces a `CsvImporterResult` containing the imported posts and any parsing or mapping errors.
4. Once the `CsvImporterResult` is validated, stores the `Post` objects in the application's persistence layer through `SqliteArchive` from the [archive](../archive) module.