# LinkedIn Idea to Post – Post Management

This directory contains the orchestration logic for coordinating writes across `PostStorage` and `PostEmbeddingStorage`
as atomic operations by leveraging the **Unit of Work** pattern.

The main components are the `UnitOfWork` protocol (context manager contract for transaction boundaries) and
[PostStoreManagementService](post_post_management_service.py), which coordinates embedding generation and keeps `posts`
and `post_embeddings` consistent as a single unit of work.

## Post Store Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant StoreManager as PostStoreManagementService
    participant Embedder as EmbeddingGenerator
    participant Storage as PostStorage
    participant EmbeddingStorage as PostEmbeddingStorage
    Note over User, EmbeddingStorage: 1. Save Post Operation
    User ->> StoreManager: save_post(post)
    activate StoreManager
    StoreManager ->> Embedder: generate(post)
    activate Embedder
    Note over Embedder: Compute Vector Embedding
    Embedder ->> StoreManager: PostEmbedding
    deactivate Embedder
    Note over StoreManager: Starts a UnitOfWork
    StoreManager ->> Storage: save(post)
    activate Storage
    Note over Storage: Creates and Stores the JSON Document
    deactivate Storage
    StoreManager ->> EmbeddingStorage: save(post_embedding)
    activate EmbeddingStorage
    Note over EmbeddingStorage: Creates and Stores the Float Embedding Array
    deactivate EmbeddingStorage
    Note over StoreManager: Closes a UnitOfWork (commit or rollback)
    deactivate StoreManager
    Note over User, EmbeddingStorage: 2. Delete Post Operation
    User ->> StoreManager: delete_post(post)
    activate StoreManager
    Note over StoreManager: Starts a UnitOfWork
    StoreManager ->> EmbeddingStorage: delete(post.id)
    activate EmbeddingStorage
    Note over EmbeddingStorage: Deletes post embedding
    deactivate EmbeddingStorage
    StoreManager ->> Storage: delete(post.id)
    activate Storage
    Note over Storage: Deletes post
    deactivate Storage
    Note over StoreManager: Closes a UnitOfWork (commit or rollback)
    deactivate StoreManager


```

## Main Components

### The `UnitOfWork` Protocol

Defines the context manager contract (`__enter__` and `__exit__`) used in `with` blocks to group statements into an
all-or-nothing transaction: committing when the block exits cleanly, and rolling back if an exception is raised.

| Method / Hook                                | Description                                                                                            |
|----------------------------------------------|--------------------------------------------------------------------------------------------------------|
| `__enter__() -> Self`                        | Enters the transaction context and returns the context manager instance for use in a `with` statement. |
| `__exit__(exc_type, exc_val, exc_tb) -> bool | None`                                                                                                  | Commits if no exception occurred (`exc_type is None`), or rolls back and lets exceptions propagate. |

### The [PostStoreManagementService](https://www.google.com/search?q=post_write_management_service.py)

The `PostStoreManagementService` class coordinates multi-table writes across `PostStorage` and `PostEmbeddingStorage`
within a `UnitOfWork` so partial updates are never left behind on failure. Storage implementations execute statements
directly without opening their own commit/rollback boundaries.

| Method                          | Description                                                                                              |
|---------------------------------|----------------------------------------------------------------------------------------------------------|
| `save_post(post: Post) -> None` | Generates a `PostEmbedding` for `post` and saves both `post` and `post_embedding` inside `unit_of_work`. |
| `delete_post(post_id: UUID)`    | Deletes the embedding and post for `post_id` atomically inside `unit_of_work`.                           |

## External Boundaries

1. [Post](../../domain/post.py) (from domain): the core entity across the application, created by the import process and
   stored in via the persistence layer.
2. [PostStorage](../../domain/storage.py) (from domain): the persistence protocol for CRUD operations on `Post`.
3. [EmbeddingGenerator](../../domain/embedding.py) (from domain): the embedding protocol
4. [PostEmbeddingStorage](../../domain/storage.py) (from domain): the persistence protocol for CRUD operations on
   `PostEmbedding`.

