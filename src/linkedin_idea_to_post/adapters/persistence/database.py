import sqlite3

from linkedin_idea_to_post.config import PersistenceSettings

_SCHEMA_SQL = """
    -- 1. Primary Source of Truth
    CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        doc TEXT NOT NULL
    );

    -- 2. Derived FTS5 Search Index
    CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
        body,
        topics,
        content='',
        content_rowid='rowid'
    );

    -- 3. Synchronization Triggers
    CREATE TRIGGER IF NOT EXISTS update_posts_fts_after_insert_on_posts AFTER INSERT ON posts
    BEGIN
        INSERT INTO posts_fts (rowid, body, topics)
        VALUES (
            NEW.rowid,
            json_extract(NEW.doc, '$.body'),
            (SELECT group_concat(value, ' ') FROM json_each(NEW.doc, '$.topics'))
        );
    END;

    CREATE TRIGGER IF NOT EXISTS update_posts_fts_after_delete_on_posts AFTER DELETE ON posts
    BEGIN
        INSERT INTO posts_fts (posts_fts, rowid, body, topics)
        VALUES (
            'delete',
            OLD.rowid,
            json_extract(OLD.doc, '$.body'),
            (SELECT group_concat(value, ' ') FROM json_each(OLD.doc, '$.topics'))
        );
    END;

    CREATE TRIGGER IF NOT EXISTS update_posts_fts_after_update_on_posts AFTER UPDATE ON posts
    BEGIN
        INSERT INTO posts_fts (posts_fts, rowid, body, topics)
        VALUES (
            'delete',
            OLD.rowid,
            json_extract(OLD.doc, '$.body'),
            (SELECT group_concat(value, ' ') FROM json_each(OLD.doc, '$.topics'))
        );
        INSERT INTO posts_fts (rowid, body, topics)
        VALUES (
            NEW.rowid,
            json_extract(NEW.doc, '$.body'),
            (SELECT group_concat(value, ' ') FROM json_each(NEW.doc, '$.topics'))
        );
    END;


    -- 4. Post Embedding Vectors for Semantic Search Index
    CREATE TABLE IF NOT EXISTS post_embeddings (
        post_id TEXT PRIMARY KEY,
        model_name TEXT NOT NULL,
        dimensions INT NOT NULL,
        vector BLOB NOT NULL,
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        FOREIGN KEY (post_id) REFERENCES posts (id)
    );
"""


def create_sqlite_connection(settings: PersistenceSettings) -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(_SCHEMA_SQL)
    return conn
