import sqlite3

import pytest

from linkedin_idea_to_post.adapters.persistence.sqlite_post_retrieval import (
    _prepare_fts_expression,
)


@pytest.mark.parametrize(
    ("raw_text", "expected"),
    [
        # Lowercasing & basic OR joining
        ("Kafka Streams Architecture", '"kafka" OR "streams" OR "architecture"'),
        # Stop-word removal & single-character filtering
        ("I am in a rush to be at the top", '"am" OR "rush" OR "top"'),
        # Order-preserving deduplication
        ("Java java JAVA and Kotlin kotlin", '"java" OR "kotlin"'),
        # Hyphenated words & contractions split into clean alphanumeric tokens
        (
            "I'm building self-growth habits",
            '"building" OR "self" OR "growth" OR "habits"',
        ),
        # FTS5 reserved keywords & column-filter syntax neutralized
        ('title:Kafka NOT (NEAR OR "AND*")', '"title" OR "kafka" OR "near"'),
        # Numeric tokens preserved
        ("Java 21 and Spring Boot 3", '"java" OR "21" OR "spring" OR "boot"'),
        # Empty, whitespace-only, punctuation-only, or stop-word-only inputs
        ("", ""),
        ("   \t\n  ", ""),
        ("??? --- *** !!!", ""),
        ("a I to the and of", ""),
    ],
)
def test_prepare_fts_expression(raw_text: str, expected: str) -> None:
    assert _prepare_fts_expression(raw_text) == expected


@pytest.mark.parametrize(
    "adversarial_input",
    [
        '"""unbalanced quotes"""',
        "C++ & C# vs. F# (2026)!",
        "title:hack OR body:hack^2",
        "NEAR(foo bar, 10) -baz +qux*",
        "Line 1\nLine 2\x00NullByte",
        "100% of users don't know why—really?",
    ],
)
def test_prepare_fts_expression_never_causes_fts5_syntax_error(
    adversarial_input: str,
) -> None:
    """Validates generated expressions directly against SQLite's FTS5 MATCH parser."""
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE VIRTUAL TABLE docs USING fts5(content);")
    conn.execute("INSERT INTO docs(content) VALUES ('sample document text');")

    expr = _prepare_fts_expression(adversarial_input)
    if expr:
        # Must execute cleanly without raising sqlite3.OperationalError
        rows = conn.execute(
            "SELECT rowid FROM docs WHERE docs MATCH ?", (expr,)
        ).fetchall()
        assert isinstance(rows, list)
