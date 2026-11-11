# LinkedIn Idea to Post – Archive

This directory contains the persistent storage and archival logic of the LinkedIn Idea to Post application.

## Content

### 1. [sqlite_archive.py](sqlite_archive.py)

Defines the `SqliteArchive` class, responsible for storing and retrieving LinkedIn posts using a SQLite database.

Each post is stored as a complete JSON document, using its post ID as the key.

The archive provides the following functionality:

- Creating database tables.
- Inserting and storing posts.
- Retrieving individual or multiple archived posts.

#### Available methods

1. **`save(Post)`**

   Saves a `Post` object to the SQLite database.

2. **`get(post_id: UUID) -> Post | None`**

   Retrieves a `Post` object by its post ID. Returns `None` if the post is not found.

3. **`get_all(
   statuses: list[PostStatus] | None,
   origins: list[PostOrigin] | None,
   limit: int,
   page: int
   ) -> list[Post]`**

   Retrieves archived posts, ordered from most recent to oldest.

   Supports:
   - **Filtering:** Optionally filters posts by status and origin.
   - **Pagination:** Uses `limit` to define the number of posts per page and `page` to select the requested page.

#### Design considerations

`SqliteArchive` is intended as a simple initial storage solution.

The implementation can be abstracted later to support alternative storage solutions and more complex data access patterns.