# LinkedIn Idea to Post

## Architecture

### Post Management Components

The Use Case for correctly managing `Post`.

- `PostStoreManagementService` is the component for saving `Post` objects, ensuring that the corresponding
  `PostEmbedding` object is generated and stored along atomically.

```mermaid
C4Container
    Container_Boundary(manager_b, "Post Manager") {
        Component(write_manager, "PostStoreManagementService", "Use Case")
        Component(uow_p, "UnitOfWork", "Protocol")
    }

    System_Boundary(domain_b, "Domain") {
        Component(post_embedding_m, "PostEmbedding", "Data Model")
        Component(embedding_p, "EmbeddingGenerator", "Protocol")
        Component(post_m, "Post", "Data Model")
        Component(storage_p, "PostStorage", "Protocol")
        Component(embedding_storage_p, "PostEmbeddingStorage", "Protocol")
    }

    Container_Boundary(storage_b, "Storage Adapter") {
        ComponentDb(storage, "SqlitePostStorage", "SQLite")
        ComponentDb(embedding_storage, "SqlitePostEmbeddingStorage", "SQLite")
        ComponentDb(uow, "SqliteUnitOfWork", "SQLite")
    }

    Container_Boundary(embedding_b, "Embedding Adapter") {
        Component(pytorch_embedding_gen, "PyTorchEmbeddingGenerator", "PyTorch")
    }

    Rel_R(write_manager, uow_p, "uses")
    Rel_R(uow_p, storage_p, "orchestrates")
    Rel_R(uow_p, embedding_storage_p, "orchestrates")
    Rel_R(write_manager, embedding_p, "uses")
    Rel_L(pytorch_embedding_gen, embedding_p, "implements")
    Rel_L(storage, storage_p, "implements")
    Rel_L(embedding_storage, embedding_storage_p, "implements")
    Rel_L(uow, uow_p, "implements")
    UpdateLayoutConfig($c4ShapeInRow="1", $c4BoundaryInRow="4")
```

### Drafting Components

The Use Case for drafting a `Post` with an AI Writer.

- `DraftService` orchestrates writing of a `Draft` or a `Post` via the `DraftWriter` (i.e. `CrewaiDraftWriter`), and the
  consistent saving of the generated `Post` via `PostStoreManagementService`.

```mermaid
C4Container
    Container_Boundary(draft_b, "Drafting") {
        Component(drafter, "DraftService", "Use Case")
    }

    Container_Boundary(post_manager_b, "Post Manager") {
        Component(post_store_manager, "PostStoreManagementService", "Use Case")
    }

    System_Boundary(domain_b, "Domain") {
        Component(post_m, "Post", "Data Model")
        Component(retriever_p, "PostRetriever", "Protocol")
        Component(writer_p, "DraftWriter", "Protocol")
    }

    Container_Boundary(storage_b, "Storage Adapter") {
        ComponentDb(retriever, "SqlitePostRetriever", "SQLite")
    }

    Container_Boundary(workflow_b, "AI Workflow ADapter") {
        Component(writer, "CrewaiDraftWriter", "CrewAI")
    }

    Rel_R(drafter, writer_p, "uses")
    Rel_R(drafter, post_store_manager, "uses")
    Rel_R(drafter, retriever_p, "uses")
    Rel_L(writer, writer_p, "implements")
    Rel_L(retriever, retriever_p, "implements")
    UpdateLayoutConfig($c4ShapeInRow="1", $c4BoundaryInRow="5")
```

- `DraftContextService` orchestrates `Post` retrieval to build the right `DraftContext`.

```mermaid
C4Container
    Container_Boundary(draft_b, "Drafting") {
        Component(context_builder, "DraftContextService", "Use Case")
    }

    System_Boundary(domain_b, "Domain") {
        Component(post_m, "Post", "Data Model")
        Component(retriever_p, "PostRetriever", "Protocol")
        Component(post_embedding_m, "PostEmbedding", "Data Model")
        Component(embedder_p, "EmbeddingGenerator", "Protocol")
        Component(draft_context_m, "DraftContext", "Data Model")
    }

    Container_Boundary(storage_b, "Storage Adapter") {
        ComponentDb(retriever, "SqlitePostRetriever", "SQLite")
    }

    Container_Boundary(embedding_b, "Embedding Adapter") {
        ComponentDb(embedder, "PyTorchEmbeddingGenerator", "PyTorch")
    }

    Rel_R(context_builder, retriever_p, "uses")
    Rel_R(context_builder, embedder_p, "uses")
    Rel_L(embedder, embedder_p, "implements")
    Rel_L(retriever, retriever_p, "implements")
    UpdateLayoutConfig($c4ShapeInRow="1", $c4BoundaryInRow="5")
```

### Importing Components

The Use Case for ingesting `Post` objects from the `Shares.csv` file, downloaded
from [LinkedIn's data export page](https://www.linkedin.com/mypreferences/d/download-my-data).

- `CsvImporter` orchestrates the parsing of a `Shares.csv` file with `CsvParser`, the mapping to `Post` objects and the
  correctly save it via `PostStoreManagementService`.

```mermaid
C4Component
    Container_Boundary(ingestion_b, "Linkedin (Ingestion)") {
        Component(importer, "CsvImporter", "Use Case")
        Component(parser, "CsvParser", "Utility")
    }

    Container_Boundary(post_manager_b, "Post Manager") {
        Component(post_store_manager, "PostStoreManagementService", "Use Case")
    }

    System_Boundary(domain_b, "Domain") {
        Component(post_m, "Post", "Data Model")
    }

    Rel_R(importer, parser, "uses")
    Rel_R(importer, post_store_manager, "uses")
    UpdateLayoutConfig($c4ShapeInRow="1", $c4BoundaryInRow="3")
```

_Note: visualize it on  [mermaid.ai](https://mermaid.ai/live) if the Markdown render doesn't work._

## Operational Flows

### Drafting a post from an idea

Prompting the "idea" message to the [`DraftService`](use_case/drafting/draft_service.py) to generate a draft of a
LinkedIn [
`Post`](domain/post.py).

```mermaid
flowchart TD
    subgraph GraphA["Phase 1: Build DraftContext from the idea"]
        direction LR
        A[Build context for an idea] -- use --> B[DraftContextService]
        B ---> DraftContext
    end

    subgraph  GraphB["Phase 2: Synchronous Ingestion (Automated)"]
        direction LR
        C[Write an idea] -- use with DraftContext --> D[DraftService]
        D[DraftService] -- generates --> Draft
    end
    
    GraphA --> GraphB
```

### Importing posts from _LinkedIn_

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

