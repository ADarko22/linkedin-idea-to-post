# LinkedIn Idea to Post – Domain

This directory contains the core domain models and boundary contracts, ensuring the domain module remains independent of
external implementation details.

## Main Components

### 1. [post.py](post.py)

Defines the `Post` class, representing a LinkedIn post.

| Attribute    | Description                                                                              |
|--------------|------------------------------------------------------------------------------------------|
| **body**     | The post's textual content.                                                              |
| **hashtags** | The hashtags contained in the post.                                                      |
| **Metadata** | Additional information associated with the post, such as timestamps, origin, and status. |

Defines the `PostEmbedding` class, presenting the embedding of a `Post`.

| Attribute           | Description                                                          |
|---------------------|----------------------------------------------------------------------|
| **post_id**         | The `id` of the post referenced.                                     |
| **embedding_model** | The name of the embedding model used for creating the embedding.     |
| **vector**          | The embedding vector, i.e. an array of float.                        |
| **Metadata**        | Additional information associated with the post, such as timestamps. |

**Timestamps:** All timestamps use UTC to ensure consistency across different time zones.

### 2. [drafting.py](drafting.py)

Defines the `DraftWriter` protocol, which abstracts the logic responsible for transforming the user's idea into a
LinkedIn post draft.

| Method                                  | Description                                           |
|-----------------------------------------|-------------------------------------------------------|
| `write(request: DraftRequest) -> Draft` | Generates a LinkedIn post draft from the user's idea. |

### 3. [storage.py](storage.py)

Defines the `PostStorage` protocol for CRUD operations on `Post` objects.

| Method                  | Input                                                                            | Output         | Description                                                                    |
|-------------------------|----------------------------------------------------------------------------------|----------------|--------------------------------------------------------------------------------|
| `save(post)`            | `Post`                                                                           | `None`         | Saves a post to the SQLite database.                                           |
| `delete(post_id)`       | `UUID`                                                                           | `None`         | Deletes the post by ID.                                                        |
| `get(post_id)`          | `UUID`                                                                           | `Post \| None` | Retrieves a post by ID, or returns `None` if it is not found.                  |
| `get_all(PostGetQuery)` | `PostGetQuery`, specifying status and origin filters, page size, and page number | `list[Post]`   | Retrieves posts from newest to oldest, with optional filtering and pagination. |

Defines the `PostEmbeddingStorage` protocol for CRUD operations on `PostEmbedding` objects.

| Method                  | Input                                                                            | Output                  | Description                                                                              |
|-------------------------|----------------------------------------------------------------------------------|-------------------------|------------------------------------------------------------------------------------------|
| `save(post_embedding)`  | `PostEmbedding`                                                                  | `None`                  | Saves a post emdding to the SQLite database.                                             |
| `delete(post_id)`       | `UUID`                                                                           | `None`                  | Deletes the post embedding by post ID.                                                   |
| `get(post_id)`          | `UUID`                                                                           | `PostEmbedding \| None` | Retrieves a post embedding by ID, or returns `None` if it is not found.                  |
| `get_all(PostGetQuery)` | `PostGetQuery`, specifying status and origin filters, page size, and page number | `list[PostEmbedding]`   | Retrieves post embeddings from newest to oldest, with optional filtering and pagination. |

### 4. [retrieval.py](retrieval.py)

Defines the `PostRetriever` protocol for advanced searches on `Post` objects, such as Full-Text searches and
semantic/vector searches.

| Method                              | Input                                                                                      | Output       | Description                                              |
|-------------------------------------|--------------------------------------------------------------------------------------------|--------------|----------------------------------------------------------|
| `full_text_search(PostSearchQuery)` | `PostSearchQuery`, specifying search text, the status and origin filters, and max results. | `list[Post]` | Retrieves posts based on FTS5 and BM25 algorithms.       |
| `semantic_search(PostSearchQuery)`  | `PostSearchQuery`, specifying search text, the status and origin filters, and max results. | `list[Post]` | Retrieves posts based on semantic (i.e. `PostEmbedding`. |

### 5. [embedding.py](embedding.py)

Defines the `EmbeddingGenerator` protocol for building embedding vectors from `Post` objects, to be used for semantic
search.

| Method           | Input  | Output        | Description                                           |
|------------------|--------|---------------|-------------------------------------------------------|
| `generate(Post)` | `Post` | `list[float]` | A dense vector embeddings for a single `Post` object. |
