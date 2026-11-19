# LinkedIn Idea to Post – Persistence

This directory contains the application's persistence layer, responsible for storing and retrieving LinkedIn posts.

## Main Components

### [SqlitePostStorage](sqlite_post_storage.py)

The `SqlitePostStorage` implements `PostGetQuery` using SQLite to perform CRUD operations on`Post` objects.

Each post is stored as a complete JSON document, keyed by its post ID, into the `posts` table.

### [sqlite_post_embedding_storage.py](sqlite_post_embedding_storage.py)

The `SQLitePostEmbeddingStorage` implements `PostEmbeddingStorage` using SQLite to perform CRUD operations on
`PostEmbedding` objects.

Each embedding is stored with metadata about the embedding model, and keyed by the referenced post ID, into the
`posts_embeddings` table.

### [SqlitePostRetriever](sqlite_post_retrieval.py)

The `SqlitePostRetriever` implements `PostSearchQuery` using SQLite to retrieve `Post` objects by Full-Text Search and
Semantic Search.

#### FTS5 - Full-Text Search

[SQLite FTS5](https://sqlite.org/fts5.html) provides lexical full-text search via an inverted index over `Post`
properties (`title`, `body`, `topics`), ranked by the [BM25](https://sqlite.org/fts5.html#the_bm25_function) algorithm
(term frequency, inverse document frequency, and field-length normalization).

The implementation chosen uses [contentless tables](https://sqlite.org/fts5.html#contentless_tables) for the Full-Text
indexes, because `posts` stores the `Post` objects as a JSON document. Full-Text indexes reference only the `rowid` in
`posts` and are kept in sync with Database Triggers.

* **Source of Truth:**
    * The `posts` table stores full JSON documents keyed by `id` and SQLite's internal `rowid`.


* **Contentless Index:**
    * The `posts_fts` virtual table is created with **_content=''_** and **_content_rowid='rowid'_**
      (see [Contentless Tables](https://sqlite.org/fts5.html#contentless_tables)).
    * Doesn't contain the content from `posts`, but references the hidden `rowid` field of `posts`.
    * Stores only the inverted word index and document token lengths (i.e. `posts_fts_data`, `posts_fts_idx`,
      `posts_fts_docsize` tables).
    * Consequently, executing `SELECT * FROM posts_fts` returns `NULL` values.


* **Trigger Synchronization:**
    * `AFTER INSERT`, `AFTER UPDATE`, and `AFTER DELETE` triggers on `posts` are used to keep
      `posts_fts` in sync.
    * Updates and deletes use the `'delete'` command with the `OLD` field values so FTS5 can remove stale tokens from
      the inverted index.


* **Query & Hydration:**
    * `MATCH` evaluates sanitized `OR`-joined tokens against `posts_fts`
      (see [FTS5 Query Syntax](https://sqlite.org/fts5.html#full_text_query_syntax)).
    * Orders by `bm25(posts_fts)`, more negative means stronger match, (
      see [bm25() Auxiliary Function](https://sqlite.org/fts5.html#the_bm25_function))
    * Joins back to `posts` on `rowid` to filter metadata (`status`, `origin`) and deserialize `doc`.

_Use [Shadow Tables &`fts5vocab`](https://sqlite.org/fts5.html#the_fts5vocab_virtual_table_module) to inspect the
underlying inverted index vocabulary and term frequencies._

#### Cosine Similarity Score on Embeddings for Semantic Search

Using [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) on all the vector embeddings, for the posts
matching the search criteria, for computing the similarity score with the search embedding and returning the top scored
posts.

The **cosine similarity** is computed using a Matrix to Vector product with [numpy](https://github.com/numpy):

- Each of the N post embedding vectors is converted to a numpy.ndarray of D `float32`.
- These arrays are stacked to form a 2D array of `NxD`.
- Cosine Similarity is computed as: `M * V / (|M| * |V|)`. Where M is `NxD`, V is `Dx1`, and the denominator is product
  of the respective [Euclidean Norm](https://en.wikipedia.org/wiki/Norm_(mathematics)).
    - Before performing the multiplications `M` is filtered to remove the rows having Euclidean Norm equals to zero.
    - The resulting `Nx1` array contains the scores of each post embedding w.r.t. the search embedding.
- These scores are sorted in descending order and their sorted indexes are used to identify the best matching posts.

### [sql_builders.py](sql_builders.py)

Pure functions for building the search queries with advanced filtering.

### [sqllite_unit_of_work.py](sqllite_unit_of_work.py)

The `SqliteUnitOfWork` implements the `UnitOfWork` use case protocol to provide a way to perform atomic database changes
on multiple tables.

Implements the [Unit Of Work](https://martinfowler.com/eaaCatalog/unitOfWork.html) design pattern.

## Design considerations

`SqlitePostStorage` provides a simple initial storage solution. Its implementation can be abstracted later to support
alternative storage backends and more advanced data access patterns.

