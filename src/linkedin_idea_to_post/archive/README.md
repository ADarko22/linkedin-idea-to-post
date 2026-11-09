# LinkedIn Idea to Post Archive

This directory contains the persistent storage and archival logic for the LinkedIn Idea to Post application.

## Content

1. [sqlite_archive.py](sqlite_archive.py): Contains the `SqliteArchive` class, which provides methods for storing and
   retrieving LinkedIn posts in a SQLite database. It stores the entire post as a JSON document by the post id as key.
   It includes functionality for creating tables, inserting posts, and querying archived posts.
   It is intended to be used as initial storage for simplicity. Abstractions can be added later to support other storage
   solutions and more complex access patterns. It provides:
    1. `save(Post)`: Saves a `Post` object to the SQLite database.
    2. `get(post_id: UUID) -> Post | None`: Retrieves a `Post` object from the SQLite database by its post id.
    3. `get_all(
                statuses: list[PostStatus] | None, 
                origins: list[PostOrigin] | None, 
                limit: int, 
                page: int
                ) -> list[Post]`:
       Retrieves all `Post` objects from the SQLite database, from the most recent to the oldest, with optional
       filtering by post status and origin. It supports pagination through the `limit` and `page` parameters.
