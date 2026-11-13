# LinkedIn Idea to Post

## Architecture

todo - add component diagrams with the boundaries between modules (top-down view)

```mermaid
architecture-beta
    group api(cloud)[API]

    service db(database)[Database] in api
    service disk1(disk)[Storage] in api
    service disk2(disk)[Storage] in api
    service server(server)[Server] in api

    db:L -- R:server
    disk1:T -- B:server
    disk2:T -- B:db

```

## Operational Flows

### Drafting a post from an idea

Prompting the "idea" message to the [`DraftService`](drafting/draft_service.py) to generate a draft of a LinkedIn [
`Post`](domain/post.py).

```mermaid
flowchart LR
    A[Write an idea] -- call --> B[DraftService]
    B -- generates --> C[Post]
```

### Importing posts from LinkedIn

Downloading the LinkedIn data from [download-my-data](https://www.linkedin.com/mypreferences/d/download-my-data) and
importing the Shares.csv file with [`CsvImporter`](linkedin/csv_importer.py).

```mermaid
flowchart TD
    subgraph Async["Phase 1: Asynchronous Acquisition (Manual)"]
        direction LR
        A[Request LinkedIn Data] -->|Async up to 24h| B[Receive Email & Download ZIP]
        B --> C[Extract Shares.csv Locally]
    end

    subgraph Sync["Phase 2: Synchronous Ingestion (Automated)"]
        direction LR
        D[Prepare Import: Parse & Validate] --> E[Commit Import: Save to SQLite]
    end

    Async --> Sync
```

