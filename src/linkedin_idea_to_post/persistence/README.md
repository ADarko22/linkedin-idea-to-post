# LinkedIn Idea to Post – Persistence

This directory contains the application's persistence layer, responsible for storing and retrieving LinkedIn posts.

## Main Components

### [SqlitePostStorage](sqlite_post_storage.py)

The `SqlitePostStorage` implements `PostGetQuery` using SQLite to perform CRUD operations on`Post` objects.

Each post is stored as a complete JSON document, keyed by its post ID, into the `posts` table.

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

## Design considerations

`SqlitePostStorage` provides a simple initial storage solution. Its implementation can be abstracted later to support
alternative storage backends and more advanced data access patterns.

