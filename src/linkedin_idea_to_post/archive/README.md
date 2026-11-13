# LinkedIn Idea to Post – Archive

This directory contains the application's persistence layer, responsible for storing and retrieving archived LinkedIn
posts.

## Main Components

### [SqliteArchive](sqlite_archive.py)

Defines the `SqliteArchive` class, which uses SQLite to persist and retrieve `Post` objects.

Each post is stored as a complete JSON document, keyed by its post ID.

| Method                                    | Input                                                          | Output         | Description                                                                    |
|-------------------------------------------|----------------------------------------------------------------|----------------|--------------------------------------------------------------------------------|
| `save(post)`                              | `Post`                                                         | `None`         | Saves a post to the SQLite database.                                           |
| `get(post_id)`                            | `UUID`                                                         | `Post \| None` | Retrieves a post by ID, or returns `None` if it is not found.                  |
| `get_all(statuses, origins, limit, page)` | Optional status and origin filters, page size, and page number | `list[Post]`   | Retrieves posts from newest to oldest, with optional filtering and pagination. |

### Design considerations

`SqliteArchive` provides a simple initial storage solution. Its implementation can be abstracted later to support
alternative storage backends and more advanced data access patterns.