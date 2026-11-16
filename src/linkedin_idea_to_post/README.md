# LinkedIn Idea to Post

## Architecture

### Drafting Components

```mermaid
C4Component
    Container_Boundary(draft_b, "Drafting") {
        Component(drafter, "DraftService", "Drafter")
    }

    System_Boundary(domain_b, "Domain") {
        Component(writer_p, "DraftWriter", "Protocol")
        Component(storage_p, "PostStorage", "Protocol")
        Component(post_m, "Post", "Data Model")
        Component(retriever_p, "PostRetriever", "Protocol")
    }

    Container_Boundary(workflow_b, "AI Workflow") {
        Component(writer, "CrewaiDraftWriter", "CrewAI")
    }
    
    Container_Boundary(storage_b, "storage") {
        ComponentDb(storage, "SqlitePostStorage", "SQLite")
        ComponentDb(retriever, "SqlitePostRetriever", "SQLite")
    }

    Rel_R(drafter, writer_p, "uses")
    Rel_R(drafter, post_m, "creates")
    Rel_R(drafter, storage_p, "uses")
    Rel_R(drafter, retriever_p, "uses")
    Rel_L(writer, writer_p, "implements")
    Rel_L(storage, storage_p, "implements")
    Rel_L(retriever, retriever_p, "implements")
    UpdateLayoutConfig($c4ShapeInRow="1", $c4BoundaryInRow="4")
```

### Importing Components

```mermaid
C4Component
    Container_Boundary(ingestion_b, "Linkedin (Ingestion)") {
        Component(importer, "CsvImporter", "Importer")
    }

    System_Boundary(domain_b, "Domain") {
        Component(post_m, "Post", "Data Model")
        Component(storage_p, "PostStorage", "Protocol")
        Component(retriever_p, "PostRetriever", "Protocol")
    }

    Container_Boundary(storage_b, "storage") {
        ComponentDb(storage, "SqlitePostStorage", "SQLite")
    }

    Rel_R(importer, post_m, "creates")
    Rel_R(importer, storage_p, "uses")
    Rel_L(storage, storage_p, "implements")
    UpdateLayoutConfig($c4ShapeInRow="1", $c4BoundaryInRow="3")
```

_Note: visualize it on  [mermaid.ai](https://mermaid.ai/live) if the Markdown render doesn't work._

## Operational Flows

### Drafting a post from an idea

Prompting the "idea" message to the [`DraftService`](drafting/draft_service.py) to generate a draft of a LinkedIn [
`Post`](domain/post.py).

```mermaid
flowchart LR
    A[Write an idea] -- call --> B[DraftService]
    B -- generates --> C[Post]
```

### Importing posts from ~~LinkedIn~~

~~~~
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

