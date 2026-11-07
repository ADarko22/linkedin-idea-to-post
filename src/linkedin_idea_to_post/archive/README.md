# LinkedIn Idea to Post Archive

This directory contains the persistent storage and archival logic for the LinkedIn Idea to Post application.

## Content

1. [sqlite_archive.py](sqlite_archive.py): Contains the `SqliteArchive` class, which provides methods for storing and
   retrieving LinkedIn posts in a SQLite database. It stores the entire post as a JSON document by the post id as key.
   It includes functionality for creating tables, inserting posts, and querying archived posts.
   It is intended to be used as initial storage for simplicity. Abstractions can be added later to support other storage
   solutions and more complex access patterns.


